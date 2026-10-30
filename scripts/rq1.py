"""RQ1 (JCA misuses found by the test-generation tools): macros, two tables, the NB2 model.

Inputs (all through common.py):
- the run table (per_task joined with direct-coverage, 16,137 runs): mop_unique4 (unique
  misuses per run), mop_total (violation events per run), cov_method, cov_act, cov_mop,
  cov_directly_reaches_mop, category, admissible, sa_methods_reaches_mop (model size covariate);
- raw-accusations.csv: one row per violation report; a unique misuse is a distinct
  (apk, spec, class, method);
- mneut_348.csv (Mneut, the app root package) restricted to the apps of dataset.csv with
  funnel_stage == 'selected', for the code origin of the start-up misuses.

Descriptive numbers use the per-app mean over the 3 repetitions of each (tool, timeout)
(Results, RQ1); the tables sum those means over the apps.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from scripts import common
from scripts.common import decimal, integer, word, word99

TIMEOUTS = (60, 180, 300)
REFERENCE_TOOL = "monkey"
GAIN = "% Gain (300s vs 60s)"
FORMULA = ("mop_unique4 ~ C(timeout) + C(tool, Treatment('monkey'))"
           " + log(sa_methods_reaches_mop)")
TOOL_TERM = "C(tool, Treatment('monkey'))"
SIZE_TERM = "log(sa_methods_reaches_mop)"
COV_ZERO = ["cov_method", "cov_act", "cov_mop"]
ALL_ZERO = COV_ZERO + ["cov_directly_reaches_mop", "mop_unique4", "mop_total"]
RAW_COLS = ["apk", "tool", "rep", "timeout", "time", "spec", "class", "method"]


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

def raw_accusations() -> pd.DataFrame:
    """The raw reports as delivered strings (no NA coercion); run key and time as int."""
    raw = common.load("raw_accusations", dtype=str, keep_default_na=False,
                      usecols=RAW_COLS)[RAW_COLS]
    return raw.astype({"rep": int, "timeout": int, "time": int})


def per_app(runs: pd.DataFrame) -> pd.DataFrame:
    """Per (apk, timeout, tool): mean over the repetitions of events and unique misuses."""
    return (runs.groupby(["apk", "timeout", "tool"])
            .agg(events=("mop_total", "mean"), unique=("mop_unique4", "mean"))
            .reset_index())


def all_zero(runs: pd.DataFrame) -> pd.Series:
    """Runs where every coverage and every violation metric is zero (Discussion)."""
    return (runs[ALL_ZERO] == 0).all(axis=1)


# ---------------------------------------------------------------------------
# The RQ1 count model
# ---------------------------------------------------------------------------

def fit_rq1(runs: pd.DataFrame) -> common.GlmFit:
    """NB2 of unique misuses per run on budget, tool (vs monkey) and log app size,
    cluster-robust by app (Results, RQ1). Pure function of ``runs``."""
    return common.fit_nb2(FORMULA, runs)


def _irr(nb, term: str, stem: str) -> dict[str, str]:
    """IRR and its Wald cluster-robust 95% CI, 4 places."""
    ci = nb.conf_int()
    return {stem: decimal(np.exp(nb.params[term]), 4),
            stem + "Lo": decimal(np.exp(ci.loc[term, 0]), 4),
            stem + "Hi": decimal(np.exp(ci.loc[term, 1]), 4)}


def _glm_claims(runs: pd.DataFrame) -> dict[str, str]:
    nb = fit_rq1(runs).nb
    ape = f"{TOOL_TERM}[T.ape]"
    tools = [t for t in nb.params.index if t.startswith(TOOL_TERM)]
    out = {"glmRawVarMean": decimal(runs["mop_unique4"].var() / runs["mop_unique4"].mean())}
    out |= _irr(nb, "C(timeout)[T.180]", "glmRawIrrTimeoutOneEighty")
    out |= _irr(nb, "C(timeout)[T.300]", "glmRawIrrTimeoutThreeHundred")
    out |= _irr(nb, ape, "glmRawIrrApe")
    out |= _irr(nb, SIZE_TERM, "glmRawIrrSize")
    out["glmRawHolmApe"] = common.pvalue(common.holm(nb.pvalues[tools])[ape])
    return out


# ---------------------------------------------------------------------------
# Tables jca-violations (events) and jca-violations-unique
# ---------------------------------------------------------------------------

def _pivot(apps: pd.DataFrame, col: str) -> pd.DataFrame:
    """Sum over apps of the per-app mean, rounded to integers, then the 60 -> 300 s gain
    in % over the rounded sums, rounded to one place."""
    p = (apps.groupby(["tool", "timeout"])[col].sum().unstack("timeout")
         .sort_index().round(0).astype(int))
    p[GAIN] = ((p[300] - p[60]) / p[60].replace(0, np.nan) * 100).round(1)
    return p


def _long(p: pd.DataFrame) -> pd.DataFrame:
    rows = [(tool, str(c), str(int(p.loc[tool, c])) if c in TIMEOUTS
             else decimal(p.loc[tool, c], 1))
            for tool in p.index for c in p.columns]
    return pd.DataFrame(rows, columns=["row", "column", "expected"])


def tables() -> dict[str, pd.DataFrame]:
    apps = per_app(common.run_table())
    return {"jca-violations": _long(_pivot(apps, "events")),
            "jca-violations-unique": _long(_pivot(apps, "unique"))}


# ---------------------------------------------------------------------------
# Macros
# ---------------------------------------------------------------------------

def _startup_lib(startup: pd.DataFrame) -> int:
    """Start-up misuses in library code: the app has a Mneut and the class is not under it."""
    selected = common.load("dataset", usecols=["apk", "funnel_stage"])
    selected = selected.loc[selected["funnel_stage"] == "selected", "apk"]
    mneut = common.load("mneut", usecols=["apk", "Mneut"])
    mneut = mneut[mneut["apk"].isin(selected)]
    o = startup.merge(mneut, on="apk", how="left", validate="m:1")
    matched = o["Mneut"].map(lambda m: isinstance(m, str) and m != "")
    lib = [m and not common.is_app_code(c, n)
           for m, c, n in zip(matched, o["class"], o["Mneut"])]
    return int(sum(lib))


def _misuse_claims(raw: pd.DataFrame, runs_per_app: int, n_tools: int) -> dict[str, str]:
    key = ["apk", "class", "method", "spec"]
    run_id = raw["tool"] + ":" + raw["timeout"].astype(str) + ":" + raw["rep"].astype(str)
    rep = (raw.assign(run=run_id).groupby(key)
           .agg(runs=("run", "nunique"), tools=("tool", "nunique")).reset_index())
    # Start-up misuses: reported in every run of their app; first report per run, median.
    startup = rep.loc[rep["runs"] == runs_per_app, key]
    first = (raw.merge(startup, on=key)
             .groupby(key + ["tool", "timeout", "rep"])["time"].min()
             .groupby(key).median())
    monkey60 = raw[(raw["tool"] == REFERENCE_TOOL) & (raw["timeout"] == 60)]
    return {
        "rawUnique": integer(len(raw.drop_duplicates(key))),
        "rawApps": integer(raw["apk"].nunique()),
        "rawSpecsWord": word99(raw["spec"].nunique()),
        "rawEveryTool": integer((rep["tools"] == n_tools).sum()),
        "rawStartupMisuses": integer(len(startup)),
        "rawStartupMisusesLib": integer(_startup_lib(startup)),
        "rawStartupFirstMin": integer(first.min()),
        "rawStartupFirstMax": integer(first.max()),
        "rawMonkeySixtyMisuses": integer(len(monkey60.drop_duplicates(key))),
    }


def _descriptive_claims(apps: pd.DataFrame) -> dict[str, str]:
    u, e = _pivot(apps, "unique"), _pivot(apps, "events")
    at300 = apps[apps["timeout"] == 300].groupby("tool")
    avg_unique, avg_events = at300["unique"].mean().round(2), at300["events"].mean().round(2)
    emin = e[GAIN].idxmin()
    return {
        "rawUniqueGainMin": decimal(u[GAIN].min(), 1),
        "rawUniqueGainMax": decimal(u[GAIN].max(), 1),
        "rawUniqueGainQtesting": decimal(u.loc["qtesting", GAIN], 1),
        "rawEventsGainMin": decimal(e[GAIN].min(), 1),
        "rawEventsGainMinSixty": integer(e.loc[emin, 60]),
        "rawEventsGainMinThreeHundred": integer(e.loc[emin, 300]),
        "rawEventsGainMax": decimal(e[GAIN].max(), 1),
        "rawEventsGainQtesting": decimal(e.loc["qtesting", GAIN], 1),
        "rawAvgUniqueMisusesMin": decimal(avg_unique.min()),
        "rawAvgUniqueMisusesMax": decimal(avg_unique.max()),
        "rawAvgEventsQtestingThreeHundred": decimal(avg_events["qtesting"]),
    }


def _run_claims(runs: pd.DataFrame) -> dict[str, str]:
    """Grid size and the zero policy (Execution, Discussion)."""
    zero = all_zero(runs)
    covered = ~(runs[COV_ZERO] == 0).all(axis=1)
    qt = covered[runs["tool"] == "qtesting"].groupby(runs["apk"]).any()
    return {
        "tasksGrid": integer(len(runs)),
        "allZeroRuns": integer(zero.sum()),
        "allZeroPct": decimal(100.0 * zero.sum() / len(runs), 1),
        "allZeroStructural": integer((runs.loc[zero, "category"] == "estrutural").sum()),
        "qtestingEffectiveApps": integer(qt.sum()),
        "qtestingNeverCoveredApps": integer((~qt).sum()),
        "inadmissibleRuns": integer((runs["admissible"] == 0).sum()),
    }


def claims() -> dict[str, str]:
    runs = common.run_table()
    per_app_runs = runs.groupby("apk").size()
    if per_app_runs.nunique() != 1:
        raise ValueError("apps do not share one number of runs")
    runs_per_app, n_tools = int(per_app_runs.iloc[0]), runs["tool"].nunique()
    out = {"runsPerApp": integer(runs_per_app), "toolCountWord": word(n_tools)}
    out |= _run_claims(runs)
    out |= _descriptive_claims(per_app(runs))
    out |= _misuse_claims(raw_accusations(), runs_per_app, n_tools)
    out |= _glm_claims(runs)
    return out


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

def _main() -> int:
    reg = common.load_claims()
    reg = reg[(reg["producer"] == "rq1") & (reg["method"] == "script")]
    got = claims()
    lines, fails = [], 0
    if set(got) != set(reg["macro"]):
        lines.append(f"FAIL  rq1  macro set differs: {sorted(set(got) ^ set(reg['macro']))}")
        fails += 1
    for macro, exp in zip(reg["macro"], reg["expected"]):
        val = got.get(macro, "<missing>")
        ok = val == exp
        fails += not ok
        lines.append(f"{'PASS' if ok else 'FAIL'}  rq1  {macro}  {val}"
                     + ("" if ok else f"  expected {exp}"))
    n_cells = 0
    for name, df in tables().items():
        exp = common.load_expected("tables", name)
        if list(df[["row", "column"]].itertuples(index=False)) != \
                list(exp[["row", "column"]].itertuples(index=False)):
            lines.append(f"FAIL  rq1  table:{name}  row/column order differs")
            fails += 1
        for (r, c, v), e in zip(df.itertuples(index=False), exp["expected"]):
            ok = v == e
            fails += not ok
            n_cells += 1
            lines.append(f"{'PASS' if ok else 'FAIL'}  rq1  table:{name}:{r}:{c}  {v}"
                         + ("" if ok else f"  expected {e}"))
    print("\n".join(lines))
    print(f"rq1: {len(reg)} claims, {n_cells} table cells, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_main())
