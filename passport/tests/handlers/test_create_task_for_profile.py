# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import abc

from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response_multiple
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_invalid_user_ticket,
    fake_user_ticket,
)
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.chrono import now
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Google import Google
from passport.backend.social.common.redis_client import get_redis
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.refresh_token.utils import save_refresh_token
from passport.backend.social.common.task import (
    load_task_from_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_ID2,
    APPLICATION_NAME1,
    APPLICATION_NAME2,
    APPLICATION_TOKEN1,
    CONSUMER1,
    CONSUMER2,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    TASK_ID1,
    UID1,
    USER_IP1,
    USER_TICKET1,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import save_token
from passport.backend.social.proxylib.test import google as google_test


class IBlackboxResponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def kwargs(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass


class UserinfoBlackboxResponse(IBlackboxResponse):
    def __init__(self):
        self._kwargs = dict()

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        pass


class BaseCreateTaskForProfileTestEnv(object):
    __metaclass__ = abc.ABCMeta

    def setup(self):
        self.setup_user_ticket()
        self.setup_blackbox_userinfo_response()
        self.setup_provider_profile_response()
        self.setup_token()
        self.setup_refresh_token()
        self.setup_provider_refresh_token_response()

    @abc.abstractmethod
    def setup_user_ticket(self):
        pass

    @abc.abstractmethod
    def setup_blackbox_userinfo_response(self):
        pass

    @abc.abstractmethod
    def setup_provider_profile_response(self):
        pass

    @abc.abstractmethod
    def setup_token(self):
        pass

    @abc.abstractmethod
    def setup_refresh_token(self):
        pass

    @abc.abstractmethod
    def setup_provider_refresh_token_response(self):
        pass


class CreateTaskForProfileTestEnv(BaseCreateTaskForProfileTestEnv):
    def __init__(self, env_subjects):
        self.env_subjects = env_subjects
        self.user_ticket = fake_user_ticket(UID1)
        self.token = self.build_token()
        self.refresh_token = self.build_refresh_token()

    def setup_user_ticket(self):
        self.env_subjects.fake_tvm_ticket_checker.set_check_user_ticket_side_effect([self.user_ticket])

    def setup_blackbox_userinfo_response(self):
        self.env_subjects.fake_blackbox.set_response_side_effect('userinfo', [
            blackbox_userinfo_response_multiple([dict(uid=UID1)]),
        ])

    def setup_provider_profile_response(self):
        self.env_subjects.fake_google.set_response_value('get_profile', google_test.GoogleApi.get_profile())

    def setup_token(self):
        save_token(self.token, self.env_subjects.db)
        self.refresh_token.token_id = self.token.token_id

    def setup_refresh_token(self):
        save_refresh_token(self.refresh_token, self.env_subjects.db)

    def setup_provider_refresh_token_response(self):
        self.env_subjects.fake_google.set_response_value('refresh_token', google_test.GoogleApi.refresh_token())

    def build_token(self):
        app = providers.get_application_by_name(APPLICATION_NAME1)
        return Token(
            application_id=app.identifier,
            application=app,
            uid=UID1,
            value=APPLICATION_TOKEN1,
        )

    def build_refresh_token(self):
        return RefreshToken(
            value=APPLICATION_TOKEN1,
        )


class EnvSubjects(object):
    def __init__(
        self,
        fake_tvm_ticket_checker,
        fake_blackbox,
        fake_google,
        db,
    ):
        self.fake_tvm_ticket_checker = fake_tvm_ticket_checker
        self.fake_blackbox = fake_blackbox
        self.fake_google = fake_google
        self.db = db


class BaseCreateTaskForProfile(TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/create_task_for_profile'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'X-Ya-User-Ticket': USER_TICKET1,
        'Ya-Consumer-Client-Ip': USER_IP1,
    }
    REQUEST_DATA = dict(
        application_name=APPLICATION_NAME1,
        consumer=CONSUMER1,
        task_consumer=CONSUMER2,
    )

    def setUp(self):
        super(BaseCreateTaskForProfile, self).setUp()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['create-task-for-profile'],
        )

        self.fake_google = google_test.FakeProxy()
        self.fake_google.start()

    def tearDown(self):
        self.fake_google.stop()
        super(BaseCreateTaskForProfile, self).tearDown()

    def build_create_task_for_profile_ok_response(self):
        return dict(task_id=TASK_ID1)

    def build_env_subjects(self):
        return EnvSubjects(
            fake_tvm_ticket_checker=self.fake_tvm_ticket_checker,
            fake_blackbox=self._fake_blackbox,
            fake_google=self.fake_google,
            db=self._fake_db.get_engine(),
        )


class TestCreateTaskForProfile(BaseCreateTaskForProfile):
    def setUp(self):
        super(TestCreateTaskForProfile, self).setUp()

        self.test_env = CreateTaskForProfileTestEnv(self.build_env_subjects())

    def build_settings(self):
        settings = super(TestCreateTaskForProfile, self).build_settings()
        settings.update(
            applications=[
                dict(
                    application_id=APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    provider_id=Google.id,
                    request_from_intranet_allowed=True,
                ),
                dict(
                    application_id=APPLICATION_ID2,
                    application_name=APPLICATION_NAME2,
                    provider_client_id=EXTERNAL_APPLICATION_ID2,
                    provider_id=Google.id,
                    request_from_intranet_allowed=True,
                ),
            ],
        )
        return settings

    def test_ok(self):
        self.test_env.setup()

        rv = self._make_request()

        self._assert_ok_response(rv, self.build_create_task_for_profile_ok_response())

        task = Task()
        task.access_token = self.test_env.token.to_dict_for_proxy()
        task.application = self.test_env.token.application
        task.consumer = CONSUMER2
        task.in_redis = True
        task.profile = google_test.SocialUserinfo.default().as_dict()
        task.provider = self.test_env.token.application.provider
        task.created = task.finished = now.f()
        task.task_id = TASK_ID1
        task.uid = UID1

        assert load_task_from_redis(get_redis(), TASK_ID1).to_json_dict() == task.to_json_dict()

    def test_application_not_found(self):
        self.test_env.setup()

        rv = self._make_request(data=dict(application_name='unknown'))

        self._assert_error_response(rv, ['provider_token.not_found'])

    def test_invalid_user_ticket(self):
        self.test_env.user_ticket = fake_invalid_user_ticket()
        self.test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['user_ticket.invalid'])

    def test_provider_token_not_found(self):
        app = providers.get_application_by_name(APPLICATION_NAME2)
        self.test_env.token.application_id = app.identifier
        self.test_env.token.application = app

        self.test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['provider_token.not_found'])

    def test_super_scope(self):
        self.test_env.token.scopes = ['foo', 'bar']
        self.test_env.setup()

        rv = self._make_request(data=dict(scope='foo'))

        self._assert_ok_response(rv, self.build_create_task_for_profile_ok_response())

    def test_equal_scope(self):
        self.test_env.token.scopes = ['foo', 'bar']
        self.test_env.setup()

        rv = self._make_request(data=dict(scope='bar foo'))

        self._assert_ok_response(rv, self.build_create_task_for_profile_ok_response())

    def test_sub_scope(self):
        self.test_env.token.scopes = ['foo']
        self.test_env.setup()

        rv = self._make_request(data=dict(scope='bar foo'))

        self._assert_error_response(rv, ['provider_token.not_found'])

    def test_token_expired_has_refresh_token(self):
        self.test_env.token.expired = now()

        self.test_env.setup()

        rv = self._make_request()

        self._assert_ok_response(rv, self.build_create_task_for_profile_ok_response())

    def test_token_expired_no_refresh_token(self):
        self.test_env.token.expired = now()
        self.test_env.setup_refresh_token = lambda: None

        self.test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['provider_token.not_found'])


class TestApplicationAllowedScopeCreateTaskForProfile(BaseCreateTaskForProfile):
    def setUp(self):
        super(TestApplicationAllowedScopeCreateTaskForProfile, self).setUp()

        self.test_env = CreateTaskForProfileTestEnv(self.build_env_subjects())

    def build_settings(self):
        settings = super(TestApplicationAllowedScopeCreateTaskForProfile, self).build_settings()
        settings.update(
            applications=[
                dict(
                    allowed_scope='foo bar',
                    application_id=APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    provider_id=Google.id,
                    request_from_intranet_allowed=True,
                ),
            ],
        )
        return settings

    def test_token_with_allowed_scope_found(self):
        self.test_env.token.scopes = ['foo', 'bar']
        self.test_env.setup()

        rv = self._make_request()

        self._assert_ok_response(rv, self.build_create_task_for_profile_ok_response())

    def test_token_with_allowed_scope_not_found(self):
        self.test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['provider_token.not_found'])
