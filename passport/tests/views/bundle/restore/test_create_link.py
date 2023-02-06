# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json

import mock
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_ADMIN_COMMENT,
    TEST_ADMIN_NAME,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_UID,
    TEST_EMAIL_RESTORATION_KEY,
    TEST_PDD_CYRILLIC_DOMAIN,
    TEST_PDD_DOMAIN,
    TEST_PDD_DOMAIN_NOT_SERVED,
    TEST_PDD_LOGIN_NOT_SERVED,
    TEST_PDD_UID,
    TEST_PERSISTENT_TRACK_ID,
    TEST_SOCIAL_LOGIN,
    TEST_USER_AGENT,
    TEST_USER_ENTERED_LOGIN,
)
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    RestoreBaseTestCase,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_hosted_domains_response
from passport.backend.core.historydb.events import (
    ACTION_RESTORE_SUPPORT_LINK_CREATED,
    EVENT_INFO_DISABLED_STATUS,
    EVENT_INFO_ENA,
    EVENT_INFO_SUPPORT_LINK_TYPE,
    EVENT_USER_AGENT,
)
from passport.backend.core.models.account import ACCOUNT_DISABLED
from passport.backend.core.models.persistent_track import (
    TRACK_TYPE_AUTH_BY_KEY_LINK,
    TRACK_TYPE_RESTORATION_SUPPORT_LINK,
)
from passport.backend.core.support_link_types import (
    SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
    SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
    SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
    SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import DatetimeNow


RESTORE_BY_LINK_TEMPLATE_URL = 'https://0.passportdev.yandex.%(tld)s/restoration/?key=%(key)s'

AUTH_BY_LINK_TEMPLATE_URL = 'https://0.passportdev.yandex.%(tld)s/auth/?key=%(key)s'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    RESTORE_BY_LINK_TEMPLATE_URL=RESTORE_BY_LINK_TEMPLATE_URL,
    AUTH_BY_KEY_LINK_TEMPLATE_URL=AUTH_BY_LINK_TEMPLATE_URL,
    RESTORATION_MANUAL_LINK_LIFETIME_SECONDS=100500,
    **mock_counters()
)
class RestoreCreateLinkTestCase(RestoreBaseTestCase, AccountValidityTestsMixin):

    restore_step = 'create_link'

    default_url = '/1/bundle/restore/create_link/'

    account_validity_tests_extra_statbox_params = {
        'support_link_type': SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
    }
    account_validity_tests_excluded_statbox_params = [
        'is_suggested_login',
        'selected_methods_order',
        'track_id',
    ]
    is_track_or_key_used = False
    test_invalid_support_link_types = False

    def setUp(self):
        super(RestoreCreateLinkTestCase, self).setUp()
        self.env.grants.set_grants_return_value(mock_grants(grants={'restore': ['base', 'create_link']}))
        self._generate_persistent_track_id_mock = mock.Mock(return_value=TEST_PERSISTENT_TRACK_ID)
        self._generate_persistent_track_id_patch = mock.patch(
            'passport.backend.core.models.persistent_track.generate_track_id',
            self._generate_persistent_track_id_mock,
        )
        self._generate_persistent_track_id_patch.start()

    def tearDown(self):
        self._generate_persistent_track_id_patch.stop()
        del self._generate_persistent_track_id_mock
        del self._generate_persistent_track_id_patch
        super(RestoreCreateLinkTestCase, self).tearDown()

    def base_expected_response(self, user_entered_login=TEST_USER_ENTERED_LOGIN, with_track=True, **kwargs):
        """
        Ручка create_link не отдает трек/логин
        """
        return kwargs

    def query_params(self, link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION, uid=TEST_DEFAULT_UID,
                     admin_name=TEST_ADMIN_NAME, comment=TEST_ADMIN_COMMENT, **kwargs):
        return dict(
            track_id=None,
            uid=uid,
            link_type=link_type,
            admin_name=admin_name,
            comment=comment,
        )

    def assert_db_ok(self, query_count=1, uid=TEST_DEFAULT_UID,
                     track_type=TRACK_TYPE_RESTORATION_SUPPORT_LINK,
                     link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
                     db='passportdbshard1', is_account_disabled=False):
        eq_(self.env.db.query_count(db), query_count)

        track_args_to_check = {
            'uid': uid,
            'created': DatetimeNow(),
            'expired': DatetimeNow(timestamp=datetime.now() + timedelta(seconds=100500)),
        }
        for field, value in track_args_to_check.items():
            self.env.db.check('tracks', field, value, db=db, track_id=TEST_PERSISTENT_TRACK_ID)

        expected_track_content = {
            'type': track_type,
            'support_link_type': link_type,
        }
        content = self.env.db.get(
            'tracks',
            'content',
            db=db,
        )
        eq_(json.loads(content), expected_track_content)

        if is_account_disabled:
            self.env.db.check_db_attr(uid, 'account.is_disabled', str(ACCOUNT_DISABLED))
        else:
            self.env.db.check_db_attr_missing(uid, 'account.is_disabled')

    def assert_events_are_logged(self, link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION, is_account_disabled=False):
        names_values = {
            'action': ACTION_RESTORE_SUPPORT_LINK_CREATED,
            'admin': TEST_ADMIN_NAME,
            'comment': TEST_ADMIN_COMMENT,
            EVENT_INFO_SUPPORT_LINK_TYPE: link_type,
            EVENT_USER_AGENT: TEST_USER_AGENT,
        }
        if is_account_disabled:
            names_values[EVENT_INFO_ENA] = '0'
            names_values[EVENT_INFO_DISABLED_STATUS] = '1'
        super(RestoreCreateLinkTestCase, self).assert_events_are_logged(self.env.handle_mock, names_values)

    def test_force_hint_restoration_not_available_for_2fa_fails(self):
        """Нельзя сделать ссылку для восстановления по КВ/КО для 2ФА пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['account.invalid_type'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='account.invalid_type',
                support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_force_phone_restoration_not_available_for_non_2fa_fails(self):
        """Нельзя сделать ссылку для восстановления исключительно по телефону для не-2ФА пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['account.invalid_type'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='account.invalid_type',
                support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_force_hint_restoration_without_hint_fails(self):
        """Нельзя сделать ссылку для восстановления по КВ/КО для пользователя без КВ/КО"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(hinta=None, hintq=None),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['account.invalid_type'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='account.invalid_type',
                support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_force_hint_restoration_link_for_pdd_not_served_by_support_fails(self):
        """Нельзя создать ссылку ПДД не из списка обслуживаемых саппортами"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                alias_type='pdd',
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN_NOT_SERVED,
                subscribed_to=[102],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='1',
                domain=TEST_PDD_DOMAIN_NOT_SERVED,
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            state='domain_not_served',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_state',
                state='domain_not_served',
                login=TEST_PDD_LOGIN_NOT_SERVED,
                uid=str(TEST_PDD_UID),
                support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_force_hint_restoration_link_created_ok(self):
        """Успешное создание ссылки, предписывающей восстановление по КВ/КО"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            secret_link=RESTORE_BY_LINK_TEMPLATE_URL % dict(tld='ru', key=TEST_EMAIL_RESTORATION_KEY),
        )
        self.assert_db_ok(link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION)
        self.assert_events_are_logged(link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])

    def test_force_phone_restoration_link_created_ok(self):
        """Успешное создание ссылки, предписывающей восстановление по телефону 2ФА пользователю"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            secret_link=RESTORE_BY_LINK_TEMPLATE_URL % dict(tld='ru', key=TEST_EMAIL_RESTORATION_KEY),
        )
        self.assert_db_ok(link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION)
        self.assert_events_are_logged(link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])

    def test_change_password_set_method_link_created_for_2fa_ok(self):
        """Успешное создание ссылки, разрешающей смену пароля и предписывающей установку средства восстановления 2ФА пользователю"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            secret_link=RESTORE_BY_LINK_TEMPLATE_URL % dict(tld='ru', key=TEST_EMAIL_RESTORATION_KEY),
        )
        self.assert_db_ok(
            query_count=2,
            is_account_disabled=True,
            link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.assert_events_are_logged(
            link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            is_account_disabled=True,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                operation='updated',
                old='enabled',
                new='disabled',
                consumer='-',
            ),
            self.env.statbox.entry(
                'passed',
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])

    def test_change_password_set_method_link_created_for_user_without_password_ok(self):
        """Успешное создание ссылки, разрешающей смену пароля и предписывающей установку средства восстановления
        пользователю без пароля"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            secret_link=RESTORE_BY_LINK_TEMPLATE_URL % dict(tld='ru', key=TEST_EMAIL_RESTORATION_KEY),
        )
        self.assert_db_ok(
            query_count=2,
            is_account_disabled=True,
            link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.assert_events_are_logged(
            link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            is_account_disabled=True,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                operation='updated',
                old='enabled',
                new='disabled',
                consumer='-',
            ),
            self.env.statbox.entry(
                'passed',
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                is_password_missing='1',
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])

    def test_complete_autoregistered_link_ok(self):
        """Успешное создание ссылки на дорегистрацию автозарег. пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                password_creating_required=True,
                subscribed_to=[100],
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            secret_link=AUTH_BY_LINK_TEMPLATE_URL % dict(tld='ru', key=TEST_EMAIL_RESTORATION_KEY),
        )
        self.assert_db_ok(
            # Тип трека отличается от обычного
            track_type=TRACK_TYPE_AUTH_BY_KEY_LINK,
            link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION,
        )
        self.assert_events_are_logged(
            link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                support_link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION,
                is_password_missing='1',
                is_autoregistered_completion_required='1',
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])

    def test_complete_social_with_portal_alias_without_password_link_ok(self):
        """Успешное создание ссылки на дорегистрацию соц. пользователя с портальным алиасом и без пароля"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                aliases={
                    'portal': TEST_DEFAULT_LOGIN,
                    'social': TEST_SOCIAL_LOGIN,
                },
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            secret_link=AUTH_BY_LINK_TEMPLATE_URL % dict(tld='ru', key=TEST_EMAIL_RESTORATION_KEY),
        )
        self.assert_db_ok(
            # Тип трека отличается от обычного
            track_type=TRACK_TYPE_AUTH_BY_KEY_LINK,
            link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION,
        )
        self.assert_events_are_logged(
            link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                support_link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION,
                is_social_completion_required='1',
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])

    def test_complete_social_with_portal_alias_without_password_incorrect_link_type_fails(self):
        """Создание ссылки не того типа невозможно для соц. пользователя с портальным алиасом и без пароля"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                aliases={
                    'portal': TEST_DEFAULT_LOGIN,
                    'social': TEST_SOCIAL_LOGIN,
                },
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            state='complete_social',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_state',
                state='complete_social',
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])

    def test_complete_autoregistered_incorrect_link_type_fails(self):
        """Создание ссылки не того типа невозможно для автозарег. пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                password_creating_required=True,
                subscribed_to=[100],
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            state='complete_autoregistered',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_state',
                state='complete_autoregistered',
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])

    def test_complete_link_inapplicable_for_social_user_without_password_fails(self):
        """Ссылка на дорегистрацию не создается для неподходящего пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                aliases={
                    # Соц. пользователь
                    'social': TEST_SOCIAL_LOGIN,
                },
            ),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            state='complete_social',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_state',
                state='complete_social',
                support_link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION,
                login=TEST_SOCIAL_LOGIN,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])

    def test_complete_link_inapplicable_for_simple_user_fails(self):
        """Ссылка на дорегистрацию не создается для неподходящего пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(
            self.query_params(link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['account.invalid_type'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='account.invalid_type',
                support_link_type=SUPPORT_LINK_TYPE_REDIRECT_TO_COMPLETION,
                _exclude=self.account_validity_tests_excluded_statbox_params,
            ),
        ])
