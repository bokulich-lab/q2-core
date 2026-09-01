# ----------------------------------------------------------------------------
# Copyright (c) 2026, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import numpy as np
import pandas as pd
from q2templates.reports import matryoshka_template
from rachis import Metadata


def _score(
    table: pd.DataFrame,
    min_rel_abundance: float = 1e-3,
    mean_abundance_on_presence: bool = False,
    offset: float = 1e-6,
) -> pd.DataFrame:
    """Compute prevalence-abundance core scores for feature table columns.

    Computes feature prevalence and mean relative abundance across samples,
    scales both quantities to the range [0, 1], and multiplies them to
    produce a core score for each feature.

    Args:
        table (pd.DataFrame): Relative abundances with samples as rows and
            features as columns.
        min_rel_abundance (float): Minimum relative abundance for counting a
            feature as present in a sample.
        mean_abundance_on_presence (bool): Whether to compute mean abundance
            using only samples in which the feature is present.
        offset (float): Positive value added before log transformation to
            prevent taking the logarithm of zero.

    Returns:
        pd.DataFrame: Prevalence, mean abundance, log mean abundance, their
            min-max scaled values, and core score values indexed by feature ID.
    """
    prevalence = (table > min_rel_abundance).mean(axis=0)
    if mean_abundance_on_presence:
        mean_abundance = table.where(table > min_rel_abundance).mean(axis=0).fillna(0)
    else:
        mean_abundance = table.mean(axis=0)
    log_mean = np.log10(mean_abundance + offset)

    prevalence_scaled = _minmax_scale(prevalence)
    log_mean_scaled = _minmax_scale(log_mean)
    scores = prevalence_scaled * log_mean_scaled

    result = pd.DataFrame(
        {
            "prevalence": prevalence,
            "prevalence_scaled": prevalence_scaled,
            "mean_abundance": mean_abundance,
            "log_mean_abundance": log_mean,
            "log_mean_abundance_scaled": log_mean_scaled,
            "core_score": scores,
        }
    )
    result.index.name = "id"
    return result


def score(
    ctx,
    table,
    min_rel_abundance=1e-3,
    mean_abundance_on_presence=False,
    offset=1e-6,
):
    """Compute core scores and visualize their prevalence-abundance relationship.

    Runs the internal core-scoring action, creates a scatterplot of mean
    abundance against prevalence colored by core score, tabulates the score
    metadata, and combines both visualizations into a Matryoshka report.

    Args:
        ctx: Pipeline execution context used to retrieve actions and create
            reports.
        table: Relative-frequency feature table to score.
        min_rel_abundance: Relative-abundance threshold above which a feature
            is considered present in a sample.
        mean_abundance_on_presence: Whether to average abundance only across
            samples in which the feature is present.
        offset: Small positive value added before log transformation.

    Returns:
        tuple: The core-score artifact and a visualization report containing
            the scatterplot and score table.
    """
    score_action = ctx.get_action("core", "_score")
    scatterplot = ctx.get_action("vizard", "scatterplot_2d")
    tabulate = ctx.get_action("metadata", "tabulate")

    (core_scores,) = score_action(
        table=table,
        min_rel_abundance=min_rel_abundance,
        mean_abundance_on_presence=mean_abundance_on_presence,
        offset=offset,
    )
    metadata = core_scores.view(Metadata)
    (scatterplot_visualization,) = scatterplot(
        metadata=metadata,
        x_measure="mean_abundance",
        y_measure="prevalence",
        color_by="core_score",
    )
    (table_visualization,) = tabulate(input=metadata)
    visualization = ctx.make_report(
        matryoshka_template,
        {
            "Scatterplot": scatterplot_visualization,
            "Core scores": table_visualization,
        },
    )
    return core_scores, visualization


def _minmax_scale(x: pd.Series) -> pd.Series:
    """Scale values to the range [0, 1]"""
    data_range = x.max() - x.min()
    if data_range == 0:
        return pd.Series(0.0, index=x.index)
    return (x - x.min()) / data_range
