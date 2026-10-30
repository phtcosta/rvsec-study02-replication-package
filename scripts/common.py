"""Shared paths, loaders, formatters and the claim registry.

Every section script (funnel, rq1, rq2, rq3, cognicrypt, venn, unit_tests) and
every statement script imports from here. Nothing else in the package reads a
data file or formats a number.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CLAIMS = ROOT / "claims"
OUT = ROOT / "out"

# ---------------------------------------------------------------------------
# Data files (restored by `make restore`). Names are exactly as upstream.
# ---------------------------------------------------------------------------

FILES = {
    "per_task": "campaign/per_task.csv",
    "direct_coverage": "campaign/direct-coverage.csv",
    "raw_accusations": "campaign/raw-accusations.csv",
    "primary_accusations": "campaign/primary-accusations.csv",
    "severe_sites": "campaign/severe-sites.csv",
    "dataset": "corpus/dataset.csv",
    "ground_truth": "corpus/ground_truth_sheet.csv",
    "mneut": "corpus/mneut_348.csv",
    "codes": "instrument/codes.csv",
    "cc_findings": "baselines/cognicrypt/findings.csv",
    "cc_outcomes": "baselines/cognicrypt/per-app-outcomes.csv",
    "cc_gaps": "baselines/cognicrypt/gaps_18.csv",
    "cc_summary": "baselines/cognicrypt/cognicrypt_summary.csv",
    "unit_status": "baselines/unit-tests/unittests_status.csv",
    "unit_errors": "baselines/unit-tests/exp02_jca_errors_unit_tests.csv",
    "unit_categories": "baselines/unit-tests/categoria_unit_tests.csv",
}

# Directories restored from specs.zip (47 .mop) and crysl-rules.zip (49 .crysl).
MOP_DIR = DATA / "instrument" / "specs"
CRYSL_DIR = DATA / "baselines" / "cognicrypt" / "crysl-rules"


def path(name: str) -> Path:
    """Absolute path of a restored data file; KeyError for an unknown name."""
    return DATA / FILES[name]


def load(name: str, **read_csv_kwargs) -> pd.DataFrame:
    """Read one restored CSV. Extra keyword arguments go to ``pd.read_csv``."""
    p = path(name)
    if not p.is_file():
        raise FileNotFoundError(f"{p.relative_to(ROOT)} is missing; run `make restore`")
    return pd.read_csv(p, **read_csv_kwargs)


def _listing(directory: Path, suffix: str) -> list[Path]:
    if not directory.is_dir():
        raise FileNotFoundError(f"{directory.relative_to(ROOT)} is missing; run `make restore`")
    return sorted(directory.glob(f"*{suffix}"))


def mop_files() -> list[Path]:
    """The .mop specifications restored from data/instrument/specs.zip."""
    return _listing(MOP_DIR, ".mop")


def crysl_files() -> list[Path]:
    """The CrySL rules restored from data/baselines/cognicrypt/crysl-rules.zip."""
    return _listing(CRYSL_DIR, ".crysl")


def crysl_spec_classes() -> set[str]:
    """The ``SPEC <class>`` of every restored CrySL rule."""
    return {line.split()[1] for p in crysl_files()
            for line in p.read_text(encoding="utf-8").splitlines() if line.startswith("SPEC ")}


# ---------------------------------------------------------------------------
# Domain rules shared by several sections
# ---------------------------------------------------------------------------

# A unique misuse is a distinct (apk, spec, class, method).
MISUSE_KEY = ["apk", "spec", "class", "method"]


def is_app_code(cls: str, mneut: str) -> bool:
    """A class is app code when it is the app's root package or lies under it."""
    return cls == mneut or cls.startswith(mneut + ".")


# A run is one (apk, tool, rep, timeout): 163 apps x 11 tools x 3 timeouts x 3 reps.
RUN_KEY = ["apk", "tool", "rep", "timeout"]


def run_table() -> pd.DataFrame:
    """per_task joined 1:1 with direct-coverage on the run key (16,137 runs).

    Both files must hold the same runs: a run missing from either side fails.
    """
    per_task, direct = load("per_task"), load("direct_coverage")
    runs = per_task.merge(direct, on=RUN_KEY, how="inner", validate="1:1")
    if not len(runs) == len(per_task) == len(direct):
        raise ValueError(f"run key mismatch: per_task {len(per_task)}, "
                         f"direct-coverage {len(direct)}, joined {len(runs)}")
    return runs


# ---------------------------------------------------------------------------
# Count models (RQ1, RQ2): discrete NB2, alpha by ML, cluster-robust SEs by app
# ---------------------------------------------------------------------------

class GlmFit(NamedTuple):
    nb: object          # statsmodels NegativeBinomial results (cluster-robust)
    poisson: object     # the Poisson fit with the same formula (start values, LR test)
    lr: float           # 2 * (llf_nb - llf_poisson)
    log10_p: float      # log10 of the boundary-corrected LR p-value


def lr_log10_p(lr: float) -> float:
    """log10 of p = 0.5 * chi2_1.sf(lr), the boundary-corrected LR test of NB vs Poisson.

    chi2_1.sf(x) = 2 * Phi(-sqrt(x)); log_ndtr keeps it finite where chi2.logsf
    underflows to -inf.
    """
    from scipy import special
    return float((np.log(0.5) + np.log(2.0) + special.log_ndtr(-np.sqrt(lr))) / np.log(10.0))


def fit_nb2(formula: str, data: pd.DataFrame) -> GlmFit:
    """The article's fit: Poisson start values plus alpha 0.5, BFGS, maxiter 500,
    cluster-robust covariance by apk."""
    import statsmodels.api as sm
    log = np.log  # noqa: F841 -- patsy resolves log() from this frame
    pois = sm.Poisson.from_formula(formula, data=data).fit(disp=0)
    start = np.append(np.asarray(pois.params), 0.5)
    nb = sm.NegativeBinomial.from_formula(formula, data=data).fit(
        start_params=start, method="bfgs", maxiter=500, disp=0,
        cov_type="cluster", cov_kwds={"groups": data["apk"]})
    lr = 2.0 * (nb.llf - pois.llf)
    return GlmFit(nb, pois, float(lr), lr_log10_p(lr))


def holm(pvalues: pd.Series) -> pd.Series:
    """Holm step-down adjusted p-values, same index, ties kept in input order."""
    p = pvalues.sort_values(kind="mergesort")
    out, running = {}, 0.0
    for i, (name, value) in enumerate(p.items()):
        running = max(running, min(1.0, (len(p) - i) * value))
        out[name] = running
    return pd.Series(out)[pvalues.index]


# ---------------------------------------------------------------------------
# Formatters: the article's macro house style, reproduced exactly.
# ---------------------------------------------------------------------------

_WORDS = (
    "zero", "one", "two", "three", "four", "five", "six",
    "seven", "eight", "nine", "ten", "eleven", "twelve",
)
_TEENS = ("thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
          "nineteen")
_TENS = ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")


def integer(value) -> str:
    r"""``16137`` -> ``16{,}137`` (LaTeX thousands separator; truncates like ``int``)."""
    return f"{int(value):,}".replace(",", "{,}")


def decimal(value, places: int = 2) -> str:
    """``13.2249`` -> ``13.22``: fixed places, rounded once by the format."""
    return f"{float(value):.{places}f}"


def word(value) -> str:
    """``8`` -> ``eight`` for 0--12; anything else falls back to :func:`integer`."""
    n = int(value)
    return _WORDS[n] if 0 <= n < len(_WORDS) else integer(n)


def word99(value) -> str:
    """``22`` -> ``twenty-two``: spelled up to 99, else :func:`integer`."""
    n = int(value)
    if n < 13:
        return word(n)
    if n < 20:
        return _TEENS[n - 13]
    if n < 100:
        tens, units = divmod(n, 10)
        return _TENS[tens - 2] + ("" if units == 0 else "-" + word(units))
    return integer(n)


def pvalue(p: float) -> str:
    r"""A p-value macro: ``\ensuremath{<}0.0001`` below 1e-4, else 4 places."""
    return r"\ensuremath{<}0.0001" if p < 0.0001 else decimal(p, 4)


# ---------------------------------------------------------------------------
# Claim registry
# ---------------------------------------------------------------------------

CLAIMS_CSV = CLAIMS / "claims.csv"
CLAIM_COLUMNS = ["id", "section", "macro", "expected", "format", "method", "producer",
                 "evidence"]
METHODS = ("script", "inspection")
PRODUCERS = ("funnel", "rq1", "rq2", "rq3", "cognicrypt", "venn", "unit_tests")
# The fixed set of checks besides the macros (PLAN §3, §4.4): a missing one is a FAIL.
TABLES = ("coverage", "coverage_mop", "jca-violations", "jca-violations-unique",
          "top-jca-violations")
FIGURES = ("selection-funnel", "venn-diagram")
STATEMENTS = ("discussion_001", "results_rq1_001", "results_rq1_002", "results_rq1_003",
              "results_rq1_004", "results_rq2_001", "results_rq2_002", "results_rq2_003")


def load_claims() -> pd.DataFrame:
    """The expected values, every column as a string, empty cells as ''."""
    df = pd.read_csv(CLAIMS_CSV, dtype=str, keep_default_na=False)
    if list(df.columns) != CLAIM_COLUMNS:
        raise ValueError(f"claims.csv columns {list(df.columns)} != {CLAIM_COLUMNS}")
    return df


def load_expected(kind: str, name: str) -> pd.DataFrame:
    """Expected cells of claims/tables/<name>.csv or claims/figures/<name>.csv, as strings."""
    if kind not in ("tables", "figures"):
        raise ValueError(f"kind must be 'tables' or 'figures', not {kind!r}")
    return pd.read_csv(CLAIMS / kind / f"{name}.csv", dtype=str, keep_default_na=False)


def expected(macro: str) -> str:
    """The expected string of one macro, for statement scripts that reuse it."""
    rows = load_claims().loc[lambda d: d["macro"] == macro, "expected"]
    if len(rows) != 1:
        raise KeyError(f"{macro}: {len(rows)} rows in claims.csv")
    return rows.iloc[0]


# ---------------------------------------------------------------------------
# Statement scripts (scripts/statements/*.py, ICST style)
# ---------------------------------------------------------------------------

def run_statement(claim: str, expected_text: str, check) -> int:
    """Print Claim / Computed / Expected / Status; return 0 PASS, 1 FAIL, 2 SKIP.

    ``check()`` returns (computed text, passed). A missing input file is a SKIP.
    """
    try:
        computed, ok = check()
        status = "PASS" if ok else "FAIL"
    except FileNotFoundError as exc:
        computed, status = f"input missing: {exc}", "SKIP"
    print("=" * 60)
    print(f"Claim:    {claim}")
    print(f"Computed: {computed}")
    print(f"Expected: {expected_text}")
    print(f"Status:   {status}")
    print("=" * 60)
    return {"PASS": 0, "FAIL": 1, "SKIP": 2}[status]
