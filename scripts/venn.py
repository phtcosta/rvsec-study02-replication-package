"""RV x CogniCrypt comparison at tuple level (Results RQ1, Baseline 2; Venn figure).

A tuple is (apk, class, method, spec).

- RV side: the distinct tuples of ``raw-accusations.csv``.
- CC side: ``findings.csv`` with ``spec`` = last component of ``ViolatedRule``
  + ``Spec`` (every ``ViolatedRule`` is the ``SPEC`` class of a copied CrySL
  rule) and ``method`` = the method name in the soot signature ``Method``.

Only-RV tuples are split by cause, first match wins: the app has no CogniCrypt
verdict (``per-app-outcomes.csv`` status != success), its report is empty
(findings == 0), the spec belongs to a rule CogniCrypt rejected (the
"Skipping rule since it contains errors: .../X.crysl" lines of
``cognicrypt_summary.csv:error_message``), the class is absent from the app's
CogniCrypt findings, or the class is reported (under other tuples).

``vennTupOnlyCCAdmittedWord`` is checked by inspection.
"""

from __future__ import annotations

import re
import sys

import pandas as pd

from scripts import common
from scripts.cognicrypt import findings, outcomes, script_rows, self_check

PRODUCER = "venn"
TUP = ["apk", "class", "method", "spec"]
METHOD_NAME = r"(<init>|<clinit>|[A-Za-z_$][\w$]*)(?=\()"
REJECTED = r"Skipping rule since it contains errors: \S*/(\w+)\.crysl"


def cc_findings() -> pd.DataFrame:
    """CogniCrypt findings with the tuple columns added."""
    f = findings().rename(columns={"Class": "class"})
    if not set(f["ViolatedRule"]) <= common.crysl_spec_classes():
        raise ValueError("a ViolatedRule is not the SPEC class of a copied CrySL rule")
    f["spec"] = f["ViolatedRule"].str.split(".").str[-1] + "Spec"
    f["method"] = f["Method"].str.extract(METHOD_NAME, expand=False)
    return f


def rv_tuples() -> pd.DataFrame:
    return common.load("raw_accusations", usecols=TUP, keep_default_na=False).drop_duplicates()


def rejected_specs() -> set[str]:
    """Specs of the CrySL rules CogniCrypt refused to load."""
    log = common.load("cc_summary", usecols=["error_message"])["error_message"].dropna()
    return {name + "Spec" for msg in log for name in re.findall(REJECTED, msg)}


def compute() -> tuple[dict[str, str], dict[str, int]]:
    cc = cc_findings()
    rv = rv_tuples()
    m = cc[TUP].drop_duplicates().merge(rv, on=TUP, how="outer", indicator=True)
    only_rv = m[m["_merge"] == "right_only"]
    only_cc = m[m["_merge"] == "left_only"]
    both = m[m["_merge"] == "both"]

    out = outcomes()
    success = set(out.loc[out["status"] == "success", "apk"])
    empty = set(out.loc[(out["status"] == "success") & (out["findings"] == 0), "apk"])
    rejected = rejected_specs()
    cc_classes = set(zip(cc["apk"], cc["class"]))

    def cause(apk, cls, spec):
        if apk not in success:
            return "no-verdict"
        if apk in empty:
            return "empty-report"
        if spec in rejected:
            return "rejected-rule"
        if (apk, cls) not in cc_classes:
            return "class-absent"
        return "class-reported"

    causes = pd.Series([cause(a, c, s) for a, c, s in
                        zip(only_rv["apk"], only_rv["class"], only_rv["spec"])]).value_counts()

    # Only-CC tuples whose findings are all IncompleteOperationError.
    types = only_cc[TUP].merge(cc[TUP + ["ErrorType"]], on=TUP).groupby(TUP)["ErrorType"]
    incomplete = int(types.agg(lambda t: set(t) == {"IncompleteOperationError"}).sum())

    # Sensitivity: both sides restricted to the apps with a CogniCrypt verdict.
    sens_only_rv = int(only_rv["apk"].isin(success).sum())
    shared = both["spec"].value_counts()

    n = {"only-rv": len(only_rv), "both": len(both), "only-cc": len(only_cc),
         "total-rv": len(rv), "total-cc": len(both) + len(only_cc)}
    i, w = common.integer, common.word
    values = {
        "vennTupCC": i(n["total-cc"]),
        "vennTupBoth": i(n["both"]),
        "vennTupOnlyRV": i(n["only-rv"]),
        "vennTupOnlyCC": i(n["only-cc"]),
        "vennTupBothSslContext": i(shared.get("SSLContextSpec", 0)),
        "vennTupBothTmf": i(shared.get("TrustManagerFactorySpec", 0)),
        "vennTupOnlyRVNoVerdict": i(causes.get("no-verdict", 0)),
        "vennTupSensOnlyRV": i(sens_only_rv),
        "vennTupOnlyRVNothing": i(causes.get("no-verdict", 0) + causes.get("empty-report", 0)),
        "vennTupOnlyRVRejectedRuleWord": w(causes.get("rejected-rule", 0)),
        "vennTupOnlyRVClassAbsent": i(causes.get("class-absent", 0)),
        "vennTupOnlyRVClassReportedWord": w(causes.get("class-reported", 0)),
        "vennTupOnlyCCIncomplete": i(incomplete),
    }
    return values, n


def claims() -> dict[str, str]:
    return compute()[0]


def figures() -> dict[str, pd.DataFrame]:
    """The Venn diagram's region sizes, in the order of claims/figures/venn-diagram.csv."""
    n = compute()[1]
    items = ["only-rv", "both", "only-cc", "total-rv", "total-cc"]
    return {"venn-diagram": pd.DataFrame({"item": items,
                                          "expected": [str(n[k]) for k in items]})}


if __name__ == "__main__":
    got = claims()
    rows = script_rows(PRODUCER)
    if set(got) != set(rows["macro"]):
        raise SystemExit(f"macro set differs from claims.csv: {sorted(set(got) ^ set(rows['macro']))}")
    items = [(m, got[m], e) for m, e in zip(rows["macro"], rows["expected"])]
    for stem, df in figures().items():
        want = common.load_expected("figures", stem)
        if list(df["item"]) != list(want["item"]):
            raise SystemExit(f"figure {stem}: items differ from claims/figures")
        items += [(f"figure:{stem}:{k}", v, e)
                  for k, v, e in zip(df["item"], df["expected"], want["expected"])]
    sys.exit(self_check(PRODUCER, items))
