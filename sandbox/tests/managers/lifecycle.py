# -*- coding: utf-8 -*-

import unittest

from sandbox.projects.sandbox_ci.managers import LifecycleManager


class TestUpdateVars(unittest.TestCase):
    lifecylce = LifecycleManager(
        task=None,
        steps=[],
        project_dir='project_dir',
        variables={},
    )

    def test_success(self):
        expected = {
            'unicode': '\xd0\xb7\xd0\xbd\xd0\xb0\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5',
            'string': 'value',
            'number': 1,
            'float': 1.0,
        }

        self.lifecylce.update_vars(**{'unicode': u'значение', 'string': 'value', 'number': 1, 'float': 1.0})

        self.assertDictEqual(self.lifecylce.vars, expected)


class TestFormatCommand(unittest.TestCase):
    lifecylce = LifecycleManager(
        task=None,
        steps=[],
        project_dir='project_dir',
        variables={
            'unicode': u'значение',
            'string': 'value',
            'number': 1,
            'float': 1.0,
        },
    )

    def test_success(self):
        expected = 'I want see \xd0\xb7\xd0\xbd\xd0\xb0\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5, value, 1 and 1.0.'

        actual = self.lifecylce.format_command('I want see {unicode}, {string}, {number} and {float}.')

        self.assertEqual(actual, expected)
