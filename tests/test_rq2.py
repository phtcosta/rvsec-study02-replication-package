"""RQ2 helpers: repetitions are averaged per app before averaging over apps."""

import pandas as pd

from scripts.rq2 import mean_coverage


def test_mean_coverage_averages_reps_then_apps():
    # app a has 3 reps (mean 10), app b has 1 rep (20): mean of app means = 15, not 12.5.
    runs = pd.DataFrame({
        "apk": ["a", "a", "a", "b"], "tool": ["monkey"] * 4, "timeout": [60] * 4,
        "rep": [1, 2, 3, 1], "cov_method": [0.0, 10.0, 20.0, 20.0],
        "cov_mop": [0.0] * 4, "cov_directly_reaches_mop": [0.0] * 4,
    })
    assert mean_coverage(runs).loc["monkey", 60] == 15.0
