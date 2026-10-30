"""Loader tests: a missing file fails loudly with the restore hint."""

import pytest

from scripts import common


@pytest.fixture
def empty_data(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "ROOT", tmp_path)
    monkeypatch.setattr(common, "DATA", tmp_path / "data")
    monkeypatch.setattr(common, "MOP_DIR", tmp_path / "data" / "instrument" / "specs")
    monkeypatch.setattr(common, "CRYSL_DIR",
                        tmp_path / "data" / "baselines" / "cognicrypt" / "crysl-rules")


@pytest.mark.parametrize("name", sorted(common.FILES))
def test_missing_csv(empty_data, name):
    with pytest.raises(FileNotFoundError, match="make restore"):
        common.load(name)


@pytest.mark.parametrize("listing", [common.mop_files, common.crysl_files])
def test_missing_directory(empty_data, listing):
    with pytest.raises(FileNotFoundError, match="make restore"):
        listing()


def test_unknown_name():
    with pytest.raises(KeyError):
        common.load("no-such-file")


def test_claims_header():
    assert list(common.load_claims().columns) == common.CLAIM_COLUMNS
