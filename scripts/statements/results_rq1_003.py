"""Statement results_rq1_003 -- Results, RQ1, Baselines Comparison, Baseline 1:
Developer-written test cases.

Article sentence:
    "All overlapping misuses originate from production code or third-party
    libraries."

Pass criterion (fixed before coding): no overlapping unit-test misuse (in_rv in
scripts.unit_tests.overlap) has origin test code or Robolectric, i.e. categoria
test_code or robolectric_noise.
"""

from __future__ import annotations

import sys

from scripts.common import run_statement
from scripts.unit_tests import overlap

CLAIM = "All overlapping misuses come from production code or libraries"
EXPECTED = "0 overlapping misuses with categoria test_code or robolectric_noise"
EXCLUDED = ("test_code", "robolectric_noise")


def check() -> tuple[str, bool]:
    unit = overlap()
    hits = unit[unit["in_rv"]]
    counts = hits["categoria"].value_counts().sort_index()
    bad = int(hits["categoria"].isin(EXCLUDED).sum())
    by_cat = ", ".join(f"{cat} {n}" for cat, n in counts.items())
    return (f"{len(hits)} overlapping misuses by categoria: {by_cat}; "
            f"{bad} with categoria test_code or robolectric_noise"), bad == 0


if __name__ == "__main__":
    sys.exit(run_statement(CLAIM, EXPECTED, check))
