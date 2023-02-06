# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from mock import Mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.social.broker.error_handler import process_error
from passport.backend.social.broker.exceptions import (
    DatabaseFailedError,
    RateLimitExceededError,
    SessionInvalidError,
    SocialBrokerError,
)
from passport.backend.social.broker.handlers.base import Handler
from passport.backend.social.broker.test import TestCase
from passport.backend.social.broker.tests.base_broker_test_data import (
    TEST_FRONTEND_URL,
    TEST_PROVIDER,
    TEST_TASK_ID,
)
from passport.backend.social.common import exception as common_exceptions
from passport.backend.social.common.exception import (
    BasicProxylibError,
    ProviderCommunicationProxylibError,
    ProviderRateLimitExceededProxylibError,
)
from passport.backend.social.common.task import Task


def execute_with_args(exc_class, error_code=None, exc_message='hello'):
    retry_url = 'http://some.url.ru/path?get=get'
    exc = exc_class(exc_message)

    request = Mock()
    request.host = 'socialdev-1.yandex.ru'
    request.args = {}
    request.id = 'request-id'
    handler = Handler(request)
    handler.method_name = 'test_method'
    handler.task = Task()
    handler.task.start_args = dict(foo='bar')
    handler.processed_args = {
        'retry_url': retry_url,
        'provider': TEST_PROVIDER,
        'frontend_url': TEST_FRONTEND_URL,
    }
    handler.task_id = TEST_TASK_ID
    handler.task.dump_session_data = Mock(return_value={'key': 'val'})

    try:
        # Для правдоподобия сперва выбрасываем исключение, чтобы подготовить
        # sys.exc_info.
        raise exc
    except exc_class:
        response = process_error(exc, handler)

    data = json.loads(response.data)
    eq_(data['retry_url'], retry_url)
    ok_('error' in data)
    eq_(len(data['cookies']), 1)
    eq_(data['provider'], TEST_PROVIDER)

    if isinstance(exc_class(), (SocialBrokerError, BasicProxylibError)):
        eq_(data['error']['code'], error_code or exc_class.error_code)
        eq_(data['error']['message'], exc_message)
    else:
        eq_(data['error']['code'], error_code)

        try:
            exception_str = unicode(exc)
        except UnicodeEncodeError:
            exception_str = str(exc)
        eq_(data['error']['message'], exception_str)


class TestErrorHandler(TestCase):
    def test_basic_exception(self):
        execute_with_args(Exception, 'InternalError', exc_message='some_message')

    def test_non_ascii_decoded_basic_exception(self):
        execute_with_args(Exception, 'InternalError', exc_message='уменяощущение')

    def test_session_invalid(self):
        execute_with_args(SessionInvalidError, 'SessionInvalidError')

    def test_provider_error(self):
        execute_with_args(ProviderCommunicationProxylibError, 'CommunicationFailedError')

    def test_rate_limit_error(self):
        execute_with_args(RateLimitExceededError, 'RateLimitExceededError')

    def test_basic_proxylib_error_error(self):
        execute_with_args(BasicProxylibError, 'InternalError')

    def test_non_ascii_decoded_error(self):
        # Все производимые Социализмом исключения должны быть декодированы.
        execute_with_args(SocialBrokerError, exc_message='Ошибка')

    def test_provider_rate_limit_exceeded_proxylib_error(self):
        execute_with_args(ProviderRateLimitExceededProxylibError, 'RateLimitExceededError')

    def test_database_failed_error(self):
        execute_with_args(DatabaseFailedError, 'DatabaseFailedError', '')

    def test_database_error(self):
        execute_with_args(common_exceptions.DatabaseError, 'DatabaseFailedError', '')


class TestAppErrorHandler(TestCase):
    def test_page_not_found_error(self):
        r = self._client.open(path='/404')
        self.assertEqual(r.status_code, 404)
        self.assertDictEqual(
            json.loads(r.data),
            {
                'error': {
                    'code': 'PageNotFound',
                    'message': 'Page not found',
                },
                'request_id': 'request-id-1',
            }
        )

    def test_unhandled_exception_error(self):
        def unknown_handler():
            raise Exception('Unhandled exception')

        self._app.add_url_rule('/500', methods=['GET'], view_func=unknown_handler)

        r = self._client.open(path='/500')
        self.assertEqual(r.status_code, 500)
        self.assertDictEqual(
            json.loads(r.data),
            {
                'error': {
                    'code': 'InternalError',
                    'message': '',
                },
                'request_id': 'request-id-1',
            }
        )
