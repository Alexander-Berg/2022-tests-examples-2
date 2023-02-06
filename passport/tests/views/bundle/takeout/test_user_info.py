# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AVATAR_URL_TEMPLATE,
    TEST_BIRTHDAY,
    TEST_CITY,
    TEST_COUNTRY_CODE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_FIRSTNAME,
    TEST_GENDER,
    TEST_LANGUAGE,
    TEST_LASTNAME,
    TEST_PHONE_CREATED_DT,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_UID,
)
from passport.backend.core import authtypes
from passport.backend.core.builders.blackbox.blackbox import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_aggregated_browser_info,
    auth_aggregated_ip_info,
    auth_aggregated_item,
    auth_aggregated_os_info,
    auths_aggregated_response,
    event_item,
    events_response,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    profile_item,
    social_api_person_item,
    USERNAME,
)
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.phones.faker import build_phone_unbound
from passport.backend.core.test.consts import TEST_TIMEZONE1
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)


eq_ = iterdiff(eq_)


TEST_LOGIN = 'Test-Login'
TEST_LOGIN_NORMALIZED = 'test-login'
TEST_AVATAR_KEY = 'avakey'

TEST_AS_ID = 13238
TEST_AS = 'AS%s' % TEST_AS_ID
TEST_GEOID = 9999
TEST_IP = '8.8.8.8'

TEST_UNIXTIME = 946674001
TEST_DATETIME_STR = datetime_to_string(unixtime_to_datetime(TEST_UNIXTIME))

TEST_OTT_SUBSCRIPTION = 'YA_PREMIUM'
TEST_PLUS_FAMILY_ROLE = 'FAMILY_MEMBER'


@with_settings_hosts(
    GET_AVATAR_URL=TEST_AVATAR_URL_TEMPLATE,
)
class TestUserInfo(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/takeout/user_info/'
    http_method = 'post'
    http_query_args = {
        'uid': TEST_UID,
        'unixtime': 123456789,
    }
    consumer = 'dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'takeout': ['user_info']},
            ),
        )
        self.setup_account_info()
        self.setup_historydb()

    def setup_account_info(self, uid=TEST_UID, primary_alias_type='portal',
                           login=TEST_LOGIN_NORMALIZED, display_login=TEST_LOGIN,
                           display_name=TEST_DISPLAY_NAME_DATA, default_avatar_key=TEST_AVATAR_KEY,
                           firstname=TEST_FIRSTNAME, lastname=TEST_LASTNAME, birthday=TEST_BIRTHDAY, gender=TEST_GENDER,
                           language=TEST_LANGUAGE, country=TEST_COUNTRY_CODE, city=TEST_CITY, timezone=TEST_TIMEZONE1,
                           registration_dt=TEST_DATETIME_STR,
                           with_external_email=True, with_phones=True, with_plus=True, with_social_profiles=True):
        emails = [
            self.create_native_email(login, 'yandex.ru'),
        ]
        if with_external_email:
            emails.append(
                self.create_validated_external_email(login, 'gmail.com', default=True, born_date=TEST_DATETIME_STR),
            )

        blackbox_args = dict(
            uid=uid,
            login=login,
            aliases={
                primary_alias_type: login,
            },
            display_login=display_login,
            display_name=display_name,
            default_avatar_key=default_avatar_key,
            dbfields={
                'userinfo.reg_date.uid': registration_dt,
            },
            attributes={},
            emails=emails,
            firstname=firstname,
            lastname=lastname,
            birthdate=birthday,
            gender=gender,
            language=language,
            country=country,
            city=city,
            timezone=timezone,
        )
        if with_phones:
            blackbox_args = deep_merge(
                blackbox_args,
                build_phone_unbound(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_confirmed=TEST_PHONE_CREATED_DT,
                ),
            )
        if with_plus:
            blackbox_args['attributes'].update({
                AT['account.have_plus']: '1',
                AT['account.plus.trial_used_ts']: TEST_UNIXTIME,
                AT['account.plus.subscription_expire_ts']: TEST_UNIXTIME,
                AT['account.plus.next_charge_ts']: TEST_UNIXTIME,
                AT['account.plus.ott_subscription']: TEST_OTT_SUBSCRIPTION,
                AT['account.plus.family_role']: TEST_PLUS_FAMILY_ROLE,
            })
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(**blackbox_args),
        )

        profiles = []
        if with_social_profiles:
            profiles = [
                profile_item(
                    person=social_api_person_item(firstname=firstname, lastname=lastname),
                    expand_provider=True,
                    provider='facebook',
                    userid=1,
                    allow_auth=False,
                ),
                profile_item(
                    person=social_api_person_item(firstname=firstname, lastname=lastname),
                    expand_provider=True,
                    provider='vkontakte',
                    userid=2,
                    allow_auth=True,
                ),
            ]
        self.env.social_api.set_social_api_response_value(dict(profiles=profiles))

    def setup_historydb(self, uid=TEST_UID, auths=None, events=None):
        if auths is None:
            auths = auth_aggregated_item(
                authtype=authtypes.AUTH_TYPE_WEB,
                ip_info=auth_aggregated_ip_info(AS=TEST_AS_ID, geoid=TEST_GEOID, ip=TEST_IP),
                browser_info=auth_aggregated_browser_info(),
                os_info=auth_aggregated_os_info(),
                ts=3600,
            ),
        if events is None:
            events = [
                event_item(
                    name='info.firstname',
                    value=TEST_FIRSTNAME,
                    user_ip=TEST_IP,
                    ip_as_list=TEST_AS,
                    ip_geoid=TEST_GEOID,
                ),
            ]
        self.env.historydb_api.set_response_value(
            'auths_aggregated',
            auths_aggregated_response(uid=uid, auths=auths),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(uid=uid, events=events),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_full_ok(self):
        resp = self.make_request()
        eq_(resp.status_code, 200)
        rv = json.loads(resp.data)

        eq_(set(rv.keys()), {'status', 'data'})
        eq_(rv['status'], 'ok')
        eq_(set(rv['data'].keys()), {'account_info.json', 'account_change_history.json', 'auth_history.json'})
        eq_(
            json.loads(rv['data']['account_info.json']),
            {
                'login': TEST_LOGIN,
                'registration_datetime': TEST_DATETIME_STR,
                'firstname': TEST_FIRSTNAME,
                'lastname': TEST_LASTNAME,
                'gender': 'm',
                'birthday': TEST_BIRTHDAY,
                'language': TEST_LANGUAGE,
                'country': TEST_COUNTRY_CODE,
                'city': TEST_CITY,
                'timezone': TEST_TIMEZONE1,
                'display_name': TEST_DISPLAY_NAME,
                'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
                'phones': [
                    {
                        'number': TEST_PHONE_NUMBER.international,
                        'confirmed': str(TEST_PHONE_CREATED_DT),
                    },
                ],
                'emails': [
                    {
                        'address': '%s@gmail.com' % TEST_LOGIN_NORMALIZED,
                        'confirmed': TEST_DATETIME_STR,
                    },
                ],
                'social_profiles': [
                    {
                        'provider': 'facebook',
                        'username': USERNAME,
                        'userid': 1,
                    },
                    {
                        'provider': 'vkontakte',
                        'username': USERNAME,
                        'userid': 2,
                        'allow_auth': True,
                    },
                ],
                'plus': {
                    'active': True,
                    'trial_used': True,
                    'subscription_expires': TEST_DATETIME_STR,
                    'next_charge': TEST_DATETIME_STR,
                    'ott_subscription': TEST_OTT_SUBSCRIPTION,
                    'family_role': TEST_PLUS_FAMILY_ROLE,
                },
            },
        )
        eq_(
            json.loads(rv['data']['account_change_history.json']),
            [
                {
                    'event_type': 'personal_data',
                    'timestamp': 3600,
                    'actions': [
                        {
                            'type': 'personal_data',
                            'changed_fields': ['firstname'],
                            'firstname': TEST_FIRSTNAME,
                        },
                    ],
                    'ip': {
                        'ip': TEST_IP,
                        'AS': TEST_AS_ID,
                        'geoid': TEST_GEOID,
                    },
                    'os': {
                        'version': None,
                        'name': None,
                    },
                    'browser': {
                        'version': None,
                        'name': None,
                    },
                },
            ],
        )
        eq_(
            json.loads(rv['data']['auth_history.json']),
            [
                {
                    'count': 1,
                    'authentications': [
                        {
                            'timestamp': 3600,
                        },
                    ],
                    'auth': {
                        'ip': {
                            'ip': TEST_IP,
                            'AS': TEST_AS_ID,
                            'geoid': TEST_GEOID,
                        },
                        'authtype': 'web',
                        'os': {
                            'version': '6.1',
                            'name': 'Windows 7',
                        },
                        'browser': {
                            'version': '33.0',
                            'name': 'Firefox',
                        },
                    },
                },
            ],
        )

    def test_minimal_ok(self):
        self.setup_account_info(
            primary_alias_type='social',
            firstname=None,
            lastname=None,
            birthday=None,
            gender=None,
            language=None,
            country=None,
            city=None,
            timezone=None,
            default_avatar_key='0/0-0',
            registration_dt=None,
            with_external_email=False,
            with_phones=False,
            with_plus=False,
            with_social_profiles=False,
        )
        self.setup_historydb(auths=[], events=[])

        resp = self.make_request()
        eq_(resp.status_code, 200)
        rv = json.loads(resp.data)

        eq_(set(rv.keys()), {'status', 'data'})
        eq_(rv['status'], 'ok')
        eq_(set(rv['data'].keys()), {'account_info.json', 'account_change_history.json', 'auth_history.json'})
        eq_(
            json.loads(rv['data']['account_info.json']),
            {
                # display_name и аватарка есть всегда
                'display_name': TEST_DISPLAY_NAME,
                'avatar_url': TEST_AVATAR_URL_TEMPLATE % ('0/0-0', 'normal'),
                # язык, страна и таймзона фолбечатся на Россию и Москву, даже если в ЧЯ нет данных
                'language': 'ru',
                'country': 'ru',
                'timezone': 'Europe/Moscow',
            },
        )
        eq_(
            json.loads(rv['data']['account_change_history.json']),
            [],
        )
        eq_(
            json.loads(rv['data']['auth_history.json']),
            [],
        )

    def test_not_found(self):
        self.setup_account_info(uid=None)

        resp = self.make_request()
        eq_(resp.status_code, 200)
        rv = json.loads(resp.data)
        eq_(rv, {'status': 'no_data'})

    def test_blackbox_error(self):
        self.env.blackbox.set_response_side_effect('userinfo', BlackboxTemporaryError)

        resp = self.make_request()
        eq_(resp.status_code, 200)
        rv = json.loads(resp.data)
        eq_(
            rv,
            {
                'status': 'error',
                'error': 'backend.blackbox_failed',
            },
        )
