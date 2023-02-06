# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import (
    datetime,
    timedelta,
)

import mock
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.builders.blackbox.parsers import PHONE_OP_DEFAULT_VALUES
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING
from passport.backend.core.models.account import Account
from passport.backend.core.models.alias import BankPhoneNumberAlias
from passport.backend.core.models.phones.faker import (
    build_account,
    build_phone_bound,
    build_phone_secured,
    PhoneIdGeneratorFaker,
)
from passport.backend.core.models.phones.phones import (
    Operation,
    Phone,
    PhoneConfirmedAlready,
    RemoveBankPhoneNumberError,
    SECURITY_IDENTITY,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    unixtime,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.undefined import Undefined
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime
from six import iteritems


TEST_PHONE_NUMBER = '+79030915478'
TEST_PHONE_NUMBER_DIGITAL = '79030915478'

TEST_ATTR_CREATED_AT = 1234567892
TEST_ATTR_BOUND_AT = 1234567893
TEST_ATTR_CONFIRMED_AT = 1234567894
TEST_ATTR_ADMITTED_AT = 1234567895
TEST_ATTR_SECURED_AT = 1234567896

TEST_DATE = datetime(2014, 6, 17, 8, 0, 0)
TEST_ATTR_CREATED_DT = datetime.fromtimestamp(TEST_ATTR_CREATED_AT)
TEST_ATTR_BOUND_DT = datetime.fromtimestamp(TEST_ATTR_BOUND_AT)
TEST_ATTR_CONFIRMED_DT = datetime.fromtimestamp(TEST_ATTR_CONFIRMED_AT)
TEST_ATTR_ADMITTED_DT = datetime.fromtimestamp(TEST_ATTR_ADMITTED_AT)
TEST_ATTR_SECURED_DT = datetime.fromtimestamp(TEST_ATTR_SECURED_AT)


ALL_ATTRS = {
    'number': TEST_PHONE_NUMBER,
    'created': TEST_ATTR_CREATED_AT,
    'bound': TEST_ATTR_BOUND_AT,
    'confirmed': TEST_ATTR_CONFIRMED_AT,
    'admitted': TEST_ATTR_ADMITTED_AT,
    'secured': TEST_ATTR_SECURED_AT,
    'is_default': '0',
    'is_bank': '0',
}

TEST_PHONE_NUMBER2 = '+79260915400'


PHONE_OPERATION_TEST_DATA = {
    'security_identity': TEST_PHONE_NUMBER,
    'type': 'bind',
    'started': unixtime(2000, 1, 23, 12, 34, 56),
    'finished': unixtime(2001, 1, 23, 12, 34, 56),
    'code_value': 'abcdefg',
    'code_checks_count': 2,
    'code_send_count': 1,
    'code_last_sent': unixtime(2002, 1, 23, 12, 34, 56),
    'code_confirmed': unixtime(2003, 1, 23, 12, 34, 56),
    'password_verified': unixtime(2004, 1, 23, 12, 34, 56),
    'flags': 123,
    'phone_id2': 555,
}

TEST_CONFIRMATION_UNIXTIME = 1234567890


PHONE_NUMBER = '+79031234567'
SIMPLE_PHONE = PhoneNumber.parse(PHONE_NUMBER)


PHONE_OPERATION_TEST_DATA_PARSED = {
    'security_identity': TEST_PHONE_NUMBER,
    'type': 'bind',
    'started': datetime(2000, 1, 23, 12, 34, 56),
    'finished': datetime(2001, 1, 23, 12, 34, 56),
    'code_value': 'abcdefg',
    'code_checks_count': 2,
    'code_send_count': 1,
    'code_last_sent': datetime(2002, 1, 23, 12, 34, 56),
    'code_confirmed': datetime(2003, 1, 23, 12, 34, 56),
    'password_verified': datetime(2004, 1, 23, 12, 34, 56),
    'flags': PhoneOperationFlags(123),
    'phone_id2': 555,
}


@with_settings(
    YASMS_ADMIT_PHONE_VALID_PERIOD=timedelta(days=10),
)
class TestPhone(PassportTestCase):
    def setUp(self):
        self.account = Account().parse({'uid': 1})

    def test_simple(self):
        """ Базовый тест. Проверяем, что все поля приехали из расширенных атрибутов."""

        # Проверим, что имеем заданые тестовые значения для всех возможных атрибутов.
        eq_(ALL_ATTRS.keys(), EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING.keys())

        # Все возможные атрибуты со значениями:
        phone = Phone().parse({'id': 1, 'attributes': ALL_ATTRS})

        eq_(phone.id, 1)
        eq_(phone.number.e164, TEST_PHONE_NUMBER)
        eq_(phone.created, TEST_ATTR_CREATED_DT)
        eq_(phone.bound, TEST_ATTR_BOUND_DT)
        eq_(phone.confirmed, TEST_ATTR_CONFIRMED_DT)
        eq_(phone.admitted, TEST_ATTR_ADMITTED_DT)
        eq_(phone.secured, TEST_ATTR_SECURED_DT)

    def test_need_admission(self):
        def updated_dt(days_past):
            return datetime.now() - timedelta(days=days_past)

        test_attrs = (
            (
                {
                    'confirmed': to_unixtime(updated_dt(1)),
                    'admitted': to_unixtime(updated_dt(2)),
                    'number': TEST_PHONE_NUMBER,
                },
                False,
            ),
            (
                {
                    'confirmed': to_unixtime(updated_dt(5)),
                    'admitted': to_unixtime(updated_dt(200)),
                    'number': TEST_PHONE_NUMBER,
                },
                False,
            ),
            (
                {
                    'admitted': to_unixtime(updated_dt(0)),
                    'confirmed': to_unixtime(updated_dt(11)),
                    'number': TEST_PHONE_NUMBER,
                },
                False,
            ),
            (
                {
                    'confirmed': to_unixtime(updated_dt(188)),
                    'number': TEST_PHONE_NUMBER,
                },
                True,
            ),
            (
                {
                    'number': TEST_PHONE_NUMBER,
                },
                False,
            ),
        )
        for attrs, result in test_attrs:
            phone = Phone().parse(
                {
                    'id': 1,
                    'attributes': attrs,
                },
            )
            eq_(phone.need_admission, result, msg=attrs)

    def test_need_admission_with_operation(self):
        """
        Над телефоном идёт операция, пользователю телефон доступен,
        проверяем необходимость переподтверждения номера как обычно.
        """
        phone = Phone().parse(
            {
                'id': 1,
                'attributes': {
                    'confirmed': TEST_ATTR_CONFIRMED_AT,
                    'number': TEST_PHONE_NUMBER,
                },
                'operation': PHONE_OPERATION_TEST_DATA,
            },
        )
        ok_(phone.need_admission)

    def test_no_need_admission_in_quarantine(self):
        """
        Над телефоном идёт операция, и в ней пользователь указал,
        что не владеет телефоном. Сейчас отсутствие code_value
        это признак того, что пользователь указал, что не владеет телефоном.
        """
        operation_with_no_code = merge_dicts(
            PHONE_OPERATION_TEST_DATA,
            dict(code_value=None),
        )
        phone = Phone().parse(
            {
                'id': 1,
                'attributes': {
                    'confirmed': TEST_ATTR_CONFIRMED_AT,
                    'number': TEST_PHONE_NUMBER,
                },
                'operation': operation_with_no_code,
            },
        )
        ok_(not phone.need_admission)

    def test_unknown_attr(self):
        """
        Пришел атрибут, номер которого нам неизвестен. Игнорируем его.
        """
        phone = Phone().parse({
            'id': 1,
            'attributes': {
                'number': ALL_ATTRS['number'],
                'unknown': 'data',
            },
        })

        eq_(phone.number.e164, TEST_PHONE_NUMBER)

    def test_no_data_about_operation_on_phone(self):
        phone = Phone().parse({
            'id': 1,
            'attributes': {'number': ALL_ATTRS['number']},
        })

        ok_(not phone.operation)

    def test_no_operation_on_phone(self):
        phone = Phone().parse({
            'id': 1,
            'attributes': {'number': ALL_ATTRS['number']},
            'operation': None,
        })

        ok_(not phone.operation)

    def test_operation(self):
        phone = Phone().parse({
            'id': 1,
            'attributes': {
                'number': ALL_ATTRS['number'],
                'created': TEST_ATTR_CREATED_AT,
            },
            'operation': PHONE_OPERATION_TEST_DATA,
        })

        ok_(phone.operation)

    def test_current_binding(self):
        phone = Phone().parse({
            'id': 1,
            'attributes': ALL_ATTRS,
            'binding': {
                'uid': 1,
                'type': 'current',
                'phone_number': TEST_PHONE_NUMBER,
                'phone_id': 1,
                'binding_time': to_unixtime(TEST_ATTR_BOUND_DT),
                'should_ignore_binding_limit': 1,
            },
        })

        ok_(phone.binding.is_current)
        ok_(not phone.binding.is_unbound)
        eq_(phone.binding.time, TEST_ATTR_BOUND_DT)
        eq_(phone.binding.should_ignore_binding_limit, True)

    def test_unbound_binding(self):
        phone = Phone().parse({
            'id': 1,
            'attributes': ALL_ATTRS,
            'binding': {
                'uid': 1,
                'type': 'unbound',
                'phone_number': TEST_PHONE_NUMBER,
                'phone_id': 1,
                'binding_time': 0,
                'should_ignore_binding_limit': 0,
            },
        })

        ok_(not phone.binding.is_current)
        ok_(phone.binding.is_unbound)
        eq_(phone.binding.time, None)
        eq_(phone.binding.should_ignore_binding_limit, False)

    def test_binding_does_not_exist(self):
        phone = Phone().parse({
            'id': 1,
            'attributes': ALL_ATTRS,
            'binding': None,
        })

        ok_(phone.binding is None)

    def test_undefined_binding(self):
        phone = Phone().parse({
            'id': 1,
            'attributes': ALL_ATTRS,
        })

        ok_(phone.binding is Undefined)

    def test_confirm_simple_phone(self):
        one_hour_ago = datetime.now() - timedelta(hours=1)
        account = build_account(
            uid=1,
            **deep_merge(
                build_phone_bound(
                    phone_id=1,
                    phone_number=TEST_PHONE_NUMBER,
                    phone_confirmed=one_hour_ago,
                ),
                build_phone_secured(
                    phone_id=2,
                    phone_number=TEST_PHONE_NUMBER2,
                    phone_confirmed=one_hour_ago,
                ),
            )
        )

        simple_phone = account.phones.by_id(1)
        simple_phone.confirm()
        secure_phone = account.phones.by_id(2)
        eq_(simple_phone.confirmed, DatetimeNow())
        eq_(secure_phone.confirmed, DatetimeNow(timestamp=one_hour_ago))

    def test_confirm_secure_phone(self):
        one_hour_ago = datetime.now() - timedelta(hours=1)
        account = build_account(
            uid=1,
            **build_phone_secured(
                phone_id=1,
                phone_number=TEST_PHONE_NUMBER,
                phone_confirmed=one_hour_ago,
            )
        )

        secure_phone = account.phones.by_id(1)
        secure_phone.confirm()
        eq_(secure_phone.confirmed, DatetimeNow())

    def test_confirm_at_specified_time_in_past(self):
        one_hour_ago = datetime.now() - timedelta(hours=1)
        two_hours_ago = datetime.now() - timedelta(hours=2)
        account = build_account(
            **build_phone_bound(
                phone_id=1,
                phone_number=TEST_PHONE_NUMBER,
                phone_confirmed=one_hour_ago,
            )
        )

        phone = account.phones.by_id(1)
        with assert_raises(PhoneConfirmedAlready):
            phone.confirm(timestamp=two_hours_ago)

    def test_confirm_at_specified_time_in_future(self):
        one_hour_ago = datetime.now() - timedelta(hours=1)
        half_hour_ago = datetime.now() - timedelta(minutes=30)
        account = build_account(
            **build_phone_bound(
                phone_id=1,
                phone_number=TEST_PHONE_NUMBER,
                phone_confirmed=one_hour_ago,
            )
        )

        phone = account.phones.by_id(1)
        phone.confirm(half_hour_ago)
        eq_(phone.confirmed, half_hour_ago)

    def test_bind_new_phone_without_binding(self):
        phone = Phone()
        ok_(not phone.bound)
        ok_(not phone.binding)

        phone.bound = TEST_DATE

        ok_(phone.binding)
        eq_(phone.binding.time, TEST_DATE)
        ok_(not phone.binding.should_ignore_binding_limit)


class TestPhoneOperation(PassportTestCase):

    def test_simple(self):
        """ Базовый тест. Проверяем, что все поля приехали из данных операции."""

        operation = Operation().parse({'operation': PHONE_OPERATION_TEST_DATA})
        for key, value in iteritems(PHONE_OPERATION_TEST_DATA_PARSED):
            eq_(getattr(operation, key), value, [key, getattr(operation, key), value])

    def test_defaults(self):
        operation = Operation().parse({'operation': {'type': 'bind'}})

        for key in PHONE_OPERATION_TEST_DATA:
            if key == 'type':
                continue

            expected = PHONE_OP_DEFAULT_VALUES.get(key, Undefined)
            if callable(expected):
                expected = expected()

            eq_(
                getattr(operation, key),
                expected,
                [key, getattr(operation, key), expected],
            )

    def test_is_secure(self):
        operation = Operation().parse({'operation': {'type': 'bind', 'security_identity': TEST_PHONE_NUMBER}})
        ok_(not operation.is_secure)

        operation = Operation().parse({'operation': {'type': 'bind', 'security_identity': SECURITY_IDENTITY}})
        ok_(operation.is_secure)

    def test_equality(self):
        operation = Operation().parse({'operation': {'type': 'bind'}})
        eq_(operation, operation)
        ok_(operation is not None)

        op1 = Operation().parse({'operation': {'type': 'bind'}})
        op1.id = 1
        op2 = Operation().parse({'operation': {'type': 'bind'}})
        op2.id = 1
        eq_(op1, op2)

    def test_is_expired_cached(self):
        operation = Operation().parse({
            'operation': {
                'type': 'bind',
                'finished': to_unixtime(TEST_DATE + timedelta(hours=1)),
            },
        })

        with mock.patch('passport.backend.core.models.phones.phones.datetime') as datetime_mock:
            datetime_mock.now.return_value = TEST_DATE
            ok_(not operation.is_expired)
            datetime_mock.now.return_value = TEST_DATE + timedelta(hours=1)
            ok_(not operation.is_expired)

    def test_does_user_admit_phone(self):
        operation = Operation().parse({
            'operation': {
                'type': 'bind',
                'code_value': None,
            },
        })
        ok_(not operation.does_user_admit_phone)

        operation.code_value = TEST_DATE
        ok_(operation.does_user_admit_phone)


class TestPhones(PassportTestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()
        self._phone_id_faker = PhoneIdGeneratorFaker()
        self._phone_id_faker.start()
        self._phone_id_faker.set_list(range(100, 105))
        self.account = Account().parse({'uid': 1})

    def tearDown(self):
        self._db_faker.stop()
        self._phone_id_faker.stop()
        del self._db_faker
        del self._phone_id_faker

    def get_account(self, phone_number='+79030915478', default=None, secure=None, is_bank=False):
        data = {
            'uid': 1,
            'phones': {
                1: {
                    'id': 1,
                    'attributes': {
                        'number': phone_number,
                        'bound': TEST_ATTR_BOUND_AT,
                        'is_bank': is_bank,
                    },
                },
            },
        }

        if default:
            data['phones.default'] = default

        if secure:
            data['phones.secure'] = secure

        return Account().parse(data)

    def test_simple(self):
        """
        На аккаунте есть один телефон, он же указан в secure и default.
        """
        acc = self.get_account(default='1', secure='1')

        phone = acc.phones.by_id(1)
        eq_(acc.phones.default, phone)
        eq_(acc.phones.secure, phone)
        eq_(phone.operation, Undefined)

        # Добавим еще телефонов, дефолт не должен смениться
        p1 = acc.phones.create(TEST_PHONE_NUMBER2, bound=datetime.fromtimestamp(TEST_ATTR_BOUND_AT - 1))
        acc.phones.create(TEST_PHONE_NUMBER2, bound=datetime.fromtimestamp(TEST_ATTR_BOUND_AT + 1))
        p1.secured = TEST_ATTR_SECURED_DT
        acc.phones.secure = p1

        eq_(acc.phones.default, phone)
        eq_(acc.phones.secure, p1)

    def test_default_phone_id_missing(self):
        """
        У пользователя нет телефона с phone_id, указанным в phones.default.
        Должен вернуться автовыбранный телефон по умолчанию.
        """
        acc = self.get_account(default='999')

        initial_phone = acc.phones.by_id(1)
        eq_(acc.phones.default, initial_phone)

    def test_default_phone_autodetect_get_from_attr(self):
        """
        Выбираем телефон по умолчанию. В первую очередь берем телефон на основании phones.default_id.
        """
        acc = self.get_account(default='1')
        initial_phone = acc.phones.by_id(1)
        older_phone = acc.phones.create(TEST_PHONE_NUMBER2, bound=datetime.fromtimestamp(TEST_ATTR_BOUND_AT - 1))
        older_phone.secured = TEST_ATTR_BOUND_DT - timedelta(seconds=1)
        acc.phones.secure = older_phone

        eq_(acc.phones.default, initial_phone)

    def test_default_phone_autodetect_get_default_is_missing(self):
        """
        Выбираем телефон по умолчанию. В phones.default несуществующий phone_id.
        Берем первый привязанный. Защищенность телефона не дает преимущества.
        """
        acc = self.get_account(default='999')
        initial_phone = acc.phones.by_id(1)
        older_phone = acc.phones.create(TEST_PHONE_NUMBER2, bound=datetime.fromtimestamp(TEST_ATTR_BOUND_AT - 1))
        initial_phone.secured = datetime.now()
        acc.phones.secure = initial_phone

        eq_(acc.phones.default, older_phone)

    def test_default_phone_autodetect_no_bound_phones(self):
        """
        Выбираем телефон по умолчанию. В phones.default указан phone_id отвязанного телефона.
        """
        acc = self.get_account(default='1')
        initial_phone = acc.phones.by_id(1)
        initial_phone.bound = None

        eq_(acc.phones.default, None)

    def test_secure_phone_id_missing(self):
        """
        У пользователя нет телефона с phone_id, указанным в phones.secure.
        """
        acc = self.get_account(secure='999')
        eq_(acc.phones.secure, None)

    def test_create_phone(self):
        """
        Проверим, что новый объект YasmsPhone создается успешно.
        """
        # Добавим первый телефон с операцией
        phone = self.account.phones.create(
            number=TEST_PHONE_NUMBER,
            operation_data=PHONE_OPERATION_TEST_DATA_PARSED,
            confirmed=datetime(2000, 1, 2, 12, 34, 56),
        )
        phone.operation.id = 1

        self.account.phones.has_id(phone.id)
        eq_(self.account.phones.by_operation_id(phone.operation.id), phone)

        eq_(self._phone_id_faker.call_count, 1)
        eq_(phone.id, 100)
        eq_(phone.number.e164, TEST_PHONE_NUMBER)
        eq_(phone.created, DatetimeNow())
        eq_(phone.confirmed, datetime(2000, 1, 2, 12, 34, 56))
        eq_(self.account.phones.all(), {100: phone})

        eq_(phone.operation.phone_id, phone.id)
        for key, value in iteritems(PHONE_OPERATION_TEST_DATA_PARSED):
            eq_(getattr(phone.operation, key), value, key)

        # Добавим еще один телефон
        phone2 = self.account.phones.create(number=PhoneNumber.parse(TEST_PHONE_NUMBER2))
        eq_(self._phone_id_faker.call_count, 2)
        eq_(phone2.id, 101)
        eq_(phone2.number.e164, TEST_PHONE_NUMBER2)
        eq_(phone2.created, DatetimeNow())
        eq_(self.account.phones.all(), {100: phone, 101: phone2})

    @raises(KeyError)
    def test_by_id_not_found(self):
        """
        Вызовем phones.by_id с несуществующим phone_id.
        """
        self.account.phones.by_id(999)

    def test_by_id_not_found__ignored(self):
        """
        Вызовем phones.by_id с несуществующим phone_id, но передадим assert_exists=False.
        """
        eq_(self.account.phones.by_id(999, assert_exists=False), None)

    def test_get_and_set_default_phone(self):
        """
        Проверим, что работает property account.phones.default
        """
        phone = self.account.phones.create(
            number=TEST_PHONE_NUMBER,
            operation_data=PHONE_OPERATION_TEST_DATA_PARSED,
            confirmed=datetime(2000, 1, 2, 12, 34, 56),
            bound=TEST_ATTR_BOUND_DT,
        )

        eq_(self.account.phones.default, phone)
        ok_(not self.account.phones.default_id)

        self.account.phones.remove(phone)
        ok_(not self.account.phones.default)
        ok_(not self.account.phones.default_id)

    def test_get_and_set_secure_phone(self):
        """
        Проверим, что работает property account.phones.secure
        """
        phone = self.account.phones.create(
            number=TEST_PHONE_NUMBER,
            operation_data=PHONE_OPERATION_TEST_DATA_PARSED,
            confirmed=datetime(2000, 1, 2, 12, 34, 56),
        )
        ok_(not self.account.phones.secure)
        ok_(not self.account.phones.secure_id)

        phone.bound = TEST_ATTR_BOUND_DT
        phone.secured = TEST_ATTR_SECURED_DT
        self.account.phones.secure = phone
        eq_(self.account.phones.secure, phone)
        eq_(self.account.phones.secure_id, phone.id)

    def test_delete_secure_phone_removes_attribute(self):
        """
        При удалении телефона, который является защищенным, должен
        автоматически удаляться атрибут secure_id
        """
        account = Account().parse({
            u'uid': 1,
        })
        phone = account.phones.create(
            number=TEST_PHONE_NUMBER,
            operation_data=PHONE_OPERATION_TEST_DATA_PARSED,
            confirmed=datetime(2000, 1, 2, 12, 34, 56),
        )
        account.phones.create(
            number=TEST_PHONE_NUMBER2,
            operation_data=PHONE_OPERATION_TEST_DATA_PARSED,
            confirmed=datetime(2000, 1, 2, 12, 34, 56),
        )

        phone.bound = TEST_ATTR_BOUND_DT
        phone.secured = TEST_ATTR_SECURED_DT
        account.phones.secure = phone

        # Удалим защищенный телефон.
        account.phones.remove(phone)

        eq_(account.phones.secure, None)
        eq_(account.phones.secure_id, None)

    def test_delete_default_phone_removes_attribute(self):
        """
        При удалении телефона, который является дефолтным, атрибут default_id должен меняться по такой логике:
        1) Если остались привязанные номера, то выбираем привязанный с наибольшим id.
        2) Если не осталось номеров, то ставим в атрибут None (удаляем).
        """
        phone1 = self.account.phones.create(
            number='+79260910001',
            bound=datetime(2001, 1, 2, 12, 34, 56),
        )
        phone2 = self.account.phones.create(
            number='+79260910002',
            bound=datetime(2002, 1, 2, 12, 34, 56),
        )
        phone3 = self.account.phones.create(
            number='+79260910003',
            bound=datetime(2003, 1, 2, 12, 34, 56),
        )
        # Отвязанный телефон
        self.account.phones.create(number='+79260910005')

        self.account.phones.default = phone1
        phone2.secured = TEST_ATTR_SECURED_DT
        self.account.phones.secure = phone2

        eq_(self.account.phones.default, phone1)

        self.account.phones.remove(phone1)

        # Выбирается привязанный с наибольшим phone_id
        # Предпочтение защищённому не делается
        eq_(self.account.phones.default, phone3)

        self.account.phones.remove(phone2)
        self.account.phones.remove(phone3)

        # Привязанных телефонов не осталось
        # Отвязанный телефон не может стать телефоном для уведомлений
        eq_(self.account.phones.default, None)

    def test_simple_account_phones_with_reparse(self):
        """
        Проверим, что если на готовом аккаунте сделать parse, то старые данные не обнулятся.
        """
        data = {
            'uid': 1,
            'phones': {
                1: {
                    'id': 1,
                    'attributes': ALL_ATTRS,
                    'operation': PHONE_OPERATION_TEST_DATA,
                },
            },
        }

        acc = Account().parse(data)

        # Вызовем parse еще раз, не передавая данных о телефонах и операциях.
        # Убедимся, что старые данные останутся.
        acc.parse({'uid': 1})
        eq_(list(acc.phones.all().keys()), [1])

        phone = acc.phones.by_id(1)
        eq_(phone.id, 1)
        eq_(phone.number.e164, TEST_PHONE_NUMBER)
        eq_(phone.created, TEST_ATTR_CREATED_DT)
        eq_(phone.bound, TEST_ATTR_BOUND_DT)
        eq_(phone.confirmed, TEST_ATTR_CONFIRMED_DT)
        eq_(phone.admitted, TEST_ATTR_ADMITTED_DT)
        eq_(phone.secured, TEST_ATTR_SECURED_DT)

        for key in PHONE_OPERATION_TEST_DATA:
            if key == 'type':
                continue

            expected = PHONE_OPERATION_TEST_DATA_PARSED[key]

            eq_(
                getattr(phone.operation, key),
                expected,
                [key, getattr(phone.operation, key), expected],
            )

    def test_set_as_secure(self):
        """
        На аккаунте есть один телефон, он же указан в secure и default.
        """
        acc = self.get_account(secure='999')
        phone = acc.phones.by_id(1)

        ok_(not acc.phones.secure)
        ok_(not phone.secured)

        phone.set_as_secure()

        eq_(acc.phones.secure, phone)
        eq_(phone.secured, DatetimeNow())

    def test_by_stred_number_found(self):
        """
        Вызовем phones.by_number с существующим номером телефона (строкой).
        """
        account = self.get_account(phone_number=u'+79012233444')
        eq_(
            account.phones.by_number(u'+79012233444').number,
            PhoneNumber.parse(u'+79012233444'),
        )

    def test_by_typed_number_found(self):
        """
        Вызовем phones.by_number с существующим номером телефона (типом).
        """
        account = self.get_account(phone_number=PhoneNumber.parse(u'+79012233444'))
        eq_(
            account.phones.by_number(u'+79012233444').number,
            PhoneNumber.parse(u'+79012233444'),
        )

    def test_by_number_not_found(self):
        """
        Вызовем phones.by_number с несуществующим номером телефона.
        """
        account = self.get_account(phone_number='+79030915478')
        eq_(account.phones.by_number(u'+79012233444'), None)

    def test_has_number_not_found(self):
        """
        Вызовем phones.has_number с несуществующим номером телефона.
        """
        account = self.get_account(phone_number='+79030915478')
        ok_(not account.phones.has_number(u'+79012233444'))

    def test_has_stred_number_found(self):
        """
        Вызовем phones.has_number с существующим номером телефона (строкой).
        """
        account = self.get_account(phone_number=u'+79012233444')
        ok_(account.phones.has_number(u'+79012233444'))

    def test_has_typed_number_found(self):
        """
        Вызовем phones.has_number с существующим номером телефона (строкой).
        """
        account = self.get_account(phone_number=PhoneNumber.parse(u'+79012233444'))
        ok_(account.phones.has_number(u'+79012233444'))

    def test_remove_phone__phone_in_phone_id2(self):
        """
        Удаляем номер, который задействован в другой операции.
        """
        account = Account().parse({
            u'phones': {
                22: dict(
                    id=22,
                    attributes=dict(ALL_ATTRS, secured=None),
                    operation=None,
                ),
                44: dict(
                    id=44,
                    attributes=dict(
                        ALL_ATTRS,
                        number=TEST_PHONE_NUMBER2,
                        secure=TEST_ATTR_SECURED_AT,
                    ),
                    operation=dict(
                        PHONE_OPERATION_TEST_DATA,
                        id=441,
                        type=u'change',
                        phone_id2=22,
                    )
                ),
            },
            u'phones.secure': 44,
            u'phones.default': 44,
        })

        ok_(account.phones.has_id(22))
        ok_(account.phones.by_id(44).operation)

        account.phones.remove(22)

        ok_(not account.phones.has_id(22))
        ok_(not account.phones.by_id(44).operation)

    @raises(RemoveBankPhoneNumberError)
    def test_remove_phone__phone_in_bank_phonenumber_alias(self):
        """
        Удаляем номер, который является банковским алиасом.
        """
        account = self.get_account(phone_number=TEST_PHONE_NUMBER, is_bank=True)
        account.bank_phonenumber_alias = BankPhoneNumberAlias(parent=account, alias=TEST_PHONE_NUMBER_DIGITAL)

        ok_(account.phones.has_id(1))

        account.phones.remove(1)

    @raises(ValueError)
    def test_by_operation_id__id_undefined(self):
        account = self.get_account(phone_number=TEST_PHONE_NUMBER)
        phone = account.phones.by_number(TEST_PHONE_NUMBER)
        phone.create_operation(u'bind')

        self.account.phones.by_operation_id(phone.operation.id)

    @raises(ValueError)
    def test_unbound_phone__in_operaton(self):
        account = self.get_account(phone_number=TEST_PHONE_NUMBER)
        phone = account.phones.by_number(TEST_PHONE_NUMBER)
        phone.create_operation(u'bind')

        account.phones.unbound_phone(phone)

    @raises(ValueError)
    def test_secure_not_bound_phone(self):
        account = self.get_account()
        phone = account.phones.by_id(1)
        phone.bound = None

        account.phones.secure = phone

    @raises(ValueError)
    def test_secure_not_secured_phone(self):
        account = self.get_account()
        phone = account.phones.by_id(1)
        phone.secured = None

        account.phones.secure = phone

    def test_mask_inconsistency(self):
        data1 = {
            'uid': 1,
            'phones': {
                1: {'id': 1, 'attributes': {'created': TEST_ATTR_CREATED_AT}},
                2: {'id': 2, 'attributes': {'admitted': TEST_ATTR_ADMITTED_AT}},
                3: {
                    'id': 3,
                    'attributes': {
                        'admitted': TEST_ATTR_ADMITTED_AT,
                    },
                },
                4: {
                    'id': 4,
                    'attributes': {'number': SIMPLE_PHONE.e164},
                    'operation': dict(
                        PHONE_OPERATION_TEST_DATA,
                        id=31,
                        type='change',
                        phone_id2=3,
                    ),
                },
            },
            'phones.default': 2,
            'phones.secure': 2,
        }
        data2 = deepcopy(data1)

        account = Account().parse(data1)

        eq_(len(account.phones.all()), 1)
        assert_is_none(account.phones.secure)
        assert_is_none(account.phones.default)

        phone = account.phones.by_id(4)
        ok_(not phone.operation)

        eq_(data1, data2)


@with_settings(
    BLACKBOX_ATTRIBUTES=[],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[u'created', u'secured'],
)
class TestPhonesModelAndBuilder(PassportTestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.blackbox = Blackbox(blackbox=u'http://bla.ckb.ox/')
        self.blackbox_faker = FakeBlackbox()
        self.blackbox_faker.start()

    def tearDown(self):
        self.blackbox_faker.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.blackbox_faker
        del self.fake_tvm_credentials_manager

    def test_account_phones_is_empty_when_no_phones_in_builder_response(self):
        self.blackbox_faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phones=None, phone_operations=None),
        )
        user_info = self.blackbox.userinfo(uid=4)

        account = Account().parse(user_info)

        ok_(not account.phones.all())

    def test_account_phones_is_empty_when_empty_phones_in_builder_response(self):
        self.blackbox_faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phones=[], phone_operations=None),
        )
        user_info = self.blackbox.userinfo(uid=4, phones=u'all')

        account = Account().parse(user_info)

        ok_(not account.phones.all())

    def test_account_with_phone_and_attributes_and_no_operation(self):
        self.blackbox_faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{
                    u'id': 71,
                    u'number': u'+79043322111',
                    u'created': datetime(2009, 3, 11, 4, 17, 5),
                    u'bound': datetime(2007, 3, 12, 4, 4, 5),
                    u'confirmed': datetime(2006, 2, 2, 14, 4, 25),
                    u'admitted': datetime(2008, 5, 2, 15, 7, 2),
                    u'secured': datetime(2005, 5, 2, 15, 7, 2),
                }],
                phone_operations=None,
            ),
        )
        user_info = self.blackbox.userinfo(
            uid=4,
            phones=u'all',
            phone_attributes=[
                u'number',
                u'created',
                u'bound',
                u'confirmed',
                u'admitted',
                u'secured',
            ],
        )

        account = Account().parse(user_info)

        phones = account.phones.all()
        eq_(len(phones), 1)
        ok_(71 in phones)
        phone = phones[71]
        eq_(phone.number, PhoneNumber.parse(u'+79043322111'))
        eq_(phone.created, datetime(2009, 3, 11, 4, 17, 5))
        eq_(phone.bound, datetime(2007, 3, 12, 4, 4, 5))
        eq_(phone.confirmed, datetime(2006, 2, 2, 14, 4, 25))
        eq_(phone.admitted, datetime(2008, 5, 2, 15, 7, 2))
        eq_(phone.secured, datetime(2005, 5, 2, 15, 7, 2))
        ok_(not phone.operation)

    def test_account_with_phone_and_no_attributes_and_no_operation(self):
        self.blackbox_faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{
                    u'id': 71,
                    u'number': SIMPLE_PHONE.e164,
                }],
                phone_operations=None,
            ),
        )
        user_info = self.blackbox.userinfo(
            uid=4,
            phones=u'all',
            phone_attributes=[u'number'],
        )

        account = Account().parse(user_info)

        phones = account.phones.all()
        eq_(len(phones), 1)
        ok_(71 in phones)
        phone = phones[71]
        eq_(phone.number, SIMPLE_PHONE)
        eq_(phone.created, Undefined)
        eq_(phone.bound, Undefined)
        eq_(phone.confirmed, Undefined)
        eq_(phone.admitted, Undefined)
        eq_(phone.secured, Undefined)
        ok_(not phone.operation)

    def test_account_with_phone_and_no_attributes_and_zombie_operation(self):
        self.blackbox_faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{
                    u'id': 71,
                    u'created': TEST_ATTR_CREATED_DT,
                    u'number': SIMPLE_PHONE.e164,
                }],
                phone_operations=[{
                    u'phone_id': 73,
                    u'phone_number': u'+79028877666',
                }],
            ),
        )
        user_info = self.blackbox.userinfo(
            uid=4,
            phones=u'all',
            phone_attributes=[u'number'],
            need_phone_operations=True,
        )

        account = Account().parse(user_info)

        phones = account.phones.all()
        phone = phones[71]
        ok_(not phone.operation)

    def test_account_with_phone_and_operation(self):
        self.blackbox_faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[
                    {
                        u'id': 71,
                        u'created': TEST_ATTR_CREATED_DT,
                        u'number': SIMPLE_PHONE.e164,
                    },
                    {
                        u'id': 72,
                        u'created': TEST_ATTR_CREATED_DT,
                        u'number': TEST_PHONE_NUMBER,
                    },
                ],
                phone_operations=[{
                    u'id': 2,
                    u'phone_id': 71,
                    u'phone_number': u'+79028877666',
                    u'type': u'bind',
                    u'started': datetime(2000, 5, 1, 12, 0, 5),
                    u'finished': datetime(2000, 6, 1, 12, 0, 4),
                    u'code_value': u'2323',
                    u'code_checks_count': 3,
                    u'code_send_count': 2,
                    u'code_last_sent': datetime(2000, 5, 1, 12, 1, 5),
                    u'code_confirmed': datetime(2000, 5, 1, 12, 1, 35),
                    u'password_verified': datetime(2000, 5, 1, 12, 1, 35),
                    u'flags': PhoneOperationFlags(1),
                    u'phone_id2': 72,
                }],
            ),
        )
        user_info = self.blackbox.userinfo(
            uid=4,
            phones=u'all',
            phone_attributes=[u'number'],
            need_phone_operations=True,
        )

        account = Account().parse(user_info)
        phones = account.phones.all()
        phone = phones[71]

        ok_(phone.operation)
        eq_(phone.operation.id, 2)
        eq_(phone.operation.phone_id, 71)
        eq_(phone.operation.security_identity, 79028877666)
        eq_(phone.operation.type, u'bind')
        eq_(phone.operation.started, datetime(2000, 5, 1, 12, 0, 5))
        eq_(phone.operation.finished, datetime(2000, 6, 1, 12, 0, 4))
        eq_(phone.operation.code_value, u'2323')
        eq_(phone.operation.code_checks_count, 3)
        eq_(phone.operation.code_send_count, 2)
        eq_(phone.operation.code_last_sent, datetime(2000, 5, 1, 12, 1, 5))
        eq_(phone.operation.code_confirmed, datetime(2000, 5, 1, 12, 1, 35))
        eq_(phone.operation.password_verified, datetime(2000, 5, 1, 12, 1, 35))
        eq_(phone.operation.flags, PhoneOperationFlags(1))
        eq_(phone.operation.phone_id2, 72)

    def test_account_with_phone_and_nake_operation(self):
        self.blackbox_faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{
                    u'id': 71,
                    u'created': TEST_ATTR_CREATED_DT,
                    u'number': SIMPLE_PHONE.e164,
                }],
                phone_operations=[{
                    u'phone_id': 71,
                    u'phone_number': u'+79028877666',
                    u'type': u'remove',
                    u'started': None,
                    u'finished': None,
                    u'code_value': None,
                    u'code_checks_count': None,
                    u'code_send_count': None,
                    u'code_last_sent': None,
                    u'code_confirmed': None,
                    u'password_verified': None,
                    u'flags': None,
                    u'phone_id2': None,
                }],
            ),
        )
        user_info = self.blackbox.userinfo(
            uid=4,
            phones=u'all',
            phone_attributes=[u'number'],
            need_phone_operations=True,
        )

        account = Account().parse(user_info)
        phones = account.phones.all()
        phone = phones[71]

        ok_(phone.operation)
        eq_(phone.operation.phone_id, 71)
        eq_(phone.operation.security_identity, 79028877666)
        eq_(phone.operation.type, u'remove')
        eq_(phone.operation.started, Undefined)
        eq_(phone.operation.finished, Undefined)
        eq_(phone.operation.code_value, Undefined)
        eq_(phone.operation.code_checks_count, 0)
        eq_(phone.operation.code_send_count, 0)
        eq_(phone.operation.code_last_sent, Undefined)
        eq_(phone.operation.code_confirmed, Undefined)
        eq_(phone.operation.password_verified, Undefined)
        eq_(phone.operation.flags, PhoneOperationFlags(0))
        eq_(phone.operation.phone_id2, Undefined)

    def test_account_with_phone_and_secure_operation(self):
        self.blackbox_faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{
                    u'id': 71,
                    u'created': TEST_ATTR_CREATED_DT,
                    u'number': SIMPLE_PHONE.e164,
                }],
                phone_operations=[{
                    u'phone_id': 71,
                    u'security_identity': SECURITY_IDENTITY,
                }],
            ),
        )
        user_info = self.blackbox.userinfo(
            uid=4,
            phones=u'all',
            phone_attributes=[u'number'],
            need_phone_operations=True,
        )

        account = Account().parse(user_info)
        phones = account.phones.all()
        phone = phones[71]

        ok_(phone.operation)
        eq_(phone.operation.security_identity, SECURITY_IDENTITY)

    def test_account_get_by_phone_number(self):
        self.blackbox_faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 71, u'number': TEST_PHONE_NUMBER}],
            ),
        )
        user_info = self.blackbox.userinfo(
            uid=1,
            phones=u'all',
            phone_attributes=[u'number'],
        )

        account = Account().parse(user_info)
        phone = account.phones.by_id(71)
        ok_(phone)

        number = PhoneNumber.parse(TEST_PHONE_NUMBER)
        eq_(account.phones.by_number(number), phone)
        eq_(account.phones.by_number(number.e164), phone)

        ok_(account.phones.has_number(number))
        ok_(account.phones.has_number(number.e164))
