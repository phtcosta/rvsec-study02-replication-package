"""CogniCrypt baseline numbers (Baselines; Results RQ1, Baseline 2).

Inputs (all through ``common``):

- ``per-app-outcomes.csv``: ``status`` of each of the 163 apps (success, error,
  timeout) and ``findings``, the report size of a successful run (empty, never
  zero, for the apps without a verdict).
- ``findings.csv``: one row per CogniCrypt finding (``apk``, ``ViolatedRule``).
- ``dataset.csv``: ``sa_directly_reaches_mop``, joined on ``apk``: False when no
  application method directly invokes a monitored API.
- ``gaps_18.csv``: ``last_attempt_budget`` (``<attempts>x<heap>g/<seconds>s``) of
  each app without a verdict. The smallest heap is the pass-1 budget, the
  largest the retry budget.
- ``crysl-rules.zip``: the CrySL rules copied for the analysis.

``ccRulesLoaded`` and ``ccRulesRejectedWord`` are checked by inspection.
"""

from __future__ import annotations

import sys

import pandas as pd

from scripts import common

PRODUCER = "cognicrypt"
BUDGET = r"^(?P<attempts>\d+)x(?P<heap>\d+)g/(?P<secs>\d+)s$"


def outcomes() -> pd.DataFrame:
    """per-app-outcomes.csv: one row per app, with status and findings."""
    return common.load("cc_outcomes")


def findings() -> pd.DataFrame:
    """findings.csv, every cell a string ('' kept, never NaN)."""
    return common.load("cc_findings", keep_default_na=False)


def budgets() -> tuple[pd.Series, pd.Series]:
    """The pass-1 and the retry budget (heap GB, seconds) from gaps_18.csv."""
    b = common.load("cc_gaps")["last_attempt_budget"].str.extract(BUDGET)
    if b.isna().any().any():
        raise ValueError("a last_attempt_budget is not <n>x<heap>g/<secs>s")
    b = b.astype(int)
    return b.loc[b["heap"].idxmin()], b.loc[b["heap"].idxmax()]


def claims() -> dict[str, str]:
    out = outcomes()
    f = findings()
    status = out["status"].value_counts()
    success = out[out["status"] == "success"]
    n_success = len(success)
    base, retry = budgets()

    reach = common.load("dataset", usecols=["apk", "sa_directly_reaches_mop"],
                        low_memory=False)
    joined = success[["apk", "findings"]].merge(reach, on="apk", how="left",
                                                validate="1:1")
    no_direct = joined["sa_directly_reaches_mop"].astype(str) == "False"
    empty = joined["findings"] == 0

    return {
        "ccRulesCopied": common.integer(len(common.crysl_files())),
        "ccHeapGb": common.integer(base["heap"]),
        "ccTimeLimitHoursWord": common.word(base["secs"] // 3600),
        "ccRetryHeapGb": common.integer(retry["heap"]),
        "ccRetryHoursWord": common.word(retry["secs"] // 3600),
        "ccNoVerdict": common.integer(len(out) - n_success),
        "ccSuccess": common.integer(n_success),
        "ccErrorWord": common.word(status.get("error", 0)),
        "ccTimeoutWord": common.word(status.get("timeout", 0)),
        "ccEmptyReports": common.integer(empty.sum()),
        "ccEmptyNoDirectReach": common.integer((empty & no_direct).sum()),
        "ccNonEmptyNoDirectReach": common.integer((~empty & no_direct).sum()),
        "ccAppsWithFindings": common.integer(f["apk"].nunique()),
        "ccFindings": common.integer(len(f)),
        "ccMeanFindings": common.decimal(len(f) / n_success, 1),
        "ccRulesViolated": common.integer(f["ViolatedRule"].nunique()),
    }


def self_check(producer: str, items: list[tuple[str, str, str]]) -> int:
    """Print PASS/FAIL per (label, computed, expected) and a summary; return the exit code."""
    failed = 0
    for label, got, want in items:
        ok = got == want
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {producer}  {label}  {got}"
              + ("" if ok else f"  expected {want}"))
    print(f"{producer}: {len(items) - failed} passed, {failed} failed")
    return 1 if failed else 0


def script_rows(producer: str) -> pd.DataFrame:
    """The claims.csv rows a producer computes."""
    c = common.load_claims()
    return c[(c["producer"] == producer) & (c["method"] == "script")]


if __name__ == "__main__":
    got = claims()
    rows = script_rows(PRODUCER)
    if set(got) != set(rows["macro"]):
        raise SystemExit(f"macro set differs from claims.csv: {sorted(set(got) ^ set(rows['macro']))}")
    sys.exit(self_check(PRODUCER, [(m, got[m], e) for m, e in zip(rows["macro"], rows["expected"])]))
