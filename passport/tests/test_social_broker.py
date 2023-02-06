# -*- coding: utf-8 -*-
import json
import unittest

from mock import Mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.social_broker import (
    BaseSocialBrokerError,
    get_best_matching_size_avatar,
    get_max_size_avatar,
    SocialBroker,
    SocialBrokerInvalidPkceVerifierError,
    SocialBrokerProfileNotAllowedError,
    SocialBrokerRequestError,
    SocialBrokerTemporaryError,
)
from passport.backend.core.builders.social_broker.faker.social_broker import (
    bind_phonish_account_by_track_v2_ok_response,
    check_pkce_ok_response,
    FakeSocialBroker,
    social_broker_error_response,
    social_broker_v2_error_response,
)
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_TRACK_ID1,
    TEST_UID1,
    TEST_UID2,
    TEST_USER_IP1,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.ip.ip import IP
from passport.backend.core.useragent.sync import (
    RequestError,
    UserAgent,
)


response_task_normal = '''{
  "provider_id": "5",
  "application_id": "52",
  "app_name": "google-oauth2",
  "requested_scope": "https://www.googleapis.com/auth/userinfo.profile,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/plus.login",
  "retpath": "https://flider.passportdev.yandex.ru/callback?consumer=dev&track_id=423ddbbad0422428ce81e193f51d9b747f",
  "yandexuid": "1272660251379517491",
  "final_timestamp": "1380194218.01",
  "consumer_id": "95",
  "frontend_url": "https://socialdev-1.yandex.ru/broker2/",
  "provider_code": "gg",
  "task_id": "87a34cb5c9d9478593b9df14f1212aab",
  "created": "1380194217.17",
  "access_token": {
    "expires": 1380183417.0,
    "value": "ya29.AHES6ZSwwT17bSwREvwodzvwawV33F22SfvSfcugFbonPRspy000000"
  },
  "hostname": "socialdev-1.yandex.ru",
  "place": "None",
  "profile": {
    "username": "username",
    "firstname": "Anton",
    "lastname": "Kirilenko",
    "email": "user@gmail.com",
    "birthday": null,
    "gender": "m",
    "id": "112913562853868300000"
  },
  "tld": "ru",
  "scope": "[]"
}
'''


task_by_token_args = ('fb', 'facebook', 'consumer', 'token', 'secret', 'scope')


@with_settings(SOCIAL_BROKER_URL='http://none.yandex.ru/brokerapi/', SOCIAL_BROKER_RETRIES=2, SOCIAL_BROKER_TIMEOUT=1)
class TestSocialBroker(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'social_broker',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.useragent = UserAgent()
        self.response = Mock()
        self.useragent.request = Mock(return_value=self.response)
        self.social_broker = SocialBroker(useragent=self.useragent)

    def tearDown(self):
        del self.useragent
        del self.response
        del self.social_broker
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_get_task_by_token_ok(self):
        self.response.content = response_task_normal
        response = self.social_broker.get_task_by_token(*task_by_token_args)
        eq_(response, json.loads(response_task_normal))

    @raises(BaseSocialBrokerError)
    def test_error_response(self):
        self.useragent.request.side_effect = RequestError('text')
        self.social_broker.get_task_by_token(*task_by_token_args)

    @raises(BaseSocialBrokerError)
    def test_get_task_data_error(self):
        self.response.content = social_broker_error_response()
        self.social_broker.get_task_by_token(*task_by_token_args)

    @raises(SocialBrokerRequestError)
    def test_invalid_json_data(self):
        self.response.content = 'not json'
        self.social_broker.get_task_by_token(*task_by_token_args)

    def test_check_pkce_ok(self):
        self.response.content = check_pkce_ok_response()
        response = self.social_broker.check_pkce('task_id', 'verifier')
        eq_(response, json.loads(check_pkce_ok_response()))

    @raises(SocialBrokerInvalidPkceVerifierError)
    def test_check_pkce_error(self):
        self.response.content = social_broker_error_response(code='PkceVerifierInvalidError')
        self.social_broker.check_pkce('task_id', 'verifier')

    @raises(ValueError)
    def test_check_pkce_bad_args(self):
        self.social_broker.check_pkce(None, 'verifier')

    def test_error_response_parsing(self):
        for code in [
            'InternalError',
            'DatabaseFailedError',
            'CommunicationFailedError',
            'RateLimitExceededError',
        ]:
            with assert_raises(SocialBrokerTemporaryError):
                self.social_broker.check_response_for_errors(
                    json.loads(social_broker_error_response(code=code)),
                    Mock(),
                )

        for code in ['UserDeniedError', 'ApplicationUnknownError']:
            try:
                self.social_broker.check_response_for_errors(
                    json.loads(social_broker_error_response(code=code)),
                    Mock(),
                )
            except Exception as ex:
                ok_(isinstance(ex, BaseSocialBrokerError))
                ok_(not isinstance(ex, SocialBrokerTemporaryError))

    def test_retries_after_network_error(self):

        def _temporary_request_method(method, url, counter=[0], **kwargs):
            counter[0] += 1
            if counter[0] == 1:
                raise RequestError()
            else:
                return Mock(content=response_task_normal)

        self.useragent.request.side_effect = _temporary_request_method
        response = self.social_broker.get_task_by_token(*task_by_token_args)
        eq_(response, json.loads(response_task_normal))

    def test_no_retries_after_logical_error(self):
        def _temporary_request_method(method, url, counter=[0], **kwargs):
            counter[0] += 1
            if counter[0] == 1:
                return Mock(content=social_broker_error_response(code='ApplicationUnknownError'))
            else:
                return Mock(content=response_task_normal)

        self.useragent.request.side_effect = _temporary_request_method
        try:
            self.social_broker.get_task_by_token(*task_by_token_args)
        except Exception as ex:
            ok_(isinstance(ex, BaseSocialBrokerError))
            ok_(not isinstance(ex, SocialBrokerTemporaryError))

    def test_get_max_size_avatar(self):
        test_data = [
            [
                {'50x0': 'url1'},
                'url1',
            ],
            [
                {'50x0': 'url1', '100x0': 'url2'},
                'url2',
            ],
            [
                {'0x50': 'url1', '40x0': 'url2'},
                'url1',
            ],
            [
                {'0x0': 'url1', '50x0': 'url2'},
                'url2',
            ],
            [
                {'50x50': 'url1', '100x100': 'url2'},
                'url2',
            ],
            [
                {'100x50': 'url1', '60x100': 'url2'},
                'url2',
            ],
            [
                {'abrakadabra': 'url1'},
                None,
            ],
            [
                {'abrakadabra': 'url1', '50x50': 'url2'},
                'url2',
            ],
            [
                {'100X0': 'url1', '50x0': 'url2'},
                'url1',
            ],
            [
                {'10x10x10': 'url1'},
                None,
            ],
        ]

        for avatars, expected_url in test_data:
            url = get_max_size_avatar(avatars)
            eq_(url, expected_url, [url, expected_url, avatars])

    def test_get_best_matching_size_avatar(self):
        test_data = [
            [
                None,
                (100, 500),
                None,
            ],
            [
                {},
                (100, 500),
                None,
            ],
            [
                {'50x0': 'url1'},
                (100, 500),
                'url1',
            ],
            [
                {'ZxZ': 'url1'},
                (100, 500),
                'url1',
            ],
            [
                {'50x0': 'url1', '100x0': 'url2'},
                (100, 10),
                'url2',
            ],
            [  # учитывается ориентация
                {'0x50': 'url1', '40x0': 'url2'},
                (50, 0),
                'url2',
            ],
            [
                {'0x0': 'url1', '50x0': 'url2'},
                (100, 0),
                'url2',
            ],
            [  # варианты одинаково хорошо подходят
                {'50x50': 'url1', '100x100': 'url2'},
                (100, 50),
                'url1',
            ],
            [
                {'100x50': 'url1', '60x100': 'url2'},
                (81, 75),
                'url1',
            ],
            [
                {'100x50': 'url1', '60x100': 'url2', '95x75': 'url3'},
                (81, 75),
                'url3',
            ],
            [
                {'abrakadabra': 'url1', '50x50': 'url2'},
                (100, 200),
                'url2',
            ],
            [
                {'100X0': 'url1', '50x0': 'url2'},
                (100, 10),
                'url1',
            ],
            [  # всегда есть фоллбек
                {'10x10x10': 'url1'},
                (1, 2),
                'url1',
            ],
        ]

        for avatars, target_size, expected_url in test_data:
            url = get_best_matching_size_avatar(avatars, target_size)
            eq_(url, expected_url, [url, expected_url, avatars])


@with_settings(
    SOCIAL_BROKER_RETRIES=2,
    SOCIAL_BROKER_TIMEOUT=1,
    SOCIAL_BROKER_URL='https://api.social.yandex.ru/brokerapi/',
)
class TestSocialBrokerV2(PassportTestCase):
    def setUp(self):
        super(TestSocialBrokerV2, self).setUp()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'social_broker',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.fake_social_broker = FakeSocialBroker()
        self.fake_social_broker.start()
        self.social_broker = SocialBroker()

    def tearDown(self):
        self.fake_social_broker.stop()
        self.fake_tvm_credentials_manager.stop()
        super(TestSocialBrokerV2, self).tearDown()

    def test_bind_phonish_account_by_track_v2(self):
        self.fake_social_broker.set_response_side_effect(
            'bind_phonish_account_by_track_v2',
            [
                bind_phonish_account_by_track_v2_ok_response(
                    uid=TEST_UID1,
                    old=True,
                    phonish_uid=TEST_UID2,
                ),
            ],
        )

        response = self.social_broker.bind_phonish_account_by_track_v2(
            consumer=TEST_CONSUMER1,
            uid=TEST_UID1,
            track_id=TEST_TRACK_ID1,
            user_ip=IP(TEST_USER_IP1),
        )

        eq_(
            response,
            dict(
                uid=TEST_UID1,
                old=True,
                phonish_uid=TEST_UID2,
                status='ok',
            ),
        )

        self.fake_social_broker.requests[0].assert_properties_equal(
            method='POST',
            url='https://api.social.yandex.ru/brokerapi/bind_phonish_account_by_track_v2?consumer=' + TEST_CONSUMER1,
            post_args=dict(
                uid=str(TEST_UID1),
                track_id=TEST_TRACK_ID1,
            ),
            headers={
                'Ya-Consumer-Client-Ip': str(TEST_USER_IP1),
                'X-Ya-Service-Ticket': TEST_TICKET,
            },
        )

    @parameterized.expand(
        [
            ('exception.unhandled', SocialBrokerTemporaryError),
            ('internal_error', SocialBrokerTemporaryError),
            ('profile.not_allowed', SocialBrokerProfileNotAllowedError),
            ('unknown_error', BaseSocialBrokerError),
        ],
    )
    def test_errors(self, error_code, exception_cls):
        self.fake_social_broker.set_response_value(
            'bind_phonish_account_by_track_v2',
            social_broker_v2_error_response(error_code),
        )

        with self.assertRaises(exception_cls):
            self.social_broker.bind_phonish_account_by_track_v2(
                consumer=TEST_CONSUMER1,
                uid=TEST_UID1,
                track_id=TEST_TRACK_ID1,
                user_ip=IP(TEST_USER_IP1),
            )
