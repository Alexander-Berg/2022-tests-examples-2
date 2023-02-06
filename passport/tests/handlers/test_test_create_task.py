# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.broker.test import TestCase
from passport.backend.social.broker.tests.base import TimeNow
from passport.backend.social.broker.tests.base_broker_test_data import TEST_PROVIDER
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.task import (
    load_task_from_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER_IP1,
    EMAIL1,
    FACEBOOK_APPLICATION_NAME1,
    REFRESH_TOKEN1,
    TASK_ID1,
    UID1,
    UNIXTIME1,
    USERNAME1,
)


_TEST_UNKNOWN_APPLICATION_NAME = 'fake_application'
_TOKEN_SCOPE = 'scope1,scope2,scope3'
_TOKEN_INVALID_SCOPE = '   ,, ,, '
_TOKEN_VALUE = 'abcdef'
_TOKEN_EXPIRED = UNIXTIME1


class TestTestCreateTask(TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/test/create_task'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
    }
    REQUEST_DATA = {
        'consumer': CONSUMER1,
        'application_name': FACEBOOK_APPLICATION_NAME1,
        'token_value': _TOKEN_VALUE,
        'token_scope': _TOKEN_SCOPE,
        'token_expired': _TOKEN_EXPIRED,
        'profile_userid': UID1,
        'profile_username': USERNAME1,
        'profile_email': EMAIL1,
        'refresh_token_value': REFRESH_TOKEN1,
    }

    def setUp(self):
        super(TestTestCreateTask, self).setUp()
        providers.init()

    def _setup_environment(self):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['test_create_task'],
        )

    def _build_task(self,
                    application_name=FACEBOOK_APPLICATION_NAME1,
                    task_id=TASK_ID1,
                    consumer=CONSUMER1,
                    token_value=_TOKEN_VALUE,
                    token_scope=_TOKEN_SCOPE,
                    token_expired=_TOKEN_EXPIRED,
                    profile_userid=UID1,
                    profile_username=USERNAME1,
                    profile_email=EMAIL1,
                    provider=TEST_PROVIDER,
                    refresh_token_value=REFRESH_TOKEN1):
        task = Task()
        task.task_id = task_id
        task.consumer = consumer
        task.application = providers.get_application_by_name(application_name)
        task.created = TimeNow()
        task.finished = TimeNow()
        task.provider = provider
        task.in_redis = True

        task.access_token = dict(
            value=token_value,
            expires=token_expired,
            scope=token_scope,
            secret=None,
            refresh=refresh_token_value,
        )
        task.profile = dict(
            userid=str(profile_userid),
            username=profile_username,
            email=profile_email,
        )
        return task

    def _assert_task_equals(self, expected):
        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertEqual(task.to_json_dict(), expected.to_json_dict())

    def test_ok(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(
            rv,
            response={'task_id': TASK_ID1},
        )
        self._assert_task_equals(self._build_task())

    def test_unknown_application_error(self):
        self._setup_environment()
        rv = self._make_request(
            data={'application_name': _TEST_UNKNOWN_APPLICATION_NAME}
        )
        self._assert_error_response(rv, ['application.unknown'])

    def test_form_required_fields_error(self):
        self._setup_environment()
        rv = self._make_request(
            exclude_data=[
                'application_name',
                'token_value',
                'token_expired',
                'token_scope',
                'profile_userid',
            ],
        )
        self._assert_error_response(
            rv,
            [
                'application_name.empty',
                'token_value.empty',
                'token_expired.empty',
                'profile_userid.empty',
                'token_scope.empty',
            ],
        )

    def test_form_optional_fields_ok(self):
        self._setup_environment()
        rv = self._make_request(
            exclude_data=[
                'profile_username',
                'profile_email',
                'refresh_token_value',
            ],
        )
        self._assert_ok_response(
            rv,
            response={'task_id': TASK_ID1},
        )
        self._assert_task_equals(self._build_task(
            profile_username=None,
            profile_email=None,
            refresh_token_value=None,
        ))

    def test_form_invalid_scope_error(self):
        self._setup_environment()
        rv = self._make_request(
            data={'token_scope': _TOKEN_INVALID_SCOPE},
        )
        self._assert_error_response(
            rv,
            ['token_scope.invalid']
        )
