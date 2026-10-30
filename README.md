# On the Effectiveness of Integrating Android Test-Case Generation with Runtime Verification for Detecting Cryptographic API Misuses — replication package

This package checks the article's quantitative claims against the data of campaign
`estudo02-20260916`. The campaign ran 11 test-generation tools on 163 F-Droid apps, with three
budgets (60, 180, 300 s) and three repetitions each: 16,137 runs in image
`phtcosta/rvandroid:0.9.4` (rvsec `fc51ab64`), monitored by 47 `jca_android` specifications. The
package holds only the spreadsheets the published numbers need, the scripts that compute those
numbers, and the expected values. It recomputes 182 macros, 5 tables, the numbers of 2 figures,
and 8 statements that have no macro. It compares each with the article's printed value. 8 more
macros are checked by inspection (see below). A few statements that come from the data but print
no number are not checked by script; they are listed below with where to check them. The spreadsheets are copies of the
campaign's outputs and pinned inputs, not regenerated (see [Data origin](#data-origin)).

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python 3.12 (uv installs it if missing)
- The article's library pins, fixed in `pyproject.toml` and `uv.lock`: pandas 2.3.3,
  numpy 1.26.4, scipy 1.17.1, statsmodels 0.14.6. The GLM values depend on these versions.

## How to run

```bash
uv sync --frozen   # create the environment from uv.lock
make restore       # unzip every data file and verify every sha256
make check         # compute every claim and compare; exit 1 on any FAIL
make test          # unit tests
```

Other targets: `make verify` (re-check the sha256 of the restored files), `make run` (compute
into `out/` without comparing), `make clean` (remove `out/` and the restored files).

## Layout

```
README.md                 this file
LICENSE                   MIT (code)
LICENSE-DATA              CC BY 4.0 (data, expected values)
LICENSE-CRYSL-RULES       EPL-2.0 (the copied CrySL rules)
pyproject.toml  uv.lock  .python-version
Makefile                  restore · verify · run · check · test · clean
data/
  README.md               data dictionary: one table per file, column meanings, traps
  SHA256SUMS              sha256 of every zip and every uncompressed file
  campaign/  corpus/  instrument/  baselines/{cognicrypt,unit-tests}/    *.zip + *.sha256
claims/
  claims.csv              one row per macro: id, section, macro, expected, format,
                          method (script | inspection), producer, evidence
  tables/*.csv            expected cells of the 5 tables
  figures/*.csv           expected numbers of the selection funnel and the Venn diagram
scripts/
  common.py               paths, loaders, formatters, the app-code rule, the misuse key
  funnel.py  rq1.py  rq2.py  rq3.py  cognicrypt.py  venn.py  unit_tests.py
  statements/             one script per statement without a macro
  restore.py              unzip and sha256 check
  check.py                runs every producer and statement script; prints PASS/FAIL
tests/                    unit tests: formatters, loaders, models, producers
out/                      generated, not tracked: values, tables, figures, report.txt
```

## Report format

`make check` prints two blocks and writes the same text to `out/report.txt`.

- **Macros:** one line per claim, grouped by article section, for example
  `PASS  rq1  rawUnique  453`. Table cells and figure numbers are compared the same way.
- **Statements:** one line per statement script. Each script prints
  `Claim / Computed / Expected / Status` and exits 0 (PASS), 1 (FAIL) or 2 (SKIP).

Then a summary line:
`macros 182 passed, 0 failed; tables 5 passed, 0 failed; figures 2 passed, 0 failed; statements 8
passed, 0 failed, 0 skipped; 8 by inspection, see README`.

Values are compared as the formatted strings the article prints (integers, number words,
decimals, percentages, p-values). There is no tolerance parameter.

## Claims

<!-- CLAIMS TABLE: generated from claims/claims.csv by scripts/check.py -->

| Section | Macro | Printed value | Checked by |
|---|---|---|---|
| abstract | `\finalDataset` | `163` | `scripts/funnel.py` |
| dataset | `\fdroidIndexDate` | `22~June 2026` | inspection |
| dataset | `\totalAppsFdroid` | `3{,}941` | `scripts/funnel.py` |
| dataset | `\emulatorCompatExcl` | `388` | `scripts/funnel.py` |
| dataset | `\abiExcl` | `304` | `scripts/funnel.py` |
| dataset | `\minSdkExcl` | `84` | `scripts/funnel.py` |
| dataset | `\emulatorCompatApps` | `3{,}553` | `scripts/funnel.py` |
| dataset | `\githubExcl` | `1{,}949` | `scripts/funnel.py` |
| dataset | `\staleCommitExcl` | `1{,}238` | `scripts/funnel.py` |
| dataset | `\notGithubExcl` | `685` | `scripts/funnel.py` |
| dataset | `\repoUnresolvableExcl` | `26` | `scripts/funnel.py` |
| dataset | `\githubApps` | `1{,}604` | `scripts/funnel.py` |
| dataset | `\playstoreExcl` | `874` | `scripts/funnel.py` |
| dataset | `\playstoreApps` | `730` | `scripts/funnel.py` |
| dataset | `\builtApps` | `348` | `scripts/funnel.py` |
| dataset | `\buildFailedExcl` | `376` | `scripts/funnel.py` |
| dataset | `\buildOutOfScopeExclWord` | `six` | `scripts/funnel.py` |
| dataset | `\dedupExcl` | `13` | `scripts/funnel.py` |
| dataset | `\dedupApps` | `335` | `scripts/funnel.py` |
| reachability | `\gtAuto` | `196` | `scripts/funnel.py` |
| reachability | `\gtAutoSingleWord` | `seven` | `scripts/funnel.py` |
| reachability | `\gtManual` | `145` | `scripts/funnel.py` |
| reachability | `\mneutScopeExcl` | `70` | `scripts/funnel.py` |
| reachability | `\mneutCollapseExcl` | `32` | `scripts/funnel.py` |
| reachability | `\mneutCovExcl` | `36` | `scripts/funnel.py` |
| reachability | `\mneutForeignExclWord` | `two` | `scripts/funnel.py` |
| reachability | `\mneutScopeApps` | `265` | `scripts/funnel.py` |
| reachability | `\saNoJsonExclWord` | `two` | `scripts/funnel.py` |
| reachability | `\saBudgetMin` | `90` | `scripts/funnel.py` |
| reachability | `\saDecidedApps` | `263` | `scripts/funnel.py` |
| reachability | `\reachesMopApps` | `173` | `scripts/funnel.py` |
| reachability | `\reachesMopPct` | `65.8` | `scripts/funnel.py` |
| reachability | `\noMopExcl` | `90` | `scripts/funnel.py` |
| instrumentation | `\smokeInstallExclWord` | `one` | `scripts/funnel.py` |
| instrumentation | `\smokeCrashExclWord` | `two` | `scripts/funnel.py` |
| instrumentation | `\instrumentationPool` | `170` | `scripts/funnel.py` |
| instrumentation | `\instrumented` | `164` | `scripts/funnel.py` |
| instrumentation | `\instrumentationSuccessPct` | `96.5` | `scripts/funnel.py` |
| instrumentation | `\notInstrumentedWord` | `six` | `scripts/funnel.py` |
| instrumentation | `\weaverBlindExclWord` | `one` | `scripts/funnel.py` |
| abstract | `\rawUnique` | `453` | `scripts/rq1.py` |
| abstract | `\rawApps` | `89` | `scripts/rq1.py` |
| execution | `\toolCountWord` | `eleven` | `scripts/rq1.py` |
| execution | `\campaignContainers` | `12` | inspection |
| execution | `\containerCpus` | `4` | inspection |
| execution | `\containerMemGb` | `10` | inspection |
| execution | `\tasksGrid` | `16{,}137` | `scripts/rq1.py` |
| results-rq1 | `\rawUniqueGainMin` | `17.7` | `scripts/rq1.py` |
| results-rq1 | `\rawUniqueGainMax` | `47.1` | `scripts/rq1.py` |
| results-rq1 | `\rawEveryTool` | `214` | `scripts/rq1.py` |
| results-rq1 | `\rawAvgUniqueMisusesMin` | `1.44` | `scripts/rq1.py` |
| results-rq1 | `\rawAvgUniqueMisusesMax` | `2.16` | `scripts/rq1.py` |
| results-rq1 | `\rawStartupMisuses` | `110` | `scripts/rq1.py` |
| results-rq1 | `\rawStartupMisusesLib` | `95` | `scripts/rq1.py` |
| results-rq1 | `\rawStartupFirstMin` | `20` | `scripts/rq1.py` |
| results-rq1 | `\rawStartupFirstMax` | `35` | `scripts/rq1.py` |
| results-rq1 | `\rawMonkeySixtyMisuses` | `271` | `scripts/rq1.py` |
| results-rq1 | `\rawEventsGainMin` | `27.9` | `scripts/rq1.py` |
| results-rq1 | `\rawEventsGainMinSixty` | `390` | `scripts/rq1.py` |
| results-rq1 | `\rawEventsGainMinThreeHundred` | `499` | `scripts/rq1.py` |
| results-rq1 | `\rawEventsGainMax` | `617.3` | `scripts/rq1.py` |
| results-rq1 | `\rawAvgEventsQtestingThreeHundred` | `33.49` | `scripts/rq1.py` |
| results-rq1 | `\rawEventsGainQtesting` | `617.3` | `scripts/rq1.py` |
| results-rq1 | `\rawUniqueGainQtesting` | `18.2` | `scripts/rq1.py` |
| results-rq1 | `\glmRawVarMean` | `7.12` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrTimeoutOneEighty` | `1.2138` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrTimeoutOneEightyLo` | `1.1080` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrTimeoutOneEightyHi` | `1.3297` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrTimeoutThreeHundred` | `1.2882` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrTimeoutThreeHundredLo` | `1.1477` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrTimeoutThreeHundredHi` | `1.4459` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrApe` | `1.0892` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrApeLo` | `1.0387` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrApeHi` | `1.1422` | `scripts/rq1.py` |
| results-rq1 | `\glmRawHolmApe` | `0.0042` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrSize` | `1.1339` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrSizeLo` | `0.9808` | `scripts/rq1.py` |
| results-rq1 | `\glmRawIrrSizeHi` | `1.3109` | `scripts/rq1.py` |
| results-rq3 | `\rawSpecsWord` | `twenty-two` | `scripts/rq1.py` |
| discussion | `\allZeroRuns` | `176` | `scripts/rq1.py` |
| discussion | `\allZeroPct` | `1.1` | `scripts/rq1.py` |
| discussion | `\allZeroStructural` | `171` | `scripts/rq1.py` |
| discussion | `\qtestingNeverCoveredApps` | `19` | `scripts/rq1.py` |
| discussion | `\qtestingEffectiveApps` | `144` | `scripts/rq1.py` |
| discussion | `\inadmissibleRuns` | `484` | `scripts/rq1.py` |
| discussion | `\runsPerApp` | `99` | `scripts/rq1.py` |
| discussion | `\campaignContainersWord` | `twelve` | inspection |
| results-rq2 | `\covMethodApeThreeHundred` | `32.72` | `scripts/rq2.py` |
| results-rq2 | `\covMethodMonkeyThreeHundred` | `27.35` | `scripts/rq2.py` |
| results-rq2 | `\covMethodDroidmateThreeHundred` | `26.21` | `scripts/rq2.py` |
| results-rq2 | `\covMethodGlobal` | `21.18` | `scripts/rq2.py` |
| results-rq2 | `\covDirectApeThreeHundred` | `12.96` | `scripts/rq2.py` |
| results-rq2 | `\covGapRatioApeThreeHundred` | `2.5` | `scripts/rq2.py` |
| results-rq2 | `\covDirectGlobal` | `9.61` | `scripts/rq2.py` |
| results-rq2 | `\covGapRatioGlobal` | `2.2` | `scripts/rq2.py` |
| results-rq2 | `\covReachesMopGlobal` | `20.60` | `scripts/rq2.py` |
| results-rq2 | `\directCovNoSupport` | `82` | `scripts/rq2.py` |
| results-rq2 | `\directCovSupportApps` | `81` | `scripts/rq2.py` |
| results-rq2 | `\directCovSupportMean` | `19.34` | `scripts/rq2.py` |
| results-rq2 | `\covMethodSupportMean` | `17.10` | `scripts/rq2.py` |
| results-rq2 | `\directCovSupportMedian` | `1.41` | `scripts/rq2.py` |
| results-rq2 | `\covMethodSupportMedian` | `13.52` | `scripts/rq2.py` |
| results-rq2 | `\directCovBelowOverallApps` | `53` | `scripts/rq2.py` |
| results-rq2 | `\directCovNeverApps` | `33` | `scripts/rq2.py` |
| results-rq2 | `\glmCovRawAlpha` | `4.0999` | `scripts/rq2.py` |
| results-rq2 | `\glmCovRawAlphaLo` | `2.7509` | `scripts/rq2.py` |
| results-rq2 | `\glmCovRawAlphaHi` | `5.4488` | `scripts/rq2.py` |
| results-rq2 | `\glmCovRawIrr` | `1.0033` | `scripts/rq2.py` |
| results-rq2 | `\glmCovRawIrrLo` | `0.9847` | `scripts/rq2.py` |
| results-rq2 | `\glmCovRawIrrHi` | `1.0222` | `scripts/rq2.py` |
| results-rq2 | `\glmCovRawIrrP` | `0.7304` | `scripts/rq2.py` |
| instrumentation | `\jcaSpecCount` | `47` | `scripts/rq3.py` |
| results-rq3 | `\rawPatDefaultTrust` | `131` | `scripts/rq3.py` |
| results-rq3 | `\rawPatDefaultTrustOkhttp` | `106` | `scripts/rq3.py` |
| results-rq3 | `\rawPatMdFive` | `31` | `scripts/rq3.py` |
| results-rq3 | `\rawPatShaOne` | `26` | `scripts/rq3.py` |
| results-rq3 | `\ecbAesMisuses` | `16` | `scripts/rq3.py` |
| results-rq3 | `\rawPatOldProtocolWord` | `two` | `scripts/rq3.py` |
| results-rq3 | `\rawPatPbeIterationsWord` | `two` | `scripts/rq3.py` |
| results-rq3 | `\rawPatKeyStoreOrderWord` | `four` | `scripts/rq3.py` |
| results-rq3 | `\rawPatFixedValueWord` | `nine` | `scripts/rq3.py` |
| results-rq3 | `\rawPatTrustAllWord` | `four` | `scripts/rq3.py` |
| results-rq3 | `\rawAppCodePct` | `17.88` | `scripts/rq3.py` |
| results-rq3 | `\rawAppCodeCount` | `81` | `scripts/rq3.py` |
| results-rq3 | `\rawLibPct` | `82.12` | `scripts/rq3.py` |
| results-rq3 | `\rawAppCodeEventsPct` | `12.12` | `scripts/rq3.py` |
| results-rq3 | `\rawSpecTopAppCode` | `12` | `scripts/rq3.py` |
| results-rq3 | `\keyStoreAppCode` | `3` | `scripts/rq3.py` |
| results-rq3 | `\keyStoreTotal` | `4` | `scripts/rq3.py` |
| results-rq3 | `\keyStoreAppCodePct` | `75.00` | `scripts/rq3.py` |
| results-rq3 | `\rawPropagationTopApps` | `54` | `scripts/rq3.py` |
| results-rq3 | `\rawPropagationCombos` | `200` | `scripts/rq3.py` |
| results-rq3 | `\rawPropagationMultiApp` | `44` | `scripts/rq3.py` |
| results-rq3 | `\rawSpecTopMisuses` | `67` | `scripts/rq3.py` |
| discussion | `\rawLibTopNamespacesPct` | `75.3` | `scripts/rq3.py` |
| baselines | `\ccRulesLoaded` | `47` | inspection |
| baselines | `\ccRulesCopied` | `49` | `scripts/cognicrypt.py` |
| baselines | `\ccRulesRejectedWord` | `two` | inspection |
| baselines | `\ccHeapGb` | `40` | `scripts/cognicrypt.py` |
| baselines | `\ccTimeLimitHoursWord` | `one` | `scripts/cognicrypt.py` |
| baselines | `\ccRetryHeapGb` | `90` | `scripts/cognicrypt.py` |
| baselines | `\ccRetryHoursWord` | `two` | `scripts/cognicrypt.py` |
| baselines | `\ccNoVerdict` | `18` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccSuccess` | `145` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccErrorWord` | `twelve` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccTimeoutWord` | `six` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccEmptyReports` | `94` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccEmptyNoDirectReach` | `60` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccNonEmptyNoDirectReach` | `19` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccAppsWithFindings` | `51` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccFindings` | `1{,}353` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccMeanFindings` | `9.3` | `scripts/cognicrypt.py` |
| results-rq1 | `\ccRulesViolated` | `22` | `scripts/cognicrypt.py` |
| results-rq1 | `\vennTupCC` | `459` | `scripts/venn.py` |
| results-rq1 | `\vennTupBoth` | `83` | `scripts/venn.py` |
| results-rq1 | `\vennTupOnlyRV` | `370` | `scripts/venn.py` |
| results-rq1 | `\vennTupOnlyCC` | `376` | `scripts/venn.py` |
| results-rq1 | `\vennTupBothSslContext` | `30` | `scripts/venn.py` |
| results-rq1 | `\vennTupBothTmf` | `29` | `scripts/venn.py` |
| results-rq1 | `\vennTupOnlyRVNoVerdict` | `113` | `scripts/venn.py` |
| results-rq1 | `\vennTupSensOnlyRV` | `257` | `scripts/venn.py` |
| results-rq1 | `\vennTupOnlyRVNothing` | `276` | `scripts/venn.py` |
| results-rq1 | `\vennTupOnlyRVRejectedRuleWord` | `one` | `scripts/venn.py` |
| results-rq1 | `\vennTupOnlyRVClassAbsent` | `89` | `scripts/venn.py` |
| results-rq1 | `\vennTupOnlyRVClassReportedWord` | `four` | `scripts/venn.py` |
| results-rq1 | `\vennTupOnlyCCIncomplete` | `46` | `scripts/venn.py` |
| results-rq1 | `\vennTupOnlyCCAdmittedWord` | `eleven` | inspection |
| baselines | `\unitWithTests` | `102` | `scripts/unit_tests.py` |
| baselines | `\unitSuccess` | `94` | `scripts/unit_tests.py` |
| results-rq1 | `\unitWithTestsPct` | `62.6` | `scripts/unit_tests.py` |
| results-rq1 | `\unitWithoutTests` | `61` | `scripts/unit_tests.py` |
| results-rq1 | `\unitSuccessPct` | `92.2` | `scripts/unit_tests.py` |
| results-rq1 | `\unitFailWord` | `eight` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawEvents` | `343` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawMisuses` | `148` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawApps` | `30` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawOriginProduction` | `84` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawOriginLib` | `39` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawOriginTestCode` | `12` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawOriginRobolectric` | `13` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawRobolectricPct` | `8.8` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawOnlyAppsWord` | `six` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawOnlyAllRoboAppsWord` | `three` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawOnlyGenuineAppsWord` | `three` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawOnlyProductionAppsWord` | `one` | `scripts/unit_tests.py` |
| results-rq1 | `\unitRawKeyMatch` | `43` | `scripts/unit_tests.py` |
| results-rq1 | `\noUnitRvRawApps` | `30` | `scripts/unit_tests.py` |
| results-rq1 | `\rvRawAppCodeMisuses` | `53` | `scripts/unit_tests.py` |
| results-rq1 | `\bidirRawAppCodeMisuses` | `31` | `scripts/unit_tests.py` |
| results-rq1 | `\bidirRawAppCodeApps` | `13` | `scripts/unit_tests.py` |

<!-- END CLAIMS TABLE -->

## Checked by inspection

These 8 macros come from a configuration file, a tool's log or a snapshot record, not from a
spreadsheet column. The file is in the package. No script reads the value. Find it as shown.

| Macro | Printed value | Where to find it |
|---|---|---|
| `campaignContainers` | 12 | `data/campaign/docker-compose.estudo02-20260916.yml`: the services that merge the `x-rvandroid` base, `container_name` `estudo02-20260916_00` to `_11`. The 13th `container_name`, `rv-humanoid`, is the Humanoid model server |
| `campaignContainersWord` | twelve | same as `campaignContainers` |
| `containerCpus` | 4 | same file: `deploy.resources.limits.cpus: "4"` of the `x-rvandroid` base, inherited by each campaign service |
| `containerMemGb` | 10 | same file: `deploy.resources.limits.memory: "10g"` of the `x-rvandroid` base |
| `ccRulesLoaded` | 47 | `data/baselines/cognicrypt/cognicrypt_summary.csv`, column `error_message` (CogniCrypt stderr): "Found 47 rules" |
| `ccRulesRejectedWord` | two | same column: the distinct rules in "Skipping rule since it contains errors: …/X.crysl", `SSLEngine` and `OAEPParameterSpec` |
| `fdroidIndexDate` | 22 June 2026 | `data/corpus/fdroid_index_snapshot.json`, field `fetched_at_utc` (`2026-06-22T16:28:23.441124+00:00`) |
| `vennTupOnlyCCAdmittedWord` | eleven | `data/baselines/cognicrypt/findings.csv`: the only-CogniCrypt tuples of the Venn diagram, other than the incomplete-only ones (`vennTupOnlyCCIncomplete`), **every** finding of which is a `ConstraintError` whose value in `Message` (`with value "…"`) is a literal of the `Arrays.asList(...)` allow-lists in the matching specification of `data/instrument/specs.zip` (8 `AndroidKeyStore` for `KeyStore`, 3 `TLS` for `SSLContext`). Counting tuples with *any* such finding gives a different number |

## Statements without a macro

The article states these 8 facts in plain text, with no macro. One script in
`scripts/statements/` checks each. The pass criteria were fixed before any script ran and were
not tuned afterwards. Each script prints the exact computed value.

| # | Script | Statement (section) | Pass criterion |
|---|---|---|---|
| 1 | `results_rq1_001.py` | likelihood-ratio test of the negative binomial against the Poisson model, "p < 10^-300" (RQ1, GLM paragraph) | in the RQ1 NB2 fit, log10 p is finite and < −300, with p = 0.5·χ²₁.sf(LR) (boundary correction), computed as log10 p = [ln 0.5 + ln 2 + `scipy.special.log_ndtr(−√LR)`] / ln 10. `chi2.logsf` underflows to −inf here and is not used |
| 2 | `results_rq2_001.py` | the same test in the RQ2 model (RQ2, GLM paragraph) | same criterion, RQ2 fit |
| 3 | `results_rq1_002.py` | "Excluding Robolectric artifacts, approximately one-third of the unit-test misuses were also detected by the test-generation tools" (RQ1, Baseline 1) | of {1/4, 1/3, 1/2}, the one nearest to the computed share is 1/3 |
| 4 | `results_rq1_003.py` | "All overlapping misuses originate from production code or third-party libraries" (RQ1, Baseline 1) | no overlapping misuse has origin test code or Robolectric |
| 5 | `results_rq2_002.py` | "even the best-performing configuration exercises only about one third of the application methods" (RQ2) | the highest mean method coverage over all (tool, timeout) pairs has 1/3 as its nearest of {1/4, 1/3, 1/2} |
| 6 | `results_rq2_003.py` | "For every tool, coverage increases with the execution budget" (RQ2) | for each of the 11 tools, mean method coverage at 60 s < 180 s < 300 s |
| 7 | `discussion_001.py` | sensitivity without the all-zero runs: both budget terms and the Ape contrast keep their direction and stay significant at 0.05 (uncorrected); the Qtesting and Ares deficits, significant only before the Holm correction in the primary model, are no longer significant (Threats to Validity) | refit the RQ1 NB2 without the all-zero runs; signs equal to the primary fit and p < 0.05 for timeout 180, timeout 300 and Ape; p ≥ 0.05 for Qtesting and Ares. In the primary fit, Qtesting and Ares have a negative coefficient, p < 0.05, and a Holm-adjusted p (over the ten tool contrasts) ≥ 0.05 |
| 8 | `results_rq1_004.py` | mOTP: runtime verification detects `HmacSHA1` (`MAC-ALG-00`) and `RAW` (`SECRETKEYSPEC-ALG-00`); CogniCrypt reports neither in this class (RQ1, Baseline 2) | both codes are present in `raw-accusations.csv` for `org.cry.otp_31.apk`, class `org.cry.otp.TOTP`; in `primary-accusations.csv` their rows carry only `val='HmacSHA1'` and `val='RAW'`; and no CogniCrypt finding for that app and class maps to either |

## Statements from the data not checked by script

These statements follow from the package's data but print no number of their own, and no script
compares them. The numbers next to them are checked. Each can be read off as shown.

| Statement (section) | Where to check it |
|---|---|
| unique-misuse gains from 60 to 300 s range from Fastbot (lowest) to DroidBot bfs_greedy (highest); violation-event gains from DroidBot dfs_naive (lowest) to Qtesting (highest) (RQ1) | gain column of the checked tables `jca-violations-unique` and `jca-violations` |
| at 300 s, Qtesting, Ape and DroidMate report the highest totals of violation events, DroidBot dfs_naive, DroidBot bfs_naive and Monkey the lowest (RQ1) | 300 s column of the checked table `jca-violations` |
| Qtesting reports the lowest average number of unique misuses at 300 s, Ape the highest (RQ1) | the tools that attain the checked `rawAvgUniqueMisusesMin` and `rawAvgUniqueMisusesMax` in `scripts/rq1.py` (per-tool mean over apps of the per-app mean of `mop_unique4`, 300 s) |
| Ape detects the most unique misuses at every budget (RQ1 and Discussion) | the 60, 180 and 300 s columns of the checked table `jca-violations-unique` |
| apart from Ape, no tool differs significantly from Monkey after the Holm correction (RQ1) | the Holm-adjusted p of the ten tool contrasts of the RQ1 model (`fit_rq1` and `common.holm` in `scripts/rq1.py`): only Ape is below 0.05 |
| the test-code misuses come from two `photok` test classes, `CryptoEnginesTest` and `CryptoMigrationV2CompatibilityTest` (RQ1, Baseline 1) | `data/baselines/unit-tests/categoria_unit_tests.csv`: column `class` of the rows with `categoria` `test_code` |
| of the apps flagged only by unit tests and not only by Robolectric artifacts, `plugbrain` and `keepalive` have library misuses and `securecamera` production-code misuses (RQ1, Baseline 1) | `categoria_unit_tests.csv` (origin) for the unit-only apps that `scripts/unit_tests.py` counts |
| the only-RV Venn tuple with a rejected CrySL rule involves `SSLEngineSpec` (RQ1, Baseline 2) | the only-RV tuples of `scripts/venn.py` whose rule is among the rejected ones in `cognicrypt_summary.csv`, column `error_message` |
| Ape has the highest method coverage at every budget, followed at 300 s by Monkey and DroidMate (RQ2) | the checked table `coverage` |
| direct JCA coverage is below method coverage for every tool and budget (RQ2) | the checked tables `coverage_mop` and `coverage`, cell by cell |
| `TrustManagerFactory` and `SSLContext` lead with the most unique misuses, tied; `Cipher` and `MessageDigest` have the most application-code misuses, tied (RQ3) | the `Total` and `App-code` columns of the checked table `top-jca-violations` (`rawSpecTopMisuses`, `rawSpecTopAppCode`) |
| the default-trust pattern is the most frequent; the old-protocol, PBE-iteration and KeyStore-order patterns are less frequent (RQ3) | ordering of the checked pattern counts (`rawPat*` macros) |
| the old-protocol misuses use `SSL` or `TLSv1` (RQ3) | `data/campaign/primary-accusations.csv`: value `val='…'` in `message` of the rows whose `code` contains `-PROTO-` |
| the most widespread library misuse is the `TrustManagerFactory` report in `platformTrustManager` of okhttp's `Platform` class; the `SSLContext` report in `newSslSocketFactory` of the same class is second (RQ3) | `data/campaign/raw-accusations.csv`: distinct `apk` per (`spec`, `class`, `method`), ranked |
| the three largest library namespaces are Google Tink, OkHttp and Ktor (Discussion) | the namespace ranking behind `rawLibTopNamespacesPct` in `scripts/rq3.py` (class cut to three package segments) |
| the all-zero runs of category `estrutural` are the Qtesting runs on the apps it never launches; the others are runs the tool stopped or that are inadmissible (Discussion) | `data/campaign/per_task.csv`: `tool` and `category` of the all-zero runs (`all_zero` in `scripts/rq1.py`) |
| of the two applications without a static-analysis verdict, one exhausted the time budget and the other failed (Reachability) | `data/corpus/dataset.csv`: `excluded_reason` of the `filtered_sa_no_json` rows (`sa_no_json:failed_timeout_no_json`, `sa_no_json:failed_no_json`) |
| the excluded instrumented application falls under the `com.google` package prefix (Instrumentation) | `data/corpus/dataset.csv`: `apk` and `excluded_reason` (`weaver_pkgfilter_zero`) of the `filtered_zero_coverage` row |
| every application of the analysis set passed the post-instrumentation validation (Instrumentation) | `data/corpus/dataset.csv`: `validation_status` is `ok` on the 163 `selected` rows |
| the builds outside the harness's scope need native toolchains or Flutter (Dataset) | `data/corpus/dataset.csv`: `excluded_reason` `out_of_scope:native_toolchain` and `out_of_scope:flutter` |

## Visible in the data, not recomputed

The design parameters stated in prose appear in the package's files. No script recomputes them:

- the 60/180/300 s budgets and the 3 repetitions: columns `timeout` and `rep` of
  `data/campaign/per_task.csv`, and `RV_TIMEOUTS`, `RV_REPETITIONS` in the `.yml`;
- the minSdk 30 cut: column `min_sdk` and the reason `minsdk>30` in `excluded_reason` of
  `data/corpus/dataset.csv`;
- the 90 % threshold of the scope gate: column `cov_G` of `data/corpus/mneut_348.csv` (kept apps
  have `cov_G` ≥ 0.90).

## Not verifiable from the package's data

Some statements in the article have no spreadsheet behind them in this package:

- **Instrumentation failures.** The number of extra method references (between 1 and 17) that
  pushed five apps over the DEX method-reference limit, and the unimplemented
  `invoke-polymorphic/range` instruction that stopped the sixth. These need the instrumenter's
  logs.
- **The mOTP code listing** and its line numbers (RQ1, Baseline 2). These need the app's source
  code. The violations themselves are checked by statement 8.
- **Tool versions and Docker image digests** (Execution; also Soot 4.7.1 in Reachability, and
  CogniCrypt 5.0.1 with the CrySL rule commit `6d844ab` in Baselines). These are not data; the
  image digests are under [Data origin](#data-origin).
- **Choices stated in prose only:** Android API level 30 of the emulator, and α = 0.05.
- **Human judgement copied as data:** the ground-truth adjudication of each app's own code, and
  the origin categories of the unit-test misuses. The package counts them but cannot re-derive
  the judgement.

## Data

The data dictionary, with the columns the published numbers use and the reading traps, is in
[`data/README.md`](data/README.md).

## Data origin

Every file under `data/` is a byte-for-byte copy of an output or a pinned input of campaign
`estudo02-20260916`. Nothing is re-instrumented, re-consolidated, filtered or trimmed; the only
change is the anonymization of three files, below. The campaign ran in the image chain below. The
images hold the tools, the specifications and their source code at the commits that ran. Pull by
digest, not by tag (`ares` and `qtesting` are built outside the `0.9.4` chain; their tag only
names them).

| Image | Tag | Digest |
|---|---|---|
| `phtcosta/rvsec_base` | `0.9.4` | `sha256:a1d4801eb5bc912386ccefa819bbda8a8d9edb195a1f3bcbff9cf2b5c90e3774` |
| `phtcosta/rvsec_android` | `0.9.4` | `sha256:3bb293bc94d73baf8beba3fbdccaf881a2281d1122ad27dd31ad1d4a8c8c5325` |
| `phtcosta/rvandroid_tools` | `0.9.4` | `sha256:47a352463b7cd3c710fe17385ee067d83c79d3ef91b9632adddd883f7d177259` |
| `phtcosta/rvandroid` | `0.9.4` | `sha256:130f127b5b4c4d88f6d700b57d20ced0ea171a47f622277d1afa7d2b99cfbce1` |
| `phtcosta/humanoid` | `1.0` | `sha256:a902ff848b7cd22b06bcf56955c543ce63a7f873153c051c96b431c421d1f38a` |
| `phtcosta/ares` | `20260813` | `sha256:d4879cfaf0755f44e07f753fc6eb5d6f0b9d88f8dfe64c7b90789568c086a767` |
| `phtcosta/qtesting` | `20260813` | `sha256:e654c2e2defe1d9a761def94cdb6f19d0683d6c80c7d3295dedbd9da07477459` |

### Anonymization

Three files contained absolute paths of the machine that produced them. A fixed, ordered list
of path-prefix substitutions replaces each such prefix with the token `<WORKSPACE>/` or
`<HOST>/`. Nothing else changes, and no claim depends on the substituted text: "Found 47 rules"
is still in the same 13 rows, and the rejected rule names are still extracted.

| File | Field changed | sha256 original | sha256 published |
|---|---|---|---|
| `corpus/dataset.csv` | `build_status`, `orig_install_err` | `b457bed91eacf4d02af1772ba4d571fb6a7375ce106f084307e43a38fbfc08a0` | `2de4b8ec2352831887d8dc00680d74aaa0c64fec4baf4ad321648fc131b738b6` |
| `baselines/cognicrypt/cognicrypt_summary.csv` | `error_message` | `4ac1c4bfd9e21617307e5f14cf81d64abdafb8e04e334ca42a4a54b73522ec25` | `eb062505a0d1e85df31954e9c97d6c4e1f1cc6e1c8c26e53f124f58ae7c751d2` |
| `campaign/docker-compose.estudo02-20260916.yml` | volume mount lines | `0dfb8a1f1afa449ac43f96d7f762b42801dfd3e6b6bed858888f9bfdfcbc0db9` | `57d36f60efa3bc0bda52c034c5c31c4eabcf8396db643cb99445917965c90dad` |

Third-party content is left as published upstream: a macOS user path inside a third-party
project's build error in `dataset.csv` (`excluded_reason`, `probe_build_class`), and the
`repo_url` values of third-party developers.

### Expected values

The expected values in `claims/` were read once from the article's sources at article commit
`7910ebcc76b1756ece004bc34fd697489a5d8555`. The article's repository is private; nothing in
this package reads it at run time.

## License

- Code (`scripts/`, `tests/`, `Makefile`, `pyproject.toml`): MIT License, see
  [`LICENSE`](LICENSE).
- Data (`data/`) and expected values (`claims/`): Creative Commons Attribution 4.0
  International (CC BY 4.0), see [`LICENSE-DATA`](LICENSE-DATA).
- Exception: the 49 CrySL rules in `data/baselines/cognicrypt/crysl-rules.zip` are an unmodified
  copy of the `JavaCryptographicArchitecture` rule set of `CROSSINGTUD/Crypto-API-Rules`, commit
  `6d844ab`, under the Eclipse Public License 2.0, see [`LICENSE-CRYSL-RULES`](LICENSE-CRYSL-RULES).

## Citation

If you use this package, please cite the article *On the Effectiveness of Integrating Android
Test-Case Generation with Runtime Verification for Detecting Cryptographic API Misuses*.
