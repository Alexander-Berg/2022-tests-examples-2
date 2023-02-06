# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox.parsers import PHONE_OP_TYPE_IDX
from passport.backend.core.db.faker.db import (
    attribute_table_insert_on_duplicate_update_key as attr_insert_odk,
    extended_attribute_table_delete as ext_attr_del,
    extended_attribute_table_insert_on_duplicate_key as ext_at_insert_odk,
    FakeDB,
    get_transaction,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    attributes_table as attr_t,
    extended_attributes_table as ext_attr_t,
    phone_bindings_history_table as ph_b_h_t,
    phone_bindings_table as ph_b_t,
    phone_operations_table as p_op_t,
)
from passport.backend.core.dbmanager.exceptions import DBIntegrityError
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import (
    ALIAS_NAME_TO_TYPE as ALT,
    ATTRIBUTE_NAME_TO_TYPE,
    EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING,
    EXTENDED_ATTRIBUTES_PHONE_TYPE,
)
from passport.backend.core.logging_utils.loggers import DummyLogger
from passport.backend.core.models.account import Account
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.models.phones.faker import (
    build_account,
    build_mark_operation,
    build_phone_being_bound,
    build_phone_bound,
    build_phone_secured,
    build_remove_operation,
    build_secure_phone_being_bound,
    build_simple_replaces_secure_operations,
)
from passport.backend.core.models.phones.phones import (
    Operation,
    PhoneBinding,
)
from passport.backend.core.serializers.eav.account import AccountEavSerializer
from passport.backend.core.serializers.eav.exceptions import (
    EavDeletedObjectNotFound,
    EavUpdatedObjectNotFound,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
    unixtime,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.undefined import Undefined
from passport.backend.utils.common import deep_merge
from passport.backend.utils.string import smart_bytes
from passport.backend.utils.time import (
    datetime_to_unixtime,
    unixtime_to_datetime,
    zero_datetime,
)
import six
from sqlalchemy.sql.expression import (
    and_,
    or_,
)


TEST_UID = 1
TEST_PHONE = '+79030915478'
TEST_PHONE2 = '+79030915400'
TEST_PHONE3 = '+79259164525'
TEST_PHONE_ID = 10
TEST_PHONE_ID2 = 20
TEST_PHONE_ID3 = 30

TEST_ATTR_CREATED = 1234567892
TEST_ATTR_BOUND = 1234567893
TEST_ATTR_CONFIRMED = 1234567894
TEST_ATTR_ADMITTED = 1234567895
TEST_ATTR_SECURED = 1234567896
TEST_ATTR_BOUND2 = 9876543213

TEST_ATTR_BOUND_DT = unixtime_to_datetime(TEST_ATTR_BOUND)
TEST_ATTR_BOUND2_DT = unixtime_to_datetime(TEST_ATTR_BOUND2)

TEST_NEW_SECURED_DT = datetime(2000, 1, 2, 1, 2, 3)
TEST_NEW_SECURED = int(datetime_to_unixtime(TEST_NEW_SECURED_DT))

TEST_STARTED_DT = datetime(2000, 1, 22, 12, 34, 56)

TEST_OPERATION_ID = 1
TEST_OPERATION = {
    'id': TEST_OPERATION_ID,
    'type': 'bind',
    'password_verified': unixtime(2000, 1, 23, 12, 34, 56),
    'started': unixtime(2000, 1, 22, 12, 34, 56),
}

PHONE_OP_PASSWORD_VERIFIED_DT = datetime(2000, 1, 23, 12, 34, 56)

TEST_PHONE_DICT = {
    'id': TEST_PHONE_ID,
    'attributes': {
        'number': TEST_PHONE,
        'created': TEST_ATTR_CREATED,
        'bound': TEST_ATTR_BOUND,
        'confirmed': TEST_ATTR_CONFIRMED,
        'admitted': TEST_ATTR_ADMITTED,
        'secured': TEST_ATTR_SECURED,
    },
    'operation': TEST_OPERATION,
    'binding': {
        'uid': TEST_UID,
        'type': 'current',
        'phone_number': PhoneNumber.parse(TEST_PHONE),
        'phone_id': TEST_PHONE_ID,
        'binding_time': TEST_ATTR_BOUND,
        'should_ignore_binding_limit': 0,
    },
}

TEST_PHONE_DICT2 = {
    'id': TEST_PHONE_ID2,
    'attributes': {
        'number': TEST_PHONE2,
        'confirmed': TEST_ATTR_CONFIRMED,
    },
}


class TestPhonesBase(PassportTestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()

    def tearDown(self):
        self.db.stop()
        del self.db

    def check_db_ext_attr(self, entity_id, field_name, value):
        self.db.check_db_ext_attr(
            TEST_UID,
            EXTENDED_ATTRIBUTES_PHONE_TYPE,
            entity_id,
            field_name,
            value,
        )

    def check_db_attr(self, field_name, value):
        self.db.check_db_attr(TEST_UID, field_name, value)

    def check_db_attr_missing(self, field_name):
        self.db.check_db_attr_missing(TEST_UID, field_name)

    def check_db_ext_attr_missing(self, entity_id, field_name):
        self.db.check_db_ext_attr_missing(
            TEST_UID,
            EXTENDED_ATTRIBUTES_PHONE_TYPE,
            entity_id,
            field_name,
        )

    def check_phone_binding(self, number=TEST_PHONE, phone_id=TEST_PHONE_ID,
                            bound=TEST_ATTR_BOUND_DT, flags=0):
        self.db.check_line(
            'phone_bindings',
            uid=TEST_UID,
            phone_id=phone_id,
            db='passportdbshard1',
            expected_data={
                'uid': TEST_UID,
                'phone_id': phone_id,
                'number': int(number),
                'bound': bound,
                'flags': flags,
            },
        )

    def check_phone_binding_missing(self, phone):
        self.db.check_missing(
            'phone_bindings',
            uid=TEST_UID,
            phone_id=phone.id,
            db='passportdbshard1',
        )

    def check_phone_binding_history(self, number, bound):
        ok_(
            self.db.get(
                'phone_bindings_history',
                uid=TEST_UID,
                number=int(number),
                bound=bound,
                db='passportdbshard1',
            ),
        )

    @staticmethod
    def get_ext_attr_dict(entity_id, field_name, value):
        return {
            'uid': TEST_UID,
            'entity_type': EXTENDED_ATTRIBUTES_PHONE_TYPE,
            'entity_id': entity_id,
            'type': EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING[field_name],
            'value': value.encode('utf8') if isinstance(value, six.text_type) else value,
        }

    @staticmethod
    def get_attr_dict(field_name, value):
        return {
            'uid': TEST_UID,
            'type': ATTRIBUTE_NAME_TO_TYPE[field_name],
            'value': smart_bytes(value),
        }

    @staticmethod
    def get_ext_attr_query(entity_id, field_name):
        return and_(
            ext_attr_t.c.entity_type == EXTENDED_ATTRIBUTES_PHONE_TYPE,
            ext_attr_t.c.entity_id == entity_id,
            ext_attr_t.c.type == EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING[field_name],
        )

    @staticmethod
    def get_account(phones=None):
        data = {
            'uid': TEST_UID,
            'aliases': {
                str(ALT['portal']): 'test',
            },
            'subscriptions': {8: {'sid': 8, 'login_rule': 1}},
        }
        if phones:
            data.update({
                u'phones': {phone[u'id']: phone for phone in phones},
            })

        return Account().parse(data)

    def get_insert_phone_binding_query(self, number=TEST_PHONE, phone_id=TEST_PHONE_ID,
                                       bound=TEST_ATTR_BOUND_DT, flags=0):
        return ph_b_t.insert().values(
            uid=TEST_UID,
            number=int(number),
            phone_id=phone_id,
            bound=bound,
            flags=flags,
        )

    @staticmethod
    def get_delete_phone_binding_query(phone_id):
        return ph_b_t.delete().where(
            and_(ph_b_t.c.uid == TEST_UID, ph_b_t.c.phone_id == phone_id),
        )

    def get_insert_phone_binding_history_query(self, number=TEST_PHONE, bound=TEST_ATTR_BOUND_DT):
        return ph_b_h_t.insert().values(
            uid=TEST_UID,
            number=int(number),
            bound=bound,
        )

    @staticmethod
    def get_expected_ext_attr_insert_query(*queries):
        return ext_at_insert_odk().values(queries)

    @staticmethod
    def get_expected_attr_insert_query(*queries):
        return attr_insert_odk().values(queries)

    @staticmethod
    def get_expected_attr_delete_query(attr_names):
        types = sorted([ATTRIBUTE_NAME_TO_TYPE[attr_name] for attr_name in attr_names])
        return attr_t.delete().where(and_(attr_t.c.uid == TEST_UID, attr_t.c.type.in_(types)))

    @staticmethod
    def get_expected_ext_attr_delete_query(*queries):
        return ext_attr_del().where(and_(ext_attr_t.c.uid == TEST_UID, or_(*queries)))

    @staticmethod
    def get_insert_phone_operation_query(**operation_data):
        operation_data['type'] = PHONE_OP_TYPE_IDX[operation_data['type']]
        return p_op_t.insert().values(**operation_data)

    @staticmethod
    def get_update_phone_operation_query(operationid, uid=TEST_UID, **operation_data):
        op_type = operation_data.get('type')
        if op_type:
            operation_data['type'] = PHONE_OP_TYPE_IDX[op_type]

        clause = and_(p_op_t.c.uid == uid, p_op_t.c.id == operationid)
        return p_op_t.update().where(clause).values(uid=uid, **operation_data)

    @staticmethod
    def get_delete_phone_operation_query(where_clause, uid=TEST_UID):
        return p_op_t.delete().where(and_(p_op_t.c.uid == uid, where_clause))

    def check_db_phone_operation(self, data, id_=1, uid=TEST_UID, phone_id=TEST_PHONE_ID):
        data.update(dict(uid=uid, phone_id=phone_id, id=id_))

        if 'started' not in data:
            data['started'] = DatetimeNow()

        data['type'] = PHONE_OP_TYPE_IDX[data['type']]

        for col in p_op_t.c:
            if col.default is None:
                continue

            if col.name not in data:
                data[col.name] = col.default.arg

        for key in ['finished', 'code_last_sent', 'code_confirmed', 'password_verified']:
            if key not in data:
                data[key] = zero_datetime

        self.db.check_line(
            'phone_operations',
            data,
            db='passportdbshard1',
            uid=TEST_UID,
            phone_id=phone_id,
            id=id_,
        )

    @staticmethod
    def get_update_phone_bindings_query(phone_id, uid=TEST_UID, old_bound=None,
                                        old_number=None, **kwargs):
        conds = [
            ph_b_t.c.uid == uid,
            ph_b_t.c.phone_id == phone_id,
        ]
        if old_bound is not None:
            conds.append(ph_b_t.c.bound == old_bound)
        if old_number is not None:
            conds.append(ph_b_t.c.number == int(old_number))
        if kwargs.get('number'):
            kwargs['number'] = int(kwargs['number'])
        return ph_b_t.update().values(**kwargs).where(and_(*conds))


class TestPhonesSerialization(TestPhonesBase):
    def test_phone_serialization(self):
        """
        На аккаунте есть телефон, проверим сериализацию всех его полей.
        """
        account = self.get_account([
            TEST_PHONE_DICT,
            TEST_PHONE_DICT2,
        ])
        clean_account = self.get_account()
        queries = AccountEavSerializer().serialize(clean_account, account, diff(clean_account, account))

        expected = get_transaction(
            self.get_expected_ext_attr_insert_query(
                self.get_ext_attr_dict(TEST_PHONE_ID, 'number', TEST_PHONE[1:]),
                self.get_ext_attr_dict(TEST_PHONE_ID, 'created', str(TEST_ATTR_CREATED)),
                self.get_ext_attr_dict(TEST_PHONE_ID, 'bound', str(TEST_ATTR_BOUND)),
                self.get_ext_attr_dict(TEST_PHONE_ID, 'confirmed', str(TEST_ATTR_CONFIRMED)),
                self.get_ext_attr_dict(TEST_PHONE_ID, 'admitted', str(TEST_ATTR_ADMITTED)),
                self.get_ext_attr_dict(TEST_PHONE_ID, 'secured', str(TEST_ATTR_SECURED)),
            ),
            self.get_insert_phone_binding_query(),
            self.get_insert_phone_binding_history_query(),
            self.get_insert_phone_operation_query(
                id=1,
                phone_id=TEST_PHONE_ID,
                uid=TEST_UID,
                type='bind',
                password_verified=PHONE_OP_PASSWORD_VERIFIED_DT,
                code_send_count=0,
                flags=0,
                code_checks_count=0,
                started=TEST_STARTED_DT,
            ),
            self.get_expected_ext_attr_insert_query(
                self.get_ext_attr_dict(TEST_PHONE_ID2, 'number', TEST_PHONE2[1:]),
                self.get_ext_attr_dict(TEST_PHONE_ID2, 'confirmed', str(TEST_ATTR_CONFIRMED)),
            ),
        )

        eq_eav_queries(queries, expected, inserted_keys=[TEST_OPERATION_ID])

        self.db._serialize_to_eav(account)
        self.check_db_ext_attr(TEST_PHONE_ID, 'number', TEST_PHONE[1:])
        self.check_db_ext_attr(TEST_PHONE_ID, 'confirmed', str(TEST_ATTR_CONFIRMED))
        self.check_db_ext_attr(TEST_PHONE_ID2, 'number', TEST_PHONE2[1:])
        self.check_db_ext_attr(TEST_PHONE_ID2, 'confirmed', str(TEST_ATTR_CONFIRMED))

        self.check_db_phone_operation({
            'password_verified': PHONE_OP_PASSWORD_VERIFIED_DT,
            'type': 'bind',
            'started': TEST_STARTED_DT,
        })

    def test_create_first_phone(self):
        """
        Создаем на аккаунте первый телефон, проверяем составленные запросы и записанное в базу.
        """

        # Создаем чистый аккаунт без телефонов.
        account = self.get_account()
        snapshot = account.snapshot()

        # Добавляем телефон.
        phone = account.phones.create(number=TEST_PHONE)
        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))
        expected = get_transaction(
            self.get_expected_ext_attr_insert_query(
                self.get_ext_attr_dict(phone.id, 'number', TEST_PHONE[1:]),
                self.get_ext_attr_dict(phone.id, 'created', TimeNow()),
            ),
            self.get_insert_phone_binding_query(
                number=TEST_PHONE,
                phone_id=phone.id,
                bound=zero_datetime
            ),
        )
        eq_eav_queries(queries, expected)

        self.db._serialize_to_eav(account)
        self.check_db_ext_attr(phone.id, 'number', TEST_PHONE[1:])
        self.check_db_ext_attr(phone.id, 'created', TimeNow())

        self.check_db_attr_missing('phones.default')

    def test_delete_phone(self):
        """
        Удаление телефона целиком. Проверим, что указанный телефон удалился,
        а соседний остался на месте.
        """
        account = self.get_account([
            TEST_PHONE_DICT,
            TEST_PHONE_DICT2,
        ])
        snapshot = account.snapshot()
        account.phones.remove(TEST_PHONE_ID)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        expected = get_transaction(
            self.get_delete_phone_operation_query(
                p_op_t.c.id == TEST_OPERATION['id'],
            ),
            self.get_delete_phone_binding_query(TEST_PHONE_ID),
            self.get_expected_ext_attr_delete_query(
                self.get_ext_attr_query(TEST_PHONE_ID, 'number'),
                self.get_ext_attr_query(TEST_PHONE_ID, 'created'),
                self.get_ext_attr_query(TEST_PHONE_ID, 'bound'),
                self.get_ext_attr_query(TEST_PHONE_ID, 'confirmed'),
                self.get_ext_attr_query(TEST_PHONE_ID, 'admitted'),
                self.get_ext_attr_query(TEST_PHONE_ID, 'secured'),
            ),
        )

        eq_eav_queries(queries, expected, row_count=[1, 1])

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

        self.check_db_ext_attr_missing(TEST_PHONE_ID, 'number')
        self.check_db_ext_attr_missing(TEST_PHONE_ID, 'confirmed')

        self.check_db_ext_attr(TEST_PHONE_ID2, 'number', TEST_PHONE2[1:])
        self.check_db_ext_attr(TEST_PHONE_ID2, 'confirmed', str(TEST_ATTR_CONFIRMED))

    def test_delete_phone_without_operations(self):
        account = self.get_account(
            phones=[{
                u'id': TEST_PHONE_ID,
                u'attributes': {u'number': TEST_PHONE},
            }],
        )

        ok_(account.phones.by_id(TEST_PHONE_ID).operation is Undefined)
        snapshot = account.snapshot()

        account.phones.by_id(TEST_PHONE_ID).confirmed = None

        account.phones.remove(TEST_PHONE_ID)
        ok_(not account.phones.has_id(TEST_PHONE_ID))

        queries = AccountEavSerializer().serialize(
            snapshot,
            account,
            diff(snapshot, account),
        )

        expected = get_transaction(
            self.get_expected_ext_attr_delete_query(
                self.get_ext_attr_query(TEST_PHONE_ID, 'number'),
            ),
        )

        eq_eav_queries(queries, expected)

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

    def test_create_account_with_phone_and_no_operation(self):
        account = self.get_account(phones=[{
            u'id': TEST_PHONE_ID,
            u'attributes': {u'number': TEST_PHONE},
            u'operation': None,
        }])

        self.db._serialize_to_eav(account, None)
        self.check_db_ext_attr(TEST_PHONE_ID, 'number', TEST_PHONE[1:])

    def test_change_and_delete_phone_attribute(self):
        """
        У телефона удален один атрибут, другой изменен.
        """
        account = self.get_account([
            TEST_PHONE_DICT,
        ])
        snapshot = account.snapshot()

        account.phones.by_id(TEST_PHONE_ID).confirmed = None
        account.phones.by_id(TEST_PHONE_ID).secured = TEST_NEW_SECURED_DT

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        expected = get_transaction(
            self.get_expected_ext_attr_insert_query(
                self.get_ext_attr_dict(TEST_PHONE_ID, 'secured', str(TEST_NEW_SECURED)),
            ),
            self.get_expected_ext_attr_delete_query(
                self.get_ext_attr_query(TEST_PHONE_ID, 'confirmed'),
            ),
        )

        eq_eav_queries(queries, expected)

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

        self.check_db_ext_attr(TEST_PHONE_ID, 'secured', str(TEST_NEW_SECURED))
        self.check_db_ext_attr_missing(TEST_PHONE_ID, 'confirmed')

    def test_update_phone_attributes(self):
        """
        У телефона удален один атрибут, другой изменен.
        """
        account = self.get_account([
            TEST_PHONE_DICT,
        ])

        snapshot = account.snapshot()

        account.phones.by_id(TEST_PHONE_ID).operation.type = 'remove'
        account.phones.by_id(TEST_PHONE_ID).operation.code_value = 'abc'

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        expected = get_transaction(
            self.get_update_phone_operation_query(TEST_OPERATION['id'], type='remove', code_value='abc'),
        )

        eq_eav_queries(queries, expected)

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

        self.check_db_phone_operation(
            {
                'type': 'remove',
                'code_value': 'abc',
                'password_verified': PHONE_OP_PASSWORD_VERIFIED_DT,
                'started': TEST_STARTED_DT,
            },
            id_=TEST_OPERATION['id'],
        )

    def test_operation_flags(self):
        """
        Проверим, что нормально сохраняется значение флагов на операции.
        """
        account = self.get_account([
            TEST_PHONE_DICT,
        ])

        phone = account.phones.by_id(TEST_PHONE_ID)
        eq_(phone.operation.flags, PhoneOperationFlags(0))

        snapshot = account.snapshot()

        phone.operation.flags.aliasify = True
        phone.operation.flags.should_ignore_binding_limit = True

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        expected = get_transaction(
            self.get_update_phone_operation_query(TEST_OPERATION['id'], flags=3),
        )

        eq_eav_queries(queries, expected)

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

        self.check_db_phone_operation(
            {
                'type': 'bind',
                'flags': 3,
                'password_verified': PHONE_OP_PASSWORD_VERIFIED_DT,
                'started': TEST_STARTED_DT,
            },
            id_=TEST_OPERATION['id'],
        )

        # Проверим, что если выставить дефолтное значение флага (0), то запрос в базу все равно будет.
        snapshot = account.snapshot()

        phone.operation.flags.aliasify = False
        phone.operation.flags.should_ignore_binding_limit = False

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        expected = get_transaction(
            self.get_update_phone_operation_query(TEST_OPERATION['id'], flags=0),
        )

        eq_eav_queries(queries, expected)

        self.db._serialize_to_eav(account, old_instance=snapshot)
        self.check_db_phone_operation(
            {
                'type': 'bind',
                'flags': 0,
                'password_verified': PHONE_OP_PASSWORD_VERIFIED_DT,
                'started': TEST_STARTED_DT,
            },
            id_=TEST_OPERATION['id'],
        )

    def test_change_operation_increment_fields(self):
        """
        У телефонных операций есть поле code_checks_count, нельзя делать
        update с абсолютным значением, потому что тогда в случае логической
        гонки получим неверные данные, вместо этого в запросе будет
        code_checks_count = phone_operations.code_checks_count + <изменение в локальной копии>
        """
        account = self.get_account([TEST_PHONE_DICT])
        snapshot = account.snapshot()

        account.phones.by_id(TEST_PHONE_ID).operation.code_checks_count += 1

        d = diff(snapshot, account)
        s = AccountEavSerializer()
        queries = s.serialize(snapshot, account, d)

        expected = get_transaction(
            self.get_update_phone_operation_query(
                TEST_OPERATION['id'],
                code_checks_count=p_op_t.c.code_checks_count + 1,
            ),
        )

        eq_eav_queries(queries, expected)

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

        self.check_db_phone_operation(
            {
                'type': 'bind',
                'code_checks_count': 1,
                'password_verified': PHONE_OP_PASSWORD_VERIFIED_DT,
                'started': TEST_STARTED_DT,
            },
            id_=TEST_OPERATION['id'],
        )

        # Сделаем сразу два обновления в базе. Текущее значение
        # code_checks_count (1) должно поменяться в итоге на 3, а не на 2.
        snapshot = account.snapshot()
        account.phones.by_id(TEST_PHONE_ID).operation.code_checks_count += 1

        # Делаем запросы в БД дважды, каждый раз на нашем аккаунте
        # code_checks_count == 2
        for _ in range(2):
            eq_(account.phones.by_id(TEST_PHONE_ID).operation.code_checks_count, 2)
            self.db._serialize_to_eav(account, old_instance=snapshot)

        # И в результате в базе code_checks_count == 3
        self.check_db_phone_operation(
            {
                'type': 'bind',
                'code_checks_count': 3,
                'password_verified': PHONE_OP_PASSWORD_VERIFIED_DT,
                'started': TEST_STARTED_DT,
            },
            id_=TEST_OPERATION['id'],
        )

    def test_overwrite_default_by_default(self):
        """
        Значение атрибута изменено с одного дефолтного значения на другое.
        При этом не нужно генерировать запросов на этот атрибут.
        """

        account = self.get_account([
            TEST_PHONE_DICT,
        ])
        account.phones.by_id(TEST_PHONE_ID).confirmed = ''
        snapshot = account.snapshot()

        account.phones.by_id(TEST_PHONE_ID).confirmed = None

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(queries, [])

    def test_create_phone_operation(self):
        """Проверка склеивания запросов внутри транзакции."""
        test_phone_dict = dict(TEST_PHONE_DICT)
        del test_phone_dict['operation']
        account = self.get_account([
            test_phone_dict,
        ])

        snapshot = account.snapshot()

        account.phones.by_id(TEST_PHONE_ID).create_operation(type='bind')

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        expected = get_transaction(
            self.get_insert_phone_operation_query(
                phone_id=TEST_PHONE_ID,
                uid=TEST_UID,
                type='bind',
                flags=0,
                code_send_count=0,
                code_checks_count=0,
                started=DatetimeNow(),
            ),
        )

        eq_eav_queries(queries, expected, inserted_keys=[TEST_OPERATION_ID])

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

        self.check_db_phone_operation(
            {'type': 'bind'},
            phone_id=TEST_PHONE_ID,
            id_=1,
        )

    def test_overwrite_operation_default_by_default(self):
        """
        Значение поля операции изменено с дефолтного значения на None или наоборот.
        При этом не нужно генерировать запросов в БД.
        """

        account = self.get_account([
            TEST_PHONE_DICT,
        ])
        op = account.phones.by_id(TEST_PHONE_ID).operation
        op.code_send_count = 0
        op.code_checks_count = 0
        op.flags = PhoneOperationFlags(0)

        # Проставим None
        snapshot = account.snapshot()
        op = account.phones.by_id(TEST_PHONE_ID).operation
        op.code_send_count = None
        op.code_checks_count = None
        op.flags = None

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))
        eq_eav_queries(queries, [])

        # Вернем обратно
        snapshot = account.snapshot()
        op = account.phones.by_id(TEST_PHONE_ID).operation
        op.code_send_count = 0
        op.code_checks_count = 0
        op.flags = PhoneOperationFlags(0)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))
        eq_eav_queries(queries, [])

    def test_overwrite_operation_non_default_by_default(self):
        """
        Значение поля операции изменено с какого-то осознанного значения на дефолтное.
        При этом должен быть запрос в БД.
        """

        account = self.get_account([
            TEST_PHONE_DICT,
        ])
        op = account.phones.by_id(TEST_PHONE_ID).operation
        op.code_send_count = 1
        op.code_checks_count = 1
        op.flags = PhoneOperationFlags(1)

        snapshot = account.snapshot()
        op = account.phones.by_id(TEST_PHONE_ID).operation
        op.code_send_count = 0
        op.code_checks_count = 0
        op.flags = PhoneOperationFlags(0)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))
        expected = get_transaction(
            self.get_update_phone_operation_query(
                TEST_OPERATION['id'],
                # Да, именно "+ (-1)", потому что иначе получим не тот SQL запрос.
                code_checks_count=p_op_t.c.code_checks_count + (-1),
                code_send_count=0,
                flags=0,
            ),
        )
        eq_eav_queries(queries, expected)

    def test_error_update_operation_without_id(self):
        account = self.get_account([
            TEST_PHONE_DICT2,
        ])

        # Руками создадим операцию без id
        op = Operation(type='bind')
        op.parent = account.phones.by_id(TEST_PHONE_ID2)
        account.phones.by_id(TEST_PHONE_ID2).operation = op

        snapshot = account.snapshot()

        account.phones.by_id(TEST_PHONE_ID2).operation.type = 'remove'

        try:
            self.db._serialize_to_eav(account, old_instance=snapshot)
        except ValueError as ex:
            eq_(str(ex), 'Operation identifier has to be set for update operation.')
        else:
            raise AssertionError('Exception not raised!')  # pragma: no cover

    def test_number_is_list_of_digits(self):
        account = default_account(uid=1).parse({
            'phones': [],
        })
        snapshot = account.snapshot()
        account.phones.create(u'+79026411724', existing_phone_id=TEST_PHONE_ID)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            get_transaction(
                self.get_expected_ext_attr_insert_query(
                    self.get_ext_attr_dict(TEST_PHONE_ID, 'number', u'79026411724'),
                    self.get_ext_attr_dict(TEST_PHONE_ID, 'created', TimeNow()),
                ),
                self.get_insert_phone_binding_query(
                    number='79026411724',
                    phone_id=TEST_PHONE_ID,
                    bound=zero_datetime
                ),
            ),
        )

    def test_replace_operation(self):
        account = self.get_account([TEST_PHONE_DICT])
        self.db._serialize_to_eav(account)

        snapshot = account.snapshot()

        phone = account.phones.by_id(TEST_PHONE_ID)
        phone.operation = None
        phone.create_operation('mark')

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))
        eq_eav_queries(
            queries,
            get_transaction(
                self.get_delete_phone_operation_query(
                    p_op_t.c.id == TEST_OPERATION['id'],
                ),
                self.get_insert_phone_operation_query(
                    phone_id=TEST_PHONE_ID,
                    uid=TEST_UID,
                    type='mark',
                    flags=0,
                    code_send_count=0,
                    code_checks_count=0,
                    started=DatetimeNow(),
                ),
            ),
            inserted_keys=[TEST_OPERATION_ID],
        )


class TestPhoneBindings(TestPhonesBase):
    def test_insert_phone_bindings(self):
        account = default_account(uid=TEST_UID)
        phone1 = account.phones.create(
            number=TEST_PHONE,
            existing_phone_id=TEST_PHONE_ID,
        )
        phone2 = account.phones.create(
            number=TEST_PHONE2,
            existing_phone_id=TEST_PHONE_ID2,
        )

        snapshot = account.snapshot()

        phone1.binding = PhoneBinding(time=TEST_ATTR_BOUND_DT)
        phone2.binding = PhoneBinding(time=TEST_ATTR_BOUND2_DT)

        queries = AccountEavSerializer().serialize(
            snapshot,
            account,
            diff(snapshot, account),
        )

        eq_eav_queries(
            queries,
            get_transaction(
                self.get_update_phone_bindings_query(
                    phone_id=TEST_PHONE_ID,
                    old_bound=zero_datetime,
                    bound=TEST_ATTR_BOUND_DT,
                    flags=0,
                ),
                self.get_insert_phone_binding_history_query(),
                self.get_update_phone_bindings_query(
                    phone_id=TEST_PHONE_ID2,
                    old_bound=zero_datetime,
                    bound=TEST_ATTR_BOUND2_DT,
                    flags=0,
                ),
                self.get_insert_phone_binding_history_query(
                    number=TEST_PHONE2,
                    bound=TEST_ATTR_BOUND2_DT,
                ),
            ),
            row_count=[1, 1],
        )

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

        self.check_phone_binding()
        self.check_phone_binding_history(number=TEST_PHONE, bound=TEST_ATTR_BOUND_DT)
        self.check_phone_binding(
            number=TEST_PHONE2,
            phone_id=TEST_PHONE_ID2,
            bound=TEST_ATTR_BOUND2_DT,
        )
        self.check_phone_binding_history(number=TEST_PHONE2, bound=TEST_ATTR_BOUND2_DT)

    def test_remove_phone_bindings(self):
        account = default_account(uid=TEST_UID)
        phone1 = account.phones.create(
            number=TEST_PHONE,
            existing_phone_id=TEST_PHONE_ID,
        )
        phone2 = account.phones.create(
            number=TEST_PHONE2,
            existing_phone_id=TEST_PHONE_ID2,
        )
        phone1.binding = PhoneBinding(time=TEST_ATTR_BOUND_DT)
        phone2.binding = PhoneBinding(time=TEST_ATTR_BOUND2_DT)

        snapshot = account.snapshot()

        phone1.binding = None
        phone2.binding = None

        queries = AccountEavSerializer().serialize(
            snapshot,
            account,
            diff(snapshot, account),
        )

        eq_eav_queries(
            queries,
            get_transaction(
                self.get_delete_phone_binding_query(TEST_PHONE_ID2),
                self.get_delete_phone_binding_query(TEST_PHONE_ID),
            ),
        )

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

        self.check_phone_binding_missing(phone1)
        # История не должна очищаться
        self.check_phone_binding_history(number=TEST_PHONE, bound=TEST_ATTR_BOUND_DT)

        self.check_phone_binding_missing(phone2)
        self.check_phone_binding_history(number=TEST_PHONE2, bound=TEST_ATTR_BOUND2_DT)

    def test_update_phone_bindings(self):
        account = default_account(uid=TEST_UID)
        phone1 = account.phones.create(
            number=TEST_PHONE,
            existing_phone_id=TEST_PHONE_ID,
        )
        phone2 = account.phones.create(
            number=TEST_PHONE2,
            existing_phone_id=TEST_PHONE_ID2,
        )
        phone1.binding = PhoneBinding(time=TEST_ATTR_BOUND_DT)
        phone2.binding = PhoneBinding(time=TEST_ATTR_BOUND2_DT)

        snapshot = account.snapshot()

        phone1.binding.time = None
        phone2.binding.time = None

        queries = AccountEavSerializer().serialize(
            snapshot,
            account,
            diff(snapshot, account),
        )

        eq_eav_queries(
            queries,
            get_transaction(
                self.get_update_phone_bindings_query(
                    phone_id=TEST_PHONE_ID,
                    old_bound=TEST_ATTR_BOUND_DT,
                    bound=zero_datetime,
                    flags=0,
                ),
                self.get_update_phone_bindings_query(
                    phone_id=TEST_PHONE_ID2,
                    old_bound=TEST_ATTR_BOUND2_DT,
                    bound=zero_datetime,
                    flags=0,
                ),
            ),
        )

        self.db._serialize_to_eav(snapshot)
        self.db._serialize_to_eav(account, old_instance=snapshot)

        self.check_phone_binding(bound=zero_datetime)
        # История не должна очищаться
        self.check_phone_binding_history(number=TEST_PHONE, bound=TEST_ATTR_BOUND_DT)

        self.check_phone_binding(
            number=TEST_PHONE2,
            phone_id=TEST_PHONE_ID2,
            bound=zero_datetime,
        )
        self.check_phone_binding_history(number=TEST_PHONE2, bound=TEST_ATTR_BOUND2_DT)

    def test_rebind__ok(self):
        account = default_account(uid=TEST_UID)
        phone = account.phones.create(
            number=TEST_PHONE,
            existing_phone_id=TEST_PHONE_ID,
        )
        phone.binding = PhoneBinding()

        snapshot = account.snapshot()

        phone.binding.time = TEST_ATTR_BOUND_DT
        phone.binding.should_ignore_binding_limit = True

        queries = AccountEavSerializer().serialize(
            snapshot,
            account,
            diff(snapshot, account),
        )

        expected = get_transaction(
            self.get_update_phone_bindings_query(
                phone_id=TEST_PHONE_ID,
                old_bound=zero_datetime,
                bound=TEST_ATTR_BOUND_DT,
                flags=1,
            ),
            self.get_insert_phone_binding_history_query(),
        )
        eq_eav_queries(
            queries,
            expected,
            row_count=[1],
        )

    @raises(EavUpdatedObjectNotFound)
    def test_rebind__fail(self):
        account = default_account(uid=TEST_UID)
        phone = account.phones.create(
            number=TEST_PHONE,
            existing_phone_id=TEST_PHONE_ID,
        )
        phone.binding = PhoneBinding()
        snapshot = account.snapshot()
        phone.binding.time = TEST_ATTR_BOUND_DT

        # Обновляем несуществующую запись
        self.db._serialize_to_eav(account, old_instance=snapshot)

    def test_bind_with_flags(self):
        account = default_account(uid=TEST_UID)
        phone = account.phones.create(
            number=TEST_PHONE,
            existing_phone_id=TEST_PHONE_ID,
        )

        snapshot = account.snapshot()

        phone.binding = PhoneBinding(
            time=TEST_ATTR_BOUND_DT,
            should_ignore_binding_limit=True,
        )

        queries = AccountEavSerializer().serialize(
            snapshot,
            account,
            diff(snapshot, account),
        )

        eq_eav_queries(
            queries,
            get_transaction(
                self.get_update_phone_bindings_query(
                    phone_id=TEST_PHONE_ID,
                    old_bound=zero_datetime,
                    bound=TEST_ATTR_BOUND_DT,
                    flags=1,
                ),
                self.get_insert_phone_binding_history_query(),
            ),
            row_count=[1],
        )

    def test_change_flags(self):
        account = default_account(uid=TEST_UID)
        phone = account.phones.create(
            number=TEST_PHONE,
            existing_phone_id=TEST_PHONE_ID,
        )
        phone.binding = PhoneBinding(time=TEST_ATTR_BOUND_DT)

        snapshot = account.snapshot()

        phone.binding.should_ignore_binding_limit = True

        queries = AccountEavSerializer().serialize(
            snapshot,
            account,
            diff(snapshot, account),
        )

        eq_eav_queries(
            queries,
            get_transaction(
                self.get_update_phone_bindings_query(
                    phone_id=TEST_PHONE_ID,
                    flags=1,
                ),
            ),
        )


class TestPhonesType(TestPhonesBase):

    def test_attribute_default_and_secure(self):
        """
        Проверяем, что при выставлении default и secure на account.phones
        соответствующие атрибуты верно обновляются в базе.
        Также проверим удаление этих атрибутов.
        """

        account = default_account(uid=1)
        phone1 = account.phones.create(number=TEST_PHONE)
        phone2 = account.phones.create(
            number=TEST_PHONE2,
            bound=datetime.now(),
        )

        # Сбросим автоустановленный default.
        account.phones.default = None

        snapshot = account.snapshot()

        self.db._serialize_to_eav(snapshot)
        self.check_db_attr_missing('phones.default')
        self.check_db_attr_missing('phones.secure')

        # Установим default и secure

        account.phones.default = phone1
        phone2.secured = datetime.now()
        account.phones.secure = phone2

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))
        expected = get_transaction(
            self.get_expected_ext_attr_insert_query(
                self.get_ext_attr_dict(phone2.id, 'secured', TimeNow()),
            ),
            self.get_expected_attr_insert_query(
                self.get_attr_dict('phones.default', phone1.id),
                self.get_attr_dict('phones.secure', phone2.id),
            ),
        )
        eq_eav_queries(queries, expected)

        self.db._serialize_to_eav(account, old_instance=snapshot)
        self.check_db_attr('phones.default', str(phone1.id))
        self.check_db_attr('phones.secure', str(phone2.id))

        # Удалим default и secure

        snapshot = account.snapshot()
        account.phones.default = None
        account.phones.secure = None

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))
        expected = get_transaction(
            self.get_expected_attr_delete_query(['phones.default', 'phones.secure']),
        )
        eq_eav_queries(queries, expected)


@with_settings()
class TestRace(PassportTestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()
        self._statbox = DummyLogger()

    def tearDown(self):
        self._db_faker.stop()
        del self._db_faker

    def test_remove_non_existent_operation(self):
        account1 = build_account(
            db_faker=self._db_faker,
            uid=TEST_UID,
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE),
                build_remove_operation(TEST_OPERATION['id'], TEST_PHONE_ID),
            )
        )
        account2 = account1.snapshot()

        snapshot = account1.snapshot()
        logical_op = account1.phones.by_id(TEST_PHONE_ID).get_logical_operation(self._statbox)
        logical_op.cancel()

        self._db_faker._serialize_to_eav(account1, old_instance=snapshot)

        snapshot = account2.snapshot()
        logical_op = account2.phones.by_id(TEST_PHONE_ID).get_logical_operation(self._statbox)
        logical_op.cancel()

        with assert_raises(EavDeletedObjectNotFound):
            self._db_faker._serialize_to_eav(account2, old_instance=snapshot)

    def test_bind_with_same_number(self):
        # Дано: на аккаунте нет телефона
        # П1: Считывает состояние аккаунта
        # П2: Считывает состояние аккаунта
        # П1: Создаёт номер и операцию
        # П1: Привязывает номер и удаляет операцию
        # П2: Создаёт номер и операцию
        build_account(
            db_faker=self._db_faker,
            uid=TEST_UID,
            **deep_merge(
                build_phone_bound(TEST_PHONE_ID, TEST_PHONE),
            )
        )

        account = default_account(uid=TEST_UID)
        snapshot = account.snapshot()
        account.phones.create(TEST_PHONE)

        with assert_raises(DBIntegrityError):
            self._db_faker._serialize_to_eav(account, old_instance=snapshot)


class TestChangePhoneNumber(TestPhonesBase):
    def test_simple(self):
        account = build_account(uid=TEST_UID, **build_phone_bound(TEST_PHONE_ID, TEST_PHONE))

        snapshot = account.snapshot()

        phone = account.phones.by_id(TEST_PHONE_ID)
        phone.number = PhoneNumber.parse(TEST_PHONE2)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            get_transaction(
                ext_at_insert_odk().values(self.get_ext_attr_dict(TEST_PHONE_ID, 'number', TEST_PHONE2[1:])),
                ph_b_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_t.c.uid == TEST_UID, ph_b_t.c.phone_id == TEST_PHONE_ID, ph_b_t.c.number == int(TEST_PHONE))),
                ph_b_h_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_h_t.c.uid == TEST_UID, ph_b_h_t.c.bound == phone.bound, ph_b_h_t.c.number == int(TEST_PHONE))),
            ),
        )

    def test_secure(self):
        account = build_account(uid=TEST_UID, **build_phone_secured(TEST_PHONE_ID, TEST_PHONE))

        snapshot = account.snapshot()

        phone = account.phones.by_id(TEST_PHONE_ID)
        phone.number = PhoneNumber.parse(TEST_PHONE2)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            get_transaction(
                ext_at_insert_odk().values(self.get_ext_attr_dict(TEST_PHONE_ID, 'number', TEST_PHONE2[1:])),
                ph_b_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_t.c.uid == TEST_UID, ph_b_t.c.phone_id == TEST_PHONE_ID, ph_b_t.c.number == int(TEST_PHONE))),
                ph_b_h_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_h_t.c.uid == TEST_UID, ph_b_h_t.c.bound == phone.bound, ph_b_h_t.c.number == int(TEST_PHONE))),
            ),
        )

    def test_simple_bind(self):
        account = build_account(uid=TEST_UID, **build_phone_being_bound(TEST_PHONE_ID, TEST_PHONE, TEST_OPERATION['id']))

        snapshot = account.snapshot()

        phone = account.phones.by_id(TEST_PHONE_ID)
        phone.number = PhoneNumber.parse(TEST_PHONE2)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            get_transaction(
                ext_at_insert_odk().values(self.get_ext_attr_dict(TEST_PHONE_ID, 'number', TEST_PHONE2[1:])),
                self.get_update_phone_bindings_query(TEST_PHONE_ID, old_number=TEST_PHONE, number=TEST_PHONE2),
                self.get_update_phone_operation_query(TEST_OPERATION['id'], security_identity=int(TEST_PHONE2)),
            ),
        )

    def test_secure_bind(self):
        account = build_account(uid=TEST_UID, **build_secure_phone_being_bound(TEST_PHONE_ID, TEST_PHONE, TEST_OPERATION['id']))

        snapshot = account.snapshot()

        phone = account.phones.by_id(TEST_PHONE_ID)
        phone.number = PhoneNumber.parse(TEST_PHONE2)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            get_transaction(
                ext_at_insert_odk().values(self.get_ext_attr_dict(TEST_PHONE_ID, 'number', TEST_PHONE2[1:])),
                self.get_update_phone_bindings_query(TEST_PHONE_ID, old_number=TEST_PHONE, number=TEST_PHONE2),
            ),
        )

    def test_secure_is_being_replaced(self):
        account = build_account(
            uid=TEST_UID,
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE),
                build_phone_bound(TEST_PHONE_ID3, TEST_PHONE3),
                build_simple_replaces_secure_operations(
                    secure_operation_id=1,
                    secure_phone_id=TEST_PHONE_ID,
                    simple_operation_id=2,
                    simple_phone_id=TEST_PHONE_ID3,
                    simple_phone_number=TEST_PHONE3,
                ),
            )
        )

        snapshot = account.snapshot()

        phone = account.phones.by_id(TEST_PHONE_ID)
        phone.number = PhoneNumber.parse(TEST_PHONE2)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            get_transaction(
                ext_at_insert_odk().values(self.get_ext_attr_dict(TEST_PHONE_ID, 'number', TEST_PHONE2[1:])),
                ph_b_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_t.c.uid == TEST_UID, ph_b_t.c.phone_id == TEST_PHONE_ID, ph_b_t.c.number == int(TEST_PHONE))),
                ph_b_h_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_h_t.c.uid == TEST_UID, ph_b_h_t.c.bound == phone.bound, ph_b_h_t.c.number == int(TEST_PHONE))),
            ),
        )

    def test_simple_replaces_secure(self):
        account = build_account(
            uid=TEST_UID,
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE),
                build_phone_bound(TEST_PHONE_ID3, TEST_PHONE3),
                build_simple_replaces_secure_operations(
                    secure_operation_id=1,
                    secure_phone_id=TEST_PHONE_ID,
                    simple_operation_id=2,
                    simple_phone_id=TEST_PHONE_ID3,
                    simple_phone_number=TEST_PHONE3,
                ),
            )
        )

        snapshot = account.snapshot()

        phone = account.phones.by_id(TEST_PHONE_ID3)
        phone.number = PhoneNumber.parse(TEST_PHONE2)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            get_transaction(
                ext_at_insert_odk().values(self.get_ext_attr_dict(TEST_PHONE_ID3, 'number', TEST_PHONE2[1:])),
                ph_b_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_t.c.uid == TEST_UID, ph_b_t.c.phone_id == TEST_PHONE_ID3, ph_b_t.c.number == int(TEST_PHONE3))),
                ph_b_h_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_h_t.c.uid == TEST_UID, ph_b_h_t.c.bound == phone.bound, ph_b_h_t.c.number == int(TEST_PHONE3))),
                self.get_update_phone_operation_query(2, security_identity=int(TEST_PHONE2)),
            ),
        )

    def test_merge(self):
        account = build_account(
            uid=TEST_UID,
            **deep_merge(
                build_phone_bound(TEST_PHONE_ID, TEST_PHONE),
                build_mark_operation(1, TEST_PHONE, TEST_PHONE_ID),
                build_phone_bound(TEST_PHONE_ID2, TEST_PHONE2),
                build_mark_operation(2, TEST_PHONE2, TEST_PHONE_ID2),
            )
        )

        snapshot = account.snapshot()

        account.phones.remove(TEST_PHONE_ID2)
        phone = account.phones.by_id(TEST_PHONE_ID)
        phone.number = PhoneNumber.parse(TEST_PHONE2)

        queries = AccountEavSerializer().serialize(snapshot, account, diff(snapshot, account))

        eq_eav_queries(
            queries,
            get_transaction(
                self.get_delete_phone_operation_query(p_op_t.c.id == 2),
                ph_b_t.delete().where(and_(ph_b_t.c.uid == TEST_UID, ph_b_t.c.phone_id == TEST_PHONE_ID2)),
                ext_at_insert_odk().values(self.get_ext_attr_dict(TEST_PHONE_ID, 'number', TEST_PHONE2[1:])),
                ph_b_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_t.c.uid == TEST_UID, ph_b_t.c.phone_id == TEST_PHONE_ID, ph_b_t.c.number == int(TEST_PHONE))),
                ph_b_h_t.update().values(number=int(TEST_PHONE2)).where(and_(ph_b_h_t.c.uid == TEST_UID, ph_b_h_t.c.bound == phone.bound, ph_b_h_t.c.number == int(TEST_PHONE))),
                self.get_update_phone_operation_query(1, security_identity=int(TEST_PHONE2)),
                self.get_expected_ext_attr_delete_query(
                    self.get_ext_attr_query(TEST_PHONE_ID2, 'number'),
                    self.get_ext_attr_query(TEST_PHONE_ID2, 'created'),
                    self.get_ext_attr_query(TEST_PHONE_ID2, 'bound'),
                    self.get_ext_attr_query(TEST_PHONE_ID2, 'confirmed'),
                ),
            ),
            row_count=[1, 1],
        )
