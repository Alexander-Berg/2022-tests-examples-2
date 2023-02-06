# -*- coding: utf-8 -*-
from datetime import date
import json
import time

from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_OAUTH_SCOPE
from passport.backend.api.views.bundle.account.options.forms import (
    OTT_SUBSCRIPTIONS,
    PLUS_FAMILY_ROLES,
)
from passport.backend.api.views.bundle.account.options.grants import (
    ACCOUNT_AUDIENCE_ON_GRANT_PREFIX,
    ACCOUNT_FAMILY_PAY_ENABLED_GRANT_PREFIX,
    ACCOUNT_FORCE_CHALLENGE_GRANT_PREFIX,
    ACCOUNT_FORRBID_DISABLING_SMS_2FA_GRANT_PREFIX,
    ACCOUNT_GLOBAL_LOGOUT_GRANT,
    ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT,
    ACCOUNT_IS_CONNECT_ADMIN_GRANT,
    ACCOUNT_IS_DOCUMENTS_AGREEMENT_ACCEPTED_GRANT_PREFIX,
    ACCOUNT_IS_DZEN_SSO_PROHIBITED_GRANT_PREFIX,
    ACCOUNT_CAN_MANAGE_CHILDREN_GRANT_PREFIX,
    ACCOUNT_IS_EASILY_HACKED_GRANT,
    ACCOUNT_IS_ENABLED_GRANT,
    ACCOUNT_IS_MAILBOX_FROZEN_GRANT_PREFIX,
    ACCOUNT_IS_MAILLIST_GRANT,
    ACCOUNT_IS_SHARED_GRANT,
    ACCOUNT_IS_SHARED_GRANT_PREFIX,
    ACCOUNT_OPTIONS_ANY_GRANT,
    ACCOUNT_OPTIONS_BASE_GRANT,
    ACCOUNT_OPTIONS_PDD_GRANT,
    ACCOUNT_OPTIONS_PHONISH_GRANT,
    ACCOUNT_PERSONAL_DATA_PUBLIC_ACCESS_ALLOWED_GRANT_PREFIX,
    ACCOUNT_PERSONAL_DATA_THIRD_PARTY_PROCESSING_ALLOWED_GRANT_PREFIX,
    ACCOUNT_PLUS_CASHBACK_ENABLED_GRANT_PREFIX,
    ACCOUNT_PLUS_ENABLED_GRANT_PREFIX,
    ACCOUNT_PLUS_FAMILY_ROLE_GRANT_PREFIX,
    ACCOUNT_PLUS_IS_FROZEN_GRANT_PREFIX,
    ACCOUNT_PLUS_NEXT_CHARGE_TS_GRANT_PREFIX,
    ACCOUNT_PLUS_OTT_SUBSCRIPTION_GRANT_PREFIX,
    ACCOUNT_PLUS_SUBSCRIBER_STATE_GRANT_PREFIX,
    ACCOUNT_PLUS_SUBSCRIPTION_EXPIRE_TS_GRANT_PREFIX,
    ACCOUNT_PLUS_SUBSCRIPTION_LEVEL_GRANT_PREFIX,
    ACCOUNT_PLUS_SUBSCRIPTION_STOPPED_TS_GRANT_PREFIX,
    ACCOUNT_PLUS_TRIAL_USED_TS_GRANT_PREFIX,
    ACCOUNT_REVOKE_APP_PASSWORDS_GRANT,
    ACCOUNT_REVOKE_TOKENS_GRANT,
    ACCOUNT_REVOKE_WEB_SESSIONS_GRANT,
    ACCOUNT_SET_BILLING_FEATURES_GRANT,
    ACCOUNT_SHOW_2FA_PROMO_GRANT,
    ACCOUNT_SMS_2FA_ON_GRANT_PREFIX,
    ALLOW_TAKEOUT_DELETE_SUBSCRIPTION_GRANT_PREFIX,
    ALLOW_TAKEOUT_SUBSCRIPTION_GRANT,
    ALLOW_TAKEOUT_SUBSCRIPTION_GRANT_PREFIX,
    DISABLE_AUTH_METHODS_GRANT,
    DISABLE_AUTH_METHODS_GRANT_PREFIX,
    EXTERNAL_ORGANIZATION_IDS_GRANT,
    EXTERNAL_ORGANIZATION_IDS_GRANT_PREFIX,
    LOG_ADMIN_ACTION_GRANT,
    PASSWORD_IS_CHANGING_REQUIRED_GRANT,
    PASSWORD_UPDATE_DATETIME_GRANT,
    PERSON_SHOW_FIO_IN_PUBLIC_NAME_GRANT_PREFIX,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.datasync_api.faker.fake_disk_api import (
    disk_error_response,
    plus_subscribe_created_response,
    plus_subscribe_removed_response,
)
from passport.backend.core.builders.federal_configs_api import FederalConfigsApiNotFoundError
from passport.backend.core.builders.federal_configs_api.faker import federal_config_ok
from passport.backend.core.builders.yasms.faker import (
    DEFAULT_PHONE_NUMBER,
    yasms_send_sms_response,
)
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.account import (
    MAIL_STATUS_ACTIVE,
    MAIL_STATUS_FROZEN,
)
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.consts import (
    TEST_PLUS_SUBSCRIBER_STATE1_BASE64,
    TEST_PLUS_SUBSCRIBER_STATE1_JSON,
    TEST_PLUS_SUBSCRIBER_STATE1_PROTO,
    TEST_USER_TICKET1,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    unixtime_to_statbox_datetime,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    fake_user_ticket,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_CLIENT_ID_2,
    TEST_TICKET,
)
from passport.backend.core.types.account.account import PDD_UID_BOUNDARY
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import get_unixtime


TEST_LOGIN = 'login'
TEST_UID = 1
TEST_DOMAIN = 'okna.ru'
TEST_PDD_LOGIN = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)
TEST_PDD_UID = PDD_UID_BOUNDARY + 1
TEST_ADMIN_LOGIN = 'test-admin'
TEST_COMMENT = 'comment'
TEST_IP = '127.0.0.1'
TEST_TIMESTAMP = 12345678
TEST_PASSWORD_UPDATE_TIMESTAMP = 1234567
TEST_PASSWORD_HASH = '1:pwd'
TEST_USER_AGENT = 'curl'

ALL_OLD_STYLE_GRANTS = (
    ACCOUNT_GLOBAL_LOGOUT_GRANT,
    ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT,
    ACCOUNT_IS_ENABLED_GRANT,
    ACCOUNT_IS_MAILLIST_GRANT,
    ACCOUNT_IS_SHARED_GRANT,
    ACCOUNT_OPTIONS_ANY_GRANT,
    ACCOUNT_OPTIONS_BASE_GRANT,
    ACCOUNT_OPTIONS_PDD_GRANT,
    ACCOUNT_OPTIONS_PHONISH_GRANT,
    ACCOUNT_REVOKE_APP_PASSWORDS_GRANT,
    ACCOUNT_REVOKE_TOKENS_GRANT,
    ACCOUNT_REVOKE_WEB_SESSIONS_GRANT,
    ACCOUNT_SET_BILLING_FEATURES_GRANT,
    ACCOUNT_SHOW_2FA_PROMO_GRANT,
    ALLOW_TAKEOUT_SUBSCRIPTION_GRANT,
    DISABLE_AUTH_METHODS_GRANT,
    EXTERNAL_ORGANIZATION_IDS_GRANT,
    LOG_ADMIN_ACTION_GRANT,
    PASSWORD_IS_CHANGING_REQUIRED_GRANT,
    PASSWORD_UPDATE_DATETIME_GRANT,
)


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'login_method_change'},
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'login_method_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:login_method_change': 5,
            'email:login_method_change': 5,
        },
    )
)
class BaseAccountOptionsTestView(BaseBundleTestViews, AccountModificationNotifyTestMixin, EmailTestMixin):

    default_url = '/2/account/%d/options/?consumer=dev' % TEST_UID
    http_method = 'post'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.setup_statbox_templates()

        self.accounts_table = 'accounts'
        self.subscriptions_table = 'subscription'
        self.attributes_table = 'attributes'
        self.start_account_modification_notify_mocks(
            ip=TEST_IP,
        )
        self.setup_kolmogor()
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok())

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            uid=str(TEST_UID),
            consumer='dev',
            consumer_ip=TEST_IP,
        )
        self.env.statbox.bind_entry(
            'is_changing_required',
            _exclude=['consumer_ip'],
            entity='password.is_changing_required',
            operation='created',
            event='account_modification',
            ip=TEST_IP,
            user_agent='-',
            new='1',
            old='-',
        )
        self.env.statbox.bind_entry(
            'notification_sent',
            unixtime=TimeNow(),
            mode='account_options',
            action='password_options.notification_sent',
            number='+79031******',
            sms_id='1',
        )
        self.env.statbox.bind_entry(
            'loaded_secure_number',
            unixtime=TimeNow(),
            mode='account_options',
            action='loaded_secure_number',
            error='invalid_phone_number',
        )

    def get_common_user_profile(self, uid=TEST_UID, login=TEST_LOGIN, enabled_2fa=False,
                                has_password=True, password_update_datetime=TEST_PASSWORD_UPDATE_TIMESTAMP,
                                lite=False, with_secure_phone=False, is_child=False, **kwargs):
        common_kwargs = {
            'uid': uid,
            'login': login,
            'subscribed_to': None,
            'dbfields': {},
            'attributes': {
                'password.update_datetime': password_update_datetime,
                'account.2fa_on': '1' if enabled_2fa else None,
                'account.is_child': '1' if is_child else None,
            },
            'crypt_password': TEST_PASSWORD_HASH if has_password else None,
        }
        if lite:
            common_kwargs.update({
                'aliases': {'lite': login},
            })
        if with_secure_phone:
            phone_secured = build_phone_secured(
                1,
                DEFAULT_PHONE_NUMBER,
            )
            common_kwargs = deep_merge(common_kwargs, phone_secured)

        return deep_merge(common_kwargs, kwargs)

    def setup_blackbox_responses_and_serialize(self, uid=TEST_UID, login=TEST_LOGIN, enabled_2fa=False,
                                               has_password=True, password_update_datetime=TEST_PASSWORD_UPDATE_TIMESTAMP,
                                               lite=False, with_secure_phone=False, **kwargs):

        common_kwargs = self.get_common_user_profile(uid, login, enabled_2fa, has_password, password_update_datetime, lite, with_secure_phone, **kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**common_kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=TEST_OAUTH_SCOPE, **common_kwargs),
        )
        userinfo_response = blackbox_userinfo_response(**common_kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        if common_kwargs.get('uid'):
            self.env.db.serialize(userinfo_response)

    def setup_grants(self, *args):
        prefix, suffix = ACCOUNT_OPTIONS_BASE_GRANT.split('.')
        grants = {prefix: [suffix]}
        for grant in args:
            prefix, suffix = grant.split('.', 1)
            grants.setdefault(prefix, []).append(suffix)
        self.env.grants.set_grants_return_value(mock_grants(grants=grants))

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def check_db_ok(self, centraldb_query_count=0, sharddb_query_count=0, uid=TEST_UID,
                    **options):
        is_pdd = uid > PDD_UID_BOUNDARY
        shard_name = 'passportdbshard%i' % (1 if not is_pdd else 2)

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count(shard_name), sharddb_query_count)

        if options.get('password_update_timestamp') is None:
            options['password_update_timestamp'] = str(TEST_PASSWORD_UPDATE_TIMESTAMP)

        other_options_to_attrs = {
            'is_disabled': 'account.is_disabled',
            'is_app_password_enabled': 'account.enable_app_password',
            'is_shared': 'account.is_shared',
            'is_maillist': 'account.is_maillist',
            'is_employee': 'account.is_employee',
            'is_connect_admin': 'account.is_connect_admin',
            'is_easily_hacked': 'account.is_easily_hacked',
            'is_password_change_required': 'password.forced_changing_reason',
            'show_2fa_promo': 'account.show_2fa_promo',
            'glogout': 'account.global_logout_datetime',
            'tokens_revoked_at': 'revoker.tokens',
            'app_passwords_revoked_at': 'revoker.app_passwords',
            'web_sessions_revoked_at': 'revoker.web_sessions',
            'password_update_timestamp': 'password.update_datetime',
            'audience_on': 'account.audience_on',
            'external_organization_ids': 'account.external_organization_ids',
            'magic_link_login_forbidden': 'account.magic_link_login_forbidden',
            'qr_code_login_forbidden': 'account.qr_code_login_forbidden',
            'sms_code_login_forbidden': 'account.sms_code_login_forbidden',
            'takeout_subscription': 'takeout.subscription',
            'billing_features': 'account.billing_features',
            'show_fio_in_public_name': 'person.show_fio_in_public_name',
            'force_challenge': 'account.force_challenge',
            'sms_2fa_on': 'account.sms_2fa_on',
            'forbid_disabling_sms_2fa': 'account.forbid_disabling_sms_2fa',
            'takeout_delete_subscription': 'takeout.delete.subscription',
            'mail_status': 'subscription.mail.status',
            'family_pay_enabled': 'account.family_pay.enabled',
            'plus_enabled':  'account.plus.enabled',
            'plus_trial_used_ts': 'account.plus.trial_used_ts',
            'plus_subscription_stopped_ts': 'account.plus.subscription_stopped_ts',
            'plus_subscription_expire_ts': 'account.plus.subscription_expire_ts',
            'plus_next_charge_ts': 'account.plus.next_charge_ts',
            'ott_subscription': 'account.plus.ott_subscription',
            'plus_family_role': 'account.plus.family_role',
            'plus_cashback_enabled': 'account.plus.cashback_enabled',
            'plus_subscription_level': 'account.plus.subscription_level',
            'plus_is_frozen': 'account.plus.is_frozen',
            'plus_subscriber_state': 'account.plus.subscriber_state',
            'is_documents_agreement_accepted': 'account.is_documents_agreement_accepted',
            'is_dzen_sso_prohibited': 'account.is_dzen_sso_prohibited',
            'can_manage_children': 'account.can_manage_children',
        }

        for option_name, attribute in other_options_to_attrs.items():
            option_value = options.get(option_name)
            if isinstance(option_value, bool):
                option_value = '1' if option_value else None

            if option_value:
                self.env.db.check(
                    self.attributes_table,
                    attribute,
                    option_value,
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

    def check_events_ok(self, comment=None, admin_name=None, user_agent=None, **options):
        expected_log_entries = {
            'action': 'account',
            'consumer': 'dev',
        }

        if user_agent:
            expected_log_entries['user_agent'] = user_agent

        if 'is_disabled' in options:
            options['is_enabled'] = not options.pop('is_disabled')

        if options.get('is_password_change_required') is not None:
            sid8_login_rule = 5 if options.pop('is_password_change_required') else 1
            options['sid_login_rule'] = '8|%d' % sid8_login_rule

        options_to_fields = {
            'is_enabled': 'info.ena',
            'is_app_password_enabled': 'info.enable_app_password',
            'is_shared': 'info.is_shared',
            'is_maillist': 'info.is_maillist',
            'is_employee': 'info.is_employee',
            'is_connect_admin': 'info.is_connect_admin',
            'is_easily_hacked': 'info.is_easily_hacked',
            'sid_login_rule': 'sid.login_rule',
            'glogout': 'info.glogout',
            'tokens_revoked_at': 'info.tokens_revoked',
            'app_passwords_revoked_at': 'info.app_passwords_revoked',
            'web_sessions_revoked_at': 'info.web_sessions_revoked',
            'password_update_timestamp': 'info.password_update_time',
            'audience_on': 'info.audience_on',
            'external_organization_ids': 'info.external_organization_ids',
            'magic_link_login_forbidden': 'info.magic_link_login_forbidden',
            'qr_code_login_forbidden': 'info.qr_code_login_forbidden',
            'sms_code_login_forbidden': 'info.sms_code_login_forbidden',
            'takeout_subscription': 'takeout.subscription',
            'billing_features': 'account.billing_features',
            'show_fio_in_public_name': 'info.show_fio_in_public_name',
            'force_challenge': 'account.force_challenge',
            'sms_2fa_on': 'info.sms_2fa_on',
            'forbid_disabling_sms_2fa': 'info.forbid_disabling_sms_2fa',
            'takeout_delete_subscription': 'takeout.delete.subscription',
            'mail_status': 'info.mail_status',
            'personal_data_public_access_allowed': 'account.personal_data_public_access_allowed',
            'personal_data_third_party_processing_allowed': 'account.personal_data_third_party_processing_allowed',
            'family_pay_enabled': 'account.family_pay.enabled',
            'plus_enabled': 'plus.enabled',
            'plus_trial_used_ts': 'plus.trial_used_ts',
            'plus_subscription_stopped_ts': 'plus.subscription_stopped_ts',
            'plus_subscription_expire_ts': 'plus.subscription_expire_ts',
            'plus_next_charge_ts': 'plus.next_charge_ts',
            'ott_subscription': 'plus.ott_subscription',
            'plus_family_role': 'plus.family_role',
            'plus_cashback_enabled': 'plus.cashback_enabled',
            'plus_subscription_level': 'plus.subscription_level',
            'plus_is_frozen': 'plus.is_frozen',
            'plus_subscriber_state': 'plus.subscriber_state',
            'is_documents_agreement_accepted': 'account.is_documents_agreement_accepted',
            'is_dzen_sso_prohibited': 'account.is_dzen_sso_prohibited',
            'can_manage_children': 'account.can_manage_children',
        }

        for name, expected in options.items():
            if name == 'is_enabled':
                expected_log_entries['info.disabled_status'] = tskv_bool(not expected)
            if isinstance(expected, bool):
                expected = tskv_bool(expected)
            expected_log_entries[options_to_fields[name]] = expected

        if admin_name and comment:
            expected_log_entries['admin'] = admin_name
            expected_log_entries['comment'] = comment
        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)


class TestAccountOptionsView(BaseAccountOptionsTestView):
    def setUp(self):
        super(TestAccountOptionsView, self).setUp()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT)

    def _assert_wrong_grants_fail(self, missing_grant, **query_kwargs):
        self.setup_blackbox_responses_and_serialize()

        grants = list(ALL_OLD_STYLE_GRANTS)
        grants.remove(missing_grant)
        self.setup_grants(*grants)

        resp = self.make_request(query_args=query_kwargs)
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_unknown_uid_fails(self):
        self.setup_blackbox_responses_and_serialize(uid=None)
        resp = self.make_request(query_args=dict(is_enabled='yes'))
        self.assert_error_response(resp, ['account.not_found'])

    def test_child_cant_manage(self):
        self.setup_blackbox_responses_and_serialize(is_child=True)
        self.setup_grants(ACCOUNT_CAN_MANAGE_CHILDREN_GRANT_PREFIX + '.any',
                          ACCOUNT_CAN_MANAGE_CHILDREN_GRANT_PREFIX + '.by_uid')
        resp = self.make_request(query_args={'can_manage_children': '1'})
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_can_manage_children_ok(self):
        self.setup_blackbox_responses_and_serialize(is_child=False)
        self.setup_grants(ACCOUNT_CAN_MANAGE_CHILDREN_GRANT_PREFIX + '.any',
                          ACCOUNT_CAN_MANAGE_CHILDREN_GRANT_PREFIX + '.by_uid')
        resp = self.make_request(query_args={'can_manage_children': '1'})
        self.assert_ok_response(resp)

    def test_event_with_admin_name_and_comment_is_logged(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_ENABLED_GRANT, LOG_ADMIN_ACTION_GRANT)

        resp = self.make_request(
            query_args=dict(
                is_enabled='no',
                admin_name=TEST_ADMIN_LOGIN,
                comment=TEST_COMMENT,
            ),
        )
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

    def test_is_enabled_grant_missing_fails(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT, ACCOUNT_IS_SHARED_GRANT)
        resp = self.make_request(query_args=dict(is_enabled='yes'))
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_is_enabled_true_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_ENABLED_GRANT)
        resp = self.make_request(query_args=dict(is_enabled='yes'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_is_enabled_false_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_ENABLED_GRANT)
        resp = self.make_request(query_args=dict(is_enabled='no'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_disabled=True,
        )
        self.check_events_ok(is_disabled=True)

    def test_is_enabled_works_for_pdd(self):
        self.setup_blackbox_responses_and_serialize(
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            domain=TEST_DOMAIN,
        )
        self.setup_grants(ACCOUNT_OPTIONS_PDD_GRANT, ACCOUNT_IS_ENABLED_GRANT)
        resp = self.make_request(query_args=dict(is_enabled='yes'))
        self.assert_ok_response(resp)

    def test_is_enabled_grants_inapplicable_for_portal(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_OPTIONS_ANY_GRANT,
            is_enabled='yes',
        )

    def test_is_app_password_enabled_grant_missing_fails(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_ENABLED_GRANT, ACCOUNT_IS_SHARED_GRANT)
        resp = self.make_request(query_args=dict(is_app_password_enabled='yes'))
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_is_app_password_enabled_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT)
        resp = self.make_request(query_args=dict(is_app_password_enabled='yes'))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=1,
            is_app_password_enabled=True,
        )
        self.check_events_ok(is_app_password_enabled=True)

    def test_is_shared_grant_missing_fails(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_ENABLED_GRANT, ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT)
        resp = self.make_request(query_args=dict(is_shared='yes'))
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_is_connect_admin_grant_missing_fails(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_ENABLED_GRANT, ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT)
        resp = self.make_request(query_args=dict(is_connect_admin='yes'))
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_is_connect_admin_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_CONNECT_ADMIN_GRANT)
        resp = self.make_request(query_args=dict(is_connect_admin='yes'))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=1,
            is_connect_admin=True,
        )
        self.check_events_ok(is_connect_admin=True)

    def test_is_easily_hacked_grant_missing_fails(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT)
        resp = self.make_request(query_args=dict(is_easily_hacked='yes'))
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_is_easily_hacked_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_EASILY_HACKED_GRANT)
        resp = self.make_request(query_args=dict(is_easily_hacked='yes'))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=1,
            is_easily_hacked=True,
        )
        self.check_events_ok(is_easily_hacked=True)

    def test_is_maillist_works_on_pdd(self):
        self.setup_blackbox_responses_and_serialize(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
        )

        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_MAILLIST_GRANT)
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
        self.setup_blackbox_responses_and_serialize(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
            subscribed_to={
                '104': '1',
            },
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_MAILLIST_GRANT)
        resp = self.make_request(query_args=dict(is_maillist='yes'))
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_is_maillist_doesnt_work_on_regular_user(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_MAILLIST_GRANT)
        resp = self.make_request(query_args=dict(is_maillist='yes'))
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_is_maillist_false_works_with_no_sso_domain(self):
        self.env.federal_configs_api.set_response_side_effect('config_by_domain_id', FederalConfigsApiNotFoundError())
        self.setup_blackbox_responses_and_serialize(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
            attributes={
                str(AT['account.is_maillist']): '1',
            },
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_MAILLIST_GRANT)
        resp = self.make_request(query_args=dict(is_maillist='no'))
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=2,
            uid=TEST_PDD_UID,
            is_maillist=False,
            is_employee=True,
        )
        self.check_events_ok(is_maillist=False, is_employee=True)

    def test_is_maillist_false_not_works_with_sso_domain(self):
        self.setup_blackbox_responses_and_serialize(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
            attributes={
                str(AT['account.is_maillist']): '1',
            },
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_MAILLIST_GRANT)
        resp = self.make_request(query_args=dict(is_maillist='no'))
        self.assert_error_response(resp, ['action.impossible'])

    def test_global_logout_grant_missing_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_GLOBAL_LOGOUT_GRANT,
            global_logout='yes',
        )

    def test_global_logout_false_works(self):
        """Указано отрицательное значение global_logout, ничего не происходит"""
        self.setup_blackbox_responses_and_serialize()

        resp = self.make_request(query_args=dict(global_logout='no'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_global_logout_true_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_GLOBAL_LOGOUT_GRANT)

        resp = self.make_request(query_args=dict(global_logout='1'))
        self.assert_ok_response(resp)
        now = TimeNow()
        self.check_db_ok(
            sharddb_query_count=1,
            glogout=now,
        )
        self.check_events_ok(glogout=now)

    def test_global_logout_works_for_phonish(self):
        self.setup_blackbox_responses_and_serialize(aliases={'phonish': TEST_LOGIN})
        self.setup_grants(ACCOUNT_OPTIONS_PHONISH_GRANT, ACCOUNT_GLOBAL_LOGOUT_GRANT)
        resp = self.make_request(query_args=dict(global_logout='1'))
        self.assert_ok_response(resp)

    def test_global_logout_grants_inapplicable_for_portal(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_OPTIONS_ANY_GRANT,
            global_logout='yes',
        )

    def test_revoke_tokens_grant_missing_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_REVOKE_TOKENS_GRANT,
            revoke_tokens='yes',
        )

    def test_revoke_tokens_false_works(self):
        self.setup_blackbox_responses_and_serialize()

        resp = self.make_request(query_args=dict(revoke_tokens='no'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_revoke_tokens_true_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_REVOKE_TOKENS_GRANT)

        resp = self.make_request(query_args=dict(revoke_tokens='1'))
        self.assert_ok_response(resp)
        now = TimeNow()
        self.check_db_ok(
            sharddb_query_count=1,
            tokens_revoked_at=now,
        )
        self.check_events_ok(tokens_revoked_at=now)

    def test_revoke_app_passwords_grant_missing_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_REVOKE_APP_PASSWORDS_GRANT,
            revoke_app_passwords='yes',
        )

    def test_revoke_app_passwords_false_works(self):
        self.setup_blackbox_responses_and_serialize()

        resp = self.make_request(query_args=dict(revoke_app_passwords='no'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_revoke_app_passwords_true_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_REVOKE_APP_PASSWORDS_GRANT)

        resp = self.make_request(query_args=dict(revoke_app_passwords='1'))
        self.assert_ok_response(resp)
        now = TimeNow()
        self.check_db_ok(
            sharddb_query_count=1,
            app_passwords_revoked_at=now,
        )
        self.check_events_ok(app_passwords_revoked_at=now)

    def test_revoke_web_sessions_grant_missing_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_REVOKE_WEB_SESSIONS_GRANT,
            revoke_web_sessions='yes',
        )

    def test_revoke_web_sessions_false_works(self):
        self.setup_blackbox_responses_and_serialize()

        resp = self.make_request(query_args=dict(revoke_web_sessions='no'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_revoke_web_sessions_true_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_REVOKE_WEB_SESSIONS_GRANT)

        resp = self.make_request(query_args=dict(revoke_web_sessions='1'))
        self.assert_ok_response(resp)
        now = TimeNow()
        self.check_db_ok(
            sharddb_query_count=1,
            web_sessions_revoked_at=now,
        )
        self.check_events_ok(web_sessions_revoked_at=now)

    def test_password_update_timestamp_grant_missing_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=PASSWORD_UPDATE_DATETIME_GRANT,
            password_update_timestamp=TEST_TIMESTAMP,
        )

    def test_password_update_timestamp_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_UPDATE_DATETIME_GRANT)

        resp = self.make_request(query_args=dict(password_update_timestamp=TEST_TIMESTAMP))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            password_update_timestamp=str(TEST_TIMESTAMP),
        )
        self.check_events_ok(password_update_timestamp=str(TEST_TIMESTAMP))

    def test_is_password_change_required_grant_missing_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=PASSWORD_IS_CHANGING_REQUIRED_GRANT,
            is_password_change_required='yes',
        )

    def test_is_password_change_required_false_works(self):
        """Снятие 3-го бита работает"""
        self.setup_blackbox_responses_and_serialize(
            subscribed_to=[8],
            dbfields={'subscription.login_rule.8': 5},
            attributes={'password.forced_changing_reason': '1'},
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_password_change_required='no'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_password_change_required=False,
        )
        self.check_events_ok(is_password_change_required=False)

    def test_is_password_change_required_true_works(self):
        """Установка 3-го бита работает"""
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_password_change_required='1'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_password_change_required=True,
        )
        self.check_events_ok(is_password_change_required=True)

    def test_sms_sent_to_secure_number(self):
        self.setup_blackbox_responses_and_serialize(with_secure_phone=True)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(
            query_args=dict(is_password_change_required='1', notify_by_sms='1'),
            headers=dict(user_agent=TEST_USER_AGENT)
        )

        self.assert_ok_response(resp, notifications={'is_sms_sent': True})
        self.check_db_ok(sharddb_query_count=1, is_password_change_required=True)
        self.check_events_ok(is_password_change_required=True, user_agent=TEST_USER_AGENT)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)  # Один раз отправили sms

        requests[0].assert_query_contains({
            'phone': DEFAULT_PHONE_NUMBER,
            'caller': 'dev',
            'identity': 'password_options.notify',
        })

        self.env.blackbox.requests[0].assert_post_data_contains({
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('is_changing_required', user_agent=TEST_USER_AGENT),
            self.env.statbox.entry('notification_sent'),
        ])

    def test_too_frequent_password_change__error(self):
        today_ts = int(time.mktime(date.today().timetuple()))
        self.setup_blackbox_responses_and_serialize(
            dbfields={'accounts.passwd.uid': str(time.time())},
            password_update_datetime=str(today_ts),  # Пароль уже меняли сегодня
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(
            query_args=dict(
                is_password_change_required='1',
                max_change_frequency_in_days=7,  # Менять пароль не чаще раза в неделю
            ),
        )

        self.assert_error_response(resp, ['password.too_frequent_change'])
        self.check_db_ok(
            sharddb_query_count=0,
            is_password_change_required=False,
            password_update_timestamp=str(today_ts),
        )

    def test_already_has_is_changing_required_flag__error(self):
        self.setup_blackbox_responses_and_serialize(
            subscribed_to=[8],
            dbfields={'subscription.login_rule.8': 5},
            attributes={'password.forced_changing_reason': '1'},
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_password_change_required='1'))
        self.assert_error_response(resp, ['action.not_required'])
        self.check_db_ok(
            sharddb_query_count=0,
            is_password_change_required=True,
        )

    def test_param_max_frequent_password_change__ok(self):
        week_ago = int(time.time()) - 60 * 60 * 24 * 7 - 1  # -1 чтоб наверняка
        self.setup_blackbox_responses_and_serialize(
            dbfields={'accounts.passwd.uid': str(week_ago)},
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(
            query_args=dict(
                is_password_change_required='1',
                max_change_frequency_in_days=7,
            ),
        )
        self.assert_ok_response(resp)
        self.check_db_ok(sharddb_query_count=1, is_password_change_required=True)
        self.check_events_ok(is_password_change_required=True)

    def test_max_frequent_password_change_no_changing_required__max_freq_ignored(self):
        now = int(time.time())
        self.setup_blackbox_responses_and_serialize(
            password_update_datetime=now,
            subscribed_to=[8],
            dbfields={'subscription.login_rule.8': 5},
            attributes={'password.forced_changing_reason': '1'},
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(
            query_args=dict(
                is_password_change_required='no',
                max_change_frequency_in_days=7,
            ),
        )
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            password_update_timestamp=str(now),
            is_password_change_required=False,
        )
        self.check_events_ok(is_password_change_required=False)

    def test_2fa_password_change_nonsense(self):
        """
        При включенной 2FA направление на принудительную смену пароля не имеет смысла.
        """
        self.setup_blackbox_responses_and_serialize(enabled_2fa=True),
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_password_change_required='yes'))
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_no_password_password_change_nonsense(self):
        """
        При отсуствии пароля направление на принудительную смену пароля не имеет смысла.
        """
        self.setup_blackbox_responses_and_serialize(has_password=False)
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_password_change_required='yes'))
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_no_password_but_can_cancel_password_change(self):
        """
        Даже если пароля нет, принудительную смену пароля можно отменить.
        """
        self.setup_blackbox_responses_and_serialize(
            subscribed_to=[8],
            dbfields={'subscription.login_rule.8': 5},
            attributes={'password.forced_changing_reason': '1'},
            has_password=False,
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_password_change_required='no'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_password_change_required=False,
        )
        self.check_events_ok(is_password_change_required=False)

    def test_show_2fa_promo_grant_missing_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_SHOW_2FA_PROMO_GRANT,
            is_password_change_required='yes',
            show_2fa_promo='1',
        )

    def test_show_2fa_promo_true_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT, ACCOUNT_SHOW_2FA_PROMO_GRANT)

        resp = self.make_request(
            query_args=dict(
                is_password_change_required='1',
                show_2fa_promo='1',
            ),
        )
        self.assert_ok_response(resp)
        self.check_db_ok(
            is_password_change_required=True,
            show_2fa_promo=True,
            sharddb_query_count=1,
        )

    def test_show_2fa_promo_false_works(self):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                'password.update_datetime': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'account.show_2fa_promo': '1',
            },
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, PASSWORD_IS_CHANGING_REQUIRED_GRANT, ACCOUNT_SHOW_2FA_PROMO_GRANT)

        resp = self.make_request(
            query_args=dict(
                is_password_change_required='1',
                show_2fa_promo='0',
            ),
        )
        self.assert_ok_response(resp)
        self.check_db_ok(
            is_password_change_required=True,
            show_2fa_promo=False,
            sharddb_query_count=2,
        )

    def test_external_organization_ids_update_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, EXTERNAL_ORGANIZATION_IDS_GRANT)

        resp = self.make_request(query_args=dict(external_organization_ids='1,3,2'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            external_organization_ids='1,2,3',
            sharddb_query_count=1,
        )
        self.check_events_ok(external_organization_ids='1,2,3')

    def test_external_organization_ids_delete_works(self):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                'account.external_organization_ids': '1,2,3',
            },
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, EXTERNAL_ORGANIZATION_IDS_GRANT)

        resp = self.make_request(query_args=dict(external_organization_ids=''))
        self.assert_ok_response(resp)
        self.check_db_ok(
            external_organization_ids='',
            sharddb_query_count=1,
        )
        self.check_events_ok(external_organization_ids='-')

    def test_billing_features_update_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_SET_BILLING_FEATURES_GRANT)

        resp = self.make_request(query_args={
            'billing_features': json.dumps({
                'cashback_100': {
                    'brand': 'brand',
                    'in_trial': True,
                    'paid_trial': False,
                    'region_id': 0,
                    'trial_duration': 0,
                },
            })
        })
        self.assert_ok_response(resp)
        self.check_db_ok(
            billing_features='\n\x1f\n\x0ccashback_100\x12\x0f\x08\x01\x10\x00\x18\x00 \x00*\x05brand',
            sharddb_query_count=1,
        )
        self.check_events_ok(
            billing_features='{"cashback_100": {"brand": "brand", "in_trial": true, "paid_trial": false, "region_id": 0, "trial_duration": 0}}',
        )

    def test_billing_features_delete_works(self):
        self.setup_blackbox_responses_and_serialize(
            billing_features={
                'cashback_100': {
                    'brand': 'brand',
                    'in_trial': True,
                    'paid_trial': False,
                    'region_id': 0,
                    'trial_duration': 0,
                },
            }
        )
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_SET_BILLING_FEATURES_GRANT)

        resp = self.make_request(query_args=dict(billing_features='{}'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            billing_features='',
            sharddb_query_count=1,
        )
        self.check_events_ok(billing_features='-')

    def test_invalid_billing_features(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_SET_BILLING_FEATURES_GRANT)

        resp = self.make_request(query_args={
            'billing_features': json.dumps({
                'CASHBACK_100': {
                    'brand': 'brand',
                    'in_trial': True,
                    'paid_trial': False,
                    'region_id': 0,
                    'trial_duration': 0,
                },
            })
        })
        self.assert_error_response(resp, ['billing_features.invalid'])

    def test_billing_features_grants_missing(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT)

        resp = self.make_request(query_args={
            'billing_features': json.dumps({
                'cashback_100': {
                    'brand': 'brand',
                    'in_trial': True,
                    'paid_trial': False,
                    'region_id': 0,
                    'trial_duration': 0,
                },
            })
        })
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_plus_subscriber_state_update_works(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(
            ACCOUNT_PLUS_SUBSCRIBER_STATE_GRANT_PREFIX + '.any',
            ACCOUNT_PLUS_SUBSCRIBER_STATE_GRANT_PREFIX + '.by_uid',
        )

        resp = self.make_request(query_args={
            'plus_subscriber_state': TEST_PLUS_SUBSCRIBER_STATE1_JSON,
        })
        self.assert_ok_response(resp)
        self.check_db_ok(
            plus_subscriber_state=TEST_PLUS_SUBSCRIBER_STATE1_PROTO,
            sharddb_query_count=1,
        )
        self.check_events_ok(
            plus_subscriber_state=TEST_PLUS_SUBSCRIBER_STATE1_JSON,
        )

    def test_plus_subscriber_state_delete_works(self):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                AT['account.plus.subscriber_state']: TEST_PLUS_SUBSCRIBER_STATE1_BASE64,
            },
        )
        self.setup_grants(
            ACCOUNT_PLUS_SUBSCRIBER_STATE_GRANT_PREFIX + '.any',
            ACCOUNT_PLUS_SUBSCRIBER_STATE_GRANT_PREFIX + '.by_uid',
        )

        resp = self.make_request(query_args={
            'plus_subscriber_state': '{}',
        })
        self.assert_ok_response(resp)
        self.check_db_ok(
            plus_subscriber_state='',
            sharddb_query_count=1,
        )
        self.check_events_ok(plus_subscriber_state='-')

    def test_plus_subscriber_state_invalid(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(
            ACCOUNT_PLUS_SUBSCRIBER_STATE_GRANT_PREFIX + '.any',
            ACCOUNT_PLUS_SUBSCRIBER_STATE_GRANT_PREFIX + '.by_uid',
        )

        resp = self.make_request(query_args={
            'plus_subscriber_state': '[111]',
        })
        self.assert_error_response(resp, ['plus_subscriber_state.invalid'])

    def test_plus_subscriber_state_grants_missing(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT)

        resp = self.make_request(query_args={
            'plus_subscriber_state': TEST_PLUS_SUBSCRIBER_STATE1_JSON,
        })
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    @parameterized.expand(
        [
            ('audience_on', 'account.audience_on', ACCOUNT_OPTIONS_ANY_GRANT, '1', True),
            ('audience_on', 'account.audience_on', ACCOUNT_OPTIONS_ANY_GRANT, '0', False),
            ('is_shared', 'account.is_shared', ACCOUNT_IS_SHARED_GRANT, '1', True),
            ('is_shared', 'account.is_shared', ACCOUNT_IS_SHARED_GRANT, '0', False),
            ('magic_link_login_forbidden', 'account.magic_link_login_forbidden', DISABLE_AUTH_METHODS_GRANT, '1', True),
            ('magic_link_login_forbidden', 'account.magic_link_login_forbidden', DISABLE_AUTH_METHODS_GRANT, '0', False),
            ('qr_code_login_forbidden', 'account.qr_code_login_forbidden', DISABLE_AUTH_METHODS_GRANT, '1', True),
            ('qr_code_login_forbidden', 'account.qr_code_login_forbidden', DISABLE_AUTH_METHODS_GRANT, '0', False),
            ('sms_code_login_forbidden', 'account.sms_code_login_forbidden', DISABLE_AUTH_METHODS_GRANT, '1', True),
            ('sms_code_login_forbidden', 'account.sms_code_login_forbidden', DISABLE_AUTH_METHODS_GRANT, '0', False),
            ('takeout_subscription', 'takeout.subscription', ALLOW_TAKEOUT_SUBSCRIPTION_GRANT, '1', True),
            ('takeout_subscription', 'takeout.subscription', ALLOW_TAKEOUT_SUBSCRIPTION_GRANT, '0', False),
        ]
    )
    def test_check_boolean_attribute_works(self, attribute, blackbox_attribute_name, grant, request_value, expected_value):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                blackbox_attribute_name: not (request_value in ['1', 1, 'yes', True]),
            },
        )
        self.setup_grants(*{ACCOUNT_OPTIONS_ANY_GRANT, grant})

        resp = self.make_request(query_args={attribute: request_value})
        self.assert_ok_response(resp)
        self.check_db_ok(**{
            attribute: expected_value,
            "sharddb_query_count": 1,
        })
        self.check_events_ok(**{attribute: expected_value})

    @parameterized.expand(
        [
            ('magic_link_login_forbidden',),
            ('qr_code_login_forbidden',),
            ('sms_code_login_forbidden',),
        ]
    )
    def test_attributes_inapplicable_for_superlite(self, attribute):
        self.setup_blackbox_responses_and_serialize(has_password=False, lite=True)
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, DISABLE_AUTH_METHODS_GRANT)
        resp = self.make_request(query_args={attribute: '1'})
        self.assert_error_response(resp, ['account.invalid_type'])
        self.check_account_modification_push_not_sent()

    @parameterized.expand(
        [
            ('magic_link_login_forbidden', '1'),
            ('qr_code_login_forbidden', '1'),
            ('sms_code_login_forbidden', '1'),
            ('sms_2fa_on', '1'),
            ('magic_link_login_forbidden', '0'),
            ('qr_code_login_forbidden', '0'),
            ('sms_code_login_forbidden', '0'),
            ('sms_2fa_on', '0'),
        ]
    )
    def test_attributes_notification(self, attribute, value):
        email = self.create_native_email(TEST_LOGIN, 'yandex.ru')
        self.setup_blackbox_responses_and_serialize(with_secure_phone=True, emails=[email])
        self.setup_grants(
            ACCOUNT_OPTIONS_ANY_GRANT,
            DISABLE_AUTH_METHODS_GRANT,
            ACCOUNT_SMS_2FA_ON_GRANT_PREFIX + '.any',
            ACCOUNT_SMS_2FA_ON_GRANT_PREFIX + '.by_uid',
        )
        resp = self.make_request(query_args={attribute: value}, headers={'host': 'yandex.ru'})
        self.assert_ok_response(resp)
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='login_method_change',
            uid=TEST_UID,
            title='Изменён способ входа в аккаунт {}'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
        )
        r = self.env.blackbox.get_requests_by_method('userinfo')[0]
        r.assert_post_data_contains(dict(emails='getall'))
        self.assert_emails_sent([
            self.create_account_modification_mail(
                'login_method_change',
                email['address'],
                dict(
                    login=TEST_LOGIN,
                    USER_IP=TEST_IP,
                ),
            ),
        ])


class TestAccountOptionsViewWithUrlAlias(TestAccountOptionsView):
    default_url = '/2/account/options/?consumer=dev'
    http_query_args = {'uid': TEST_UID}


PLUS_CHANGE_ATTRIBUTES_SETTINGS = dict(
    BLACKBOX_URL='localhost',
    DATASYNC_API_URL='http://localhost/',
    DATASYNC_API_TIMEOUT=0.5,
    DATASYNC_API_RETRIES=2,
    DISK_PLUS_PARTNER_ID='yandex_plus',
    DISK_PLUS_PRODUCT_ID='yandex_plus_10gb',
    DISK_PLUS_ENABLED=True,
)


@with_settings_hosts(**PLUS_CHANGE_ATTRIBUTES_SETTINGS)
class TestAccountOptionsWithNewGrantsAndUrlAlias(BaseAccountOptionsTestView):
    default_url = '/2/account/options/?consumer=dev'

    TESTCASES = [
        # attribute, blackbox_attribute_name, grant_prefix, old_value, request_value, expected_value
        ('audience_on', 'account.audience_on', ACCOUNT_AUDIENCE_ON_GRANT_PREFIX, False, '1', True),
        ('audience_on', 'account.audience_on', ACCOUNT_AUDIENCE_ON_GRANT_PREFIX, True, '0', False),
        ('is_shared', 'account.is_shared', ACCOUNT_IS_SHARED_GRANT_PREFIX, False, '1', True),
        ('is_shared', 'account.is_shared', ACCOUNT_IS_SHARED_GRANT_PREFIX, True, '0', False),
        ('magic_link_login_forbidden', 'account.magic_link_login_forbidden', DISABLE_AUTH_METHODS_GRANT_PREFIX, False, '1', True),
        ('magic_link_login_forbidden', 'account.magic_link_login_forbidden', DISABLE_AUTH_METHODS_GRANT_PREFIX, True, '0', False),
        ('qr_code_login_forbidden', 'account.qr_code_login_forbidden', DISABLE_AUTH_METHODS_GRANT_PREFIX, False, '1', True),
        ('qr_code_login_forbidden', 'account.qr_code_login_forbidden', DISABLE_AUTH_METHODS_GRANT_PREFIX, True, '0', False),
        ('sms_code_login_forbidden', 'account.sms_code_login_forbidden', DISABLE_AUTH_METHODS_GRANT_PREFIX, False, '1', True),
        ('sms_code_login_forbidden', 'account.sms_code_login_forbidden', DISABLE_AUTH_METHODS_GRANT_PREFIX, True, '0', False),
        ('takeout_subscription', 'takeout.subscription', ALLOW_TAKEOUT_SUBSCRIPTION_GRANT_PREFIX, False, '1', True),
        ('takeout_subscription', 'takeout.subscription', ALLOW_TAKEOUT_SUBSCRIPTION_GRANT_PREFIX, True, '0', False),
        ('external_organization_ids', 'account.external_organization_ids', EXTERNAL_ORGANIZATION_IDS_GRANT_PREFIX, '1,2', '1,2,3', '1,2,3'),
        ('show_fio_in_public_name', 'person.show_fio_in_public_name', PERSON_SHOW_FIO_IN_PUBLIC_NAME_GRANT_PREFIX, False, '1', True),
        ('show_fio_in_public_name', 'person.show_fio_in_public_name', PERSON_SHOW_FIO_IN_PUBLIC_NAME_GRANT_PREFIX, True, '0', False),
        ('force_challenge', 'account.force_challenge', ACCOUNT_FORCE_CHALLENGE_GRANT_PREFIX, False, '1', True),
        ('force_challenge', 'account.force_challenge', ACCOUNT_FORCE_CHALLENGE_GRANT_PREFIX, True, '0', False),
        ('sms_2fa_on', 'account.sms_2fa_on', ACCOUNT_SMS_2FA_ON_GRANT_PREFIX, True, '0', False),
        ('forbid_disabling_sms_2fa', 'account.forbid_disabling_sms_2fa', ACCOUNT_FORRBID_DISABLING_SMS_2FA_GRANT_PREFIX, False, '1', True),
        ('forbid_disabling_sms_2fa', 'account.forbid_disabling_sms_2fa', ACCOUNT_FORRBID_DISABLING_SMS_2FA_GRANT_PREFIX, True, '0', False),
        ('takeout_delete_subscription', 'takeout.delete.subscription', ALLOW_TAKEOUT_DELETE_SUBSCRIPTION_GRANT_PREFIX, False, '1', True),
        ('takeout_delete_subscription', 'takeout.delete.subscription', ALLOW_TAKEOUT_DELETE_SUBSCRIPTION_GRANT_PREFIX, True, '0', False),
        ('personal_data_public_access_allowed', 'account.personal_data_public_access_allowed', ACCOUNT_PERSONAL_DATA_PUBLIC_ACCESS_ALLOWED_GRANT_PREFIX, False, '1', True),
        ('personal_data_public_access_allowed', 'account.personal_data_public_access_allowed', ACCOUNT_PERSONAL_DATA_PUBLIC_ACCESS_ALLOWED_GRANT_PREFIX, True, '0', False),
        ('personal_data_third_party_processing_allowed', 'account.personal_data_third_party_processing_allowed', ACCOUNT_PERSONAL_DATA_THIRD_PARTY_PROCESSING_ALLOWED_GRANT_PREFIX, False, '1', True),
        ('personal_data_third_party_processing_allowed', 'account.personal_data_third_party_processing_allowed', ACCOUNT_PERSONAL_DATA_THIRD_PARTY_PROCESSING_ALLOWED_GRANT_PREFIX, True, '0', False),
        ('family_pay_enabled', 'account.family_pay.enabled', ACCOUNT_FAMILY_PAY_ENABLED_GRANT_PREFIX, False, '1', True),
        ('plus_enabled', 'account.plus.enabled', ACCOUNT_PLUS_ENABLED_GRANT_PREFIX, False, '1', True),
        ('plus_trial_used_ts', 'account.plus.trial_used_ts', ACCOUNT_PLUS_TRIAL_USED_TS_GRANT_PREFIX, 0, 12345, '12345'),
        ('plus_subscription_stopped_ts', 'account.plus.subscription_stopped_ts', ACCOUNT_PLUS_SUBSCRIPTION_STOPPED_TS_GRANT_PREFIX, 0, 12345, '12345'),
        ('plus_subscription_expire_ts', 'account.plus.subscription_expire_ts', ACCOUNT_PLUS_SUBSCRIPTION_EXPIRE_TS_GRANT_PREFIX, 0, 12345, '12345'),
        ('plus_next_charge_ts', 'account.plus.next_charge_ts', ACCOUNT_PLUS_NEXT_CHARGE_TS_GRANT_PREFIX, 0, 12345, '12345'),
        ('ott_subscription', 'account.plus.ott_subscription', ACCOUNT_PLUS_OTT_SUBSCRIPTION_GRANT_PREFIX, None, 'YA_PLUS', 'YA_PLUS'),
        ('plus_family_role', 'account.plus.family_role', ACCOUNT_PLUS_FAMILY_ROLE_GRANT_PREFIX, None, 'CHILD', 'CHILD'),
        ('plus_cashback_enabled', 'account.plus.cashback_enabled', ACCOUNT_PLUS_CASHBACK_ENABLED_GRANT_PREFIX, False, '1', True),
        ('plus_subscription_level', 'account.plus.subscription_level', ACCOUNT_PLUS_SUBSCRIPTION_LEVEL_GRANT_PREFIX, 100, 1000, '1000'),
        ('plus_is_frozen', 'account.plus.is_frozen', ACCOUNT_PLUS_IS_FROZEN_GRANT_PREFIX, False, '1', True),
        ('is_documents_agreement_accepted', 'account.is_documents_agreement_accepted', ACCOUNT_IS_DOCUMENTS_AGREEMENT_ACCEPTED_GRANT_PREFIX, False, '1', True),
        ('is_dzen_sso_prohibited', 'account.is_dzen_sso_prohibited', ACCOUNT_IS_DZEN_SSO_PROHIBITED_GRANT_PREFIX, False, '1', True),
    ]

    def setUp(self):
        super(TestAccountOptionsWithNewGrantsAndUrlAlias, self).setUp()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID): {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
                str(TEST_CLIENT_ID_2): {
                    'alias': 'datasync_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()
        self.setup_grants()

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        super(TestAccountOptionsWithNewGrantsAndUrlAlias, self).tearDown()

    def setup_ticket_checker(self, scopes=None, uids=None):
        uids = uids or [TEST_UID]
        ticket = fake_user_ticket(
            default_uid=TEST_UID,
            scopes=scopes or ['bb:sessionid'],
            uids=uids,
        )
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([ticket])

    def test_multisession_uid(self):
        another_uid = 2
        assert TEST_UID != another_uid
        self.setup_blackbox_responses_and_serialize()
        self.setup_ticket_checker(uids=[TEST_UID, another_uid])
        self.setup_grants(ACCOUNT_OPTIONS_ANY_GRANT, ACCOUNT_IS_APP_PASSWORD_ENABLED_GRANT)
        resp = self.make_request(
            query_args=dict(is_app_password_enabled='yes', multisession_uid=another_uid),
            headers={'user_ticket': TEST_USER_TICKET1},
        )
        self.assert_ok_response(resp)

        self.check_db_ok(
            sharddb_query_count=1,
            is_app_password_enabled=True,
        )
        self.check_events_ok(is_app_password_enabled=True)

    def test_no_credentials_passed(self):
        resp = self.make_request(query_args={'is_shared': '1'})
        self.assert_error_response(resp, ['request.credentials_all_missing'])

    @parameterized.expand(TESTCASES)
    def test_no_grants_for_attribute(self, attribute, blackbox_attribute_name, grant_prefix,
                                     old_value, request_value, expected_value):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                blackbox_attribute_name: old_value,
            },
        )
        self.setup_grants()

        resp = self.make_request(query_args={'uid': TEST_UID, attribute: request_value})
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    @parameterized.expand(TESTCASES)
    def test_no_grants_to_work_by_uid(self, attribute, blackbox_attribute_name, grant_prefix,
                                      old_value, request_value, expected_value):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                blackbox_attribute_name: old_value,
            },
        )
        self.setup_grants(grant_prefix + '.any')

        resp = self.make_request(query_args={'uid': TEST_UID, attribute: request_value})
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    @parameterized.expand(TESTCASES)
    def test_no_grants_for_account_type(self, attribute, blackbox_attribute_name, grant_prefix,
                                        old_value, request_value, expected_value):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                blackbox_attribute_name: old_value,
            },
        )
        self.setup_grants(grant_prefix + '.pdd', grant_prefix + '.by_uid')

        resp = self.make_request(query_args={'uid': TEST_UID, attribute: request_value})
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    @parameterized.expand(TESTCASES)
    def test_simple_attribute_works_by_uid(self, attribute, blackbox_attribute_name, grant_prefix,
                                           old_value, request_value, expected_value):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                blackbox_attribute_name: old_value,
            },
        )
        self.setup_grants(grant_prefix + '.normal', grant_prefix + '.by_uid')

        resp = self.make_request(query_args={'uid': TEST_UID, attribute: request_value})
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            **{attribute: expected_value}
        )
        self.check_events_ok(**{attribute: expected_value})

    @parameterized.expand(TESTCASES)
    def test_simple_attribute_works_by_user_ticket(self, attribute, blackbox_attribute_name, grant_prefix,
                                                   old_value, request_value, expected_value):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                blackbox_attribute_name: old_value,
            },
        )
        self.setup_ticket_checker()
        self.setup_grants(grant_prefix + '.any')

        resp = self.make_request(query_args={attribute: request_value}, headers={'user_ticket': TEST_USER_TICKET1})
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            **{attribute: expected_value}
        )
        self.check_events_ok(**{attribute: expected_value})

    @parameterized.expand(TESTCASES)
    def test_simple_attribute_works_by_session_id(self, attribute, blackbox_attribute_name, grant_prefix,
                                                  old_value, request_value, expected_value):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                blackbox_attribute_name: old_value,
            },
        )
        self.setup_grants(grant_prefix + '.any')

        resp = self.make_request(query_args={attribute: request_value}, headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            **{attribute: expected_value}
        )
        self.check_events_ok(**{attribute: expected_value})

    @parameterized.expand(TESTCASES)
    def test_simple_attribute_works_by_xtoken(self, attribute, blackbox_attribute_name, grant_prefix,
                                              old_value, request_value, expected_value):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                blackbox_attribute_name: old_value,
            },
        )
        self.setup_grants(grant_prefix + '.any')

        resp = self.make_request(query_args={attribute: request_value}, headers={'authorization': 'OAuth token'})
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            **{attribute: expected_value}
        )
        self.check_events_ok(**{attribute: expected_value})

    def test_enable_sms_2fa__ok(self):
        self.setup_blackbox_responses_and_serialize(
            with_secure_phone=True,
        )
        self.setup_grants(ACCOUNT_SMS_2FA_ON_GRANT_PREFIX + '.any')

        resp = self.make_request(
            query_args={'sms_2fa_on': '1'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            sms_2fa_on=True,
        )
        self.check_events_ok(sms_2fa_on=True)

    def test_enable_sms_2fa__no_secure_phone_error(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_SMS_2FA_ON_GRANT_PREFIX + '.any')

        resp = self.make_request(
            query_args={'sms_2fa_on': '1'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_error_response(resp, ['phone_secure.not_found'])

    def test_enable_sms_2fa__2fa_enabled_error(self):
        self.setup_blackbox_responses_and_serialize(
            with_secure_phone=True,
            enabled_2fa=True,
        )
        self.setup_grants(ACCOUNT_SMS_2FA_ON_GRANT_PREFIX + '.any')

        resp = self.make_request(
            query_args={'sms_2fa_on': '1'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_error_response(resp, ['account.2fa_enabled'])

    def test_enable_sms_2fa__account_invalid_type_error(self):
        self.setup_blackbox_responses_and_serialize(
            with_secure_phone=True,
            aliases={'neophonish': TEST_LOGIN},
        )
        self.setup_grants(ACCOUNT_SMS_2FA_ON_GRANT_PREFIX + '.any')

        resp = self.make_request(
            query_args={'sms_2fa_on': '1'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_disable_sms_2fa__not_allowed_error(self):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                'account.sms_2fa_on': '1',
                'account.forbid_disabling_sms_2fa': '1',
            },
        )
        self.setup_grants(ACCOUNT_SMS_2FA_ON_GRANT_PREFIX + '.any')

        resp = self.make_request(
            query_args={'sms_2fa_on': '0'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_error_response(resp, ['action.impossible'])

    def test_is_mailbox_frozen__enabled_ok(self):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                'subscription.mail.status': MAIL_STATUS_ACTIVE,
            },
        )
        self.setup_grants(ACCOUNT_IS_MAILBOX_FROZEN_GRANT_PREFIX + '.any')
        resp = self.make_request(
            query_args={'is_mailbox_frozen': '1'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            mail_status=str(MAIL_STATUS_FROZEN),
        )
        self.check_events_ok(mail_status=str(MAIL_STATUS_FROZEN))

    def test_is_mailbox_frozen__disabled_ok(self):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                'subscription.mail.status': MAIL_STATUS_FROZEN,
            },
        )
        self.setup_grants(ACCOUNT_IS_MAILBOX_FROZEN_GRANT_PREFIX + '.any')
        resp = self.make_request(
            query_args={'is_mailbox_frozen': '0'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            mail_status=str(MAIL_STATUS_ACTIVE),
        )
        self.check_events_ok(mail_status=str(MAIL_STATUS_ACTIVE))

    def test_is_mailbox_frozen__disabled_error_already_used(self):
        self.setup_blackbox_responses_and_serialize(
            attributes={
                'subscription.mail.status': MAIL_STATUS_FROZEN,
            },
        )

        common_another_profile = self.get_common_user_profile(uid=2, subscribed_to=[2])
        userinfo_response_other_uid = blackbox_userinfo_response(**common_another_profile)

        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                userinfo_response_other_uid,
            ]
        )

        self.setup_grants(ACCOUNT_IS_MAILBOX_FROZEN_GRANT_PREFIX + '.any')
        resp = self.make_request(
            query_args={'is_mailbox_frozen': '0'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_error_response(resp, ['action.impossible'])

    def test_is_mailbox_frozen__pdd_error(self):
        self.setup_blackbox_responses_and_serialize(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
        )
        self.setup_grants(ACCOUNT_IS_MAILBOX_FROZEN_GRANT_PREFIX + '.any')
        resp = self.make_request(
            query_args={'is_mailbox_frozen': '1'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_is_mailbox_frozen__no_mailbox_error(self):
        self.setup_blackbox_responses_and_serialize()
        self.setup_grants(ACCOUNT_IS_MAILBOX_FROZEN_GRANT_PREFIX + '.any')
        resp = self.make_request(
            query_args={'is_mailbox_frozen': '1'},
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_error_response(resp, ['account.not_subscribed'])


@with_settings_hosts(**PLUS_CHANGE_ATTRIBUTES_SETTINGS)
class TestPlusChangeAttributesView(BaseBundleTestViews):
    default_url = '/1/bundle/plus/%d/?consumer=dev' % TEST_UID
    http_method = 'post'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.grants.set_grant_list(['plus.change_attributes'])
        self.env.start()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID): {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
                str(TEST_CLIENT_ID_2): {
                    'alias': 'datasync_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.setup_statbox_templates()

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            unixtime=TimeNow(),
            tskv_format='passport-log',
            py='1',
            ip='127.0.0.1',
            user_agent='-',
            old='-',
            new='-',
            consumer='dev',
            uid=str(TEST_UID),
            event='account_modification',
        )

        for operation in [
            'updated',
            'created',
            'deleted',
        ]:
            self.env.statbox.bind_entry(
                operation,
                operation=operation,
            )

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        self.env.stop()
        del self.fake_tvm_credentials_manager
        del self.env

    def check_db(self, attributes):
        shard_name = 'passportdbshard1'

        eq_(self.env.db.query_count(shard_name), 1)

        for attribute, value in attributes.items():
            self.env.db.check(
                'attributes',
                attribute,
                value,
                uid=TEST_UID,
                db=shard_name,
            )

    def check_events_ok(self, comment=None, admin_name=None, **options):
        expected_log_entries = {
            'action': 'account',
            'consumer': 'dev',
        }

        for name, expected in options.items():
            if isinstance(expected, bool):
                expected = tskv_bool(expected)
            expected_log_entries[name] = expected

        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

    def assert_disk_plus_subscribe_requested(self, uid):
        self.env.disk_api.requests[0].assert_properties_equal(
            url='http://localhost/v1/disk/partners/yandex_plus/services?product_id=yandex_plus_10gb',
            method='POST',
        )
        self.env.disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(uid),
        })

    def plus_change_attributes_settings_context(self, **kwargs):
        settings = dict(PLUS_CHANGE_ATTRIBUTES_SETTINGS)
        settings.update(kwargs)
        return settings_context(**settings)

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=None,
            ),
        )
        resp = self.make_request(query_args={
            'plus_enabled': '1',
        })
        self.assert_error_response(resp, ['account.not_found'])

    def test_grant_missing(self):
        self.env.grants.set_grant_list([])

        resp = self.make_request(query_args={'plus_enabled': '1'})
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_all_attributes_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
            ),
        )
        self.env.disk_api.set_response_value(
            'plus_subscribe',
            plus_subscribe_created_response(),
            status=201,
        )

        ts_1 = str(get_unixtime())
        ts_2 = str(get_unixtime() - 3600)
        ts_3 = str(get_unixtime() - 3600 * 2)
        ts_4 = str(get_unixtime() - 3600 * 3)

        dt_1 = unixtime_to_statbox_datetime(ts_1)
        dt_2 = unixtime_to_statbox_datetime(ts_2)
        dt_3 = unixtime_to_statbox_datetime(ts_3)
        dt_4 = unixtime_to_statbox_datetime(ts_4)

        ott_subscription = OTT_SUBSCRIPTIONS[0]

        plus_family_role = PLUS_FAMILY_ROLES[0]

        resp = self.make_request(query_args={
            'plus_enabled': '1',
            'plus_trial_used_ts': ts_1,
            'plus_subscription_stopped_ts': ts_2,
            'plus_subscription_expire_ts': ts_3,
            'plus_next_charge_ts': ts_4,
            'ott_subscription': ott_subscription,
            'plus_family_role': plus_family_role,
            'plus_cashback_enabled': '1',
            'plus_subscription_level': '3',
            'plus_is_frozen': '1',
        })
        self.assert_ok_response(resp)

        self.check_db({
            'account.plus.enabled': '1',
            'account.plus.trial_used_ts': ts_1,
            'account.plus.subscription_stopped_ts': ts_2,
            'account.plus.subscription_expire_ts': ts_3,
            'account.plus.next_charge_ts': ts_4,
            'account.plus.ott_subscription': ott_subscription,
            'account.plus.family_role': plus_family_role,
            'account.plus.cashback_enabled': '1',
            'account.plus.subscription_level': '3',
            'account.plus.is_frozen': '1',
        })
        self.check_events_ok(**{
            'plus.enabled': True,
            'plus.trial_used_ts': ts_1,
            'plus.subscription_stopped_ts': ts_2,
            'plus.subscription_expire_ts': ts_3,
            'plus.next_charge_ts': ts_4,
            'plus.ott_subscription': ott_subscription,
            'plus.family_role': plus_family_role,
            'plus.cashback_enabled': True,
            'plus.subscription_level': '3',
            'plus.is_frozen': True,
        })
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('created', entity='plus.enabled', new='1'),
                self.env.statbox.entry('created', entity='plus.trial_used_ts', new=dt_1),
                self.env.statbox.entry('created', entity='plus.subscription_stopped_ts', new=dt_2),
                self.env.statbox.entry('created', entity='plus.subscription_expire_ts', new=dt_3),
                self.env.statbox.entry('created', entity='plus.next_charge_ts', new=dt_4),
                self.env.statbox.entry('created', entity='plus.ott_subscription', new=ott_subscription),
                self.env.statbox.entry('created', entity='plus.family_role', new=plus_family_role),
                self.env.statbox.entry('created', entity='plus.cashback_enabled', new='1'),
                self.env.statbox.entry('created', entity='plus.subscription_level', new='3'),
                self.env.statbox.entry('created', entity='plus.is_frozen', new='1'),
            ],
        )

    def test_several_attributes_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
            ),
        )

        ts_1 = str(get_unixtime())
        ts_2 = str(get_unixtime() - 3600)

        dt_1 = unixtime_to_statbox_datetime(ts_1)
        dt_2 = unixtime_to_statbox_datetime(ts_2)

        resp = self.make_request(query_args={
            'plus_trial_used_ts': ts_1,
            'plus_subscription_stopped_ts': ts_2,
        })
        self.assert_ok_response(resp)

        self.check_db({
            'account.plus.trial_used_ts': ts_1,
            'account.plus.subscription_stopped_ts': ts_2,
        })
        self.check_events_ok(**{
            'plus.trial_used_ts': ts_1,
            'plus.subscription_stopped_ts': ts_2,
        })
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('created', entity='plus.trial_used_ts', new=dt_1),
                self.env.statbox.entry('created', entity='plus.subscription_stopped_ts', new=dt_2),
            ],
        )

    def test_empty_ott_subscription_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={
                    AT['account.plus.enabled']: '1',
                    AT['account.plus.ott_subscription']: 'ott-subscription',
                },
            ),
        )

        resp = self.make_request(query_args={
            'plus_enabled': '1',
            'ott_subscription': '',
        })
        self.assert_ok_response(resp)

        self.check_db({
            # account.plus.enabled не будет записан в бд, т.к. ничего не изменилось
            'account.plus.ott_subscription': None,
        })
        self.check_events_ok(**{
            'plus.ott_subscription': '-',
        })

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('deleted', entity='plus.ott_subscription', new='-', old='ott-subscription'),
            ],
        )

    def test_empty_plus_family_role_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={
                    AT['account.plus.enabled']: '1',
                    AT['account.plus.family_role']: 'family-role',
                },
            ),
        )

        resp = self.make_request(query_args={
            'plus_enabled': '1',
            'plus_family_role': '',
        })
        self.assert_ok_response(resp)

        self.check_db({
            # account.plus.enabled не будет записан в бд, т.к. ничего не изменилось
            'account.plus.family_role': None,
        })
        self.check_events_ok(**{
            'plus.family_role': '-',
        })

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('deleted', entity='plus.family_role', new='-', old='family-role'),
            ],
        )

    def test_disable_zero_attributes_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={
                    AT['account.plus.enabled']: '1',
                    AT['account.plus.trial_used_ts']: '2',
                    AT['account.plus.subscription_stopped_ts']: '3',
                    AT['account.plus.subscription_expire_ts']: '4',
                    AT['account.plus.next_charge_ts']: '5',
                },
            ),
        )
        self.env.disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )

        resp = self.make_request(query_args={
            'plus_enabled': '0',
            'plus_trial_used_ts': '0',
            'plus_subscription_stopped_ts': '0',
            'plus_subscription_expire_ts': '0',
            'plus_next_charge_ts': '0',
        })
        self.assert_ok_response(resp)

        self.check_db({
            'account.plus.enabled': None,
            'account.plus.trial_used_ts': None,
            'account.plus.subscription_stopped_ts': None,
            'account.plus.subscription_expire_ts': None,
            'account.plus.next_charge_ts': None,
        })
        self.check_events_ok(**{
            'plus.enabled': False,
            'plus.trial_used_ts': '0',
            'plus.subscription_stopped_ts': '0',
            'plus.subscription_expire_ts': '0',
            'plus.next_charge_ts': '0',
        })

        dt_1 = unixtime_to_statbox_datetime(2)
        dt_2 = unixtime_to_statbox_datetime(3)
        dt_3 = unixtime_to_statbox_datetime(4)
        dt_4 = unixtime_to_statbox_datetime(5)

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('updated', entity='plus.enabled', new='0', old='1'),
                self.env.statbox.entry('updated', entity='plus.trial_used_ts', new='-', old=dt_1),
                self.env.statbox.entry('updated', entity='plus.subscription_stopped_ts', new='-', old=dt_2),
                self.env.statbox.entry('updated', entity='plus.subscription_expire_ts', new='-', old=dt_3),
                self.env.statbox.entry('updated', entity='plus.next_charge_ts', new='-', old=dt_4),
            ],
        )

    def test_distant_future_ok(self):
        ts_1 = str(2 ** 32)
        dt_1 = unixtime_to_statbox_datetime(ts_1)
        ts_2 = str(2 ** 32 + 1)
        dt_2 = unixtime_to_statbox_datetime(ts_2)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={
                    AT['account.plus.trial_used_ts']: ts_1,
                    AT['account.plus.subscription_stopped_ts']: ts_1,
                    AT['account.plus.subscription_expire_ts']: ts_1,
                    AT['account.plus.next_charge_ts']: ts_1,
                },
            ),
        )

        resp = self.make_request(query_args={
            'plus_trial_used_ts': ts_2,
            'plus_subscription_stopped_ts': ts_2,
            'plus_subscription_expire_ts': ts_2,
            'plus_next_charge_ts': ts_2,
        })
        self.assert_ok_response(resp)

        self.check_db({
            'account.plus.trial_used_ts': ts_2,
            'account.plus.subscription_stopped_ts': ts_2,
            'account.plus.subscription_expire_ts': ts_2,
            'account.plus.next_charge_ts': ts_2,
        })
        self.check_events_ok(**{
            'plus.trial_used_ts': ts_2,
            'plus.subscription_stopped_ts': ts_2,
            'plus.subscription_expire_ts': ts_2,
            'plus.next_charge_ts': ts_2,
        })
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('updated', entity='plus.trial_used_ts', old=dt_1, new=dt_2),
                self.env.statbox.entry('updated', entity='plus.subscription_stopped_ts', old=dt_1, new=dt_2),
                self.env.statbox.entry('updated', entity='plus.subscription_expire_ts', old=dt_1, new=dt_2),
                self.env.statbox.entry('updated', entity='plus.next_charge_ts', old=dt_1, new=dt_2),
            ],
        )

    def test_disable_empty_attributes_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={
                    AT['account.plus.enabled']: '1',
                    AT['account.plus.trial_used_ts']: '2',
                    AT['account.plus.subscription_stopped_ts']: '3',
                    AT['account.plus.subscription_expire_ts']: '4',
                    AT['account.plus.next_charge_ts']: '5',
                },
            ),
        )
        self.env.disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )

        resp = self.make_request(query_args={
            'plus_enabled': '0',
            'plus_trial_used_ts': '',
            'plus_subscription_stopped_ts': '',
            'plus_subscription_expire_ts': '',
            'plus_next_charge_ts': '',
        })
        self.assert_ok_response(resp)

        self.check_db({
            'account.plus.enabled': None,
            'account.plus.trial_used_ts': None,
            'account.plus.subscription_stopped_ts': None,
            'account.plus.subscription_expire_ts': None,
            'account.plus.next_charge_ts': None,
        })
        self.check_events_ok(**{
            'plus.enabled': '0',
            'plus.trial_used_ts': '0',
            'plus.subscription_stopped_ts': '0',
            'plus.subscription_expire_ts': '0',
            'plus.next_charge_ts': '0',
        })

        dt_1 = unixtime_to_statbox_datetime(2)
        dt_2 = unixtime_to_statbox_datetime(3)
        dt_3 = unixtime_to_statbox_datetime(4)
        dt_4 = unixtime_to_statbox_datetime(5)

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('updated', entity='plus.enabled', new='0', old='1'),
                self.env.statbox.entry('updated', entity='plus.trial_used_ts', new='-', old=dt_1),
                self.env.statbox.entry('updated', entity='plus.subscription_stopped_ts', new='-', old=dt_2),
                self.env.statbox.entry('updated', entity='plus.subscription_expire_ts', new='-', old=dt_3),
                self.env.statbox.entry('updated', entity='plus.next_charge_ts', new='-', old=dt_4),
            ],
        )

    def test_plus_disk_subscribe_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
            ),
        )
        self.env.disk_api.set_response_value(
            'plus_subscribe',
            plus_subscribe_created_response(),
            status=201,
        )

        resp = self.make_request(query_args={
            'plus_enabled': '1',
        })
        self.assert_ok_response(resp)

        self.assert_disk_plus_subscribe_requested(TEST_UID)

    def test_plus_disk_unsubscribe_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
            ),
        )
        self.env.disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )

        resp = self.make_request(query_args={
            'plus_enabled': '0',
        })
        self.assert_ok_response(resp)

        self.env.disk_api.requests[0].assert_properties_equal(
            url='http://localhost/v1/disk/partners/yandex_plus/services/remove_by_product?product_id=yandex_plus_10gb',
            method='DELETE',
        )
        self.env.disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_plus_disk_subscribe_fail(self):
        """Проверяем, что подавлено исключение при активации подписки на Диск"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
            ),
        )
        self.env.disk_api.set_response_value(
            'plus_subscribe',
            disk_error_response('InternalServerError'),
            status=500,
        )

        resp = self.make_request(query_args={
            'plus_enabled': '1',
        })
        self.assert_ok_response(resp)

        self.env.disk_api.requests[0].assert_properties_equal(
            url='http://localhost/v1/disk/partners/yandex_plus/services?product_id=yandex_plus_10gb',
            method='POST',
        )
        self.env.disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_plus_disk_unsubscribe_fail(self):
        """Проверяем, что подавлено исключение при деактивации подписки на Диск"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
            ),
        )
        self.env.disk_api.set_response_value(
            'plus_unsubscribe',
            disk_error_response('InternalServerError'),
            status=500,
        )

        resp = self.make_request(query_args={
            'plus_enabled': '0',
        })
        self.assert_ok_response(resp)

        self.env.disk_api.requests[0].assert_properties_equal(
            url='http://localhost/v1/disk/partners/yandex_plus/services/remove_by_product?product_id=yandex_plus_10gb',
            method='DELETE',
        )
        self.env.disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_disk_plus_disabled(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )

        with self.plus_change_attributes_settings_context(DISK_PLUS_ENABLED=False):
            resp = self.make_request(query_args={'plus_enabled': '1'})

        self.assert_ok_response(resp)
        eq_(self.env.disk_api.requests, [])

    def test_yandexoid__disk_plus_disabled(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                aliases={
                    'portal': TEST_LOGIN,
                    'yandexoid': TEST_LOGIN,
                },
            ),
        )

        with self.plus_change_attributes_settings_context(DISK_PLUS_ENABLED=False):
            resp = self.make_request(query_args={'plus_enabled': '1'})

        self.assert_ok_response(resp)
        self.assert_disk_plus_subscribe_requested(TEST_UID)
