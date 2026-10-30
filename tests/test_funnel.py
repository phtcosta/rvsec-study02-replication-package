"""Funnel producer: every script claim and figure item matches claims/."""

import pandas as pd
import pytest

from scripts import common, funnel

pytestmark = pytest.mark.skipif(not common.path("dataset").is_file(),
                                reason="data not restored (make restore)")


def test_claims_match():
    rows = common.load_claims().query("producer == 'funnel' and method == 'script'")
    assert funnel.claims() == dict(zip(rows["macro"], rows["expected"]))


def test_figure_matches():
    want = common.load_expected("figures", "selection-funnel")
    got = funnel.figures()["selection-funnel"]
    pd.testing.assert_frame_equal(got.reset_index(drop=True), want)


def test_levels_chain():
    levels = funnel._levels(funnel._dataset())
    for (_, prev, _), (_, left, excl) in zip(levels, levels[1:]):
        assert left == prev - excl
