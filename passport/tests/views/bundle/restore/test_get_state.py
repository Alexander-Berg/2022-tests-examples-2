# -*- coding: utf-8 -*-

from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonTestsMixin,
    eq_,
    remove_none_values,
    RestoreBaseTestCase,
)
from passport.backend.api.views.bundle.restore.base import *
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_hosted_domains_response
from passport.backend.core.builders.social_api.faker.social_api import (
    get_profiles_full_response,
    get_profiles_no_profiles,
    profile_item,
)
from passport.backend.core.counters import restore_counter
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.phones.faker import build_phone_bound
from passport.backend.core.support_link_types import (
    SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
    SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
    SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.utils.common import deep_merge


class RestoreGetStateTestCaseBase(RestoreBaseTestCase):
    restore_step = 'get_state'

    default_url = '/1/bundle/restore/get_state/'

    def set_track_values(self, restore_state=RESTORE_STATE_SUBMIT_PASSED, **params):
        params.update(
            restore_state=restore_state,
        )
        super(RestoreGetStateTestCaseBase, self).set_track_values(**params)

    def query_params(self, **kwargs):
        return {}

    def expected_response(self, user_entered_login=TEST_USER_ENTERED_LOGIN, suitable_restore_methods=None,
                          current_restore_method=None, method_state=None, restore_method_passed=False,
                          flushed_entities=None, allowed_methods_to_bind=None, is_method_binding_required=False,
                          show_method_passed_page=True, is_new_phone_confirmed=None, new_phone=None,
                          is_forced_password_changing_pending=False, allow_select_revokers=True):
        response = dict(
            user_entered_login=user_entered_login,
            track_id=self.track_id,
            restore_method_passed=restore_method_passed,
            suitable_restore_methods=suitable_restore_methods,
        )
        if current_restore_method:
            response['current_restore_method'] = current_restore_method
            response['method_state'] = method_state
        if restore_method_passed:
            response['new_auth_state'] = dict(
                flushed_entities=flushed_entities or [],
                revokers={
                    'allow_select': allow_select_revokers,
                    'default': {
                        'app_passwords': True,
                        'tokens': True,
                        'web_sessions': True,
                    },
                },
                allowed_methods_to_bind=allowed_methods_to_bind or [],
                is_method_binding_required=is_method_binding_required,
                show_method_passed_page=show_method_passed_page,
                is_new_phone_confirmed=is_new_phone_confirmed,
                new_phone=new_phone,
                is_forced_password_changing_pending=is_forced_password_changing_pending,
            )
        return response

    def expected_response_after_commit_passed(self, current_restore_method, retpath=None,
                                              next_track_id=None, state=None, has_restorable_email=False,
                                              has_secure_phone_number=False, is_restore_passed_by_support_link=False):
        response = dict(
            track_id=self.track_id,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
            restore_finished=True,
            current_restore_method=current_restore_method,
            next_track_id=next_track_id,
            retpath=retpath,
            state=state,
            has_restorable_email=has_restorable_email,
            has_secure_phone_number=has_secure_phone_number,
            is_restore_passed_by_support_link=is_restore_passed_by_support_link,
        )
        return remove_none_values(response)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    ALLOWED_PIN_CHECK_FAILS_COUNT=3,
    ANSWER_CHECK_ERRORS_CAPTCHA_THRESHOLD=3,
    RESTORE_2FA_FORM_CHECK_ERRORS_CAPTCHA_THRESHOLD=5,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class RestoreGetStateTestCase(RestoreGetStateTestCaseBase, CommonTestsMixin, AccountValidityTestsMixin, EmailTestMixin):
    def setUp(self):
        super(RestoreGetStateTestCase, self).setUp()
        self.env.social_api.set_social_api_response_value(get_profiles_no_profiles())

    def test_global_counter_overflow_finishes_with_state(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.set_track_values()
        counter = restore_counter.get_per_ip_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_IP)
        eq_(counter.get(TEST_IP), counter.limit)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            state='rate_limit_exceeded',
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        eq_(counter.get(TEST_IP), counter.limit)  # счетчик не увеличивается
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_state',
                state='rate_limit_exceeded',
            ),
        ])

    def test_only_semi_auto_form_ok(self):
        """Пользователю доступна только анкета восстановления"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(hintq=None, hinta=None),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=RESTORE_METHOD_SEMI_AUTO_FORM,
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_login_from_suggest_flag_written_to_statbox(self):
        """Использован логин из саджеста - признак записывается в Статбокс"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(hintq=None, hinta=None),
        )
        self.set_track_values(suggested_logins=[TEST_USER_ENTERED_LOGIN])

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=RESTORE_METHOD_SEMI_AUTO_FORM,
                is_suggested_login='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_pdd_with_no_semi_auto_form_ok(self):
        """ПДД пользователю с необслуживаемым саппортами доменом недоступна анкета восстановления"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_PDD_LOGIN_NOT_SERVED,
                uid=TEST_PDD_UID,
                subscribed_to=[102],
                aliases={
                    'pdd': TEST_PDD_LOGIN_NOT_SERVED,
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1'),
        )
        self.set_track_values(
            login=TEST_PDD_LOGIN_NOT_SERVED,
            user_entered_login=TEST_PDD_LOGIN_NOT_SERVED,
            uid=TEST_PDD_UID,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                user_entered_login=TEST_PDD_LOGIN_NOT_SERVED,
                suitable_restore_methods=[RESTORE_METHOD_HINT],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=RESTORE_METHOD_HINT,
                uid=str(TEST_PDD_UID),
                login=TEST_PDD_LOGIN_NOT_SERVED,
            ),
        ])
        self.assert_blackbox_userinfo_called(uid=str(TEST_PDD_UID))

    def test_pdd_with_no_semi_auto_form_and_strong_password_policy_finishes_with_state(self):
        """ПДД пользователю с необслуживаемым саппортами доменом, с требованием сильного пароля,
        восстановление недоступно"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_PDD_LOGIN_NOT_SERVED,
                uid=TEST_PDD_UID,
                subscribed_to=[67, 102],
                alias_type='pdd',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1'),
        )
        self.set_track_values(
            login=TEST_PDD_LOGIN_NOT_SERVED,
            user_entered_login=TEST_PDD_LOGIN_NOT_SERVED,
            uid=TEST_PDD_UID,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            state='domain_not_served',
            **self.base_expected_response(user_entered_login=TEST_PDD_LOGIN_NOT_SERVED)
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_state',
                state='domain_not_served',
                uid=str(TEST_PDD_UID),
                login=TEST_PDD_LOGIN_NOT_SERVED,
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called(uid=str(TEST_PDD_UID))

    def test_2fa_user_ok(self):
        """2ФА пользователь получает особенный способ восстановления, другие способы кроме анкеты использовать нельзя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={'account.2fa_on': '1'},
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=USUAL_2FA_RESTORE_METHODS,
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_with_phonenumber_alias_login_2fa_restore_not_available_ok(self):
        """При использовании цифрового алиаса в качестве логина 2ФА-восстановление недоступно"""
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                self.default_userinfo_response(
                    password='',
                    attributes={'account.2fa_on': '1'},
                    # Это не важно, но для порядка укажем алиас
                    aliases={
                        'portal': TEST_DEFAULT_LOGIN,
                        'phonenumber': TEST_PHONE_OBJECT.digital,
                    },
                    emails=TEST_EMAILS,
                    emails_native=False,
                    phone=TEST_PHONE,
                    is_phone_secure=True,
                ),
                # Второй запрос должен быть сделан с sid=restore
                self.default_userinfo_response(uid=None),
            ],
        )
        self.set_track_values(user_entered_login=TEST_PHONE_LOCAL_FORMAT)

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                user_entered_login=TEST_PHONE_LOCAL_FORMAT,
                suitable_restore_methods=[RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_SEMI_AUTO_FORM]),
                is_phonenumber_alias_used_as_login='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.env.blackbox.requests[1].assert_post_data_contains(
            {
                'method': 'userinfo',
                'login': TEST_PHONE_LOCAL_FORMAT,
                'sid': 'restore',
            },
        )

    def test_email_overrides_hint_ok(self):
        """При наличии подтвержденного email восстановление по КВ/КО недоступно"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(emails=TEST_EMAILS, emails_native=False),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_phone_overrides_hint_ok(self):
        """При наличии защищенного номера восстановление по КВ/КО недоступно"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
                emails=TEST_EMAILS,
                emails_native=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_phone_priority_over_email_ok(self):
        """Телефонный номер является предпочтительным способом восстановления"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
                emails=TEST_EMAILS,
                emails_native=False,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_multiple_suitable_phones_ok(self):
        """У пользователя может быть много телефонов, пригодных для восстановления, если они были привязаны давно"""
        phone_kwargs = dict(
            phone_created=TEST_PHONE_OLD_SCHEME_VALIDATION_DATE,
            phone_bound=TEST_PHONE_OLD_SCHEME_VALIDATION_DATE,
            phone_confirmed=TEST_PHONE_OLD_SCHEME_VALIDATION_DATE,
            is_default=False,
        )
        blackbox_kwargs = deep_merge(
            build_phone_bound(
                TEST_PHONE_ID,
                TEST_PHONE,
                **phone_kwargs
            ),
            build_phone_bound(
                TEST_PHONE_ID2,
                TEST_PHONE2,
                **phone_kwargs
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(**blackbox_kwargs),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_with_phonenumber_alias_login_phone_restore_not_available_ok(self):
        """При использовании цифрового алиаса в качестве логина восстановление по телефону недоступно"""
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                self.default_userinfo_response(
                    aliases={
                        'portal': TEST_DEFAULT_LOGIN,
                        'phonenumber': TEST_PHONE_OBJECT.digital,
                    },
                    emails=TEST_EMAILS,
                    emails_native=False,
                    phone=TEST_PHONE,
                    is_phone_secure=True,
                ),
                # Второй запрос должен быть сделан с sid=restore
                self.default_userinfo_response(uid=None),
            ],
        )
        self.set_track_values(user_entered_login=TEST_PHONE_LOCAL_FORMAT)

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                user_entered_login=TEST_PHONE_LOCAL_FORMAT,
                suitable_restore_methods=[RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                is_hint_masked='1',
                is_phonenumber_alias_used_as_login='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.env.blackbox.requests[1].assert_post_data_contains(
            {
                'method': 'userinfo',
                'login': TEST_PHONE_LOCAL_FORMAT,
                'sid': 'restore',
            },
        )

    def test_with_login_looks_like_but_not_phonenumber_alias_phone_restore_available_ok(self):
        """Логин похож на цифровой алиас, но не является им"""
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                self.default_userinfo_response(
                    aliases={
                        'portal': TEST_DEFAULT_LOGIN,
                        'phonenumber': TEST_PHONE_OBJECT.digital,
                    },
                    emails=TEST_EMAILS,
                    emails_native=False,
                    phone=TEST_PHONE,
                    is_phone_secure=True,
                ),
                # Второй запрос должен быть сделан с sid=restore
                self.default_userinfo_response(),
            ],
        )
        self.set_track_values(user_entered_login=TEST_PHONE_LOCAL_FORMAT)

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                user_entered_login=TEST_PHONE_LOCAL_FORMAT,
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.env.blackbox.requests[1].assert_post_data_contains(
            {
                'method': 'userinfo',
                'login': TEST_PHONE_LOCAL_FORMAT,
                'sid': 'restore',
            },
        )

    def test_with_disabled_on_deletion_account_ok(self):
        """Аккаунт заблокирован при удалении не слишком давно, восстановление возможно"""
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 50
        userinfo = self.default_userinfo_response(
            password_quality=TEST_PASSWORD_QUALITY_OLD,
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
            ],
            attributes={
                'account.deletion_operation_started_at': deletion_started_at,
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
            },
            phone=TEST_PHONE,
            is_phone_secure=True,
            hintq=None,
            hinta=None,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        suitable_methods = [RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]
        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=suitable_methods,
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join(suitable_methods),
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_only_semi_auto_form_for_maillist_ok(self):
        """Для рассылок доступна только анкета"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    str(AT['account.is_maillist']): '1',
                },
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_SEMI_AUTO_FORM]),
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_with_selected_method_no_more_available_fails(self):
        """Выбранный способ восстановления стал недоступен"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_PHONE,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        # в ответе есть необходимые данные для выбора другого способа восстановления
        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def base_phone_restore_case(self, set_track_params, method_state, is_forced_password_changing_pending=False):
        """Общий код тестов состояния восстановления по телефону"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
                password_changing_required=is_forced_password_changing_pending,
            ),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_PHONE,
            **set_track_params
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_PHONE,
                method_state=method_state,
                restore_method_passed=set_track_params['restore_state'] == RESTORE_STATE_METHOD_PASSED,
                is_forced_password_changing_pending=is_forced_password_changing_pending,
                allow_select_revokers=not is_forced_password_changing_pending,
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_method_phone_with_not_suitable_phone_ok(self):
        """Восстановление по телефону, введен телефон, не подходящий для восстановления"""
        self.base_phone_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_SELECTED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=False,
                is_phone_confirmed=False,
            ),
        )

    def test_method_phone_with_suitable_phone_ok(self):
        """Восстановление по телефону, введен телефон, подходящий для восстановления"""
        self.base_phone_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_SELECTED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=False,
            ),
        )

    def test_method_phone_passed_ok(self):
        """Восстановление по телефону, телефон подтвержден"""
        self.base_phone_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_PASSED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_is_confirmed=True,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=True,
            ),
        )

    def test_method_phone_passed_with_forced_password_changing_ok(self):
        """Восстановление по телефону пройдено, на аккаунте требуется смена пароля, не требуем привязки нового
        телефона"""
        self.base_phone_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_PASSED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_is_confirmed=True,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=True,
            ),
            is_forced_password_changing_pending=True,
        )

    def base_2fa_restore_case(self, set_track_params, method_state, method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                              flushed_entities=None, extra_statbox_kwargs=None):
        """Общий код тестов состояния восстановления при 2ФА-восстановлении"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            current_restore_method=method,
            **set_track_params
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=USUAL_2FA_RESTORE_METHODS,
                current_restore_method=method,
                method_state=method_state,
                restore_method_passed=set_track_params['restore_state'] == RESTORE_STATE_METHOD_PASSED,
                flushed_entities=flushed_entities,
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=method,
                **(extra_statbox_kwargs or {})
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_method_phone_and_pin_with_not_suitable_phone_ok(self):
        """Введен телефон, не подходящий для восстановления"""
        self.base_2fa_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_SELECTED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=False,
                is_phone_confirmed=False,
                pin_checks_left=3,
                question=TEST_DEFAULT_HINT_QUESTION_TEXT,
                is_captcha_required=False,
                last_method_step=None,
            ),
        )

    def test_method_phone_and_pin_with_suitable_phone_ok(self):
        """Введен телефон, подходящий для восстановления"""
        self.base_2fa_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_SELECTED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=False,
                pin_checks_left=3,
                question=TEST_DEFAULT_HINT_QUESTION_TEXT,
                is_captcha_required=False,
                last_method_step=None,
            ),
        )

    def test_method_phone_and_pin_with_confirmed_phone_ok(self):
        """Телефон подтвержден"""
        self.base_2fa_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_SELECTED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_is_confirmed=True,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
                last_restore_method_step=RESTORE_STEP_CHECK_PIN,
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=True,
                pin_checks_left=3,
                question=TEST_DEFAULT_HINT_QUESTION_TEXT,
                is_captcha_required=False,
                last_method_step=RESTORE_STEP_CHECK_PIN,
            ),
        )

    def test_method_phone_and_pin_passed_ok(self):
        """Введен правильный пин"""
        self.base_2fa_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_PASSED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_is_confirmed=True,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
                is_pin_checked=True,
                last_restore_method_step=RESTORE_STEP_CHECK_PIN,
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=True,
                question=TEST_DEFAULT_HINT_QUESTION_TEXT,
                is_captcha_required=False,
                pin_checks_left=3,
                last_method_step=RESTORE_STEP_CHECK_PIN,
            ),
            flushed_entities=[u'2fa'],
        )

    def test_method_phone_and_2fa_form_captcha_required_ok(self):
        """Проверка 2ФА-формы не пройдена, требуется ввод капчи"""
        self.base_2fa_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_SELECTED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_is_confirmed=True,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
                restore_2fa_form_checks_count=5,
                last_restore_method_step=RESTORE_STEP_CHECK_2FA_FORM,
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=True,
                question=TEST_DEFAULT_HINT_QUESTION_TEXT,
                is_captcha_required=True,
                pin_checks_left=3,
                last_method_step=RESTORE_STEP_CHECK_2FA_FORM,
            ),
            flushed_entities=[u'2fa'],
            extra_statbox_kwargs={
                '2fa_form_checks_count': '5',
            },
        )

    def test_method_phone_and_2fa_form_passed_ok(self):
        """Проверка 2ФА-формы пройдена"""
        self.base_2fa_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_PASSED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_is_confirmed=True,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
                last_restore_method_step=RESTORE_STEP_CHECK_2FA_FORM,
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=True,
                question=TEST_DEFAULT_HINT_QUESTION_TEXT,
                is_captcha_required=False,
                last_method_step=RESTORE_STEP_CHECK_2FA_FORM,
                pin_checks_left=3,
            ),
            flushed_entities=[u'2fa'],
        )

    def base_hint_restore_case(self, restore_state=RESTORE_STATE_METHOD_SELECTED,
                               answer_checks_count=None, is_captcha_required=False,
                               support_link_type=None, restoration_key_created_at=None,
                               flushed_entities=None, show_method_passed_page=True,
                               is_forced_password_changing_pending=False,
                               is_method_binding_required=False):
        """Общий код тестов состояния восстановления по КО"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                password_changing_required=is_forced_password_changing_pending,
            ),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            restore_state=restore_state,
            answer_checks_count=answer_checks_count,
            support_link_type=support_link_type,
            restoration_key_created_at=restoration_key_created_at,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_HINT,
                method_state=dict(
                    question=TEST_DEFAULT_HINT_QUESTION_TEXT,
                    is_captcha_required=is_captcha_required,
                ),
                restore_method_passed=restore_state == RESTORE_STATE_METHOD_PASSED,
                flushed_entities=flushed_entities,
                show_method_passed_page=show_method_passed_page,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
                is_new_phone_confirmed=False,
                is_forced_password_changing_pending=is_forced_password_changing_pending,
                allow_select_revokers=not is_forced_password_changing_pending,
                is_method_binding_required=is_method_binding_required,
            )
        )
        self.assert_track_unchanged()
        entry = self.env.statbox.entry(
            'passed',
            suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
            current_restore_method=RESTORE_METHOD_HINT,
        )
        if answer_checks_count:
            entry['answer_checks_count'] = str(answer_checks_count)
        if support_link_type:
            entry['support_link_type'] = support_link_type
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_method_hint_selected_ok(self):
        """Выбрано восстановление по КВ/КО"""
        self.base_hint_restore_case(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
        )

    def test_method_hint_selected_with_captcha_required_ok(self):
        """Выбрано восстановление по КВ/КО, требуется капча"""
        self.base_hint_restore_case(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            answer_checks_count=3,
            is_captcha_required=True,
        )

    def test_method_hint_passed_ok(self):
        """Выбрано восстановление по КВ/КО, введен правильный КО"""
        self.base_hint_restore_case(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            answer_checks_count=1,
        )

    def test_method_hint_not_passed_with_forced_password_changing_pending_ok(self):
        """Выбрано восстановление по КВ/КО, не пройдено так как есть флаг принудительной смены пароля,
        требуем привязки телефона"""

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                password_changing_required=True,
            ),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            restore_state=RESTORE_STATE_METHOD_PASSED,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_HINT,
                is_hint_masked='1',
            ),
        ])

    def base_email_restore_case(self, method_state, restore_state=RESTORE_STATE_METHOD_SELECTED,
                                with_phone=False, is_new_phone_confirmed=False, new_phone=None,
                                allowed_methods_to_bind=None, is_forced_password_changing_pending=False,
                                is_method_binding_required=False, **track_kwargs):
        """Общий код тестов состояния восстановления по email-адресу"""
        userinfo_kwargs = dict(
            emails=[
                self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
            ],
            password_changing_required=is_forced_password_changing_pending,
        )
        if with_phone:
            userinfo_kwargs.update(
                phone=TEST_PHONE,
                is_phone_secure=True,
            )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(**userinfo_kwargs),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_EMAIL,
            restore_state=restore_state,
            **track_kwargs
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        suitable_methods = [RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]
        if with_phone:
            suitable_methods.insert(0, RESTORE_METHOD_PHONE)
        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=suitable_methods,
                current_restore_method=RESTORE_METHOD_EMAIL,
                method_state=method_state,
                restore_method_passed=restore_state == RESTORE_STATE_METHOD_PASSED,
                allowed_methods_to_bind=allowed_methods_to_bind or [],
                is_new_phone_confirmed=is_new_phone_confirmed,
                new_phone=new_phone,
                is_forced_password_changing_pending=is_forced_password_changing_pending,
                allow_select_revokers=not is_forced_password_changing_pending,
                is_method_binding_required=is_method_binding_required,
            )
        )
        self.assert_track_unchanged()
        entry = self.env.statbox.entry(
            'passed',
            suitable_restore_methods=','.join(suitable_methods),
            current_restore_method=RESTORE_METHOD_EMAIL,
            is_hint_masked='1',
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_method_email_selected_ok(self):
        """Выбрано восстановление по email-адресу"""
        self.base_email_restore_case(
            method_state={
                'email_entered': None,
                'is_email_suitable_for_restore': False,
            },
            restore_state=RESTORE_STATE_METHOD_SELECTED,
        )

    def test_method_email_with_not_suitable_email_ok(self):
        """Восстановление по email-адресу, введен email-адрес не подходящий для восстановления"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.base_email_restore_case(
            method_state={
                'email_entered': entered_email,
                'is_email_suitable_for_restore': False,
            },
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            user_entered_email=entered_email,
            is_email_check_passed=False,
        )

    def test_method_email_with_suitable_email_ok(self):
        """Восстановление по email-адресу, введен email-адрес, подходящий для восстановления"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.base_email_restore_case(
            method_state={
                'email_entered': entered_email,
                'is_email_suitable_for_restore': True,
            },
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            user_entered_email=entered_email,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            is_email_check_passed=True,
        )

    def test_method_email_passed_ok(self):
        """Восстановление по email-адресу пройдено"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.base_email_restore_case(
            method_state={
                'email_entered': entered_email,
                'is_email_suitable_for_restore': True,
            },
            restore_state=RESTORE_STATE_METHOD_PASSED,
            user_entered_email=entered_email,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            is_email_check_passed=True,
            allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
        )

    def test_method_email_passed_with_new_phone_passed_but_unconfirmed_ok(self):
        """Восстановление по email-адресу пройдено, пользователь ввёл, но не подтвердил новый номер телефона"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.base_email_restore_case(
            method_state={
                'email_entered': entered_email,
                'is_email_suitable_for_restore': True,
            },
            allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
            is_new_phone_confirmed=False,
            new_phone=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            user_entered_email=entered_email,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            is_email_check_passed=True,
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            country='RU',
            phone_confirmation_phone_number=TEST_PHONE,
        )

    def test_method_email_passed_with_new_phone_confirmed_ok(self):
        """Восстановление по email-адресу пройдено, пользователь подтвердил новый номер телефона"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.base_email_restore_case(
            method_state={
                'email_entered': entered_email,
                'is_email_suitable_for_restore': True,
            },
            allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
            is_new_phone_confirmed=True,
            new_phone=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            user_entered_email=entered_email,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            is_email_check_passed=True,
            phone_confirmation_is_confirmed=True,
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            country='RU',
            phone_confirmation_phone_number=TEST_PHONE,
        )

    def test_method_email_passed_with_phone_available_ok(self):
        """Восстановление по email-адресу пройдено, защищенный телефон не предлагаем привязать т.к. он уже есть"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.base_email_restore_case(
            with_phone=True,
            method_state={
                'email_entered': entered_email,
                'is_email_suitable_for_restore': True,
            },
            restore_state=RESTORE_STATE_METHOD_PASSED,
            user_entered_email=entered_email,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            is_email_check_passed=True,
            is_new_phone_confirmed=None,
        )

    def test_method_email_with_phone_available_with_forced_password_changing_failed(self):
        """Восстановление по email-адресу не пройдено, защищенный телефон требуем перепривязать т.к.
        выставлен флаг принудительной смены пароля"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
                password_changing_required=True,
                phone=TEST_PHONE,
                is_phone_secure=True,
            )
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_EMAIL,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            user_entered_email=entered_email,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            is_email_check_passed=True,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                is_hint_masked='1',
            ),
        ])

    def test_method_email_with_forced_password_changing_with_phone_restore_attempt_fail(self):
        """Восстановление по email-адресу не пройдено, защищенный телефон требуем перепривязать т.к.
        выставлен флаг принудительной смены пароля, в процессе восстановления пользователь
        пытался восстановиться по телефону, но не смог угадать код - и это не отразилось на ответе ручки"""
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
                password_changing_required=True,
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_EMAIL,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            user_entered_email=entered_email,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            is_email_check_passed=True,
            # поля, выставленные ручкой проверки защищенного номера
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                is_hint_masked='1',
            ),
        ])

    def test_support_link_force_hint_restoration_ok(self):
        """Состояние после перехода по саппортской ссылке, предписывающей восстановление по КВ/КО"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
            ),
        )
        self.set_track_values(
            restore_state=RESTORE_STATE_SUBMIT_PASSED,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
                restore_method_passed=False,
            )
        )
        self.assert_track_unchanged()
        entry = self.env.statbox.entry(
            'passed',
            suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_support_link_force_hint_restoration_with_ip_counter_overflow_ok(self):
        """Состояние после перехода по саппортской ссылке, предписывающей восстановление по КВ/КО;
        счетчик по IP переполнен, но при проверке используется специальный лимит"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
            ),
        )
        self.set_track_values(
            restore_state=RESTORE_STATE_SUBMIT_PASSED,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )

        counter = restore_counter.get_per_ip_buckets()
        for _ in range(counter.limit + 5):
            counter.incr(TEST_IP)

        with settings_context(
            BLACKBOX_URL='localhost',
            RESTORE_PER_IP_COUNTER_LIMIT_FOR_SUPPORT_LINK=20,
            **mock_counters()
        ):
            resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM],
                restore_method_passed=False,
            )
        )
        self.assert_track_unchanged()
        entry = self.env.statbox.entry(
            'passed',
            suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_forced_method_hint_selected_ok(self):
        """Восстановление по КВ по ссылке от саппорта. Выбрано восстановление по КВ/КО"""
        self.base_hint_restore_case(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )

    def test_forced_method_hint_selected_with_captcha_required_ok(self):
        """Восстановление по КВ по ссылке от саппорта. Выбрано восстановление по КВ/КО, требуется капча"""
        self.base_hint_restore_case(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            answer_checks_count=3,
            is_captcha_required=True,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )

    def test_forced_method_hint_passed_ok(self):
        """Восстановление по КВ по ссылке от саппорта. Выбрано восстановление по КВ/КО, введен правильный КО"""
        self.base_hint_restore_case(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            answer_checks_count=1,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            show_method_passed_page=False,
        )

    def test_support_link_force_phone_restoration_2fa_ok(self):
        """Состояние после перехода по саппортской ссылке, предписывающей восстановление по телефону для 2ФА"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            restore_state=RESTORE_STATE_SUBMIT_PASSED,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
                restore_method_passed=False,
            )
        )
        self.assert_track_unchanged()
        entry = self.env.statbox.entry(
            'passed',
            suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
            support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def base_forced_phone_restore_case(self, set_track_params, method_state, flushed_entities=None,
                                       show_method_passed_page=True):
        """Общий код тестов состояния восстановления по телефону по ссылке от саппортов для 2ФА пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_PHONE,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            **set_track_params
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_PHONE,
                method_state=method_state,
                restore_method_passed=set_track_params['restore_state'] == RESTORE_STATE_METHOD_PASSED,
                flushed_entities=flushed_entities,
                show_method_passed_page=show_method_passed_page,
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
            ),
        ])

    def test_forced_method_phone_with_not_suitable_phone_ok(self):
        """Восстановление по телефону по ссылке от саппортов для 2ФА, введен телефон, не подходящий для восстановления"""
        self.base_forced_phone_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_SELECTED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=False,
                is_phone_confirmed=False,
            ),
        )

    def test_forced_method_phone_with_suitable_phone_ok(self):
        """Восстановление по телефону по ссылке от саппортов для 2ФА, введен телефон, подходящий для восстановления"""
        self.base_forced_phone_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_SELECTED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=False,
            ),
        )

    def test_forced_method_phone_passed_ok(self):
        """Восстановление по телефону по ссылке от саппортов для 2ФА, телефон подтвержден"""
        self.base_forced_phone_restore_case(
            dict(
                restore_state=RESTORE_STATE_METHOD_PASSED,
                user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                phone_confirmation_is_confirmed=True,
                phone_confirmation_code=str(TEST_VALIDATION_CODE),
            ),
            dict(
                phone_entered=TEST_PHONE_LOCAL_FORMAT,
                is_phone_suitable_for_restore=True,
                is_phone_confirmed=True,
            ),
            flushed_entities=[u'2fa'],
            show_method_passed_page=False,
        )

    def test_support_link_change_password_new_method_required_all_entities_flushed_ok(self):
        """Состояние после перехода по саппортской ссылке для ввода нового пароля и средства восстановления;
        на аккаунте много средств восстановления и соц. профили, сообщаем о сбросе"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                enabled=False,  # При генерации ссылки такого типа пользователь блокируется
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                ],
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.env.social_api.set_social_api_response_value(get_profiles_full_response())
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_LINK,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                method_state={},
                restore_method_passed=True,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_method_binding_required=True,
                show_method_passed_page=False,
                is_new_phone_confirmed=False,
                allow_select_revokers=False,
            )
        )
        self.assert_track_unchanged()
        entry = self.env.statbox.entry(
            'passed',
            suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_support_link_change_password_new_method_required_no_entities_flushed_ok(self):
        """Состояние после перехода по саппортской ссылке для ввода нового пароля и средства восстановления;
        на аккаунте нет сущностей, которые требуется сбросить, отменять глогаут нельзя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                enabled=False,  # При генерации ссылки такого типа пользователь блокируется
                emails=[
                    self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
                ],
                hintq=False,
                hinta=False,
                phone=TEST_PHONE,
                is_phone_secure=False,
                subscribed_to=[67],
            ),
        )
        self.env.social_api.set_social_api_response_value(
            {
                'profiles': [profile_item(allow_auth=False)],
            },
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_LINK,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                method_state={},
                restore_method_passed=True,
                flushed_entities=[],
                allow_select_revokers=False,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_method_binding_required=True,
                show_method_passed_page=False,
                is_new_phone_confirmed=False,
            )
        )
        self.assert_track_unchanged()
        entry = self.env.statbox.entry(
            'passed',
            suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_support_link_missing_password_ok(self):
        """У пользователя, имеющего портальный алиас, не установлен пароль, саппорт выписал ссылку"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                password='',
                login=TEST_DEFAULT_LOGIN,
                enabled=False,
            ),
        )
        self.env.social_api.set_social_api_response_value(get_profiles_no_profiles())
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_LINK,
            restore_state=RESTORE_STATE_METHOD_PASSED,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM],
                current_restore_method=RESTORE_METHOD_LINK,
                method_state={},
                restore_method_passed=True,
                flushed_entities=[],
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE, RESTORE_METHOD_HINT],
                is_method_binding_required=True,
                show_method_passed_page=False,
                is_new_phone_confirmed=False,
                allow_select_revokers=False,
            )
        )
        self.assert_track_unchanged()
        self.assert_track_unchanged()
        entry = self.env.statbox.entry(
            'passed',
            is_password_missing='1',
            suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=0,
    ALLOWED_PIN_CHECK_FAILS_COUNT=3,
    ANSWER_CHECK_ERRORS_CAPTCHA_THRESHOLD=3,
    RESTORE_2FA_FORM_CHECK_ERRORS_CAPTCHA_THRESHOLD=5,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class RestoreGetStateNoSemiAutoFormTestCase(RestoreGetStateTestCaseBase, CommonTestsMixin, AccountValidityTestsMixin, EmailTestMixin):
    def setUp(self):
        super(RestoreGetStateNoSemiAutoFormTestCase, self).setUp()
        self.env.social_api.set_social_api_response_value(get_profiles_no_profiles())

    def test_only_semi_auto_form_ok(self):
        """Пользователю доступна только анкета восстановления, показываем вне зависимости от вхождения в долю на обучение"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(hintq=None, hinta=None),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=RESTORE_METHOD_SEMI_AUTO_FORM,
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_only_semi_auto_form_for_maillist_ok(self):
        """Для рассылок доступна только анкета, показываем вне зависимости от вхождения в долю на обучение"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    str(AT['account.is_maillist']): '1',
                },
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_SEMI_AUTO_FORM]),
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_2fa_user_no_semi_auto_form_ok(self):
        """Пользователь не входит в долю на обучение, анкета недоступна"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                password='',
                attributes={'account.2fa_on': '1'},
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                suitable_restore_methods=[RESTORE_METHOD_PHONE_AND_2FA_FACTOR],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE_AND_2FA_FACTOR]),
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_semi_auto_form_passed_and_available_ok(self):
        """Пользователь не входит в долю на обучение, однако анкета пройдена по прямой ссылке, поэтому доступна"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response(
                current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
                restore_method_passed=True,
                method_state={},
                is_new_phone_confirmed=False,
                allowed_methods_to_bind=[RESTORE_METHOD_PHONE],
                is_method_binding_required=True,
                suitable_restore_methods=[RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM],
            )
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_commit_passed_no_redirect_required(self):
        """Восстановление пройдено, не требуется перенаправление"""
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            restore_state=RESTORE_STATE_COMMIT_PASSED,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response_after_commit_passed(
                current_restore_method=RESTORE_METHOD_HINT,
            )
        )
        self.assert_track_unchanged()

    def test_commit_passed_with_retpath_and_redirect_required(self):
        """Восстановление пройдено, требуется перенаправление, задан retpath"""
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            restore_state=RESTORE_STATE_COMMIT_PASSED,
            retpath=TEST_RETPATH,
            state='show_2fa_promo',
            next_track_id=TEST_TRACK_ID,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response_after_commit_passed(
                current_restore_method=RESTORE_METHOD_HINT,
                retpath=TEST_RETPATH,
                state='show_2fa_promo',
                next_track_id=TEST_TRACK_ID,
            )
        )
        self.assert_track_unchanged()

    def test_commit_passed_with_support_link_and_secure_phone(self):
        """Восстановление пройдено по саппортской ссылке, есть пригодный для восстановления телефон"""
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            restore_state=RESTORE_STATE_COMMIT_PASSED,
            has_secure_phone_number=True,
            support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response_after_commit_passed(
                current_restore_method=RESTORE_METHOD_HINT,
                has_secure_phone_number=True,
                is_restore_passed_by_support_link=True,
            )
        )
        self.assert_track_unchanged()

    def test_commit_passed_with_restorable_email(self):
        """Восстановление пройдено, есть пригодный для восстановления email"""
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            restore_state=RESTORE_STATE_COMMIT_PASSED,
            has_restorable_email=True,
        )

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.expected_response_after_commit_passed(
                current_restore_method=RESTORE_METHOD_HINT,
                has_restorable_email=True,
            )
        )
        self.assert_track_unchanged()
