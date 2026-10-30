"""Statement results_rq2_001 -- Results, RQ2, GLM paragraph.

Article sentence:
    "The estimated dispersion (alpha = \\glmCovRawAlpha, 95% CI
    [\\glmCovRawAlphaLo, \\glmCovRawAlphaHi]) and a likelihood-ratio test against
    a Poisson model (p < 10^-300) support the negative binomial choice."

Pass criterion (fixed before coding): in the RQ2 NB2 fit (scripts.rq2.fit_rq2 on
the run table), log10 p of the boundary-corrected LR test, p = 0.5 * chi2_1.sf(LR)
computed by common.lr_log10_p, is finite and < -300.
"""

from __future__ import annotations

import math
import sys

from scripts import common
from scripts.rq2 import fit_rq2

CLAIM = "RQ2: LR test favors NB2 over Poisson"
EXPECTED = "p < 10^-300"
LOG10_BOUND = -300


def check() -> tuple[str, bool]:
    fit = fit_rq2(common.run_table())
    ok = math.isfinite(fit.log10_p) and fit.log10_p < LOG10_BOUND
    return f"log10 p = {fit.log10_p:.2f} (LR = {fit.lr:.2f})", ok


if __name__ == "__main__":
    sys.exit(common.run_statement(CLAIM, EXPECTED, check))
