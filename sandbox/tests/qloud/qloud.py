# -*- coding: utf-8 -*-

import mock
import unittest

from sandbox.projects.sandbox_ci.qloud.errors import QloudDeployFailed, QloudReadonly
from sandbox.projects.sandbox_ci.qloud.qloud import QloudApi
from sandbox.projects.sandbox_ci.tests import DotDict


def make_call_args(method='get', path='', content_type='application/json', **kwargs):
    return mock.call(
        method,
        'https://qloud.yandex-team.ru/api/' + path,
        headers={'Content-Type': content_type, 'Authorization': 'OAuth dummy'},
        verify=False,
        **kwargs
    )


class TestGetFullUrl(unittest.TestCase):
    def test_success(self):
        """Should return correct full url"""
        expected = 'https://qloud.yandex-team.ru/my-path'

        actual = QloudApi('dummy').get_full_url('my-path')

        self.assertEqual(actual, expected)


class TestUploadEnvironment(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_success(self, mock_send_request):
        """
        Should upload environment

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [
            DotDict({'status_code': 200, 'text': 'false'}),
            DotDict({'status_code': 200, 'text': 'response'}),
        ]

        actual = QloudApi('dummy').upload_environment('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='management/readonly', content_type='text/plain'),
            make_call_args(method='post', path='v1/environment/upload', data='"some_env"'),
        ])
        self.assertIsNone(actual)

    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_failure(self, mock_send_request):
        """
        Should raise AssertionError

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [
            DotDict({'status_code': 200, 'text': 'false'}),
            DotDict({'status_code': 403}),
        ]

        with self.assertRaises(AssertionError):
            QloudApi('dummy').upload_environment('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='management/readonly', content_type='text/plain'),
            make_call_args(method='post', path='v1/environment/upload', data='"some_env"'),
        ])


class TestRequestEnvironment(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_success(self, mock_send_request):
        """
        Should return environment

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [{'key': 'value'}]

        expected = {'key': 'value'}

        actual = QloudApi('dummy').request_environment('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/stable/some_env'),
        ])
        self.assertEqual(actual, expected)


class TestDumpEnvironment(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_success(self, mock_send_request):
        """
        Should return settings of environment

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'text': '{"key": "value"}'})]

        expected = {'key': 'value'}

        actual = QloudApi('dummy').dump_environment('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/dump/some_env'),
        ])
        self.assertEqual(actual, expected)

    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_failure(self, mock_send_request):
        """
        Should raise AssertionError

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 403})]

        with self.assertRaises(AssertionError):
            QloudApi('dummy').dump_environment('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/dump/some_env'),
        ])


class TestCreateDomain(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_success(self, mock_send_request):
        """
        Should create domain in the environment

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [
            DotDict({'status_code': 200, 'text': 'false'}),
            DotDict({'status_code': 204, 'text': 'response'}),
        ]

        actual = QloudApi('dummy').create_domain('some_env', {'key': 0})

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='management/readonly', content_type='text/plain'),
            make_call_args(method='put', path='v1/environment-domain/some_env?silent=true', data='{"key": 0}'),
        ])
        self.assertIsNone(actual)

    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_failure(self, mock_send_request):
        """
        Should create domain in the environment

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [
            DotDict({'status_code': 200, 'text': 'false'}),
            DotDict({'status_code': 403}),
        ]

        with self.assertRaises(AssertionError):
            QloudApi('dummy').create_domain('some_env', {'key': 0})

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='management/readonly', content_type='text/plain'),
            make_call_args(method='put', path='v1/environment-domain/some_env?silent=true', data='{"key": 0}'),
        ])


class TestGetEnvironmentStatus(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_success(self, mock_send_request):
        """
        Should upload environment

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [{'status': 'NEW'}]

        expected = {'status': 'NEW'}

        actual = QloudApi('dummy').get_environment_status('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/status/some_env'),
        ])
        self.assertEqual(actual, expected)


class TestGetEnvironmentDomains(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_success(self, mock_send_request):
        """
        Should return domains of the current environment

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'text': '[{"domainName": "domain.ru"}]'})]

        expected = [{'domainName': 'domain.ru'}]

        actual = QloudApi('dummy').get_environment_domains('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/domains/some_env'),
        ])
        self.assertEqual(actual, expected)

    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_failure(self, mock_send_request):
        """
        Should raise AssertionError

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 403})]

        with self.assertRaises(AssertionError):
            QloudApi('dummy').get_environment_domains('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/domains/some_env'),
        ])


class TestIsEnvironmentExist(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_true(self, mock_send_request):
        """
        Should return True if environment is exist

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'status': 'NEW'})]

        actual = QloudApi('dummy').is_environment_exist('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/status/some_env'),
        ])
        self.assertTrue(actual)

    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_false(self, mock_send_request):
        """
        Should return False if environment is not exist

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 403, 'status': 'NEW'})]

        actual = QloudApi('dummy').is_environment_exist('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/status/some_env'),
        ])
        self.assertFalse(actual)


class TestGetEnvironment(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_success(self, mock_send_request):
        """
        Should return information about environment

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'text': '{"key": "value"}'})]

        expected = {'key': 'value'}

        actual = QloudApi('dummy').get_environment('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/stable/some_env'),
        ])
        self.assertEqual(actual, expected)


class TestIsEnvironmentDeployed(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_forbidded(self, mock_send_request):
        """
        Should return False if response code is forbidded (403)

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 403})]

        actual = QloudApi('dummy').is_environment_deployed('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/status/some_env'),
        ])
        self.assertFalse(actual)

    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_raise(self, mock_send_request):
        """
        Should raise Exception

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'text': '{"status": "TEMPLATE"}'})]

        with self.assertRaises(QloudDeployFailed):
            QloudApi('dummy').is_environment_deployed('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/status/some_env'),
        ])

    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_success(self, mock_send_request):
        """
        Should return True

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'text': '{"status": "DEPLOYED"}'})]

        actual = QloudApi('dummy').is_environment_deployed('some_env')

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='v1/environment/status/some_env'),
        ])
        self.assertTrue(actual)


class TestIsInReadonly(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_true(self, mock_send_request):
        """
        Should return True if Qloud in readonly mode

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'text': 'true'})]

        actual = QloudApi('dummy').is_in_readonly()

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='management/readonly', content_type='text/plain'),
        ])
        self.assertTrue(actual)

    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_false(self, mock_send_request):
        """
        Should return False if Qloud not in readonly mode

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'text': 'false'})]

        actual = QloudApi('dummy').is_in_readonly()

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='management/readonly', content_type='text/plain'),
        ])
        self.assertFalse(actual)


class TestCheckNotReadonly(unittest.TestCase):
    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_success(self, mock_send_request):
        """
        Should return None if Qloud not in readonly mode

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'text': 'false'})]

        actual = QloudApi('dummy').check_not_readonly()

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='management/readonly', content_type='text/plain'),
        ])
        self.assertIsNone(actual)

    @mock.patch('sandbox.projects.sandbox_ci.qloud.qloud.send_request')
    def test_failure(self, mock_send_request):
        """
        Should raise QloudDeployFailed error

        :type mock_send_request: mock.Mock
        """
        mock_send_request.side_effect = [DotDict({'status_code': 200, 'text': 'true'})]

        with self.assertRaises(QloudReadonly):
            QloudApi('dummy').check_not_readonly()

        self.assertSequenceEqual(mock_send_request.call_args_list, [
            make_call_args(path='management/readonly', content_type='text/plain'),
        ])
