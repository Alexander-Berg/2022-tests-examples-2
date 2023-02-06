import pytest
from unittest import mock, TestCase
from requests import HTTPError, ConnectionError

from demand_etl.layer.yt.cdm.user_survey.fct_survey_answer.wrk.translation_result.loader import translate_to_en

import json
from requests.models import Response


TEST_KWARGS = {
    'lang': 'ru',
    'text': ['## Мой текст ']
}
TEST_RESPONSE = '## my text '


class MockServer:
    def __init__(self, limit=0, **kwargs):
        self._n_calls = 0
        self._limit = limit
        self._fail_connection = kwargs.get('fail_connection')
        self._fail_http = kwargs.get('fail_http')

    def __call__(self, *args, **kwargs):
        if self._n_calls == self._limit:
            result = self._mocked_request_get_ok(*args, **kwargs)
        else:
            if self._fail_connection:
                result = self._mocked_request_get_bad_connection(*args, **kwargs)
            elif self._fail_http:
                result = self._mocked_request_get_bad_http(*args, **kwargs)
            else:
                result = self._mocked_request_get_bad_response(*args, **kwargs)
        self._n_calls += 1
        return result

    @staticmethod
    def _mocked_request_get_ok(*args, **kwargs):
        params = kwargs['params']
        response_content = {
            'code': 200,
            'lang': params['lang'],
            'text': [TEST_RESPONSE]
        }

        response = Response()
        response.status_code = 200
        response._content = str.encode(json.dumps(response_content))
        return response

    @staticmethod
    def _mocked_request_get_bad_response(*args, **kwargs):
        response_content = {
            'code': 429
        }
        response = Response()
        response.status_code = 429
        response._content = str.encode(json.dumps(response_content))
        return response

    @staticmethod
    def _mocked_request_get_bad_http(*args, **kwargs):
        raise HTTPError('My HTTP Error')

    @staticmethod
    def _mocked_request_get_bad_connection(*args, **kwargs):
        raise ConnectionError('My Connection Error')


class TestTranslate(TestCase):
    @mock.patch('requests.get', side_effect=MockServer())
    def test_ok(self, mock_get):
        result = translate_to_en(**TEST_KWARGS)
        self.assertEqual(result, TEST_RESPONSE)
        self.assertEqual(mock_get.call_count, 1)

    @pytest.mark.slow
    @mock.patch('requests.get', side_effect=MockServer(limit=2))
    def test_restoring(self, mock_get):
        result = translate_to_en(**TEST_KWARGS)
        self.assertEqual(result, TEST_RESPONSE)
        self.assertEqual(mock_get.call_count, 3)

    @pytest.mark.slow
    @mock.patch('requests.get', side_effect=MockServer(limit=10))
    def test_failing(self, mock_get):
        self.assertRaisesRegex(HTTPError, 'Too many requests', translate_to_en, **TEST_KWARGS)
        self.assertEqual(mock_get.call_count, 5)

    @pytest.mark.slow
    @mock.patch('requests.get', side_effect=MockServer(limit=10, fail_connection=True))
    def test_failing_connection(self, mock_get):
        self.assertRaisesRegex(ConnectionError, 'My Connection Error', translate_to_en, **TEST_KWARGS)
        self.assertEqual(mock_get.call_count, 5)

    @pytest.mark.slow
    @mock.patch('requests.get', side_effect=MockServer(limit=10, fail_http=True))
    def test_failing_http(self, mock_get):
        self.assertRaisesRegex(HTTPError, 'My HTTP Error', translate_to_en, **TEST_KWARGS)
        self.assertEqual(mock_get.call_count, 5)
