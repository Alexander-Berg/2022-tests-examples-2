# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
from functools import partial
from itertools import product
from time import time
import unittest

from nose.tools import (
    assert_is_instance,
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.logging_utils.faker.fake_tskv_logger import StatboxLoggerFaker
from passport.backend.core.logging_utils.loggers import (
    DummyLogger,
    StatboxLogger,
)
from passport.backend.core.models.phones.faker import (
    assert_phone_marked,
    assert_secure_phone_being_aliasified,
    assert_secure_phone_being_bound,
    assert_secure_phone_being_dealiasified,
    assert_secure_phone_being_removed,
    assert_secure_phone_being_replaced,
    assert_secure_phone_bound,
    assert_simple_phone_being_bound,
    assert_simple_phone_being_bound_replace_secure,
    assert_simple_phone_being_securified,
    assert_simple_phone_bound,
    assert_simple_phone_replace_secure,
    build_account,
    build_aliasify_secure_operation,
    build_dealiasify_secure_operation,
    build_mark_operation,
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
from passport.backend.core.models.phones.phones import (
    _ConfirmationInfo,
    AliasifySecureOperation,
    BuildOperationError,
    ConfirmationLimitExceeded,
    DealiasifySecureOperation,
    MarkOperation,
    NumberBoundAlready,
    NumberNotBound,
    NumberNotSecured,
    OperationExists,
    OperationExpired,
    OperationInapplicable,
    PasswordVerifiedAlready,
    PhoneChangeSet,
    PhoneConfirmedAlready,
    PhoneDoesNotTakePartInOperation,
    RemoveSecureOperation,
    ReplaceSecurePhoneWithBoundPhoneOperation,
    ReplaceSecurePhoneWithNonboundPhoneOperation,
    SecureBindOperation,
    SecureBindToSimpleBindError,
    SecureNumberBoundAlready,
    SecurifyOperation,
    SimpleBindOperation,
    SingleSecureOperationError,
)
from passport.backend.core.test.test_utils import (
    settings_context,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.utils.common import deep_merge
import pytest


PHONE_NUMBER = u'+79010001000'
PHONE_ID = 1000
OPERATION_ID = 1010
PHONE_NUMBER_EXTRA = u'+79020002000'
PHONE_ID_EXTRA = 2000
OPERATION_ID_EXTRA = 2020

PHONE_ID_FREE = 1
TEST_PHONE_QUARANTINE_SECONDS = 5 * 60

TEST_DATE1 = datetime(2015, 1, 9, 9, 9, 1)
TEST_DATE2 = datetime(2015, 1, 9, 9, 9, 2)
CONFIRMATION_CODE1 = u'1234'
CONFIRMATION_CODE2 = u'5678'

TEST_CONFIRMATION_INFO1 = _ConfirmationInfo(
    code_value=CONFIRMATION_CODE1,
    code_confirmed=TEST_DATE1,
    code_last_sent=TEST_DATE2,
    code_checks_count=1,
    code_send_count=2,
)
TEST_CONFIRMATION_INFO2 = _ConfirmationInfo(
    code_value=CONFIRMATION_CODE2,
    code_confirmed=TEST_DATE2,
    code_last_sent=TEST_DATE1,
    code_checks_count=2,
    code_send_count=1,
)

TEST_MAX_CONFIRMATION_CODE_CHECKS = 2


def _create_simple_bind_operation(account, phone1, phone2):
    phone_id, phone_number = phone1
    phone = account.phones.create(phone_number, existing_phone_id=phone_id)
    SimpleBindOperation.create(
        phone_manager=account.phones,
        phone_id=phone_id,
        code=CONFIRMATION_CODE1,
        should_ignore_binding_limit=False,
        statbox=DummyLogger(),
    )
    return [phone]


def _create_secure_bind_operation(account, phone1, phone2):
    phone_id, phone_number = phone1
    phone = account.phones.create(phone_number, existing_phone_id=phone_id)
    SecureBindOperation.create(
        phone_manager=account.phones,
        phone_id=phone_id,
        code=CONFIRMATION_CODE1,
        should_ignore_binding_limit=False,
        statbox=DummyLogger(),
    )
    return [phone]


def _create_securify_operation(account, phone1, phone2):
    phone_id, phone_number = phone1
    phone = account.phones.create(
        phone_number,
        bound=TEST_DATE1,
        existing_phone_id=phone_id,
    )
    SecurifyOperation.create(
        phone_manager=account.phones,
        phone_id=phone_id,
        code=CONFIRMATION_CODE1,
        statbox=DummyLogger(),
    )
    return [phone]


def _create_remove_secure_operation(account, phone1, phone2):
    phone_id, phone_number = phone1
    phone = account.phones.create(
        phone_number,
        bound=TEST_DATE1,
        secured=TEST_DATE1,
        existing_phone_id=phone_id,
    )
    account.phones.secure = phone
    RemoveSecureOperation.create(
        phone_manager=account.phones,
        phone_id=phone_id,
        code=CONFIRMATION_CODE1,
        statbox=DummyLogger(),
    )
    return [phone]


def _create_mark_operation(account, phone1, phone2):
    phone_id, phone_number = phone1
    phone = account.phones.create(
        phone_number,
        bound=TEST_DATE1,
        existing_phone_id=phone_id,
    )
    MarkOperation.create(
        phone_manager=account.phones,
        phone_id=phone_id,
        code=CONFIRMATION_CODE1,
        statbox=DummyLogger(),
    )
    return [phone]


def _create_replace_secure_with_non_bound_operation(account, phone1, phone2):
    being_bound_phone_id, being_bound_phone_number = phone1
    being_bound_phone = account.phones.create(
        being_bound_phone_number,
        existing_phone_id=being_bound_phone_id,
    )
    secure_phone_id, secure_phone_number = phone2
    secure_phone = account.phones.create(
        secure_phone_number,
        bound=TEST_DATE1,
        secured=TEST_DATE1,
        existing_phone_id=secure_phone_id,
    )
    account.phones.secure = secure_phone
    ReplaceSecurePhoneWithNonboundPhoneOperation.create(
        phone_manager=account.phones,
        secure_phone_id=secure_phone_id,
        being_bound_phone_id=being_bound_phone_id,
        secure_code=CONFIRMATION_CODE1,
        being_bound_code=CONFIRMATION_CODE2,
        statbox=DummyLogger(),
    )
    return [being_bound_phone, secure_phone]


def _create_replace_secure_with_bound_operation(account, phone1, phone2):
    simple_phone_id, simple_phone_number = phone1
    simple_phone = account.phones.create(
        simple_phone_number,
        bound=TEST_DATE1,
        existing_phone_id=simple_phone_id,
    )
    secure_phone_id, secure_phone_number = phone2
    secure_phone = account.phones.create(
        secure_phone_number,
        bound=TEST_DATE1,
        secured=TEST_DATE1,
        existing_phone_id=secure_phone_id,
    )
    account.phones.secure = secure_phone
    ReplaceSecurePhoneWithBoundPhoneOperation.create(
        phone_manager=account.phones,
        secure_phone_id=secure_phone_id,
        simple_phone_id=simple_phone_id,
        secure_code=CONFIRMATION_CODE1,
        simple_code=CONFIRMATION_CODE2,
        statbox=DummyLogger(),
    )
    return [simple_phone, secure_phone]


def _create_aliasify_secure_operation(account, phone1, phone2):
    phone_id, phone_number = phone1
    phone = account.phones.create(
        phone_number,
        bound=TEST_DATE1,
        secured=TEST_DATE1,
        existing_phone_id=phone_id,
    )
    account.phones.secure = phone
    AliasifySecureOperation.create(
        phone_manager=account.phones,
        phone_id=phone_id,
        code=CONFIRMATION_CODE1,
        statbox=DummyLogger(),
    )
    return [phone]


def _create_dealiasify_secure_operation(account, phone1, phone2):
    phone_id, phone_number = phone1
    phone = account.phones.create(
        phone_number,
        bound=TEST_DATE1,
        secured=TEST_DATE1,
        existing_phone_id=phone_id,
    )
    account.phones.secure = phone
    DealiasifySecureOperation.create(
        phone_manager=account.phones,
        phone_id=phone_id,
        code=CONFIRMATION_CODE1,
        statbox=DummyLogger(),
    )
    return [phone]


OPERATIONS = [
    (_create_simple_bind_operation, SimpleBindOperation, False),
    (_create_secure_bind_operation, SecureBindOperation, True),
    (_create_securify_operation, SecurifyOperation, True),
    (_create_remove_secure_operation, RemoveSecureOperation, True),
    (_create_mark_operation, MarkOperation, False),
    (
        _create_replace_secure_with_non_bound_operation,
        ReplaceSecurePhoneWithNonboundPhoneOperation,
        True,
    ),
    (
        _create_replace_secure_with_bound_operation,
        ReplaceSecurePhoneWithBoundPhoneOperation,
        True,
    ),
    (_create_aliasify_secure_operation, AliasifySecureOperation, True),
    (_create_dealiasify_secure_operation, DealiasifySecureOperation, True),
]


@pytest.mark.parametrize(
    ('create_op1', 'expected_class1', 'is_op1_secure'),
    OPERATIONS,
)
@pytest.mark.parametrize(
    ('create_op2', 'expected_class2', 'is_op2_secure'),
    OPERATIONS,
)
def test_get_logical_operations(
    create_op1, expected_class1, is_op1_secure,
    create_op2, expected_class2, is_op2_secure
):
    if is_op1_secure and is_op2_secure:
        # На учётной записи невозможно построить 2 операции над защищённым
        # номером, не тестируем этот случай.
        return
    account = build_account(phones=[], phone_operations=[])
    phones1 = create_op1(
        account,
        phone1=(PHONE_ID, PHONE_NUMBER),
        phone2=(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
    )
    phones2 = create_op2(
        account,
        phone1=(3000, u'+79030003000'),
        phone2=(4000, u'+79040004000'),
    )

    for expected_class, phones in [
        (expected_class1, phones1),
        (expected_class2, phones2),
    ]:
        for phone in phones:
            assert_is_instance(
                phone.get_logical_operation(DummyLogger()),
                expected_class,
            )


@raises(NotImplementedError)
def test_invalid_phone_data():
    account = build_account(phones=[], phone_operations=[])
    phone1 = account.phones.create(
        number=PHONE_NUMBER,
        bound=TEST_DATE1,
        existing_phone_id=PHONE_ID,
    )
    phone2 = account.phones.create(
        number=PHONE_NUMBER_EXTRA,
        bound=TEST_DATE1,
        existing_phone_id=PHONE_ID_EXTRA,
    )
    phone1.create_operation(u'invalid', phone_id2=phone2.id)
    phone2.create_operation(u'invalid', phone_id2=phone1.id)

    phone1.get_logical_operation(DummyLogger())


class Base(object):
    _is_binding = False
    _is_secure = False
    _arg_mappings = {}

    # Исходное время жизни операции 14 дней
    _OPERATION_TTL = timedelta(hours=24 * 14)

    def setUp(self):
        super(Base, self).setUp()
        self._statbox_faker = StatboxLoggerFaker()
        self._statbox_faker.start()
        self._statbox = StatboxLogger()

    def tearDown(self):
        self._statbox_faker.stop()
        del self._statbox_faker
        super(Base, self).tearDown()

    def _build_account(self, operation=None):
        raise NotImplementedError()  # pragma: no cover

    def _create_operation(self, account):
        raise NotImplementedError()  # pragma: no cover

    def _build_operation_from_account_phone_data(self, account,
                                                 operation_id=OPERATION_ID):
        raise NotImplementedError()  # pragma: no cover

    def _build_expired_operation(self, phone_id):
        account = self._build_account(operation={
            self._arg_name(phone_id, u'finished'): datetime.now() - timedelta(seconds=1),
        })
        phone = account.phones.by_id(phone_id)
        return phone.get_logical_operation(self._statbox), phone

    def _arg_name(self, phone_id, name):
        mapping = self._arg_mappings[phone_id]
        return mapping.get(name, name)

    def _assert_data_attr_passed(self, attr, values):
        for value in values:
            account = self._build_account(operation={attr: value})
            logical_op = self._build_operation_from_account_phone_data(account)
            eq_(getattr(logical_op, attr), value)

    def test_started_data_passed(self):
        self._assert_data_attr_passed(
            attr=u'started',
            values=[TEST_DATE1],
        )

    def test_finished_data_passed(self):
        self._assert_data_attr_passed(
            attr=u'finished',
            values=[TEST_DATE1],
        )

    def test_flags_data_passed(self):
        def yield_all_operation_flags():
            all_flags_combinations = product([False, True], repeat=3)
            for should_ignore_binding_limit, aliasify, in_quarantine in all_flags_combinations:
                flags = PhoneOperationFlags()
                flags.should_ignore_binding_limit = should_ignore_binding_limit
                flags.aliasify = aliasify
                flags.in_qurantine = in_quarantine
                yield flags

        self._assert_data_attr_passed(
            attr=u'flags',
            values=yield_all_operation_flags(),
        )

    def test_is_expired(self):
        for phone_id in self._phone_ids:
            account = self._build_account(operation={
                u'finished': datetime.now() + timedelta(hours=1),
            })
            phone = account.phones.by_id(phone_id)
            logical_op = phone.get_logical_operation(self._statbox)

            ok_(not logical_op.is_expired)

            account = self._build_account(operation={
                u'finished': datetime.now() - timedelta(seconds=1),
            })
            phone = account.phones.by_id(phone_id)
            logical_op = phone.get_logical_operation(self._statbox)

            ok_(logical_op.is_expired)

    def test_expired_is_inapplicable(self):
        for phone_id in self._phone_ids:
            account = self._build_account(operation={
                u'finished': datetime.now() - timedelta(seconds=1),
            })
            phone = account.phones.by_id(phone_id)
            logical_op = phone.get_logical_operation(self._statbox)

            self.assertIsInstance(logical_op.is_inapplicable(), OperationExpired)

    def test_expired_is_inapplicable__harvester_and_no_quarantine(self):
        for phone_id in self._phone_ids:
            account = self._build_account(operation={
                u'finished': datetime.now() - timedelta(seconds=1),
            })
            phone = account.phones.by_id(phone_id)
            logical_op = phone.get_logical_operation(self._statbox)

            self.assertIsInstance(
                logical_op.is_inapplicable(is_harvester=True),
                OperationExpired,
            )

    def test_create_operation__initial_attributes(self):
        account = self._build_account()
        logical_op = self._create_operation(account=account)

        eq_(logical_op.is_binding, self._is_binding)
        eq_(logical_op.is_secure, self._is_secure)
        eq_(logical_op.id, None)
        eq_(logical_op.started, DatetimeNow())
        eq_(logical_op.finished, DatetimeNow() + self._OPERATION_TTL)
        eq_(logical_op.password_verified, None)

    def test_equality(self):
        account = self._build_account()
        for phone_id in self._phone_ids:
            phone = account.phones.by_id(phone_id)
            logical_op1 = phone.get_logical_operation(statbox=self._statbox)
            logical_op2 = phone.get_logical_operation(statbox=self._statbox)
            eq_(logical_op1, logical_op2)
        for phone_id1, phone_id2 in product(self._phone_ids, repeat=2):
            phone1 = account.phones.by_id(phone_id1)
            phone2 = account.phones.by_id(phone_id2)
            logical_op1 = phone1.get_logical_operation(statbox=self._statbox)
            logical_op2 = phone2.get_logical_operation(statbox=self._statbox)
            eq_(logical_op1, logical_op2)

    def test_apply__expired_operation__fail(self):
        for phone_id in self._phone_ids:
            expired_op, _ = self._build_expired_operation(phone_id)
            with assert_raises(OperationExpired):
                expired_op.apply()

    def test_cancel__expired_operation__fail(self):
        for phone_id in self._phone_ids:
            expired_op, _ = self._build_expired_operation(phone_id)
            with assert_raises(OperationExpired):
                expired_op.cancel()

    def test_cancel__expired_operation_and_harvester__ok(self):
        for phone_id in self._phone_ids:
            expired_op, phone = self._build_expired_operation(phone_id)
            expired_op.cancel(is_harvester=True)
            eq_(phone.get_logical_operation(None), None)

    def test_to_simple_bind__expired_operation__fail(self):
        for phone_id in self._phone_ids:
            expired_op, phone = self._build_expired_operation(phone_id)
            with assert_raises(OperationExpired):
                expired_op.to_simple_bind(phone, CONFIRMATION_CODE1)

    def test_to_secure_bind__expired_operation__fail(self):
        for phone_id in self._phone_ids:
            expired_op, phone = self._build_expired_operation(phone_id)
            with assert_raises(OperationExpired):
                expired_op.to_secure_bind(phone, CONFIRMATION_CODE1, False)

    def test_create_operation__on_phone__ok(self):
        for phone_id in self._phone_ids:
            account = self._build_account()

            logical_op = self._create_operation(account)

            phone = account.phones.by_id(phone_id)
            eq_(phone.get_logical_operation(self._statbox), logical_op)

    def test_read_expired_operation(self):
        for phone_id in self._phone_ids:
            expired_op, _ = self._build_expired_operation(phone_id)

            expired_op.is_binding
            expired_op.id
            expired_op.started
            expired_op.finished
            expired_op.flags
            expired_op.is_expired
            expired_op.is_secure
            expired_op.password_verified

    def test_phone_ids_not_empty(self):
        ok_(self._phone_ids)


class ConfirmCodeMixin(object):
    def _test_confirm_phone(self, account, phone_id, confirmation_code,
                            timestamp=None):
        phone = account.phones.by_id(phone_id)
        logical_op = phone.get_logical_operation(statbox=self._statbox)

        old_confirmation_info = logical_op.get_confirmation_info(phone_id)
        ok_(not old_confirmation_info.code_confirmed)

        with settings_context(SMS_VALIDATION_MAX_CHECKS_COUNT=TEST_MAX_CONFIRMATION_CODE_CHECKS):
            is_phone_confirmed, code_checks_left = logical_op.confirm_phone(phone_id, confirmation_code, timestamp)
        ok_(is_phone_confirmed)
        eq_(code_checks_left, TEST_MAX_CONFIRMATION_CODE_CHECKS - old_confirmation_info.code_checks_count - 1)

        confirmation_info = logical_op.get_confirmation_info(phone_id)
        expected_timestamp = timestamp or DatetimeNow()
        eq_(confirmation_info.code_confirmed, expected_timestamp)
        eq_(phone.confirmed, expected_timestamp)
        eq_(
            confirmation_info.code_checks_count,
            old_confirmation_info.code_checks_count + 1,
        )

    def test_confirm_phone__expired_operation__fail(self):
        for phone_id in self._phone_ids:
            expired_op, _ = self._build_expired_operation(phone_id)
            old_confirmation_info = expired_op.get_confirmation_info(phone_id)

            with assert_raises(OperationExpired):
                expired_op.confirm_phone(PHONE_ID_EXTRA, CONFIRMATION_CODE2)
            confirmation_info = expired_op.get_confirmation_info(phone_id)
            eq_(
                confirmation_info.code_checks_count,
                old_confirmation_info.code_checks_count,
            )

    def test_get_confirmation_info__free_phone_id__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        with assert_raises(PhoneDoesNotTakePartInOperation):
            logical_op.get_confirmation_info(PHONE_ID_FREE)

    def test_set_confirmation_info__free_phone_id__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        confirmation_info = logical_op.get_confirmation_info(PHONE_ID)
        with assert_raises(PhoneDoesNotTakePartInOperation):
            logical_op.set_confirmation_info(PHONE_ID_FREE, confirmation_info)

    def test_confirmation_data_passed_to_logical_operation(self):
        for phone_id in self._phone_ids:
            a = partial(self._arg_name, phone_id)
            account = self._build_account(operation={
                a(u'code_value'): CONFIRMATION_CODE1,
                a(u'code_confirmed'): TEST_DATE1,
                a(u'code_last_sent'): TEST_DATE2,
                a(u'code_send_count'): 13,
                a(u'code_checks_count'): 17,
            })

            logical_op = self._build_operation_from_account_phone_data(account)

            confirmation_info = logical_op.get_confirmation_info(phone_id)
            eq_(confirmation_info.code_value, CONFIRMATION_CODE1)
            eq_(confirmation_info.code_confirmed, TEST_DATE1)
            eq_(confirmation_info.code_send_count, 13)
            eq_(confirmation_info.code_checks_count, 17)
            eq_(confirmation_info.code_last_sent, TEST_DATE2)

    def test_create_operation__initial_confirmation_info(self):
        for phone_id in self._phone_ids:
            account = self._build_account()
            logical_op = self._create_operation(**{
                u'account': account,
                self._arg_name(phone_id, u'code_value'): CONFIRMATION_CODE1,
            })
            confirmation_info = logical_op.get_confirmation_info(phone_id)

            eq_(confirmation_info.code_value, CONFIRMATION_CODE1)
            eq_(confirmation_info.code_last_sent, None)
            eq_(confirmation_info.code_checks_count, 0)
            eq_(confirmation_info.code_confirmed, None)
            eq_(confirmation_info.code_send_count, 0)

    def test_set_confirmation_info(self):
        for phone_id in self._phone_ids:
            account = self._build_account()
            logical_op = self._create_operation(account=account)
            logical_op.set_confirmation_info(phone_id, TEST_CONFIRMATION_INFO1)

            changed = logical_op.get_confirmation_info(phone_id)
            changed.code_value = TEST_CONFIRMATION_INFO2.code_value
            changed.code_last_sent = TEST_CONFIRMATION_INFO2.code_last_sent
            changed.code_checks_count = TEST_CONFIRMATION_INFO2.code_checks_count
            changed.code_confirmed = TEST_CONFIRMATION_INFO2.code_confirmed
            changed.code_send_count = TEST_CONFIRMATION_INFO2.code_send_count

            confirmation_info = logical_op.get_confirmation_info(phone_id)
            eq_(confirmation_info, TEST_CONFIRMATION_INFO1)

            logical_op.set_confirmation_info(phone_id, changed)

            confirmation_info = logical_op.get_confirmation_info(phone_id)
            eq_(confirmation_info, TEST_CONFIRMATION_INFO2)

    def test_confirm_phone__with_timestamp(self):
        for phone_id in self._phone_ids:
            account = self._build_account()
            self._create_operation(**{
                u'account': account,
                self._arg_name(phone_id, u'code_value'): CONFIRMATION_CODE1,
            })

            self._test_confirm_phone(
                account,
                phone_id,
                CONFIRMATION_CODE1,
                timestamp=TEST_DATE1,
            )

    def test_confirm_phone__without_timestamp(self):
        for phone_id in self._phone_ids:
            account = self._build_account()
            self._create_operation(**{
                u'account': account,
                self._arg_name(phone_id, u'code_value'): CONFIRMATION_CODE1,
            })

            self._test_confirm_phone(account, phone_id, CONFIRMATION_CODE1)

    def test_confirm_phone__free_phone_id__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        with assert_raises(PhoneDoesNotTakePartInOperation):
            logical_op.confirm_phone(PHONE_ID_FREE, CONFIRMATION_CODE1)

    def test_confirm_phone__wrong_code__fail(self):
        for phone_id in self._phone_ids:
            account = self._build_account()
            logical_op = self._create_operation(**{
                u'account': account,
                self._arg_name(phone_id, u'code_value'): CONFIRMATION_CODE1,
            })

            old_confirmation_info = logical_op.get_confirmation_info(phone_id)
            with settings_context(SMS_VALIDATION_MAX_CHECKS_COUNT=TEST_MAX_CONFIRMATION_CODE_CHECKS):
                is_phone_confirmed, code_checks_left = logical_op.confirm_phone(phone_id, CONFIRMATION_CODE2)
            ok_(not is_phone_confirmed)
            eq_(code_checks_left, TEST_MAX_CONFIRMATION_CODE_CHECKS - 1)
            confirmation_info = logical_op.get_confirmation_info(phone_id)
            eq_(
                confirmation_info.code_checks_count,
                old_confirmation_info.code_checks_count + 1,
            )

    def test_confirm_phone__phone_confirmed__fail(self):
        for phone_id in self._phone_ids:
            account = self._build_account()
            logical_op = self._create_operation(**{
                u'account': account,
                self._arg_name(phone_id, u'code_value'): CONFIRMATION_CODE1,
            })
            old_confirmation_info = logical_op.get_confirmation_info(phone_id)

            logical_op.confirm_phone(phone_id, CONFIRMATION_CODE1)
            with assert_raises(PhoneConfirmedAlready):
                logical_op.confirm_phone(phone_id, CONFIRMATION_CODE2)
            confirmation_info = logical_op.get_confirmation_info(phone_id)
            eq_(
                confirmation_info.code_checks_count,
                old_confirmation_info.code_checks_count + 1,
            )

    def test_check_code__phone_confirmed__fail(self):
        for phone_id in self._phone_ids:
            account = self._build_account()
            logical_op = self._create_operation(**{
                u'account': account,
                self._arg_name(phone_id, u'code_value'): CONFIRMATION_CODE1,
            })
            old_confirmation_info = logical_op.get_confirmation_info(phone_id)

            logical_op.confirm_phone(phone_id, CONFIRMATION_CODE1)
            with assert_raises(PhoneConfirmedAlready):
                logical_op.check_code(phone_id, CONFIRMATION_CODE2)
            confirmation_info = logical_op.get_confirmation_info(phone_id)
            eq_(
                confirmation_info.code_checks_count,
                old_confirmation_info.code_checks_count + 1,
            )

    def test_confirm_phone__limit_exceeded__fail(self):
        for phone_id in self._phone_ids:
            a = partial(self._arg_name, phone_id)
            account = self._build_account(operation={
                a(u'code_value'): CONFIRMATION_CODE1,
                a(u'code_confirmed'): None,
                a(u'code_last_sent'): TEST_DATE2,
                a(u'code_send_count'): 1,
                a(u'code_checks_count'): TEST_MAX_CONFIRMATION_CODE_CHECKS,
            })
            logical_op = self._build_operation_from_account_phone_data(account)

            with settings_context(
                SMS_VALIDATION_MAX_CHECKS_COUNT=TEST_MAX_CONFIRMATION_CODE_CHECKS,
            ):
                with assert_raises(ConfirmationLimitExceeded):
                    logical_op.confirm_phone(phone_id, CONFIRMATION_CODE1)

    def test_set_confirmation_info__expired_operation__fail(self):
        for phone_id in self._phone_ids:
            expired_op, _ = self._build_expired_operation(phone_id)
            confirmation_info = expired_op.get_confirmation_info(phone_id)
            with assert_raises(OperationExpired):
                expired_op.set_confirmation_info(phone_id, confirmation_info)

    def test_read_expired_operation__confirmation_info(self):
        for phone_id in self._phone_ids:
            expired_op, _ = self._build_expired_operation(phone_id)
            expired_op.get_confirmation_info(phone_id)


class VerifyPasswordMixin(object):
    def test_password_verified_data_passed(self):
        self._assert_data_attr_passed(
            attr=u'password_verified',
            values=[TEST_DATE1, None],
        )

    def test_set_password_verified__expired_operation__fail(self):
        for phone_id in self._phone_ids:
            expired_op, _ = self._build_expired_operation(phone_id)
            with assert_raises(OperationExpired):
                expired_op.password_verified = TEST_DATE1

    def test_set_password_verified__twice__fail(self):
        for phone_id in self._phone_ids:
            account = self._build_account()
            logical_op = self._create_operation(account)
            logical_op.password_verified = TEST_DATE1
            with assert_raises(PasswordVerifiedAlready):
                logical_op.password_verified = TEST_DATE1


class QuarantineMixin(object):
    def test_start_quarantine(self):
        now = datetime.now()
        account = self._build_account(
            operation=dict(
                finished=now + timedelta(seconds=60),
            ),
        )
        phone = account.phones.by_id(PHONE_ID)
        logical_op = phone.get_logical_operation(self._statbox)

        ok_(not logical_op.in_quarantine)

        logical_op.start_quarantine()

        ok_(logical_op.in_quarantine)
        eq_(
            logical_op.finished,
            DatetimeNow() + timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS),
        )

    def test_start_quarantine_already_started(self):
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        phone_operation_finished = datetime.fromtimestamp(int(time())) + timedelta(hours=1)
        account = self._build_account(
            operation=dict(
                finished=phone_operation_finished,
                flags=phone_operation_flags,
            ),
        )
        phone = account.phones.by_id(PHONE_ID)
        logical_op = phone.get_logical_operation(self._statbox)

        ok_(logical_op.in_quarantine)

        logical_op.start_quarantine()

        ok_(logical_op.in_quarantine)
        eq_(logical_op.finished, phone_operation_finished)


class TestSimpleBindOperation(ConfirmCodeMixin, Base, unittest.TestCase):
    _is_secure = False
    _is_binding = True
    _phone_ids = [PHONE_ID]
    _arg_mappings = {PHONE_ID: {}}

    def test_operation_id_data_passed_to_logical_operation(self):
        account = self._build_account(operation={u'operation_id': OPERATION_ID})
        logical_op = self._build_operation_from_account_phone_data(account)
        eq_(logical_op.id, OPERATION_ID)

    def test_data_to_operation__simple_phone_being_bound__ok(self):
        # Операцию можно построить из правильно сформированных данных
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        operation = account.phones.by_id(PHONE_ID).operation
        logical_op, used = SimpleBindOperation.build_by_data(
            operation,
            account.phones,
        )

        ok_(logical_op)
        ok_(logical_op.is_binding)
        ok_(not logical_op.is_secure)
        eq_(used, {operation})

    @raises(BuildOperationError)
    def test_data_to_operation__secure_phone_being_bound__fail(self):
        # Операцию невозможно построить из данных, которые не подходят
        account = build_account(
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        self._build_operation_from_account_phone_data(account, OPERATION_ID)

    def test_create_operation__ok(self):
        account = self._build_account()

        self._create_operation(account)

        assert_simple_phone_being_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
            {u'id': None},
        )

    def test_create_operation__simple_phone_being_bound__fail(self):
        account = self._build_account()
        self._create_operation(account)
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    @raises(NumberBoundAlready)
    def test_create_operation__phone_bound__fail(self):
        account = build_account(
            **build_phone_bound(
                phone_id=PHONE_ID,
                phone_number=PHONE_NUMBER,
            )
        )
        self._create_operation(account=account)

    def test_should_ignore_binding_limit_on_created_operation(self):
        _test_should_ignore_binding_limit_on_created_operation(self)

    def test_apply__not_confirmed_phone__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account=account)

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            eq_(e.need_confirmed_phones, {account.phones.by_id(PHONE_ID)})
            ok_(not e.need_password_verification)

    def test_apply__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        next_op, _ = logical_op.apply()

        assert_is_none(next_op)
        assert_simple_phone_bound(
            account,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'bound': DatetimeNow(),
                u'confirmed': DatetimeNow(),
            },
        )

    def test_apply__timestamp__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        logical_op.apply(timestamp=TEST_DATE1)

        assert_simple_phone_bound(
            account,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'bound': TEST_DATE1,
                u'confirmed': DatetimeNow(),
            },
        )

    def test_cancel(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        logical_op.cancel()

        ok_(not account.phones.has_id(PHONE_ID))

    def test_to_simple_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.set_confirmation_info(PHONE_ID, TEST_CONFIRMATION_INFO1)
        phone = account.phones.by_id(PHONE_ID)

        next_op = logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

        eq_(logical_op, next_op)
        eq_(
            next_op.get_confirmation_info(PHONE_ID),
            TEST_CONFIRMATION_INFO1,
        )

    def test_to_secure_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
            should_ignore_binding_limit=False,
        )
        logical_op.set_confirmation_info(PHONE_ID, TEST_CONFIRMATION_INFO1)
        phone = account.phones.by_id(PHONE_ID)

        next_op = logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

        self.assertIsInstance(next_op, SecureBindOperation)
        ok_(next_op.flags.should_ignore_binding_limit)

        confirmation_info = next_op.get_confirmation_info(PHONE_ID)
        eq_(confirmation_info.code_value, CONFIRMATION_CODE2)
        eq_(confirmation_info.code_last_sent, None)
        eq_(confirmation_info.code_checks_count, 0)
        eq_(confirmation_info.code_confirmed, None)
        eq_(confirmation_info.code_send_count, 0)

    @raises(SingleSecureOperationError)
    def test_to_secure_bind__other_secure_phone_being_bound(self):
        account = build_account(
            **deep_merge(
                build_phone_unbound(PHONE_ID, PHONE_NUMBER),
                build_phone_unbound(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
            )
        )
        SecureBindOperation.create(
            phone_manager=account.phones,
            phone_id=PHONE_ID_EXTRA,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=False,
            statbox=self._statbox,
        )
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
            should_ignore_binding_limit=False,
        )
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    @raises(SecureNumberBoundAlready)
    def test_to_secure_bind__secure_phone_exists(self):
        account = build_account(
            **deep_merge(
                build_phone_unbound(PHONE_ID, PHONE_NUMBER),
                build_phone_secured(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
            )
        )
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
            should_ignore_binding_limit=False,
        )
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    def test_confirm__unconfirmed_phone(self):
        account = self._build_account(operation={'code_confirmed': None})
        phone = account.phones.by_id(PHONE_ID)
        logical_op = phone.get_logical_operation(self._statbox)

        ok_(not phone.confirmed)
        c_info = logical_op.get_confirmation_info(PHONE_ID)
        ok_(not c_info.code_confirmed)

        logical_op.confirm_phone(PHONE_ID, c_info.code_value)

        eq_(phone.confirmed, DatetimeNow())
        c_info = logical_op.get_confirmation_info(PHONE_ID)
        eq_(c_info.code_confirmed, DatetimeNow())

    def _build_account(self, operation=None):
        if operation is not None:
            operation.update({
                u'phone_id': PHONE_ID,
                u'phone_number': PHONE_NUMBER,
            })
            operation.setdefault(u'operation_id', OPERATION_ID)
            if u'started' in operation:
                operation[u'operation_started'] = operation.pop(u'started')
            if u'finished' in operation:
                operation[u'operation_finished'] = operation.pop(u'finished')
            kwargs = build_phone_being_bound(**operation)
        else:
            kwargs = build_phone_unbound(PHONE_ID, PHONE_NUMBER)
        return build_account(**kwargs)

    def _create_operation(self, account, code_value=CONFIRMATION_CODE1,
                          should_ignore_binding_limit=False):
        return SimpleBindOperation.create(
            phone_manager=account.phones,
            phone_id=PHONE_ID,
            code=code_value,
            should_ignore_binding_limit=should_ignore_binding_limit,
            statbox=self._statbox,
        )

    def _build_operation_from_account_phone_data(self, account,
                                                 operation_id=OPERATION_ID):
        operation = account.phones.by_operation_id(operation_id).operation
        logical_op, _ = SimpleBindOperation.build_by_data(
            operation,
            account.phones,
        )
        return logical_op


class TestSecureBindOperation(ConfirmCodeMixin, VerifyPasswordMixin, Base, unittest.TestCase):
    _is_binding = True
    _phone_ids = [PHONE_ID]
    _arg_mappings = {PHONE_ID: {}}
    _is_secure = True

    def test_operation_id_data_passed_to_logical_operation(self):
        account = self._build_account(operation={u'operation_id': OPERATION_ID})
        logical_op = self._build_operation_from_account_phone_data(account)
        eq_(logical_op.id, OPERATION_ID)

    def test_data_to_operation__secure_phone_being_bound__ok(self):
        # Операцию можно построить из правильно сформированных данных
        account = build_account(
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        operation = account.phones.by_operation_id(OPERATION_ID).operation
        logical_op, used = SecureBindOperation.build_by_data(
            operation,
            account.phones,
        )

        ok_(logical_op)
        ok_(logical_op.is_binding)
        ok_(logical_op.is_secure)
        eq_(used, {operation})

    @raises(BuildOperationError)
    def test_data_to_operation__simple_phone_being_bound__fail(self):
        # Операцию невозможно построить из данных, которые не подходят
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        self._build_operation_from_account_phone_data(account, OPERATION_ID)

    def test_create_operation__simple_phone_being_bound__fail(self):
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    @raises(SingleSecureOperationError)
    def test_create_operation__secure_phone_being_bound__fail(self):
        account = self._build_account()
        self._create_operation(account=account)
        self._create_operation(account=account)

    @raises(NumberBoundAlready)
    def test_create_operation__phone_bound__fail(self):
        account = build_account(
            **build_phone_bound(
                phone_id=PHONE_ID,
                phone_number=PHONE_NUMBER,
            )
        )
        self._create_operation(account=account)

    @raises(SecureNumberBoundAlready)
    def test_create_operation__secure_phone_bound__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_unbound(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                ),
                build_phone_secured(
                    phone_id=PHONE_ID_EXTRA,
                    phone_number=PHONE_NUMBER_EXTRA,
                ),
            )
        )
        self._create_operation(account=account)

    @raises(SingleSecureOperationError)
    def test_create_operation__other_secure_phone_being_bound__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_unbound(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                ),
                build_secure_phone_being_bound(
                    phone_id=PHONE_ID_EXTRA,
                    phone_number=PHONE_NUMBER_EXTRA,
                    operation_id=OPERATION_ID_EXTRA,
                ),
            )
        )
        self._create_operation(account=account)

    def test_create_operation__ok(self):
        account = self._build_account()

        self._create_operation(account)

        assert_secure_phone_being_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
            {u'id': None},
        )

    def test_should_ignore_binding_limit_on_created_operation(self):
        _test_should_ignore_binding_limit_on_created_operation(self)

    def test_aliasify_on_created_operation(self):
        account = self._build_account()
        logical_op = self._create_operation(account, aliasify=False)

        ok_(not logical_op.flags.aliasify)

        account = self._build_account()
        logical_op = self._create_operation(account, aliasify=True)

        ok_(logical_op.flags.aliasify)

    def test_apply__not_confirmed_phone__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account=account)
        logical_op.password_verified = TEST_DATE1

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            eq_(e.need_confirmed_phones, {account.phones.by_id(PHONE_ID)})
            ok_(not e.need_password_verification)

    def test_apply__password_not_verified__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            ok_(not e.need_confirmed_phones)
            ok_(e.need_password_verification)

    def test_apply__password_not_verified__password_verification_not_required__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )

        with assert_raises(OperationInapplicable) as assertion:
            logical_op.apply(need_authenticated_user=False)

        eq_(assertion.exception.need_confirmed_phones, {account.phones.by_id(PHONE_ID)})
        ok_(not assertion.exception.need_password_verification)

    def test_apply__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.password_verified = TEST_DATE1
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        next_op, _ = logical_op.apply()

        assert_is_none(next_op)
        assert_secure_phone_bound(
            account,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'bound': DatetimeNow(),
                u'confirmed': DatetimeNow(),
                u'secured': DatetimeNow(),
            },
        )

    def test_apply__timestamp__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.password_verified = TEST_DATE1
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        logical_op.apply(timestamp=TEST_DATE2)

        assert_secure_phone_bound(
            account,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'bound': TEST_DATE2,
                u'confirmed': DatetimeNow(),
                u'secured': TEST_DATE2,
            },
        )

    def test_apply__password_verified__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)
        logical_op.password_verified = datetime.now()

        logical_op.apply()

        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )

    def test_apply__password_not_verified__password_verification_not_required__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        logical_op.apply(need_authenticated_user=False)

        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )

    def test_cancel(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        logical_op.cancel()

        ok_(not account.phones.has_id(PHONE_ID))

    @raises(SecureBindToSimpleBindError)
    def test_to_simple_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

    def test_to_secure_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
            should_ignore_binding_limit=False,
        )
        logical_op.set_confirmation_info(PHONE_ID, TEST_CONFIRMATION_INFO1)
        phone = account.phones.by_id(PHONE_ID)

        next_op = logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

        eq_(next_op, logical_op)
        eq_(next_op.flags.should_ignore_binding_limit, False)
        eq_(
            next_op.get_confirmation_info(PHONE_ID),
            TEST_CONFIRMATION_INFO1,
        )

    def test_get_conflict_operations(self):
        account = build_account(
            **deep_merge(
                build_phone_being_bound(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                    operation_id=OPERATION_ID,
                ),
                build_secure_phone_being_bound(
                    phone_id=PHONE_ID_EXTRA,
                    phone_number=PHONE_NUMBER_EXTRA,
                    operation_id=OPERATION_ID_EXTRA,
                ),
            )
        )

        conflict_ops = SecureBindOperation.get_conflict_operations(
            phone_manager=account.phones,
            phone_number=PHONE_NUMBER,
            statbox=self._statbox,
        )

        conflict_ops.sort(key=lambda co: co.id)
        eq_(conflict_ops[0].id, OPERATION_ID)
        eq_(conflict_ops[1].id, OPERATION_ID_EXTRA)

    def _build_account(self, operation=None):
        if operation is not None:
            operation.update({
                u'phone_id': PHONE_ID,
                u'phone_number': PHONE_NUMBER,
            })
            operation.setdefault(u'operation_id', OPERATION_ID)
            if u'started' in operation:
                operation[u'operation_started'] = operation.pop(u'started')
            if u'finished' in operation:
                operation[u'operation_finished'] = operation.pop(u'finished')
            kwargs = build_secure_phone_being_bound(**operation)
        else:
            kwargs = build_phone_unbound(PHONE_ID, PHONE_NUMBER)
        return build_account(**kwargs)

    def _create_operation(self, account, code_value=CONFIRMATION_CODE1,
                          should_ignore_binding_limit=False, aliasify=False):
        return SecureBindOperation.create(
            phone_manager=account.phones,
            phone_id=PHONE_ID,
            code=code_value,
            should_ignore_binding_limit=should_ignore_binding_limit,
            statbox=self._statbox,
            aliasify=aliasify,
        )

    def _build_operation_from_account_phone_data(self, account,
                                                 operation_id=OPERATION_ID):
        operation = account.phones.by_operation_id(operation_id).operation
        logical_op, _ = SecureBindOperation.build_by_data(
            operation,
            account.phones,
        )
        return logical_op


def _test_should_ignore_binding_limit_on_created_operation(test_case):
    account = test_case._build_account()

    logical_op = test_case._create_operation(
        account=account,
        should_ignore_binding_limit=False,
    )

    ok_(not logical_op.flags.should_ignore_binding_limit)

    account = test_case._build_account()

    logical_op = test_case._create_operation(
        account=account,
        should_ignore_binding_limit=True,
    )

    ok_(logical_op.flags.should_ignore_binding_limit)


class TestSecurifyOperation(ConfirmCodeMixin, VerifyPasswordMixin, Base, unittest.TestCase):
    _phone_ids = [PHONE_ID]
    _arg_mappings = {PHONE_ID: {}}
    _is_secure = True

    def test_operation_id_data_passed_to_logical_operation(self):
        account = self._build_account(operation={u'operation_id': OPERATION_ID})
        logical_op = self._build_operation_from_account_phone_data(account)
        eq_(logical_op.id, OPERATION_ID)

    def test_data_to_operation__securify_phone__ok(self):
        # Операцию можно построить из правильно сформированных данных
        account = build_account(
            **deep_merge(
                build_phone_bound(PHONE_ID, PHONE_NUMBER),
                build_securify_operation(OPERATION_ID, PHONE_ID),
            )
        )

        operation = account.phones.by_operation_id(OPERATION_ID).operation
        logical_op, used = SecurifyOperation.build_by_data(
            operation,
            account.phones,
        )

        ok_(logical_op)
        ok_(not logical_op.is_binding)
        ok_(logical_op.is_secure)
        eq_(used, {operation})

    @raises(BuildOperationError)
    def test_data_to_operation__simple_phone_being_bound__fail(self):
        # Операцию невозможно построить из данных, которые не подходят
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        self._build_operation_from_account_phone_data(account, OPERATION_ID)

    @raises(NumberNotBound)
    def test_create_operation__phone_unbound__fail(self):
        account = build_account(
            **build_phone_unbound(
                phone_id=PHONE_ID,
                phone_number=PHONE_NUMBER,
            )
        )
        self._create_operation(account=account)

    @raises(SingleSecureOperationError)
    def test_create_operation__other_secure_phone_being_bound__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_bound(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                ),
                build_secure_phone_being_bound(
                    phone_id=PHONE_ID_EXTRA,
                    phone_number=PHONE_NUMBER_EXTRA,
                    operation_id=OPERATION_ID_EXTRA,
                ),
            )
        )
        self._create_operation(account=account)

    @raises(SecureNumberBoundAlready)
    def test_create_operation__secure_phone_bound__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_bound(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                ),
                build_phone_secured(
                    phone_id=PHONE_ID_EXTRA,
                    phone_number=PHONE_NUMBER_EXTRA,
                ),
            )
        )
        self._create_operation(account=account)

    def test_create_operation__mark_operation__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_bound(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                ),
                build_mark_operation(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                    operation_id=OPERATION_ID_EXTRA,
                ),
            )
        )
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    @raises(SingleSecureOperationError)
    def test_create_operation__simple_phone_being_securified__fail(self):
        account = self._build_account()
        self._create_operation(account=account)
        self._create_operation(account=account)

    def test_create_operation__ok(self):
        account = self._build_account()

        self._create_operation(account)

        assert_simple_phone_being_securified(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
            {u'id': None},
        )

    def test_apply__not_confirmed_phone__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account=account)
        logical_op.password_verified = TEST_DATE1

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            eq_(e.need_confirmed_phones, {account.phones.by_id(PHONE_ID)})
            ok_(not e.need_password_verification)

    def test_apply__password_not_verified__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            ok_(not e.need_confirmed_phones)
            ok_(e.need_password_verification)

    def test_apply__ok(self):
        account = self._build_account()
        phone = account.phones.by_id(PHONE_ID)
        phone.bound = TEST_DATE1
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.password_verified = TEST_DATE1
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        next_op, _ = logical_op.apply()

        assert_is_none(next_op)
        assert_secure_phone_bound(
            account,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'bound': TEST_DATE1,
                u'confirmed': DatetimeNow(),
                u'secured': DatetimeNow(),
            },
        )

    def test_apply__timestamp__ok(self):
        account = self._build_account()
        phone = account.phones.by_id(PHONE_ID)
        phone.bound = TEST_DATE1
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.password_verified = TEST_DATE1
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        logical_op.apply(timestamp=TEST_DATE2)

        assert_secure_phone_bound(
            account,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'bound': TEST_DATE1,
                u'confirmed': DatetimeNow(),
                u'secured': TEST_DATE2,
            },
        )

    def test_cancel(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        logical_op.cancel()

        assert_simple_phone_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )

    @raises(NumberBoundAlready)
    def test_to_simple_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

    @raises(NumberBoundAlready)
    def test_to_secure_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    def _build_account(self, operation=None):
        if operation is not None:
            operation[u'phone_id'] = PHONE_ID
            operation.setdefault(u'operation_id', OPERATION_ID)
            operation_dict = build_securify_operation(**operation)
        else:
            operation_dict = {}
        return build_account(
            **deep_merge(
                build_phone_bound(PHONE_ID, PHONE_NUMBER, is_default=True),
                operation_dict,
            )
        )

    def _create_operation(self, account, code_value=CONFIRMATION_CODE1):
        return SecurifyOperation.create(
            phone_manager=account.phones,
            phone_id=PHONE_ID,
            code=code_value,
            statbox=self._statbox,
        )

    def _build_operation_from_account_phone_data(self, account,
                                                 operation_id=OPERATION_ID):
        operation = account.phones.by_operation_id(operation_id).operation
        logical_op, _ = SecurifyOperation.build_by_data(
            operation,
            account.phones,
        )
        return logical_op


@with_settings(
    PHONE_QUARANTINE_SECONDS=TEST_PHONE_QUARANTINE_SECONDS,
)
class TestRemoveSecureOperation(
    QuarantineMixin,
    ConfirmCodeMixin,
    VerifyPasswordMixin,
    Base,
    unittest.TestCase,
):
    _phone_ids = [PHONE_ID]
    _arg_mappings = {PHONE_ID: {}}
    _is_secure = True

    _OPERATION_TTL = timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS)

    def test_operation_id_data_passed_to_logical_operation(self):
        account = self._build_account(operation={u'operation_id': OPERATION_ID})
        logical_op = self._build_operation_from_account_phone_data(account)
        eq_(logical_op.id, OPERATION_ID)

    def test_data_to_operation__remove_secure_phone__ok(self):
        # Операцию можно построить из правильно сформированных данных
        account = build_account(
            **deep_merge(
                build_phone_secured(PHONE_ID, PHONE_NUMBER),
                build_remove_operation(OPERATION_ID, PHONE_ID),
            )
        )

        operation = account.phones.by_operation_id(OPERATION_ID).operation
        logical_op, used = RemoveSecureOperation.build_by_data(
            operation,
            account.phones,
        )

        ok_(logical_op)
        ok_(not logical_op.is_binding)
        ok_(logical_op.is_secure)
        eq_(used, {operation})

    @raises(BuildOperationError)
    def test_data_to_operation__simple_phone_being_bound__fail(self):
        # Операцию невозможно построить из данных, которые не подходят
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        self._build_operation_from_account_phone_data(account, OPERATION_ID)

    @raises(NumberNotBound)
    def test_create_operation__phone_unbound__fail(self):
        account = build_account(
            **build_phone_unbound(
                phone_id=PHONE_ID,
                phone_number=PHONE_NUMBER,
            )
        )
        self._create_operation(account=account)

    @raises(NumberNotSecured)
    def test_create_operation__simple_phone_bound__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_bound(
                    phone_id=PHONE_ID,
                    phone_number=PHONE_NUMBER,
                ),
            )
        )
        self._create_operation(account=account)

    def test_create_operation__secure_phone_being_removed__fail(self):
        account = self._build_account()
        self._create_operation(account=account)
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    def test_create_operation__ok(self):
        account = self._build_account()

        self._create_operation(account)

        assert_secure_phone_being_removed(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
            {u'id': None},
        )

    def test_set_password_verified__start_quarantine(self):
        now = datetime.now()
        account = self._build_account(operation={
            u'started': now,
            u'finished': now + timedelta(seconds=60),
            u'code_last_sent': None,
            u'code_send_count': 0,
            u'code_value': None,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(
            self._statbox,
        )

        logical_op.password_verified = TEST_DATE1

        eq_(
            logical_op.finished,
            DatetimeNow() + timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS),
        )
        ok_(logical_op.in_quarantine)

    def test_set_password_verified__not_start_quarantine(self):
        now = datetime.now()
        finished = now + timedelta(seconds=60)
        account = self._build_account(operation={
            u'started': now,
            u'finished': finished,

            # Пользователь указал, что номер ему доступен.
            u'code_last_sent': now,
            u'code_send_count': 1,
            u'code_value': CONFIRMATION_CODE1,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(self._statbox)

        eq_(logical_op.finished, DatetimeNow(timestamp=finished))
        ok_(not logical_op.in_quarantine)

    def test_apply__not_confirmed_phone__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account=account)
        logical_op.password_verified = TEST_DATE1

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            eq_(e.need_confirmed_phones, {account.phones.by_id(PHONE_ID)})
            ok_(not e.need_password_verification)

    def test_apply__password_not_verified__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            ok_(not e.need_confirmed_phones)
            ok_(e.need_password_verification)

    def test_apply__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.password_verified = TEST_DATE1
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        next_op, changes = logical_op.apply()

        assert_is_none(next_op)
        eq_(changes.unbound_numbers, {PHONE_NUMBER})
        ok_(not account.phones.has_id(PHONE_ID))

    def test_apply__password_not_verified__password_verification_not_required__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        next_op, changes = logical_op.apply(need_authenticated_user=False)

        assert_is_none(next_op)
        eq_(changes.unbound_numbers, {PHONE_NUMBER})
        ok_(not account.phones.has_id(PHONE_ID))

    def test_apply__password_not_verified__password_verification_not_required__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )

        with assert_raises(OperationInapplicable) as assertion:
            logical_op.apply(need_authenticated_user=False)

        eq_(assertion.exception.need_confirmed_phones, {account.phones.by_id(PHONE_ID)})
        ok_(not assertion.exception.need_password_verification)

    def test_cancel(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        logical_op.cancel()

        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )

    @raises(NumberBoundAlready)
    def test_to_simple_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

    @raises(NumberBoundAlready)
    def test_to_secure_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    def test_does_user_admit_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        ok_(logical_op.does_user_admit_phone)

        account = self._build_account()
        logical_op = self._create_operation(account, code_value=None)
        ok_(not logical_op.does_user_admit_phone)

    def test_harvester_applies__in_quarantine(self):
        now = datetime.now()
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        account = self._build_account(operation={
            u'started': now - timedelta(seconds=60),
            u'finished': now,
            u'code_last_sent': None,
            u'code_send_count': 0,
            u'code_value': None,
            u'password_verified': TEST_DATE1,
            u'flags': phone_operation_flags,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(
            self._statbox,
        )

        next_op, changes = logical_op.apply(is_harvester=True)

        assert_is_none(next_op)
        eq_(changes.unbound_numbers, {PHONE_NUMBER})
        ok_(not account.phones.has_id(PHONE_ID))

    def test_ready_for_quarantine(self):
        account = self._build_account(
            operation=dict(
                code_value=None,
                password_verified=TEST_DATE1,
            ),
        )
        phone = account.phones.by_id(PHONE_ID)
        logical_op = phone.get_logical_operation(self._statbox)

        ok_(logical_op.is_ready_for_quarantine())

        # А если пользователь признаёт наличие телефона, то операцию нельзя
        # помещать в карантин.
        confirmation_info = logical_op.get_confirmation_info(PHONE_ID)
        confirmation_info.code_value = CONFIRMATION_CODE1
        logical_op.set_confirmation_info(PHONE_ID, confirmation_info)

        ok_(not logical_op.is_ready_for_quarantine())

    def test_ready_for_quarantine__password_not_verified(self):
        account = self._build_account(
            operation=dict(
                code_value=None,
            ),
        )
        phone = account.phones.by_id(PHONE_ID)
        logical_op = phone.get_logical_operation(self._statbox)

        ok_(not logical_op.is_ready_for_quarantine())
        ok_(logical_op.is_ready_for_quarantine(need_authenticated_user=False))

    def _build_account(self, operation=None):
        if operation is not None:
            operation[u'phone_id'] = PHONE_ID
            operation.setdefault(u'operation_id', OPERATION_ID)
            operation_dict = build_remove_operation(**operation)
        else:
            operation_dict = {}
        return build_account(
            **deep_merge(
                build_phone_secured(
                    PHONE_ID,
                    PHONE_NUMBER,
                    is_default=True,
                ),
                operation_dict,
            )
        )

    def _create_operation(self, account, code_value=CONFIRMATION_CODE1,
                          should_ignore_binding_limit=False):
        return RemoveSecureOperation.create(
            phone_manager=account.phones,
            phone_id=PHONE_ID,
            code=code_value,
            statbox=self._statbox,
        )

    def _build_operation_from_account_phone_data(self, account,
                                                 operation_id=OPERATION_ID):
        operation = account.phones.by_operation_id(operation_id).operation
        logical_op, _ = RemoveSecureOperation.build_by_data(
            operation,
            account.phones,
        )
        return logical_op


@with_settings(
    PHONE_QUARANTINE_SECONDS=TEST_PHONE_QUARANTINE_SECONDS,
)
class TestReplaceSecurePhoneWithBoundPhoneOperation(
    QuarantineMixin,
    ConfirmCodeMixin,
    VerifyPasswordMixin,
    Base,
    unittest.TestCase,
):
    _secure_phone_id = PHONE_ID
    _simple_phone_id = PHONE_ID_EXTRA
    _phone_ids = [_secure_phone_id, _simple_phone_id]
    _is_secure = True

    _OPERATION_TTL = timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS)

    _arg_mappings = {
        _secure_phone_id: {
            u'code_value': u'secure_code_value',
            u'code_last_sent': u'secure_code_last_sent',
            u'code_send_count': u'secure_code_send_count',
            u'code_confirmed': u'secure_code_confirmed',
            u'code_checks_count': u'secure_code_checks_count',
        },
        _simple_phone_id: {
            u'code_value': u'simple_code_value',
            u'code_last_sent': u'simple_code_last_sent',
            u'code_send_count': u'simple_code_send_count',
            u'code_confirmed': u'simple_code_confirmed',
            u'code_checks_count': u'simple_code_checks_count',
        },
    }

    def test_operation_id_data_passed_to_logical_operation(self):
        account = self._build_account(operation={
            u'secure_operation_id': OPERATION_ID,
            u'simple_operation_id': OPERATION_ID_EXTRA,
        })
        logical_op = self._build_operation_from_account_phone_data(account)
        eq_(logical_op.id, OPERATION_ID)

    def test_data_to_operation__correct_data__ok(self):
        # Операцию можно построить из правильно сформированных данных
        account = build_account(
            **deep_merge(
                build_phone_secured(PHONE_ID, PHONE_NUMBER),
                build_phone_bound(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
                build_simple_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID,
                    secure_phone_id=PHONE_ID,
                    simple_operation_id=OPERATION_ID_EXTRA,
                    simple_phone_id=PHONE_ID_EXTRA,
                    simple_phone_number=PHONE_NUMBER_EXTRA,
                ),
            )
        )

        operation = account.phones.by_operation_id(OPERATION_ID).operation
        operation_extra = account.phones.by_operation_id(OPERATION_ID_EXTRA).operation

        logical_op, used = ReplaceSecurePhoneWithBoundPhoneOperation.build_by_data(
            operation,
            account.phones,
        )

        ok_(logical_op)
        ok_(not logical_op.is_binding)
        ok_(logical_op.is_secure)
        eq_(used, {operation, operation_extra})

        logical_op, used = ReplaceSecurePhoneWithBoundPhoneOperation.build_by_data(
            operation_extra,
            account.phones,
        )

        ok_(logical_op)
        ok_(not logical_op.is_binding)
        ok_(logical_op.is_secure)
        eq_(used, {operation, operation_extra})

    @raises(BuildOperationError)
    def test_data_to_operation__simple_phone_being_bound__fail(self):
        # Операцию невозможно построить из данных, которые не подходят
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        self._build_operation_from_account_phone_data(account, OPERATION_ID)

    @raises(NumberNotBound)
    def test_create_operation__simple_phone_unbound__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER),
                build_phone_unbound(self._simple_phone_id, PHONE_NUMBER_EXTRA),
            )
        )
        self._create_operation(account=account)

    @raises(NumberNotSecured)
    def test_create_operation__secure_phone_not_secure__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_bound(self._secure_phone_id, PHONE_NUMBER),
                build_phone_bound(self._simple_phone_id, PHONE_NUMBER_EXTRA),
            )
        )
        self._create_operation(account=account)

    @raises(NumberNotSecured)
    def test_create_operation__secure_phone_not_bound__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_unbound(self._secure_phone_id, PHONE_NUMBER),
                build_phone_bound(self._simple_phone_id, PHONE_NUMBER_EXTRA),
            )
        )
        self._create_operation(account=account)

    def test_create_operation__secure_phone_in_operation__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER),
                build_phone_bound(self._simple_phone_id, PHONE_NUMBER_EXTRA),
                build_mark_operation(
                    OPERATION_ID,
                    PHONE_NUMBER,
                    self._secure_phone_id,
                ),
            )
        )
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    def test_create_operation__simple_phone_in_operation__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER),
                build_phone_bound(self._simple_phone_id, PHONE_NUMBER_EXTRA),
                build_mark_operation(
                    OPERATION_ID,
                    PHONE_NUMBER_EXTRA,
                    self._simple_phone_id,
                ),
            )
        )
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    def test_create_operation__ok(self):
        account = self._build_account()

        self._create_operation(account)

        assert_simple_phone_replace_secure(
            account,
            {u'id': self._simple_phone_id, u'number': PHONE_NUMBER_EXTRA},
            {u'id': None},
        )
        assert_secure_phone_being_replaced(
            account,
            {u'id': self._secure_phone_id, u'number': PHONE_NUMBER},
            {u'id': None},
        )

    def test_set_password_verified__start_quarantine(self):
        now = datetime.now()
        account = self._build_account(operation={
            u'started': now,
            u'finished': now + timedelta(seconds=60),
            u'simple_code_confirmed': TEST_DATE1,
            u'secure_code_last_sent': None,
            u'secure_code_send_count': 0,
            u'secure_code_value': None,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(
            self._statbox,
        )

        logical_op.password_verified = TEST_DATE1

        eq_(
            logical_op.finished,
            DatetimeNow() + timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS),
        )
        ok_(logical_op.in_quarantine)

    def test_set_password_verified__not_start_quarantine(self):
        now = datetime.now()
        finished = now + timedelta(seconds=60)
        account = self._build_account(operation={
            u'started': now,
            u'finished': finished,
            u'simple_code_confirmed': TEST_DATE1,

            # Пользователь указал, что защищённый номер ему доступен
            u'secure_code_value': CONFIRMATION_CODE1,
            u'secure_code_last_sent': now,
            u'secure_code_send_count': 1,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(self._statbox)

        logical_op.password_verified = TEST_DATE1

        eq_(logical_op.finished, DatetimeNow(timestamp=finished))
        ok_(not logical_op.in_quarantine)

    def test_confirm_simple_phone__start_quarantine(self):
        now = datetime.now()
        account = self._build_account(operation={
            u'started': now,
            u'finished': now + timedelta(seconds=60),
            u'password_verified': TEST_DATE1,
            u'simple_code_value': CONFIRMATION_CODE1,
            u'secure_code_last_sent': None,
            u'secure_code_send_count': 0,
            u'secure_code_value': None,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(
            self._statbox,
        )

        logical_op.confirm_phone(self._simple_phone_id, CONFIRMATION_CODE1)

        eq_(
            logical_op.finished,
            DatetimeNow() + timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS),
        )
        ok_(logical_op.in_quarantine)

    def test_confirm_simple_phone__not_start_quarantine(self):
        now = datetime.now()
        finished = now + timedelta(seconds=60)
        account = self._build_account(operation={
            u'started': now,
            u'finished': finished,
            u'password_verified': TEST_DATE1,
            u'simple_code_value': CONFIRMATION_CODE1,

            # Пользователь указал, что защищённый номер ему доступен
            u'secure_code_value': CONFIRMATION_CODE1,
            u'secure_code_last_sent': now,
            u'secure_code_send_count': 1,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(self._statbox)

        logical_op.confirm_phone(self._simple_phone_id, CONFIRMATION_CODE1)

        eq_(logical_op.finished, DatetimeNow(timestamp=finished))
        ok_(not logical_op.in_quarantine)

    def test_confirm_phone__relative_confirmation_code__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
            simple_code_value=CONFIRMATION_CODE2,
        )

        is_phone_confirmed, _ = logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE2)
        ok_(not is_phone_confirmed)

    def test_apply__not_confirmed_phone__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account=account)
        logical_op.password_verified = TEST_DATE1

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            eq_(
                e.need_confirmed_phones,
                {
                    account.phones.by_id(phone_id)
                    for phone_id in self._phone_ids
                },
            )
            ok_(not e.need_password_verification)

    def test_apply__not_password_verified__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
            simple_code_value=CONFIRMATION_CODE2,
        )
        logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE1)
        logical_op.confirm_phone(self._simple_phone_id, CONFIRMATION_CODE2)

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            ok_(not e.need_confirmed_phones)
            ok_(e.need_password_verification)

    def test_apply__ok(self):
        account = self._build_account()
        simple_phone = account.phones.by_id(self._simple_phone_id)
        simple_phone.bound = TEST_DATE1
        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
            simple_code_value=CONFIRMATION_CODE2,
        )
        logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE1)
        logical_op.confirm_phone(self._simple_phone_id, CONFIRMATION_CODE2)
        logical_op.password_verified = TEST_DATE1

        next_op, changes = logical_op.apply()

        assert_is_none(next_op)
        eq_(changes.unbound_numbers, {PHONE_NUMBER})
        assert_secure_phone_bound(
            account,
            {
                u'id': self._simple_phone_id,
                u'number': PHONE_NUMBER_EXTRA,
                u'bound': TEST_DATE1,
                u'confirmed': DatetimeNow(),
                u'secured': DatetimeNow(),
            },
        )
        ok_(not account.phones.has_id(self._secure_phone_id))

    def test_apply__timestamp__ok(self):
        account = self._build_account()
        simple_phone = account.phones.by_id(self._simple_phone_id)
        simple_phone.bound = TEST_DATE1
        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
            simple_code_value=CONFIRMATION_CODE2,
        )
        logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE1)
        logical_op.confirm_phone(self._simple_phone_id, CONFIRMATION_CODE2)
        logical_op.password_verified = TEST_DATE1

        logical_op.apply(timestamp=TEST_DATE2)

        assert_secure_phone_bound(
            account,
            {
                u'id': self._simple_phone_id,
                u'number': PHONE_NUMBER_EXTRA,
                u'bound': TEST_DATE1,
                u'confirmed': DatetimeNow(),
                u'secured': TEST_DATE2,
            },
        )

    def test_apply__password_verified__ok(self):
        account = self._build_account()
        simple_phone = account.phones.by_id(self._simple_phone_id)
        simple_phone.bound = TEST_DATE1
        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
            simple_code_value=CONFIRMATION_CODE2,
        )
        logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE1)
        logical_op.confirm_phone(self._simple_phone_id, CONFIRMATION_CODE2)

        logical_op.apply(need_authenticated_user=False)

    def test_apply__secure_phone_is_bank_phonenumber_alias__ok(self):
        account = build_account(
            aliases=dict(bank_phonenumber=PHONE_NUMBER.replace('+', '')),
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER, is_bank=True),
                build_phone_bound(self._simple_phone_id, PHONE_NUMBER_EXTRA),
            )
        )

        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
            simple_code_value=CONFIRMATION_CODE2,
        )
        logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE1)
        logical_op.confirm_phone(self._simple_phone_id, CONFIRMATION_CODE2)
        logical_op.password_verified = TEST_DATE1

        next_op, changes = logical_op.apply()

        assert next_op is None
        assert not changes.unbound_numbers
        assert_secure_phone_bound(
            account,
            dict(
                id=self._simple_phone_id,
                number=PHONE_NUMBER_EXTRA,
            ),
        )
        assert_simple_phone_bound(
            account,
            dict(
                id=self._secure_phone_id,
                number=PHONE_NUMBER,
            ),
        )
        assert account.phones.by_id(self._secure_phone_id).is_bank

    def test_cancel(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        logical_op.cancel()

        assert_secure_phone_bound(
            account,
            {u'id': self._secure_phone_id, u'number': PHONE_NUMBER},
        )
        assert_simple_phone_bound(
            account,
            {u'id': self._simple_phone_id, u'number': PHONE_NUMBER_EXTRA},
        )

    @raises(NumberBoundAlready)
    def test_to_simple_bind__secure_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(self._secure_phone_id)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

    @raises(NumberBoundAlready)
    def test_to_secure_bind__secure_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(self._secure_phone_id)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    @raises(NumberBoundAlready)
    def test_to_simple_bind__simple_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(self._simple_phone_id)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

    @raises(NumberBoundAlready)
    def test_to_secure_bind__simple_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(self._simple_phone_id)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    def test_does_user_admit_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        ok_(logical_op.does_user_admit_phone)

        account = self._build_account()
        logical_op = self._create_operation(account, secure_code_value=None)
        ok_(not logical_op.does_user_admit_phone)

    def test_harvester_applies__in_quarantine(self):
        now = datetime.now()
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        account = self._build_account(
            operation={
                u'started': now - timedelta(seconds=60),
                u'finished': now,
                u'password_verified': TEST_DATE1,
                u'simple_code_confirmed': TEST_DATE1,
                u'secure_code_last_sent': None,
                u'secure_code_send_count': 0,
                u'secure_code_value': None,
                u'flags': phone_operation_flags,
            },
        )
        simple_phone = account.phones.by_id(self._simple_phone_id)
        simple_phone.bound = TEST_DATE1

        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(self._statbox)
        next_op, changes = logical_op.apply(is_harvester=True)

        assert_is_none(next_op)
        eq_(changes.unbound_numbers, {PHONE_NUMBER})
        assert_secure_phone_bound(
            account,
            {
                u'id': self._simple_phone_id,
                u'number': PHONE_NUMBER_EXTRA,
                u'bound': TEST_DATE1,
                u'confirmed': TEST_DATE1,
                u'secured': DatetimeNow(),
            },
        )
        ok_(not account.phones.has_id(self._secure_phone_id))

    def test_ready_for_quarantine(self):
        account = self._build_account(
            operation=dict(
                simple_code_confirmed=TEST_DATE1,
                simple_code_value=CONFIRMATION_CODE1,
                password_verified=TEST_DATE1,
                secure_code_value=None,
            ),
        )
        phone = account.phones.by_id(self._secure_phone_id)
        logical_op = phone.get_logical_operation(self._statbox)

        ok_(logical_op.is_ready_for_quarantine())

        # А если пользователь признаёт наличие основного телефона, то операцию
        # нельзя помещать в карантин.
        confirmation_info = logical_op.get_confirmation_info(self._secure_phone_id)
        confirmation_info.code_value = CONFIRMATION_CODE2
        logical_op.set_confirmation_info(self._secure_phone_id, confirmation_info)

        ok_(not logical_op.is_ready_for_quarantine())

    def _build_account(self, operation=None):
        if operation is not None:
            operation.update({
                u'secure_phone_id': self._secure_phone_id,
                u'simple_phone_id': self._simple_phone_id,
                u'simple_phone_number': PHONE_NUMBER_EXTRA,
            })
            operation.setdefault(u'secure_operation_id', OPERATION_ID)
            operation.setdefault(u'simple_operation_id', OPERATION_ID_EXTRA)
            operation_dict = build_simple_replaces_secure_operations(**operation)
        else:
            operation_dict = {}
        return build_account(
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER),
                build_phone_bound(self._simple_phone_id, PHONE_NUMBER_EXTRA),
                operation_dict,
            )
        )

    def _create_operation(self, account, secure_code_value=CONFIRMATION_CODE1,
                          simple_code_value=CONFIRMATION_CODE2):
        return ReplaceSecurePhoneWithBoundPhoneOperation.create(
            phone_manager=account.phones,
            secure_phone_id=self._secure_phone_id,
            simple_phone_id=self._simple_phone_id,
            secure_code=secure_code_value,
            simple_code=simple_code_value,
            statbox=self._statbox,
        )

    def _build_operation_from_account_phone_data(self, account,
                                                 operation_id=OPERATION_ID):
        operation = account.phones.by_operation_id(operation_id).operation
        logical_op, _ = ReplaceSecurePhoneWithBoundPhoneOperation.build_by_data(
            operation,
            account.phones,
        )
        return logical_op


@with_settings(
    PHONE_QUARANTINE_SECONDS=TEST_PHONE_QUARANTINE_SECONDS,
)
class TestReplaceSecurePhoneWithNonboundPhoneOperation(
    QuarantineMixin,
    ConfirmCodeMixin,
    VerifyPasswordMixin,
    Base,
    unittest.TestCase,
):
    _OPERATION_TTL = timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS)

    _is_binding = True
    _secure_phone_id = PHONE_ID
    _being_bound_phone_id = PHONE_ID_EXTRA
    _phone_ids = [_secure_phone_id, _being_bound_phone_id]
    _is_secure = True

    _arg_mappings = {
        _secure_phone_id: {
            u'code_value': u'secure_code_value',
            u'code_last_sent': u'secure_code_last_sent',
            u'code_send_count': u'secure_code_send_count',
            u'code_confirmed': u'secure_code_confirmed',
            u'code_checks_count': u'secure_code_checks_count',
        },
        _being_bound_phone_id: {
            u'code_value': u'being_bound_code_value',
            u'code_last_sent': u'being_bound_code_last_sent',
            u'code_send_count': u'being_bound_code_send_count',
            u'code_confirmed': u'being_bound_code_confirmed',
            u'code_checks_count': u'being_bound_code_checks_count',
        },
    }

    def test_operation_id_data_passed_to_logical_operation(self):
        account = self._build_account(operation={
            u'secure_operation_id': OPERATION_ID,
            u'being_bound_operation_id': OPERATION_ID_EXTRA,
        })
        logical_op = self._build_operation_from_account_phone_data(account)
        eq_(logical_op.id, OPERATION_ID)

    def test_data_to_operation__correct_data__ok(self):
        # Операцию можно построить из правильно сформированных данных
        account = build_account(
            **deep_merge(
                build_phone_secured(PHONE_ID, PHONE_NUMBER),
                build_phone_unbound(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID,
                    secure_phone_id=PHONE_ID,
                    being_bound_operation_id=OPERATION_ID_EXTRA,
                    being_bound_phone_id=PHONE_ID_EXTRA,
                    being_bound_phone_number=PHONE_NUMBER_EXTRA,
                ),
            )
        )

        operation = account.phones.by_operation_id(OPERATION_ID).operation
        operation_extra = account.phones.by_operation_id(OPERATION_ID_EXTRA).operation

        logical_op, used = ReplaceSecurePhoneWithNonboundPhoneOperation.build_by_data(
            operation,
            account.phones,
        )

        ok_(logical_op)
        ok_(logical_op.is_binding)
        ok_(logical_op.is_secure)
        eq_(used, {operation, operation_extra})

        logical_op, used = ReplaceSecurePhoneWithNonboundPhoneOperation.build_by_data(
            operation_extra,
            account.phones,
        )

        ok_(logical_op)
        ok_(logical_op.is_binding)
        ok_(logical_op.is_secure)
        eq_(used, {operation, operation_extra})

    @raises(BuildOperationError)
    def test_data_to_operation__simple_phone_being_bound__fail(self):
        # Операцию невозможно построить из данных, которые не подходят
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        self._build_operation_from_account_phone_data(account, OPERATION_ID)

    @raises(NumberBoundAlready)
    def test_create_operation__being_bound_phone_bound__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER),
                build_phone_bound(self._being_bound_phone_id, PHONE_NUMBER_EXTRA),
            )
        )
        self._create_operation(account=account)

    @raises(NumberNotSecured)
    def test_create_operation__secure_phone_not_secure__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_bound(self._secure_phone_id, PHONE_NUMBER),
                build_phone_unbound(self._being_bound_phone_id, PHONE_NUMBER_EXTRA),
            )
        )
        self._create_operation(account=account)

    @raises(NumberNotSecured)
    def test_create_operation__secure_phone_not_bound__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_unbound(self._secure_phone_id, PHONE_NUMBER),
                build_phone_unbound(self._being_bound_phone_id, PHONE_NUMBER_EXTRA),
            )
        )
        self._create_operation(account=account)

    def test_create_operation__secure_phone_in_operation__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER),
                build_phone_unbound(self._being_bound_phone_id, PHONE_NUMBER_EXTRA),
                build_remove_operation(OPERATION_ID, self._secure_phone_id),
            )
        )
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    def test_create_operation__being_bound_phone_in_operation__fail(self):
        account = build_account(
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER),
                build_phone_being_bound(
                    self._being_bound_phone_id,
                    PHONE_NUMBER_EXTRA,
                    OPERATION_ID,
                ),
            )
        )
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    def test_create_operation__ok(self):
        account = self._build_account()

        self._create_operation(account)

        assert_simple_phone_being_bound_replace_secure(
            account,
            {u'id': self._being_bound_phone_id, u'number': PHONE_NUMBER_EXTRA},
            {u'id': None},
        )
        assert_secure_phone_being_replaced(
            account,
            {u'id': self._secure_phone_id, u'number': PHONE_NUMBER},
            {u'id': None},
        )

    def test_set_password_verified__start_quarantine(self):
        now = datetime.now()
        account = self._build_account(operation={
            u'started': now,
            u'finished': now + timedelta(seconds=60),
            u'being_bound_code_confirmed': TEST_DATE1,
            u'secure_code_value': None,
            u'secure_code_last_sent': None,
            u'secure_code_send_count': 0,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(
            self._statbox,
        )

        logical_op.password_verified = TEST_DATE1

        eq_(
            logical_op.finished,
            DatetimeNow() + timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS),
        )
        ok_(logical_op.in_quarantine)

    def test_set_password_verified__not_start_quarantine(self):
        now = datetime.now()
        finished = now + timedelta(seconds=60)
        account = self._build_account(operation={
            u'started': now,
            u'finished': finished,
            u'being_bound_code_confirmed': TEST_DATE1,

            u'secure_code_value': CONFIRMATION_CODE1,
            u'secure_code_last_sent': now,
            u'secure_code_send_count': 1,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(self._statbox)

        logical_op.password_verified = TEST_DATE1

        eq_(logical_op.finished, DatetimeNow(timestamp=finished))
        ok_(not logical_op.in_quarantine)

    def test_confirm_being_bound_phone__start_quarantine(self):
        now = datetime.now()
        account = self._build_account(operation={
            u'started': now,
            u'finished': now + timedelta(seconds=60),
            u'password_verified': TEST_DATE1,
            u'being_bound_code_value': CONFIRMATION_CODE1,
            u'secure_code_last_sent': None,
            u'secure_code_send_count': 0,
            u'secure_code_value': None,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(
            self._statbox,
        )

        logical_op.confirm_phone(self._being_bound_phone_id, CONFIRMATION_CODE1)

        eq_(
            logical_op.finished,
            DatetimeNow() + timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS),
        )
        ok_(logical_op.in_quarantine)

    def test_confirm_being_bound_phone__not_start_quarantine(self):
        now = datetime.now()
        finished = now + timedelta(seconds=60)
        account = self._build_account(operation={
            u'started': now,
            u'finished': finished,
            u'password_verified': TEST_DATE1,
            u'being_bound_code_value': CONFIRMATION_CODE1,

            u'secure_code_value': CONFIRMATION_CODE1,
            u'secure_code_last_sent': now,
            u'secure_code_send_count': 1,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(self._statbox)

        logical_op.confirm_phone(self._being_bound_phone_id, CONFIRMATION_CODE1)

        eq_(logical_op.finished, DatetimeNow(timestamp=finished))
        ok_(not logical_op.in_quarantine)

    def test_confirm_phone__relative_confirmation_code__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
            being_bound_code_value=CONFIRMATION_CODE2,
        )

        is_phone_confirmed, _ = logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE2)
        ok_(not is_phone_confirmed)

    def test_apply__not_confirmed_phone__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account=account)
        logical_op.password_verified = TEST_DATE1

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            eq_(
                e.need_confirmed_phones,
                {
                    account.phones.by_id(phone_id)
                    for phone_id in self._phone_ids
                },
            )
            ok_(not e.need_password_verification)

    def test_apply__not_password_verified__being_bound_phone_not_confirmed__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
        )
        logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE1)

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            eq_(
                e.need_confirmed_phones,
                {account.phones.by_id(self._being_bound_phone_id)},
            )
            ok_(e.need_password_verification)

    def test_apply__not_password_verified__ok(self):
        now = datetime.now()
        account = self._build_account(operation={
            u'started': now,
            u'finished': now + timedelta(seconds=60),
            u'secure_code_value': CONFIRMATION_CODE1,
            u'secure_code_confirmed': TEST_DATE1,
            u'being_bound_code_value': CONFIRMATION_CODE2,
            u'being_bound_code_confirmed': TEST_DATE1,
            u'being_bound_code_last_sent': TEST_DATE2,
            u'being_bound_code_send_count': 7,
            u'being_bound_code_checks_count': 11,
        })
        secure_phone = account.phones.by_id(self._secure_phone_id)
        logical_op = secure_phone.get_logical_operation(self._statbox)

        next_op, _ = logical_op.apply()

        self.assertIsInstance(next_op, ReplaceSecurePhoneWithBoundPhoneOperation)
        eq_(next_op.statbox, self._statbox)
        ok_(not next_op.password_verified)
        assert_simple_phone_replace_secure(
            account,
            {
                u'id': self._being_bound_phone_id,
                u'number': PHONE_NUMBER_EXTRA,
                u'bound': DatetimeNow(),
                u'confirmed': TEST_DATE1,
            },
            {
                u'id': None,
                u'started': now,
                u'finished': now + timedelta(seconds=60),
                u'code_value': CONFIRMATION_CODE2,
                u'code_confirmed': TEST_DATE1,
                u'code_last_sent': TEST_DATE2,
                u'code_send_count': 7,
                u'code_checks_count': 11,
                u'phone_id2': self._secure_phone_id,
            },
        )

    def test_apply__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
            being_bound_code_value=CONFIRMATION_CODE2,
        )
        logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE1)
        logical_op.confirm_phone(self._being_bound_phone_id, CONFIRMATION_CODE2)
        logical_op.password_verified = TEST_DATE1

        next_op, changes = logical_op.apply()

        assert_is_none(next_op)
        eq_(changes.unbound_numbers, {PHONE_NUMBER})
        assert_secure_phone_bound(
            account,
            {
                u'id': self._being_bound_phone_id,
                u'number': PHONE_NUMBER_EXTRA,
                u'bound': DatetimeNow(),
                u'confirmed': DatetimeNow(),
                u'secured': DatetimeNow(),
            },
        )
        ok_(not account.phones.has_id(self._secure_phone_id))

    def test_apply__secure_phone_is_bank_phonenumber_alias__ok(self):
        account = build_account(
            aliases=dict(bank_phonenumber=PHONE_NUMBER.replace('+', '')),
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER, is_bank=True),
                build_phone_unbound(self._being_bound_phone_id, PHONE_NUMBER_EXTRA),
            )
        )
        logical_op = self._create_operation(
            account=account,
            secure_code_value=CONFIRMATION_CODE1,
            being_bound_code_value=CONFIRMATION_CODE2,
        )
        logical_op.confirm_phone(self._secure_phone_id, CONFIRMATION_CODE1)
        logical_op.confirm_phone(self._being_bound_phone_id, CONFIRMATION_CODE2)
        logical_op.password_verified = TEST_DATE1

        next_op, changes = logical_op.apply()

        assert next_op is None
        assert not changes.unbound_numbers
        assert_secure_phone_bound(
            account,
            dict(
                id=self._being_bound_phone_id,
                number=PHONE_NUMBER_EXTRA,
            ),
        )
        assert_simple_phone_bound(
            account,
            dict(
                id=self._secure_phone_id,
                number=PHONE_NUMBER,
            ),
        )
        assert account.phones.by_id(self._secure_phone_id).is_bank

    def test_cancel(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        logical_op.cancel()

        assert_secure_phone_bound(
            account,
            {u'id': self._secure_phone_id, u'number': PHONE_NUMBER},
        )
        ok_(not account.phones.has_id(self._being_bound_phone_id))

    @raises(NumberBoundAlready)
    def test_to_simple_bind__secure_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(self._secure_phone_id)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

    @raises(NumberBoundAlready)
    def test_to_secure_bind__secure_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(self._secure_phone_id)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    def test_to_simple_bind__being_bound_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(self._being_bound_phone_id)

        next_op = logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

        eq_(next_op, logical_op)

    @raises(SecureNumberBoundAlready)
    def test_to_secure_bind__being_bound_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(self._being_bound_phone_id)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    def test_does_user_admit_phone(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        ok_(logical_op.does_user_admit_phone)

        account = self._build_account()
        logical_op = self._create_operation(account, secure_code_value=None)
        ok_(not logical_op.does_user_admit_phone)

    def test_harvester_applies__in_quarantine(self):
        now = datetime.now()
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        account = self._build_account(
            operation={
                u'started': now - timedelta(seconds=60),
                u'finished': now,
                u'password_verified': TEST_DATE1,
                u'being_bound_code_value': CONFIRMATION_CODE1,
                u'being_bound_code_confirmed': TEST_DATE1,
                u'secure_code_last_sent': None,
                u'secure_code_send_count': 0,
                u'secure_code_value': None,
                u'flags': phone_operation_flags,
            },
        )
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(self._statbox)

        next_op, changes = logical_op.apply(is_harvester=True)

        assert_is_none(next_op)
        eq_(changes.unbound_numbers, {PHONE_NUMBER})
        assert_secure_phone_bound(
            account,
            {
                u'id': self._being_bound_phone_id,
                u'number': PHONE_NUMBER_EXTRA,
                u'bound': DatetimeNow(),
                u'confirmed': TEST_DATE1,
                u'secured': DatetimeNow(),
            },
        )
        ok_(not account.phones.has_id(self._secure_phone_id))

    def test_repr(self):
        account = self._build_account(operation={
            u'started': TEST_DATE1,
            u'finished': TEST_DATE2,
            u'password_verified': TEST_DATE1,
        })
        logical_op = account.phones.by_id(PHONE_ID).get_logical_operation(self._statbox)

        kwargs = {
            'started': TEST_DATE1,
            'finished': TEST_DATE2,
            'password_verified': TEST_DATE1,
            'secure_phone_id': self._secure_phone_id,
            'being_bound_phone_id': self._being_bound_phone_id,
            'security_identity': str(int(PHONE_NUMBER_EXTRA)),
        }

        primary_op = ('<Operation type=replace security_identity=1 started="%(started)s" '
                      'finished="%(finished)s" password_verified="%(password_verified)s" '
                      'code_confirmed=None does_user_admit_phone=True flags=0 '
                      'phone_id=%(secure_phone_id)d phone_id2=%(being_bound_phone_id)d>')
        primary_op = primary_op % kwargs

        secondary_op = ('<Operation type=bind security_identity=%(security_identity)s started="%(started)s" '
                        'finished="%(finished)s" password_verified="%(password_verified)s" '
                        'code_confirmed=None does_user_admit_phone=True flags=0 '
                        'phone_id=%(being_bound_phone_id)d phone_id2=%(secure_phone_id)d>')
        secondary_op = secondary_op % kwargs

        eq_(
            repr(logical_op),
            '<LogicalOperation: '
            'id=%d '
            'name=replace_secure_phone_with_nonbound_phone '
            'primary_operation=%s '
            'secondary_operation=%s>' % (logical_op.id, primary_op, secondary_op),
        )

    def test_ready_for_quarantine(self):
        account = self._build_account(
            operation=dict(
                being_bound_code_confirmed=TEST_DATE1,
                being_bound_code_value=CONFIRMATION_CODE1,
                password_verified=TEST_DATE1,
                secure_code_value=None,
            ),
        )
        phone = account.phones.by_id(self._secure_phone_id)
        logical_op = phone.get_logical_operation(self._statbox)

        ok_(logical_op.is_ready_for_quarantine())

        # А если пользователь признаёт наличие основного телефона, то операцию
        # нельзя помещать в карантин.
        confirmation_info = logical_op.get_confirmation_info(self._secure_phone_id)
        confirmation_info.code_value = CONFIRMATION_CODE2
        logical_op.set_confirmation_info(self._secure_phone_id, confirmation_info)

        ok_(not logical_op.is_ready_for_quarantine())

    def test_upgrade_to_replace_with_bound_phone__in_quarantine(self):
        phone_operation_finished = datetime.fromtimestamp(int(time())) + timedelta(hours=1)
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        account = self._build_account(
            operation=dict(
                being_bound_code_confirmed=TEST_DATE1,
                being_bound_code_value=CONFIRMATION_CODE1,
                finished=phone_operation_finished,
                flags=phone_operation_flags,
                password_verified=TEST_DATE1,
                secure_code_value=None,
                started=TEST_DATE1,
            ),
        )
        phone = account.phones.by_id(self._secure_phone_id)
        logical_op = phone.get_logical_operation(self._statbox)

        next_logical_op, _ = logical_op.apply()

        ok_(type(next_logical_op) is ReplaceSecurePhoneWithBoundPhoneOperation)
        eq_(next_logical_op.finished, phone_operation_finished)
        ok_(next_logical_op.in_quarantine)
        eq_(next_logical_op.started, TEST_DATE1)

    def _build_account(self, operation=None):
        if operation is not None:
            operation.update({
                u'secure_phone_id': self._secure_phone_id,
                u'being_bound_phone_id': self._being_bound_phone_id,
                u'being_bound_phone_number': PHONE_NUMBER_EXTRA,
            })
            operation.setdefault(u'secure_operation_id', OPERATION_ID)
            operation.setdefault(u'being_bound_operation_id', OPERATION_ID_EXTRA)
            operation_dict = build_phone_being_bound_replaces_secure_operations(**operation)
        else:
            operation_dict = {}
        return build_account(
            **deep_merge(
                build_phone_secured(self._secure_phone_id, PHONE_NUMBER),
                build_phone_unbound(self._being_bound_phone_id, PHONE_NUMBER_EXTRA),
                operation_dict,
            )
        )

    def _create_operation(self, account, secure_code_value=CONFIRMATION_CODE1,
                          being_bound_code_value=CONFIRMATION_CODE2):
        return ReplaceSecurePhoneWithNonboundPhoneOperation.create(
            phone_manager=account.phones,
            secure_phone_id=self._secure_phone_id,
            being_bound_phone_id=self._being_bound_phone_id,
            secure_code=secure_code_value,
            being_bound_code=being_bound_code_value,
            statbox=self._statbox,
        )

    def _build_operation_from_account_phone_data(self, account,
                                                 operation_id=OPERATION_ID):
        operation = account.phones.by_operation_id(operation_id).operation
        logical_op, _ = ReplaceSecurePhoneWithNonboundPhoneOperation.build_by_data(
            operation,
            account.phones,
        )
        return logical_op


@with_settings(
    YASMS_MARK_OPERATION_TTL=60,
)
class TestMarkOperation(Base, unittest.TestCase):
    _phone_ids = [PHONE_ID]
    _arg_mappings = {PHONE_ID: {}}

    _OPERATION_TTL = timedelta(seconds=60)

    def test_operation_id_data_passed_to_logical_operation(self):
        account = self._build_account(operation={u'operation_id': OPERATION_ID})
        logical_op = self._build_operation_from_account_phone_data(account)
        eq_(logical_op.id, OPERATION_ID)

    def test_data_to_operation__mark_operation__ok(self):
        # Операцию можно построить из правильно сформированных данных
        account = build_account(
            **deep_merge(
                build_phone_bound(PHONE_ID, PHONE_NUMBER),
                build_mark_operation(OPERATION_ID, PHONE_NUMBER, PHONE_ID),
            )
        )

        operation = account.phones.by_operation_id(OPERATION_ID).operation
        logical_op, used = MarkOperation.build_by_data(
            operation,
            account.phones,
        )

        ok_(logical_op)
        ok_(not logical_op.is_binding)
        ok_(not logical_op.is_secure)
        eq_(used, {operation})

    @raises(BuildOperationError)
    def test_data_to_operation__simple_phone_being_bound__fail(self):
        # Операцию невозможно построить из данных, которые не подходят
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        self._build_operation_from_account_phone_data(account, OPERATION_ID)

    def test_create_operation__simple_phone_being_bound__fail(self):
        account = build_account(
            **build_phone_being_bound(
                phone_id=PHONE_ID,
                phone_number=PHONE_NUMBER,
                operation_id=OPERATION_ID,
            )
        )
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    def test_create_operation__ok(self):
        account = self._build_account()

        self._create_operation(account)

        assert_phone_marked(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
            {u'id': None},
        )

    def test_create_operation__phone_unbound__ok(self):
        account = build_account(
            **build_phone_unbound(
                phone_id=PHONE_ID,
                phone_number=PHONE_NUMBER,
            )
        )
        self._create_operation(account=account)

    def test_create_operation__phone_bound__ok(self):
        account = build_account(
            **build_phone_bound(
                phone_id=PHONE_ID,
                phone_number=PHONE_NUMBER,
            )
        )
        self._create_operation(account=account)

    def test_create_operation__phone_secured__ok(self):
        account = build_account(
            **build_phone_secured(
                phone_id=PHONE_ID,
                phone_number=PHONE_NUMBER,
            )
        )
        self._create_operation(account=account)

    def test_apply__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        next_op, _ = logical_op.apply()

        assert_is_none(next_op)
        assert_simple_phone_bound(
            account,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
            },
        )

    def test_cancel(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        logical_op.cancel()

        assert_simple_phone_bound(
            account,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
            },
        )

    @raises(NumberBoundAlready)
    def test_to_simple_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE1)

    @raises(NumberBoundAlready)
    def test_to_secure_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_secure_bind(phone, CONFIRMATION_CODE1, True)

    @raises(OperationExists)
    def test_to_simple_bind__phone_unbound(self):
        account = self._build_account(is_phone_bound=False)
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE1)

    @raises(OperationExists)
    def test_to_secure_bind__phone_unbound(self):
        account = self._build_account(is_phone_bound=False)
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_secure_bind(phone, CONFIRMATION_CODE1, False)

    def _build_account(self, operation=None, is_phone_bound=True):
        if operation is not None:
            operation.update({
                u'phone_id': PHONE_ID,
                u'phone_number': PHONE_NUMBER,
            })
            operation.setdefault(u'operation_id', OPERATION_ID)
            operation_dict = build_mark_operation(**operation)
        else:
            operation_dict = {}
        if is_phone_bound:
            phone_data = build_phone_bound(PHONE_ID, PHONE_NUMBER)
        else:
            phone_data = build_phone_unbound(PHONE_ID, PHONE_NUMBER)
        return build_account(**deep_merge(phone_data, operation_dict))

    def _create_operation(self, account):
        return MarkOperation.create(
            phone_manager=account.phones,
            phone_id=PHONE_ID,
            code=CONFIRMATION_CODE1,
            statbox=self._statbox,
        )

    def _build_operation_from_account_phone_data(self, account,
                                                 operation_id=OPERATION_ID):
        operation = account.phones.by_operation_id(operation_id).operation
        logical_op, _ = MarkOperation.build_by_data(operation, account.phones)
        return logical_op


@with_settings(
    PHONE_QUARANTINE_SECONDS=TEST_PHONE_QUARANTINE_SECONDS,
)
class TestAliasifySecureOperation(ConfirmCodeMixin, Base, unittest.TestCase):
    _phone_ids = [PHONE_ID]
    _arg_mappings = {PHONE_ID: {}}
    _is_secure = True

    _OPERATION_TTL = timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS)

    def test_operation_id_data_passed_to_logical_operation(self):
        account = self._build_account(operation={u'operation_id': OPERATION_ID})
        logical_op = self._build_operation_from_account_phone_data(account)
        eq_(logical_op.id, OPERATION_ID)

    def test_data_to_operation__aliasify_secure_phone__ok(self):
        # Операцию можно построить из правильно сформированных данных
        account = build_account(
            **deep_merge(
                build_phone_secured(PHONE_ID, PHONE_NUMBER),
                build_aliasify_secure_operation(OPERATION_ID, PHONE_ID),
            )
        )

        operation = account.phones.by_operation_id(OPERATION_ID).operation
        logical_op, used = AliasifySecureOperation.build_by_data(operation, account.phones)

        ok_(logical_op)
        ok_(not logical_op.is_binding)
        ok_(logical_op.is_secure)
        eq_(used, {operation})

    @raises(BuildOperationError)
    def test_data_to_operation__simple_phone_being_bound__fail(self):
        # Операцию невозможно построить из данных, которые не подходят
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        self._build_operation_from_account_phone_data(account, OPERATION_ID)

    @raises(NumberNotBound)
    def test_create_operation__phone_unbound__fail(self):
        account = build_account(**build_phone_unbound(phone_id=PHONE_ID, phone_number=PHONE_NUMBER))
        self._create_operation(account=account)

    @raises(NumberNotSecured)
    def test_create_operation__simple_phone_bound__fail(self):
        account = build_account(**deep_merge(build_phone_bound(phone_id=PHONE_ID, phone_number=PHONE_NUMBER)))
        self._create_operation(account=account)

    def test_create_operation__secure_phone_being_aliasified__fail(self):
        account = self._build_account()
        self._create_operation(account=account)
        with self.assertRaisesRegexp(AttributeError, u'Operation already exists'):
            self._create_operation(account=account)

    def test_create_operation__ok(self):
        account = self._build_account()

        self._create_operation(account)

        assert_secure_phone_being_aliasified(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
            {u'id': None},
        )

    def test_apply__not_confirmed_phone__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(account=account)

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            eq_(e.need_confirmed_phones, {account.phones.by_id(PHONE_ID)})
            ok_(not e.need_password_verification)

    def test_apply__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(account=account, code_value=CONFIRMATION_CODE1)
        logical_op.confirm_phone(PHONE_ID, CONFIRMATION_CODE1)

        next_op, changes = logical_op.apply()

        assert_is_none(next_op)
        ok_(not changes.unbound_numbers)
        ok_(not changes.bound_numbers)
        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
        ok_(not account.phonenumber_alias.number)

    def test_cancel(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        logical_op.cancel()

        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
        ok_(not account.phonenumber_alias.number)

    @raises(NumberBoundAlready)
    def test_to_simple_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

    @raises(NumberBoundAlready)
    def test_to_secure_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    def _build_account(self, operation=None):
        if operation is not None:
            operation[u'phone_id'] = PHONE_ID
            operation.setdefault(u'operation_id', OPERATION_ID)
            operation_dict = build_aliasify_secure_operation(**operation)
        else:
            operation_dict = {}
        return build_account(
            **deep_merge(
                build_phone_secured(PHONE_ID, PHONE_NUMBER),
                operation_dict,
            )
        )

    def _create_operation(self, account, code_value=CONFIRMATION_CODE1):
        return AliasifySecureOperation.create(
            phone_manager=account.phones,
            phone_id=PHONE_ID,
            code=code_value,
            statbox=self._statbox,
        )

    def _build_operation_from_account_phone_data(self, account, operation_id=OPERATION_ID):
        operation = account.phones.by_operation_id(operation_id).operation
        logical_op, _ = AliasifySecureOperation.build_by_data(operation, account.phones)
        return logical_op


@with_settings(
    PHONE_QUARANTINE_SECONDS=TEST_PHONE_QUARANTINE_SECONDS,
)
class TestDealiasifySecureOperation(VerifyPasswordMixin, Base, unittest.TestCase):
    _phone_ids = [PHONE_ID]
    _arg_mappings = {PHONE_ID: {}}
    _is_secure = True

    _OPERATION_TTL = timedelta(seconds=TEST_PHONE_QUARANTINE_SECONDS)

    def test_operation_id_data_passed_to_logical_operation(self):
        account = self._build_account(operation={u'operation_id': OPERATION_ID})
        logical_op = self._build_operation_from_account_phone_data(account)
        eq_(logical_op.id, OPERATION_ID)

    def test_data_to_operation__dealiasify_secure_phone__ok(self):
        # Операцию можно построить из правильно сформированных данных
        account = build_account(
            **deep_merge(
                build_phone_secured(PHONE_ID, PHONE_NUMBER, is_alias=True),
                build_dealiasify_secure_operation(OPERATION_ID, PHONE_ID),
            )
        )

        operation = account.phones.by_operation_id(OPERATION_ID).operation
        logical_op, used = DealiasifySecureOperation.build_by_data(operation, account.phones)

        ok_(logical_op)
        ok_(not logical_op.is_binding)
        ok_(logical_op.is_secure)
        eq_(used, {operation})

    @raises(BuildOperationError)
    def test_data_to_operation__simple_phone_being_bound__fail(self):
        # Операцию невозможно построить из данных, которые не подходят
        account = build_account(
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
            )
        )

        self._build_operation_from_account_phone_data(account, OPERATION_ID)

    @raises(NumberNotBound)
    def test_create_operation__phone_unbound__fail(self):
        account = build_account(**build_phone_unbound(phone_id=PHONE_ID, phone_number=PHONE_NUMBER))
        self._create_operation(account=account)

    @raises(NumberNotSecured)
    def test_create_operation__simple_phone_bound__fail(self):
        account = build_account(**deep_merge(build_phone_bound(phone_id=PHONE_ID, phone_number=PHONE_NUMBER)))
        self._create_operation(account=account)

    def test_create_operation__secure_phone_being_dealiasified__fail(self):
        account = self._build_account()
        self._create_operation(account=account)
        with self.assertRaisesRegexp(
            AttributeError,
            u'Operation already exists',
        ):
            self._create_operation(account=account)

    def test_create_operation__ok(self):
        account = self._build_account()

        self._create_operation(account)

        assert_secure_phone_being_dealiasified(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
            {u'id': None},
        )

    def test_apply__password_not_verified__fail(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )

        with assert_raises(OperationInapplicable):
            logical_op.apply()

        try:
            logical_op.apply()
        except OperationInapplicable as e:
            ok_(not e.need_confirmed_phones)
            ok_(e.need_password_verification)

    def test_apply__ok(self):
        account = self._build_account()
        logical_op = self._create_operation(
            account=account,
            code_value=CONFIRMATION_CODE1,
        )
        logical_op.password_verified = TEST_DATE1

        next_op, changes = logical_op.apply()

        assert_is_none(next_op)
        ok_(not changes.unbound_numbers)
        ok_(not changes.bound_numbers)
        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
        ok_(account.phonenumber_alias.number)

    def test_cancel(self):
        account = self._build_account()
        logical_op = self._create_operation(account)

        logical_op.cancel()

        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
        ok_(account.phonenumber_alias.number)

    @raises(NumberBoundAlready)
    def test_to_simple_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_simple_bind(phone, CONFIRMATION_CODE2)

    @raises(NumberBoundAlready)
    def test_to_secure_bind(self):
        account = self._build_account()
        logical_op = self._create_operation(account)
        phone = account.phones.by_id(PHONE_ID)

        logical_op.to_secure_bind(
            phone=phone,
            code=CONFIRMATION_CODE2,
            should_ignore_binding_limit=True,
        )

    def _build_account(self, operation=None):
        if operation is not None:
            operation[u'phone_id'] = PHONE_ID
            operation.setdefault(u'operation_id', OPERATION_ID)
            operation_dict = build_dealiasify_secure_operation(**operation)
        else:
            operation_dict = {}
        return build_account(
            **deep_merge(
                build_phone_secured(PHONE_ID, PHONE_NUMBER, is_alias=True),
                operation_dict,
            )
        )

    def _create_operation(self, account, code_value=CONFIRMATION_CODE1):
        return DealiasifySecureOperation.create(
            phone_manager=account.phones,
            phone_id=PHONE_ID,
            code=code_value,
            statbox=self._statbox,
        )

    def _build_operation_from_account_phone_data(self, account, operation_id=OPERATION_ID):
        operation = account.phones.by_operation_id(operation_id).operation
        logical_op, _ = DealiasifySecureOperation.build_by_data(operation, account.phones)
        return logical_op


class TestPhoneChangeSet(unittest.TestCase):
    def test_empty(self):
        change_set = PhoneChangeSet()

        eq_(change_set.unbound_numbers, set())
        eq_(change_set.bound_numbers, set())
        assert_is_none(change_set.secured_number, None)

    def test_not_empty(self):
        change_set = PhoneChangeSet(
            bound_numbers={PHONE_NUMBER, PHONE_NUMBER_EXTRA},
            secured_number=PHONE_NUMBER,
            unbound_numbers={PHONE_NUMBER_EXTRA},
        )

        eq_(change_set.bound_numbers, {PHONE_NUMBER, PHONE_NUMBER_EXTRA})
        eq_(change_set.secured_number, PHONE_NUMBER)
        eq_(change_set.unbound_numbers, {PHONE_NUMBER_EXTRA})

    def test_equality(self):
        bound_numbers = [
            None,
            {PHONE_NUMBER},
            {PHONE_NUMBER, PHONE_NUMBER_EXTRA},
        ]
        unbound_numbers = [
            None,
            {PHONE_NUMBER},
            {PHONE_NUMBER, PHONE_NUMBER_EXTRA},
        ]
        secured_number = [None, PHONE_NUMBER]

        in_args = product(
            product(unbound_numbers, bound_numbers, secured_number),
            repeat=2,
        )

        for in_args1, in_args2 in in_args:
            change_set1 = PhoneChangeSet(*in_args1)
            change_set2 = PhoneChangeSet(*in_args2)
            if in_args1 == in_args2:
                ok_(change_set1 == change_set2)
            else:
                ok_(change_set1 != change_set2)

    def test_repr(self):
        eq_(
            repr(PhoneChangeSet()),
            '<PhoneChangeSet bound_numbers=[], unbound_numbers=[], '
            'secured_number=None>',
        )
        eq_(
            repr(
                PhoneChangeSet(
                    bound_numbers={'+79259164525', '+79026411724'},
                    secured_number='+79026411724',
                    unbound_numbers={'+79082414400'},
                ),
            ),
            "<PhoneChangeSet bound_numbers=['+79026411724', '+79259164525'], "
            "unbound_numbers=['+79082414400'], secured_number='+79026411724'>",
        )

    def test_iadd(self):
        change_set1 = PhoneChangeSet(
            bound_numbers={PHONE_NUMBER},
            secured_number=PHONE_NUMBER,
            unbound_numbers={PHONE_NUMBER},
        )
        change_set2 = PhoneChangeSet(
            bound_numbers={PHONE_NUMBER_EXTRA},
            unbound_numbers={PHONE_NUMBER_EXTRA},
        )

        change_set1 += change_set2

        eq_(
            change_set1,
            PhoneChangeSet(
                bound_numbers={PHONE_NUMBER, PHONE_NUMBER_EXTRA},
                secured_number=PHONE_NUMBER,
                unbound_numbers={PHONE_NUMBER, PHONE_NUMBER_EXTRA},
            ),
        )
        eq_(
            change_set2,
            PhoneChangeSet(
                bound_numbers={PHONE_NUMBER_EXTRA},
                unbound_numbers={PHONE_NUMBER_EXTRA},
            ),
        )
