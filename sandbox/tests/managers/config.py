# -*- coding: utf-8 -*-
import unittest

from sandbox.projects.sandbox_ci.managers import ConfigManager
from sandbox.projects.sandbox_ci.managers.config import deep_get


def get_test_conf():
    return {
        '*': {
            '*': {
                'deploy': {'static': False},
                'environ': {'TMPL_ENGINE': 'bh'},
                'github': {'report_statuses': False},
            },
            'dev': {'environ': {'YENV': 'production'}, 'deploy': {'static': True}},
            'pull-request': {'environ': {'YENV': 'testing'}},
        },
        'fiji': {
            '*': {'environ': None},
            'dev': {'deploy': {'kitty': True}},
        },
        'web4': {
            '*': {
                'environ': {'TMPL_ENGINE': 'bemhtml'}
            },
            'dev': {'environ': {'YCONFIG': 'pre-production'}},
        }
    }


class Task:

    project_conf = {
        'deploy': {
            'yappy': {
                'enabled': True
            }
        }
    }


class TestsGetProjectConf(unittest.TestCase):
    def test_project_asterisk(self):
        """
        Should return value from project's asterisk level
        """
        expect = 'bemhtml'

        result = ConfigManager.get_project_conf(get_test_conf(), {'project_name': 'web4'})
        actual = result.get('environ').get('TMPL_ENGINE')

        self.assertEqual(actual, expect)

    def test_project_not_exist(self):
        """
        Should work with project which not exist in config
        """
        expect = {
            'deploy': {'static': False, },
            'environ': {'TMPL_ENGINE': 'bh'},
            'github': {'report_statuses': False},
        }

        actual = ConfigManager.get_project_conf(get_test_conf(), {'project_name': 'web666'})

        self.assertDictEqual(actual, expect)

    def test_build_context(self):
        """
        Should return conf merged with build context level
        """
        expect = {
            'deploy': {'static': True, 'kitty': True},
            'environ': {'TMPL_ENGINE': 'bh', 'YENV': 'production'},
            'github': {'report_statuses': False},
        }

        actual = ConfigManager.get_project_conf(get_test_conf(), {'project_name': 'fiji', 'build_context': 'dev'})

        self.assertDictEqual(actual, expect)

    def test_correct_with_none(self):
        """
        Should use empty dictionary instead of None if vars group are empty
        """
        expect = {
            'deploy': {'static': False},
            'environ': {'TMPL_ENGINE': 'bh'},
            'github': {'report_statuses': False},
        }

        actual = ConfigManager.get_project_conf(get_test_conf(), {'project_name': 'fiji'})

        self.assertEqual(actual, expect)


class TestsDeepGet(unittest.TestCase):
    def test_get_value(self):
        """
        Should return value
        """
        expect = {
            '*': {'environ': None},
            'dev': {'deploy': {'kitty': True}},
        }

        actual = deep_get(get_test_conf(), ['fiji'])

        self.assertDictEqual(actual, expect)

    def test_get_nested_value(self):
        """
        Should return value by given path
        """
        expect = False

        actual = deep_get(get_test_conf(), ['*', '*', 'deploy', 'static'])

        self.assertEqual(actual, expect)

    def test_default_value(self):
        """
        Should return None if default value is not given
        """
        actual = deep_get(get_test_conf(), ['*', 'nonexist'])

        self.assertIsNone(actual)

    def test_given_default_value(self):
        """
        Should return given default value
        """
        expect = 123

        actual = deep_get(get_test_conf(), ['*', 'nonexist'], 123)

        self.assertEqual(actual, expect)


class Test(unittest.TestCase):
    def test_config_value(self):
        task = Task()
        manager = ConfigManager(task)

        actual = manager.get_deep_value(['deploy', 'yappy', 'enabled'])

        self.assertTrue(actual)

    def test_nested_config(self):
        task = Task()
        manager = ConfigManager(task)

        expect = {'enabled': True}

        actual = manager.get_deep_value(['deploy', 'yappy'])

        self.assertDictEqual(actual, expect)

    def test_default_value(self):
        task = Task()
        manager = ConfigManager(task)

        actual = manager.get_deep_value(['deploy', 'yappy', 'unexisting'])

        self.assertIsNone(actual)

    def test_given_default_value(self):
        task = Task()
        manager = ConfigManager(task)

        actual = manager.get_deep_value(['deploy', 'yappy', 'unexisting'], False)

        self.assertFalse(actual)
