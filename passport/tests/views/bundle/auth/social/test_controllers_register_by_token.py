# -*- coding: utf-8 -*-

import json

from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response_multiple
from passport.backend.core.builders.oauth.faker import token_response
from passport.backend.core.builders.social_api.faker.social_api import (
    FIRSTNAME,
    get_bind_response,
    LASTNAME,
    PROFILE_EMAIL,
    profile_item,
)
from passport.backend.core.builders.social_broker.exceptions import SocialBrokerTemporaryError
from passport.backend.core.builders.social_broker.faker.social_broker import social_broker_error_response
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.geobase.faker.fake_geobase import FakeRegion
from passport.backend.core.test.consts import TEST_APPLICATION_ID1
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.email.email import mask_email_for_statbox

from .base_test_data import (
    TEST_CONSUMER_IP1,
    TEST_GENERATED_LOGIN,
    TEST_SOCIAL_ALIAS,
    TEST_SOCIAL_UID,
    TEST_TASK_ID,
    TEST_USER_IP,
    TEST_USERID,
)
from .test_controllers_register import BaseAuthSocialRegister


TEST_PROVIDER_TOKEN1 = 'token1'
TEST_ACCESS_TOKEN = '12345678'
TEST_EXPIRES_IN = '100'
TEST_REGISTER_ACCOUNT_UID = '1'
TEST_MTS_CLIENT_ID = 'mts_client_id'
TEST_MTS_CLIENT_SECRET = 'mts_client_secret'


@with_settings_hosts(
    AUTH_ALLOWED_PROVIDERS=['mt'],
    SOCIAL_TRUSTED_SIMPLE_PHONE=['mt'],
    OAUTH_APPLICATIONS_FOR_MUSIC={
        'mt': {
            'client_id': TEST_MTS_CLIENT_ID,
            'client_secret': TEST_MTS_CLIENT_SECRET,
        },
    },
)
class TestAuthSocialRegisterByToken(BaseAuthSocialRegister):
    default_url = '/1/bundle/auth/social/register_by_token/?consumer=dev'
    http_method = 'POST'
    http_query_args = {
        'provider_token': TEST_PROVIDER_TOKEN1,
        'provider': 'mt',
        'application': TEST_APPLICATION_ID1,
    }
    http_headers = {
        'user_ip': TEST_USER_IP,
        'user_agent': 'curl',
    }

    def setUp(self):
        super(TestAuthSocialRegisterByToken, self).setUp()
        self.env.social_api.set_response_value(
            'get_profiles',
            json.dumps({'profiles': []}),
        )
        self.env.social_api.set_response_value(
            'bind_task_profile',
            json.dumps(get_bind_response()),
        )
        self.env.oauth.set_response_value(
            '_token',
            token_response(
                access_token=TEST_ACCESS_TOKEN,
                expires_in=TEST_EXPIRES_IN,
            )
        )
        self._builder = self.get_primary_builder()

        self.fake_region = FakeRegion()
        self.fake_region.start()

        self.fake_region.set_region_for_ip(TEST_USER_IP, dict(timezone='Europe/Moscow'))

    def tearDown(self):
        self.fake_region.stop()
        super(TestAuthSocialRegisterByToken, self).tearDown()

    def setup_grants(self, **kwargs):
        self.env.grants.set_grants_return_value(
            {
                'dev': {
                    'grants': {'auth_social': ['register_by_token']},
                    'networks': [TEST_CONSUMER_IP1],
                },
            },
        )

    def default_response_values(self):
        return {
            'access_token': TEST_ACCESS_TOKEN,
            'expires_in': TEST_EXPIRES_IN,
            'status': 'ok',
        }

    def test_ok(self):
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            self.env.social_broker.get_task_by_token_response(
                provider_code='mt',
                userid=TEST_USERID,
                task_id=TEST_TASK_ID,
                firstname=FIRSTNAME,
            ),
        )
        rv = self.make_request()

        self.assert_ok_response(rv, **self.default_response_values())

        self.assertEqual(len(self.env.social_broker.requests), 1)
        self.env.social_broker.requests[0].assert_query_equals({
            'provider': 'mt',
            'application': str(TEST_APPLICATION_ID1),
            'consumer': 'passport'
        })
        self.env.social_broker.requests[0].assert_url_starts_with(
            'https://api.social-test.yandex.ru/brokerapi/task_by_token?',
        )
        self.assertEqual(len(self.env.social_api.requests), 2)
        self.env.social_api.requests[0].assert_query_equals({
            'provider': 'mt',
            'userid': str(TEST_USERID),
            'consumer': 'passport'
        })
        self.env.social_api.requests[0].assert_url_starts_with(
            'https://api.social-test.yandex.ru/api/profiles?',
        )
        self.env.social_api.requests[1].assert_query_equals({
            'allow_auth': str(1),
            'uid': TEST_REGISTER_ACCOUNT_UID,
            'consumer': 'passport'
        })
        self.env.social_api.requests[1].assert_url_starts_with(
            'https://api.social-test.yandex.ru/api/task/' + TEST_TASK_ID + '/bind',
        )
        self.assertEqual(len(self.env.oauth.requests), 1)
        self.env.oauth.requests[0].assert_query_equals({
            'user_ip': TEST_USER_IP,
        })
        self.env.oauth.requests[0].assert_post_data_equals({
            'client_secret': TEST_MTS_CLIENT_SECRET,
            'grant_type': 'passport_assertion',
            'assertion': int(TEST_REGISTER_ACCOUNT_UID),
            'client_id': TEST_MTS_CLIENT_ID,
            'password_passed': False,
        })
        self.env.db.check(
            'aliases',
            'social',
            TEST_GENERATED_LOGIN,
            uid=int(TEST_REGISTER_ACCOUNT_UID),
            db='passportdbcentral'
        )
        self.env.db.check_missing(
            'aliases',
            'portal',
            uid=int(TEST_REGISTER_ACCOUNT_UID),
            db='passportdbcentral'
        )
        self.env.db.check_db_attr(int(TEST_REGISTER_ACCOUNT_UID), 'person.firstname', FIRSTNAME)
        self.env.db.check_db_attr(int(TEST_REGISTER_ACCOUNT_UID), 'person.lastname', LASTNAME)

        self.assertEqual(len(self.env.frodo.requests), 1)

        self.env.frodo.requests[0].assert_query_contains({
            'action': 'admsocialreg',
            'social_provider': 'mt',
            'iname': FIRSTNAME,
            'fname': LASTNAME,
        })
        self.assert_statbox()
        self.assert_historydb()

    def test_ok_existed_account(self):
        response = {'profiles': [profile_item(uid=TEST_SOCIAL_UID)]}
        self.env.social_api.set_response_value(
            'get_profiles',
            json.dumps(response),
        )
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            self.env.social_broker.get_task_by_token_response(
                provider_code='mt',
                userid=TEST_USERID,
                task_id=TEST_TASK_ID,
                firstname=FIRSTNAME,
            ),
        )
        response = blackbox_userinfo_response_multiple([
            dict(
                uid=TEST_SOCIAL_UID,
                login=TEST_SOCIAL_ALIAS,
                aliases={'social': TEST_SOCIAL_ALIAS},
            ),
        ])
        self.env.blackbox.set_response_value('userinfo', response)
        rv = self.make_request()

        self.assert_ok_response(rv, **self.default_response_values())
        self.assertEqual(len(self.env.oauth.requests), 1)
        self.env.oauth.requests[0].assert_query_equals({
            'user_ip': TEST_USER_IP,
        })
        self.env.oauth.requests[0].assert_post_data_equals({
            'client_secret': TEST_MTS_CLIENT_SECRET,
            'grant_type': 'passport_assertion',
            'assertion': int(TEST_SOCIAL_UID),
            'client_id': TEST_MTS_CLIENT_ID,
            'password_passed': False,
        })
        self.assertEqual(len(self.env.frodo.requests), 0)
        self.env.statbox.assert_has_written([])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_ok_existed_multiple_accounts(self):
        response = {'profiles': [
            profile_item(uid=TEST_SOCIAL_UID),
            profile_item(uid=TEST_SOCIAL_UID + 1),
        ]}
        self.env.social_api.set_response_value(
            'get_profiles',
            json.dumps(response),
        )
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            self.env.social_broker.get_task_by_token_response(
                provider_code='mt',
                userid=TEST_USERID,
                task_id=TEST_TASK_ID,
                firstname=FIRSTNAME,
            ),
        )
        response = blackbox_userinfo_response_multiple([
            dict(
                uid=TEST_SOCIAL_UID,
                login=TEST_SOCIAL_ALIAS,
                aliases={'social': TEST_SOCIAL_ALIAS},
            ),
            dict(
                uid=TEST_SOCIAL_UID + 1,
                login=TEST_SOCIAL_ALIAS + '_A',
                aliases={'social': TEST_SOCIAL_ALIAS + '_A'},
            ),
        ])
        self.env.blackbox.set_response_value('userinfo', response)
        rv = self.make_request()

        self.assert_ok_response(rv, **self.default_response_values())
        self.assertEqual(len(self.env.oauth.requests), 1)
        self.env.oauth.requests[0].assert_query_equals({
            'user_ip': TEST_USER_IP,
        })
        self.env.oauth.requests[0].assert_post_data_equals({
            'client_secret': TEST_MTS_CLIENT_SECRET,
            'grant_type': 'passport_assertion',
            'assertion': int(TEST_SOCIAL_UID + 1),
            'client_id': TEST_MTS_CLIENT_ID,
            'password_passed': False,
        })
        self.assertEqual(len(self.env.frodo.requests), 0)
        self.env.statbox.assert_has_written([])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_get_task_by_token_network_error(self):

        self.env.social_broker.set_response_side_effect(
            'get_task_by_token',
            SocialBrokerTemporaryError,
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.social_broker_failed'])

    def test_error_invalid_provider(self):
        """
        Принимаем только провайдеров из REGISTER_BY_TASK_PROVIDERS
        """
        rv = self.make_request(query_args={'provider': 'fb'})

        self.assert_error_response(
            rv,
            ['provider.invalid']
        )

    def test_error_invalid_token(self):
        """
        Принимаем инвалидный токен
        """

        self.env.social_broker.set_response_value(
            'get_task_by_token',
            social_broker_error_response(code='OAuthTokenInvalidError'),
        )
        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['provider_token.invalid']
        )

    def test_no_provider(self):
        rv = self.make_request(exclude_args=['provider'])
        self.assert_error_response(rv, ['provider.empty'])

    def test_no_application(self):
        rv = self.make_request(exclude_args=['application'])
        self.assert_error_response(rv, ['application.empty'])

    def test_no_provider_token(self):
        rv = self.make_request(exclude_args=['provider_token'])
        self.assert_error_response(rv, ['provider_token.empty'])

    def test_error_provider_unknown(self):
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            social_broker_error_response('ProviderUnknownError'),
        )
        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['provider.invalid']
        )

    def test_error_application_unknown(self):
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            social_broker_error_response('ApplicationUnknownError'),
        )
        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['application.invalid']
        )

    def assert_statbox(self):
        lines = [
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                operation='created',
                old='-',
                new='enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='aliases',
                type=str(ANT['social']),
                operation='added',
                value=TEST_GENERATED_LOGIN,
            ),
        ]

        now = DatetimeNow(convert_to_datetime=True)
        lines.append(
            self.env.statbox.entry(
                'account_modification',
                bound_at=now,
                confirmed_at=now,
                created_at=now,
                email_id='1',
                entity='account.emails',
                new=mask_email_for_statbox(PROFILE_EMAIL),
                old='-',
                uid=str(TEST_REGISTER_ACCOUNT_UID),
                is_unsafe='1',
                ip=TEST_USER_IP,
                operation='added',
                is_suitable_for_restore='0',
            ),
        )

        lines.append(
            self.env.statbox.entry(
                'account_modification',
                entity='person.firstname',
                operation='created',
                new=FIRSTNAME,
                old='-',
            ),
        )
        lines.append(
            self.env.statbox.entry(
                'account_modification',
                entity='person.lastname',
                operation='created',
                new=LASTNAME,
                old='-',
            ),
        )

        for entity, operation, new, old in [
            ('person.language', 'created', 'en', '-'),
            ('person.country', 'created', 'en', '-'),
        ]:
            lines.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    operation=operation,
                    new=new,
                    old=old,
                ),
            )

        lines.append(
            self.env.statbox.entry(
                'account_modification',
                entity='person.gender',
                operation='created',
                new='m',
                old='-',
            ),
        )

        lines.append(
            self.env.statbox.entry(
                'account_modification',
                entity='person.fullname',
                operation='created',
                new=FIRSTNAME + ' ' + LASTNAME,
                old='-',
            ),
        )

        lines.append(
            self.env.statbox.entry(
                'frodo_karma',
                action='account_register_social',
                login=TEST_GENERATED_LOGIN,
                registration_datetime=DatetimeNow(convert_to_datetime=True),
            ),
        )
        for sid in ['8', '58']:
            lines.append(
                self.env.statbox.entry(
                    'subscriptions',
                    operation='added',
                    sid=sid,
                ),
            )

        lines.append(
            self.env.statbox.entry(
                'account_modification',
                entity='person.display_name',
                operation='created',
                new='s:123456789:mt:{}'.format(FIRSTNAME + ' ' + LASTNAME),
                old='-',
            ),
        )

        lines.append(
            self.env.statbox.entry(
                'account_created',
                _exclude={
                    'ip',
                    'is_suggested_login',
                    'password_quality',
                    'suggest_generation_number',
                    'captcha_generation_number',
                    'is_voice_generated',
                    'retpath',
                    'track_id',
                },
                userid=str(TEST_USERID),
            ),
        )
        self.env.statbox.assert_has_written(lines)

    def assert_historydb(self):
        now = TimeNow()
        historydb_entries = [
            {'name': 'info.login', 'value': TEST_GENERATED_LOGIN},
            {'name': 'info.ena', 'value': '1'},
            {'name': 'info.disabled_status', 'value': '0'},
            {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True)},
            {'name': 'info.firstname', 'value': 'Firstname'},
            {'name': 'info.lastname', 'value': 'Lastname'},
            {'name': 'info.sex', 'value': '1'},
            {'name': 'info.country', 'value': 'en'},
            {'name': 'info.tz', 'value': 'Europe/Moscow'},
            {'name': 'info.lang', 'value': 'en'},
            {'name': 'info.karma_prefix', 'value': '0'},
            {'name': 'info.karma_full', 'value': '0'},
            {'name': 'info.karma', 'value': '0'},
            {'name': 'alias.social.add', 'value': TEST_GENERATED_LOGIN},
            {'name': 'sid.add', 'value': '8|{0},58|{0}'.format(TEST_GENERATED_LOGIN)},
            {'name': 'email.1', 'value': 'created'},
            {'name': 'email.1.address', 'value': 'some-mail@example.com'},
            {'name': 'email.1.confirmed_at', 'value': now},
            {'name': 'email.1.created_at', 'value': now},
            {'name': 'email.1.bound_at', 'value': now},
            {'name': 'email.1.is_unsafe', 'value': '1'},
            {'name': 'action', 'value': 'account_register_social'},
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'curl'},
            {'name': 'info.display_name', 'value': 's:123456789:mt:{}'.format(FIRSTNAME + ' ' + LASTNAME)},
            {'name': 'info.dont_use_displayname_as_public_name', 'value': '1'},
            {'name': 'action', 'value': 'change_display_name'},
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'curl'},
        ]
        self.assert_events_are_logged(self.env.handle_mock, historydb_entries)
