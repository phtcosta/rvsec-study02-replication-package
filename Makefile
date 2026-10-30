# Replication package for campaign estudo02-20260916.
#   make restore   unzip every data file and verify every sha256
#   make verify    verify the sha256 of the restored files only
#   make run       compute every claim into out/
#   make check     compare every claim with claims/; exit 1 on any FAIL
#   make test      unit tests (formatters, loaders, models, producers)
#   make clean     remove out/ and the restored data files

PY := uv run --frozen python

.PHONY: restore verify run check test clean

restore:
	$(PY) -m scripts.restore

verify:
	$(PY) -m scripts.restore --verify-only

run:
	$(PY) -m scripts.check --no-compare

check:
	$(PY) -m scripts.check

test:
	uv run --frozen pytest -q

clean:
	rm -rf out
	$(PY) -m scripts.restore --clean
