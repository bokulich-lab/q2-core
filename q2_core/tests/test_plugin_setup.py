# ----------------------------------------------------------------------------
# Copyright (c) 2026, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_types.feature_data import FeatureData
from rachis.plugin.testing import TestPluginBase

from q2_core.types import Scores, ScoresDirFmt


class PluginTests(TestPluginBase):
    package = "q2_core.tests"

    def test_plugin(self):
        self.assertEqual(self.plugin.name, "core")

    def test_score_is_registered(self):
        self.assertIn("score", self.plugin.methods)
        self.assertEqual(
            self.plugin.methods["score"].signature.outputs["core_scores"].qiime_type,
            FeatureData[Scores],
        )

    def test_scores_type_is_registered(self):
        self.assertRegisteredSemanticType(Scores)
        self.assertSemanticTypeRegisteredToFormat(FeatureData[Scores], ScoresDirFmt)
