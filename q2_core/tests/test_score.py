# ----------------------------------------------------------------------------
# Copyright (c) 2026, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from unittest import TestCase

import numpy as np
import pandas as pd
import pandas.testing as pdt

from q2_core import score
from q2_core.core_score import _minmax_scale


class TestScore(TestCase):
    def setUp(self):
        self.table = pd.DataFrame(
            np.array(
                [
                    [0.0, 0.005, 0.0],
                    [0.02, 0.005, 0.0],
                    [0.04, 0.005, 0.3],
                ]
            ),
            index=["S1", "S2", "S3"],
            columns=["O1", "O2", "O3"],
        )

    def test_score(self):
        observed = score(self.table)

        prevalence = np.array([2 / 3, 1, 1 / 3])
        mean_abundance = np.array([0.06 / 3, 0.005, 0.1])
        log_mean = np.log10(mean_abundance + 1e-6)
        expected = pd.DataFrame(
            {
                "core_score": (
                    _minmax_scale(prevalence, offset=1e-6)
                    * _minmax_scale(log_mean, offset=1e-6)
                )
            },
            index=pd.Index(["O1", "O2", "O3"], name="id"),
        )

        pdt.assert_frame_equal(observed, expected)

    def test_score_values_are_finite(self):
        observed = score(self.table)
        self.assertTrue(np.isfinite(observed.to_numpy()).all())

    def test_score_custom_parameters(self):
        observed = score(self.table, min_rel_abundance=0.01, offset=1e-3)

        prevalence = np.array([2 / 3, 0, 1 / 3])
        mean_abundance = np.array([0.06 / 3, 0.005, 0.1])
        log_mean = np.log10(mean_abundance + 1e-3)
        expected = pd.DataFrame(
            {
                "core_score": (
                    _minmax_scale(prevalence, offset=1e-3)
                    * _minmax_scale(log_mean, offset=1e-3)
                )
            },
            index=pd.Index(["O1", "O2", "O3"], name="id"),
        )

        pdt.assert_frame_equal(observed, expected)

    def test_score_mean_abundance_on_presence(self):
        observed = score(
            self.table, min_rel_abundance=0.01, mean_abundance_on_presence=True
        )

        prevalence = np.array([2 / 3, 0, 1 / 3])
        mean_abundance = np.array([0.03, 0, 0.3])
        log_mean = np.log10(mean_abundance + 1e-6)
        expected = pd.DataFrame(
            {
                "core_score": (
                    _minmax_scale(prevalence, offset=1e-6)
                    * _minmax_scale(log_mean, offset=1e-6)
                )
            },
            index=pd.Index(["O1", "O2", "O3"], name="id"),
        )

        pdt.assert_frame_equal(observed, expected)

    def test_minmax_scale(self):
        observed = _minmax_scale(pd.Series([2, 2, 2]), offset=1e-6)
        self.assertTrue(np.isfinite(observed.to_numpy()).all())
