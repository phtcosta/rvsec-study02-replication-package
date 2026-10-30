"""Statement results_rq2_003 -- Results, RQ2, Coverage Assessment (first paragraph).

Article sentence:
    "For every tool, coverage increases with the execution budget."

Pass criterion (fixed before coding): for each of the 11 tools, mean method
coverage (scripts.rq2.mean_coverage on the run table) at 60 s < 180 s < 300 s,
strictly. The tool count is the article's own (macro toolCountWord).
"""

from __future__ import annotations

import sys

from scripts import common
from scripts.rq2 import TIMEOUTS, mean_coverage

CLAIM = "For every tool, mean method coverage increases with the budget"
EXPECTED = f"60 s < 180 s < 300 s for each of the {common.expected('toolCountWord')} tools"
PAD = "\n" + " " * 10


def check() -> tuple[str, bool]:
    cov = mean_coverage(common.run_table())[list(TIMEOUTS)]
    lines, ok = [], True
    for tool, row in cov.iterrows():
        up = all(row[a] < row[b] for a, b in zip(TIMEOUTS, TIMEOUTS[1:]))
        ok &= up
        lines.append(f"{tool:<20} " + " < ".join(f"{row[t]:.4f}" for t in TIMEOUTS)
                     + ("" if up else "  NOT increasing"))
    n_ok = common.word(len(cov)) == common.expected("toolCountWord")
    head = f"{len(cov)} tools (article: {common.expected('toolCountWord')}); mean % at 60/180/300 s:"
    return PAD.join([head] + lines), ok and n_ok


if __name__ == "__main__":
    sys.exit(common.run_statement(CLAIM, EXPECTED, check))
