"""Formatter tests. Expected strings are macro bodies printed in the article."""

import pytest

from scripts.common import decimal, integer, pvalue, word, word99


@pytest.mark.parametrize("value, expected", [
    (3941, "3{,}941"),        # totalAppsFdroid
    (16137, "16{,}137"),      # tasksGrid
    (163, "163"),             # finalDataset
    (1353, "1{,}353"),        # ccFindings
    (91368, "91{,}368"),      # raw events
])
def test_integer(value, expected):
    assert integer(value) == expected


@pytest.mark.parametrize("value, places, expected", [
    (100 * 176 / 16137, 1, "1.1"),           # allZeroPct
    (32.72068328572107, 2, "32.72"),         # coverage.tex, ape at 300 s
    (100 * 81 / 453, 2, "17.88"),            # rawAppCodePct
    (16137 / 163, 1, "99.0"),
    (0.5, 4, "0.5000"),
])
def test_decimal(value, places, expected):
    assert decimal(value, places) == expected


@pytest.mark.parametrize("value, expected", [
    (6, "six"),               # buildOutOfScopeExclWord
    (12, "twelve"),           # ccErrorWord
    (0, "zero"),
    (13, "13"),               # beyond twelve: digits
    (1604, "1{,}604"),
])
def test_word(value, expected):
    assert word(value) == expected


@pytest.mark.parametrize("value, expected", [
    (22, "twenty-two"),       # rawSpecsWord
    (11, "eleven"),
    (13, "thirteen"),
    (19, "nineteen"),
    (20, "twenty"),
    (99, "ninety-nine"),
    (100, "100"),
])
def test_word99(value, expected):
    assert word99(value) == expected


@pytest.mark.parametrize("p, expected", [
    (0.0041779, "0.0042"),                    # glmRawHolmApe
    (0.7304, "0.7304"),                       # glmCovRawIrrP
    (0.00009, r"\ensuremath{<}0.0001"),
    (0.0001, "0.0001"),
])
def test_pvalue(p, expected):
    assert pvalue(p) == expected
