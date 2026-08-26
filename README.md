# q2-core

Rachis (QIIME 2) plugin for computing prevalence-abundance core scores from
relative-frequency feature tables.

## How the core score is calculated

For each feature, q2-core combines how consistently the feature occurs across
samples with how abundant it is:

1. **Prevalence** is the fraction of samples in which the feature's relative
   abundance is strictly greater than `min_rel_abundance` (default: `0.001`).
2. **Mean relative abundance** is calculated across all samples by default. If
   `mean_abundance_on_presence=True`, the mean instead uses only samples where
   the feature exceeds `min_rel_abundance`.
3. The mean abundance is transformed as
   `log10(mean_abundance + offset)`, where `offset` (default: `1e-6`) prevents
   taking the logarithm of zero.
4. Prevalence and log-transformed mean abundance are each min--max scaled to
   the interval `[0, 1]` across all features in the input table.
5. The final score is their product:
   `core_score = scaled_prevalence * scaled_log_mean_abundance`.

Consequently, a high score identifies features that are both widespread and
relatively abundant. Features with a low value for either component receive a
low score. Scores are relative to the features in the supplied table; if all
features have the same value for either component, that component is set to
zero for every feature.

The output contains the unscaled and scaled component values as
`prevalence`, `mean_abundance`, `log_mean_abundance`, `prevalence_scaled`, and
`log_mean_abundance_scaled`, in addition to `core_score`.

## Installation
Please follow the installation instructions on
the [QIIME 2 Library](https://library.qiime2.org/plugins/bokulich-lab/q2-core), to
install an env with the QIIME 2 or MOSHPIT distros and q2-core.

## Usage

### Python API
```
rel_frequency_table = Artifact.load("path-to-table")

core_scores = core.actions.score(
    table=rel_frequency_table,
    min_rel_abundance=0.001,
    mean_abundance_on_presence=True,
)
core_scores_artifact = core_scores.core_scores
core_scores_artifact.save("output_path_core_score")

filtered_table = feature_table.actions.filter_features(
    table=rel_frequency_table,
    metadata=core_scores_artifact.view(Metadata),
    where="core_score > 0.01",
    max_frequency="None",
)
filtered_rel_frequency_table = filtered_table.filtered_table
filtered_rel_frequency_table.save("output_path_filtered_table")
```

### CLI
```
qiime core score \
  --i-table rel_frequency_table.qza \
  --p-min-rel-abundance 0.001 \
  --p-mean-abundance-on-presence \
  --o-core-scores core_scores.qza

qiime feature-table filter-features \
  --i-table rel_frequency_table.qza \
  --m-metadata-file core_scores.qza \
  --p-where 'core_score > 0.01' \
  --o-filtered-table filtered_rel_frequency_table.qza
```
