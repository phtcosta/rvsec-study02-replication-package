"""The application-selection funnel (article sections Dataset, Reachability and
Instrumentation; figure ``selection-funnel``).

Inputs:
  - corpus/dataset.csv: ``funnel_stage`` (the stage at which an application left
    the funnel; ``selected`` = the analysis set), ``excluded_reason`` (the reason
    is the text before the first ':'), ``sa_status`` and ``sa_analysis_seconds``
    (the static-analysis time budget, read off the run killed at it);
  - corpus/ground_truth_sheet.csv: ``decided_by`` (how each built application's
    package root was adjudicated).

Every level is the number of applications left after applying the exclusion
stages in pipeline order. The figure collapses the build probe and the full build
into one level ("built unobfuscated and debuggable"), giving 12 levels.

Run: ``python -m scripts.funnel`` prints PASS/FAIL per claim and figure item.
"""

from __future__ import annotations

import sys

import pandas as pd

from scripts.common import decimal, integer, load, load_claims, load_expected, word

PRODUCER = "funnel"

# The exclusion stages in pipeline order; only in this order does the cascade
# close on `selected`.
STAGES = [
    "filtered_compat",
    "filtered_github",
    "filtered_playstore",
    "filtered_build_probe",
    "filtered_build",
    "filtered_dedup",
    "filtered_mneut_scope",
    "filtered_sa_no_json",
    "filtered_no_mop",
    "filtered_smoke",
    "filtered_instrumentation",
    "filtered_zero_coverage",
]

# Figure levels: (item slug, stages whose exclusions produce the level). The
# first level is the full candidate set; the build probe joins the build level.
LEVELS = [
    ("fdroid-candidates", []),
    ("emulator-compatible", ["filtered_compat"]),
    ("github-source-2026-commit", ["filtered_github"]),
    ("google-play", ["filtered_playstore"]),
    ("built-unobfuscated-debuggable", ["filtered_build_probe", "filtered_build"]),
    ("distinct-dex", ["filtered_dedup"]),
    ("scope-key-resolves", ["filtered_mneut_scope"]),
    ("static-analysis-decided", ["filtered_sa_no_json"]),
    ("reach-monitored-api", ["filtered_no_mop"]),
    ("original-apk-runs", ["filtered_smoke"]),
    ("instrumented-validated", ["filtered_instrumentation"]),
    ("final-analysis-set", ["filtered_zero_coverage"]),
]


def _dataset() -> pd.DataFrame:
    df = load("dataset", low_memory=False)
    return df.assign(reason=df["excluded_reason"].fillna("").str.split(":").str[0])


def _counts(df: pd.DataFrame) -> tuple[dict, dict]:
    """Stage sizes and (stage, reason) sizes."""
    stage = df["funnel_stage"].value_counts().to_dict()
    reason = df.groupby(["funnel_stage", "reason"]).size().to_dict()
    return stage, reason


def _levels(df: pd.DataFrame) -> list[tuple[str, int, int | None]]:
    """The 12 presented levels: (slug, applications left, excluded at the level)."""
    stage, _ = _counts(df)
    left, out = len(df), []
    for slug, stages in LEVELS:
        excl = sum(int(stage.get(s, 0)) for s in stages)
        left -= excl
        out.append((slug, left, excl if stages else None))
    return out


def claims() -> dict[str, str]:
    """The funnel macros (fdroidIndexDate is checked by inspection)."""
    df = _dataset()
    stage, reason = _counts(df)

    def n(s: str) -> int:
        return int(stage.get(s, 0))

    def r(s: str, *reasons: str) -> int:
        return sum(int(reason.get((s, x), 0)) for x in reasons)

    after, left = {}, len(df)
    for s in STAGES:
        left -= n(s)
        after[s] = left

    # Static-analysis budget: the run killed at it (Reachability).
    budget = df.loc[df["sa_status"] == "failed_timeout_no_json",
                    "sa_analysis_seconds"].max()
    gt = load("ground_truth", dtype=str, keep_default_na=False)["decided_by"].value_counts()

    instr_pool = after["filtered_smoke"]
    instrumented = after["filtered_instrumentation"]
    sa_decided = after["filtered_sa_no_json"]
    reaches = after["filtered_no_mop"]
    return {
        "finalDataset": integer(after["filtered_zero_coverage"]),
        # Dataset
        "totalAppsFdroid": integer(len(df)),
        "emulatorCompatExcl": integer(n("filtered_compat")),
        "abiExcl": integer(r("filtered_compat", "abi_no_x86")),
        "minSdkExcl": integer(r("filtered_compat", "minsdk>30")),
        "emulatorCompatApps": integer(after["filtered_compat"]),
        "githubExcl": integer(n("filtered_github")),
        "staleCommitExcl": integer(r("filtered_github", "stale_commit")),
        "notGithubExcl": integer(r("filtered_github", "not_github")),
        "repoUnresolvableExcl": integer(r("filtered_github", "repo_404", "repo_url_invalid")),
        "githubApps": integer(after["filtered_github"]),
        "playstoreExcl": integer(n("filtered_playstore")),
        "playstoreApps": integer(after["filtered_playstore"]),
        "builtApps": integer(after["filtered_build"]),
        # A failed or inconclusive build (probe or full) yields no usable APK.
        "buildFailedExcl": integer(r("filtered_build_probe", "build_probe_failed")
                                   + r("filtered_build", "build_failed", "build_inconclusive")),
        "buildOutOfScopeExclWord": word(r("filtered_build", "out_of_scope")),
        "dedupExcl": integer(n("filtered_dedup")),
        "dedupApps": integer(after["filtered_dedup"]),
        # Reachability
        "gtAuto": integer(gt.get("auto", 0)),
        "gtAutoSingleWord": word(gt.get("auto_single_witness", 0)),
        "gtManual": integer(gt.get("manual", 0)),
        "mneutScopeExcl": integer(n("filtered_mneut_scope")),
        "mneutCollapseExcl": integer(r("filtered_mneut_scope", "mneut_collapse")),
        "mneutCovExcl": integer(r("filtered_mneut_scope", "mneut_cov")),
        "mneutForeignExclWord": word(r("filtered_mneut_scope", "mneut_foreign")),
        "mneutScopeApps": integer(after["filtered_mneut_scope"]),
        "saNoJsonExclWord": word(n("filtered_sa_no_json")),
        "saBudgetMin": integer(budget // 60),
        "saDecidedApps": integer(sa_decided),
        "reachesMopApps": integer(reaches),
        # Share of the applications the static analysis decided.
        "reachesMopPct": decimal(100.0 * reaches / sa_decided, 1),
        "noMopExcl": integer(n("filtered_no_mop")),
        # Instrumentation
        "smokeInstallExclWord": word(r("filtered_smoke", "smoke_install_failed")),
        "smokeCrashExclWord": word(r("filtered_smoke", "smoke_launch_crash")),
        "instrumentationPool": integer(instr_pool),
        "instrumented": integer(instrumented),
        "instrumentationSuccessPct": decimal(100.0 * instrumented / instr_pool, 1),
        "notInstrumentedWord": word(n("filtered_instrumentation")),
        "weaverBlindExclWord": word(n("filtered_zero_coverage")),
    }


def figures() -> dict[str, pd.DataFrame]:
    """The selection-funnel figure: 12 levels, then the 11 exclusions."""
    levels = _levels(_dataset())
    rows = [(f"level-{i:02d}-{slug}", integer(left))
            for i, (slug, left, _) in enumerate(levels, 1)]
    rows += [(f"excl-{i:02d}-{slug}", integer(excl))
             for i, (slug, _, excl) in enumerate(levels, 1) if excl is not None]
    return {"selection-funnel": pd.DataFrame(rows, columns=["item", "expected"])}


def _check() -> int:
    rows = load_claims().query("producer == @PRODUCER and method == 'script'")
    got, fails, passed = claims(), 0, 0
    if set(got) != set(rows["macro"]):
        print(f"FAIL  {PRODUCER}  macro set differs: "
              f"{sorted(set(got) ^ set(rows['macro']))}")
        fails += 1
    for macro, exp in zip(rows["macro"], rows["expected"]):
        value = got.get(macro, "<missing>")
        ok = value == exp
        passed, fails = passed + ok, fails + (not ok)
        print(f"{'PASS' if ok else 'FAIL'}  {PRODUCER}  {macro}  {value}"
              + ("" if ok else f"  expected {exp}"))
    for key, frame in figures().items():
        want = load_expected("figures", key)
        if list(frame["item"]) != list(want["item"]):
            print(f"FAIL  {PRODUCER}  figure:{key} item list or order differs")
            fails += 1
        computed = dict(zip(frame["item"], frame["expected"]))
        for item, exp in zip(want["item"], want["expected"]):
            value = computed.get(item, "<missing>")
            ok = value == exp
            passed, fails = passed + ok, fails + (not ok)
            print(f"{'PASS' if ok else 'FAIL'}  {PRODUCER}  figure:{key}:{item}  {value}"
                  + ("" if ok else f"  expected {exp}"))
    print(f"{PRODUCER}: {passed} passed, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_check())
