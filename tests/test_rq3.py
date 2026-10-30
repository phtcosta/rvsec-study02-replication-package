"""RQ3 producer: every script row and every table cell matches claims/."""

import pandas as pd

from scripts import rq3
from scripts.common import load_claims, load_expected


def test_claims_match():
    cl = load_claims()
    exp = cl[(cl["producer"] == "rq3") & (cl["method"] == "script")]
    assert rq3.claims() == dict(zip(exp["macro"], exp["expected"]))


def test_table_matches():
    want = load_expected("tables", rq3.TABLE)
    pd.testing.assert_frame_equal(rq3.tables()[rq3.TABLE], want)
