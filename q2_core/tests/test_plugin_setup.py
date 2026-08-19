# ----------------------------------------------------------------------------
# Copyright (c) 2026, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from unittest import TestCase

from q2_core.plugin_setup import plugin


class PluginTests(TestCase):
    def test_plugin(self):
        self.assertEqual(plugin.name, "core")

    def test_score_is_registered(self):
        self.assertIn("score", plugin.methods)
