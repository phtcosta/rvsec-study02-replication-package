"""RQ3: where the JCA misuses sit (app code vs libraries) and the recurring patterns.

Computes the 24 ``rq3`` macros of claims.csv and the table ``top-jca-violations``
(article: Instrumentation, Results RQ3, Discussion). A unique misuse is a distinct
(apk, spec, class, method) over the raw reports.

Inputs (via common.py):
- raw-accusations.csv: apk, spec, class, method, code (every raw report = one event);
- codes.csv: code, label ('platform-default' marks the default-trust pattern);
- dataset.csv (funnel_stage == 'selected') and mneut_348.csv (Mneut): app code is a
  class under the app's Mneut package (common.is_app_code);
- primary-accusations.csv: code, message; the value patterns (MD5, SHA-1, AES/ECB,
  old protocol, PBE iterations) read ``val='...'`` from the message;
- severe-sites.csv: verdict 'trust-all' and 'constant' (fixed value) sites;
- specs.zip: the .mop specifications (jcaSpecCount).
"""

from __future__ import annotations

import sys
from functools import lru_cache

import pandas as pd

from scripts.common import (MISUSE_KEY, decimal, integer, is_app_code, load, load_claims, load_expected,
                            mop_files, word)

PRODUCER = "rq3"
TABLE = "top-jca-violations"


@lru_cache(maxsize=1)
def events() -> pd.DataFrame:
    """Raw reports joined with their code label and flagged app code (one row per event)."""
    raw = load("raw_accusations", dtype=str, keep_default_na=False,
               usecols=MISUSE_KEY + ["code"])
    codes = load("codes", usecols=["code", "label"])
    ds = load("dataset", usecols=["apk", "funnel_stage"])
    keys = load("mneut", usecols=["apk", "Mneut"])
    keys = keys[keys["apk"].isin(ds.loc[ds["funnel_stage"] == "selected", "apk"])]
    ev = (raw.merge(codes, on="code", how="inner", validate="m:1")
             .merge(keys, on="apk", how="left", validate="m:1"))
    ev["is_app"] = [isinstance(m, str) and m != "" and is_app_code(c, m)
                    for c, m in zip(ev["class"], ev["Mneut"])]
    return ev


def misuses() -> pd.DataFrame:
    """One row per unique misuse, with its app-code flag."""
    return events().drop_duplicates(MISUSE_KEY)


def per_spec() -> pd.DataFrame:
    """Unique misuses and app-code misuses per spec, by total descending then spec."""
    t = (misuses().groupby("spec")
         .agg(total=("apk", "size"), app=("is_app", "sum")).reset_index())
    return t.sort_values(["total", "spec"], ascending=[False, True], ignore_index=True)


def tables() -> dict[str, pd.DataFrame]:
    """The table of Results RQ3: per spec Total, App-code, App-code (%)."""
    rows = []
    for r in per_spec().itertuples():
        rows += [(r.spec, "Total", integer(r.total)),
                 (r.spec, "App-code", integer(r.app)),
                 (r.spec, "App-code (%)", decimal(100 * r.app / r.total, 2))]
    return {TABLE: pd.DataFrame(rows, columns=["row", "column", "expected"])}


def _count(rows: pd.DataFrame) -> int:
    """Number of distinct unique misuses among some rows."""
    return len(rows[MISUSE_KEY].drop_duplicates())


def patterns() -> dict[str, int]:
    """The recurring patterns of Results RQ3, in unique misuses."""
    ev = events()
    pd_trust = ev[(ev["label"] == "platform-default")
                  & ev["spec"].isin(["TrustManagerFactorySpec", "SSLContextSpec"])]
    prim = load("primary_accusations", usecols=MISUSE_KEY + ["code", "message"])
    prim["val"] = prim["message"].str.extract(r"val='([^']*)'", expand=False)
    md = prim[prim["code"].str.startswith("MESSAGEDIGEST-ALG-")]
    md_alg = md["val"].str.upper().str.replace("-", "", regex=False)
    cipher = prim[prim["code"].str.startswith("CIPHER-ALG-")]
    sites = load("severe_sites")
    return {
        "default_trust": _count(pd_trust),
        "default_trust_okhttp": _count(
            pd_trust[pd_trust["class"] == "okhttp3.internal.platform.Platform"]),
        "md5": _count(md[md_alg == "MD5"]),
        "sha1": _count(md[md_alg == "SHA1"]),
        "ecb_aes": _count(cipher[cipher["val"].str.upper().str.startswith("AES/ECB")]),
        "old_protocol": _count(prim[prim["code"].str.contains("-PROTO-", regex=False)]),
        "pbe_iterations": _count(prim[prim["code"].str.startswith("PBEKEYSPEC-CONSTR-00")]),
        "keystore_order": _count(ev[ev["code"] == "KEYSTORE-ORDER-00"]),
        "trust_all": _count(sites[sites["verdict"] == "trust-all"]),
        "fixed_value": _count(sites[sites["verdict"] == "constant"]),
    }


def claims() -> dict[str, str]:
    """Macro name -> formatted value for the rq3 script rows."""
    ev, u, spec = events(), misuses(), per_spec()
    total, app = len(u), int(u["is_app"].sum())
    lib = total - app

    # Discussion: the three largest library namespaces (package cut to three segments).
    libs = u.loc[~u["is_app"], "class"]
    ns = libs.str.rsplit(".", n=1).str[0].str.split(".").str[:3].str.join(".")
    top3 = ns.value_counts().iloc[:3].sum()

    # Propagation: apps sharing the same (spec, class, method).
    prop = u.groupby(["spec", "class", "method"])["apk"].nunique()

    ks = spec.set_index("spec").loc["KeyStoreSpec"]
    p = patterns()
    return {
        "jcaSpecCount": integer(len(mop_files())),
        "rawPatDefaultTrust": integer(p["default_trust"]),
        "rawPatDefaultTrustOkhttp": integer(p["default_trust_okhttp"]),
        "rawPatMdFive": integer(p["md5"]),
        "rawPatShaOne": integer(p["sha1"]),
        "ecbAesMisuses": integer(p["ecb_aes"]),
        "rawPatOldProtocolWord": word(p["old_protocol"]),
        "rawPatPbeIterationsWord": word(p["pbe_iterations"]),
        "rawPatKeyStoreOrderWord": word(p["keystore_order"]),
        "rawPatFixedValueWord": word(p["fixed_value"]),
        "rawPatTrustAllWord": word(p["trust_all"]),
        "rawAppCodePct": decimal(100 * app / total, 2),
        "rawAppCodeCount": integer(app),
        "rawLibPct": decimal(100 * lib / total, 2),
        "rawAppCodeEventsPct": decimal(100 * ev["is_app"].sum() / len(ev), 2),
        "rawSpecTopAppCode": integer(spec["app"].max()),
        "keyStoreAppCode": integer(ks["app"]),
        "keyStoreTotal": integer(ks["total"]),
        "keyStoreAppCodePct": decimal(100 * ks["app"] / ks["total"], 2),
        "rawPropagationTopApps": integer(prop.max()),
        "rawPropagationCombos": integer(len(prop)),
        "rawPropagationMultiApp": integer((prop > 1).sum()),
        "rawSpecTopMisuses": integer(spec["total"].iloc[0]),
        "rawLibTopNamespacesPct": decimal(100 * top3 / lib, 1),
    }


def _check() -> int:
    cl = load_claims()
    exp = cl[(cl["producer"] == PRODUCER) & (cl["method"] == "script")]
    got = claims()
    lines = []
    for macro, want in zip(exp["macro"], exp["expected"]):
        have = got.get(macro, "<missing>")
        lines.append((have == want, f"{macro}  {have}", want))
    for macro in sorted(set(got) - set(exp["macro"])):
        lines.append((False, f"{macro}  {got[macro]}", "<not in claims.csv>"))
    for stem, df in tables().items():
        want_df = load_expected("tables", stem)
        n = max(len(df), len(want_df))
        for i in range(n):
            have = tuple(df.iloc[i]) if i < len(df) else ("", "", "<missing>")
            want = tuple(want_df.iloc[i]) if i < len(want_df) else ("", "", "<extra>")
            ok = have == want
            lines.append((ok, f"table:{stem}:{have[0]}:{have[1]}  {have[2]}",
                          f"{want[0]}:{want[1]} {want[2]}"))
    fails = 0
    for ok, text, want in lines:
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {PRODUCER}  {text}"
              + ("" if ok else f"  expected {want}"))
    print(f"{PRODUCER}: {len(lines) - fails} PASS, {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_check())
