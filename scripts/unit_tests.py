"""RQ1, Baseline 1: the apps' own unit-test suites run under RV.

Computes the 23 ``unit_tests`` macros of the article (Baselines; Results, RQ1,
Baseline 1). Raw reports on both sides: every unit-test report against every
campaign report, with no label rule on either side.

Inputs (all through common.load):
  unit_status      has_unit_tests (yes/no), test_status (success/fail) per app.
  unit_errors      every raw unit-test report; a misuse is a distinct MISUSE_KEY.
  unit_categories  origin of each unit-test misuse (categoria: app_producao, lib,
                   test_code, robolectric_noise), 1:1 on MISUSE_KEY.
  raw_accusations  every campaign report (MISUSE_KEY columns only).
  mneut            the app's root package (Mneut), for the app-code criterion.
"""

from __future__ import annotations

import sys

import pandas as pd

from scripts import common
from scripts.common import MISUSE_KEY

PRODUCER = "unit_tests"


def _unit_errors() -> pd.DataFrame:
    """Every raw unit-test report."""
    return common.load("unit_errors", keep_default_na=False)


def _unit_misuses() -> pd.DataFrame:
    """Unique unit-test misuses with their origin category."""
    unique = _unit_errors().drop_duplicates(subset=MISUSE_KEY)[MISUSE_KEY]
    cats = common.load("unit_categories", keep_default_na=False)[MISUSE_KEY + ["categoria"]]
    out = unique.merge(cats, on=MISUSE_KEY, how="left", validate="1:1")
    if (out["categoria"].isna() | (out["categoria"] == "")).any():
        raise ValueError("a unit-test misuse has no categoria")
    return out.reset_index(drop=True)


def _campaign_misuses() -> pd.DataFrame:
    """Unique campaign raw misuses (MISUSE_KEY only)."""
    raw = common.load("raw_accusations", usecols=MISUSE_KEY, dtype=str,
                      keep_default_na=False)[MISUSE_KEY]
    return raw.drop_duplicates().reset_index(drop=True)


def _keys(df: pd.DataFrame) -> set[tuple]:
    return set(map(tuple, df[MISUSE_KEY].values))


def overlap(campaign: pd.DataFrame | None = None) -> pd.DataFrame:
    """Unique unit-test misuses: MISUSE_KEY + categoria + in_rv (key among the
    campaign's raw misuses; ``campaign`` defaults to them, loaded here)."""
    unit = _unit_misuses()
    rv = _keys(_campaign_misuses() if campaign is None else campaign)
    unit["in_rv"] = [tuple(k) in rv for k in unit[MISUSE_KEY].values]
    return unit


def claims() -> dict[str, str]:
    """Macro name -> formatted value for the 23 unit-test macros."""
    status = common.load("unit_status")
    with_tests = int((status["has_unit_tests"] == "yes").sum())
    without_tests = int((status["has_unit_tests"] == "no").sum())
    success = int((status["test_status"] == "success").sum())
    fail = int((status["test_status"] == "fail").sum())
    success_apks = set(status.loc[status["test_status"] == "success", "apk"])
    no_unit_apks = set(status.loc[status["has_unit_tests"] == "no", "apk"])

    errors = _unit_errors()
    campaign = _campaign_misuses()
    unit = overlap(campaign)
    cat = unit["categoria"].value_counts()
    robo = int(cat.get("robolectric_noise", 0))

    # Apps by the origin categories of their unit-test misuses.
    app_cats = unit.groupby("apk")["categoria"].apply(set)
    all_robo = {a for a, c in app_cats.items() if c == {"robolectric_noise"}}
    genuine = set(app_cats.index) - all_robo
    production = {a for a, c in app_cats.items() if "app_producao" in c}

    rv_apks = set(campaign["apk"])
    unit_only = set(app_cats.index) - rv_apks

    # Campaign app-code misuses in apps whose tests ran, and those the tests missed.
    mneut = common.load("mneut", usecols=["apk", "Mneut"])
    rv = campaign.merge(mneut, on="apk", how="left", validate="m:1")
    if rv["Mneut"].isna().any():
        raise ValueError("a campaign app without its Mneut")
    is_app = [common.is_app_code(c, m) for c, m in zip(rv["class"], rv["Mneut"])]
    app_code = rv[pd.Series(is_app, index=rv.index) & rv["apk"].isin(success_apks)]
    unit_keys = _keys(unit)
    bidir = app_code[[tuple(k) not in unit_keys for k in app_code[MISUSE_KEY].values]]

    i, w = common.integer, common.word
    return {
        "unitWithTests": i(with_tests),
        "unitSuccess": i(success),
        "unitWithTestsPct": common.decimal(100.0 * with_tests / len(status), 1),
        "unitWithoutTests": i(without_tests),
        "unitSuccessPct": common.decimal(100.0 * success / with_tests, 1),
        "unitFailWord": w(fail),
        "unitRawEvents": i(len(errors)),
        "unitRawMisuses": i(len(unit)),
        "unitRawApps": i(errors["apk"].nunique()),
        "unitRawOriginProduction": i(cat.get("app_producao", 0)),
        "unitRawOriginLib": i(cat.get("lib", 0)),
        "unitRawOriginTestCode": i(cat.get("test_code", 0)),
        "unitRawOriginRobolectric": i(robo),
        "unitRawRobolectricPct": common.decimal(100.0 * robo / len(unit), 1),
        "unitRawOnlyAppsWord": w(len(unit_only)),
        "unitRawOnlyAllRoboAppsWord": w(len(unit_only & all_robo)),
        "unitRawOnlyGenuineAppsWord": w(len(genuine - rv_apks)),
        "unitRawOnlyProductionAppsWord": w(len(production - rv_apks)),
        "unitRawKeyMatch": i(unit["in_rv"].sum()),
        "noUnitRvRawApps": i(len(no_unit_apks & rv_apks)),
        "rvRawAppCodeMisuses": i(len(app_code)),
        "bidirRawAppCodeMisuses": i(len(bidir)),
        "bidirRawAppCodeApps": i(bidir["apk"].nunique()),
    }


def main() -> int:
    rows = common.load_claims()
    rows = rows[(rows["producer"] == PRODUCER) & (rows["method"] == "script")]
    got = claims()
    passed = failed = 0
    for macro, exp in zip(rows["macro"], rows["expected"]):
        value = got.get(macro, "<missing>")
        ok = value == exp
        passed, failed = passed + ok, failed + (not ok)
        print(f"{'PASS' if ok else 'FAIL'}  {PRODUCER}  {macro}  {value}"
              + ("" if ok else f"  expected {exp}"))
    for macro in sorted(set(got) - set(rows["macro"])):
        failed += 1
        print(f"FAIL  {PRODUCER}  {macro}  {got[macro]}  expected <no claims.csv row>")
    print(f"{PRODUCER}: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
