# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.api.yasms import exceptions
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_phone_bindings_response
from passport.backend.core.builders.yasms.faker import (
    yasms_error_xml_response,
    yasms_send_sms_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.env.env import Environment
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_being_bound,
    assert_secure_phone_being_removed,
    assert_secure_phone_being_replaced,
    assert_secure_phone_bound,
    assert_simple_phone_being_bound,
    assert_simple_phone_being_bound_replace_secure,
    assert_simple_phone_being_securified,
    assert_simple_phone_bound,
    assert_simple_phone_replace_secure,
    build_account,
    build_phone_being_bound,
    build_phone_being_bound_replaces_secure_operations,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_remove_operation,
    build_secure_phone_being_bound,
    build_securify_operation,
    build_simple_replaces_secure_operations,
)
from passport.backend.core.models.phones.phones import OperationExpired
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.yasms.test import sms as sms_notifications
from passport.backend.core.yasms.test.emails import (
    assert_user_notified_about_secure_phone_bound,
    assert_user_notified_about_secure_phone_replaced,
    assert_user_notified_about_secure_phone_replacement_started,
)
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime

from .base import BaseYasmsTestCase


UID = 1
PHONE_ID_EXTRA = 101
PHONE_NUMBER_EXTRA = u'+79019988777'
OPERATION_ID_EXTRA = 10177
PHONE_ID_SUBJECT = 220
PHONE_ID_SUBJECT_EXPIRED = 221
PHONE_NUMBER_SUBJECT = u'+79027766555'
OPERATION_ID_SUBJECT = 20288
TEST_DATE = datetime(2012, 2, 1, 10, 20, 30)
PAST_DATE = datetime(2012, 2, 1, 10, 20, 30)
USER_IP = u'1.2.3.4'
USER_AGENT = u'curl'
CONSUMER = u'quad'
FIRSTNAME = u'Андрей'
LOGIN = u'andrey1931'
EMAIL = u'%s@yandex-team.ru' % LOGIN

NEW_CODE = u'3232'
OLD_CODE = u'9449'

CODE_PER_IP_LIMIT = 2
MAX_CODE_CHECKS_COUNT = 2


class BaseRegisterTestCaseOldYasmsAndBlackbox(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        SMS_VALIDATION_RESEND_TIMEOUT=5,
        SMS_VALIDATION_MAX_CHECKS_COUNT=MAX_CODE_CHECKS_COUNT,
        **mock_counters(
            PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 30, CODE_PER_IP_LIMIT),
            UNTRUSTED_PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 30, CODE_PER_IP_LIMIT),
        )
    )

    def setUp(self):
        super(BaseRegisterTestCaseOldYasmsAndBlackbox, self).setUp()
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        self.env.code_generator.set_return_value(NEW_CODE)
        self._phone_id_generator_faker.set_list([PHONE_ID_SUBJECT])

        self.env.statbox.bind_base(
            ip=u'5.2.7.1',
        )
        self.env.statbox.bind_entry(
            'send_confirmation_code',
            uid=str(UID),
            number=u'+79027******',
            action=u'register.send_confirmation_code',
            error=u'sms_limit.exceeded',
        )
        self.env.statbox.bind_entry(
            'phone_operation_created',
            uid=str(UID),
            action=u'register.phone_operation_created',
            operation_type=u'simple_bind',
            number=u'+79027******',
            phone_id=str(PHONE_ID_SUBJECT),
        )

    def _build_args(self, **kwargs):
        kwargs.setdefault(u'phone_number', PHONE_NUMBER_SUBJECT)
        kwargs.setdefault(u'user_ip', USER_IP)
        kwargs.setdefault(u'user_agent', USER_AGENT)
        kwargs.setdefault(u'statbox', self._statbox)
        kwargs.setdefault(u'consumer', CONSUMER)
        return kwargs

    def _build_account(self, **kwargs):
        kwargs.setdefault(u'uid', UID)
        kwargs.setdefault(u'firstname', FIRSTNAME)
        kwargs.setdefault(u'login', LOGIN)
        kwargs.setdefault(u'language', u'ru')
        # Есть пароль
        kwargs.setdefault(u'attributes', {})
        kwargs[u'attributes'].setdefault(u'password.encrypted', u'1:password')
        kwargs.setdefault(
            u'emails',
            [
                self.env.email_toolkit.create_native_email(
                    login=EMAIL.split(u'@')[0],
                    domain=EMAIL.split(u'@')[1],
                ),
            ],
        )
        return build_account(**kwargs)

    @staticmethod
    def _build_env():
        return Environment(user_ip=USER_IP)

    def _assert_english_confirmation_code_sent(self, code):
        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            u'phone': PHONE_NUMBER_SUBJECT,
            u'text': u'Your confirmation code is {{code}}. '
                     u'Please enter it in the text field.',
        })
        requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "%s"}' % code,
        })

    def _assert_russian_confirmation_code_sent(self, code):
        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            u'phone': PHONE_NUMBER_SUBJECT,
            u'text': u'Ваш код подтверждения: {{code}}. '
                     u'Наберите его в поле ввода.',
        })
        requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "%s"}' % code,
        })

    def _assert_confirmation_code_sent(self, code):
        self._assert_russian_confirmation_code_sent(code)

    def _assert_confirmation_code_not_sent(self):
        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        for request in requests:
            query = request.get_query_params()
            ok_(u'Ваш код подтверждения' not in query[u'text'][0])
            ok_(u'Your confirmation code is' not in query[u'text'][0])

    def _assert_response_ok(self, response):
        eq_(
            response,
            {
                u'id': PHONE_ID_SUBJECT,
                u'number': PHONE_NUMBER_SUBJECT,
                u'uid': UID,
                u'is_revalidated': False,
            },
        )

    def _assert_notification_not_sent(self):
        eq_(len(self.env.mailer.messages), 0)

    def _assert_notification_sent(self):
        self._assert_russian_notification_sent()

    def _assert_russian_notification_sent(self):
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=EMAIL,
            firstname=FIRSTNAME,
            login=LOGIN,
        )

    def _assert_english_notification_sent(self):
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language='en',
            email_address=EMAIL,
            firstname=FIRSTNAME,
            login=LOGIN,
        )

    def _assert_user_notified_about_secure_phone_replaced(self, language=u'ru'):
        assert_user_notified_about_secure_phone_replaced(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=EMAIL,
            firstname=FIRSTNAME,
            login=LOGIN,
        )

    def _assert_user_notified_about_secure_phone_replacement_started(self, language=u'ru'):
        assert_user_notified_about_secure_phone_replacement_started(
            mailer_faker=self.env.mailer,
            language=language,
            email_address=EMAIL,
            firstname=FIRSTNAME,
            login=LOGIN,
        )
        sms_notifications.assert_user_notified_about_secure_phone_replacement_started(
            yasms_builder_faker=self.env.yasms,
            language=language,
            phone_number=PhoneNumber.parse(PHONE_NUMBER_EXTRA),
            uid=UID,
        )

    def _assert_operation_not_exist(self, account, operation_id):
        ok_(
            not account.phones.by_operation_id(operation_id),
            u'Операция %s должна быть удалена' % (operation_id,),
        )

    def _assert_phone_not_exist(self, account, phone_id):
        ok_(
            not account.phones.has_id(phone_id),
            u'Телефон %s должен быть удалён' % (phone_id,),
        )

    def _assert_account_washed(self, account):
        eq_(account.karma.prefix, settings.KARMA_PREFIX_WASHED)

    def _assert_account_not_washed(self, account):
        eq_(account.karma.prefix, 0)


class TestRegisterNoPhones(BaseRegisterTestCaseOldYasmsAndBlackbox):
    # Нет телефонов

    def test_no_phone__bind_simple_phone__ok(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()

    def test_no_phone__bind_secure_phone__ok(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

        self._assert_response_ok(response)
        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()


class TestRegisterSimplePhoneBeingBound(BaseRegisterTestCaseOldYasmsAndBlackbox):
    # Нет телефонов
    # Привязывается простой телефон
    # Других телефонов нет

    def test_phone_being_bound__bind_simple_phone__ok(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
            )
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            # Операция осталась прежней
            {u'id': OPERATION_ID_SUBJECT},
        )
        self._assert_confirmation_code_sent(OLD_CODE)
        self._assert_notification_not_sent()

    def test_phone_being_bound__bind_secure_phone__ok(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

        self._assert_response_ok(response)
        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_operation_not_exist(account, OPERATION_ID_SUBJECT)
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()

    def test_extra_being_bound__no_subject__bind_simple_subject__ok(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_EXTRA,
                PHONE_NUMBER_EXTRA,
                OPERATION_ID_EXTRA,
                code_value=OLD_CODE,
            )
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {u'id': OPERATION_ID_EXTRA},
        )

    def test_extra_being_bound__no_subject__bind_secure_subject__ok(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_EXTRA,
                PHONE_NUMBER_EXTRA,
                OPERATION_ID_EXTRA,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

        self._assert_response_ok(response)

        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {u'id': OPERATION_ID_EXTRA},
        )

    @raises(OperationExpired)
    def test_phone_being_bound_expired__bind_simple_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT_EXPIRED,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
                operation_started=PAST_DATE - timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                operation_finished=PAST_DATE,
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(OperationExpired)
    def test_phone_being_bound_expired__bind_secure_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT_EXPIRED,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
                operation_started=PAST_DATE - timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                operation_finished=PAST_DATE,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))


class TestRegisterSimpleBound(BaseRegisterTestCaseOldYasmsAndBlackbox):
    # Привязан простой телефон
    # Других телефонов нет

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_simple_phone_bound__bind_simple_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **build_phone_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                is_default=True,
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_simple_phone_bound__bind_secure_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **build_phone_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                is_default=True,
            )
        )

        self._yasms.register(**self._build_args(account=account, secure=True))

    def test_simple_extra_bound__no_subject__bind_simple_subject__ok(self):
        account = self._build_account(
            uid=UID,
            **build_phone_bound(
                PHONE_ID_EXTRA,
                PHONE_NUMBER_EXTRA,
                is_default=True,
            )
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()
        assert_simple_phone_bound(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
        )
        eq_(account.phones.default.number.e164, PHONE_NUMBER_EXTRA)

    def test_simple_extra_bound__no_subject__bind_secure_subject__ok(self):
        account = self._build_account(
            uid=UID,
            **build_phone_bound(
                PHONE_ID_EXTRA,
                PHONE_NUMBER_EXTRA,
                is_default=True,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()
        assert_simple_phone_bound(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
        )
        eq_(account.phones.default.number.e164, PHONE_NUMBER_EXTRA)


class TestRegisterSecurePhoneBeingBound(BaseRegisterTestCaseOldYasmsAndBlackbox):
    # Привязывается защищённый телефон
    # Других телефонов нет

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_secure_phone_being_bound__bind_simple_phone__fail(self):
        # Нарушена обратная совместимость!
        # В перловом Я.Смсе операцию привязки защищённого номера было возможно
        # заменить на операцию привязки простого.
        # Выбрано исключение YaSmsSecureNumberExists, потому что оно ближе
        # остальных выражает, что отказ произошёл из-за выполнения привязки
        # защищённого номера.
        account = self._build_account(
            uid=UID,
            **build_secure_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
            )
        )

        self._yasms.register(**self._build_args(account=account))

    def test_secure_phone_being_bound__bind_secure_phone__ok(self):
        account = self._build_account(
            uid=UID,
            **build_secure_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

        self._assert_response_ok(response)
        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {u'id': OPERATION_ID_SUBJECT},
        )
        self._assert_confirmation_code_sent(OLD_CODE)
        # Т.к. код подтверждения перевыслан, уведомление уже высылалось и
        # второй раз уведомлять не нужно.
        self._assert_notification_not_sent()

    def test_secure_extra_being_bound__no_subject__bind_simple_subject__ok(self):
        account = self._build_account(
            uid=UID,
            **build_secure_phone_being_bound(
                PHONE_ID_EXTRA,
                PHONE_NUMBER_EXTRA,
                OPERATION_ID_EXTRA,
                code_value=OLD_CODE,
            )
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()
        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {u'id': OPERATION_ID_EXTRA},
        )

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_secure_extra_being_bound__no_subject__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **build_secure_phone_being_bound(
                PHONE_ID_EXTRA,
                PHONE_NUMBER_EXTRA,
                OPERATION_ID_EXTRA,
                code_value=OLD_CODE,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_secure_extra_being_bound_expired__no_subject__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **build_secure_phone_being_bound(
                PHONE_ID_EXTRA,
                PHONE_NUMBER_EXTRA,
                OPERATION_ID_EXTRA,
                code_value=OLD_CODE,
                operation_started=PAST_DATE - timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                operation_finished=PAST_DATE,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))


class TestRegisterSecurePhoneBound(BaseRegisterTestCaseOldYasmsAndBlackbox):
    # Привязан защищённый телефон
    # Других телефонов нет

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_secure_phone_bound__bind_simple_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **build_phone_secured(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                is_default=True,
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_secure_phone_bound__bind_secure_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **build_phone_secured(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                is_default=True,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    def test_secure_extra_bound__no_subject__bind_simple_subject__ok(self):
        account = self._build_account(
            uid=UID,
            **build_phone_secured(
                PHONE_ID_EXTRA,
                PHONE_NUMBER_EXTRA,
                is_default=True,
            )
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()
        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
        )
        eq_(account.phones.default.number.e164, PHONE_NUMBER_EXTRA)

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_secure_extra_bound__no_subject__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **build_phone_secured(
                PHONE_ID_EXTRA,
                PHONE_NUMBER_EXTRA,
                is_default=True,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))


class TestRegisterSimplePhoneBeingSecurified(BaseRegisterTestCaseOldYasmsAndBlackbox):
    # Телефон простой и защищается
    # Других телефонов нет

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_phone_being_securified__bind_simple_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_securify_operation(
                    OPERATION_ID_SUBJECT,
                    PHONE_ID_SUBJECT,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(OperationExpired)
    def test_phone_being_securified_expired_inapplicable__bind_simple_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_securify_operation(
                    OPERATION_ID_SUBJECT,
                    PHONE_ID_SUBJECT,
                    started=PAST_DATE - timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                    finished=PAST_DATE,
                    password_verified=PAST_DATE,
                    code_confirmed=None,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_phone_being_securified__bind_secure_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_securify_operation(
                    OPERATION_ID_SUBJECT,
                    PHONE_ID_SUBJECT,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    def test_extra_being_securified__no_subject__bind_simple_subject__ok(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_securify_operation(
                    OPERATION_ID_EXTRA,
                    PHONE_ID_EXTRA,
                    code_value=OLD_CODE,
                ),
            )
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()
        assert_simple_phone_being_securified(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {u'id': OPERATION_ID_EXTRA},
        )
        eq_(account.phones.default.number.e164, PHONE_NUMBER_EXTRA)

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_extra_being_securified__no_subject__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_securify_operation(
                    OPERATION_ID_EXTRA,
                    PHONE_ID_EXTRA,
                    code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_extra_being_securified_expired_inapplicable__no_subject__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_securify_operation(
                    OPERATION_ID_EXTRA,
                    PHONE_ID_EXTRA,
                    code_value=OLD_CODE,
                    started=PAST_DATE - timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                    finished=PAST_DATE,
                    password_verified=PAST_DATE,
                    code_confirmed=None,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))


class TestRegisterSecurePhoneBeingRemoved(BaseRegisterTestCaseOldYasmsAndBlackbox):
    # Телефон защищён и удаляется
    # Других телефонов нет

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_secure_phone_being_removed__bind_simple_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_remove_operation(
                    OPERATION_ID_SUBJECT,
                    PHONE_ID_SUBJECT,
                    code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(OperationExpired)
    def test_secure_phone_being_removed_expired__bind_simple_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_remove_operation(
                    OPERATION_ID_SUBJECT,
                    PHONE_ID_SUBJECT,
                    code_value=OLD_CODE,
                    started=PAST_DATE - timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                    finished=PAST_DATE,
                    password_verified=None,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_secure_phone_being_removed__bind_secure_phone__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_remove_operation(
                    OPERATION_ID_SUBJECT,
                    PHONE_ID_SUBJECT,
                    code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    def test_secure_extra_being_removed__no_subject__bind_simple_subject__ok(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_remove_operation(
                    OPERATION_ID_EXTRA,
                    PHONE_ID_EXTRA,
                    code_value=OLD_CODE,
                ),
            )
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()
        assert_secure_phone_being_removed(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {u'id': OPERATION_ID_EXTRA},
        )
        eq_(account.phones.default.number.e164, PHONE_NUMBER_EXTRA)

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_secure_extra_being_removed__no_subject__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_remove_operation(
                    OPERATION_ID_EXTRA,
                    PHONE_ID_EXTRA,
                    code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))


class TestRegister(BaseRegisterTestCaseOldYasmsAndBlackbox):
    # Привязывается защищённый телефон
    # Привязывается другой простой телефон

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_secure_extra_being_bound__simple_subject_being_bound__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_being_bound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    OPERATION_ID_SUBJECT,
                    code_value=OLD_CODE,
                ),
                build_secure_phone_being_bound(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    OPERATION_ID_EXTRA,
                    code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account, secure=True))

    # Телефон простой и защищается
    # Другой телефон привязывается как простой

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_extra_being_securified__simple_subject_being_bound__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_being_bound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    OPERATION_ID_SUBJECT,
                    code_value=OLD_CODE,
                ),
                build_phone_bound(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_securify_operation(
                    OPERATION_ID_EXTRA,
                    PHONE_ID_EXTRA,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account, secure=True))

    # Привязывается защищённый телефон
    # Привязан другой простой телефон

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_secure_extra_being_bound__simple_subject_bound__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_secure_phone_being_bound(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    OPERATION_ID_EXTRA,
                    code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    # Телефон простой и заменяет другой
    # Другой защищён и заменяется

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_secure_extra_being_replaced__simple_subject_replacing_secured__bind_simple_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_phone_bound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                ),
                build_simple_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    simple_operation_id=OPERATION_ID_SUBJECT,
                    simple_phone_id=PHONE_ID_SUBJECT,
                    simple_phone_number=PHONE_NUMBER_SUBJECT,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_secure_extra_being_replaced__simple_subject_replacing_secured__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_phone_bound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                ),
                build_simple_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    simple_operation_id=OPERATION_ID_SUBJECT,
                    simple_phone_id=PHONE_ID_SUBJECT,
                    simple_phone_number=PHONE_NUMBER_SUBJECT,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_simple_extra_replacing_secured__secure_subject_being_replaced__bind_simple_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                ),
                build_phone_secured(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_simple_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_SUBJECT,
                    secure_phone_id=PHONE_ID_SUBJECT,
                    simple_operation_id=OPERATION_ID_EXTRA,
                    simple_phone_id=PHONE_ID_EXTRA,
                    simple_phone_number=PHONE_NUMBER_EXTRA,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_simple_extra_replacing_secured__secure_subject_being_replaced__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                ),
                build_phone_secured(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_simple_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_SUBJECT,
                    secure_phone_id=PHONE_ID_SUBJECT,
                    simple_operation_id=OPERATION_ID_EXTRA,
                    simple_phone_id=PHONE_ID_EXTRA,
                    simple_phone_number=PHONE_NUMBER_EXTRA,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    @raises(OperationExpired)
    def test_simple_extra_replacing_secured_expired_applicable__secure_subject_being_replaced__bind_simple_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_bound(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                ),
                build_phone_secured(
                    PHONE_ID_SUBJECT_EXPIRED,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_simple_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_SUBJECT,
                    secure_phone_id=PHONE_ID_SUBJECT_EXPIRED,
                    secure_code_value=OLD_CODE,
                    simple_operation_id=OPERATION_ID_EXTRA,
                    simple_phone_id=PHONE_ID_EXTRA,
                    simple_phone_number=PHONE_NUMBER_EXTRA,
                    simple_code_value=OLD_CODE,
                    started=PAST_DATE - timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                    finished=PAST_DATE,
                    password_verified=PAST_DATE,
                    simple_code_confirmed=PAST_DATE,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    # Привязывается простой телефон чтобы заменить защищённый
    # Другой защищён и заменяется

    def test_secure_extra_being_replaced__simple_subject_being_bound_replace_secured__bind_simple_subject__ok(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_phone_unbound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    phone_created=TEST_DATE,
                    phone_confirmed=TEST_DATE,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_value=OLD_CODE,
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    being_bound_code_value=OLD_CODE,
                ),
            )
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        self._assert_notification_not_sent()
        self._assert_confirmation_code_sent(OLD_CODE)
        assert_simple_phone_being_bound_replace_secure(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {u'id': OPERATION_ID_SUBJECT, u'phone_id2': PHONE_ID_EXTRA},
        )
        assert_secure_phone_being_replaced(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {u'id': OPERATION_ID_EXTRA, u'phone_id2': PHONE_ID_SUBJECT},
        )
        eq_(account.phones.default.number.e164, PHONE_NUMBER_EXTRA)
        eq_(account.phones.secure.number.e164, PHONE_NUMBER_EXTRA)

    @raises(exceptions.YaSmsSecureNumberExists)
    def test_secure_extra_being_replaced__simple_subject_being_bound_replace_secured__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                dict(phones=[dict(
                    id=PHONE_ID_SUBJECT,
                    number=PHONE_NUMBER_SUBJECT,
                    created=TEST_DATE,
                    bound=None,
                    confirmed=None,
                    secured=None,
                )]),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_value=OLD_CODE,
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    being_bound_code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_simple_extra_being_bound_replace_secured__secure_subject_being_replaced__bind_simple_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                dict(phones=[dict(
                    id=PHONE_ID_EXTRA,
                    number=PHONE_NUMBER_EXTRA,
                    created=TEST_DATE,
                    bound=None,
                    confirmed=None,
                    secured=None,
                )]),
                build_phone_secured(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_SUBJECT,
                    secure_phone_id=PHONE_ID_SUBJECT,
                    secure_code_value=OLD_CODE,
                    being_bound_operation_id=OPERATION_ID_EXTRA,
                    being_bound_phone_id=PHONE_ID_EXTRA,
                    being_bound_phone_number=PHONE_NUMBER_EXTRA,
                    being_bound_code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(exceptions.YaSmsAlreadyVerified)
    def test_simple_extra_being_bound_replace_secured__secure_subject_being_replaced__bind_secure_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                dict(phones=[dict(
                    id=PHONE_ID_EXTRA,
                    number=PHONE_NUMBER_EXTRA,
                    created=TEST_DATE,
                    bound=None,
                    confirmed=None,
                    secured=None,
                )]),
                build_phone_secured(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_SUBJECT,
                    secure_phone_id=PHONE_ID_SUBJECT,
                    secure_code_value=OLD_CODE,
                    being_bound_operation_id=OPERATION_ID_EXTRA,
                    being_bound_phone_id=PHONE_ID_EXTRA,
                    being_bound_phone_number=PHONE_NUMBER_EXTRA,
                    being_bound_code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    @raises(OperationExpired)
    def test_simple_extra_being_bound_replace_secured_expired__secure_subject_being_replaced__bind_simple_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                dict(phones=[dict(
                    id=PHONE_ID_EXTRA,
                    number=PHONE_NUMBER_EXTRA,
                    created=TEST_DATE,
                    bound=None,
                    confirmed=None,
                    secured=None,
                )]),
                build_phone_secured(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    is_default=True,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_SUBJECT,
                    secure_phone_id=PHONE_ID_SUBJECT,
                    secure_code_value=OLD_CODE,
                    being_bound_operation_id=OPERATION_ID_EXTRA,
                    being_bound_phone_id=PHONE_ID_EXTRA,
                    being_bound_phone_number=PHONE_NUMBER_EXTRA,
                    being_bound_code_value=OLD_CODE,
                    started=PAST_DATE - timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                    finished=PAST_DATE,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    @raises(OperationExpired)
    def test_secure_extra_being_replaced_expired__simple_subject_being_bound_replace_secured__bind_simple_subject__fail(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                dict(phones=[dict(
                    id=PHONE_ID_SUBJECT_EXPIRED,
                    number=PHONE_NUMBER_SUBJECT,
                    created=TEST_DATE,
                    bound=None,
                    confirmed=None,
                    secured=None,
                )]),
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_value=OLD_CODE,
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT_EXPIRED,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    being_bound_code_value=OLD_CODE,
                    started=PAST_DATE - timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                    finished=PAST_DATE,
                ),
            )
        )

        self._yasms.register(**self._build_args(account=account))

    def test_phone_unbound__bind_simple_phone(self):
        account = self._build_account(
            uid=UID,
            **build_phone_unbound(PHONE_ID_SUBJECT, PHONE_NUMBER_SUBJECT)
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()

    def test_phone_unbound__bind_secure_phone(self):
        account = self._build_account(
            uid=UID,
            **build_phone_unbound(PHONE_ID_SUBJECT, PHONE_NUMBER_SUBJECT)
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

        self._assert_response_ok(response)
        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_sent(NEW_CODE)
        self._assert_notification_not_sent()

    # Параметр without_sms

    def test_no_phone__bind_simple_phone__without_sms(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        assert_simple_phone_bound(
            account,
            {
                u'id': PHONE_ID_SUBJECT,
                u'number': PHONE_NUMBER_SUBJECT,
                u'bound': DatetimeNow(),
                u'confirmed': DatetimeNow(),
            },
        )
        self._assert_confirmation_code_not_sent()
        self._assert_notification_not_sent()

    def test_no_phone__bind_secure_phone__without_sms(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_confirmation_code_not_sent()
        self._assert_notification_sent()

    def test_phone_being_bound__bind_simple_phone__without_sms(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        assert_simple_phone_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_operation_not_exist(account, OPERATION_ID_SUBJECT)
        self._assert_confirmation_code_not_sent()
        self._assert_notification_not_sent()

    def test_phone_being_bound__bind_secure_phone__without_sms(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_operation_not_exist(account, OPERATION_ID_SUBJECT)
        self._assert_confirmation_code_not_sent()
        self._assert_notification_sent()

    def test_secure_phone_being_bound__bind_secure_phone__without_sms(self):
        account = self._build_account(
            uid=UID,
            **build_secure_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_operation_not_exist(account, OPERATION_ID_SUBJECT)
        self._assert_confirmation_code_not_sent()
        self._assert_notification_sent()

    def test_secure_extra_being_replaced__simple_subject_being_bound_replace_secured__bind_simple_subject__without_sms(self):
        started = datetime.now() - timedelta(hours=24)
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                dict(phones=[dict(
                    id=PHONE_ID_SUBJECT,
                    number=PHONE_NUMBER_SUBJECT,
                    created=TEST_DATE,
                    bound=None,
                    confirmed=None,
                    secured=None,
                )]),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_value=OLD_CODE,
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    being_bound_code_value=NEW_CODE,
                    started=started,
                ),
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        assert_simple_phone_replace_secure(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {
                u'phone_id2': PHONE_ID_EXTRA,
                u'code_value': NEW_CODE,
                u'code_confirmed': DatetimeNow(),
                u'started': started,
                u'finished': started + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
            },
        )
        self._assert_operation_not_exist(account, OPERATION_ID_SUBJECT)
        assert_secure_phone_being_replaced(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {
                u'id': OPERATION_ID_EXTRA,
                u'phone_id2': PHONE_ID_SUBJECT,
                u'code_value': OLD_CODE,
                u'code_confirmed': None,
                u'started': started,
                u'finished': started + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
            },
        )
        eq_(account.phones.default.number.e164, PHONE_NUMBER_EXTRA)
        eq_(account.phones.secure.number.e164, PHONE_NUMBER_EXTRA)
        self._assert_notification_not_sent()
        self._assert_confirmation_code_not_sent()

    def test_secure_extra_being_replaced__simple_subject_being_bound_replace_secured__bind_simple_subject__without_sms__password_verified(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                dict(phones=[dict(
                    id=PHONE_ID_SUBJECT,
                    number=PHONE_NUMBER_SUBJECT,
                    created=TEST_DATE,
                    bound=None,
                    confirmed=None,
                    secured=None,
                )]),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_confirmed=datetime.now(),
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    password_verified=datetime.now(),
                ),
            )
        )
        response = self._yasms.register(**self._build_args(
            account=account,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        self._assert_user_notified_about_secure_phone_replaced()
        self._assert_confirmation_code_not_sent()
        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
        )
        self._assert_operation_not_exist(account, OPERATION_ID_SUBJECT)
        eq_(account.phones.default.number.e164, PHONE_NUMBER_SUBJECT)
        eq_(account.phones.secure.number.e164, PHONE_NUMBER_SUBJECT)
        self._assert_phone_not_exist(account, PHONE_ID_EXTRA)
        self._assert_operation_not_exist(account, OPERATION_ID_EXTRA)

    def test_secure_extra_being_replaced__simple_subject_being_bound_replace_secured__bind_simple_subject__without_sms__password_verified__secure_not_admitted(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
                build_phone_unbound(PHONE_ID_SUBJECT, PHONE_NUMBER_SUBJECT),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_value=None,
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    password_verified=datetime.now(),
                ),
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        assert_simple_phone_replace_secure(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {
                u'code_confirmed': DatetimeNow(),
                u'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
            },
        )
        assert_secure_phone_being_replaced(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {
                u'code_value': None,
                u'code_confirmed': None,
                u'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
            },
        )
        self._assert_operation_not_exist(account, OPERATION_ID_SUBJECT)
        self._assert_user_notified_about_secure_phone_replacement_started()
        self._assert_confirmation_code_not_sent()

    def test_phone_being_bound__code_confirmed__without_sms(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_confirmed=TEST_DATE,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            without_sms=True,
        ))

        self._assert_response_ok(response)

    def test_wash_account(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        self._assert_account_washed(account)

    def test_dont_wash_account(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([{
                'type': 'history',
                'phone_id': PHONE_ID_EXTRA,
                'uid': UID,
                'number': PHONE_NUMBER_SUBJECT,
                'bound': datetime.now() - timedelta(seconds=1),
            }]),
        )

        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            without_sms=True,
        ))

        self._assert_response_ok(response)
        self._assert_account_not_washed(account)

    # Параметр timestamp

    def test_timestamp(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                phone_created=datetime.now(),
                code_value=OLD_CODE,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            without_sms=True,
            timestamp=to_unixtime(PAST_DATE),
        ))

        assert_simple_phone_bound(
            account,
            {
                u'id': PHONE_ID_SUBJECT,
                u'number': PHONE_NUMBER_SUBJECT,
                u'created': DatetimeNow(),
                u'bound': DatetimeNow(),
                u'confirmed': PAST_DATE,
            },
        )

    # На учётной записи нет пароля

    @raises(exceptions.YaSmsSecureNumberNotAllowed)
    def test_bind_secure_phone__no_password__fail(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
            attributes={'password.encrypted': ''},
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
        ))

    # Параметр ignore_bindlimit

    def test_bind_simple_phone__should_ignore_binding_limit(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            ignore_bindlimit=True,
        ))

        flags = PhoneOperationFlags()
        flags.should_ignore_binding_limit = True
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {u'flags': flags},
        )

    def test_bind_secure_phone__should_ignore_binding_limit(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            ignore_bindlimit=True,
        ))

        flags = PhoneOperationFlags()
        flags.should_ignore_binding_limit = True
        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {u'flags': flags},
        )

    def test_phone_being_bound__bind_simple_phone__should_ignore_binding_limit(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            ignore_bindlimit=True,
        ))

        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {u'flags': PhoneOperationFlags()},
        )

    def test_phone_being_bound__bind_secure_phone__should_ignore_binding_limit(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            ignore_bindlimit=True,
        ))

        flags = PhoneOperationFlags()
        flags.should_ignore_binding_limit = True
        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {u'flags': flags},
        )

    def test_secure_phone_being_bound__bind_secure_phone__should_ignore_binding_limit(self):
        account = self._build_account(
            uid=UID,
            **build_secure_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            ignore_bindlimit=True,
        ))

        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {u'flags': PhoneOperationFlags()},
        )

    def test_secure_extra_being_replaced__simple_subject_being_bound_replace_secured__bind_simple_subject__should_ignore_binding_limit(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                ),
                build_phone_unbound(
                    PHONE_ID_SUBJECT,
                    PHONE_NUMBER_SUBJECT,
                    phone_created=TEST_DATE,
                    phone_confirmed=TEST_DATE,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_value=OLD_CODE,
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    being_bound_code_value=OLD_CODE,
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            ignore_bindlimit=True,
        ))

        assert_simple_phone_being_bound_replace_secure(
            account,
            {u'id': PHONE_ID_SUBJECT, u'number': PHONE_NUMBER_SUBJECT},
            {u'flags': PhoneOperationFlags()},
        )
        assert_secure_phone_being_replaced(
            account,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {u'flags': PhoneOperationFlags()},
        )

    # Параметр revalidate

    def test_no_phone__bind_simple_phone__revalidate(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            revalidate=True,
        ))

        eq_(response[u'is_revalidated'], False)

    def test_phone_being_bound__bind_simple_phone__revalidate(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            revalidate=True,
        ))

        eq_(response[u'is_revalidated'], True)

    def test_secure_phone_being_bound__bind_secure_phone__revalidate(self):
        account = self._build_account(
            uid=UID,
            **build_secure_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            revalidate=True,
        ))

        eq_(response[u'is_revalidated'], True)

    def test_phone_being_bound__bind_simple_phone__dont_revalidate(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            revalidate=False,
        ))

        eq_(response[u'is_revalidated'], False)

    def test_phone_being_bound__bind_simple_phone__revalidate__without_sms(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
            )
        )

        response = self._yasms.register(**self._build_args(
            account=account,
            revalidate=True,
            without_sms=True,
        ))

        eq_(response[u'is_revalidated'], False)

    # Параметр language

    def test_language_not_specified(self):
        account = self._build_account(
            uid=UID,
            language=u'ru',
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            language=None,
        ))

        self._assert_notification_not_sent()
        self._assert_russian_confirmation_code_sent(NEW_CODE)

    def test_language_not_specified__without_sms__bind_secure(self):
        account = self._build_account(
            uid=UID,
            language=u'ru',
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            language=None,
            without_sms=True,
        ))

        self._assert_russian_notification_sent()
        self._assert_confirmation_code_not_sent()

    def test_language_not_specified__without_sms__replacement(self):
        account = self._build_account(
            uid=UID,
            language=u'ru',
            **deep_merge(
                build_phone_secured(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
                build_phone_unbound(PHONE_ID_SUBJECT, PHONE_NUMBER_SUBJECT),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_confirmed=datetime.now(),
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    password_verified=datetime.now(),
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            language=None,
            without_sms=True,
        ))

        self._assert_user_notified_about_secure_phone_replaced(language=u'ru')
        self._assert_confirmation_code_not_sent()

    def test_language_not_specified__without_sms__replacement_started(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
                build_phone_unbound(PHONE_ID_SUBJECT, PHONE_NUMBER_SUBJECT),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_value=None,
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    password_verified=datetime.now(),
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            language=None,
            without_sms=True,
        ))

        self._assert_user_notified_about_secure_phone_replacement_started()
        self._assert_confirmation_code_not_sent()

    def test_language_specified(self):
        account = self._build_account(
            uid=UID,
            language=u'ru',
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            language=u'en',
        ))

        self._assert_notification_not_sent()
        self._assert_english_confirmation_code_sent(NEW_CODE)

    def test_language_specified__without_sms__bind_secure(self):
        account = self._build_account(
            uid=UID,
            language=u'ru',
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            language=u'en',
            without_sms=True,
        ))

        self._assert_english_notification_sent()
        self._assert_confirmation_code_not_sent()

    def test_language_specified__without_sms__replacement(self):
        account = self._build_account(
            uid=UID,
            language=u'ru',
            **deep_merge(
                build_phone_secured(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
                build_phone_unbound(PHONE_ID_SUBJECT, PHONE_NUMBER_SUBJECT),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_confirmed=datetime.now(),
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    password_verified=datetime.now(),
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            language=u'en',
            without_sms=True,
        ))

        self._assert_user_notified_about_secure_phone_replaced(language=u'en')
        self._assert_confirmation_code_not_sent()

    def test_language_specified__without_sms__replacement_started(self):
        account = self._build_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
                build_phone_unbound(PHONE_ID_SUBJECT, PHONE_NUMBER_SUBJECT),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_value=None,
                    being_bound_operation_id=OPERATION_ID_SUBJECT,
                    being_bound_phone_id=PHONE_ID_SUBJECT,
                    being_bound_phone_number=PHONE_NUMBER_SUBJECT,
                    password_verified=datetime.now(),
                ),
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            language=u'en',
            without_sms=True,
        ))

        self._assert_user_notified_about_secure_phone_replacement_started(language=u'en')
        self._assert_confirmation_code_not_sent()

    def test_confirmation_code_send(self):
        self.env.code_generator.set_return_value(u'4721')
        account = self._build_account(
            uid=UID,
            language=u'ru',
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_SUBJECT,
            consumer=u'manyasha',
        ))

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            u'caller': u'manyasha',
            u'phone': PHONE_NUMBER_SUBJECT,
            u'text': u'Ваш код подтверждения: {{code}}. Наберите его в поле ввода.',
            u'identity': u'register.send_confirmation_code',
            u'from_uid': str(account.uid),
        })
        requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "4721"}',
        })

    # Ограничения на отправку кода

    def test_phone_number_limit__fail(self):
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_error_xml_response(u'LIMITEXCEEDED', u'LIMITEXCEEDED'),
        )
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        with self.assertRaises(exceptions.YaSmsCodeLimitError):
            self._yasms.register(**self._build_args(
                account=account,
                phone_number=u'+79027122131',
                statbox=self._statbox,
                user_ip=USER_IP,
            ))

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'send_confirmation_code',
                ip=USER_IP,
                reason='yasms_phone_limit',
            ),
        ])

    def test_uid_limit__fail(self):
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_error_xml_response(u'UIDLIMITEXCEEDED', u'UIDLIMITEXCEEDED'),
        )
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        with self.assertRaises(exceptions.YaSmsCodeLimitError):
            self._yasms.register(**self._build_args(
                account=account,
                phone_number=u'+79027122131',
                statbox=self._statbox,
                user_ip=USER_IP,
            ))

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'send_confirmation_code',
                error=u'sms_limit.exceeded',
                reason='yasms_uid_limit',
                ip=USER_IP,
            ),
        ])

    def test_phone_number_blocked_permanently__fail(self):
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_error_xml_response(u'PERMANENTBLOCK', u'PERMANENTBLOCK'),
        )
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        with self.assertRaises(exceptions.YaSmsPermanentBlock):
            self._yasms.register(**self._build_args(
                account=account,
                phone_number=u'+79027122131',
                statbox=self._statbox,
                user_ip=USER_IP,
            ))

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'send_confirmation_code',
                error=u'phone.blocked',
                ip=USER_IP,
            ),
        ])

    def test_phone_number_blocked__fail(self):
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_error_xml_response(u'PHONEBLOCKED', u'PHONEBLOCKED'),
        )
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        with self.assertRaises(exceptions.YaSmsPermanentBlock):
            self._yasms.register(**self._build_args(
                account=account,
                phone_number=u'+79027122131',
                statbox=self._statbox,
                user_ip=USER_IP,
            ))

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'send_confirmation_code',
                error=u'phone.blocked',
                ip=USER_IP,
            ),
        ])

    def test_ip_limit__fail(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )
        for _ in range(CODE_PER_IP_LIMIT):
            sms_per_ip.get_counter(USER_IP).incr(USER_IP)

        with self.assertRaises(exceptions.YaSmsCodeLimitError):
            self._yasms.register(**self._build_args(
                account=account,
                user_ip=USER_IP,
                phone_number=u'+79027122131',
                statbox=self._statbox,
            ))

        self._assert_confirmation_code_not_sent()
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'send_confirmation_code',
                error=u'sms_limit.exceeded',
                ip=USER_IP,
                reason='ip_limit',
            ),
        ])

    def test_rate_limit__fail(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            phone_number=u'+79027122131',
            statbox=self._statbox,
            user_ip=u'6.2.4.1',
        ))

        with self.assertRaises(exceptions.YaSmsTemporaryBlock):
            self._yasms.register(**self._build_args(
                account=account,
                phone_number=u'+79027122131',
                statbox=self._statbox,
                user_ip=USER_IP,
            ))

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'send_confirmation_code',
                error=u'sms_limit.exceeded',
                reason='rate_limit',
                ip=USER_IP,
            ),
        ])

    def test_change_code__hit_max_codes_check_count(self):
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_checks_count=MAX_CODE_CHECKS_COUNT,
                code_value=OLD_CODE,
            )
        )

        response = self._yasms.register(**self._build_args(account=account))

        self._assert_response_ok(response)
        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT},
            {u'code_checks_count': 0},
        )
        self._assert_confirmation_code_sent(NEW_CODE)

    def test_dont_check_limits__without_sms(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            user_ip=USER_IP,
        ))

        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_error_xml_response(u'LIMITEXCEEDED', u'LIMITEXCEEDED'),
        )
        for _ in range(CODE_PER_IP_LIMIT):
            sms_per_ip.get_counter(USER_IP).incr(USER_IP)

        response = self._yasms.register(**self._build_args(
            account=account,
            user_ip=USER_IP,
            without_sms=True,
        ))

        self._assert_response_ok(response)

    def test_update_confirmation_info(self):
        """
        Изменяются счётчки отправленных кодов.
        """
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_send_count=1,
                code_last_sent=datetime.now() - timedelta(hours=1),
            )
        )

        self._yasms.register(**self._build_args(account=account))

        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID_SUBJECT},
            {
                u'code_send_count': 2,
                u'code_last_sent': DatetimeNow(),
            },
        )

    # statbox

    def test_statbox__code_sent(self):
        account = self._build_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        self._yasms.register(**self._build_args(
            account=account,
            phone_number=u'+79027122131',
            statbox=self._statbox,
        ))

        self.env.statbox.assert_has_written([])
        self._statbox.dump_stashes()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'base',
                uid=str(UID),
                number=u'+79027******',
                action=u'register.send_confirmation_code.code_sent',
                ip=USER_IP,
                sms_count=u'1',
                sms_id=u'1',
            ),
        ])

    def test_bug__resend_old_confirmation_code(self):
        # В перловом Я.Смсе, после замены операции привязки простого номера на
        # операцию привязки защищённого номера, высылается старый код
        # подтверждения. Старым кодом невозможно подтвердить новую операцию.
        #
        # Проверим, что здесь такой ошибки не допущено.
        account = self._build_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID_SUBJECT,
                PHONE_NUMBER_SUBJECT,
                OPERATION_ID_SUBJECT,
                code_value=OLD_CODE,
            )
        )

        self._yasms.register(**self._build_args(
            account=account,
            secure=True,
            phone_number=PHONE_NUMBER_SUBJECT,
        ))

        self._assert_confirmation_code_sent(NEW_CODE)
        phone = account.phones.by_number(PHONE_NUMBER_SUBJECT)
        logical_operation = phone.get_logical_operation(statbox=None)
        confirmation_info = logical_operation.get_confirmation_info(phone.id)
        eq_(confirmation_info.code_value, NEW_CODE)
