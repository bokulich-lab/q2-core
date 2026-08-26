# ----------------------------------------------------------------------------
# Copyright (c) 2026, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import numpy as np
import pandas as pd
import pandas.testing as pdt
from rachis.plugin.testing import TestPluginBase

from q2_core import score
from q2_core.core_score import _minmax_scale


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
        observed = score(self.table)

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
        observed = score(self.table, min_rel_abundance=0.01, offset=1e-3)

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
        observed = score(
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
