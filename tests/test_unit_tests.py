"""unit_tests: the overlap helper and the claim set."""

from scripts import common, unit_tests


def test_overlap_shape():
    ov = unit_tests.overlap()
    assert list(ov.columns) == common.MISUSE_KEY + ["categoria", "in_rv"]
    assert not ov.duplicated(subset=common.MISUSE_KEY).any()
    assert ov["in_rv"].dtype == bool


def test_claims_cover_the_registry():
    rows = common.load_claims()
    mine = rows.loc[(rows["producer"] == "unit_tests") & (rows["method"] == "script"), "macro"]
    assert set(unit_tests.claims()) == set(mine)
