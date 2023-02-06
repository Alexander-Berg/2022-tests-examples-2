# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.consts import (
    TEST_CONSUMER_IP1,
    TEST_USER_AGENT1,
    TEST_USER_IP1,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants

from .base import (
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
)


class BasePhoneConfirmedCase(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/bundle/phone/is_secure_confirmed/'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
        'user_agent': TEST_USER_AGENT1,
        'user_ip': TEST_USER_IP1,
    }
    http_method = 'POST'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'phone_bundle': ['base']}),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_account_and_track_without_secure_phone(self):
        self.setup_account_without_phone()
        self.setup_track_without_phone()
        self.http_query_args = dict(track_id=self.track_id)
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_account_without_secure_phone(self):
        self.setup_account_without_phone()
        self.setup_track_with_phone()
        self.http_query_args = dict(track_id=self.track_id)
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_expired_confirmation_without_track_phone(self):
        self.setup_account_with_secure_phone(True)
        self.setup_track_without_phone()
        self.http_query_args = dict(track_id=self.track_id)
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_expired_confirmation_track_not_confirmed(self):
        self.setup_account_with_secure_phone(expired=True)
        self.setup_track_with_phone(confirmed=False)
        self.http_query_args = dict(track_id=self.track_id)
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_account_and_track_diff_secure_phone(self):
        self.setup_account_with_secure_phone(expired=True)
        self.setup_track_with_phone(number=TEST_PHONE_NUMBER1)
        self.http_query_args = dict(track_id=self.track_id)
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_account_expired_track_eq(self):
        self.setup_account_with_secure_phone(expired=True)
        self.setup_track_with_phone()
        self.http_query_args = dict(track_id=self.track_id)
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_ok_response(rv)

    def test_account_recently_confirmed(self):
        self.setup_account_with_secure_phone()
        self.setup_track_with_phone()
        self.http_query_args = dict(track_id=self.track_id)
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_ok_response(rv)

    def setup_account_without_phone(
        self,
    ):
        self.env.blackbox.set_blackbox_response_value('sessionid', blackbox_sessionid_multi_response())

    def setup_account_with_secure_phone(self, expired=False):
        confirmed = datetime.now() - timedelta(hours=4) if expired else datetime.now()
        response = blackbox_sessionid_multi_response(
                **build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    phone_confirmed=confirmed
                )
            )
        self.env.blackbox.set_blackbox_response_value('sessionid', response)

    def setup_track_with_phone(self, number=TEST_PHONE_NUMBER, confirmed=True):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = True
            track.phone_confirmation_is_confirmed = confirmed
            track.phone_confirmation_phone_number = number.e164

    def setup_track_without_phone(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = False
