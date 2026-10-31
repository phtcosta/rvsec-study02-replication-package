# Data dictionary

Every file under `data/` belongs to campaign `estudo02-20260916` (image `rvandroid:0.9.4`,
rvsec `fc51ab64`, 163 apps, 16,137 runs, 47 `jca_android` specifications) or is one of its pinned
inputs. Each file is committed as `<file>.zip` plus `<file>.sha256` (the sha256 of the uncompressed
file). The two rule sets are committed as `specs.zip` and `crysl-rules.zip`, each with a member
list (`specs.sha256`, `crysl-rules.sha256`). `data/SHA256SUMS` pins every zip and every
uncompressed file. `make restore` unzips and verifies them. The zips are deterministic (every
entry has the timestamp 1980-01-01 00:00:00, entries are sorted by name, deflate at level 9), so
rebuilding a zip from the same file gives the same bytes.

File names are the upstream names, unchanged. Row counts exclude the header and were counted with
a CSV parser, because some fields hold quoted newlines.

**Marks.** In the column tables, **used** means that a published number, table or figure reads the
column. **key** means that the column identifies the row or joins tables. A blank mark means that
the file carries the column but no claim reads it.

| Folder | Content |
|---|---|
| `campaign/` | outputs of the 16,137 runs and the campaign's compose file |
| `corpus/` | the selection funnel, the scope key, the ground truth, the F-Droid snapshot record |
| `instrument/` | the 47 specifications that ran and their code labels |
| `baselines/cognicrypt/` | the CogniCrypt 5.0.1 baseline and the 49 CrySL rules |
| `baselines/unit-tests/` | the developer unit-test baseline |

## `campaign/`

### `campaign/per_task.csv`

The consolidation that rv-android delivered for the campaign. One row per run. Key `(apk, tool,
timeout, rep)`. **16,137 rows**, 18 columns, CRLF line endings. Grid: 163 apps × 11 tools × 3
timeouts (60, 180, 300 s) × 3 repetitions, so 99 runs per app.

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id `<package>_<version_code>.apk` | key |
| `timeout` | budget of the run in seconds: 60, 180 or 300 | key |
| `rep` | repetition, 1 to 3 | key |
| `tool` | tool label: `monkey`, `ape`, `ares`, `droidmate`, `fastbot`, `humanoid`, `qtesting`, `droidbot:bfs_greedy`, `droidbot:bfs_naive`, `droidbot:dfs_greedy`, `droidbot:dfs_naive` | key |
| `cov_method` | method coverage of the app's scope, percentage points (0–100) | used |
| `cov_act` | activity coverage, percentage points (0–100) | used |
| `cov_mop` | coverage of the methods that **transitively** reach a monitored API (`cov_reaches_mop`), percentage points (0–100) | used |
| `mop_unique` | count of a seven-part accusation key (see Traps). Float-formatted (`3.0`) on 6,101 rows, integer text on the other 10,036 | |
| `mop_total` | raw accusation events in the run | used |
| `mop_unique4` | unique misuses in the run: distinct `(class, method, spec)` | used |
| `crashes` | app crashes seen in the run | |
| `anrs` | "application not responding" events seen in the run | |
| `tool_seconds` | time the tool actually ran (exposure), not the budget | |
| `sa_methods` | methods of the app found by static analysis (constant per app) | |
| `sa_methods_reaches_mop` | methods that reach a monitored API; constant per app; the size covariate of the RQ1 GLM | used |
| `category` | admissibility class: `admissivel` 15,653, `parada_ferramenta` 246, `estrutural` 171, `lancamento_externo` 45, `inadmissivel` 22 | used |
| `admissible` | 1 when `category` is `admissivel`, else 0 (484 runs with 0) | used |
| `fails` | admissibility criteria that failed (`C2`, `C4+C5`, …); empty on 16,112 rows | |

### `campaign/direct-coverage.csv`

Direct-reach coverage per run. Key `(apk, tool, rep, timeout)`, the same 16,137 keys as
`per_task.csv`, joined 1:1. **16,137 rows**, 6 columns.

| Column | Meaning | Mark |
|---|---|---|
| `apk`, `tool`, `rep`, `timeout` | run key, as in `per_task.csv` | key |
| `cov_directly_reaches_mop` | coverage of the methods that call a monitored API **directly**, percentage points (0–100) | used |
| `measured` | `true` when the coverage denominator was measured; `true` in all rows | |

### `campaign/raw-accusations.csv`

Every accusation the monitors raised in the campaign, from the 12 per-container `errors.csv`
exports. The columns `message` and `unique_msg` were dropped upstream. One row per accusation
event, no unique key. **91,368 rows**, 11 columns, in 89 apps.

| Column | Meaning | Mark |
|---|---|---|
| `apk`, `rep`, `timeout`, `tool` | run key | key |
| `time` | seconds from the tool start to the accusation (whole seconds, clamped at 0) | used |
| `spec` | declared name of the specification that fired, e.g. `CipherSpec` | used |
| `class` | class of the call site | used |
| `method` | method of the call site | used |
| `source` | source file and line of the call site, e.g. `Platform.kt:168` | |
| `code` | code of the accusation; its label is in `instrument/codes.csv` | used |
| `event` | monitor event that fired | |

### `campaign/primary-accusations.csv`

The rows of the 12 `errors.csv` whose own `code` is labelled `violation` or `sequence` in
`codes.csv`. All 13 original columns, unchanged. One row per accusation event. **18,214 rows**, in
48 apps.

| Column | Meaning | Mark |
|---|---|---|
| `apk`, `rep`, `timeout`, `tool`, `time` | as in `raw-accusations.csv` | key |
| `spec`, `class`, `method` | as in `raw-accusations.csv`; with `apk` they form the misuse key | key |
| `source`, `event` | as in `raw-accusations.csv` | |
| `code` | accusation code | used |
| `message` | the monitor's report, `v=1 code=… ev=… obj=… val='…' exp='…' msg='…'`. The RQ3 value patterns (ECB, MD5, SHA-1, old protocol, PBE iterations) read `val='…'` | used |
| `unique_msg` | `class:::method:::spec:::…` concatenation | |

### `campaign/severe-sites.csv`

The audit table of the severe-misuse sensitivity outcome. One row per candidate site
`(apk, class, method, spec, code)`. **106 rows**, 9 columns.

| Column | Meaning | Mark |
|---|---|---|
| `apk`, `class`, `method`, `spec` | site; the misuse key | used |
| `code` | accusation code of the site | |
| `criterion` | `trust-all` (9 rows) or `constant` (97 rows) | |
| `evidence` | the disassembled `checkServerTrusted` bodies, or `runs=…; distinct_vfp=…` | |
| `verdict` | `trust-all` 4, `not-trust-all` 5, `constant` 9, `varying` 80, `undecided` 8 | used |
| `in_primary` | whether the misuse `(apk, class, method, spec)` is already a primary misuse | |

### `campaign/docker-compose.estudo02-20260916.yml`

The campaign's compose file, generated by rv-android's comparison tooling. Not read by any script.
It is the evidence for four macros checked by inspection (see the main README): 12 campaign
containers (`container_name: estudo02-20260916_00` … `_11`), each from the `rvandroid:0.9.4` image
with `/dev/kvm`, limited to `cpus: "4"` and `memory: "10g"`, plus the `rv-humanoid` model server.
Its comment lines are in Portuguese, as written upstream. The volume mount lines are anonymized
(see Traps).

## `corpus/`

### `corpus/dataset.csv`

The selection funnel of the `jca_android` corpus. One row per candidate app; no row is ever
deleted. Key `apk`. **3,941 rows**, 89 columns, CRLF line endings. The 163 analysed apps are the
rows with `funnel_stage == 'selected'`.

Columns read by the published numbers:

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id `<package>_<version_code>.apk`, the F-Droid harvest identity | key |
| `funnel_stage` | `selected` or the `filtered_*` stage where the app left the funnel (13 values, see below) | used |
| `excluded_reason` | `<class>` or `<class>:<detail>`; the class is the text before the first `:`. Empty on the 163 `selected` rows | used |
| `sa_status` | static-analysis outcome: `complete` 263, `failed_timeout_no_json` 1, `failed_no_json` 1; empty for apps that never reached it | used |
| `sa_analysis_seconds` | static-analysis wall time, seconds | used |
| `sa_methods_reaches_mop` | methods that transitively reach a monitored API | |
| `sa_methods_directly_reaches_mop` | methods that call a monitored API directly | used |
| `sa_directly_reaches_mop` | whether any method calls a monitored API directly | used |

`funnel_stage` values, in pipeline order: `filtered_compat` 388, `filtered_github` 1,949,
`filtered_playstore` 874, `filtered_build_probe` 355, `filtered_build` 27, `filtered_dedup` 13,
`filtered_mneut_scope` 70, `filtered_sa_no_json` 2, `filtered_no_mop` 90, `filtered_smoke` 3,
`filtered_instrumentation` 6, `filtered_zero_coverage` 1, `selected` 163.

The other 81 columns are carried unchanged and read by no claim. By group, in the order of the
pipeline stage that fills them (a cell is empty when the app never reached that stage):

| Group | Columns |
|---|---|
| identity | `manifest_package`, `detected_package`, `sa_mismatch`, `main_activity` |
| F-Droid harvest | `version_code`, `version_name`, `repo`, `repo_url`, `fdroid_last_updated`, `categories`, `apk_size_mb`, `dex_count`, `min_sdk`, `target_sdk`, `max_sdk`, `compile_sdk`, `native_code_abis` |
| GitHub recency | `is_github`, `github_last_commit_date`, `github_last_commit_sha` |
| Google Play | `in_playstore`, `play_installs`, `play_min_installs`, `play_real_installs`, `play_score`, `play_ratings` |
| build probe | `probe_build_ok`, `probe_build_class`, `probe_jdk`, `probe_gradle`, `probe_commit` |
| versionCode build | `pinned_commit`, `repos_cloned`, `build_status`, `build_task`, `jdk_used`, `gradle_used`, `recovery_notes`, `unobfuscated_verified`, `debuggable_verified` |
| HEAD build (the corpus) | `head_pinned_commit`, `head_repos_vendored`, `head_build_status`, `head_build_class`, `head_build_task`, `head_build_variant`, `head_jdk_used`, `head_gradle_used`, `head_recovery_notes`, `head_unobfuscated_verified`, `head_debuggable_verified`, `head_is_env` |
| static analysis | `sa_engine`, `sa_classes`, `sa_methods`, `sa_methods_reachable`, `sa_reaches_mop`, `sa_num_activities`, `sa_num_services`, `sa_num_receivers`, `sa_num_providers`, `sa_windows_count`, `sa_transitions_count`, `sa_components_count` |
| original-APK smoke test | `orig_install_ok`, `orig_install_err`, `orig_launch_ok`, `orig_launch_err`, `orig_validation_status`, `orig_has_verifyerror` |
| instrumentation | `jca_instrumented`, `install_ok`, `install_err`, `launch_ok`, `launch_err`, `validation_status`, `has_verifyerror` |
| funnel note | `obs` (free text, one row) |
| earlier package detector | `pkgdet_verdict`, `pkgdet_app_code_frac`, `pkgdet_foreign_frac` (history, see Traps) |

Empty in all rows: `manifest_package`, `sa_mismatch`, `main_activity`, `dex_count`, `max_sdk`,
`compile_sdk`, `recovery_notes`, `launch_err`.

### `corpus/ground_truth_sheet.csv`

The manually adjudicated ground truth of which package roots are each app's own code. One row
per app built from source. Key `apk`. **348 rows**, 25 columns. The funnel's scope gate ran over
`G_final`.

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id | key |
| `decided_by` | who fixed `G_final`: `auto` 196, `manual` 145, `auto_single_witness` 7 | used |
| `G_final` | the adjudicated package roots of the app's own code | |
| `evidence` | adjudicator's note; `readjudicated 2026-08-07` marks the six rows changed in the last pass | |
| `date` | date of the decision | |
| `M`, `P`, `detection_method`, `confidence`, `unstable_election`, `auto_G`, `oracle_G`, `oracle_ambiguous`, `r1_dropped_candidates`, `denylist_candidates` | intermediate fields of the automatic election that preceded adjudication | |
| `flag_r1_drops`, `flag_denylist_hits`, `flag_g_empty`, `flag_multiroot`, `flag_divergence`, `flag_repackaged`, `flag_oracle_abstain`, `queued`, `queue_reason`, `safety_net` | flags that queued a row for manual review | |

### `corpus/mneut_348.csv`

The scope key `Mneut` and the scope-gate verdict for each app built from source. Key `apk`.
**348 rows**, 8 columns.

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id | key |
| `manifest_package` | applicationId of the built APK | |
| `Mneut` | neutralized manifest package (build-type suffixes stripped): the app's root package. A class is app code when it equals `Mneut` or starts with `Mneut + '.'` | used |
| `G_final` | ground-truth package roots, as in `ground_truth_sheet.csv` | |
| `n_A_mneut` | compiled classes under `Mneut` | |
| `cov_G` | coverage score of the gate; keeping an app needs `cov_G` ≥ 0.90 | |
| `foreign` | classes under `Mneut` outside the ground truth; keeping an app needs 0 | |
| `keep` | gate verdict: `true` 265, `false` 83 | |

### `corpus/fdroid_index_snapshot.json`

A record of the F-Droid index the corpus was harvested from (not the index itself). One JSON
object with `source_url`, `index_file`, `sha256`, `size_bytes`, `fetched_at_utc`,
`repo_timestamp`, `repo_name`. Not read by any script. `fetched_at_utc`
(`2026-06-22T16:28:23.441124+00:00`) is the evidence for `fdroidIndexDate`, checked by inspection.

## `instrument/`

### `instrument/codes.csv`

The accusation codes of the 47 specifications and their labels. Key `code`. **330 rows** over
45 specifications (`KeySpec` and `SecretKeySpec` raise no code), 7 columns.

| Column | Meaning | Mark |
|---|---|---|
| `spec` | declared specification name (not always the file name, see Traps) | |
| `code` | accusation code, e.g. `CIPHER-ALG-00` | used |
| `error_type` | CrySL-style error type, e.g. `UnsafeAlgorithm` | |
| `site_kind` | `ORDER` 101, `CONSTR` 86, `NOBS` 84, `ALG` 43, `FORB` 6, `KEYSIZE` 5, `PROTO` 4, `KSTYPE` 1 | |
| `event` | monitor event that raises the code | |
| `file_line` | `<file>.mop:<line>` of the `addError(` call | |
| `label` | `violation` 145, `not-observed` 64, `sequence` 44, `creation-unobserved` 43, `creation-refused` 12, `upstream-refused` 12, `platform-default` 5, `reuse-after-final` 2, `random-key-material` 2, `application-manager` 1. A misuse is **primary** when one of its codes is `violation` or `sequence`. `platform-default` drives the default-trust pattern of RQ3 | used |

### `instrument/specs.zip`

The 47 JavaMOP specifications (`.mop`) that ran, restored to `instrument/specs/`. Member list in
`instrument/specs.sha256`. The number of files gives `jcaSpecCount`. The literals of the
`Arrays.asList(...)` allow-lists are the evidence for `vennTupOnlyCCAdmittedWord`, checked by
inspection.

## `baselines/cognicrypt/`

### `baselines/cognicrypt/findings.csv`

Every row of the 145 CogniCrypt reports, with `apk` prepended. Nothing is filtered, relabelled or
mapped. One row per finding. **1,353 rows**, 11 columns.

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id | key |
| `ErrorId` | finding id inside the report | |
| `ErrorType` | `RequiredPredicateError` 563, `TypestateError` 317, `ConstraintError` 183, `IncompleteOperationError` 158, `ImpreciseValueExtractionError` 132 | used |
| `PrecedingErrors`, `SubsequentErrors` | ids of linked findings | |
| `ViolatedRule` | fully qualified JCA class of the rule, e.g. `javax.net.ssl.TrustManagerFactory` | used |
| `Class` | class of the finding | used |
| `Method` | Soot signature of the method of the finding | used |
| `Statement`, `LineNumber` | Jimple statement and line | |
| `Message` | CogniCrypt's message; 154 of the 183 `ConstraintError` findings carry `with value "…"` | used |

### `baselines/cognicrypt/per-app-outcomes.csv`

CogniCrypt outcome per app of the 163. Key `apk`. **163 rows**, 9 columns.

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id | key |
| `status` | `success` 145, `error` 12, `timeout` 6 | used |
| `gap_class` | for the 18 apps without a verdict: `soot_spark_varnode_crash` or `callgraph_timeout` | |
| `findings` | number of findings; **empty** (not 0) for the 18 apps without a verdict | used |
| `findings_ConstraintError`, `findings_ImpreciseValueExtractionError`, `findings_IncompleteOperationError`, `findings_RequiredPredicateError`, `findings_TypestateError` | findings per `ErrorType`; empty for the 18 | |

### `baselines/cognicrypt/gaps_18.csv`

The 18 apps for which CogniCrypt gave no verdict. Key `apk`. **18 rows**, 8 columns.

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id | key |
| `final_status` | `error` or `timeout` | |
| `gap_class` | `soot_spark_varnode_crash` 12, `callgraph_timeout` 6 | |
| `attempts` | status of each attempt, space-separated | |
| `durations_s` | duration of each attempt, seconds | |
| `last_attempt_budget` | `<n>x<heap>g/<seconds>s`: `2x40g/3600s` 10, `1x90g/7200s` 8. Heap and time budgets are parsed from it | used |
| `root_cause` | crash message | |
| `crash_site` | Soot method where the crash happened | |

### `baselines/cognicrypt/cognicrypt_summary.csv`

CogniCrypt run status per app. Key `apk`. **163 rows**, 7 columns. `error_message` holds quoted
newlines.

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id | key |
| `pass1`, `pass2`, `pass3` | whether each pass succeeded (`yes`, `no`; `---` or empty when not run) | |
| `last_status` | `success` 145, `error` 12, `timeout` 6 | |
| `duration_s` | duration of the last pass, seconds | |
| `error_message` | CogniCrypt stderr, filled on 13 rows. Holds "Found 47 rules" and the "Skipping rule since it contains errors: …/X.crysl" lines (`SSLEngine`, `OAEPParameterSpec`). Inspection evidence for `ccRulesLoaded` and `ccRulesRejectedWord`; the Venn script reads the rejected rule names. Anonymized (see Traps) | used |

### `baselines/cognicrypt/crysl-rules.zip`

The 49 CrySL rules (`.crysl`) CogniCrypt ran with, restored to `baselines/cognicrypt/crysl-rules/`.
Member list in `crysl-rules.sha256`. The number of files gives `ccRulesCopied`. The `SPEC <class>`
line of each rule maps a finding's `ViolatedRule` to a JCA class.

## `baselines/unit-tests/`

### `baselines/unit-tests/unittests_status.csv`

Unit-test status per app of the 163. Key `apk`. **163 rows**, 10 columns.

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id | key |
| `source_status` | how the source was obtained (`vendored` in all rows) | |
| `has_unit_tests` | `yes` 102, `no` 61 | used |
| `build_status` | test build outcome; empty when the app has no tests | |
| `test_status` | `success` 94, `fail` 8, empty 61 | used |
| `violations` | accusation count reported by the run | |
| `notes` | free text | |
| `unit_test_files` | number of unit-test files | |
| `jdk_used`, `gradle_used` | JDK and Gradle versions of the test run | |

### `baselines/unit-tests/exp02_jca_errors_unit_tests.csv`

The accusations raised while the unit tests ran under the JavaMOP agent. One row per accusation
event. **343 rows**, 10 columns, in 30 apps. There is no `code` column.

| Column | Meaning | Mark |
|---|---|---|
| `apk` | app id | used |
| `rep`, `timeout`, `tool`, `time` | constant placeholders: `1`, `0`, `unit_test`, `0` | |
| `spec`, `class`, `method` | as in `raw-accusations.csv` | used |
| `message` | the monitor's report; the code is the `code=` field | |
| `unique_msg` | `class:::method:::spec:::…` concatenation | |

### `baselines/unit-tests/categoria_unit_tests.csv`

Origin of each unit-test misuse, assigned upstream (66 of the 148 were reviewed by hand). Key
`(apk, spec, class, method)`.
**148 rows**, 6 columns.

| Column | Meaning | Mark |
|---|---|---|
| `apk`, `spec`, `class`, `method` | the misuse | used |
| `categoria` | origin: `app_producao` (production code) 84, `lib` (library) 39, `robolectric_noise` (Robolectric artifact) 13, `test_code` (test code) 12 | used |
| `confidence` | empty in all rows | |

## Traps

Each trap below gives a wrong number that still passes a type check.

1. **Two "MOP coverage" columns.** `per_task.cov_mop` is the **transitive** measure
   (`cov_reaches_mop`). `direct-coverage.cov_directly_reaches_mop` is the **direct** one, a
   different measure. The article's RQ2 code names the direct column `cov_mop` after loading it.
   That alias is not `per_task.cov_mop`. The `coverage_mop` table and the all-zero definition use
   the direct column.
2. **Coverage is in percentage points.** Every coverage column is 0–100, not 0–1.
3. **Two uniqueness keys.** `mop_unique` counts a seven-part key (class, method, spec, error type,
   code, event, message). `mop_unique4` counts distinct `(class, method, spec)` in the run. The
   article's "unique misuse" is `mop_unique4`. The two cannot be compared.
4. **Accusations are not misuses.** `raw-accusations.csv` has one row per event, several per
   misuse and of every label. A misuse is a distinct `(class, method, spec)` in a run, or
   `(apk, class, method, spec)` across the campaign (453 unique). A misuse is primary when **any**
   of its codes is labelled `violation` or `sequence`. The labels do not partition the misuses:
   one misuse can carry codes of several labels. Never add per-label counts.
5. **`per_task.csv` is the delivered consolidation.** It has the same 16,137 rows and the same
   values as the consolidation re-derived from the raw logs, plus `category`, `admissible` and
   `fails`. These three columns are recorded and counted. No run is excluded on them in the primary
   analysis.
6. **All-zero runs.** A run is all-zero when `cov_method`, `cov_act`, `cov_mop`,
   `cov_directly_reaches_mop`, `mop_unique4` and `mop_total` are all 0 (176 runs). Five of these
   columns come from `per_task.csv` and one from `direct-coverage.csv`.
7. **`tool_seconds` is the exposure, not the budget.** It counts from the tool start to its end.
   The budget is `timeout`.
8. **An empty CogniCrypt count is not a zero.** In `per-app-outcomes.csv`, the 18 apps with
   `status` `error` or `timeout` have empty counts. CogniCrypt gave them no verdict. Filling with 0
   turns 18 unanalysed apps into clean ones and the denominator from 145 into 163.
9. **Three unit-test denominators.** `unittests_status.csv` covers 163 apps. 102 have unit tests
   (the population). The tests of 94 ran (`test_status = success`) and those of 8 did not
   (`fail`). An empty `test_status` means no tests, not a failed run.
10. **Severe is a verdict, not a label.** In `severe-sites.csv` only `trust-all` and `constant` are
    severe. `undecided` is its own class and never counts as severe. A severe site can already be
    primary (`in_primary`), so a union of the two never equals their sum.
11. **The scope key is `Mneut`, never `detected_package`.** `dataset.csv`'s `detected_package` keeps
    build-type suffixes (`.debug`, …) and differs from `Mneut` on 76 of the 163 apps. Read `Mneut`
    from `mneut_348.csv`.
12. **Two gate counts.** `mneut_348.csv` rejects 83 apps (`keep = false`), but only 70 have
    `funnel_stage = filtered_mneut_scope`, because 13 were already cut as `filtered_dedup`. The
    `pkgdet_*` columns of `dataset.csv` belong to an earlier package detector. They are not a scope
    rule of this funnel.
13. **`spec` is the declared name, not the file name.** `IvChainJunction.mop` declares
    `IvChainJunctionSpec` and `IvParameterSpec.mop` declares `IvParameterSpecSpec`. Joining
    `codes.csv` to the files by stripping `.mop` loses two specifications.
14. **Parse, do not split.** `error_message` in `cognicrypt_summary.csv` holds quoted newlines.
    Tool labels contain `:` (`droidbot:dfs_naive`). Eight CSVs use CRLF line endings
    (`per_task`, `dataset`, `ground_truth_sheet`, `gaps_18`, `cognicrypt_summary`,
    `unittests_status`, `exp02_jca_errors_unit_tests`, `categoria_unit_tests`). Read every file with a CSV parser.
15. **Anonymization tokens.** In three files, absolute path prefixes of the producing machine were
    replaced with the tokens `<WORKSPACE>/` and `<HOST>/`. The affected fields are `build_status`
    and `orig_install_err` of `dataset.csv`, `error_message` of `cognicrypt_summary.csv`, and the
    volume mount lines of the `.yml`. The rest of each file is unchanged. A macOS user path inside a
    third-party project's build error (`excluded_reason`, `probe_build_class`) and third-party
    `repo_url` values are left as published upstream. See the main README, Data origin.
