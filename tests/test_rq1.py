"""RQ1 producer: the model function is pure and refits on a subset of runs."""

import numpy as np

from scripts import common, rq1


def test_fit_rq1_pure_and_refits_without_all_zero_runs():
    runs = common.run_table()
    before = runs.copy()
    full = rq1.fit_rq1(runs)
    assert runs.equals(before)
    assert np.isfinite(full.log10_p) and full.log10_p < -300
    kept = runs[~rq1.all_zero(runs)]
    sub = rq1.fit_rq1(kept)
    assert sub.nb.nobs == len(kept) < len(runs)
    assert list(sub.nb.params.index) == list(full.nb.params.index)
