"""Statement discussion_001 -- Discussion, Threats to Validity, Internal Validity.

Article sentence:
    "In a sensitivity analysis that does exclude the all-zero runs, the two budget
    terms and the Ape contrast keep their direction and remain significant at the
    0.05 level (uncorrected), whereas the deficits of Qtesting and Ares,
    significant only before the Holm correction in the primary model, are no
    longer significant."

Pass criterion (fixed before coding): refit the RQ1 NB2 (scripts.rq1.fit_rq1)
without the all-zero runs (scripts.rq1.all_zero); for timeout 180, timeout 300
and Ape the coefficient sign equals the primary fit's and p < 0.05; for Qtesting
and Ares p >= 0.05 (cluster-robust Wald p, uncorrected). In the primary fit,
Qtesting and Ares have a negative coefficient, p < 0.05, and a Holm-adjusted p
(over the ten tool contrasts, as in scripts.rq1) >= 0.05.
"""

from __future__ import annotations

import sys

import numpy as np

from scripts import common
from scripts.rq1 import TOOL_TERM, all_zero, fit_rq1

CLAIM = ("Without the all-zero runs: budget and Ape keep sign and p < 0.05; Qtesting, Ares "
         "p >= 0.05, having been significant only before Holm in the primary model")
EXPECTED = ("timeout 180, timeout 300, Ape: same sign as primary, p < 0.05; "
            "Qtesting, Ares: primary coef < 0, p < 0.05, Holm p >= 0.05; refit p >= 0.05")
ALPHA = 0.05
KEEP = {"timeout 180": "C(timeout)[T.180]", "timeout 300": "C(timeout)[T.300]",
        "Ape": f"{TOOL_TERM}[T.ape]"}
LOSE = {"Qtesting": f"{TOOL_TERM}[T.qtesting]", "Ares": f"{TOOL_TERM}[T.ares]"}
PAD = "\n" + " " * 10


def fmt_p(p: float) -> str:
    """4 places, or exponent form below 1e-4."""
    return f"{p:.4f}" if p >= 1e-4 else f"{p:.1e}"


def check() -> tuple[str, bool]:
    runs = common.run_table()
    zero = all_zero(runs)
    primary = fit_rq1(runs).nb
    sens = fit_rq1(runs[~zero].reset_index(drop=True)).nb
    tools = [t for t in primary.params.index if t.startswith(TOOL_TERM)]
    holm = common.holm(primary.pvalues[tools])
    lines = [f"{int(zero.sum())} all-zero runs removed, {int((~zero).sum())} kept",
             f"{'term':<12} {'primary coef':>12} {'p':>8} {'Holm p':>8} {'refit coef':>12} "
             f"{'p':>8}  verdict"]
    ok = True
    for label, term in (KEEP | LOSE).items():
        b0, p0 = primary.params[term], primary.pvalues[term]
        b1, p1 = sens.params[term], sens.pvalues[term]
        h0 = holm.get(term, np.nan)
        if label in KEEP:
            good = np.sign(b1) == np.sign(b0) and p1 < ALPHA
        else:
            good = b0 < 0 and p0 < ALPHA and h0 >= ALPHA and p1 >= ALPHA
        ok &= bool(good)
        holm_txt = fmt_p(h0) if term in holm.index else "-"
        lines.append(f"{label:<12} {b0:>+12.4f} {fmt_p(p0):>8} {holm_txt:>8} {b1:>+12.4f} "
                     f"{fmt_p(p1):>8}  " + ("ok" if good else "VIOLATED"))
    return PAD.join(lines), ok


if __name__ == "__main__":
    sys.exit(common.run_statement(CLAIM, EXPECTED, check))
