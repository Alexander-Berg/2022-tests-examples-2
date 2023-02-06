# -*- coding: utf-8 -*-
import json
import time

import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
    TEST_DEFAULT_BIRTHDAY,
    TEST_DEFAULT_FIRSTNAME,
    TEST_DEFAULT_LASTNAME,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_REGISTRATION_TIMESTAMP,
    TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
    TEST_DEFAULT_UID,
    TEST_HOST,
    TEST_IP,
    TEST_LITE_LOGIN,
    TEST_PDD_LOGIN,
    TEST_PDD_LOGIN_NOT_SERVED,
    TEST_PDD_UID,
    TEST_REQUEST_SOURCE,
    TEST_SOCIAL_LOGIN,
    TEST_USER_AGENT,
    TEST_YANDEXUID_COOKIE,
    TRANSLATIONS_QUESTIONS,
)
from passport.backend.api.tests.views.bundle.restore.test.test_base import RestoreTestUtilsMixin
from passport.backend.core import authtypes
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_hosted_domains_response
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_successful_aggregated_browser_info,
    auth_successful_aggregated_runtime_auth_item,
    auth_successful_aggregated_runtime_auths_item,
    auth_successful_aggregated_runtime_ip_info,
    auths_successful_aggregated_runtime_response,
    event_item,
    events_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator


eq_ = iterdiff(eq_)


@with_settings_hosts(
    ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD=TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
)
class BaseTestRestoreSemiAutoView(BaseBundleTestViews, RestoreTestUtilsMixin):
    statbox_action = 'submitted'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.setup_trackid_generator()
        self.setup_statbox_templates()
        self.env.grants.set_grants_return_value(mock_grants(grants={'restore': ['semi_auto']}))
        self.questions_settings_patch = mock.patch.object(
            settings.translations,
            'QUESTIONS',
            TRANSLATIONS_QUESTIONS,
        )
        self.questions_settings_patch.start()

    def tearDown(self):
        self.questions_settings_patch.stop()
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.questions_settings_patch
        del self.track_id_generator

    def setup_trackid_generator(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('restore')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

    def setup_statbox_templates(self, **kwargs):
        base_params = dict(
            ip=TEST_IP,
            mode='restore_semi_auto',
            host=TEST_HOST,
            track_id=self.track_id,
            request_source=TEST_REQUEST_SOURCE,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
        )
        base_params.update(kwargs)
        self.env.statbox.bind_base(
            login=TEST_DEFAULT_LOGIN,
            uid=str(TEST_DEFAULT_UID),
            **base_params
        )
        self.env.statbox.bind_entry(
            'submitted',
            action='submitted',
            _exclude=['uid'],
        )
        for action in ('compared', 'finished_with_error', 'finished_with_state', 'got_state'):
            self.env.statbox.bind_entry(
                action,
                action=action,
            )

    def make_request(self, data, headers=None):
        return self.env.client.post(
            self.default_url,
            data=data,
            headers=headers,
        )

    def get_headers(self, host=None, user_ip=None, cookie=None, user_agent=None):
        return mock_headers(
            host=host or TEST_HOST,
            user_agent=user_agent or TEST_USER_AGENT,
            cookie=cookie or 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            user_ip=user_ip or TEST_IP,
        )

    def set_historydb_responses(self, names_present=True, birthday_present=True,
                                firstname=TEST_DEFAULT_FIRSTNAME,
                                lastname=TEST_DEFAULT_LASTNAME,
                                birthday=TEST_DEFAULT_BIRTHDAY,
                                userinfo_ft=False,
                                user_ip=TEST_IP, extra_events=None,
                                events_passwords_response=None,
                                events_passwords_side_effect=None,
                                events_side_effect=None,
                                timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP,
                                auths_aggregated_runtime_present=False,
                                auths_aggregated_runtime_items=None):
        events = []
        if names_present:
            events.extend([
                event_item(name='info.firstname', value=firstname, user_ip=user_ip, timestamp=timestamp),
                event_item(name='info.lastname', value=lastname, user_ip=user_ip, timestamp=timestamp),
            ])
        if birthday_present:
            events.append(event_item(name='info.birthday', value=birthday, user_ip=user_ip, timestamp=timestamp))
        if extra_events:
            events.extend(extra_events)

        if events_side_effect is not None:
            self.env.historydb_api.set_response_side_effect(
                'events',
                events_side_effect,
            )
        else:
            self.env.historydb_api.set_response_value(
                'events',
                events_response(events=sorted(events, key=lambda event: event['timestamp'])),
            )

        if events_passwords_response is not None:
            self.env.historydb_api.set_response_value(
                'events_passwords',
                events_passwords_response,
            )
        if events_passwords_side_effect is not None:
            self.env.historydb_api.set_response_side_effect(
                'events_passwords',
                events_passwords_side_effect,
            )

        if auths_aggregated_runtime_present:
            auths_items = auths_aggregated_runtime_items
            auths_items = auths_items if auths_items is not None else [
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
            ]
            self.env.historydb_api.set_response_value(
                'auths_aggregated_runtime',
                auths_successful_aggregated_runtime_response(items=auths_items),
            )

    def assert_state_or_error_recorded_to_statbox(self, state=None, error=None, **kwargs):
        if state:
            entry = self.env.statbox.entry('finished_with_state', state=state, **kwargs)
        else:
            entry = self.env.statbox.entry('finished_with_error', error=error, **kwargs)

        self.env.statbox.assert_has_written([entry])

    def assert_submit_state_or_error_recorded_to_statbox(self, state=None, error=None, uid=None, **kwargs):
        entries = [self.env.statbox.entry('submitted', **kwargs)]
        if uid is not None:
            kwargs['uid'] = str(uid)
        if state:
            entries.append(self.env.statbox.entry('finished_with_state', state=state, **kwargs))
        elif error:
            entries.append(self.env.statbox.entry('finished_with_error', error=error, **kwargs))

        self.env.statbox.assert_has_written(entries)

    def assert_mail_not_sent(self):
        eq_(self.env.mailer.message_count, 0)

    def check_restore_log_empty(self):
        eq_(self.restore_handle_mock.call_count, 0)

    def check_restore_log_entry(self, **kwargs):
        eq_(self.restore_handle_mock.call_count, 1)
        log_entry = self.restore_handle_mock.call_args_list[0][0][0]
        for field, value in kwargs.items():
            actual = self._get_log_field(field, log_type='restore', log_msg=log_entry)
            if field == 'data_json':
                actual = json.loads(actual)
            eq_(
                actual,
                value,
                (field, actual, value),
            )


class CheckAccountByLoginTests(object):

    def test_unknown_login_fails(self):
        """Неизвестный логин"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, ['account.not_found'])
        self.assert_submit_state_or_error_recorded_to_statbox(
            error='account.not_found',
            _exclude=['uid'],
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_unknown_lite_login_fails(self):
        """Неизвестный lite-логин"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        self.set_track_values(user_entered_login=TEST_LITE_LOGIN)
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, ['account.not_found'])
        self.assert_submit_state_or_error_recorded_to_statbox(
            error='account.not_found',
            login=TEST_LITE_LOGIN,
            _exclude=['uid'],
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_account_disabled_fails(self):
        """Аккаунт отключен"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled=False),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, ['account.disabled'])
        self.assert_submit_state_or_error_recorded_to_statbox(
            error='account.disabled',
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_account_disabled_on_deletion_too_long_ago_fails(self):
        """Аккаунт заблокирован при удалении, время карантина вышло"""
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'account.deletion_operation_started_at': deletion_started_at,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, ['account.disabled'])
        self.assert_submit_state_or_error_recorded_to_statbox(
            error='account.disabled',
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_pdd_account_disabled_on_deletion_recently__domain_disabled__fails(self):
        """ПДД-аккаунт недавно заблокирован при удалении, но его домен заблокирован и восстановление невозможно"""
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 100
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
                attributes={
                    'account.deletion_operation_started_at': deletion_started_at,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
                domain_enabled=False,
            ),
        )
        self.set_track_values(user_entered_login=TEST_PDD_LOGIN)

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, ['account.disabled'])
        self.assert_submit_state_or_error_recorded_to_statbox(
            error='account.disabled',
            login=TEST_PDD_LOGIN,
            uid=str(TEST_PDD_UID),
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_lite_account_disabled_fails(self):
        """Lite-аккаунт отключен"""
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                self.default_userinfo_response(uid=None),
                self.default_userinfo_response(
                    aliases={
                        'lite': TEST_LITE_LOGIN,
                    },
                    enabled=False,
                ),
            ],
        )
        self.set_track_values(user_entered_login=TEST_LITE_LOGIN)
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, ['account.disabled'])
        self.assert_submit_state_or_error_recorded_to_statbox(
            error='account.disabled',
            login=TEST_LITE_LOGIN,
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_incomplete_pdd_redirect(self):
        """Недорегистрированный пользователь ПДД получает приглашение дорегистрироваться"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )
        self.set_track_values(user_entered_login=TEST_PDD_LOGIN)
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, state='complete_pdd')
        self.assert_submit_state_or_error_recorded_to_statbox(
            state='complete_pdd',
            login=TEST_PDD_LOGIN,
            uid=str(TEST_PDD_UID),
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_pdd_cannot_change_password_ok(self):
        """Пользователь ПДД с запретом смены пароля не может воспользоваться восстановлением"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='0'),
        )
        self.set_track_values(user_entered_login=TEST_PDD_LOGIN)
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, state='password_change_forbidden')
        self.assert_submit_state_or_error_recorded_to_statbox(
            state='password_change_forbidden',
            login=TEST_PDD_LOGIN,
            uid=str(TEST_PDD_UID),
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_pdd_domain_not_served_ok(self):
        """Пользователь ПДД, домен не обслуживается саппортами Яндекса"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN_NOT_SERVED,
                aliases={
                    'pdd': TEST_PDD_LOGIN_NOT_SERVED,
                },
                subscribed_to=[102],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1'),
        )
        self.set_track_values(user_entered_login=TEST_PDD_LOGIN_NOT_SERVED)
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, state='domain_not_served')
        self.assert_submit_state_or_error_recorded_to_statbox(
            state='domain_not_served',
            login=TEST_PDD_LOGIN_NOT_SERVED,
            uid=str(TEST_PDD_UID),
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_password_not_set_fails(self):
        """У не-социального пользователя не установлен пароль"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(password=''),
        )
        self.set_track_values()
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['account.without_password'])
        self.assert_submit_state_or_error_recorded_to_statbox(
            error='account.without_password',
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_social_password_not_set_ok(self):
        """У социального пользователя не установлен пароль"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_SOCIAL_LOGIN,
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
                password='',
            ),
        )
        self.set_track_values(user_entered_login=TEST_SOCIAL_LOGIN)
        resp = self.make_request(
            self.query_params(),
            self.get_headers(),
        )

        self.assert_ok_response(resp, state='complete_social')
        self.assert_submit_state_or_error_recorded_to_statbox(
            state='complete_social',
            login=TEST_SOCIAL_LOGIN,
        )
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_with_portal_and_social_aliases_password_not_set_ok(self):
        """У пользователя, имеющего и портальный, и социальный алиасы, не установлен пароль"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                password='',
                aliases={
                    'portal': TEST_DEFAULT_LOGIN,
                    'social': TEST_SOCIAL_LOGIN,
                },
            ),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, state='complete_social')
        self.assert_submit_state_or_error_recorded_to_statbox(state='complete_social')
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_mail_not_sent()

    def test_autoregistered_password_changing_required_redirect(self):
        """Автозарегистрированный пользователь с требованием смены пароля"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(password_creating_required=True, subscribed_to=[100]),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, state='complete_autoregistered')
        self.assert_submit_state_or_error_recorded_to_statbox(state='complete_autoregistered')
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()
