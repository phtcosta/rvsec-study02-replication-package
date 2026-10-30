"""Model helpers: the LR log-p identity and the Holm step-down."""

import numpy as np
import pandas as pd
from scipy import stats

from scripts.common import holm, lr_log10_p


def test_lr_log10_p_matches_chi2_where_finite():
    for lr in (1.0, 10.0, 200.0):
        direct = np.log10(0.5 * stats.chi2.sf(lr, 1))
        assert abs(lr_log10_p(lr) - direct) < 1e-9


def test_lr_log10_p_finite_for_huge_lr():
    assert np.isfinite(lr_log10_p(36585.7)) and lr_log10_p(36585.7) < -300


def test_holm():
    p = pd.Series({"a": 0.01, "b": 0.04, "c": 0.03})
    assert holm(p).round(6).to_dict() == {"a": 0.03, "b": 0.06, "c": 0.06}
