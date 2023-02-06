# -*- coding: utf-8 -*-

import time

from passport.backend.api.common.processes import PROCESS_RESTORE
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_UID,
    TEST_EMAIL,
    TEST_EMAIL_RESTORATION_KEY,
    TEST_FAMILY_ID,
    TEST_OPERATION_TTL,
    TEST_PDD_CYRILLIC_DOMAIN,
    TEST_PDD_DOMAIN,
    TEST_PDD_EMAIL_RESTORATION_KEY,
    TEST_PDD_UID,
    TEST_PERSISTENT_TRACK_ID,
    TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
    TEST_USER_ENTERED_LOGIN,
)
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonTestsMixin,
    RestoreBaseTestCase,
)
from passport.backend.api.views.bundle.restore.base import (
    RESTORE_METHOD_EMAIL,
    RESTORE_METHOD_HINT,
    RESTORE_METHOD_LINK,
    RESTORE_METHOD_PHONE,
    RESTORE_METHOD_SEMI_AUTO_FORM,
    RESTORE_STATE_METHOD_PASSED,
    RESTORE_STATE_METHOD_SELECTED,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_family_info_response,
    blackbox_get_track_response,
)
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.persistent_track import (
    TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK,
    TRACK_TYPE_RESTORATION_SUPPORT_LINK,
)
from passport.backend.core.support_link_types import (
    SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
    SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
    SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class RestoreKeySubmitTestCase(RestoreBaseTestCase, EmailTestMixin, CommonTestsMixin, AccountValidityTestsMixin):

    restore_step = 'key_submit'

    default_url = '/1/bundle/restore/key/submit/'

    account_validity_tests_extra_statbox_params = {
        'is_track_passed': '1',
        'does_key_exist': '1',
        'is_key_expired': '0',
        'key_type': str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
    }
    test_invalid_support_link_types = False

    def setUp(self):
        super(RestoreKeySubmitTestCase, self).setUp()
        self.set_persistent_track_content_for_email_restoration(user_entered_login=None)
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.env.statbox.bind_entry(
            'passed_with_email',
            _inherit_from='passed',
            matched_emails_count='1',
            is_email_confirmed='1',
            is_email_external='1',
            is_email_rpop='0',
            is_email_silent='0',
            is_email_suitable='1',
            is_email_unsafe='0',
        )

    def tearDown(self):
        self.track_id_generator.stop()
        del self.track_id_generator
        super(RestoreKeySubmitTestCase, self).tearDown()

    def set_track_values(self, restore_state=RESTORE_STATE_METHOD_SELECTED,
                         current_restore_method=RESTORE_METHOD_EMAIL,
                         uid=TEST_DEFAULT_UID,
                         **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
            uid=uid,
        )
        super(RestoreKeySubmitTestCase, self).set_track_values(**params)

    def set_persistent_track_content_for_email_restoration(self, uid=TEST_DEFAULT_UID,
                                                           user_entered_login=TEST_USER_ENTERED_LOGIN,
                                                           user_entered_email=TEST_EMAIL, retpath=None):
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                uid,
                TEST_PERSISTENT_TRACK_ID,
                created=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
                expired=int(time.time() + 60),
                content={
                    'type': TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK,
                    'user_entered_login': user_entered_login,
                    'user_entered_email': user_entered_email,
                    'retpath': retpath,
                    'initiator_track_id': 'old-track-id',
                },
            ),
        )

    def set_persistent_track_content_for_support_link(self, uid=TEST_DEFAULT_UID,
                                                      link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION):
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                uid,
                TEST_PERSISTENT_TRACK_ID,
                created=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
                expired=int(time.time() + 60),
                content={
                    'type': TRACK_TYPE_RESTORATION_SUPPORT_LINK,
                    'support_link_type': link_type,
                },
            ),
        )

    def query_params(self, secret_key=TEST_EMAIL_RESTORATION_KEY, **params):
        return dict(
            params,
            secret_key=secret_key,
        )

    def assert_track_created(self, **params):
        self.assert_track_updated(
            is_created=True,
            created=TimeNow(),
            process_name=PROCESS_RESTORE,
            restore_methods_select_order=[],
            suggested_logins=[],
            phone_operation_confirmations=[],
            totp_push_device_ids=[],
            **params
        )

    def assert_blackbox_userinfo_called(self, uid=TEST_DEFAULT_UID, call_index=0):
        super(RestoreKeySubmitTestCase, self).assert_blackbox_userinfo_called(
            uid=uid,
            call_index=call_index,
        )

    def test_with_track_unexpected_but_valid_restore_state_fails(self):
        """Трек с недопустимым (но корректным) состоянием восстановления не принимаем"""
        self.set_track_values(restore_state=RESTORE_STATE_METHOD_PASSED)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'])

    def test_with_track_unexpected_restore_method_fails(self):
        """Трек с недопустимым способом восстановления не принимаем"""
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_PHONE,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'])

    def test_with_track_restoration_key_not_found_fails(self):
        """Работаем с существующим треком, ключ восстановления не найден"""
        self.set_track_values()
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(TEST_DEFAULT_UID, TEST_PERSISTENT_TRACK_ID, is_found=False),
        )

        resp = self.make_request(
            self.query_params(),
            headers=self.get_headers(),
        )

        self.assert_error_response(resp, ['secret_key.invalid'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='secret_key.invalid',
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='0',
                is_track_passed='1',
            ),
        ])

    def test_without_track_restoration_key_expired_fails(self):
        """Работаем без трека, ключ восстановления протух"""
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(TEST_DEFAULT_UID, TEST_PERSISTENT_TRACK_ID, expired=int(time.time())),
        )

        resp = self.make_request(
            self.query_params(track_id=None),
            headers=self.get_headers(),
        )

        self.assert_error_response(resp, ['secret_key.invalid'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='secret_key.invalid',
                does_key_exist='1',
                is_key_expired='1',
                is_track_passed='0',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
                _exclude=['is_suggested_login', 'login', 'selected_methods_order', 'track_id'],
            ),
        ])

    def test_with_track_restoration_key_invalid_type_fails(self):
        """Работаем с существующим треком, тип ключа восстановления не поддерживается"""
        self.set_track_values()
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                TEST_DEFAULT_UID,
                TEST_PERSISTENT_TRACK_ID,
                expired=int(time.time() + 60),
                content={'type': 'bad'},
            ),
        )

        resp = self.make_request(
            self.query_params(),
            headers=self.get_headers(),
        )

        self.assert_error_response(resp, ['secret_key.invalid'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='secret_key.invalid',
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='1',
                is_key_expired='0',
                key_type='bad',
                is_track_passed='1',
            ),
        ])

    def test_with_track_restoration_key_uid_not_matches_track_uid_fails(self):
        """Работаем с существующим треком, UID в треке не совпадает с UID-ом в ключе"""
        self.set_track_values()
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                TEST_PDD_UID,
                TEST_PERSISTENT_TRACK_ID,
                expired=int(time.time() + 60),
            ),
        )

        resp = self.make_request(
            self.query_params(secret_key=TEST_PDD_EMAIL_RESTORATION_KEY),
            headers=self.get_headers(),
        )

        self.assert_error_response(resp, ['secret_key.invalid'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='secret_key.invalid',
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='1',
                is_key_expired='0',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
                is_track_passed='1',
            ),
        ])

    def test_without_track_restoration_key_older_than_logout_fails(self):
        """Использован ключ восстановления, который был создан до момента логаута"""
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                TEST_DEFAULT_UID,
                TEST_PERSISTENT_TRACK_ID,
                expired=int(time.time() + 60),
                content={
                    'type': TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK,
                    'user_entered_login': TEST_USER_ENTERED_LOGIN,
                    'user_entered_email': TEST_EMAIL,
                    'retpath': None,
                    'initiator_track_id': 'old-track-id',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'revoker.web_sessions': int(time.time()),
                },
            ),
        )

        resp = self.make_request(self.query_params(track_id=None), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['account.global_logout'],
            **self.base_expected_response(with_track=False)
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='account.global_logout',
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='0',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
                _exclude=['is_suggested_login', 'selected_methods_order', 'track_id'],
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_with_track_older_than_logout_fails(self):
        """Использован трек, который был создан до момента логаута"""
        self.set_persistent_track_content_for_email_restoration()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'revoker.web_sessions': int(time.time() + 10),
                },
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['account.global_logout'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='account.global_logout',
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='1',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_with_track_restore_method_no_more_suitable_fails(self):
        """Работаем с существующим треком, способ восстановления более недоступен"""
        self.set_persistent_track_content_for_email_restoration()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            user_entered_email=TEST_EMAIL,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            track_id=self.track_id,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='1',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
                initiator_track_id='old-track-id',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_without_track_restore_method_no_more_suitable_fails(self):
        """Работаем без трека, способ восстановления более недоступен"""
        self.set_persistent_track_content_for_email_restoration()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            self.orig_track = track.snapshot()

        resp = self.make_request(self.query_params(track_id=None), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            track_id=self.track_id,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
        )
        # Создается новый трек восстановления, с ним далее можно идти в get_state для получения альтернатив
        self.assert_track_created(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_EMAIL,
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            user_entered_email=TEST_EMAIL,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='0',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
                initiator_track_id='old-track-id',
                _exclude=['is_suggested_login', 'selected_methods_order'],
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_with_track_email_no_more_suitable_fails(self):
        """Работаем с существующим треком, способ восстановления доступен, но использованный email стал недоступен"""
        self.set_persistent_track_content_for_email_restoration()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
            ),
        )
        self.set_track_values(
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            user_entered_email=TEST_EMAIL,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['email.changed'],
            track_id=self.track_id,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='email.changed',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='1',
                matched_emails_count='0',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
                initiator_track_id='old-track-id',
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_with_track_ok(self):
        """Работаем с существующим треком, ручка успешно отрабатывает"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.set_persistent_track_content_for_email_restoration(
            user_entered_email=entered_email,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
            ),
        )
        self.set_track_values(
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            user_entered_email=entered_email,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
        )
        self.assert_track_updated(
            is_strong_password_policy_required=False,
            is_email_check_passed=True,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            restore_state=RESTORE_STATE_METHOD_PASSED,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed_with_email',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='1',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
                initiator_track_id='old-track-id',
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_with_track_with_disabled_on_deletion_account_ok(self):
        """Аккаунт заблокирован при удалении не слишком давно, восстановление возможно"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.set_persistent_track_content_for_email_restoration(
            user_entered_email=entered_email,
        )
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 50
        userinfo = self.default_userinfo_response(
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
            ],
            attributes={
                'account.deletion_operation_started_at': deletion_started_at,
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.set_track_values(
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            user_entered_email=entered_email,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
        )
        self.assert_track_updated(
            is_strong_password_policy_required=False,
            is_email_check_passed=True,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            restore_state=RESTORE_STATE_METHOD_PASSED,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed_with_email',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='1',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
                initiator_track_id='old-track-id',
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_without_track_ok(self):
        """Работаем без трека, ручка успешно отрабатывает"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.set_persistent_track_content_for_email_restoration(
            user_entered_email=entered_email,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
            ),
        )
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            self.orig_track = track.snapshot()

        resp = self.make_request(self.query_params(track_id=None), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
        )
        self.assert_track_created(
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            current_restore_method=RESTORE_METHOD_EMAIL,
            user_entered_email=entered_email,
            is_email_check_passed=True,
            is_strong_password_policy_required=False,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed_with_email',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='0',
                key_type=str(TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK),
                initiator_track_id='old-track-id',
                is_hint_masked='1',
                _exclude=['is_suggested_login', 'selected_methods_order'],
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_support_link_hint_restoration_without_hint_fails(self):
        """Нельзя обработать ссылку для восстановления по КВ/КО для пользователя без КВ/КО"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(hinta=None, hintq=None),
        )
        self.set_persistent_track_content_for_support_link(
            link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
        )

        resp = self.make_request(
            self.query_params(track_id=None),
            self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['account.invalid_type'],
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='account.invalid_type',
                support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='0',
                key_type=str(TRACK_TYPE_RESTORATION_SUPPORT_LINK),
                _exclude=['is_suggested_login', 'selected_methods_order'],
            ),
        ])
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_blackbox_userinfo_called()

    def test_support_link_hint_restoration_ok(self):
        """Успешно обработали ссылку для восстановления по КВ/КО"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_persistent_track_content_for_support_link(
            link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
        )
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            self.orig_track = track.snapshot()

        resp = self.make_request(
            self.query_params(track_id=None),
            self.get_headers(),
        )

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_DEFAULT_LOGIN)
        self.assert_track_created(
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            user_entered_login=TEST_DEFAULT_LOGIN,
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_HINT,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='0',
                key_type=str(TRACK_TYPE_RESTORATION_SUPPORT_LINK),
                current_restore_method=RESTORE_METHOD_HINT,
                _exclude=['is_suggested_login', 'selected_methods_order'],
            ),
        ])
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_blackbox_userinfo_called()

    def test_support_link_force_phone_restoration_for_2fa_ok(self):
        """Успешно обработали ссылку для восстановления по телефону для 2ФА пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        self.set_persistent_track_content_for_support_link(
            link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
        )
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            self.orig_track = track.snapshot()

        resp = self.make_request(
            self.query_params(track_id=None),
            self.get_headers(),
        )

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_DEFAULT_LOGIN)
        self.assert_track_created(
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
            user_entered_login=TEST_DEFAULT_LOGIN,
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_PHONE,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='0',
                key_type=str(TRACK_TYPE_RESTORATION_SUPPORT_LINK),
                current_restore_method=RESTORE_METHOD_PHONE,
                _exclude=['is_suggested_login', 'selected_methods_order'],
            ),
        ])
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_blackbox_userinfo_called()

    def test_support_link_change_password_with_required_method_for_2fa_ok(self):
        """Успешно обработали ссылку для ввода новых данных с привязкой средства восстановления для 2ФА пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        self.set_persistent_track_content_for_support_link(
            link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            self.orig_track = track.snapshot()

        resp = self.make_request(
            self.query_params(track_id=None),
            self.get_headers(),
        )

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_DEFAULT_LOGIN)
        self.assert_track_created(
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            user_entered_login=TEST_DEFAULT_LOGIN,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            current_restore_method=RESTORE_METHOD_LINK,
            is_strong_password_policy_required=False,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                current_restore_method=RESTORE_METHOD_LINK,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='0',
                key_type=str(TRACK_TYPE_RESTORATION_SUPPORT_LINK),
                _exclude=['is_suggested_login', 'selected_methods_order'],
            ),
        ])
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_blackbox_userinfo_called()

    def test_support_link_change_password_with_required_method_without_password_ok(self):
        """У пользователя, имеющего портальный алиас, не установлен пароль, саппорт выписал ссылку"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                enabled=False,
            ),
        )
        self.set_persistent_track_content_for_support_link(
            link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            self.orig_track = track.snapshot()

        resp = self.make_request(
            self.query_params(track_id=None),
            self.get_headers(),
        )

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_DEFAULT_LOGIN)
        self.assert_track_created(
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            user_entered_login=TEST_DEFAULT_LOGIN,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            current_restore_method=RESTORE_METHOD_LINK,
            is_strong_password_policy_required=False,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                is_password_missing='1',
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                current_restore_method=RESTORE_METHOD_LINK,
                does_key_exist='1',
                is_key_expired='0',
                is_track_passed='0',
                key_type=str(TRACK_TYPE_RESTORATION_SUPPORT_LINK),
                _exclude=['is_suggested_login', 'selected_methods_order'],
            ),
        ])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_child_ok(self):
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.set_persistent_track_content_for_email_restoration(
            user_entered_email=entered_email,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
                attributes={
                    'account.is_child': '1',
                    'account.last_child_family': TEST_FAMILY_ID,
                    'account.deletion_operation_started_at': time.time() - 60,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(family_id=TEST_FAMILY_ID),
        )
        self.set_track_values(
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            user_entered_email=entered_email,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_USER_ENTERED_LOGIN)

    def test_child_family_full_error(self):
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.set_persistent_track_content_for_email_restoration(
            user_entered_email=entered_email,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
                attributes={
                    'account.is_child': '1',
                    'account.last_child_family': TEST_FAMILY_ID,
                    'account.deletion_operation_started_at': time.time() - 60,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(family_id=TEST_FAMILY_ID, uids=[1, 2, 3, 4]),
        )
        self.set_track_values(
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            user_entered_email=entered_email,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            errors=['family.max_capacity'],
            **self.base_expected_response(user_entered_login=TEST_USER_ENTERED_LOGIN)
        )

    def test_child_family_not_found_error(self):
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.set_persistent_track_content_for_email_restoration(
            user_entered_email=entered_email,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
                attributes={
                    'account.is_child': '1',
                    'account.last_child_family': TEST_FAMILY_ID,
                    'account.deletion_operation_started_at': time.time() - 60,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(family_id=TEST_FAMILY_ID, exists=False),
        )
        self.set_track_values(
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            user_entered_email=entered_email,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            errors=['family.does_not_exist'],
            **self.base_expected_response(user_entered_login=TEST_USER_ENTERED_LOGIN)
        )
