# ----------------------------------------------------------------------------
# Copyright (c) 2026, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_types.feature_data import FeatureData
from q2_types.feature_table import FeatureTable, RelativeFrequency
from rachis.plugin import Bool, Float, Plugin, Range

import q2_core
from q2_core.types import Scores, ScoresDirFmt

plugin = Plugin(
    name="core",
    version=q2_core.__version__,
    website="https://qiime2.org",
    package="q2_core",
    short_description="Compute core scores for relative-frequency tables.",
    description=(
        "This plugin computes prevalence-abundance core scores for features in "
        "relative-frequency feature tables."
    ),
)

plugin.methods.register_function(
    function=q2_core.score,
    inputs={"table": FeatureTable[RelativeFrequency]},
    parameters={
        "min_rel_abundance": Float % Range(0, 1, inclusive_start=False),
        "mean_abundance_on_presence": Bool,
        "offset": Float % Range(0, None, inclusive_start=False),
    },
    outputs=[("core_scores", FeatureData[Scores])],
    input_descriptions={"table": "The relative-frequency feature table to score."},
    parameter_descriptions={
        "min_rel_abundance": (
            "Minimum relative abundance used to count a feature as present in a "
            "sample."
        ),
        "mean_abundance_on_presence": (
            "If true, compute mean relative abundance using only samples where "
            "the feature is greater than `min_rel_abundance`. If false, compute "
            "mean relative abundance across all samples."
        ),
        "offset": (
            "Small positive value used as the log offset and min-max scaling "
            "denominator offset."
        ),
    },
    output_descriptions={
        "core_scores": (
            "Prevalence, mean abundance, log mean abundance, scaled prevalence, "
            "scaled log mean abundance, and core score values for each feature."
        )
    },
    name="Compute core score for features",
    description=(
        "Compute a prevalence-abundance core score for each feature in a "
        "relative-frequency feature table. Prevalence is the fraction of samples "
        "where a feature exceeds `min_rel_abundance`; mean relative abundance is "
        "computed either across all samples or only samples above "
        "`min_rel_abundance`, then log-transformed with `offset`; both quantities "
        "are min-max scaled across features and multiplied to produce the final "
        "score."
    ),
)

plugin.register_formats(ScoresDirFmt)
plugin.register_semantic_types(Scores)
plugin.register_semantic_type_to_format(FeatureData[Scores], ScoresDirFmt)
