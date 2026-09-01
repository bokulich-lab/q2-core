# ----------------------------------------------------------------------------
# Copyright (c) 2026, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json
from pathlib import Path
from unittest.mock import MagicMock, call

import numpy as np
import pandas as pd
import pandas.testing as pdt
from qiime2 import Artifact, Metadata
from qiime2.plugins.core.pipelines import score as score_pipeline
from rachis.plugin.testing import TestPluginBase

from q2_core import _score, score
from q2_core.core_score import _minmax_scale, matryoshka_template


class TestScore(TestPluginBase):
    package = "q2_core.tests"

    def setUp(self):
        super().setUp()
        self.table = pd.DataFrame(
            [
                [0.001, 0.099, 0.90],
                [0.02, 0.08, 0.90],
                [0.03, 0.07, 0.90],
            ],
            index=["S1", "S2", "S3"],
            columns=["O1", "O2", "O3"],
        )

    def test_score(self):
        observed = _score(self.table)

        index = pd.Index(["O1", "O2", "O3"], name="id")
        expected = pd.DataFrame(
            {
                "prevalence": (self.table > 1e-3).mean(axis=0),
                "prevalence_scaled": [0.0, 1.0, 1.0],
                "mean_abundance": self.table.mean(axis=0),
                "log_mean_abundance": np.log10(self.table.mean(axis=0) + 1e-6),
                "log_mean_abundance_scaled": [0.0, 0.3994787279202171, 1.0],
                "core_score": np.multiply(
                    [0.0, 1.0, 1.0], [0.0, 0.3994787279202171, 1.0]
                ),
            },
            index=index,
        )

        pdt.assert_frame_equal(observed, expected)

    def test_score_custom_parameters(self):
        observed = _score(self.table, min_rel_abundance=0.01, offset=1e-3)

        index = pd.Index(["O1", "O2", "O3"], name="id")
        expected = pd.DataFrame(
            {
                "prevalence": (self.table > 0.01).mean(axis=0),
                "prevalence_scaled": [0.0, 1.0, 1.0],
                "mean_abundance": self.table.mean(axis=0),
                "log_mean_abundance": np.log10(self.table.mean(axis=0) + 1e-3),
                "log_mean_abundance_scaled": [0.0, 0.3936602318986702, 1.0],
                "core_score": np.multiply(
                    [0.0, 1.0, 1.0], [0.0, 0.3936602318986702, 1.0]
                ),
            },
            index=index,
        )

        pdt.assert_frame_equal(observed, expected)

    def test_score_mean_abundance_on_presence(self):
        observed = _score(
            self.table,
            min_rel_abundance=0.01,
            mean_abundance_on_presence=True,
        )

        index = pd.Index(["O1", "O2", "O3"], name="id")
        expected = pd.DataFrame(
            {
                "prevalence": (self.table > 0.01).mean(axis=0),
                "prevalence_scaled": [0.0, 1.0, 1.0],
                "mean_abundance": self.table.where(self.table > 0.01).mean(axis=0),
                "log_mean_abundance": np.log10(
                    self.table.where(self.table > 0.01).mean(axis=0) + 1e-6
                ),
                "log_mean_abundance_scaled": [0.0, 0.3348523823164069, 1.0],
                "core_score": np.multiply(
                    [0.0, 1.0, 1.0], [0.0, 0.3348523823164069, 1.0]
                ),
            },
            index=index,
        )

        pdt.assert_frame_equal(observed, expected)

    def test_minmax_scale_values(self):
        observed = _minmax_scale(pd.Series([2.0, 4.0, 6.0]))
        pdt.assert_series_equal(observed, pd.Series([0.0, 0.5, 1.0]))

    def test_minmax_scale_zero_range(self):
        observed = _minmax_scale(pd.Series([2, 2, 2]))
        pdt.assert_series_equal(observed, pd.Series([0.0, 0.0, 0.0]))

    def test_score_pipeline_calls_its_actions(self):
        core_scores = MagicMock()
        metadata = MagicMock()
        core_scores.view.return_value = metadata
        scatterplot_visualization = MagicMock()
        table_visualization = MagicMock()
        score_action = MagicMock(return_value=(core_scores,))
        scatterplot_action = MagicMock(return_value=(scatterplot_visualization,))
        tabulate_action = MagicMock(return_value=(table_visualization,))
        mock_action = MagicMock(
            side_effect=[score_action, scatterplot_action, tabulate_action]
        )
        mock_context = MagicMock(get_action=mock_action)

        score(
            ctx=mock_context,
            table=self.table,
            min_rel_abundance=0.01,
            mean_abundance_on_presence=True,
            offset=1e-3,
        )

        self.assertEqual(
            mock_context.get_action.call_args_list,
            [
                call("core", "_score"),
                call("vizard", "scatterplot_2d"),
                call("metadata", "tabulate"),
            ],
        )
        score_action.assert_called_once_with(
            table=self.table,
            min_rel_abundance=0.01,
            mean_abundance_on_presence=True,
            offset=1e-3,
        )
        scatterplot_action.assert_called_once_with(
            metadata=metadata,
            x_measure="mean_abundance",
            y_measure="prevalence",
            color_by="core_score",
        )
        tabulate_action.assert_called_once_with(input=metadata)
        mock_context.make_report.assert_called_once_with(
            matryoshka_template,
            {
                "Scatterplot": scatterplot_visualization,
                "Core scores": table_visualization,
            },
        )

    def test_score_pipeline_integration(self):
        table = Artifact.import_data("FeatureTable[RelativeFrequency]", self.table)

        result = score_pipeline(
            table=table,
            min_rel_abundance=0.01,
            mean_abundance_on_presence=True,
            offset=1e-3,
        )

        expected = _score(
            self.table,
            min_rel_abundance=0.01,
            mean_abundance_on_presence=True,
            offset=1e-3,
        )
        observed = result.core_scores.view(Metadata).to_dataframe()
        pdt.assert_frame_equal(observed, expected)
        self.assertEqual(repr(result.visualization.type), "Visualization")
        result.visualization.export_data(self.temp_dir.name)
        report_dir = Path(self.temp_dir.name)
        self.assertTrue((report_dir / "index.html").exists())
        index = json.loads((report_dir / "subfigures" / "index.json").read_text())
        self.assertEqual(set(index), {"Scatterplot", "Core scores"})
        self.assertTrue((report_dir / index["Scatterplot"]["index"]).is_file())
        self.assertTrue((report_dir / index["Core scores"]["index"]).is_file())
