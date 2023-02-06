# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import eq_
from passport.backend.api.yasms import exceptions
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_phone_bindings_response
from passport.backend.core.env import Environment
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_being_bound,
    assert_secure_phone_bound,
    assert_simple_phone_bound,
    build_account,
    build_phone_being_bound,
    build_phone_being_bound_replaces_secure_operations,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_secure_phone_being_bound,
)
from passport.backend.core.models.phones.phones import OperationExpired
from passport.backend.core.runner.context_managers import UPDATE
from passport.backend.core.test.consts import TEST_PASSWORD_HASH1
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.yasms.test.emails import assert_user_notified_about_secure_phone_bound
from passport.backend.utils.common import deep_merge

from .base import BaseYasmsTestCase


CONSUMER_IP = u'1.2.3.4'
USER_IP = u'4.3.2.1'
USER_AGENT = u'curl'
CONFIRMATION_CODE = u'3232'
CONFIRMATION_CODE_EXTRA = u'4545'
PHONE_NUMBER = PhoneNumber.parse(u'+79026411724')
NOT_EXISTENT_PHONE_NUMBER = PhoneNumber.parse(u'+79082414400')
PHONE_NUMBER_EXTRA = PhoneNumber.parse(u'+79259164525')
TEST_CODE_CHECKS_LIMIT = 2
LOGIN = u'testlogin'
UID_ALPHA = 4000
EMAIL = u'%s@yandex.ru' % LOGIN
FIRSTNAME = u'Андрей'
PHONE_ID = 3000
PHONE_ID_EXTRA = 3010
OPERATION_ID = 5000
OPERATION_ID_EXTRA = 5020
ACTION = u'testaction'
UID_BETA = 4040
TEST_DATE = datetime(2014, 4, 14, 4, 4, 4)


class TestConfirm(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        SMS_VALIDATION_MAX_CHECKS_COUNT=TEST_CODE_CHECKS_LIMIT,
        YASMS_VALIDATION_LIMIT=1,
    )

    def setUp(self):
        super(TestConfirm, self).setUp()
        self.env.statbox.bind_entry(
            u'account_phones_secure',
            _inherit_from=[u'account_modification'],
            uid=str(UID_ALPHA),
            entity=u'phones.secure',
            operation='created',
            new=PHONE_NUMBER.masked_format_for_statbox,
            new_entity_id=str(PHONE_ID),
            old=u'-',
            old_entity_id=u'-',
            ip=USER_IP,
            consumer=u'-',
        )

    def test_bind_secure_with_password(self):
        # phone_id важней phone_number
        # Можно привязать защищённый номер только когда проверен пароль
        # Обеляем учётную запись
        account = self._build_account(
            enabled=True,
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                password_verified=datetime.now(),
                code_value=CONFIRMATION_CODE,
                flags=PhoneOperationFlags(),
            )
        )
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        with UPDATE(account, Environment(user_ip=USER_IP), {u'action': ACTION}):
            response, flags = self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=NOT_EXISTENT_PHONE_NUMBER.e164,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )
        self._statbox.dump_stashes()

        self._assert_response_code_valid(response)
        eq_(flags, PhoneOperationFlags())

        self._assert_secure_phone_bound(account)
        eq_(account.karma.prefix, 6)
        self.env.db.check(u'attributes', u'karma.value', u'6000', uid=UID_ALPHA, db=u'passportdbshard1')

        self._assert_bindings_history_asked_from_blackbox()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('account_phones_secure'),
            self._statbox_line_karma_changed(),
            self._statbox_line_code_confirmed(code_checks_count=u'1'),
            self._statbox_line_secure_phone_bound(),
        ])

        fmt = (PHONE_ID, OPERATION_ID)
        self.env.event_logger.assert_events_are_logged({
            u'action': ACTION,
            u'phone.%d.action' % PHONE_ID: u'changed',
            u'phone.%d.number' % PHONE_ID: PHONE_NUMBER.e164,
            u'phone.%d.bound' % PHONE_ID: TimeNow(),
            u'phone.%d.confirmed' % PHONE_ID: TimeNow(),
            u'phone.%d.secured' % PHONE_ID: TimeNow(),
            u'phone.%d.operation.%d.action' % fmt: u'deleted',
            u'phone.%d.operation.%d.type' % fmt: u'bind',
            u'phone.%d.operation.%d.security_identity' % fmt: u'1',
            u'phones.secure': str(PHONE_ID),
            u'info.karma_prefix': u'6',
            u'info.karma_full': u'6000',
        })

    def test_bind_secure_without_password(self):
        account = self._build_account(
            enabled=True,
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                password_verified=None,
                code_value=CONFIRMATION_CODE,
                flags=PhoneOperationFlags(),
            )
        )

        with self.assertRaises(exceptions.YaSmsImpossibleConfirm):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])

    def test_bind_to_disabled_account(self):
        # Можно привязать телефон к заблокированной учётной записи
        # Последняя попытка проверить код
        # Не считать данную связь, когда стоит флажок should_ignore_binding_limit

        flags = PhoneOperationFlags()
        flags.should_ignore_binding_limit = True
        account = self._build_account(
            enabled=False,
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                code_value=CONFIRMATION_CODE,
                code_checks_count=TEST_CODE_CHECKS_LIMIT - 1,
                flags=flags,
            )
        )
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'type': u'history',
                    u'number': PHONE_NUMBER.e164,
                    u'phone_id': PHONE_ID,
                    u'uid': UID_BETA,
                    u'bound': TEST_DATE,
                },
            ]),
        )

        with UPDATE(account, Environment(user_ip=USER_IP), {u'action': ACTION}):
            response, flags = self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=PHONE_NUMBER.e164,
                phone_id=None,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )
        self._statbox.dump_stashes()

        self._assert_response_code_valid(response)

        expected_flags = PhoneOperationFlags()
        expected_flags.should_ignore_binding_limit = True
        eq_(flags, expected_flags)

        expected_phone = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER.e164,
            u'bound': DatetimeNow(),
            u'confirmed': DatetimeNow(),
        }
        assert_simple_phone_bound(account, expected_phone)
        assert_simple_phone_bound.check_db(self.env.db, UID_ALPHA, expected_phone)

        eq_(account.karma.prefix, 6)
        self.env.db.check(u'attributes', u'karma.value', u'6000', uid=UID_ALPHA, db=u'passportdbshard1')

        self._assert_bindings_history_asked_from_blackbox()

        self.env.statbox.assert_has_written([
            self._statbox_line_karma_changed(),
            self._statbox_line_code_confirmed(code_checks_count=u'2'),
            self.env.statbox.entry(
                u'base',
                action=u'confirm.simple_phone_bound',
                phone_id=str(PHONE_ID),
                number=PHONE_NUMBER.masked_format_for_statbox,
                operation_id=str(OPERATION_ID),
                uid=str(UID_ALPHA),
            ),
        ])

        fmt = (PHONE_ID, OPERATION_ID)
        self.env.event_logger.assert_events_are_logged({
            u'action': ACTION,
            u'phone.%d.action' % PHONE_ID: u'changed',
            u'phone.%d.number' % PHONE_ID: PHONE_NUMBER.e164,
            u'phone.%d.bound' % PHONE_ID: TimeNow(),
            u'phone.%d.confirmed' % PHONE_ID: TimeNow(),
            u'phone.%d.operation.%d.action' % fmt: u'deleted',
            u'phone.%d.operation.%d.type' % fmt: u'bind',
            u'phone.%d.operation.%d.security_identity' % fmt: PHONE_NUMBER.digital,
            u'info.karma_prefix': u'6',
            u'info.karma_full': u'6000',
        })

    def test_dont_wash_account(self):
        # Не обелять учётную записи, когда число привязок превысило лимит

        account = self._build_account(
            enabled=True,
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                password_verified=TEST_DATE,
                code_value=CONFIRMATION_CODE,
                flags=PhoneOperationFlags(),
            )
        )
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'type': u'history',
                    u'number': PHONE_NUMBER.e164,
                    u'phone_id': PHONE_ID,
                    u'uid': UID_BETA,
                    u'bound': TEST_DATE,
                },
            ]),
        )

        with UPDATE(account, Environment(user_ip=USER_IP), {u'action': ACTION}):
            response, flags = self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=None,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )
        self._statbox.dump_stashes()

        self._assert_response_code_valid(response)
        eq_(flags, PhoneOperationFlags())

        self._assert_secure_phone_bound(account)
        eq_(account.karma.prefix, 0)
        self.env.db.check_missing(u'attributes', u'karma.value', uid=UID_ALPHA, db=u'passportdbshard1')

        self._assert_bindings_history_asked_from_blackbox()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('account_phones_secure'),
            self._statbox_line_code_confirmed(code_checks_count=u'1'),
            self._statbox_line_secure_phone_bound(),
        ])

        fmt = (PHONE_ID, OPERATION_ID)
        self.env.event_logger.assert_events_are_logged({
            u'action': ACTION,
            u'phone.%d.action' % PHONE_ID: u'changed',
            u'phone.%d.number' % PHONE_ID: PHONE_NUMBER.e164,
            u'phone.%d.bound' % PHONE_ID: TimeNow(),
            u'phone.%d.confirmed' % PHONE_ID: TimeNow(),
            u'phone.%d.secured' % PHONE_ID: TimeNow(),
            u'phone.%d.operation.%d.action' % fmt: u'deleted',
            u'phone.%d.operation.%d.type' % fmt: u'bind',
            u'phone.%d.operation.%d.security_identity' % fmt: u'1',
            u'phones.secure': str(PHONE_ID),
        })

    def test_wrong_code(self):
        account = self._build_account(
            enabled=True,
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                code_value=CONFIRMATION_CODE,
            )
        )

        with UPDATE(account, Environment(user_ip=USER_IP), {u'action': ACTION}):
            response, _ = self._yasms.confirm(
                account,
                CONFIRMATION_CODE_EXTRA,
                phone_number=None,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )
        self._statbox.dump_stashes()

        eq_(
            response,
            {
                u'id': PHONE_ID,
                u'phone_number': PHONE_NUMBER.e164,
                u'uid': UID_ALPHA,
                u'is_valid': False,
                u'is_current': False,
                u'code_checks_left': TEST_CODE_CHECKS_LIMIT - 1,
            },
        )

        args = (
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER.e164,
                u'confirmed': None,
            },
            {
                u'id': OPERATION_ID,
                u'code_value': CONFIRMATION_CODE,
                u'code_checks_count': 1,
            },
        )
        assert_secure_phone_being_bound(account, *args)
        assert_secure_phone_being_bound.check_db(self.env.db, UID_ALPHA, *args)

        eq_(self.env.blackbox.requests, [])
        eq_(self.env.yasms.requests, [])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'base',
                action=u'confirm.confirm_phone',
                phone_id=str(PHONE_ID),
                number=PHONE_NUMBER.masked_format_for_statbox,
                error=u'code.invalid',
                code_checks_count=u'1',
                operation_id=str(OPERATION_ID),
                uid=str(UID_ALPHA),
            ),
        ])

        self.env.event_logger.assert_events_are_logged({})

    def test_pseudo_e164_phone_number(self):
        account = self._build_account(enabled=True)

        with self.assertRaises(exceptions.YaSmsImpossibleConfirm):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=u'+0953123456',
                phone_id=None,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])

    def test_no_phone_argument(self):
        account = self._build_account(enabled=True)

        with self.assertRaises(exceptions.YaSmsValueError):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=None,
                phone_id=None,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])

    def test_account_has_no_phone(self):
        account = self._build_account(enabled=True)

        with self.assertRaises(exceptions.YaSmsImpossibleConfirm):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=None,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])

    def test_phone_bound(self):
        account = self._build_account(
            enabled=True,
            **build_phone_bound(PHONE_ID, PHONE_NUMBER.e164)
        )

        with self.assertRaises(exceptions.YaSmsImpossibleConfirm):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=None,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])
        eq_(len(self.env.mailer.messages), 0)

    def test_no_operation(self):
        account = self._build_account(
            enabled=True,
            **build_phone_unbound(PHONE_ID, PHONE_NUMBER.e164)
        )

        with self.assertRaises(exceptions.YaSmsImpossibleConfirm):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=None,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])

    def test_wrong_operation(self):
        account = self._build_account(
            enabled=True,
            **deep_merge(
                build_phone_unbound(PHONE_ID, PHONE_NUMBER.e164),
                build_phone_secured(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA.e164),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    being_bound_operation_id=OPERATION_ID,
                    being_bound_phone_id=PHONE_ID,
                    being_bound_phone_number=PHONE_NUMBER.e164,
                    being_bound_code_value=CONFIRMATION_CODE,
                ),
            )
        )

        with self.assertRaises(exceptions.YaSmsImpossibleConfirm):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=None,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])

    def test_phone_confirmed(self):
        account = self._build_account(
            enabled=True,
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                code_value=CONFIRMATION_CODE,
                code_confirmed=datetime.now(),
            )
        )

        with self.assertRaises(exceptions.YaSmsImpossibleConfirm):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=None,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])

    def test_operation_expired(self):
        account = self._build_account(
            enabled=True,
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                code_value=CONFIRMATION_CODE,
                operation_started=datetime.now(),
                operation_finished=datetime.now(),
            )
        )

        with self.assertRaises(OperationExpired):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=None,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])

    def test_hit_code_checks_limit(self):
        account = self._build_account(
            enabled=True,
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                code_value=CONFIRMATION_CODE,
                code_checks_count=TEST_CODE_CHECKS_LIMIT,
            )
        )

        with self.assertRaises(exceptions.YaSmsCodeLimitError):
            self._yasms.confirm(
                account,
                CONFIRMATION_CODE,
                phone_number=None,
                phone_id=PHONE_ID,
                statbox=self._statbox,
                user_ip=USER_IP,
                user_agent=USER_AGENT,
            )

        self.env.statbox.assert_has_written([])

    def _build_account(self, **kwargs):
        kwargs.setdefault(
            u'emails',
            [
                self.env.email_toolkit.create_native_email(
                    login=EMAIL.split(u'@')[0],
                    domain=EMAIL.split(u'@')[1],
                ),
            ],
        )
        kwargs.setdefault('crypt_password', TEST_PASSWORD_HASH1)
        return build_account(
            db_faker=self.env.db,
            uid=UID_ALPHA,
            login=LOGIN,
            firstname=FIRSTNAME,
            **kwargs
        )

    def _assert_response_code_valid(self, response):
        eq_(
            response,
            {
                u'id': PHONE_ID,
                u'phone_number': PHONE_NUMBER.e164,
                u'uid': UID_ALPHA,
                u'is_valid': True,
                u'is_current': True,
                u'code_checks_left': None,
            },
        )

    def _statbox_line_karma_changed(self, **kwargs):
        return self.env.statbox.entry(
            u'frodo_karma',
            action=ACTION,
            uid=str(UID_ALPHA),
            login=LOGIN,
            old=u'0',
            new=u'6000',
            registration_datetime=u'-',
            consumer=u'-',
            ip=USER_IP,
            user_agent=u'-',
            **kwargs
        )

    def _statbox_line_code_confirmed(self, **kwargs):
        return self.env.statbox.entry(
            u'base',
            action=u'confirm.phone_confirmed',
            phone_id=str(PHONE_ID),
            number=PHONE_NUMBER.masked_format_for_statbox,
            confirmation_time=DatetimeNow(convert_to_datetime=True),
            operation_id=str(OPERATION_ID),
            uid=str(UID_ALPHA),
            **kwargs
        )

    def _assert_bindings_history_asked_from_blackbox(self):
        self.env.blackbox.requests[0].assert_query_contains({
            u'method': u'phone_bindings',
            u'numbers': PHONE_NUMBER.e164,
            u'type': u'history',
        })

    def _assert_secure_phone_bound(self, account):
        expected_phone = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER.e164,
            u'bound': DatetimeNow(),
            u'confirmed': DatetimeNow(),
            u'secured': DatetimeNow(),
        }
        assert_secure_phone_bound(account, expected_phone)
        assert_secure_phone_bound.check_db(self.env.db, UID_ALPHA, expected_phone)
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language=u'ru',
            email_address=EMAIL,
            firstname=FIRSTNAME,
            login=LOGIN,
        )

    def _statbox_line_secure_phone_bound(self, **kwargs):
        return self.env.statbox.entry(
            u'base',
            action=u'confirm.secure_phone_bound',
            phone_id=str(PHONE_ID),
            number=PHONE_NUMBER.masked_format_for_statbox,
            operation_id=str(OPERATION_ID),
            uid=str(UID_ALPHA),
            **kwargs
        )
