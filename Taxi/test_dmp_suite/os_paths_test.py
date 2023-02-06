# coding: utf-8
from unittest import TestCase
from dmp_suite.exceptions import ConfigError
import mock
import os

from taxidwh_settings import DictSettingsSource, StringToTupleSourceProxy
from dmp_suite.os_paths import get_custom_data_path


def mock_settings(test_data):
    return mock.patch(
        'dmp_suite.os_paths.settings',
        new=StringToTupleSourceProxy(
            DictSettingsSource(test_data)
        )
    )


class OsPathsTest(TestCase):

    def test_get_custom_data_path(self):
        with mock_settings({'system': {'data_path': '~/tmp'}}), \
                mock.patch('os.path.exists', return_value=True):
            self.assertEquals(
                get_custom_data_path(),
                os.path.expanduser('~/tmp')
            )

        with mock_settings({'system': {'data_path': '~/tmp'}}), \
                mock.patch('os.path.exists', return_value=True):
            self.assertEquals(
                get_custom_data_path('test'),
                os.path.expanduser('~/tmp/test')
            )

        with mock_settings({'system': {'data_path': 'tmp'}}), \
                mock.patch('os.path.exists', return_value=True):
            self.assertRaises(ConfigError, get_custom_data_path, 'test')

        with mock_settings({'system': {'data_path': '.tmp'}}), \
                mock.patch('os.path.exists', return_value=True):
            self.assertRaises(ConfigError, get_custom_data_path, 'test')

        with mock_settings({'system': {'data_path': './tmp'}}), \
                mock.patch('os.path.exists', return_value=True):
            self.assertRaises(ConfigError, get_custom_data_path, 'test')
