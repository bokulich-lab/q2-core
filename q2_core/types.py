# ----------------------------------------------------------------------------
# Copyright (c) 2026, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_types.feature_data import FeatureData, ImportanceFormat
from rachis.plugin import SemanticType, model

Scores = SemanticType("Scores", variant_of=FeatureData.field["type"])

ScoresDirFmt = model.SingleFileDirectoryFormat(
    "ScoresDirFmt", "scores.tsv", ImportanceFormat
)
