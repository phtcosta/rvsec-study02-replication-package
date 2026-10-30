"""Run every producer and statement script and compare with claims/.

Producers (scripts/<name>.py, names in common.PRODUCERS) expose claims(), and
optionally tables() and figures(); their output is compared, as formatted
strings, with claims/claims.csv, claims/tables/*.csv and claims/figures/*.csv.
Statement scripts (scripts/statements/*.py) run as separate processes; exit
code 0 is PASS, 1 FAIL, 2 SKIP.

Writes out/values.csv, out/tables/, out/figures/, out/statements/ and
out/report.txt. Exit code 1 on any FAIL.

Usage:
    python -m scripts.check               compute, compare, report
    python -m scripts.check --no-compare  compute into out/ only
    python -m scripts.check --readme      regenerate the README claims table
"""

from __future__ import annotations

import argparse
import importlib
import subprocess
import sys

import pandas as pd

from scripts.common import (CLAIMS, FIGURES, OUT, PRODUCERS, ROOT, STATEMENTS, TABLES,
                            load_claims, load_expected)

README = ROOT / "README.md"
STATEMENTS_DIR = ROOT / "scripts" / "statements"
BEGIN = "<!-- CLAIMS TABLE: generated from claims/claims.csv by scripts/check.py -->"
END = "<!-- END CLAIMS TABLE -->"


def run_producers():
    values, tables, figures = {}, {}, {}
    for name in PRODUCERS:
        mod = importlib.import_module(f"scripts.{name}")
        values[name] = mod.claims()
        if hasattr(mod, "tables"):
            tables.update(mod.tables())
        if hasattr(mod, "figures"):
            figures.update(mod.figures())
    return values, tables, figures


def run_statements():
    out = []
    for stem in STATEMENTS:
        proc = subprocess.run([sys.executable, "-m", f"scripts.statements.{stem}"],
                              cwd=ROOT, capture_output=True, text=True)
        out.append((stem, proc.returncode, proc.stdout + proc.stderr))
    return out


def compare_long(kind, name, computed, keys):
    """Cell-by-cell comparison of a table or figure with its expected CSV, row order included."""
    exp = load_expected(kind, name)
    got = computed.astype(str).set_index(keys)["expected"]
    lines, failed = [], 0
    for _, row in exp.iterrows():
        key = tuple(row[k] for k in keys)
        value = got.get(key if len(keys) > 1 else key[0])
        ok = value == row["expected"]
        failed += not ok
        label = ":".join((name,) + key)
        lines.append(f"{'PASS' if ok else 'FAIL'}  {kind[:-1]:<6}  {label}  {value}"
                     + ("" if ok else f"  [expected {row['expected']}]"))
    extra = len(got) - len(exp)
    if extra:
        failed += 1
        lines.append(f"FAIL  {kind[:-1]:<6}  {name}  {extra:+d} cells beyond the expected ones")
    elif list(got.index) != list(exp.set_index(keys).index):
        failed += 1
        lines.append(f"FAIL  {kind[:-1]:<6}  {name}  rows not in the printed order")
    return lines, failed


def readme_table(claims: pd.DataFrame) -> str:
    rows = ["| Section | Macro | Printed value | Checked by |", "|---|---|---|---|"]
    for _, r in claims.iterrows():
        how = f"`scripts/{r['producer']}.py`" if r["method"] == "script" else "inspection"
        rows.append(f"| {r['section']} | `\\{r['macro']}` | `{r['expected']}` | {how} |")
    return "\n".join([BEGIN, ""] + rows + ["", END])


def write_readme(claims: pd.DataFrame) -> None:
    text = README.read_text(encoding="utf-8")
    start = text.index(BEGIN)
    stop = text.index(END) + len(END) if END in text else start + len(BEGIN)
    README.write_text(text[:start] + readme_table(claims) + text[stop:], encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compute every claim and compare with claims/.")
    ap.add_argument("--no-compare", action="store_true")
    ap.add_argument("--readme", action="store_true")
    args = ap.parse_args(argv)

    claims = load_claims()
    if args.readme:
        write_readme(claims)
        print("README claims table regenerated")
        return 0

    values, tables, figures = run_producers()
    statements = run_statements()

    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    (OUT / "statements").mkdir(parents=True, exist_ok=True)
    pd.DataFrame([(p, m, v) for p, d in values.items() for m, v in sorted(d.items())],
                 columns=["producer", "macro", "computed"]).to_csv(OUT / "values.csv", index=False)
    for name, df in tables.items():
        df.to_csv(OUT / "tables" / f"{name}.csv", index=False)
    for name, df in figures.items():
        df.to_csv(OUT / "figures" / f"{name}.csv", index=False)
    for stem, _, text in statements:
        (OUT / "statements" / f"{stem}.txt").write_text(text, encoding="utf-8")
    if args.no_compare:
        print(f"computed into {OUT.relative_to(ROOT)}/")
        return 0

    report, n = [], {"macro": [0, 0], "table": [0, 0], "figure": [0, 0], "statement": [0, 0, 0]}

    # Macros, grouped by the article section where each is first cited.
    report.append("== Macros")
    script_rows = claims[claims["method"] == "script"]
    for section, rows in script_rows.groupby("section", sort=False):
        report.append(f"-- {section}")
        for _, r in rows.iterrows():
            got = values[r["producer"]].get(r["macro"])
            ok = got == r["expected"]
            n["macro"][0 if ok else 1] += 1
            report.append(f"{'PASS' if ok else 'FAIL'}  {r['producer']:<10}  {r['macro']}  {got}"
                          + ("" if ok else f"  [expected {r['expected']}]"))
    for producer, d in values.items():
        expected = set(script_rows.loc[script_rows["producer"] == producer, "macro"])
        for extra in sorted(set(d) - expected):
            n["macro"][1] += 1
            report.append(f"FAIL  {producer:<10}  {extra}  computed but not a script claim")

    report.append("")
    report.append("== Tables and figures")
    for kind, computed, keys, expected_names in (("tables", tables, ["row", "column"], TABLES),
                                                 ("figures", figures, ["item"], FIGURES)):
        for name in sorted(set(computed) - set(expected_names)):
            n[kind[:-1]][1] += 1
            report.append(f"FAIL  {kind[:-1]:<6}  {name}  computed but not an expected {kind[:-1]}")
        for name in sorted({p.stem for p in (CLAIMS / kind).glob("*.csv")} - set(expected_names)):
            n[kind[:-1]][1] += 1
            report.append(f"FAIL  {kind[:-1]:<6}  {name}  claims/{kind}/{name}.csv is not a pinned {kind[:-1]}")
        for name in expected_names:
            if name not in computed:
                n[kind[:-1]][1] += 1
                report.append(f"FAIL  {kind[:-1]:<6}  {name}  not computed")
                continue
            try:
                lines, failed = compare_long(kind, name, computed[name], keys)
            except FileNotFoundError:
                lines, failed = [f"FAIL  {kind[:-1]:<6}  {name}  expected file missing"], 1
            n[kind[:-1]][0 if not failed else 1] += 1
            report.extend(lines)

    report.append("")
    report.append("== Statements")
    for stem, code, _ in statements:
        status = {0: "PASS", 1: "FAIL", 2: "SKIP"}.get(code, "FAIL")
        n["statement"][{"PASS": 0, "FAIL": 1, "SKIP": 2}[status]] += 1
        report.append(f"{status}  {stem}")
    for stem in sorted({p.stem for p in STATEMENTS_DIR.glob("*_[0-9][0-9][0-9].py")}
                       - set(STATEMENTS)):
        n["statement"][1] += 1
        report.append(f"FAIL  {stem}  scripts/statements/{stem}.py is not a pinned statement")

    report.append("")
    report.append("== Checked by inspection (see README)")
    for _, r in claims[claims["method"] == "inspection"].iterrows():
        report.append(f"INSPECT  {r['producer']:<10}  {r['macro']}  {r['expected']}  <- {r['evidence']}")

    readme_ok = BEGIN in README.read_text(encoding="utf-8") and \
        readme_table(claims) in README.read_text(encoding="utf-8")
    report.append("")
    report.append(f"{'PASS' if readme_ok else 'FAIL'}  README claims table "
                  f"{'matches claims.csv' if readme_ok else 'is stale: run python -m scripts.check --readme'}")

    inspection = int((claims["method"] == "inspection").sum())
    summary = (f"macros {n['macro'][0]} passed, {n['macro'][1]} failed; "
               f"tables {n['table'][0]} passed, {n['table'][1]} failed; "
               f"figures {n['figure'][0]} passed, {n['figure'][1]} failed; "
               f"statements {n['statement'][0]} passed, {n['statement'][1]} failed, "
               f"{n['statement'][2]} skipped; {inspection} by inspection, see README")
    report += ["", summary]
    text = "\n".join(report) + "\n"
    (OUT / "report.txt").write_text(text, encoding="utf-8")
    print(text, end="")

    failed = n["macro"][1] + n["table"][1] + n["figure"][1] + n["statement"][1] \
        + n["statement"][2] + (not readme_ok)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
