# -*- coding: utf-8 -*-
from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.account.account_options import (
    ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT,
    ACCOUNT_IS_ENABLED_GRANT,
    ACCOUNT_IS_MAILLIST_GRANT,
    ACCOUNT_IS_SHARED_GRANT,
    ACCOUNT_OPTIONS_ANY_GRANT,
    ACCOUNT_OPTIONS_BASE_GRANT,
    ACCOUNT_OPTIONS_NORMAL_GRANT,
    ACCOUNT_OPTIONS_PDD_GRANT,
    LOG_ADMIN_ACTION_GRANT,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.federal_configs_api import FederalConfigsApiNotFoundError
from passport.backend.core.builders.federal_configs_api.faker import federal_config_ok
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.account.account import PDD_UID_BOUNDARY
from passport.backend.utils.common import merge_dicts


TEST_LOGIN = 'login'
TEST_UID = 1
TEST_PDD_LOGIN = 'login@okna.ru'
TEST_PDD_UID = PDD_UID_BOUNDARY + 1
TEST_ADMIN_LOGIN = 'test-admin'
TEST_COMMENT = 'comment'

TEST_ALIAS_TYPES = [
    'portal',
    'pdd',
    'lite',
    'mailish',
    'social',
    'phonish',
    'kinopoisk',
    'uber',
    'kolonkish',
    'yambot',
]


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class TestAccountOptionsView(BaseBundleTestViews):

    default_url = '/1/account/%d/options/?consumer=dev' % TEST_UID
    http_method = 'post'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.setup_grants()

        self.accounts_table = 'accounts'
        self.subscriptions_table = 'subscription'
        self.attributes_table = 'attributes'
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok())

    def tearDown(self):
        self.env.stop()
        del self.env

    def construct_userinfo_response(self, uid=TEST_UID, login=TEST_LOGIN, **kwargs):
        response_args = {
            'uid': uid,
            'login': login,
            'subscribed_to': None,
            'dbfields': {},
            'attributes': {},
        }
        return blackbox_userinfo_response(
            **merge_dicts(
                response_args,
                kwargs,
            )
        )

    def setup_grants(self, *args):
        base_prefix, suffix = ACCOUNT_OPTIONS_BASE_GRANT.split('.')
        grants = {
            base_prefix: [
                suffix,
            ],
        }

        for grant in args:
            prefix, suffix = grant.split('.')
            grants.setdefault(prefix, []).append(suffix)

        self.env.grants.set_grants_return_value(mock_grants(grants=grants))

    def set_and_serialize_userinfo(self, blackbox_response):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.env.db.serialize(blackbox_response)

    def check_db_ok(self, centraldb_query_count=0, sharddb_query_count=0,
                    uid=TEST_UID, **options):
        is_pdd = uid > PDD_UID_BOUNDARY
        shard_name = 'passportdbshard%i' % (1 if not is_pdd else 2)

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count(shard_name), sharddb_query_count)

        options_to_attrs = {
            'is_disabled': 'account.is_disabled',
            'is_app_password_enabled': 'account.enable_app_password',
            'is_shared': 'account.is_shared',
            'is_maillist': 'account.is_maillist',
            'is_employee': 'account.is_employee',
        }

        for option_name, attribute in options_to_attrs.items():
            if options.get(option_name, False):
                self.env.db.check(
                    self.attributes_table,
                    attribute,
                    '1',
                    uid=uid,
                    db=shard_name,
                )
            else:
                self.env.db.check_missing(
                    self.attributes_table,
                    attribute,
                    uid=uid,
                    db=shard_name,
                )

    def check_events_ok(self, comment=None, admin_name=None, **options):
        expected_log_entries = {
            'action': 'account',
            'consumer': 'dev',
        }

        if 'is_disabled' in options:
            options['is_disabled'] = not options['is_disabled']

        options_to_fields = {
            'is_disabled': 'info.ena',
            'is_app_password_enabled': 'info.enable_app_password',
            'is_shared': 'info.is_shared',
            'is_maillist': 'info.is_maillist',
            'is_employee': 'info.is_employee',
        }

        for name, expected in options.items():
            expected_log_entries[options_to_fields[name]] = tskv_bool(expected)
            if name == 'is_disabled':
                expected_log_entries['info.disabled_status'] = tskv_bool(not expected)

        if admin_name and comment:
            expected_log_entries['admin'] = admin_name
            expected_log_entries['comment'] = comment
        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.construct_userinfo_response(uid=None),
        )
        self.setup_grants()
        resp = self.make_request(query_args=dict(is_enabled='yes'))
        self.assert_error_response(resp, ['account.not_found'])

    def test_grant_missing_is_enabled_fails(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT,
            ACCOUNT_IS_SHARED_GRANT,
        )
        resp = self.make_request(query_args=dict(is_enabled='yes'))
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_grant_missing_is_app_password_enabled_fails(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_SHARED_GRANT,
        )
        resp = self.make_request(query_args=dict(is_app_password_enabled='yes'))
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_grant_missing_is_shared_fails(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_ENABLED_GRANT,
            ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT,
        )
        resp = self.make_request(query_args=dict(is_shared='yes'))
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_is_enabled_true_works(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_ENABLED_GRANT,
        )
        resp = self.make_request(query_args=dict(is_enabled='yes'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_is_enabled_false_works(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_ENABLED_GRANT,
        )
        resp = self.make_request(query_args=dict(is_enabled='no'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_disabled=True,
        )
        self.check_events_ok(is_disabled=True)

    def test_is_app_password_enabled_works(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT,
        )
        resp = self.make_request(query_args=dict(is_app_password_enabled='yes'))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=1,
            is_app_password_enabled=True,
        )
        self.check_events_ok(is_app_password_enabled=True)

    def test_is_shared_works(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_SHARED_GRANT,
        )
        resp = self.make_request(query_args=dict(is_shared='yes'))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=1,
            is_shared=True,
        )
        self.check_events_ok(is_shared=True)

    def test_is_maillist_works_on_pdd(self):
        userinfo_response = self.construct_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
        )

        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_PDD_GRANT,
            ACCOUNT_IS_MAILLIST_GRANT,
        )
        resp = self.make_request(query_args=dict(is_maillist='yes'))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=2,
            uid=TEST_PDD_UID,
            is_maillist=True,
            is_employee=False,
        )
        self.check_events_ok(is_maillist=True, is_employee=False)

    def test_is_maillist_doesnt_work_on_pdd_admin(self):
        userinfo_response = self.construct_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
            subscribed_to={
                '104': '1',
            },
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_PDD_GRANT,
            ACCOUNT_IS_MAILLIST_GRANT,
        )
        resp = self.make_request(query_args=dict(is_maillist='yes'))
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_is_maillist_doesnt_work_on_regular_user(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_MAILLIST_GRANT,
        )
        resp = self.make_request(query_args=dict(is_maillist='yes'))
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_is_maillist_off_works_if_not_sso_domain(self):
        self.env.federal_configs_api.set_response_side_effect('config_by_domain_id', FederalConfigsApiNotFoundError())
        userinfo_response = self.construct_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
            attributes={
                str(AT['account.is_maillist']): '1',
            },
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_PDD_GRANT,
            ACCOUNT_IS_MAILLIST_GRANT,
        )
        resp = self.make_request(query_args=dict(is_maillist='no'))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=2,
            uid=TEST_PDD_UID,
            is_maillist=False,
            is_employee=True,
        )
        self.check_events_ok(is_maillist=False, is_employee=True)

    def test_is_maillist_off_impossible_if_sso_domain(self):
        userinfo_response = self.construct_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
            attributes={
                str(AT['account.is_maillist']): '1',
            },
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_PDD_GRANT,
            ACCOUNT_IS_MAILLIST_GRANT,
        )
        resp = self.make_request(query_args=dict(is_maillist='no'))
        self.assert_error_response(
            resp,
            ['action.impossible'],
        )

    def test_all_options_for_pdd_user_at_once_works(self):
        userinfo_response = self.construct_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_PDD_GRANT,
            ACCOUNT_IS_ENABLED_GRANT,
            ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT,
            ACCOUNT_IS_SHARED_GRANT,
            ACCOUNT_IS_MAILLIST_GRANT,
        )

        resp = self.make_request(query_args=dict(
            is_enabled='no',
            is_app_password_enabled='1',
            is_shared='yes',
            is_maillist='yes',
        ))
        self.assert_ok_response(resp)

        updated_fields = {
            'is_disabled': True,
            'is_app_password_enabled': True,
            'is_shared': True,
            'is_maillist': True,
            'is_employee': False,
        }

        self.check_db_ok(
            sharddb_query_count=2,
            uid=TEST_PDD_UID,
            **updated_fields
        )
        self.check_events_ok(**updated_fields)

    def test_all_options_for_regular_user_at_once_works(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_ENABLED_GRANT,
            ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT,
            ACCOUNT_IS_SHARED_GRANT,
        )

        resp = self.make_request(query_args=dict(
            is_enabled='no',
            is_app_password_enabled='1',
            is_shared='yes',
        ))
        self.assert_ok_response(resp)

        updated_fields = {
            'is_disabled': True,
            'is_app_password_enabled': True,
            'is_shared': True,
        }
        self.check_db_ok(
            sharddb_query_count=1,
            **updated_fields
        )
        self.check_events_ok(**updated_fields)

    def test_is_enabled_without_comment_works(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_ENABLED_GRANT,
        )
        resp = self.make_request(query_args=dict(is_enabled='no'))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=1,
            is_disabled=True,
        )
        self.check_events_ok(is_disabled=True, comment='-')

    def test_event_with_admin_name_and_comment_is_logged(self):
        userinfo_response = self.construct_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ACCOUNT_OPTIONS_NORMAL_GRANT,
            ACCOUNT_IS_ENABLED_GRANT,
            LOG_ADMIN_ACTION_GRANT,
        )

        resp = self.make_request(query_args=dict(
            is_enabled='no',
            admin_name=TEST_ADMIN_LOGIN,
            comment=TEST_COMMENT,
        ))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=1,
            is_disabled=True,
        )
        self.check_events_ok(
            is_disabled=True,
            admin_name=TEST_ADMIN_LOGIN,
            comment=TEST_COMMENT,
        )

    @parameterized.expand([
        (alias_type, )
        for alias_type in TEST_ALIAS_TYPES
    ])
    def test_check_any_account_type_without_grant_fails(self, alias_type):
        self.setup_grants(
            ACCOUNT_IS_ENABLED_GRANT,
        )

        userinfo_response = self.construct_userinfo_response(
            aliases={alias_type: TEST_PDD_LOGIN},
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(query_args=dict(is_maillist='yes'))
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    @parameterized.expand([
        (alias_type, )
        for alias_type in TEST_ALIAS_TYPES
    ])
    def test_check_any_account_type_with_grant_any_succeeds(self, alias_type):
        self.setup_grants(
            ACCOUNT_OPTIONS_ANY_GRANT,
            ACCOUNT_IS_ENABLED_GRANT,
        )

        userinfo_response = self.construct_userinfo_response(
            aliases={alias_type: TEST_PDD_LOGIN},
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(query_args=dict(is_enabled='yes'))
        self.assert_ok_response(resp)
