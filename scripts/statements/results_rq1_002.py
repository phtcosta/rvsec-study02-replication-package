"""Statement results_rq1_002 -- Results, RQ1, Baselines Comparison, Baseline 1:
Developer-written test cases.

Article sentence:
    "Excluding Robolectric artifacts, approximately one-third of the unit-test
    misuses were also detected by the test-generation tools."

Pass criterion (fixed before coding): share = unit-test misuses that overlap the
campaign (in_rv) and are not robolectric_noise / unit-test misuses that are not
robolectric_noise (scripts.unit_tests.overlap); the nearest of {1/4, 1/3, 1/2} to
the share is 1/3.
"""

from __future__ import annotations

import sys
from fractions import Fraction

from scripts.common import run_statement
from scripts.unit_tests import overlap

CLAIM = "Excluding Robolectric artifacts, about one-third of unit-test misuses overlap"
EXPECTED = "1/3"
CANDIDATES = (Fraction(1, 4), Fraction(1, 3), Fraction(1, 2))


def nearest(x: float) -> Fraction:
    return min(CANDIDATES, key=lambda c: abs(x - float(c)))


def check() -> tuple[str, bool]:
    unit = overlap()
    genuine = unit[unit["categoria"] != "robolectric_noise"]
    hits = int(genuine["in_rv"].sum())
    share = hits / len(genuine)
    near = nearest(share)
    return (f"share = {hits}/{len(genuine)} = {share:.4f}; nearest of 1/4, 1/3, 1/2 = {near}",
            str(near) == EXPECTED)


if __name__ == "__main__":
    sys.exit(run_statement(CLAIM, EXPECTED, check))
