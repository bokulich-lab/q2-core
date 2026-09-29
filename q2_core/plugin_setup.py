# ----------------------------------------------------------------------------
# Copyright (c) 2026, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_types.feature_data import FeatureData, ImportanceDirectoryFormat
from q2_types.feature_table import FeatureTable, RelativeFrequency
from rachis.plugin import Bool, Float, Plugin, Range, Visualization

import q2_core
from q2_core.types import Scores

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

score_inputs = {"table": FeatureTable[RelativeFrequency]}
score_parameters = {
    "min_rel_abundance": Float % Range(0, 1, inclusive_start=False),
    "mean_abundance_on_presence": Bool,
    "offset": Float % Range(0, None, inclusive_start=False),
}
score_input_descriptions = {"table": "The relative-frequency feature table to score."}
score_parameter_descriptions = {
    "min_rel_abundance": (
        "Relative-abundance threshold above which a feature is considered present "
        "in a sample."
    ),
    "mean_abundance_on_presence": (
        "If true, compute mean relative abundance using only samples in which the "
        "feature exceeds 'min_rel_abundance'. If false, compute mean relative "
        "abundance across all samples."
    ),
    "offset": "Small positive value added before log transformation.",
}

score_description = (
    "Compute a prevalence-abundance core score for each feature in a "
    "relative-frequency feature table. Prevalence is the fraction of samples "
    "where a feature exceeds `min_rel_abundance`; mean relative abundance is "
    "computed either across all samples or only samples above "
    "`min_rel_abundance`, then log-transformed with `offset`; both quantities "
    "are min-max scaled across features and multiplied to produce the final "
    "score."
)

plugin.methods.register_function(
    function=q2_core._score,
    inputs=score_inputs,
    parameters=score_parameters,
    outputs=[("core_scores", FeatureData[Scores])],
    input_descriptions=score_input_descriptions,
    parameter_descriptions=score_parameter_descriptions,
    output_descriptions={
        "core_scores": (
            "Prevalence, mean abundance, log mean abundance, scaled prevalence, "
            "scaled log mean abundance, and core score values for each feature."
        )
    },
    name="Compute core score for features",
    description=score_description,
)

plugin.pipelines.register_function(
    function=q2_core.score,
    inputs=score_inputs,
    parameters=score_parameters,
    outputs=[
        ("core_scores", FeatureData[Scores]),
        ("visualization", Visualization),
    ],
    input_descriptions=score_input_descriptions,
    parameter_descriptions=score_parameter_descriptions,
    output_descriptions={
        "core_scores": (
            "Prevalence, mean abundance, log mean abundance, scaled prevalence, "
            "scaled log mean abundance, and core score values for each feature."
        ),
        "visualization": (
            "Report containing a prevalence-abundance scatterplot and a table of "
            "core scores."
        ),
    },
    name="Compute and visualize core scores for features",
    description=(
        f"{score_description} The pipeline also creates a report containing a "
        "prevalence-abundance scatterplot and tabulation of the core scores."
    ),
)

plugin.register_semantic_types(Scores)
plugin.register_semantic_type_to_format(FeatureData[Scores], ImportanceDirectoryFormat)
