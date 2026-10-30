"""Statement results_rq1_004 -- Results, RQ1, Baselines Comparison, Baseline 2: CogniCrypt.

Article sentences:
    "As an example of a misuse detected through dynamic analysis but missed by
    CogniCrypt, consider the application org.cry.otp_31.apk (mOTP). [...]
    RV detects two constraint violations involving HmacSHA1 (MAC-ALG-00) and
    RAW (SECRETKEYSPEC-ALG-00). CogniCrypt reports neither violation in this
    class."

Pass criterion (fixed before coding): both MAC-ALG-00 and SECRETKEYSPEC-ALG-00
are present in raw-accusations.csv (column code) for org.cry.otp_31.apk and class
org.cry.otp.TOTP, and no CogniCrypt finding (findings.csv: apk, Class,
ViolatedRule) for that app and class has ViolatedRule javax.crypto.Mac or
javax.crypto.spec.SecretKeySpec. Extended 2026-10-29 (consistency review): the
rows of each code for that app and class in primary-accusations.csv carry the
value the sentence names, val='HmacSHA1' for MAC-ALG-00 and val='RAW' for
SECRETKEYSPEC-ALG-00, and no other value.
"""

from __future__ import annotations

import sys

from scripts import common

CLAIM = "mOTP TOTP: RV reports MAC-ALG-00 and SECRETKEYSPEC-ALG-00, CogniCrypt neither"
APK = "org.cry.otp_31.apk"
CLASS = "org.cry.otp.TOTP"
VALUES = {"MAC-ALG-00": "HmacSHA1", "SECRETKEYSPEC-ALG-00": "RAW"}
CODES = tuple(VALUES)
RULES = ("javax.crypto.Mac", "javax.crypto.spec.SecretKeySpec")
EXPECTED = (f"RV codes {' and '.join(f'{c} ({v})' for c, v in VALUES.items())} in {CLASS}; "
            f"no CogniCrypt {' or '.join(RULES)} finding in {CLASS}")
PAD = "\n" + " " * 10


def check() -> tuple[str, bool]:
    raw = common.load("raw_accusations", usecols=["apk", "class", "code"], dtype=str,
                      keep_default_na=False)
    rv_codes = sorted(set(raw.loc[(raw["apk"] == APK) & (raw["class"] == CLASS), "code"]))
    cc = common.load("cc_findings", usecols=["apk", "Class", "ViolatedRule"], dtype=str,
                     keep_default_na=False)
    cc = cc[cc["apk"] == APK]
    cc_bad = cc[(cc["Class"] == CLASS) & cc["ViolatedRule"].isin(RULES)]
    prim = common.load("primary_accusations", usecols=["apk", "class", "code", "message"],
                       dtype=str, keep_default_na=False)
    prim = prim[(prim["apk"] == APK) & (prim["class"] == CLASS) & prim["code"].isin(CODES)]
    vals = (prim.assign(val=prim["message"].str.extract(r"val='([^']*)'", expand=False))
            .groupby("code")["val"].apply(lambda v: sorted(set(v.fillna("")))))
    rv_ok = all(c in rv_codes for c in CODES) \
        and all(vals.get(c) == [v] for c, v in VALUES.items())

    lines = [f"RV codes in {CLASS}: {', '.join(rv_codes) or 'none'}",
             "values in primary-accusations: "
             + ", ".join(f"{c} {vals.get(c, [])}" for c in CODES),
             f"CogniCrypt findings of {APK} by class (count):"]
    for (cls, rule), n in cc.groupby(["Class", "ViolatedRule"]).size().items():
        lines.append(f"  {cls:<20} {rule:<34} {n}")
    if CLASS not in set(cc["Class"]):
        lines.append(f"  {CLASS:<20} (no finding)")
    lines.append(f"CogniCrypt Mac/SecretKeySpec findings in {CLASS}: {len(cc_bad)}")
    return PAD.join(lines), rv_ok and cc_bad.empty


if __name__ == "__main__":
    sys.exit(common.run_statement(CLAIM, EXPECTED, check))
