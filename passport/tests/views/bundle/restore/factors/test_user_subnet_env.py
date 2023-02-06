# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    user_env_auths_factors,
    user_env_auths_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.views.bundle.restore.factors import get_user_env_check_status
from passport.backend.core.builders.historydb_api.exceptions import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_successful_aggregated_browser_info,
    auth_successful_aggregated_os_info,
    auth_successful_aggregated_runtime_auth_item,
    auth_successful_aggregated_runtime_auths_item,
    auth_successful_aggregated_runtime_ip_info,
    auths_successful_aggregated_runtime_response,
    event_item,
    events_response,
)
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_FLOAT_MATCH,
    FACTOR_FLOAT_NO_MATCH,
    FACTOR_NOT_SET,
)
from passport.backend.core.compare.test.compare import compare_uas_factor
from passport.backend.core.historydb.events import *
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


@with_settings_hosts()
class UserEnvAuthsHandlerTestCase(BaseCalculateFactorsMixinTestCase):

    def set_historydb_api_responses(self, auths_items=None, events=None):
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=auths_items),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=events),
        )

    def test_no_matches(self):
        self.set_historydb_api_responses()
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors(
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                ),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), False)

    def test_historydb_api_auths_error(self):
        self.env.historydb_api.set_response_side_effect(
            'auths_aggregated_runtime',
            HistoryDBApiTemporaryError,
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(),
        )
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors(
                auths_aggregated_runtime_api_status=False,
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(
                    auths_aggregated_runtime_api_status=False,
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                ),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), False)

    def test_historydb_api_events_error(self):
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(),
        )
        self.env.historydb_api.set_response_side_effect(
            'events',
            HistoryDBApiTemporaryError,
        )
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors(
                historydb_api_events_status=False,
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(
                    historydb_api_events_status=False,
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                ),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), False)

    def test_ip_eq_reg(self):
        self.set_historydb_api_responses(events=[
            event_item(user_ip=TEST_IP, firstname=u'вася', name=EVENT_USERINFO_FT, timestamp=1, yandexuid=None),
            event_item(name=EVENT_INFO_FIRSTNAME, value=u'петя'),
        ])
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors(
                factor_ip_eq_reg=FACTOR_BOOL_MATCH,
                factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
                reg_ip=TEST_IP,
                reg_subnet=TEST_IP_AS_SUBNET,
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(
                    factor_ip_eq_reg=FACTOR_BOOL_MATCH,
                    factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                ),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), False)

    def test_subnet_eq_reg(self):
        self.set_historydb_api_responses(events=[
            event_item(user_ip=TEST_IP_2, firstname=u'вася', name=EVENT_USERINFO_FT, timestamp=1, yandexuid=None),
            event_item(name=EVENT_INFO_FIRSTNAME, value=u'петя'),
        ])
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors(
                factor_ip_eq_reg=FACTOR_BOOL_NO_MATCH,
                factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
                reg_ip=TEST_IP_2,
                reg_subnet=TEST_IP_AS_SUBNET,
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(
                    factor_ip_eq_reg=FACTOR_BOOL_NO_MATCH,
                    factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                ),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), False)

    def test_ua_eq_reg(self):
        self.set_historydb_api_responses(events=[
            event_item(user_ip=TEST_IP_3, firstname=u'вася', name=EVENT_USERINFO_FT, timestamp=1, yandexuid=None),
            event_item(name=EVENT_USER_AGENT, value=TEST_USER_AGENT_2, timestamp=1),
            event_item(name=EVENT_INFO_FIRSTNAME, value=u'петя'),
        ])
        userinfo_response = self.default_userinfo_response()
        headers = self.get_headers(user_agent=TEST_USER_AGENT_2)
        with self.create_base_bundle_view(userinfo_response, headers=headers) as view:
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors(
                factor_ip_eq_reg=FACTOR_BOOL_NO_MATCH,
                factor_subnet_eq_reg=FACTOR_NOT_SET,
                factor_ua_eq_reg=compare_uas_factor('os.name', 'browser.name'),
                user_agent=TEST_USER_AGENT_2_PARSED,
                reg_ip=TEST_IP_3,
                reg_user_agent=TEST_USER_AGENT_2_PARSED_WITHOUT_YANDEXUID,
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(
                    factor_ip_eq_reg=FACTOR_BOOL_NO_MATCH,
                    factor_subnet_eq_reg=FACTOR_NOT_SET,
                    factor_ua_eq_reg=compare_uas_factor('os.name', 'browser.name'),
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                ),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), False)

    def test_ip_subnet_found_in_auths_once_at_registration(self):
        self.set_historydb_api_responses(auths_items=[
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(
                        authtype=authtypes.AUTH_TYPE_IMAP,
                        status='successful',
                        ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP),
                    ),
                    auth_successful_aggregated_runtime_auth_item(
                        browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                        count=10,
                    ),
                ],
                timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
            ),
        ])
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors()
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), True)

    def test_subnet_found_in_auths_once_now(self):
        now_ts = round(time.time())  # округляем чтобы было меньше погрешностей
        reg_ts = now_ts - timedelta(days=10).total_seconds()
        self.set_historydb_api_responses(auths_items=[
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(
                        authtype=authtypes.AUTH_TYPE_IMAP,
                        status='successful',
                        ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP_2),
                    ),
                    auth_successful_aggregated_runtime_auth_item(
                        browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                        count=10,
                    ),
                ],
                timestamp=now_ts,
            ),
        ])
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(reg_ts)))
        with self.create_base_bundle_view(userinfo_response) as view, self.time_now_mock(now_ts):
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors(
                subnet_first_auth=build_auth_info(timestamp=now_ts),
                subnet_last_auth=build_auth_info(timestamp=now_ts),
                factor_subnet_auth_interval=FACTOR_FLOAT_NO_MATCH,
                factor_subnet_first_auth_depth=FACTOR_FLOAT_NO_MATCH,
                ip_first_auth=None,
                ip_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(
                    factor_subnet_auth_interval=FACTOR_FLOAT_NO_MATCH,
                    factor_subnet_first_auth_depth=FACTOR_FLOAT_NO_MATCH,
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                ),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), True)

    def test_ip_subnet_found_in_auths_many_times(self):
        now_ts = round(time.time())  # округляем чтобы было меньше погрешностей
        reg_ts = now_ts - timedelta(days=10).total_seconds()
        last_auth_ts = reg_ts + timedelta(days=5).total_seconds()
        self.set_historydb_api_responses(auths_items=[
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(
                        authtype=authtypes.AUTH_TYPE_IMAP,
                        status='successful',
                        ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP),
                    ),
                ],
                timestamp=last_auth_ts,
            ),
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(
                        browser_info=auth_successful_aggregated_browser_info(),
                    ),
                ],
                timestamp=reg_ts + timedelta(days=1).total_seconds(),
            ),
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(
                        ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP),
                    ),
                ],
                timestamp=reg_ts,
            ),
        ])
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(reg_ts)))
        with self.create_base_bundle_view(userinfo_response) as view, self.time_now_mock(now_ts):
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors(
                ip_first_auth=build_auth_info(authtype=authtypes.AUTH_TYPE_WEB, status='ses_create', timestamp=reg_ts),
                ip_last_auth=build_auth_info(timestamp=last_auth_ts),
                subnet_first_auth=build_auth_info(authtype=authtypes.AUTH_TYPE_WEB, status='ses_create', timestamp=reg_ts),
                subnet_last_auth=build_auth_info(timestamp=last_auth_ts),
                factor_ip_auth_interval=0.5,
                factor_subnet_auth_interval=0.5,
                factor_ip_first_auth_depth=FACTOR_FLOAT_MATCH,
                factor_subnet_first_auth_depth=FACTOR_FLOAT_MATCH,
                gathered_auths_count=3,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(
                    factor_ip_auth_interval=0.5,
                    factor_subnet_auth_interval=0.5,
                    factor_ip_first_auth_depth=FACTOR_FLOAT_MATCH,
                    factor_subnet_first_auth_depth=FACTOR_FLOAT_MATCH,
                ),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), True)

    def test_ua_found_in_auths_many_times(self):
        now_ts = round(time.time())  # округляем чтобы было меньше погрешностей
        reg_ts = now_ts - timedelta(days=10).total_seconds()
        last_auth_ts = reg_ts + timedelta(days=5).total_seconds()
        self.set_historydb_api_responses(auths_items=[
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(
                        authtype=authtypes.AUTH_TYPE_IMAP,
                        status='successful',
                        browser_info=auth_successful_aggregated_browser_info(yandexuid=TEST_YANDEXUID_COOKIE),
                        os_info=auth_successful_aggregated_os_info(name='Windows XP'),
                    ),
                ],
                timestamp=last_auth_ts,
            ),
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(),
                ],
                timestamp=reg_ts + timedelta(days=1).total_seconds(),
            ),
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(
                        browser_info=auth_successful_aggregated_browser_info(yandexuid=TEST_YANDEXUID_COOKIE),
                        os_info=auth_successful_aggregated_os_info(name='Windows XP'),
                    ),
                ],
                timestamp=reg_ts,
            ),
        ])
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(reg_ts)))
        headers = self.get_headers(user_agent=TEST_USER_AGENT_2)
        with self.create_base_bundle_view(userinfo_response, headers=headers) as view, self.time_now_mock(now_ts):
            factors = view.calculate_factors('user_env_auths')
            expected_factors = user_env_auths_factors(
                ua_first_auth=build_auth_info(authtype=authtypes.AUTH_TYPE_WEB, status='ses_create', timestamp=reg_ts),
                ua_last_auth=build_auth_info(timestamp=last_auth_ts),
                factor_ua_auth_interval=0.5,
                factor_ua_first_auth_depth=FACTOR_FLOAT_MATCH,
                user_agent=TEST_USER_AGENT_2_PARSED,
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=3,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                user_env_auths_statbox_entry(
                    factor_ua_auth_interval=0.5,
                    factor_ua_first_auth_depth=FACTOR_FLOAT_MATCH,
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                ),
                view.statbox,
            )
            eq_(get_user_env_check_status(factors), True)

    def test_auths_limit_reached(self):
        self.set_historydb_api_responses(auths_items=[
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(
                        authtype=authtypes.AUTH_TYPE_IMAP,
                        status='successful',
                        ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP),
                    ),
                ],
                timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
            ),
        ])
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            with settings_context(RESTORE_SEMI_AUTO_AUTHS_HISTORY_LIMIT=1):

                factors = view.calculate_factors('user_env_auths')
                expected_factors = user_env_auths_factors(
                    factor_auths_limit_reached=FACTOR_BOOL_MATCH,
                    gathered_auths_count=1,
                )
                eq_(factors, expected_factors)
                self.assert_entry_in_statbox(
                    user_env_auths_statbox_entry(
                        factor_auths_limit_reached=FACTOR_BOOL_MATCH,
                    ),
                    view.statbox,
                )
                eq_(get_user_env_check_status(factors), True)
