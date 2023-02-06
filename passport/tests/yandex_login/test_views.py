# -*- coding: utf-8 -*-
from datetime import datetime

from django.test.utils import override_settings
from django.urls import (
    reverse,
    reverse_lazy,
)
import jwt
import mock
from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_OAUTH_VALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    FakeBlackbox,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.oauth.api.api.yandex_login.utils import VerificationLevel
from passport.backend.oauth.core.common.utils import parse_datetime_to_unixtime
from passport.backend.oauth.core.db.eav import UPDATE
from passport.backend.oauth.core.test.base_test_data import (
    TEST_CIPHER_KEYS,
    TEST_FAKE_UUID,
    TEST_HOST,
)
from passport.backend.oauth.core.test.fake_configs import FakeScopeGrants
from passport.backend.oauth.core.test.framework import ApiTestCase
from passport.backend.oauth.core.test.utils import iter_eq


TEST_EXPIRE_DATE = '2030-01-02 03:04:05'
TEST_EXPIRE_TS = parse_datetime_to_unixtime(TEST_EXPIRE_DATE)
TEST_DEFAULT_SCOPES = ['login:info', 'login:birthday', 'login:email', 'login:avatar', 'login:full_phones', 'login:plus_subscriptions', 'login:verification_level']
TEST_META = 'meta'
TEST_CLIENT_ID = 'a' * 32
TEST_CLIENT_NAME = 'client-name'
TEST_CONTEXT_ID = 'context-id'
TEST_SCOPE_ADDENDUM = '{some-json}'
TEST_CONSUMER = 'money_yalogin_consumer'
TEST_EXPECTED_PSUID = '1.AAAAAQ.68tJ1I6kD-ksUdNjBXeq1g.VD9x8QM2UO7XrnO7dkLITQ'


@override_settings(
    PSUID_DEFAULT_VERSION=1,
    PSUID_ENCRYPTION_KEYS=TEST_CIPHER_KEYS,
    PSUID_SIGNATURE_KEYS=TEST_CIPHER_KEYS,
    PAYMENT_AUTH_INFO_FAKE_CONSUMER=TEST_CONSUMER,
)
class InfoTestCase(ApiTestCase):
    default_url = reverse_lazy('yandex_login_info')
    http_method = 'GET'

    def setUp(self):
        super(InfoTestCase, self).setUp()

        with UPDATE(self.test_client) as client:
            client.display_id = TEST_CLIENT_ID

        self.blackbox = FakeBlackbox()
        self.set_blackbox_return_value()
        self.blackbox.start()

        self.fake_grants = FakeScopeGrants()
        self.fake_grants.set_data({
            TEST_CONSUMER: {
                'grants': {
                    'api': [
                        'get_payment_auth_info',
                    ],
                },
                'networks': [
                    '0.0.0.0/0',
                    '::/0',
                ],
            },
        })
        self.fake_grants.start()

        self.expected_response = {
            'id': '123',
            'login': 'Vasya.1',
            'client_id': self.test_client.display_id,
            'display_name': 'Vasya',
            'default_avatar_id': 1234,
            'is_avatar_empty': False,
            'real_name': 'Vasya Pupkin',
            'first_name': 'Vasya',
            'last_name': 'Pupkin',
            'birthday': '1234-56-79',
            'sex': 'male',
            'default_email': 'aa@bb.cc',
            'emails': ['aa@bb.cc'],
            'phones': [
                {
                    'id': 1,
                    'number': '+79151234567',
                    'confirmed': 100,
                },
            ],
            'default_phone': {
                'id': 1,
                'number': '+79151234567',
            },
            'has_plus': True,
            'psuid': TEST_EXPECTED_PSUID,
            'verification_level': VerificationLevel.NO_VERIFIED,
        }

        self.expected_jwt_response = {
            'iat': TimeNow(),
            'jti': TEST_FAKE_UUID,
            'exp': TEST_EXPIRE_TS,
            'iss': TEST_HOST,
            'uid': 123,
            'login': 'Vasya.1',
            'name': 'Vasya Pupkin',
            'email': 'aa@bb.cc',
            'birthday': '1234-56-79',
            'gender': 'male',
            'display_name': 'Vasya',
            'avatar_id': 1234,
            'phone': {
                'id': 1,
                'number': '+79151234567',
            },
            'psuid': TEST_EXPECTED_PSUID,
        }

    def tearDown(self):
        self.blackbox.stop()
        super(InfoTestCase, self).tearDown()

    def set_blackbox_return_value(self, uid=123, status=None, scopes=None, extra_bb_keys=None, **extra_oauth_info):
        blackbox_response = dict(
            status=status or BLACKBOX_OAUTH_VALID_STATUS,
            uid=uid,
            display_name={'name': 'Vasya'},
            default_avatar_key=1234,
            subscribed_to=[4, 8, 46],
            dbfields={
                'subscription.login.8': 'Vasya.1',
            },
            attributes={
                'account.normalized_login': 'vasya-1',
                'person.firstname': 'Vasya',
                'person.lastname': 'Pupkin',
                'person.gender': 'm',
                'person.birthday': '1234-56-79',
                'subscription.37': '1',
                'account.have_plus': '1',
            },
            aliases={
                'social': 'uid-mmzxjnry',
            },
            emails=[
                {
                    'address': 'aa@bb.cc',
                    'default': True,
                    'validated': True,
                    'native': True,
                },
                {
                    'address': 'aa2@bb2.cc2',
                    'default': False,
                    'validated': True,
                    'native': False,
                },
            ],
            phones=[
                {
                    'number': '+79151234567',
                    'id': 1,
                    'bound': datetime.fromtimestamp(100),
                    'secured': datetime.fromtimestamp(101),
                    'is_default': 1,
                },
            ],
            client_id=self.test_client.display_id,
            scope=' '.join(scopes or TEST_DEFAULT_SCOPES),
            oauth_token_info=dict(
                token_id=100500,
                expire_time=TEST_EXPIRE_DATE,
                client_name=TEST_CLIENT_NAME,
                meta=TEST_META,
                **extra_oauth_info
            ),
        )
        if extra_bb_keys:
            blackbox_response.update(extra_bb_keys)
        self.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(**blackbox_response),
        )

    def default_params(self):
        return {}

    def assert_blackbox_not_called(self):
        eq_(len(self.blackbox.requests), 0)

    def assert_blackbox_called(self):
        eq_(len(self.blackbox.requests), 1)
        self.blackbox.requests[0].assert_query_contains({'oauth_token': 'TOKEN'})

    def assert_statbox_empty(self):
        self.check_statbox_entries([])

    def assert_statbox_written(self, response_format='json', with_payment_auth_info=False):
        self.check_statbox_entries([
            {
                'mode': 'get_info_by_token',
                'status': 'ok',
                'uid': '123',
                'client_id': self.test_client.display_id,
                'token_id': '100500',
                'format': response_format,
                'with_payment_auth_info': '1' if with_payment_auth_info else '0',
            },
        ])

    def test_invalid_format_error(self):
        """При неправильном формате должно отдаваться 400"""
        self.make_request(
            format='foo',
            expected_status=400,
            decode_response=False,
        )
        self.assert_blackbox_not_called()
        self.assert_statbox_empty()

    def test_authorization_from_header_ok(self):
        """Токен должен поддерживаться в заголовке Authorization"""
        self.make_request(
            headers={'HTTP_AUTHORIZATION': 'OAuth TOKEN'},
        )
        self.assert_blackbox_called()
        self.assert_statbox_written()

    def test_token_from_get_ok(self):
        """Токен должен поддерживаться в GET-параметрах"""
        self.make_request(
            oauth_token='TOKEN',
        )
        self.assert_blackbox_called()
        self.assert_statbox_written()

    def test_token_from_post_ok(self):
        """Токен должен поддерживаться в POST-параметрах"""
        self.make_request(
            http_method='POST',
            oauth_token='TOKEN',
        )
        self.assert_blackbox_called()
        self.assert_statbox_written()

    def test_empty_token_error(self):
        """С пустым токеном должно отдаваться 401"""
        self.make_request(
            headers={'HTTP_AUTHORIZATION': 'OAuth '},
            expected_status=401,
            decode_response=False,
        )
        self.assert_blackbox_not_called()
        self.assert_statbox_empty()

    def test_invalid_token_error(self):
        """С неправильным токеном должно отдаваться 401"""
        self.set_blackbox_return_value(status=BLACKBOX_OAUTH_INVALID_STATUS)
        self.make_request(
            oauth_token='TOKEN',
            expected_status=401,
            decode_response=False,
        )
        self.assert_blackbox_called()
        self.assert_statbox_empty()

    def test_depersonalized_token_error(self):
        """Деперсонализированный токен считаем невалидным"""
        self.set_blackbox_return_value(uid=None)
        self.make_request(
            oauth_token='TOKEN',
            expected_status=401,
            decode_response=False,
        )
        self.assert_blackbox_called()
        self.assert_statbox_empty()

    def test_format_xml_ok(self):
        """С format=xml должен отдаваться xml"""
        rv = self.make_request(
            oauth_token='TOKEN',
            format='xml',
            with_payment_auth_info='yes',  # для xml этот параметр не влияет на состав ответа
            decode_response=False,
            expected_content_type='application/xml',
        )
        eq_(
            rv,
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<user>'
            '<birthday>1234-56-79</birthday>'
            '<client_id>%s</client_id>'
            '<default_avatar_id>1234</default_avatar_id>'
            '<default_email>aa@bb.cc</default_email>'
            '<default_phone><id>1</id><number>+79151234567</number></default_phone>'
            '<display_name>Vasya</display_name>'
            '<emails><address>aa@bb.cc</address></emails>'
            '<first_name>Vasya</first_name>'
            '<has_plus>true</has_plus>'
            '<id>123</id>'
            '<is_avatar_empty>false</is_avatar_empty>'
            '<last_name>Pupkin</last_name>'
            '<login>Vasya.1</login>'
            '<phones><phone><id>1</id><number>+79151234567</number><confirmed>100</confirmed></phone></phones>'
            '<psuid>%s</psuid>'
            '<real_name>Vasya Pupkin</real_name>'
            '<sex>male</sex>'
            '<verification_level>%s</verification_level>'
            '</user>' % (self.test_client.display_id, TEST_EXPECTED_PSUID, VerificationLevel.NO_VERIFIED),
        )
        self.assert_blackbox_called()
        self.assert_statbox_written(response_format='xml', with_payment_auth_info=True)

    def test_format_json_ok(self):
        """С format=json должен отдаваться json"""
        rv = self.make_request(
            oauth_token='TOKEN',
            format='json',
            expected_content_type='application/json',
        )
        iter_eq(
            rv,
            self.expected_response,
        )
        self.assert_blackbox_called()
        self.assert_statbox_written()

    def test_format_jwt_ok(self):
        with mock.patch('uuid.uuid1', mock.Mock(return_value=TEST_FAKE_UUID)):
            rv = self.make_request(
                oauth_token='TOKEN',
                format='jwt',
                jwt_secret='secret',
                decode_response=False,
                expected_content_type='text/plain',
            )
        iter_eq(
            jwt.decode(rv, 'secret', algorithms='HS256'),
            self.expected_jwt_response,
        )
        self.assert_blackbox_called()
        self.assert_statbox_written(response_format='jwt')

    def test_format_jwt_with_empty_secret_ok(self):
        with mock.patch('uuid.uuid1', mock.Mock(return_value=TEST_FAKE_UUID)):
            rv = self.make_request(
                oauth_token='TOKEN',
                format='jwt',
                jwt_secret='',
                decode_response=False,
                expected_content_type='text/plain',
            )
        iter_eq(
            jwt.decode(rv, algorithms='HS256'),
            self.expected_jwt_response,
        )
        self.assert_blackbox_called()
        self.assert_statbox_written(response_format='jwt')

    def test_format_jwt_without_secret_ok(self):
        with mock.patch('uuid.uuid1', mock.Mock(return_value=TEST_FAKE_UUID)):
            rv = self.make_request(
                oauth_token='TOKEN',
                format='jwt',
                decode_response=False,
                expected_content_type='text/plain',
            )
        iter_eq(
            jwt.decode(rv, self.test_client.secret, algorithms='HS256'),
            self.expected_jwt_response,
        )
        self.assert_blackbox_called()
        self.assert_statbox_written(response_format='jwt')

    def test_format_missing_ok(self):
        """Без format должен отдаваться json"""
        rv = self.make_request(
            oauth_token='TOKEN',
            expected_content_type='application/json',
        )
        iter_eq(
            rv,
            self.expected_response,
        )
        self.assert_blackbox_called()
        self.assert_statbox_written()

    def test_ok_without_openid_identity(self):
        for false_value in ('no', 'false', '0'):
            rv = self.make_request(
                oauth_token='TOKEN',
                with_openid_identity=false_value,
            )
            iter_eq(rv, self.expected_response)

    def test_ok_with_openid_identity(self):
        for true_value in ('yes', 'true', '1'):
            rv = self.make_request(
                oauth_token='TOKEN',
                with_openid_identity=true_value,
            )
            iter_eq(
                rv,
                dict(
                    self.expected_response,
                    openid_identities=[
                        'http://openid.yandex.ru/uid-mmzxjnry/',
                        'http://openid.yandex.ru/vasya-1/',
                        'http://vasya-1.ya.ru/',
                    ],
                ),
            )

    def test_ok_with_payment_auth_info(self):
        self.set_blackbox_return_value(
            scopes=TEST_DEFAULT_SCOPES + ['money:scope1', 'money:scope2'],
            payment_auth_context_id=TEST_CONTEXT_ID,
            payment_auth_scope_addendum=TEST_SCOPE_ADDENDUM,
        )
        rv = self.make_request(
            oauth_token='TOKEN',
            with_payment_auth_info='yes',
        )
        iter_eq(
            rv,
            dict(
                self.expected_response,
                payment_auth_info={
                    'scopes': ['money:scope1', 'money:scope2'],
                    'client_name': TEST_CLIENT_NAME,
                    'meta': TEST_META,
                    'context_id': TEST_CONTEXT_ID,
                    'scope_addendum': TEST_SCOPE_ADDENDUM,
                },
            ),
        )
        self.assert_statbox_written(with_payment_auth_info=True)

    def test_ok_with_payment_auth_info_but_no_payment_scopes(self):
        rv = self.make_request(
            oauth_token='TOKEN',
            with_payment_auth_info='yes',
        )
        iter_eq(
            rv,
            dict(
                self.expected_response,
                payment_auth_info=None,
            ),
        )
        self.assert_statbox_written(with_payment_auth_info=True)

    def test_ok_with_payment_auth_info_but_no_grants(self):
        self.fake_grants.set_data({})
        self.make_request(
            oauth_token='TOKEN',
            with_payment_auth_info='yes',
            decode_response=False,
            expected_status=403,
        )
        self.assert_blackbox_not_called()

    def test_not_canonical_url_ok(self):
        self.make_request(
            url=reverse('yandex_login_info') + '/',
            oauth_token='TOKEN',
        )
        self.assert_blackbox_called()
        self.assert_statbox_written()

    @parameterized.expand([
        (['secured', 'confirmed'], 1085, VerificationLevel.NO_VERIFIED),
        (['secured', 'confirmed'], 0, VerificationLevel.HIGH_VERIFIED),
        (['confirmed'], 0, VerificationLevel.LOW_VERIFIED),
        ([], 0, VerificationLevel.NO_VERIFIED)
    ])
    def test_verification_level(self, phone_attributes, karma, expected_verification_level):
        phone = {
            'number': '+79151234567',
            'id': 1,
            'bound': datetime.fromtimestamp(100),
            'is_default': 1,
        }
        for attribute in phone_attributes:
            phone[attribute] = datetime.fromtimestamp(100)
        self.set_blackbox_return_value(
            extra_bb_keys=dict(
                phones=[phone],
                karma=karma,
            )
        )
        rv = self.make_request(
            oauth_token='TOKEN',
            format='json',
            expected_content_type='application/json',
        )
        iter_eq(
            rv,
            dict(
                self.expected_response,
                verification_level=expected_verification_level,
                default_phone={'id': 1, 'number': '+79151234567'} if 'secured' in phone_attributes else None,
            ),
        )

        self.assert_blackbox_called()
        self.assert_statbox_written()
