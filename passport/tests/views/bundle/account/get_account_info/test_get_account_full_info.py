# -*- coding: utf-8 -*-
from copy import deepcopy

from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mixins.account import GetAccountBySessionOrTokenMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_ACCOUNT_DATA,
    TEST_AVATAR_KEY,
    TEST_CITY,
    TEST_CYRILLIC_DOMAIN,
    TEST_CYRILLIC_DOMAIN_IDNA,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_DOMAIN,
    TEST_FAMILY_ID,
    TEST_FAMILY_INFO,
    TEST_FAMILY_INVITE1,
    TEST_FAMILY_INVITE2,
    TEST_FIRSTNAME,
    TEST_HINT_ANSWER,
    TEST_HINT_QUESTION,
    TEST_HINT_QUESTION_TEXT,
    TEST_HOST,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_OAUTH_SCOPE,
    TEST_OPERATION_ID,
    TEST_PASSWORD_HASH,
    TEST_PASSWORD_QUALITY,
    TEST_PASSWORD_QUALITY_VERSION,
    TEST_PASSWORD_UPDATE_TIMESTAMP,
    TEST_PDD_CYRILLIC_LOGIN,
    TEST_PDD_DOMAIN_TEMPLATE,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_CREATED_DT,
    TEST_PHONE_CREATED_TS,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_PUBLIC_ID,
    TEST_TZ,
    TEST_UID,
    TEST_UID1,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
    TEST_WEAK_PASSWORD_HASH,
    TEST_WEAK_PASSWORD_QUALITY,
)
from passport.backend.api.views.bundle.phone.helpers import dump_number
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_family_info_response,
    blackbox_hosted_domains_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.historydb_api.exceptions import (
    HistoryDBApiInvalidResponseError,
    HistoryDBApiTemporaryError,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_aggregated_browser_info,
    auth_aggregated_ip_info,
    auth_aggregated_item,
    auth_aggregated_os_info,
    auths_aggregated_response,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    profile_item,
    social_api_person_item,
)
from passport.backend.core.models.family import FamilyInvite
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_remove_operation,
    evaluate_finished_time,
)
from passport.backend.core.test.consts import TEST_BIRTHDATE1
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime


PASSWORD_STRENGTH_STATUS_WEAK = 0
PASSWORD_STRENGTH_STATUS_STRONG = 1
PASSWORD_STRENGTH_STATUS_UNKNOWN = -1

SECURITY_LEVEL_UNKNOWN = -1
SECURITY_LEVEL_WEAK = 4
SECURITY_LEVEL_NORMAL = 16
SECURITY_LEVEL_STRONG = 32

ACCOUNT_FULL_INFO_READ_GRANT = 'account.full_info_read'

TEST_ACCOUNT_FULL_DATA = deepcopy(TEST_ACCOUNT_DATA)
TEST_ACCOUNT_FULL_DATA[u'account'][u'person'].update(
    city=TEST_CITY,
    timezone=str(TEST_TZ),
)
TEST_FULL_NAME = '%s %s' % (TEST_FIRSTNAME, TEST_LASTNAME)
TEST_ACCOUNT_FULL_DATA[u'account'][u'public_id'] = TEST_PUBLIC_ID
TEST_ACCOUNT_FULL_DATA[u'account'][u'display_names'] = {
    TEST_FIRSTNAME: 'p:%s' % TEST_FIRSTNAME,
    TEST_LASTNAME: 'p:%s' % TEST_LASTNAME,
    TEST_FULL_NAME: 'p:%s %s' % (TEST_FIRSTNAME, TEST_LASTNAME),
    TEST_LOGIN: 'p:%s' % TEST_LOGIN,
}
TEST_ACCOUNT_FULL_DATA[u'account'][u'phones'] = {
    '1': {
        'id': 1,
        'number': dump_number(TEST_PHONE_NUMBER),
        'created': TEST_PHONE_CREATED_TS,
        'confirmed': TEST_PHONE_CREATED_TS,
        'need_admission': True,
        'is_alias': False,
        'alias': {
            'login_enabled': False,
            'email_enabled': False,
            'email_allowed': True,
        },
        'is_default': False,
    },
}
TEST_ACCOUNT_FULL_DATA[u'account'][u'emails'] = {
    'confirmed_external': [
        'Musk@mail.ru',
    ],
    'default': 'Elon@ya.kz',
    'external': [
        'Musk@mail.ru',
    ],
    'native': [
        'Elon@ya.kz',
        'login@ya.ru',
    ],
    'suitable_for_restore': [
        'Musk@mail.ru',
    ],
}
TEST_ACCOUNT_FULL_DATA[u'account'][u'profiles'] = []
TEST_ACCOUNT_FULL_DATA[u'account'][u'app_passwords_enabled'] = False
TEST_ACCOUNT_FULL_DATA[u'account'][u'security_level'] = SECURITY_LEVEL_UNKNOWN
TEST_ACCOUNT_FULL_DATA[u'account'][u'password_info'] = {
    'strength': PASSWORD_STRENGTH_STATUS_UNKNOWN,
    'last_update': None,
    'strong_policy_on': False,
}
TEST_ACCOUNT_FULL_DATA[u'account'][u'lastauth'] = {
    'authtype': 'web',
    'timestamp': 3600,
    'browser': {
        'name': 'Firefox',
        'version': '33.0',
    },
    'ip': {
        'AS': 13238,
        'geoid': 9999,
        'ip': u'2a02:6b8:0:101:19c3:e71d:2e1d:5017',
    },
    'os': {
        'name': 'Windows 7',
        'version': '6.1',
    },
}

TEST_FAMILY_MAX_SIZE = 4
TEST_FAMILY_MAX_KIDS_NUMBER = 3

TEST_OPERATION_STARTED_DT = DatetimeNow()
TEST_OPERATION_STARTED_TS = datetime_to_integer_unixtime(TEST_OPERATION_STARTED_DT)

TEST_OPERATION_FINISHED_DT = evaluate_finished_time(TEST_OPERATION_STARTED_DT)
TEST_OPERATION_FINISHED_TS = datetime_to_integer_unixtime(TEST_OPERATION_FINISHED_DT)
TEST_PHONE_ALIAS_EMAILS = ['%s@%s' % (TEST_PHONE_NUMBER.digital, domain) for domain in ['ya.ru', 'ya.kz']]
TEST_PUBLIC_NAME = u'Мр. Октябрь'


@with_settings_hosts(
    FAMILY_MAX_KIDS_NUMBER=TEST_FAMILY_MAX_KIDS_NUMBER,
    FAMILY_MAX_SIZE=TEST_FAMILY_MAX_SIZE,
    IS_INTRANET=False,
    SOCIAL_DEFAULT_SUBSCRIPTION=[],
)
class TestGetAccountFullInfoView(BaseBundleTestViews, EmailTestMixin, GetAccountBySessionOrTokenMixin):

    default_url = '/1/bundle/account/'
    http_query_args = dict(consumer='dev')
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_USER_COOKIE,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )
    mocked_grants = [ACCOUNT_FULL_INFO_READ_GRANT]

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE,
                              pdd_options=None,
                              count_domains=3,
                              with_password=False,
                              weak_password=False,
                              with_phone=True,
                              is_bound_phone=False,
                              is_secure_phone=False,
                              with_native_emails=True,
                              with_restore_emails=True,
                              with_hint=False,
                              strong_policy_required=False,
                              family_info=None,
                              family_members=None,
                              family_members_places=None,
                              family_kids=None,
                              **initial_data):
        initial_data = initial_data or self.initial_data
        domain = initial_data.get('domain') or TEST_DOMAIN
        can_users_change_password = initial_data.pop('can_users_change_password', None)

        if with_password:
            password_hash = TEST_WEAK_PASSWORD_HASH if weak_password else TEST_PASSWORD_HASH
            password_quality = TEST_WEAK_PASSWORD_QUALITY if weak_password else TEST_PASSWORD_QUALITY
            initial_data.setdefault('dbfields', {}).update(
                {
                    'password_quality.quality.uid': password_quality,
                    'password_quality.version.uid': TEST_PASSWORD_QUALITY_VERSION,
                },
            )
            initial_data.setdefault('attributes', {}).update(
                {
                    'password.update_datetime': TEST_PASSWORD_UPDATE_TIMESTAMP,
                    'password.encrypted': '1:%s' % password_hash,
                },
            )
        if strong_policy_required:
            initial_data.setdefault('dbfields', {}).update(
                {
                    'subscription.login_rule.67': 1,
                },
            )
            initial_data['subscribed_to'] = [67]
        if with_hint:
            initial_data.setdefault('dbfields', {}).update(
                {
                    'userinfo_safe.hintq.uid': TEST_HINT_QUESTION,
                    'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
                },
            )

        emails = []
        if with_native_emails:
            emails = [
                self.create_native_email(TEST_LOGIN, 'ya.ru'),
                self.create_native_email(TEST_FIRSTNAME, 'ya.kz'),
            ]
        if with_restore_emails:
            emails.append(
                self.create_validated_external_email(TEST_LASTNAME, 'mail.ru'),
            )
        initial_data.update(emails=emails)

        if with_phone and is_bound_phone:
            initial_data = deep_merge(
                initial_data,
                build_phone_bound(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_CREATED_DT,
                    phone_confirmed=TEST_PHONE_CREATED_DT,
                ),
            )
        elif with_phone and is_secure_phone:
            initial_data = deep_merge(
                initial_data,
                build_phone_secured(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_CREATED_DT,
                    phone_confirmed=TEST_PHONE_CREATED_DT,
                    phone_secured=TEST_PHONE_CREATED_DT,
                    phone_admitted=TEST_PHONE_CREATED_DT,
                ),
            )
        elif with_phone:
            initial_data = deep_merge(
                initial_data,
                build_phone_unbound(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_confirmed=TEST_PHONE_CREATED_DT,
                ),
            )
        else:
            initial_data.update(phones=[])

        if family_info is not None:
            initial_data = deep_merge(initial_data, {'family_info': family_info})
            self.env.blackbox.set_blackbox_response_value(
                'family_info',
                blackbox_family_info_response(
                    uids=family_members,
                    places=family_members_places,
                    kid_uids=family_kids,
                    with_members_info=True,
                    **family_info
                ),
            )
            if (
                family_kids is not None or
                family_members is not None
            ):
                family_uids = list()
                for uids in [family_kids, family_members]:
                    if uids is not None:
                        family_uids.extend(uids)
                self.env.blackbox.set_response_value(
                    'userinfo',
                    blackbox_userinfo_response(
                        attributes={'account.have_plus': '1'},
                        default_avatar_key=TEST_AVATAR_KEY,
                        display_name=TEST_DISPLAY_NAME_DATA,
                        firstname=TEST_FIRSTNAME,
                        lastname=TEST_LASTNAME,
                        public_name=TEST_PUBLIC_NAME,
                        uids=family_uids,
                        birthdate=TEST_BIRTHDATE1,
                    ),
                )
        else:
            self.env.blackbox.set_blackbox_response_value(
                'family_info',
                blackbox_family_info_response(exists=False),
            )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**initial_data),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
                **initial_data
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                options_json=pdd_options,
                count=count_domains,
                can_users_change_password=can_users_change_password,
                domain=domain,
            ),
        )

    def set_historydb_api_auths_aggregated(self, uid=TEST_UID, auths=None):
        self.env.historydb_api.set_response_value(
            'auths_aggregated',
            auths_aggregated_response(uid=uid, auths=auths),
        )

    def set_historydb_error(self, error):
        self.env.historydb_api.set_response_side_effect(
            'auths_aggregated',
            error,
        )

    def set_kikimr_response(self, *responses):
        self.env.fake_ydb.set_execute_side_effect([
            [FakeResultSet(response) for response in responses]
        ])

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)
        self.initial_data = deepcopy(TEST_ACCOUNT_FULL_DATA['account']['person'])
        self.initial_data['birthdate'] = self.initial_data.pop('birthday')
        self.initial_data['uid'] = TEST_UID
        self.initial_data['login'] = TEST_LOGIN
        self.initial_data['display_name'] = {'name': TEST_DISPLAY_NAME}
        self.initial_data['public_id'] = TEST_PUBLIC_ID
        self.set_blackbox_response()
        self.env.social_api.set_social_api_response_value(
            dict(profiles=[]),
        )
        self.set_historydb_api_auths_aggregated()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp, **TEST_ACCOUNT_FULL_DATA)

    def test_without_optional_fields_ok(self):
        self.set_blackbox_response(with_hint=True)
        profiles = [
            profile_item(
                person=social_api_person_item(firstname='Pusheen', lastname='TheCat'),
                subscriptions=[],
                expand_provider=True,
            ),
        ]
        self.env.social_api.set_social_api_response_value(dict(profiles=profiles))

        resp = self.make_request(
            query_args=dict(
                need_display_name_variants=False,
                need_phones=False,
                need_emails=False,
                need_social_profiles=False,
                need_question=False,
                need_additional_account_data=False,
            ),
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        for field in (
            'display_names',
            'phones',
            'emails',
            'profiles',
            'app_passwords_enabled',
            'lastauth',
            'security_level',
            'password_info',
        ):
            del expected_response['account'][field]
        self.assert_ok_response(resp, **expected_response)
        eq_(len(self.env.social_api.requests), 0)

    def test_display_names_incomplete_social_ok(self):
        social_account_data = deepcopy(self.initial_data)
        social_account_data.update(
            aliases={
                'social': TEST_LOGIN,
            },
        )
        self.set_blackbox_response(**social_account_data)

        profiles = [
            profile_item(
                person=social_api_person_item(firstname='Pusheen', lastname='TheCat'),
                subscriptions=[],
                expand_provider=True,
            ),
        ]
        self.env.social_api.set_social_api_response_value(dict(profiles=profiles))

        resp = self.make_request(query_args=dict(need_phones=False))

        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response[u'account'].update(dict(profiles=profiles))
        expected_response[u'account'][u'display_login'] = ''
        expected_response[u'account'][u'display_names'] = {
            name: 's:123:fb:%s' % name
            for name in (
                TEST_FIRSTNAME,
                TEST_LASTNAME,
                TEST_FULL_NAME,
                'some.user',
                'Pusheen',
                'TheCat',
                'Pusheen TheCat',
            )
        }
        del expected_response[u'account'][u'phones']
        self.assert_ok_response(resp, **expected_response)

    def test_display_names_complete_social_ok(self):
        profiles = [
            profile_item(
                person=social_api_person_item(firstname='Pusheen', lastname='TheCat'),
                subscriptions=[],
                expand_provider=True,
            ),
            profile_item(
                person=social_api_person_item(firstname=None, lastname=u'TheCat'),
                provider='vkontakte',
                subscriptions=[],
                expand_provider=True,
            ),
            profile_item(
                person=social_api_person_item(firstname=u'Пушин  ', lastname=u'  Котяра'),
                provider='google',
                subscriptions=[],
                expand_provider=True,
            ),
        ]
        self.env.social_api.set_social_api_response_value(dict(profiles=profiles))
        resp = self.make_request()
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response[u'account'].update(dict(profiles=profiles))
        expected_response[u'account'][u'display_names'].update({
            name: 'p:%s' % name
            for name in (
                'some.user',
                'Pusheen',
                'TheCat',
                'Pusheen TheCat',
                u'Пушин',
                u'Котяра',
                u'Пушин Котяра',
            )
        })
        self.assert_ok_response(resp, **expected_response)

    def test_complete_user_with_social_error_ok(self):
        self.env.social_api.set_social_api_response_value(dict(error=dict(description='Party is over')))
        resp = self.make_request()
        self.assert_ok_response(resp, **TEST_ACCOUNT_FULL_DATA)

    def test_incomplete_social_with_social_error_ok(self):
        social_account_data = deepcopy(self.initial_data)
        social_account_data.update(
            aliases={
                'social': TEST_LOGIN,
            },
        )
        self.set_blackbox_response(**social_account_data)
        self.env.social_api.set_social_api_response_value(dict(error=dict(description='Party is over')))

        resp = self.make_request()

        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response[u'account'].update(dict(profiles=[]))
        expected_response[u'account'][u'display_login'] = ''
        expected_response[u'account'][u'display_names'] = {
            name: 'p:%s' % name
            for name in (
                TEST_FIRSTNAME,
                TEST_LASTNAME,
                TEST_FULL_NAME,
            )
        }
        expected_response[u'account'][u'phones'][u'1']['alias'][u'email_allowed'] = False
        self.assert_ok_response(resp, **expected_response)

    def test_display_names_pdd_ok(self):
        pdd_account_data = deepcopy(self.initial_data)
        pdd_account_data.update(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            domain=TEST_DOMAIN,
            can_users_change_password='0',
        )
        self.set_blackbox_response(**pdd_account_data)

        resp = self.make_request(query_args=dict(need_phones=False))

        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            display_login=TEST_PDD_LOGIN,
            login=TEST_PDD_LOGIN,
            uid=TEST_PDD_UID,
            domain={
                u'punycode': TEST_DOMAIN,
                u'unicode': TEST_DOMAIN,
            },
            can_change_password=False,
        )
        expected_response['account']['display_names'].pop(TEST_LOGIN)
        expected_response['account']['display_names'].update({
            'login@okna.ru': TEST_PDD_DOMAIN_TEMPLATE,
        })
        del expected_response[u'account'][u'phones']
        self.assert_ok_response(resp, **expected_response)

    def test_child_ok(self):
        account_data = deepcopy(self.initial_data)
        account_data.update(
            attributes={
                'account.is_child': '1',
                'account.content_rating_class': '18',
            },
        )
        self.set_blackbox_response(**account_data)

        resp = self.make_request()

        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            is_child=True,
            content_rating_class=18,
        )
        self.assert_ok_response(resp, **expected_response)

    def test_pdd_cyrillic_domain_ok(self):
        pdd_account_data = deepcopy(self.initial_data)
        pdd_account_data.update(
            uid=TEST_PDD_UID,
            login=TEST_PDD_CYRILLIC_LOGIN,
            aliases={
                'pdd': TEST_PDD_CYRILLIC_LOGIN,
            },
            domain=TEST_CYRILLIC_DOMAIN,
            can_users_change_password='0',
        )
        self.set_blackbox_response(**pdd_account_data)

        resp = self.make_request(query_args=dict(need_phones=False))

        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            display_login=TEST_PDD_CYRILLIC_LOGIN,
            login=TEST_PDD_CYRILLIC_LOGIN,
            uid=TEST_PDD_UID,
            domain={
                u'punycode': TEST_CYRILLIC_DOMAIN_IDNA,
                u'unicode': TEST_CYRILLIC_DOMAIN,
            },
            can_change_password=False,
        )
        expected_response['account']['display_names'].pop(TEST_LOGIN)
        expected_response['account']['display_names'].update({
            TEST_PDD_CYRILLIC_LOGIN: TEST_PDD_DOMAIN_TEMPLATE,
        })
        del expected_response[u'account'][u'phones']
        self.assert_ok_response(resp, **expected_response)

    def test_with_question_present_ok(self):
        self.set_blackbox_response(with_hint=True)
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            question=dict(
                id=99,
                text=TEST_HINT_QUESTION_TEXT,
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_with_phone_operations(self):
        data = deepcopy(self.initial_data)
        data.update(
            build_remove_operation(
                TEST_OPERATION_ID,
                TEST_PHONE_ID1,
                started=TEST_OPERATION_STARTED_DT,
                code_last_sent=TEST_OPERATION_STARTED_DT,
            ),
        )
        self.set_blackbox_response(**data)
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account']['phones']['1'].update({
            'operation': {
                'id': TEST_OPERATION_ID,
                'type': 'remove',
                'is_secure_phone_operation': True,
                'started': TEST_OPERATION_STARTED_TS,
                'finished': TEST_OPERATION_FINISHED_TS,
                'does_user_admit_phone': True,
                'in_quarantine': False,
                'code': {
                    'send_count': 1,
                    'last_sent': TEST_OPERATION_STARTED_TS,
                    'checks_count': 0,
                },
            },
        })
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_rfc_2fa_enabled(self):
        account_data = deepcopy(self.initial_data)
        account_data.update(
            attributes={
                'account.rfc_2fa_on': True,
            },
        )
        self.set_blackbox_response(**account_data)
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            is_rfc_2fa_enabled=True,
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_app_passwords_and_2fa_enabled(self):
        account_data = deepcopy(self.initial_data)
        account_data.update(
            attributes={
                'account.enable_app_password': True,
                'account.2fa_on': True,
            },
        )
        self.set_blackbox_response(**account_data)
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            is_2fa_enabled=True,
            app_passwords_enabled=True,
            security_level=SECURITY_LEVEL_STRONG,
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_empty_auths_ok(self):
        self.set_historydb_api_auths_aggregated(auths=[])
        resp = self.make_request()
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response[u'account'].update(lastauth={})
        self.assert_ok_response(resp, **expected_response)

    def test_with_apps_auth_ok(self):
        auths = [
            auth_aggregated_item(
                ts=8,
                authtype=authtypes.AUTH_TYPE_POP3,
                ip_info=auth_aggregated_ip_info(
                    AS=9999,
                    ip='10.10.10.10',
                ),
            ),
            auth_aggregated_item(
                ts=10,
                authtype=authtypes.AUTH_TYPE_IMAP,
                ip_info=auth_aggregated_ip_info(
                    AS=9999,
                    ip='10.10.10.10',
                ),
            ),
            auth_aggregated_item(
                ts=3,
                authtype=authtypes.AUTH_TYPE_WEB,
                os_info=auth_aggregated_os_info('Ubuntu', '333'),
                browser_info=auth_aggregated_browser_info('Chrome', '555'),
                ip_info=auth_aggregated_ip_info(
                    AS=8888,
                    geoid=9999,
                    ip='8.8.8.8',
                ),
            ),
        ]
        self.set_historydb_api_auths_aggregated(auths=auths)
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response[u'account'].update(
            lastauth={
                'timestamp': 10,
                'authtype': 'imap',
                'ip': {
                    'AS': 9999,
                    'geoid': 9999,
                    'ip': '10.10.10.10',
                },
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_emails_with_phone_alias__search_enabled(self):
        account_data = deep_merge(
            self.initial_data,
            dict(
                aliases=dict(
                    portal=TEST_LOGIN,
                    phonenumber=TEST_PHONE_NUMBER.digital,
                ),
                attributes={'account.enable_search_by_phone_alias': '1'},
            ),
        )
        self.set_blackbox_response(**account_data)

        resp = self.make_request()

        expected_response = deep_merge(
            TEST_ACCOUNT_FULL_DATA,
            {
                'account': {
                    'emails': {
                        'phonenumber_aliases': sorted(TEST_PHONE_ALIAS_EMAILS),
                    },
                    'phones': {
                        '1': {
                            'is_alias': True,
                            'alias': {
                                'login_enabled': True,
                                'email_enabled': True,
                            },
                        },
                    },
                },
            },
        )
        self.assert_ok_response(resp, **expected_response)

    def test_emails_with_phone_alias__search_disabled(self):
        account_data = deep_merge(
            self.initial_data,
            dict(
                aliases=dict(
                    portal=TEST_LOGIN,
                    phonenumber=TEST_PHONE_NUMBER.digital,
                ),
            ),
        )
        self.set_blackbox_response(**account_data)

        resp = self.make_request()

        expected_response = deep_merge(
            TEST_ACCOUNT_FULL_DATA,
            {
                'account': {
                    'phones': {
                        '1': {
                            'is_alias': True,
                            'alias': {
                                'email_enabled': False,
                                'login_enabled': True,
                            },
                        },
                    },
                },
            },
        )
        self.assert_ok_response(resp, **expected_response)

    def test_weak_password_and_no_restore_methods(self):
        self.set_blackbox_response(
            with_password=True,
            weak_password=True,
            with_restore_emails=False,
            with_phone=False,
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account']['emails'].update(
            {
                'confirmed_external': [],
                'suitable_for_restore': [],
                'external': [],
            },
        )
        expected_response['account'].update(
            phones={},
            security_level=SECURITY_LEVEL_WEAK,
            password_info={
                'last_update': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'strength': PASSWORD_STRENGTH_STATUS_WEAK,
                'strong_policy_on': False,
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_weak_password_and_secure_phone(self):
        self.set_blackbox_response(
            with_password=True,
            weak_password=True,
            with_restore_emails=False,
            is_secure_phone=True,
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account']['emails'].update(
            {
                'confirmed_external': [],
                'suitable_for_restore': [],
                'external': [],
            },
        )
        expected_response['account']['phones'][str(TEST_PHONE_ID1)].update(
            {
                'is_default': True,
                'created': TEST_PHONE_CREATED_TS,
                'admitted': TEST_PHONE_CREATED_TS,
                'bound': TEST_PHONE_CREATED_TS,
                'confirmed': TEST_PHONE_CREATED_TS,
                'secured': TEST_PHONE_CREATED_TS,
            },
        )
        expected_response['account'].update(
            security_level=SECURITY_LEVEL_NORMAL,
            password_info={
                'last_update': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'strength': PASSWORD_STRENGTH_STATUS_WEAK,
                'strong_policy_on': False,
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_weak_password_and_email(self):
        self.set_blackbox_response(
            with_password=True,
            weak_password=True,
            with_phone=False,
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            phones={},
            security_level=SECURITY_LEVEL_NORMAL,
            password_info={
                'last_update': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'strength': PASSWORD_STRENGTH_STATUS_WEAK,
                'strong_policy_on': False,
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_weak_password_and_hint(self):
        self.set_blackbox_response(
            with_password=True,
            weak_password=True,
            with_hint=True,
            with_phone=False,
            with_native_emails=False,
            with_restore_emails=False,
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            phones={},
            question=dict(
                id=99,
                text=TEST_HINT_QUESTION_TEXT,
            ),
            emails={},
            security_level=SECURITY_LEVEL_WEAK,
            password_info={
                'last_update': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'strength': PASSWORD_STRENGTH_STATUS_WEAK,
                'strong_policy_on': False,
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_strong_password_and_no_restore_methods(self):
        self.set_blackbox_response(
            with_password=True,
            with_phone=False,
            with_restore_emails=False,
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account']['emails'].update(
            {
                'confirmed_external': [],
                'suitable_for_restore': [],
                'external': [],
            },
        )
        expected_response['account'].update(
            phones={},
            security_level=SECURITY_LEVEL_WEAK,
            password_info={
                'last_update': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'strength': PASSWORD_STRENGTH_STATUS_STRONG,
                'strong_policy_on': False,
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_strong_password_and_bound_phone(self):
        self.set_blackbox_response(
            with_password=True,
            with_native_emails=False,
            with_restore_emails=False,
            with_phone=True,
            is_bound_phone=True,
        )

        resp = self.make_request()

        expected_response = deep_merge(
            TEST_ACCOUNT_FULL_DATA,
            {
                'account': {
                    'security_level': SECURITY_LEVEL_STRONG,
                    'password_info': {
                        'last_update': TEST_PASSWORD_UPDATE_TIMESTAMP,
                        'strength': PASSWORD_STRENGTH_STATUS_STRONG,
                        'strong_policy_on': False,
                    },
                    'phones': {
                        str(TEST_PHONE_ID1): {
                            'is_default': True,
                            'created': TEST_PHONE_CREATED_TS,
                            'bound': TEST_PHONE_CREATED_TS,
                            'confirmed': TEST_PHONE_CREATED_TS,
                            'alias': {'email_allowed': False},
                        },
                    },
                },
            },
        )
        expected_response['account']['emails'] = dict()

        self.assert_ok_response(resp, **expected_response)

    def test_strong_password_and_email(self):
        self.set_blackbox_response(
            with_password=True,
            with_phone=False,
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            phones={},
            security_level=SECURITY_LEVEL_STRONG,
            password_info={
                'last_update': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'strength': PASSWORD_STRENGTH_STATUS_STRONG,
                'strong_policy_on': False,
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_strong_password_and_hint(self):
        self.set_blackbox_response(
            with_password=True,
            with_hint=True,
            with_phone=False,
            with_native_emails=False,
            with_restore_emails=False,
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            phones={},
            question=dict(
                id=99,
                text=TEST_HINT_QUESTION_TEXT,
            ),
            emails={},
            security_level=SECURITY_LEVEL_NORMAL,
            password_info={
                'last_update': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'strength': PASSWORD_STRENGTH_STATUS_STRONG,
                'strong_policy_on': False,
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_no_password_no_restore_methods_ok(self):
        self.set_blackbox_response(
            with_password=False,
            with_native_emails=False,
            with_restore_emails=False,
            with_phone=False,
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            phones={},
            emails={},
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_strong_policy_ok(self):
        self.set_blackbox_response(
            with_password=True,
            with_hint=False,
            with_phone=False,
            with_native_emails=False,
            with_restore_emails=False,
            strong_policy_required=True,
        )
        expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected_response['account'].update(
            phones={},
            emails={},
            security_level=SECURITY_LEVEL_WEAK,
            password_info={
                'last_update': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'strength': PASSWORD_STRENGTH_STATUS_STRONG,
                'strong_policy_on': True,
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **expected_response)

    def test_ok_intranet(self):
        self.set_blackbox_response(
            with_native_emails=False,
        )
        with settings_context(IS_INTRANET=True):
            resp = self.make_request()
        expected_response = deepcopy(TEST_ACCOUNT_DATA)
        expected_response['account'].pop('is_2fa_enabled')
        expected_response['account'].pop('is_yandexoid')
        expected_response['account'].pop('is_workspace_user')
        expected_response['account']['emails'] = {
            'confirmed_external': [
                'Musk@mail.ru',
            ],
            'default': None,
            'external': [
                'Musk@mail.ru',
            ],
            'native': [],
            'suitable_for_restore': [
                'Musk@mail.ru',
            ],
        }
        expected_response['account']['public_id'] = TEST_PUBLIC_ID
        self.assert_ok_response(resp, **expected_response)

    def test_historydb_unavailable_ok(self):
        for error in (HistoryDBApiTemporaryError, HistoryDBApiInvalidResponseError):
            self.set_historydb_error(error)
            resp = self.make_request()
            expected_response = deepcopy(TEST_ACCOUNT_FULL_DATA)
            expected_response[u'account'].update(lastauth={})
            self.assert_ok_response(resp, **expected_response)

    def test_family_info(self):
        self.set_blackbox_response(
            family_info=TEST_FAMILY_INFO,
        )
        resp = self.make_request(
            query_args=dict(
                need_family_info=True,
            ),
        )
        expected = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected['account'].update({
            'family_info': TEST_FAMILY_INFO,
        })
        expected.update({
            'family_settings': {
                'max_capacity': TEST_FAMILY_MAX_SIZE,
                'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
            },
        })
        self.assert_ok_response(resp, **expected)

    def test_family_info_no_family(self):
        self.set_blackbox_response(
            family_info={},
        )
        resp = self.make_request(
            query_args=dict(
                need_family_info=True,
            ),
        )
        expected = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected.update({
            'family_settings': {
                'max_capacity': TEST_FAMILY_MAX_SIZE,
                'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
            },
        })
        self.assert_ok_response(resp, **expected)

    def test_family_info_with_members(self):
        self.set_blackbox_response(
            family_info=TEST_FAMILY_INFO,
            family_members=[TEST_UID, TEST_UID1, TEST_UID2],
        )
        resp = self.make_request(
            query_args=dict(
                need_family_info=True,
                need_family_members=True,
            ),
        )
        expected = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected['account'].update({
            'family_info': TEST_FAMILY_INFO,
        })
        expected.update({
            'family_settings': {
                'max_capacity': TEST_FAMILY_MAX_SIZE,
                'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
            },
            'family_members': [
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'display_name': TEST_PUBLIC_NAME,
                    'uid': uid,
                    'place_id': '%s:%s' % (TEST_FAMILY_ID, place),
                    'has_plus': True,
                } for uid, place in zip([TEST_UID, TEST_UID1, TEST_UID2], range(3))
            ],
        })
        self.assert_ok_response(resp, **expected)

    def test_family_info_with_kids(self):
        self.set_blackbox_response(
            family_info=TEST_FAMILY_INFO,
            family_members=[TEST_UID],
            family_kids=[TEST_UID1],
        )

        resp = self.make_request(query_args=dict(need_family_kids=True))

        expected = deep_merge(
            TEST_ACCOUNT_FULL_DATA,
            {
                'account': {
                    'family_info': TEST_FAMILY_INFO,
                },
                'family_kids': [
                    {
                        'display_login': 'test',
                        'has_plus': True,
                        'login': 'test',
                        'place_id': '%s:%s' % (TEST_FAMILY_ID, 100),
                        'uid': TEST_UID1,
                        'display_name': {
                            'default_avatar': TEST_AVATAR_KEY,
                            'name': TEST_DISPLAY_NAME_DATA.get('name'),
                        },
                        'person': {
                            'birthday': TEST_BIRTHDATE1,
                            'country': 'ru',
                            'firstname': TEST_FIRSTNAME,
                            'gender': 1,
                            'language': 'ru',
                            'lastname': TEST_LASTNAME,
                        },
                    },
                ],
                'family_settings': {
                    'max_capacity': TEST_FAMILY_MAX_SIZE,
                    'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
                },
            },
        )
        self.assert_ok_response(resp, **expected)

    def test_family_info_with_members_no_family(self):
        self.set_blackbox_response(
            family_info={},
        )
        resp = self.make_request(
            query_args=dict(
                need_family_info=True,
                need_family_members=True,
            ),
        )
        expected = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected.update({
            'family_settings': {
                'max_capacity': TEST_FAMILY_MAX_SIZE,
                'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
            },
        })
        self.assert_ok_response(resp, **expected)

    def test_family_invites(self):
        self.set_blackbox_response(
            family_info=TEST_FAMILY_INFO,
        )
        invites = [TEST_FAMILY_INVITE1, TEST_FAMILY_INVITE2]
        self.set_kikimr_response(invites)
        resp = self.make_request(
            query_args=dict(
                need_family_info=True,
                need_family_invites=True,
            ),
        )
        expected = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected['account'].update({
            'family_info': TEST_FAMILY_INFO,
        })
        expected.update({
            'family_settings': {
                'max_capacity': TEST_FAMILY_MAX_SIZE,
                'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
            },
            'family_invites': [
                {
                    'invite_id': invite['invite_id'],
                    'family_id': 'f%s' % invite['family_id'],
                    'issuer_uid': invite['issuer_uid'],
                    'create_time': int(invite['create_time']/1000000),
                    'send_method': FamilyInvite.send_method_to_text(invite['send_method']),
                    'contact': invite['contact'],
                } for invite in invites
            ],
        })
        self.assert_ok_response(resp, **expected)

    def test_family_invites_no_family(self):
        self.set_blackbox_response(
            family_info={},
        )
        invites = [TEST_FAMILY_INVITE1, TEST_FAMILY_INVITE2]
        self.set_kikimr_response(invites)
        resp = self.make_request(
            query_args=dict(
                need_family_info=True,
                need_family_invites=True,
            ),
        )
        expected = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected.update({
            'family_settings': {
                'max_capacity': TEST_FAMILY_MAX_SIZE,
                'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
            },
        })
        self.assert_ok_response(resp, **expected)

    def test_family_invites_not_admin(self):
        family_info = deepcopy(TEST_FAMILY_INFO)
        family_info['admin_uid'] = TEST_UID2
        self.set_blackbox_response(
            family_info=family_info,
        )
        invites = [TEST_FAMILY_INVITE1, TEST_FAMILY_INVITE2]
        self.set_kikimr_response(invites)
        resp = self.make_request(
            query_args=dict(
                need_family_info=True,
                need_family_invites=True,
            ),
        )
        expected = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected['account'].update({
            'family_info': family_info,
        })
        expected.update({
            'family_settings': {
                'max_capacity': TEST_FAMILY_MAX_SIZE,
                'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
            },
        })
        self.assert_ok_response(resp, **expected)

    def test_family_altogether(self):
        self.set_blackbox_response(
            family_info=TEST_FAMILY_INFO,
            family_members=[TEST_UID, TEST_UID1, TEST_UID2],
            family_members_places=[3, 0, 1],
        )
        invites = [TEST_FAMILY_INVITE1, TEST_FAMILY_INVITE2]
        self.set_kikimr_response(invites)
        resp = self.make_request(
            query_args=dict(
                need_family_members=True,
                need_family_invites=True,
            ),
        )
        expected = deepcopy(TEST_ACCOUNT_FULL_DATA)
        expected['account'].update({
            'family_info': TEST_FAMILY_INFO,
        })
        expected.update({
            'family_settings': {
                'max_capacity': TEST_FAMILY_MAX_SIZE,
                'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
            },
            'family_members': [
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'display_name': TEST_PUBLIC_NAME,
                    'uid': uid,
                    'place_id': '%s:%s' % (TEST_FAMILY_ID, place),
                    'has_plus': True,
                } for uid, place in zip([TEST_UID, TEST_UID1, TEST_UID2], [3, 0, 1])
            ],
        })
        expected.update({
            'family_invites': [
                {
                    'invite_id': invite['invite_id'],
                    'family_id': 'f%s' % invite['family_id'],
                    'issuer_uid': invite['issuer_uid'],
                    'create_time': int(invite['create_time'] / 1000000),
                    'send_method': FamilyInvite.send_method_to_text(
                        invite['send_method']),
                    'contact': invite['contact'],
                } for invite in invites
            ],
        })
        self.assert_ok_response(resp, **expected)
