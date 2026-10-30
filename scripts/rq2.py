"""RQ2: method coverage, direct JCA coverage and the coverage NB2 GLM.

Inputs (through common.py only):
- the run table (per_task.csv joined with direct-coverage.csv, 16,137 runs):
  cov_method and cov_mop (per_task; the article's "reaches MOP" coverage),
  cov_directly_reaches_mop (direct-coverage; the article's "JCA MOP coverage",
  aliased "cov_mop" in its tables, NOT per_task.cov_mop), mop_unique4;
- dataset.csv: funnel_stage == 'selected' (the 163 apps) and
  sa_methods_directly_reaches_mop > 0 (apps whose own code directly invokes a
  monitored JCA API: the support of the direct-coverage mean).

Every descriptive number first averages the 3 repetitions of an
(apk, tool, timeout) cell, then averages over apps. Tables `coverage` and
`coverage_mop` (Results, RQ2) are the tool x timeout means of method and direct
coverage. The GLM is the article's raw-report model:
mop_unique4 ~ cov_method + C(timeout) + C(tool, Treatment('monkey')), NB2 with
cluster-robust SEs by app, on the per-run counts.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from scripts import common

PRODUCER = "rq2"
TIMEOUTS = (60, 180, 300)
FORMULA = "mop_unique4 ~ cov_method + C(timeout) + C(tool, Treatment('monkey'))"


def per_app(runs: pd.DataFrame) -> pd.DataFrame:
    """Mean over repetitions per (apk, tool, timeout): cov, cov_reach, cov_direct."""
    return (runs.groupby(["apk", "tool", "timeout"])
            .agg(cov=("cov_method", "mean"), cov_reach=("cov_mop", "mean"),
                 cov_direct=("cov_directly_reaches_mop", "mean"))
            .reset_index())


def _cells(runs: pd.DataFrame) -> pd.DataFrame:
    """Tool x timeout mean over apps of the per-app means (unrounded)."""
    return per_app(runs).groupby(["tool", "timeout"])[["cov", "cov_reach", "cov_direct"]].mean()


def mean_coverage(runs: pd.DataFrame) -> pd.DataFrame:
    """Mean method coverage (pp), tools as rows and timeouts as columns, unrounded."""
    return _cells(runs)["cov"].unstack("timeout").sort_index()


def fit_rq2(runs: pd.DataFrame) -> common.GlmFit:
    """The coverage NB2 GLM on the per-run counts (no offset)."""
    return common.fit_nb2(FORMULA, runs)


def _support_apps() -> tuple[int, set[str]]:
    """Number of selected apps and the set with a non-empty direct denominator."""
    ds = common.load("dataset", low_memory=False,
                     usecols=["apk", "funnel_stage", "sa_methods_directly_reaches_mop"])
    sel = ds[ds["funnel_stage"] == "selected"]
    return sel["apk"].nunique(), set(sel.loc[sel["sa_methods_directly_reaches_mop"] > 0, "apk"])


def claims() -> dict[str, str]:
    runs = common.run_table()
    apps = per_app(runs)
    cells = _cells(runs)
    d = common.decimal
    out: dict[str, str] = {}

    # Coverage gap (Results, RQ2): cells rounded as the article prints them.
    ape = cells.loc[("ape", 300)]
    out["covMethodApeThreeHundred"] = d(round(ape["cov"], 2))
    out["covDirectApeThreeHundred"] = d(round(ape["cov_direct"], 2))
    out["covGapRatioApeThreeHundred"] = d(round(ape["cov"] / ape["cov_direct"], 1), 1)
    c300 = cells.xs(300, level="timeout")["cov"].round(2)
    out["covMethodMonkeyThreeHundred"] = d(c300["monkey"])
    out["covMethodDroidmateThreeHundred"] = d(c300["droidmate"])
    g_cov, g_direct = apps["cov"].mean(), apps["cov_direct"].mean()
    out["covMethodGlobal"] = d(g_cov)
    out["covReachesMopGlobal"] = d(apps["cov_reach"].mean())
    out["covDirectGlobal"] = d(g_direct)
    out["covGapRatioGlobal"] = d(g_cov / g_direct, 1)

    # Support of the direct-coverage mean: apps with a direct JCA method of their own.
    n_apps, support = _support_apps()
    sup = apps[apps["apk"].isin(support)]
    sup_app = sup.groupby("apk")[["cov", "cov_direct"]].mean()
    out["directCovSupportApps"] = common.integer(len(support))
    out["directCovNoSupport"] = common.integer(n_apps - len(support))
    out["directCovSupportMean"] = d(sup["cov_direct"].mean())
    out["covMethodSupportMean"] = d(sup["cov"].mean())
    out["directCovSupportMedian"] = d(sup_app["cov_direct"].median())
    out["covMethodSupportMedian"] = d(sup_app["cov"].median())
    out["directCovBelowOverallApps"] = common.integer(
        (sup_app["cov_direct"] < sup_app["cov"]).sum())
    out["directCovNeverApps"] = common.integer(
        (sup.groupby("apk")["cov_direct"].max() == 0).sum())

    # Coverage GLM: IRR of one percentage point of method coverage, and alpha.
    nb = fit_rq2(runs).nb
    ci = nb.conf_int()
    out["glmCovRawIrr"] = d(np.exp(nb.params["cov_method"]), 4)
    out["glmCovRawIrrLo"] = d(np.exp(ci.loc["cov_method", 0]), 4)
    out["glmCovRawIrrHi"] = d(np.exp(ci.loc["cov_method", 1]), 4)
    out["glmCovRawIrrP"] = common.pvalue(nb.pvalues["cov_method"])
    out["glmCovRawAlpha"] = d(nb.params["alpha"], 4)
    out["glmCovRawAlphaLo"] = d(ci.loc["alpha", 0], 4)
    out["glmCovRawAlphaHi"] = d(ci.loc["alpha", 1], 4)
    return out


def _long(pivot: pd.DataFrame) -> pd.DataFrame:
    """Tool x timeout pivot -> (row, column, expected) rows, tools sorted, timeouts ascending."""
    rows = [(tool, str(t), common.decimal(round(pivot.loc[tool, t], 2)))
            for tool in sorted(pivot.index) for t in TIMEOUTS]
    return pd.DataFrame(rows, columns=["row", "column", "expected"])


def tables() -> dict[str, pd.DataFrame]:
    cells = _cells(common.run_table())
    return {"coverage": _long(cells["cov"].unstack("timeout")),
            "coverage_mop": _long(cells["cov_direct"].unstack("timeout"))}


def _main() -> int:
    exp = common.load_claims()
    exp = exp[(exp["producer"] == PRODUCER) & (exp["method"] == "script")]
    got = claims()
    n_fail = 0
    lines = []
    for macro, want in zip(exp["macro"], exp["expected"]):
        have = got.get(macro, "<missing>")
        ok = have == want
        n_fail += not ok
        lines.append(f"{'PASS' if ok else 'FAIL'}  {PRODUCER}  {macro}  {have}"
                     + ("" if ok else f"  expected {want}"))
    extra = sorted(set(got) - set(exp["macro"]))
    for macro in extra:
        n_fail += 1
        lines.append(f"FAIL  {PRODUCER}  {macro}  {got[macro]}  expected <no claim row>")
    n_cells = 0
    for name, df in tables().items():
        want = common.load_expected("tables", name)
        if list(want[["row", "column"]].itertuples(index=False)) != \
                list(df[["row", "column"]].itertuples(index=False)):
            n_fail += 1
            lines.append(f"FAIL  {PRODUCER}  table:{name}  row/column order differs")
            continue
        for (r, c, have), w in zip(df.itertuples(index=False), want["expected"]):
            ok = have == w
            n_fail += not ok
            n_cells += 1
            lines.append(f"{'PASS' if ok else 'FAIL'}  {PRODUCER}  table:{name}:{r}:{c}  {have}"
                         + ("" if ok else f"  expected {w}"))
    print("\n".join(lines))
    print(f"{PRODUCER}: {len(exp)} claims, {n_cells} table cells, {n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(_main())
