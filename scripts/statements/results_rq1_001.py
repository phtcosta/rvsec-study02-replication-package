"""Statement results_rq1_001 -- Results, RQ1, Statistical Analysis (GLM paragraph).

Article sentence:
    "The response exhibits substantial overdispersion (variance-to-mean ratio =
    \\glmRawVarMean), and a likelihood-ratio test favors the NB model over a
    Poisson model (p < 10^-300)."

Pass criterion (fixed before coding): in the RQ1 NB2 fit (scripts.rq1.fit_rq1 on
the run table), log10 p of the boundary-corrected LR test, p = 0.5 * chi2_1.sf(LR)
computed by common.lr_log10_p, is finite and < -300.
"""

from __future__ import annotations

import math
import sys

from scripts import common
from scripts.rq1 import fit_rq1

CLAIM = "RQ1: LR test favors NB2 over Poisson"
EXPECTED = "p < 10^-300"
LOG10_BOUND = -300


def check() -> tuple[str, bool]:
    fit = fit_rq1(common.run_table())
    ok = math.isfinite(fit.log10_p) and fit.log10_p < LOG10_BOUND
    return f"log10 p = {fit.log10_p:.2f} (LR = {fit.lr:.2f})", ok


if __name__ == "__main__":
    sys.exit(common.run_statement(CLAIM, EXPECTED, check))
