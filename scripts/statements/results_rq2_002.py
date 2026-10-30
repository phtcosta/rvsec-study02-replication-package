"""Statement results_rq2_002 -- Results, RQ2, Coverage Assessment (first paragraph).

Article sentence:
    "Overall, even the best-performing configuration exercises only about one
    third of the application methods."

Pass criterion (fixed before coding): the best (tool, timeout) mean method
coverage (scripts.rq2.mean_coverage on the run table), as a fraction
(percent / 100), has 1/3 as its nearest of {1/4, 1/3, 1/2}.
"""

from __future__ import annotations

import sys
from fractions import Fraction

from scripts import common
from scripts.rq2 import mean_coverage

CLAIM = "The best configuration covers about one third of the app methods"
EXPECTED = "1/3"
CANDIDATES = (Fraction(1, 4), Fraction(1, 3), Fraction(1, 2))


def nearest(x: float) -> Fraction:
    return min(CANDIDATES, key=lambda c: abs(x - float(c)))


def check() -> tuple[str, bool]:
    cov = mean_coverage(common.run_table()).stack()
    (tool, timeout), pct = cov.idxmax(), float(cov.max())
    share = pct / 100.0
    near = nearest(share)
    return (f"best = {tool} at {timeout} s, mean method coverage {pct:.4f} % "
            f"= {share:.6f}; nearest of 1/4, 1/3, 1/2 = {near}"), str(near) == EXPECTED


if __name__ == "__main__":
    sys.exit(common.run_statement(CLAIM, EXPECTED, check))
