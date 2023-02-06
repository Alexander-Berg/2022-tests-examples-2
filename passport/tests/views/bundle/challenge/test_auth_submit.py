# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from nose_parameterized import parameterized
from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    TEST_DIFFERENT_PHONE_NUMBER,
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_HINT_QUESTION_TEXT
from passport.backend.core.test.test_utils.utils import settings_context

from .base import (
    BaseAuthTestCase,
    CommonAuthChallengeTests,
)


class SubmitTestcase(BaseAuthTestCase, CommonAuthChallengeTests):
    default_url = '/1/bundle/auth/password/challenge/submit/'

    @staticmethod
    def _secured_phone_date(days=10):
        return datetime.now() - timedelta(days=days)

    def expected_response(
        self, has_phone=True, phone_confirmation_challenge=False,
        default_challenge='phone', masked_challenge_email='g***.com',
        has_question=False, has_push_2fa=False, has_email_code=False, phone_id=1,
    ):
        response = {
            'track_id': self.track_id,
            'challenges_enabled': {},
            'default_challenge': default_challenge,
        }
        if has_phone and phone_confirmation_challenge:
            response['challenges_enabled']['phone_confirmation'] = {
                'hint': '+7 926 ***-**-67',
                'phone_id': phone_id,
                'phone_number': TEST_PHONE_NUMBER.e164,
            }
        else:
            if masked_challenge_email:
                response['challenges_enabled']['email'] = {
                    'hint': 't***r@' + masked_challenge_email,
                }
            if has_phone:
                response['challenges_enabled']['phone'] = {
                    'hint': '+7 926 ***-**-67',
                }

        if has_question:
            response['challenges_enabled']['question'] = {
                'hint': TEST_HINT_QUESTION_TEXT,
            }

        if has_push_2fa:
            response['challenges_enabled']['push_2fa'] = {
                'hint': None,
            }

        if has_email_code:
            response['challenges_enabled']['email_code'] = {
                'hint': [
                    u't***r@G***.com',
                    u't***r@g***.com',
                    u't***r@m***.ru',
                    u't***r@x***.com',
                ],
            }

        return response

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response()
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='phone',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.phone.rps_dmmm')

    def test_ok_device_info_in_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.account_manager_version = '1.2.3'
            track.device_application = 'ru.yandex.app_id'
            track.device_id = 'device-id'

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response()
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='phone',
                am_version='1.2.3',
                am_version_name='1.2.3',
                app_id='ru.yandex.app_id',
                device_id='device-id',
                is_mobile='1',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.mobile.phone.rps_dmmm')

    def test_is_easily_hacked_ok(self):
        self.setup_blackbox_response(
            is_easily_hacked=True,
            bank_phonenumber_alias=TEST_DIFFERENT_PHONE_NUMBER.digital,
            simple_phone=TEST_DIFFERENT_PHONE_NUMBER,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(phone_confirmation_challenge=True, default_challenge='phone_confirmation')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                challenges='phone_confirmation',
                default_challenge='phone_confirmation',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.phone_confirmation.rps_dmmm')

    def test_login_by_phonenumber_alias_ok(self):
        # При логине по ЛЦА будет доступен только челлендж phone_confirmation
        self.setup_blackbox_response(secured_phone_confirmed=self._secured_phone_date(days=10))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.user_entered_login = TEST_PHONE_NUMBER.national

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(phone_confirmation_challenge=True, default_challenge='phone_confirmation')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                challenges='phone_confirmation',
                default_challenge='phone_confirmation',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.phone_confirmation.rps_dmmm')

    def test_login_without_secure_phone_ok(self):
        # При логине без телефона метод is_enable челенджа phone_confirmation отрабатывает верно.
        self.setup_blackbox_response(has_phones=False)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(has_phone=False, default_challenge='email')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                challenges='email',
                default_challenge='email',
                is_mobile='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.email.rps_dmmm')

    def test_login_without_secure_phone_but_with_bank_phone_ok(self):
        # При логине без защищенного телефона, но с банковским метод is_enable челенджа phone_confirmation
        # работает верно.
        self.setup_blackbox_response(
            has_phones=False,
            bank_phonenumber_alias=TEST_PHONE_NUMBER.digital,
            simple_phone=TEST_PHONE_NUMBER,
        )

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(
                phone_confirmation_challenge=True,
                phone_id=3,
                default_challenge='phone_confirmation',
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                challenges='phone_confirmation',
                default_challenge='phone_confirmation',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )

    def test_sms_2fa_ok(self):
        self.setup_blackbox_response(has_sms_2fa=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(phone_confirmation_challenge=True, default_challenge='phone_confirmation')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                challenges='phone_confirmation',
                default_challenge='phone_confirmation',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.phone_confirmation.rps_dmmm')

    def test_sms_2fa_after_auth_by_sms_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.auth_method = 'sms_code'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_sms'

        self.setup_blackbox_response(has_sms_2fa=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(
                # Телефон уже подтверждался, поэтому ни к чему просить его
                # подтвердить заново или ввести замаскированный номер.
                default_challenge='email',
                has_phone=False,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='email',
                challenges='email',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.email.rps_dmmm')

    def test_is_am_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.x_token_client_id = '123456'
            track.device_application = 'ru.yandex.test'

        self.setup_blackbox_response(secured_phone_confirmed=self._secured_phone_date(days=89))
        with settings_context(
            PHONE_CONFIRMATION_CHALLENGE_FOR_ALL_APPS=False,            # проверяется совпадение app_id
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM=True,           # челлендж для АМ - вкл
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM_DENOMINATOR=1,  # 100 %
            PHONE_CONFIRMATION_CHALLENGE_APP_IDS={'ru.yandex.test'},
            PHONE_CONFIRMATION_CHALLENGE_ACTUALITY_THRESHOLD_DAYS=90,
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(phone_confirmation_challenge=True, default_challenge='phone_confirmation')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                app_id='ru.yandex.test',
                default_challenge='phone_confirmation',
                challenges='phone_confirmation',
                is_mobile='1',
                phone_confirmation_enabled_for_app_id='1',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.mobile.phone_confirmation.rps_dmmm')

    def test_am_expired_secure_phone_confirmation(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.x_token_client_id = '123456'
            track.device_application = 'ru.yandex.test'

        self.setup_blackbox_response(secured_phone_confirmed=self._secured_phone_date(days=91))
        with settings_context(
            PHONE_CONFIRMATION_CHALLENGE_FOR_ALL_APPS=False,            # проверяется совпадение app_id
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM=True,           # челлендж для АМ - вкл
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM_DENOMINATOR=1,  # 100 %
            PHONE_CONFIRMATION_CHALLENGE_APP_IDS={'ru.yandex.test'},
            PHONE_CONFIRMATION_CHALLENGE_ACTUALITY_THRESHOLD_DAYS=90,
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response()
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                app_id='ru.yandex.test',
                default_challenge='phone',
                challenges='phone,email',
                is_mobile='1',
                phone_confirmation_enabled_for_app_id='1',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.mobile.phone.rps_dmmm')

    def test_uid_not_in_experiment(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.x_token_client_id = '123456'
            track.device_application = 'ru.yandex.test'

        self.setup_blackbox_response()
        with settings_context(
            PHONE_CONFIRMATION_CHALLENGE_FOR_ALL_APPS=False,            # проверяется совпадение app_id
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM=True,           # челлендж для АМ - вкл
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM_DENOMINATOR=0,  # 0 %
            PHONE_CONFIRMATION_CHALLENGE_APP_IDS={'ru.yandex.test'},
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(phone_confirmation_challenge=False, default_challenge='phone')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                app_id='ru.yandex.test',
                default_challenge='phone',
                challenges='phone,email',
                is_mobile='1',
                phone_confirmation_enabled_for_app_id='1',
                uid_in_experiment='0',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.mobile.phone.rps_dmmm')

    def test_antidraud_need_phone_confirmation_challenge(self):
        # не должны показывать телефонный челлендж, но показали потому что велел антифрод
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.x_token_client_id = '123456'
            track.device_application = 'ru.yandex.test'
            track.antifraud_tags = ['sms']

        self.setup_blackbox_response()
        with settings_context(
            PHONE_CONFIRMATION_CHALLENGE_FOR_ALL_APPS=False,            # проверяется совпадение app_id
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM=True,           # челлендж для АМ - вкл
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM_DENOMINATOR=0,  # 0 %
            PHONE_CONFIRMATION_CHALLENGE_APP_IDS={'ru.yandex.test'},
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(phone_confirmation_challenge=True, default_challenge='phone_confirmation')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                app_id='ru.yandex.test',
                default_challenge='phone_confirmation',
                challenges='phone_confirmation',
                is_mobile='1',
                phone_confirmation_enabled_for_app_id='1',
                uid_in_experiment='0',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.mobile.phone_confirmation.rps_dmmm')

    def test_is_am_different_app_id(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.x_token_client_id = '123456'
            track.device_application = 'different.app.id'

        self.setup_blackbox_response()
        with settings_context(
            PHONE_CONFIRMATION_CHALLENGE_FOR_ALL_APPS=False,            # проверяется совпадение app_id
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM=True,           # челлендж для АМ - вкл
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM_DENOMINATOR=1,  # 100 %
            PHONE_CONFIRMATION_CHALLENGE_APP_IDS={'ru.yandex.test'},
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(phone_confirmation_challenge=False, default_challenge='phone')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                app_id='different.app.id',
                default_challenge='phone',
                challenges='phone,email',
                is_mobile='1',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.mobile.phone.rps_dmmm')

    def test_app_id_is_ignored(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.x_token_client_id = '123456'
            track.device_application = 'different.app.id'

        self.setup_blackbox_response(secured_phone_confirmed=self._secured_phone_date())
        with settings_context(
            PHONE_CONFIRMATION_CHALLENGE_FOR_ALL_APPS=True,             # НЕ проверяется совпадение app_id
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM=True,           # челлендж для АМ - вкл
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM_DENOMINATOR=1,  # 100 %
            PHONE_CONFIRMATION_CHALLENGE_APP_IDS={'ru.yandex.test'},
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(phone_confirmation_challenge=True, default_challenge='phone_confirmation')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                app_id='different.app.id',
                default_challenge='phone_confirmation',
                challenges='phone_confirmation',
                is_mobile='1',
                phone_confirmation_enabled_for_app_id='1',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.mobile.phone_confirmation.rps_dmmm')

    def test_client_unable_to_send_sms(self):
        self.setup_blackbox_response(is_easily_hacked=True)
        resp = self.make_request(query_args=dict(can_send_sms=False))
        self.assert_ok_response(
            resp,
            **self.expected_response(phone_confirmation_challenge=False, default_challenge='phone')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                challenges='phone,email',
                default_challenge='phone',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.phone.rps_dmmm')

    def test_punycode_ok(self):
        self.setup_blackbox_response(challenge_email=u'домен.рф')
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(masked_challenge_email=u'д***.рф')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='phone',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.phone.rps_dmmm')

    def test_only_phone_ok(self):
        self.setup_blackbox_response(has_emails=False)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(masked_challenge_email=None)
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='phone',
                challenges='phone',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.phone.rps_dmmm')

    def test_only_email_ok(self):
        self.setup_blackbox_response(has_phones=False)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(has_phone=False, default_challenge='email')
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                is_mobile='0',
                default_challenge='email',
                challenges='email',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.email.rps_dmmm')

    def test_lite_email_not_used(self):
        self.setup_blackbox_response(
            alias_type='lite',
            alias='%s@mail.ru' % TEST_LOGIN,
            challenge_email='mail.ru',
            challenge_email_only=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(masked_challenge_email=None)
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='phone',
                challenges='phone',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.phone.rps_dmmm')

    @parameterized.expand([
        (['sms'], 'phone_confirmation'),
        (['sms', 'flash_call', 'call'], 'phone_confirmation'),
        (['flash_call'], 'phone_confirmation'),
        (['phone_hint'], 'phone'),
        (['email_hint'], 'email'),
        (['question'], 'question'),
    ])
    def test_antifraud_tags_ok(self, tags, challenge):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.x_token_client_id = '123456'
            track.device_application = 'ru.yandex.test'
            track.antifraud_tags = tags

        self.setup_blackbox_response(
            secured_phone_confirmed=self._secured_phone_date(days=89),
        )
        with settings_context(
            PHONE_CONFIRMATION_CHALLENGE_FOR_ALL_APPS=False,            # проверяется совпадение app_id
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM=True,           # челлендж для АМ - вкл
            PHONE_CONFIRMATION_CHALLENGE_ENABLED_FOR_AM_DENOMINATOR=1,  # 100 %
            PHONE_CONFIRMATION_CHALLENGE_APP_IDS={'ru.yandex.test'},
            PHONE_CONFIRMATION_CHALLENGE_ACTUALITY_THRESHOLD_DAYS=90,
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(
                phone_confirmation_challenge=challenge == 'phone_confirmation',
                default_challenge=challenge,
                masked_challenge_email='g***.com' if challenge == 'email' else None,
                has_phone=challenge.startswith('phone'),
                has_question=challenge == 'question',
            )
        )

        entry_kwargs_if_phone = dict(
            phone_confirmation_enabled_for_app_id='1',
            uid_in_experiment='1',
            client_can_send_sms='1',
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                app_id='ru.yandex.test',
                default_challenge=challenge,
                challenges=challenge,
                is_mobile='1',
                **(entry_kwargs_if_phone if challenge == 'phone_confirmation' else {})
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.mobile.{}.rps_dmmm'.format(challenge))

    def test_question_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.x_token_client_id = '123456'
            track.device_application = 'ru.yandex.test'
            track.antifraud_tags = ['question', 'email_hint']
        self.setup_blackbox_response()

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(
                default_challenge='question',
                has_question=True,
                has_phone=False,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                app_id='ru.yandex.test',
                default_challenge='question',
                challenges='question,email',
                is_mobile='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.mobile.question.rps_dmmm')

    def test_push_2fa_ok(self):
        self.setup_blackbox_response(has_trusted_xtokens=True)
        self.setup_push_api_list_response(with_trusted_subscription=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['push_2fa', 'question', 'email_hint']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.expected_response(
                default_challenge='push_2fa',
                has_question=True,
                has_push_2fa=True,
                has_phone=False,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='push_2fa',
                challenges='push_2fa,question,email',
                is_mobile='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.push_2fa.rps_dmmm')

    def test_push_2fa_ok__with_sms_2fa(self):
        self.setup_blackbox_response(has_trusted_xtokens=True, has_sms_2fa=True)
        self.setup_push_api_list_response(with_trusted_subscription=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = []

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.expected_response(
                default_challenge='push_2fa',
                has_question=False,
                has_push_2fa=True,
                phone_confirmation_challenge=True,
                has_phone=True,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='push_2fa',
                challenges='push_2fa,phone_confirmation',
                is_mobile='0',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.push_2fa.rps_dmmm')

    def test_push_2fa_no_trusted_xtokens(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['push_2fa', 'question', 'email_hint']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.expected_response(
                default_challenge='question',
                has_question=True,
                has_phone=False,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='question',
                challenges='question,email',
                is_mobile='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.question.rps_dmmm')
        self.assertFalse(self.env.push_api.requests)

    def test_push_2fa_no_trusted_subscriptions(self):
        self.setup_blackbox_response(has_trusted_xtokens=True)
        self.setup_push_api_list_response(with_trusted_subscription=False)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['push_2fa', 'question', 'email_hint']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.expected_response(
                default_challenge='question',
                has_question=True,
                has_phone=False,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='question',
                challenges='question,email',
                is_mobile='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.question.rps_dmmm')

    def test_push_2fa_disabled_by_antifraud__but_no_sms2fa(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['question', 'email_hint']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.expected_response(
                default_challenge='question',
                has_question=True,
                has_phone=False,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='question',
                challenges='question,email',
                is_mobile='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.question.rps_dmmm')
        self.assertFalse(self.env.push_api.requests)

    def test_push_2fa_disabled_by_config(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['push_2fa', 'question', 'email_hint']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=False,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.expected_response(
                default_challenge='question',
                has_question=True,
                has_phone=False,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='question',
                challenges='question,email',
                is_mobile='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.question.rps_dmmm')
        self.assertFalse(self.env.push_api.requests)

    def test_push_2fa_disabled_by_experiment(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['push_2fa', 'question', 'email_hint']

        with settings_context(
            PUSH_2FA_CHALLENGE_ENABLED=True,
            PUSH_2FA_CHALLENGE_ENABLED_DENOMINATOR=0.1,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.expected_response(
                default_challenge='question',
                has_question=True,
                has_phone=False,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='question',
                challenges='question,email',
                is_mobile='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.question.rps_dmmm')
        self.assertFalse(self.env.push_api.requests)

    def test_email_code_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code', 'question', 'email_hint']

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.expected_response(
                default_challenge='email_code',
                has_question=True,
                has_email_code=True,
                has_phone=False,
            )
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='email_code',
                challenges='email_code,question,email',
                is_mobile='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.email_code.rps_dmmm')

    def test_email_code_lite_account_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code']

        self.setup_blackbox_response(
            alias_type='lite',
            alias='%s@mail.ru' % TEST_LOGIN,
            challenge_email='mail.ru',
            challenge_email_only=True,
        )

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()

        expected_response = self.expected_response(
            default_challenge='email_code',
            masked_challenge_email=None,
            has_question=False,
            has_email_code=True,
            has_phone=False,
        )
        expected_response['challenges_enabled']['email_code']['hint'] = [u't***r@m***.ru']

        self.assert_ok_response(
            resp,
            **expected_response
        )
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'shown',
                default_challenge='email_code',
                challenges='email_code',
                is_mobile='0',
            ),
        )
        self.assert_xunistater('challenges_shown', 'challenge.shown.web.email_code.rps_dmmm')

    def test_email_code_not_enabled_by_antifraud_tags(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['push_2fa', 'question', 'email_hint']
            track.email_confirmation_code = '12345'

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()
            self.assert_ok_response(
                resp,
                **self.expected_response(
                    default_challenge='question',
                    has_question=True,
                    has_phone=False,
                )
            )

    def test_email_code_not_enabled_by_settings(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code', 'question', 'email_hint']
            track.email_confirmation_code = '12345'

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=False,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()
            self.assert_ok_response(
                resp,
                **self.expected_response(
                    default_challenge='question',
                    has_question=True,
                    has_phone=False,
                )
            )

    def test_email_code_not_enabled_by_experiment(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code', 'question', 'email_hint']
            track.email_confirmation_code = '12345'

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=0,
        ):
            resp = self.make_request()
            self.assert_ok_response(
                resp,
                **self.expected_response(
                    default_challenge='question',
                    has_question=True,
                    has_phone=False,
                )
            )

    def test_email_code_not_enabled_by_account_type(self):
        self.setup_blackbox_response(native_email_only=True)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['email_code', 'question', 'email_hint']
            track.email_confirmation_code = '12345'

        with settings_context(
            EMAIL_CODE_CHALLENGE_ENABLED=True,
            EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR=1,
        ):
            resp = self.make_request()
            self.assert_ok_response(
                resp,
                **self.expected_response(
                    default_challenge='question',
                    has_question=True,
                    has_phone=False,
                    masked_challenge_email=None,
                )
            )
