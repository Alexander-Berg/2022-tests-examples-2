# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.emails import (
    assert_user_notified_about_alias_as_email_disabled,
    assert_user_notified_about_alias_as_email_enabled,
)
from passport.backend.api.tests.views.bundle.mixins.account import GetAccountBySessionOrTokenMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_DISPLAY_LANGUAGE,
    TEST_OAUTH_SCOPE,
    TEST_OPERATION_ID,
    TEST_OTHER_EXIST_PHONE_NUMBER,
    TEST_PHONE_CREATED_DT,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_PHONISH_LOGIN1,
    TEST_UID,
    TEST_UID1,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
    TEST_YANDEXUID_VALUE,
)
from passport.backend.api.views.bundle.constants import (
    BIND_PHONE_OAUTH_SCOPE,
    X_TOKEN_OAUTH_SCOPE,
)
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.api.views.bundle.phone.manage.base import Confirmation
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_data_equals
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_login_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.yasms import exceptions as yasms_exceptions
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.conf import settings
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.mailer.faker.mail_utils import create_native_email
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_no_default_phone_chosen,
    assert_no_phone_in_db,
    assert_phone_has_been_bound,
    assert_secure_phone_being_bound,
    build_account_from_session,
    build_phone_being_bound,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_secure_phone_being_bound,
    build_simple_replaces_secure_operations,
    build_unbound_phone_binding,
)
from passport.backend.core.models.phones.phones import (
    SecureBindOperation,
    SECURITY_IDENTITY,
    SimpleBindOperation,
)
from passport.backend.core.test.consts import (
    TEST_FIRSTNAME1,
    TEST_LOGIN1,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.time import (
    datetime_to_integer_unixtime as to_unixtime,
    zero_datetime,
)

from .base import PhoneManageBaseTestCase
from .base_test_data import (
    TEST_CONFIRMATION_CODE,
    TEST_LOGIN,
    TEST_MARK_OPERATION_TTL,
    TEST_OP_CODE_CONFIRMED_DT,
    TEST_OP_CODE_CONFIRMED_TS,
    TEST_OP_CODE_LAST_SENT_DT,
    TEST_OP_CODE_LAST_SENT_TS,
    TEST_OP_FINISHED_DT,
    TEST_OP_FINISHED_TS,
    TEST_OP_PASSWORD_VERIFIED_DT,
    TEST_OP_PASSWORD_VERIFIED_TS,
    TEST_OPERATION_ID_EXTRA,
    TEST_OPERATION_STARTED_DT,
    TEST_OPERATION_STARTED_TS,
    TEST_OPERATION_TTL,
    TEST_PASSWORD,
    TEST_PHONE_ADMITTED_DT,
    TEST_PHONE_ADMITTED_TS,
    TEST_PHONE_BOUND_DT,
    TEST_PHONE_BOUND_TS,
    TEST_PHONE_CONFIRMED_DT,
    TEST_PHONE_CONFIRMED_TS,
    TEST_PHONE_CREATED_TS,
    TEST_PHONE_ID,
    TEST_PHONE_SECURED_DT,
    TEST_PHONE_SECURED_TS,
    TEST_REPLACEMENT_PHONE_ID,
    TEST_REPLACEMENT_PHONE_NUMBER,
    TEST_SECURE_PHONE_ID,
    TEST_SECURE_PHONE_NUMBER,
)


TEST_OPERATION_CONFIRMED = TEST_PHONE_CREATED_DT + timedelta(hours=1)
TEST_UNBOUND_PHONE_ID = TEST_PHONE_ID2 + 1


class BaseSmsTestCase(PhoneManageBaseTestCase):
    phone = {}
    operation = {}

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE, operation_fields=None,
                              password_is_set=True):
        phone = dict(self.phone)

        if not phone.get('bound'):
            binding = build_unbound_phone_binding(phone['id'], phone['number'])
        else:
            raise NotImplementedError()  # pragma: no cover

        operation = dict(self.operation)
        if operation_fields:
            operation.update(operation_fields)
        bb_kwargs = {
            'phones': [phone],
            'phone_operations': [operation],
            'phone_bindings': [binding],
            'crypt_password': '1:pass' if password_is_set else None,
        }
        bb_response = blackbox_sessionid_multi_response(
            **bb_kwargs
        )
        self.env.blackbox.set_blackbox_response_value('sessionid', bb_response)
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
                **bb_kwargs
            ),
        )

        self.env.db.serialize_sessionid(bb_response)

    def assert_response_ok(self, rv):
        self.assert_ok_response(
            rv,
            track_id=self.track_id,
        )

    def check_yasms_no_requests(self):
        eq_(len(self.env.yasms.requests), 0)

    def assert_statbox_submitted(self, with_check_cookies=False):
        entries = [self.env.statbox.entry('submitted', _exclude=['mode'], operation_id=str(TEST_OPERATION_ID))]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def _test_error_operation_expired(self):
        # Время жизни операции вышло.
        self.set_blackbox_response(operation_fields={'finished': datetime.now()})
        rv = self.make_request()
        self.assert_error_response(rv, ['operation.expired'])


@with_settings_hosts()
class SendSmsTestCase(BaseSmsTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/send_code/'
    base_request_args = {'operation_id': TEST_OPERATION_ID, 'display_language': TEST_DISPLAY_LANGUAGE}
    step = 'resend_code'
    mode = 'secure_bind'
    with_check_cookies = True

    def setUp(self):
        super(SendSmsTestCase, self).setUp()

        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'bind',
            'security_identity': SECURITY_IDENTITY,
            'phone_id': TEST_PHONE_ID,
            'code_value': TEST_CONFIRMATION_CODE,
            'code_send_count': 1,
            'code_last_sent': TEST_OP_CODE_LAST_SENT_DT,
            'started': TEST_OPERATION_STARTED_DT,
            'finished': DatetimeNow() + TEST_OPERATION_TTL,
        }

        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

    def assert_response_ok(self, rv):
        self.assert_ok_response(
            rv,
            code_length=settings.SMS_VALIDATION_CODE_LENGTH,
            track_id=self.track_id,
        )

    def assert_statbox_ok(self, sms_count='1', with_check_cookies=False):
        entries = [self.env.statbox.entry('submitted', _exclude=['mode'], operation_id=str(TEST_OPERATION_ID))]
        entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('code_sent', sms_count=sms_count),
            self.env.statbox.entry('completed'),
        ])
        self.env.statbox.assert_has_written(entries)

    def assert_statbox_error(self, error='sms_limit.exceeded', with_check_cookies=False, **error_kwargs):
        entries = [self.env.statbox.entry('submitted', _exclude=['mode'], operation_id=str(TEST_OPERATION_ID))]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(
            self.env.statbox.entry(
                'send_code_error',
                operation_id=str(TEST_OPERATION_ID),
                error=error,
                **error_kwargs
            )
        )
        self.env.statbox.assert_has_written(entries)

    def test_ok_send_code_second_time(self):
        """
        Отправляем код повторно. Код должен быть взят из операции.
        """
        self.set_blackbox_response(operation_fields={
            'code_value': '591312',
            'code_send_count': 1,
            'code_last_sent': TEST_OP_CODE_LAST_SENT_DT,
        })

        rv = self.make_request()

        self.assert_response_ok(rv)

        self.check_db_phone_operation(
            dict(
                type='bind',
                id=TEST_OPERATION_ID,
                code_send_count=2,
                security_identity=SECURITY_IDENTITY,
                code_last_sent=DatetimeNow(),
                code_value='591312',
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
            ),
            id_=TEST_OPERATION_ID,
        )

        eq_(self._fake_generate_random_code.call_count, 0)

        self.check_yasms_send_sms_request(self.env.yasms.requests[0], code='591312')

        self.assert_events_are_empty(self.env.handle_mock)

        self.assert_statbox_ok(sms_count='2', with_check_cookies=True)

    def test_error_already_confirmed(self):
        """
        В операции есть отметка о том, что код уже был успешно подтвержден.
        """

        self.set_blackbox_response(operation_fields={
            'code_confirmed': TEST_OPERATION_CONFIRMED,
            'code_last_sent': TEST_OP_CODE_LAST_SENT_DT,
            'code_value': TEST_CONFIRMATION_CODE,
            'code_send_count': 1,
        })

        rv = self.make_request()
        self.assert_error_response(rv, ['phone.confirmed'])

        self.check_db_phone_operation(
            dict(
                type='bind',
                id=TEST_OPERATION_ID,
                code_send_count=1,
                security_identity=SECURITY_IDENTITY,
                code_value=TEST_CONFIRMATION_CODE,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
                code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                code_confirmed=TEST_OPERATION_CONFIRMED,
            ),
            id_=TEST_OPERATION_ID,
        )

        eq_(self._fake_generate_random_code.call_count, 0)
        self.check_yasms_no_requests()

        self.assert_statbox_error('phone.confirmed', with_check_cookies=True)

    def test_ok_sms_count_limit_exceeded(self):
        """
        Тест "на всякий случай".
        Для текущей операции уже отправили много (settings.SMS_VALIDATION_MAX_SMS_COUNT) смс, проверим,
        что все равно можно отправлять коды.
        """

        self.set_blackbox_response(operation_fields={
            'code_last_sent': TEST_OP_CODE_LAST_SENT_DT,
            'code_value': TEST_CONFIRMATION_CODE,
            'code_send_count': settings.SMS_VALIDATION_MAX_SMS_COUNT,
        })

        rv = self.make_request()
        self.assert_response_ok(rv)

        self.check_db_phone_operation(
            dict(
                type='bind',
                code_send_count=settings.SMS_VALIDATION_MAX_SMS_COUNT + 1,
                security_identity=SECURITY_IDENTITY,
                code_last_sent=DatetimeNow(),
                code_value=TEST_CONFIRMATION_CODE,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
            ),
            id_=TEST_OPERATION_ID,
        )

        self.assert_statbox_ok(sms_count=str(settings.SMS_VALIDATION_MAX_SMS_COUNT + 1), with_check_cookies=True)

        eq_(self._fake_generate_random_code.call_count, 0)
        self.check_yasms_send_sms_request(self.env.yasms.requests[0])

    def test_error_sms_resent_too_soon(self):
        """
        Для текущей операции уже отправили смс, и сразу просим отправить еще раз.
        """
        self.set_blackbox_response(operation_fields={
            'code_last_sent': datetime.now(),
            'code_value': TEST_CONFIRMATION_CODE,
            'code_send_count': 1,
        })

        rv = self.make_request()
        self.assert_error_response(rv, ['sms_limit.exceeded'])

        self.check_db_phone_operation(
            dict(
                type='bind',
                id=TEST_OPERATION_ID,
                code_send_count=1,
                security_identity=SECURITY_IDENTITY,
                code_value=TEST_CONFIRMATION_CODE,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
                code_last_sent=DatetimeNow(),
            ),
            id_=TEST_OPERATION_ID,
        )

        eq_(self._fake_generate_random_code.call_count, 0)
        self.check_yasms_no_requests()

        self.assert_statbox_error(reason='rate_limit', with_check_cookies=True)

    def test_yasms_errors_processing(self):
        """
        Проверяем, что в случае ошибок при вызове yasms мы правильно на них реагируем
        (ловим исключение, пишем в statbox,выкидываем бандловое исключение.)
        """
        exceptions_mapping = {
            yasms_exceptions.YaSmsLimitExceeded: ('sms_limit.exceeded', 'sms_limit.exceeded', 'yasms_phone_limit'),
            yasms_exceptions.YaSmsUidLimitExceeded: ('sms_limit.exceeded', 'sms_limit.exceeded', 'yasms_uid_limit'),
            yasms_exceptions.YaSmsPermanentBlock: ('phone.blocked', 'phone.blocked', None),
            yasms_exceptions.YaSmsTemporaryBlock: ('sms_limit.exceeded', 'sms_limit.exceeded', 'yasms_rate_limit'),
            yasms_exceptions.YaSmsPhoneNumberValueError: ('sms.isnt_sent', 'number.invalid', None),
            yasms_exceptions.YaSmsDeliveryError: ('sms.isnt_sent', 'backend.yasms_failed', None),
            yasms_exceptions.YaSmsError: ('sms.isnt_sent', 'exception.unhandled', None),
        }

        self.set_blackbox_response()

        for raised_exc, (statbox_error_name, returned_error, statbox_reason) in exceptions_mapping.items():
            self.env.statbox_handle_mock.reset_mock()

            self.env.yasms.set_response_side_effect('send_sms', raised_exc)

            rv = self.make_request()
            self.assert_error_response(rv, [returned_error])

            self.check_db_phone_operation(
                dict(
                    type='bind',
                    id=TEST_OPERATION_ID,
                    code_send_count=1,
                    code_value=TEST_CONFIRMATION_CODE,
                    security_identity=SECURITY_IDENTITY,
                    started=TEST_OPERATION_STARTED_DT,
                    finished=DatetimeNow() + TEST_OPERATION_TTL,
                    code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                ),
                id_=TEST_OPERATION_ID,
            )

            if statbox_reason:
                self.assert_statbox_error(error=statbox_error_name, reason=statbox_reason, with_check_cookies=True)
            else:
                self.assert_statbox_error(error=statbox_error_name, with_check_cookies=True)

    def test_error_global_ip_limit_exceed(self):
        """
        Если переполнился глобальный счетчик отправки, то вернем ошибку.
        """
        self.set_blackbox_response()

        counter = sms_per_ip.get_counter(user_ip=TEST_USER_IP)
        # установим счетчик вызовов на ip в limit
        for i in range(counter.limit):
            counter.incr(TEST_USER_IP)

        rv = self.make_request()
        self.assert_error_response(rv, ['sms_limit.exceeded'])

        self.check_db_phone_operation(
            dict(
                type='bind',
                id=TEST_OPERATION_ID,
                security_identity=SECURITY_IDENTITY,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
                code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                code_value=TEST_CONFIRMATION_CODE,
                code_send_count=1,
            ),
            id_=TEST_OPERATION_ID,
        )

        self.check_yasms_no_requests()

        self.assert_statbox_error(reason='ip_limit', with_check_cookies=True)

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_account_disabled_on_deletion(self):
        self._test_error_account_disabled_on_deletion()

    def test_error_operation_not_found(self):
        self._test_error_operation_not_found(submitted_first=True)

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()

    def test_error_operation_expired(self):
        self._test_error_operation_expired()

    def test_stores_display_langauge_to_track(self):
        self.set_blackbox_response()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.display_language = 'ru'

        rv = self.make_request(
            data=dict(
                self.base_request_args,
                display_language='tr',
                track_id=self.track_id,
            ),
        )

        self.assert_response_ok(rv)

        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, 'tr')

    def test_user_does_not_admit_phone(self):
        self.set_blackbox_response(operation_fields={
            'code_value': None,
        })

        rv = self.make_request()

        self.assert_error_response(rv, ['action.not_required'])


@with_settings_hosts()
class CheckSmsTestCase(BaseSmsTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/check_code/'
    base_request_args = {'operation_id': TEST_OPERATION_ID, 'code': TEST_CONFIRMATION_CODE}
    step = 'check_code'
    mode = 'secure_bind'
    with_check_cookies = True

    def setUp(self):
        super(CheckSmsTestCase, self).setUp()

        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'bind',
            'security_identity': SECURITY_IDENTITY,
            'phone_id': TEST_PHONE_ID,
            'code_value': TEST_CONFIRMATION_CODE,
            'code_send_count': 1,
            'code_last_sent': TEST_OP_CODE_LAST_SENT_DT,
            'started': TEST_OPERATION_STARTED_DT,
            'finished': DatetimeNow() + TEST_OPERATION_TTL,
        }

        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

    def _test_ok(self, by_token=False):
        """
        Даётся правильный код подтверждения.
        В операцию записывается время подвтерждения кода.
        """
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        track = self.track_manager.read(self.track_id)
        eq_(len(track.phone_operation_confirmations.get()), 0)

        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv)

        entries = [self.env.statbox.entry('submitted', _exclude=['mode'], operation_id=str(TEST_OPERATION_ID))]
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
                self.env.statbox.entry('completed'),
            ]
        )

        self.env.statbox.assert_has_written(entries)

        self.check_db_phone_operation(
            dict(
                type='bind',
                code_send_count=1,
                security_identity=SECURITY_IDENTITY,
                code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                code_value=TEST_CONFIRMATION_CODE,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
                code_confirmed=zero_datetime,
                code_checks_count=1,
            ),
            id_=TEST_OPERATION_ID,
        )

        eq_(self._fake_generate_random_code.call_count, 0)
        eq_(len(self.env.yasms.get_requests_by_method('send_sms')), 0)

        self.env.event_logger.assert_events_are_logged({})

        track = self.track_manager.read(self.track_id)
        confirmations = [Confirmation.from_json(c) for c in track.phone_operation_confirmations.get()]
        eq_(
            confirmations[0],
            Confirmation(
                logical_operation_id=TEST_OPERATION_ID,
                phone_id=TEST_PHONE_ID,
                phone_confirmed=DatetimeNow(),
            ),
        )

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_error_invalid_code(self):
        """
        Проверяем отправленный код. Код неверный.
        """
        self.set_blackbox_response()

        rv = self.make_request(data={'operation_id': TEST_OPERATION_ID, 'code': 'invalid_code'})
        self.assert_error_response(rv, ['code.invalid'])

        self.check_db_phone_operation(
            dict(
                type='bind',
                id=TEST_OPERATION_ID,
                code_send_count=1,
                security_identity=SECURITY_IDENTITY,
                code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                code_value=TEST_CONFIRMATION_CODE,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
                code_checks_count=1,
            ),
            id_=TEST_OPERATION_ID,
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted', _exclude=['mode'], operation_id=str(TEST_OPERATION_ID)),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'phone_confirmed',
                _exclude=['confirmation_time'],
                action='confirm_phone',
                error='code.invalid',
            ),
        ])

        self.env.event_logger.assert_events_are_logged([])

    def test_error_empty_code(self):
        """
        Недопустим пустой код подтверждения.
        """
        self.set_blackbox_response()

        rv = self.make_request(data={'operation_id': TEST_OPERATION_ID, 'code': ''})

        self.assert_error_response(rv, ['code.empty'])

    def test_error_sms_not_sent(self):
        """
        Еще не отправляли смс с кодом, нечего проверять.
        """
        self.set_blackbox_response(operation_fields={
            'code_send_count': 0,
        })

        rv = self.make_request(data={'operation_id': TEST_OPERATION_ID, 'code': 'invalid_code'})
        self.assert_error_response(rv, ['sms.not_sent'])

        self.check_db_phone_operation(
            dict(
                type='bind',
                id=TEST_OPERATION_ID,
                code_send_count=0,
                security_identity=SECURITY_IDENTITY,
                code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                code_value=TEST_CONFIRMATION_CODE,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
                code_checks_count=0,
            ),
            id_=TEST_OPERATION_ID,
        )
        self.assert_statbox_submitted(with_check_cookies=True)

    def test_error_confirmations_limit_exceeded(self):
        """
        Слишком много попыток проверки кода для текущей операции.
        """
        self.set_blackbox_response(operation_fields={
            'code_checks_count': settings.SMS_VALIDATION_MAX_CHECKS_COUNT,
        })

        rv = self.make_request(data={'operation_id': TEST_OPERATION_ID, 'code': 'invalid_code'})
        self.assert_error_response(rv, ['confirmations_limit.exceeded'])

        self.check_db_phone_operation(
            dict(
                type='bind',
                id=TEST_OPERATION_ID,
                code_send_count=1,
                security_identity=SECURITY_IDENTITY,
                code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                code_value=TEST_CONFIRMATION_CODE,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
                code_checks_count=settings.SMS_VALIDATION_MAX_CHECKS_COUNT,
            ),
            id_=TEST_OPERATION_ID,
        )

        self.assert_statbox_submitted(with_check_cookies=True)

    def test_error_code_confirmed(self):
        self.set_blackbox_response(
            operation_fields={
                'code_confirmed': TEST_OP_CODE_LAST_SENT_DT,
                'code_checks_count': 1,
            },
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['action.not_required'])

        assert_secure_phone_being_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID},
            {
                'code_confirmed': TEST_OP_CODE_LAST_SENT_DT,
                'code_checks_count': 1,
            },
        )

        self.assert_statbox_submitted(with_check_cookies=True)

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()

    def test_error_operation_not_found(self):
        self._test_error_operation_not_found(submitted_first=True)

    def test_error_operation_expired(self):
        self._test_error_operation_expired()


@with_settings_hosts()
class CheckPasswordTestCase(BaseSmsTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/check_password/'
    base_request_args = {'operation_id': TEST_OPERATION_ID, 'current_password': TEST_PASSWORD}
    step = 'check_password'
    mode = 'secure_bind'
    with_check_cookies = True

    def setUp(self):
        super(CheckPasswordTestCase, self).setUp()

        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'bind',
            'security_identity': SECURITY_IDENTITY,
            'phone_id': TEST_PHONE_ID,
            'code_value': TEST_CONFIRMATION_CODE,
            'code_send_count': 1,
            'finished': DatetimeNow() + TEST_OPERATION_TTL,
            'code_last_sent': TEST_OP_CODE_LAST_SENT_DT,
            'started': TEST_OPERATION_STARTED_DT,
        }

        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(uid=TEST_UID),
        )

    def assert_blackbox_login_called(self, password=TEST_PASSWORD, callnum=1, exclude_args=None):
        if exclude_args is None:
            exclude_args = []

        args = {
            'aliases': 'all_with_hidden',
            'authtype': authtypes.AUTH_TYPE_VERIFY,
            'format': 'json',
            'full_info': 'yes',
            'get_badauth_counts': 'yes',
            'get_public_name': 'yes',
            'is_display_name_empty': 'yes',
            'method': 'login',
            'password': password,
            'regname': 'yes',
            'uid': int(TEST_UID),
            'useragent': TEST_USER_AGENT,
            'ver': '2',
            'yandexuid': TEST_YANDEXUID_VALUE,
        }
        for exclude_arg in exclude_args:
            args.pop(exclude_arg)
        assert_builder_data_equals(
            self.env.blackbox,
            args,
            callnum=callnum,
            exclude_fields=[
                'userip',  # возвращается инстансом внутреннего класса в libipreg
            ],
        )

    def _test_ok(self, by_token=False):
        """
        С первой попытки правильно вводим пароль.
        """
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        track = self.track_manager.read(self.track_id)
        eq_(len(track.phone_operation_confirmations.get()), 0)

        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv)

        entries = [self.env.statbox.entry('submitted', _exclude=['mode'], operation_id=str(TEST_OPERATION_ID))]
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
                self.env.statbox.entry('password_checked'),
                self.env.statbox.entry('completed'),
            ],
        )

        self.env.statbox.assert_has_written(entries)

        self.check_db_phone_operation(
            dict(
                type='bind',
                code_send_count=1,
                security_identity=SECURITY_IDENTITY,
                code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                code_value=TEST_CONFIRMATION_CODE,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
                code_checks_count=0,
                password_verified=zero_datetime,
            ),
            id_=TEST_OPERATION_ID,
        )

        track = self.track_manager.read(self.track_id)
        confirmations = [Confirmation.from_json(c) for c in track.phone_operation_confirmations.get()]
        eq_(
            confirmations[0],
            Confirmation(
                logical_operation_id=TEST_OPERATION_ID,
                phone_id=TEST_PHONE_ID,
                password_verified=DatetimeNow(),
            ),
        )

    def test_ok_by_session(self):
        self._test_ok()
        self.assert_blackbox_login_called()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)
        self.assert_blackbox_login_called(exclude_args=['yandexuid'])

    def test_error_password_verified(self):
        self.set_blackbox_response(
            operation_fields={
                'password_verified': TEST_OP_CODE_LAST_SENT_DT,
            },
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['action.not_required'])

        eq_(self.env.blackbox.get_requests_by_method('login'), [])

        assert_secure_phone_being_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID},
            {'password_verified': TEST_OP_CODE_LAST_SENT_DT},
        )

        self.assert_statbox_submitted(with_check_cookies=True)

    def test_error_invalid_password(self):
        """
        Проверяем введенный пароль. Пароль неверный.
        """
        self.set_blackbox_response()
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['password.not_matched'])

        self.check_db_phone_operation(
            dict(
                type='bind',
                id=TEST_OPERATION_ID,
                code_send_count=1,
                security_identity=SECURITY_IDENTITY,
                code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                code_value=TEST_CONFIRMATION_CODE,
                started=TEST_OPERATION_STARTED_DT,
                finished=DatetimeNow() + TEST_OPERATION_TTL,
                code_checks_count=0,
            ),
            id_=TEST_OPERATION_ID,
        )

        self.assert_statbox_submitted(with_check_cookies=True)

    def test_ok_bruteforce_recognized_captcha_and_good_password(self):
        """
        Пришёл пользователь с верным паролем, ЧЯ сказал, что необходима капча,
        и капча уже пройдена. Успешно сохранили в БД данные.
        """
        self.set_blackbox_response()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )

        rv = self.make_request()
        self.assert_response_ok(rv)

        self.assert_blackbox_login_called()

        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_required, True)
        eq_(track.is_captcha_recognized, True)
        eq_(track.is_captcha_checked, True)

    def test_error_bruteforce_not_recognized_captcha_and_good_password(self):
        """
        Пришёл пользователь с верным паролем, ЧЯ сказал, что необходима капча, но капча еще не пройдена.
        Успешно сохранили в БД данные.
        """
        self.set_blackbox_response()

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['captcha.required'])

        self.assert_blackbox_login_called()

    def test_bruteforce_recognized_captcha_and_bad_password(self):
        """
        Пришёл пользователь с неправильным паролем, ЧЯ сказал что опять требуется капча
        и капча уже пройдена. Вернём 2 ошибки captcha.required, password.not_matched.
        """
        self.set_blackbox_response()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
                bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['captcha.required', 'password.not_matched'])

        self.assert_blackbox_login_called()

        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_required, True)
        eq_(track.is_captcha_recognized, False)
        eq_(track.is_captcha_checked, False)

    def test_ok_recognized_captcha_and_bad_password(self):
        """
        Пришёл пользователь с неправильным паролем, ЧЯ не требует капчи,
        но капча уже была пройдена в данном треке.
        Вернули ошибку password.not_matched.
        """

        self.set_blackbox_response()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['password.not_matched'])

        self.assert_blackbox_login_called()

        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_required, False)
        eq_(track.is_captcha_recognized, False)
        eq_(track.is_captcha_checked, False)

    def test_error_bruteforce_and_set_required_captcha(self):
        """
        Пришёл пользователь не важно с каким паролем, ЧЯ потребовал показать капчу.
        Записали об этом в трек и вернули ошибку captcha.required.
        """
        self.set_blackbox_response()

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['captcha.required'])

        self.assert_blackbox_login_called()

        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_required, True)
        eq_(track.is_captcha_recognized, None)
        eq_(track.is_captcha_checked, None)

    def test_ok_captcha_required_not_recognized(self):
        """
        Пришёл пользователь не важно с каким паролем.
        В треке написано, что нужна капча и еще не введена.
        Вернули ошибку captcha.required.
        """

        self.set_blackbox_response()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['captcha.required'])

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 0)

        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_required, True)
        eq_(track.is_captcha_recognized, None)
        eq_(track.is_captcha_checked, None)

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()

    def test_error_operation_not_found(self):
        self._test_error_operation_not_found(submitted_first=True)

    def test_error_operation_expired(self):
        self._test_error_operation_expired()


@with_settings_hosts()
class CancelOperationTestCase(BaseSmsTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/cancel_operation/'
    base_request_args = {'operation_id': TEST_OPERATION_ID}
    step = 'cancel_operation'
    mode = 'secure_bind'
    with_check_cookies = True

    def setUp(self):
        super(CancelOperationTestCase, self).setUp()

        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'bind',
            'security_identity': SECURITY_IDENTITY,
            'phone_id': TEST_PHONE_ID,
            'code_value': TEST_CONFIRMATION_CODE,
            'code_send_count': 1,
            'finished': DatetimeNow() + TEST_OPERATION_TTL,
            'code_last_sent': TEST_OP_CODE_LAST_SENT_DT,
            'started': TEST_OPERATION_STARTED_DT,
        }

    def _build_account(self, token_scope=X_TOKEN_OAUTH_SCOPE, phone_operation=SimpleBindOperation):
        userinfo = {}

        if phone_operation is SimpleBindOperation:
            userinfo = deep_merge(userinfo, build_phone_being_bound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164, TEST_OPERATION_ID))
        elif phone_operation is SecureBindOperation:
            userinfo = deep_merge(userinfo, build_secure_phone_being_bound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164, TEST_OPERATION_ID))
        else:
            raise NotImplementedError()  # pragma: no cover

        return dict(
            userinfo=userinfo,
            oauth={'scope': token_scope},
        )

    def _setup_account(self, account):
        oauth_response = blackbox_oauth_response(**deep_merge(account['userinfo'], account['oauth']))
        self.env.blackbox.set_response_value('oauth', oauth_response)

        userinfo_response = blackbox_userinfo_response(**account['userinfo'])
        self.env.db.serialize(userinfo_response)

    def _test_ok(self, by_token=False):
        """
        Удаляем существующую операцию.
        """
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv)

        entries = [self.env.statbox.entry('submitted', _exclude=['mode'], operation_id=str(TEST_OPERATION_ID))]
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
                self.env.statbox.entry('phone_operation_cancelled'),
                self.env.statbox.entry('completed'),
            ]
        )

        self.env.statbox.assert_has_written(entries)

        self.check_db_phone_operation_missing(TEST_OPERATION_ID)
        self.assert_blackbox_auth_method_ok(by_token)

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()

    def test_error_operation_not_found(self):
        self._test_error_operation_not_found(submitted_first=True)

    def test_error_operation_expired(self):
        self._test_error_operation_expired()

    def test_token_scope_bind_phone__simple_bind(self):
        self._setup_account(self._build_account(token_scope=BIND_PHONE_OAUTH_SCOPE))

        rv = self.make_request(headers=self.build_headers(authorization=TEST_AUTH_HEADER))

        self.assert_response_ok(rv)

    def test_token_scope_bind_phone__secure_bind(self):
        self._setup_account(
            self._build_account(
                token_scope=BIND_PHONE_OAUTH_SCOPE,
                phone_operation=SecureBindOperation,
            ),
        )

        rv = self.make_request(headers=self.build_headers(authorization=TEST_AUTH_HEADER))

        self.assert_error_response(rv, ['oauth_token.invalid'])


@with_settings_hosts(
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
)
class GetStateTestCase(BaseSmsTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/get_state/'
    base_request_args = {}
    step = 'get_state'

    def setUp(self):
        super(GetStateTestCase, self).setUp()
        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'bind',
            'security_identity': SECURITY_IDENTITY,
            'phone_id': TEST_PHONE_ID,
            'code_value': TEST_CONFIRMATION_CODE,
            'code_send_count': 1,
            'finished': DatetimeNow() + TEST_OPERATION_TTL,
            'code_last_sent': TEST_OP_CODE_LAST_SENT_DT,
            'started': TEST_OPERATION_STARTED_DT,
        }

    def get_state_response(self, phones_dict):
        return {
            'status': 'ok',
            'account': {
                'display_name': {
                    'default_avatar': '',
                    'name': '',
                },
                'uid': 1,
                'display_login': 'test',
                'person': {
                    'firstname': u'\\u0414',
                    'language': 'ru',
                    'gender': 1,
                    'birthday': '1963-05-15',
                    'lastname': u'\\u0424',
                    'country': 'ru',
                },
                'login': 'test',
                'phones': phones_dict,
            },
        }

    def setup_blackbox(self, uid=TEST_UID, **kwargs):
        bb_response = blackbox_sessionid_multi_response(uid=uid, **kwargs)
        self.env.blackbox.set_blackbox_response_value('sessionid', bb_response)

    def assert_ok_response(self, response, phones_dict=None, **kwargs):
        eq_(response.status_code, 200)
        data = json.loads(response.data)
        iterdiff(eq_)(data, self.get_state_response(phones_dict=phones_dict))

    def get_response_with_default(self, default_id=None):
        base_response = {
            str(TEST_PHONE_ID): {
                'id': TEST_PHONE_ID,
                'number': dump_number(TEST_PHONE_NUMBER),
                'created': TEST_PHONE_CREATED_TS,
                'bound': TEST_PHONE_BOUND_TS,
                'confirmed': TEST_PHONE_CONFIRMED_TS,
                'secured': TEST_PHONE_SECURED_TS,
                'need_admission': True,
                'is_default': False,
                'is_alias': False,
                'alias': {
                    'login_enabled': False,
                    'email_enabled': False,
                    'email_allowed': False,
                },
            },
            str(TEST_PHONE_ID2): {
                'id': TEST_PHONE_ID2,
                'number': dump_number(TEST_OTHER_EXIST_PHONE_NUMBER),
                'created': TEST_PHONE_CREATED_TS,
                'bound': TEST_PHONE_BOUND_TS,
                'confirmed': TEST_PHONE_CONFIRMED_TS,
                'need_admission': True,
                'is_default': False,
                'is_alias': False,
                'alias': {
                    'login_enabled': False,
                    'email_enabled': False,
                    'email_allowed': False,
                },
            },
            str(TEST_UNBOUND_PHONE_ID): {
                'id': TEST_UNBOUND_PHONE_ID,
                'number': dump_number(TEST_OTHER_EXIST_PHONE_NUMBER),
                'created': TEST_PHONE_CREATED_TS,
                'confirmed': TEST_PHONE_CONFIRMED_TS,
                'need_admission': True,
                'is_default': False,
                'is_alias': False,
                'alias': {
                    'login_enabled': False,
                    'email_enabled': False,
                    'email_allowed': False,
                },
            },
        }
        if default_id:
            base_response[default_id].update(is_default=True)
        return base_response

    def _test_ok(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)

        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'bind',
            'security_identity': SECURITY_IDENTITY,
            'phone_id': TEST_PHONE_ID,
            'code_value': None,
            'code_send_count': 0,
            'code_last_sent': None,
            'started': TEST_OPERATION_STARTED_DT,
            'finished': TEST_OP_FINISHED_DT,
        }
        self.set_blackbox_response()

        rv = self.make_request(headers=headers)

        self.assert_ok_response(rv, {
            '1': {
                'id': 1,
                'number': dump_number(TEST_PHONE_NUMBER),
                'created': TEST_PHONE_CREATED_TS,
                'need_admission': False,
                'is_alias': False,
                'alias': {
                    'login_enabled': False,
                    'email_enabled': False,
                    'email_allowed': False,
                },
                'is_default': False,

                'operation': {
                    'id': TEST_OPERATION_ID,
                    'type': 'bind',
                    'is_secure_phone_operation': True,
                    'started': TEST_OPERATION_STARTED_TS,
                    'finished': TEST_OP_FINISHED_TS,
                    'does_user_admit_phone': False,
                    'in_quarantine': False,
                    'code': {
                        'send_count': 0,
                        'checks_count': 0,
                    },
                },
            },
        })

        entries = []
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_blackbox_auth_method_ok(by_token)

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_empty_phones_list(self):

        bb_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            phones=[],
            phone_operations=[],
        )
        self.env.blackbox.set_blackbox_response_value('sessionid', bb_response)

        rv = self.make_request()

        self.assert_ok_response(rv, {})

    def test_max_filled_phone_and_operation(self):
        """
        На телефоне и операции все поля заполнены чем-то смысленным.
        Проверим, что в ответе есть все нужное и ничего лишнего.
        """
        self.setup_blackbox(
            uid=TEST_UID,
            **deep_merge(
                build_phone_secured(
                    TEST_SECURE_PHONE_ID,
                    TEST_SECURE_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_BOUND_DT,
                    phone_confirmed=TEST_PHONE_CONFIRMED_DT,
                    phone_admitted=TEST_PHONE_ADMITTED_DT,
                    phone_secured=TEST_PHONE_SECURED_DT,
                ),
                build_phone_bound(
                    TEST_REPLACEMENT_PHONE_ID,
                    TEST_REPLACEMENT_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_BOUND_DT,
                    phone_confirmed=TEST_PHONE_CONFIRMED_DT,
                    phone_admitted=TEST_PHONE_ADMITTED_DT,
                ),
                build_simple_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID,
                    secure_phone_id=TEST_SECURE_PHONE_ID,
                    simple_operation_id=TEST_OPERATION_ID_EXTRA,
                    simple_phone_id=TEST_REPLACEMENT_PHONE_ID,
                    simple_phone_number=TEST_REPLACEMENT_PHONE_NUMBER.e164,
                    started=TEST_OPERATION_STARTED_DT,
                    finished=TEST_OPERATION_STARTED_DT + TEST_OPERATION_TTL,
                    password_verified=TEST_OP_PASSWORD_VERIFIED_DT,
                    secure_code_confirmed=TEST_OP_CODE_CONFIRMED_DT,
                    secure_code_value=TEST_CONFIRMATION_CODE,
                    secure_code_checks_count=5,
                    secure_code_send_count=4,
                    secure_code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                    simple_code_confirmed=TEST_OP_CODE_CONFIRMED_DT,
                    simple_code_value=TEST_CONFIRMATION_CODE,
                    simple_code_checks_count=6,
                    simple_code_send_count=5,
                    simple_code_last_sent=TEST_OP_CODE_LAST_SENT_DT,
                ),
            )
        )
        rv = self.make_request()

        self.assert_ok_response(rv, {
            str(TEST_SECURE_PHONE_ID): {
                'id': TEST_SECURE_PHONE_ID,
                'number': dump_number(TEST_SECURE_PHONE_NUMBER),
                'created': TEST_PHONE_CREATED_TS,
                'bound': TEST_PHONE_BOUND_TS,
                'confirmed': TEST_PHONE_CONFIRMED_TS,
                'secured': TEST_PHONE_SECURED_TS,
                'admitted': TEST_PHONE_ADMITTED_TS,
                'is_alias': False,
                'alias': {
                    'login_enabled': False,
                    'email_enabled': False,
                    'email_allowed': False,
                },
                'need_admission': True,
                'is_default': True,

                'operation': {
                    'id': TEST_OPERATION_ID,
                    'type': 'replace',
                    'is_secure_phone_operation': True,
                    'started': to_unixtime(TEST_OPERATION_STARTED_DT),
                    'finished': to_unixtime(TEST_OPERATION_STARTED_DT + TEST_OPERATION_TTL),
                    'phone_id2': TEST_REPLACEMENT_PHONE_ID,
                    'does_user_admit_phone': True,
                    'in_quarantine': False,
                    'password_verified': TEST_OP_PASSWORD_VERIFIED_TS,
                    'code': {
                        'send_count': 4,
                        'confirmed': TEST_OP_CODE_CONFIRMED_TS,
                        'last_sent': TEST_OP_CODE_LAST_SENT_TS,
                        'checks_count': 5,
                    },
                },
            },
            str(TEST_REPLACEMENT_PHONE_ID): {
                'id': TEST_REPLACEMENT_PHONE_ID,
                'number': dump_number(TEST_REPLACEMENT_PHONE_NUMBER),
                'created': TEST_PHONE_CREATED_TS,
                'bound': TEST_PHONE_BOUND_TS,
                'confirmed': TEST_PHONE_CONFIRMED_TS,
                'admitted': TEST_PHONE_ADMITTED_TS,
                'is_alias': False,
                'alias': {
                    'login_enabled': False,
                    'email_enabled': False,
                    'email_allowed': False,
                },
                'need_admission': True,
                'is_default': False,

                'operation': {
                    'id': TEST_OPERATION_ID_EXTRA,
                    'type': 'mark',
                    'is_secure_phone_operation': False,
                    'started': to_unixtime(TEST_OPERATION_STARTED_DT),
                    'finished': to_unixtime(TEST_OPERATION_STARTED_DT + TEST_OPERATION_TTL),
                    'phone_id2': TEST_SECURE_PHONE_ID,
                    'does_user_admit_phone': True,
                    'in_quarantine': False,
                    'password_verified': TEST_OP_PASSWORD_VERIFIED_TS,
                    'code': {
                        'send_count': 5,
                        'confirmed': TEST_OP_CODE_CONFIRMED_TS,
                        'last_sent': TEST_OP_CODE_LAST_SENT_TS,
                        'checks_count': 6,
                    },
                },
            },
        })

    def test_expired_operation(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **build_phone_being_bound(
                    TEST_PHONE_ID,
                    TEST_PHONE_NUMBER.e164,
                    TEST_OPERATION_ID,
                    phone_created=datetime.now(),
                    operation_started=datetime.now(),
                    operation_finished=datetime.now(),
                    code_last_sent=datetime.now(),
                )
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            {
                str(TEST_PHONE_ID): {
                    'id': TEST_PHONE_ID,
                    'number': dump_number(TEST_PHONE_NUMBER),
                    'created': TimeNow(),
                    'is_alias': False,
                    'alias': {
                        'login_enabled': False,
                        'email_enabled': False,
                        'email_allowed': False,
                    },
                    'need_admission': False,
                    'is_default': False,

                    'operation': {
                        'id': TEST_OPERATION_ID,
                        'type': 'bind',
                        'is_secure_phone_operation': False,
                        'code': {
                            'send_count': 1,
                            'checks_count': 0,
                            'last_sent': TimeNow(),
                        },
                        'started': TimeNow(),
                        'finished': TimeNow(),
                        'does_user_admit_phone': True,
                        'in_quarantine': False,
                    },
                },
            },
        )

    def test_explicit_default(self):
        self.setup_blackbox(
            uid=TEST_UID,
            **deep_merge(
                build_phone_secured(
                    TEST_PHONE_ID,
                    TEST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_BOUND_DT,
                    phone_confirmed=TEST_PHONE_CONFIRMED_DT,
                    phone_secured=TEST_PHONE_SECURED_DT,
                    is_default=True,
                ),
                build_phone_bound(
                    TEST_PHONE_ID2,
                    TEST_OTHER_EXIST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_BOUND_DT,
                    phone_confirmed=TEST_PHONE_CONFIRMED_DT,
                ),
                build_phone_unbound(
                    TEST_UNBOUND_PHONE_ID,
                    TEST_OTHER_EXIST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_confirmed=TEST_PHONE_CONFIRMED_DT,
                ),
            )
        )
        rv = self.make_request()
        expected = self.get_response_with_default(default_id=str(TEST_PHONE_ID))
        self.assert_ok_response(rv, expected)

    def test_implicit_default(self):
        self.setup_blackbox(
            uid=TEST_UID,
            **deep_merge(
                build_phone_secured(
                    TEST_PHONE_ID,
                    TEST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_BOUND_DT,
                    phone_confirmed=TEST_PHONE_CONFIRMED_DT,
                    phone_secured=TEST_PHONE_SECURED_DT,
                ),
                build_phone_bound(
                    TEST_PHONE_ID2,
                    TEST_OTHER_EXIST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_BOUND_DT,
                    phone_confirmed=TEST_PHONE_CONFIRMED_DT,
                ),
                build_phone_unbound(
                    TEST_UNBOUND_PHONE_ID,
                    TEST_OTHER_EXIST_PHONE_NUMBER.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_confirmed=TEST_PHONE_CONFIRMED_DT,
                ),
            )
        )
        rv = self.make_request()
        expected = self.get_response_with_default(default_id=str(TEST_PHONE_ID2))
        self.assert_ok_response(rv, expected)


@with_settings_hosts(
    YASMS_MARK_OPERATION_TTL=TEST_MARK_OPERATION_TTL,
)
class TestRemoveSimplePhone(BaseSmsTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/remove_simple/'
    base_request_args = {
        'phone_id': TEST_PHONE_ID,
        'display_language': TEST_DISPLAY_LANGUAGE,
    }
    step = 'remove_simple_phone'

    def setUp(self):
        super(TestRemoveSimplePhone, self).setUp()
        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
        }

        self.operation = {
            'id': TEST_OPERATION_ID,
            'type': 'bind',
            'security_identity': SECURITY_IDENTITY,
            'phone_id': TEST_PHONE_ID,
            'code_value': TEST_CONFIRMATION_CODE,
            'code_send_count': 1,
            'finished': DatetimeNow() + TEST_OPERATION_TTL,
            'code_last_sent': TEST_OP_CODE_LAST_SENT_DT,
            'started': TEST_OPERATION_STARTED_DT,
        }

    def assert_statbox_ok(self, with_check_cookies=False):
        entries = [self.env.statbox.entry('submitted', _exclude=['mode', 'track_id'])]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
                self.env.statbox.entry('mark_operation_created', _exclude=['mode', 'track_id']),
                self.env.statbox.entry('completed', _exclude=['mode', 'track_id', 'operation_id']),
            ],
        )
        self.env.statbox.assert_has_written(entries)

    def _test_bound(self, headers=None, method='sessionid'):
        # Телефон привязан
        # Телефон используется для уведомлений
        self._build_account(**build_phone_bound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164, is_default=True))

        rv = self.make_request(headers=headers)

        self._assert_response_ok(rv)

        assert_no_default_phone_chosen(self.env.db, TEST_UID)
        assert_no_phone_in_db(self.env.db, TEST_UID, TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        assert_phone_has_been_bound(self.env.db, TEST_UID, TEST_PHONE_NUMBER.e164)

        self.assert_events_are_logged(
            self.env.handle_mock,
            self._event_lines_phone_marked() +
            self._event_lines_action_consumer() +
            self._event_lines_simple_phone_removed() +
            ({'name': 'phones.default', 'value': '0'},) +
            self._event_lines_action_consumer(),
        )

        self.assert_statbox_ok(with_check_cookies=headers is None)

        self._assert_phone_data_asked_from_blackbox(self.env.blackbox.requests[0], method=method)
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='phone_change',
            uid=TEST_UID,
            title='В аккаунте testuser изменён номер телефона',
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )

    def test_bound_by_session(self):
        self._test_bound()

    def test_bound_by_token(self):
        self._test_bound(headers=self.build_headers(authorization=TEST_AUTH_HEADER), method='oauth')

    def test_unbound(self):
        # Телефон отвязан

        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            **build_phone_unbound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        )

        rv = self.make_request()

        self._assert_response_ok(rv)

        assert_no_phone_in_db(self.env.db, TEST_UID, TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)

        self.assert_events_are_logged(
            self.env.handle_mock,
            self._event_lines_phone_marked() +
            self._event_lines_action_consumer() +
            self._event_lines_simple_phone_removed() +
            self._event_lines_action_consumer(),
        )

        self.assert_statbox_ok(with_check_cookies=True)

        self._assert_phone_data_asked_from_blackbox(self.env.blackbox.requests[0])

    def test_invalid_phone_id(self):
        rv = self.make_request(data=dict(self.base_request_args, phone_id=u'x'))
        self.assert_error_response(rv, [u'phone_id.invalid'])

    def test_phone_not_found(self):
        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            phones=[],
        )

        rv = self.make_request(data=dict(self.base_request_args, phone_id=u'0'))

        self.assert_error_response(rv, [u'phone.not_found'])

    def test_secure_phone(self):
        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            **build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        )

        rv = self.make_request()

        self.assert_error_response(rv, [u'phone.invalid_type'])

    def test_phone_has_operation(self):
        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            **build_phone_being_bound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164, TEST_OPERATION_ID)
        )

        rv = self.make_request()

        self.assert_error_response(rv, [u'operation.exists'])

    def test_phonish(self):
        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True

        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    login=TEST_PHONISH_LOGIN1,
                    aliases={'phonish': TEST_PHONISH_LOGIN1},
                ),
                build_phone_bound(
                    TEST_PHONE_ID,
                    TEST_PHONE_NUMBER.e164,
                    binding_flags=flags,
                ),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, [u'account.invalid_type'])

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def _assert_response_ok(self, rv):
        eq_(rv.status_code, 200)
        data = json.loads(rv.data)

        eq_(data['status'], 'ok')
        ok_('account' in data)

    def _assert_phone_data_asked_from_blackbox(self, request, method='sessionid'):
        request.assert_query_contains({
            'method': method,
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
        })
        request.assert_contains_attributes({'phones.secure', 'phones.default'})

    def _event_lines_phone_marked(self):
        return (
            {'name': 'action', 'value': 'simple_phone_remove'},
            {'name': 'phone.%d.number' % TEST_PHONE_ID, 'value': '+79261234567'},
            {'name': 'phone.%d.operation.1.type' % TEST_PHONE_ID, 'value': 'mark'},
            {'name': 'phone.%d.operation.1.action' % TEST_PHONE_ID, 'value': 'created'},
            {'name': 'phone.%d.operation.1.security_identity' % TEST_PHONE_ID, 'value': '79261234567'},
            {'name': 'phone.%d.operation.1.started' % TEST_PHONE_ID, 'value': TimeNow()},
            {'name': 'phone.%d.operation.1.finished' % TEST_PHONE_ID, 'value': TimeNow(offset=TEST_MARK_OPERATION_TTL)},
        )

    def _event_lines_action_consumer(self):
        return (
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'curl'},
        )

    def _event_lines_simple_phone_removed(self):
        return (
            {'name': 'action', 'value': 'simple_phone_remove'},
            {'name': 'phone.%d.action' % TEST_PHONE_ID, 'value': 'deleted'},
            {'name': 'phone.%d.number' % TEST_PHONE_ID, 'value': '+79261234567'},
            {'name': 'phone.%d.operation.1.type' % TEST_PHONE_ID, 'value': 'mark'},
            {'name': 'phone.%d.operation.1.action' % TEST_PHONE_ID, 'value': 'deleted'},
            {'name': 'phone.%d.operation.1.security_identity' % TEST_PHONE_ID, 'value': '79261234567'},
        )


class PhoneManageSimpleTestCase(PhoneManageBaseTestCase):
    base_request_args = {
        'phone_id': TEST_PHONE_ID,
        'display_language': TEST_DISPLAY_LANGUAGE,
    }

    def setUp(self):
        super(PhoneManageSimpleTestCase, self).setUp()
        self.phones = {
            TEST_PHONE_ID: {
                'id': TEST_PHONE_ID,
                'number': TEST_PHONE_NUMBER.e164,
                'created': TEST_PHONE_CREATED_DT,
                'bound': TEST_PHONE_BOUND_DT,
            },
            TEST_PHONE_ID2: {
                'id': TEST_PHONE_ID2,
                'number': TEST_OTHER_EXIST_PHONE_NUMBER.e164,
                'created': TEST_PHONE_CREATED_DT,
                'bound': TEST_PHONE_BOUND_DT,
                'confirmed': TEST_PHONE_CONFIRMED_DT,
            },
        }

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE):
        bb_kwargs = {
            'phones': self.phones.values(),
            'attributes': {
                'phones.default': str(TEST_PHONE_ID2),
            },
        }
        bb_response = blackbox_sessionid_multi_response(
            **bb_kwargs
        )
        self.env.blackbox.set_response_value(
            'sessionid',
            bb_response,
        )
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
                **bb_kwargs
            ),
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                **bb_kwargs
            ),
        )
        self.env.db.serialize_sessionid(bb_response)

    def assert_ok_response(self, response, **kwargs):
        eq_(json.loads(response.data)['status'], 'ok')
        eq_(response.status_code, 200)

    def _event_lines_action_consumer(self):
        return (
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'curl'},
        )

    def _test_missing_params_error(self):
        self.set_blackbox_response()
        resp = self.make_request(
            data={
                'display_language': '',
            },
        )

        self.assert_error_response(
            resp,
            [
                'phone_id.empty',
                'display_language.empty',
            ],
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.env.statbox.assert_has_written([])

    def _test_phone_not_found_error(self):
        self.set_blackbox_response()
        resp = self.make_request(
            data={
                'phone_id': 123,
                'display_language': 'ru',
            },
        )

        self.assert_error_response(
            resp,
            ['phone.not_found'],
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_statbox_ok(error=True, with_check_cookies=True)

    def assert_statbox_ok(self, error=False, with_check_cookies=False):
        entries = [self.env.statbox.entry('submitted', _exclude=['mode', 'track_id'])]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('completed', _exclude=['mode', 'track_id', 'operation_id']))
        if error:
            entries.pop()

        self.env.statbox.assert_has_written(entries)


@with_settings_hosts()
class TestProlongValidPhone(PhoneManageSimpleTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/prolong_valid/'
    step = 'prolong_valid'

    def _test_ok(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        resp = self.make_request(headers=headers)

        self.assert_ok_response(resp)
        self.check_db_phone_attr(
            'admitted',
            TimeNow(),
            phone_id=TEST_PHONE_ID,
        )
        self.check_db_phone_attr(
            'admitted',
            None,
            phone_id=TEST_PHONE_ID2,
        )
        self.assert_events_are_logged(
            self.env.handle_mock,
            self._event_lines_action_consumer() +
            self._event_lines_action_prolong_valid(),
        )
        self.assert_statbox_ok(with_check_cookies=not by_token)
        self.assert_blackbox_auth_method_ok(by_token)

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_missing_params(self):
        self._test_missing_params_error()

    def test_phone_not_found(self):
        self._test_phone_not_found_error()

    def test_not_bound(self):
        admitted_dt = datetime.now() - timedelta(weeks=52)
        admitted_ts = to_unixtime(admitted_dt)
        self.phones[TEST_PHONE_ID].update(
            bound=None,
            admitted=admitted_dt,
        )

        self.set_blackbox_response()
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['phone.not_found'],
        )
        self.check_db_phone_attr(
            'admitted',
            str(admitted_ts),
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_statbox_ok(error=True, with_check_cookies=True)

    def _event_lines_action_prolong_valid(self):
        return (
            {'name': 'action', 'value': 'prolong_valid'},
            {'name': 'phone.%d.action' % TEST_PHONE_ID, 'value': 'changed'},
            {'name': 'phone.%d.admitted' % TEST_PHONE_ID, 'value': TimeNow()},
            {'name': 'phone.%d.number' % TEST_PHONE_ID, 'value': TEST_PHONE_NUMBER.original},
        )


@with_settings_hosts()
class TestSetDefaultPhone(PhoneManageSimpleTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/set_default/'
    base_request_args = {'phone_id': TEST_PHONE_ID}
    step = 'set_default'

    def _test_ok(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        resp = self.make_request(headers=headers)

        self.assert_ok_response(resp)
        self._assert_notification_number_selected(TEST_PHONE_ID)
        self.assert_events_are_logged(
            self.env.handle_mock,
            self._event_lines_action_consumer() +
            self._event_lines_action_set_default(),
        )
        self.assert_statbox_ok(with_check_cookies=not by_token)
        self.assert_blackbox_auth_method_ok(by_token)

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_missing_params(self):
        resp = self.make_request(
            data={},
            headers=self.build_headers(),
        )
        self.assert_error_response(resp, ['phone_id.empty'])

    def test_phone_not_found(self):
        self._test_phone_not_found_error()

    def test_not_bound(self):
        self.phones[TEST_PHONE_ID].update(bound=None)
        self.set_blackbox_response()

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['phone.not_found'],
        )
        self._assert_notification_number_selected(TEST_PHONE_ID2)
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_statbox_ok(error=True, with_check_cookies=True)

    def test_by_uid__with_grant(self):
        self.set_blackbox_response()

        rv = self.make_request(
            data=merge_dicts(self.base_request_args, {'uid': TEST_UID}),
            headers=self.build_headers(),
        )

        self.assert_ok_response(rv)
        self._assert_notification_number_selected(TEST_PHONE_ID)

        userinfo_req = self.env.blackbox.requests[0]
        userinfo_req.assert_post_data_contains({
            'method': 'userinfo',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
        })
        userinfo_req.assert_contains_attributes({'phones.secure', 'phones.default'})

    def test_by_uid__without_grant(self):
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'phone_bundle': ['base']}),
        )
        self.set_blackbox_response()

        rv = self.make_request(
            data=merge_dicts(self.base_request_args, {'uid': TEST_UID}),
            headers=self.build_headers(),
        )

        self.assert_error_response(rv, ['access.denied'], status_code=403)
        self._assert_notification_number_selected(TEST_PHONE_ID2)

    def _assert_notification_number_selected(self, phone_id):
        self.env.db.check_db_attr(TEST_UID, 'phones.default', str(phone_id))

    def _event_lines_action_set_default(self):
        return (
            {'name': 'action', 'value': 'set_default'},
            {'name': 'phones.default', 'value': str(TEST_PHONE_ID)},
            {'name': 'phone.%s.number' % TEST_PHONE_ID, 'value': TEST_PHONE_NUMBER.original},
        )


class _PhonenumberAliasAsEmailTestCase(PhoneManageBaseTestCase):
    def _assert_alias_as_email_enabled(self):
        assert_account_has_phonenumber_alias(
            self.env.db,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
            enable_search=True,
        )

    def _assert_alias_as_email_disabled(self):
        assert_account_has_phonenumber_alias(
            self.env.db,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
            enable_search=False,
        )

    def _assert_no_mail_sent(self):
        eq_(self.env.mailer.messages, [])

    def _build_account(
        self,
        has_phonenumber_alias=True,
        phonenumber_alias_as_email_enabled=True,
        no_emails=False,
        has_phone=True,
    ):
        userinfo = dict(
            uid=TEST_UID1,
            firstname=TEST_FIRSTNAME1,
            aliases={'portal': TEST_LOGIN1},
        )

        if has_phonenumber_alias and has_phone:
            userinfo = deep_merge(
                userinfo,
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    is_alias=True,
                    is_enabled_search_for_alias=phonenumber_alias_as_email_enabled,
                ),
            )
        elif has_phonenumber_alias and not has_phone:
            userinfo = deep_merge(
                userinfo,
                dict(aliases={'phonenumber': TEST_PHONE_NUMBER1.digital}),
            )
        elif not has_phonenumber_alias and has_phone:
            userinfo = deep_merge(
                userinfo,
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
            )
        else:
            raise NotImplementedError()

        if not no_emails:
            userinfo = deep_merge(
                userinfo,
                dict(
                    emails=[create_native_email(TEST_LOGIN, 'yandex.ru')],
                ),
            )

        sessionid = {}

        return {'userinfo': userinfo, 'sessionid': sessionid}

    def _setup_account(self, **kwargs):
        account = self._build_account(**kwargs)

        sessionid = account['sessionid']
        userinfo = account['userinfo']

        self.env.blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_multi_response(**deep_merge(sessionid, userinfo)),
            ],
        )

        self.env.db.serialize(blackbox_userinfo_response(**userinfo))

    def _setup_account_for_uid(self, **kwargs):
        account = self._build_account(**kwargs)
        userinfo = account['userinfo']
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(**userinfo),
            ],
        )
        self.env.db.serialize(blackbox_userinfo_response(**userinfo))

    def setup_statbox_templates(self):
        super(_PhonenumberAliasAsEmailTestCase, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'submitted',
            _exclude=['mode', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'completed',
            _exclude=['mode', 'track_id', 'operation_id'],
            uid=str(TEST_UID1),
            number=TEST_PHONE_NUMBER1.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_search_enabled',
            uid=str(TEST_UID1),
            ip=TEST_USER_IP,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_search_disabled',
            _inherit_from=['phonenumber_alias_search_enabled'],
            operation='updated',
            old='1',
            new='0',
            uid=str(TEST_UID1),
            ip=TEST_USER_IP,
        )


@with_settings_hosts()
class TestEnablePhonenumberAliasAsEmail(_PhonenumberAliasAsEmailTestCase):
    base_method_path = '/1/bundle/phone/manage/enable_alias_as_email/'
    base_request_args = {'display_language': 'ru'}

    step = 'enable_phonenumber_alias_as_email'

    def _assert_enable_phonenumber_alias_as_email_response(self, rv):
        self.assert_ok_response(rv, skip=['account'])
        rv = json.loads(rv.data)
        ok_('account' in rv)

    def _assert_mail_about_alias_as_email_enabled_sent(self):
        assert_user_notified_about_alias_as_email_enabled(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_LOGIN + '@yandex.ru',
            firstname=TEST_FIRSTNAME1,
            portal_email=TEST_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER1.digital,
        )

    def test_no_display_language(self):
        data = merge_dicts(self.base_request_args, {'display_language': None})
        rv = self.make_request(data=data)

        self.assert_error_response(rv, ['display_language.empty'])

    def test_no_account_id(self):
        headers = self.build_headers(cookie=None)
        rv = self.make_request(headers=headers)

        self.assert_error_response(rv, ['request.credentials_all_missing'])

    def test_no_grants(self):
        self.env.grants.set_grants_return_value({'dev': dict()})

        rv = self.make_request()

        self._assert_access_denied_response(rv)

    def test_no_grants_to_get_account_by_uid(self):
        self.env.grants.set_grants_return_value({
            'dev': {
                'networks': ['127.0.0.1'],
                'grants': {'phone_bundle': ['base']},
            },
        })

        data = merge_dicts(self.base_request_args, {'uid': TEST_UID1})
        rv = self.make_request(data=data)

        self._assert_access_denied_response(rv)

    def test_no_alias(self):
        self._setup_account(has_phonenumber_alias=False)

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_alias.not_found'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
        ])

    def test_alias_as_email_enabled(self):
        self._setup_account()

        rv = self.make_request()

        self._assert_enable_phonenumber_alias_as_email_response(rv)
        self._assert_alias_as_email_enabled()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('completed'),
        ])

        self.env.event_logger.assert_events_are_logged({})
        self._assert_no_mail_sent()

    def test_alias_as_email_disabled(self):
        self._setup_account(phonenumber_alias_as_email_enabled=False)

        rv = self.make_request()

        self._assert_enable_phonenumber_alias_as_email_response(rv)
        self._assert_alias_as_email_enabled()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('phonenumber_alias_search_enabled'),
            self.env.statbox.entry('completed'),
        ])

        self.env.event_logger.assert_events_are_logged({
            'action': 'enable_phonenumber_alias_as_email',
            'info.phonenumber_alias_search_enabled': '1',
            'user_agent': TEST_USER_AGENT,
            'consumer': 'dev',
        })

        self._assert_mail_about_alias_as_email_enabled_sent()

    def test_uid(self):
        self._setup_account_for_uid()

        headers = self.build_headers(cookie=None)
        data = merge_dicts(self.base_request_args, {'uid': TEST_UID1})
        rv = self.make_request(headers=headers, data=data)

        self._assert_enable_phonenumber_alias_as_email_response(rv)

    def test_no_emails(self):
        self._setup_account(no_emails=True)

        rv = self.make_request()

        self._assert_enable_phonenumber_alias_as_email_response(rv)


@with_settings_hosts()
class TestDisablePhonenumberAliasAsEmail(_PhonenumberAliasAsEmailTestCase):
    base_method_path = '/1/bundle/phone/manage/disable_alias_as_email/'
    base_request_args = {'display_language': 'ru'}

    step = 'disable_phonenumber_alias_as_email'

    def _assert_disable_phonenumber_alias_as_email_response(self, rv):
        self.assert_ok_response(rv, skip=['account'])
        rv = json.loads(rv.data)
        ok_('account' in rv)

    def _assert_mail_about_alias_as_email_disabled_sent(self):
        assert_user_notified_about_alias_as_email_disabled(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_LOGIN + '@yandex.ru',
            firstname=TEST_FIRSTNAME1,
            portal_email=TEST_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER1.digital,
        )

    def test_no_display_language(self):
        data = merge_dicts(self.base_request_args, {'display_language': None})
        rv = self.make_request(data=data)

        self.assert_error_response(rv, ['display_language.empty'])

    def test_no_account_id(self):
        headers = self.build_headers(cookie=None)
        rv = self.make_request(headers=headers)

        self.assert_error_response(rv, ['request.credentials_all_missing'])

    def test_no_grants(self):
        self.env.grants.set_grants_return_value({'dev': dict()})

        rv = self.make_request()

        self._assert_access_denied_response(rv)

    def test_no_grants_to_get_account_by_uid(self):
        self.env.grants.set_grants_return_value({
            'dev': {
                'networks': ['127.0.0.1'],
                'grants': {'phone_bundle': ['base']},
            },
        })

        data = merge_dicts(self.base_request_args, {'uid': TEST_UID1})
        rv = self.make_request(data=data)

        self._assert_access_denied_response(rv)

    def test_no_alias(self):
        self._setup_account(has_phonenumber_alias=False)

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_alias.not_found'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
        ])

    def test_alias_as_email_enabled(self):
        self._setup_account()

        rv = self.make_request()

        self._assert_disable_phonenumber_alias_as_email_response(rv)
        self._assert_alias_as_email_disabled()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('phonenumber_alias_search_disabled'),
            self.env.statbox.entry('completed'),
        ])

        self.env.event_logger.assert_events_are_logged({
            'action': 'disable_phonenumber_alias_as_email',
            'info.phonenumber_alias_search_enabled': '0',
            'user_agent': TEST_USER_AGENT,
            'consumer': 'dev',
        })

        self._assert_mail_about_alias_as_email_disabled_sent()

    def test_alias_as_email_disabled(self):
        self._setup_account(phonenumber_alias_as_email_enabled=False)

        rv = self.make_request()

        self._assert_disable_phonenumber_alias_as_email_response(rv)
        self._assert_alias_as_email_disabled()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('completed'),
        ])

        self.env.event_logger.assert_events_are_logged({})
        self._assert_no_mail_sent()

    def test_uid(self):
        self._setup_account_for_uid()

        headers = self.build_headers(cookie=None)
        data = merge_dicts(self.base_request_args, {'uid': TEST_UID1})
        rv = self.make_request(headers=headers, data=data)

        self._assert_disable_phonenumber_alias_as_email_response(rv)

    def test_race_alias_exists_but_no_phone(self):
        self._setup_account(has_phone=False)

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_alias.not_found'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
        ])

    def test_alias_exists_but_no_mail_to_notify(self):
        self._setup_account(no_emails=True)

        rv = self.make_request()

        self._assert_disable_phonenumber_alias_as_email_response(rv)
        self._assert_alias_as_email_disabled()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('phonenumber_alias_search_disabled'),
            self.env.statbox.entry('completed'),
        ])

        self.env.event_logger.assert_events_are_logged({
            'action': 'disable_phonenumber_alias_as_email',
            'info.phonenumber_alias_search_enabled': '0',
            'user_agent': TEST_USER_AGENT,
            'consumer': 'dev',
        })
        self._assert_no_mail_sent()
