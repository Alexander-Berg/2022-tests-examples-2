# -*- coding: utf-8 -*-

from datetime import datetime
import unittest

from nose.tools import raises
from passport.backend.core.db.faker.db import (
    extended_attribute_table_delete as eat_delete,
    extended_attribute_table_insert_on_duplicate_key as eat_insert_odk,
    IdGeneratorFaker,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    email_bindings_table,
    extended_attributes_table as eat,
)
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EXT_ATTR_EMAIL,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
)
from passport.backend.core.models.account import Account
from passport.backend.core.models.email import Email
from passport.backend.core.serializers.eav.emails import (
    EmailEavSerializer,
    EmailsEavSerializer,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.time import zero_datetime
from sqlalchemy.sql.expression import and_


TEST_ENTITY_ID = 1
TEST_UID = 123
TEST_ADDRESS = 'asd@asd.ru'
TEST_ADDRESS2 = 'asd2@asd.ru'
TEST_CYRILLIC_ADDRESS = u'volozh@яндекс.рф'


class BaseEmailSerializeTestCase(unittest.TestCase):
    serializer_class = None

    def setUp(self):
        self.id_faker = IdGeneratorFaker()
        self.id_faker.set_list(range(1, 100))
        self.id_faker.start()

        self.acc = Account(uid=TEST_UID).parse({})
        super(BaseEmailSerializeTestCase, self).setUp()

    def tearDown(self):
        self.id_faker.stop()
        del self.id_faker

    def serialize(self, s1, s2):
        return self.serializer_class().serialize(
            s1,
            s2,
            diff(s1, s2),
        )

    def create(self, instance):
        return self.serialize(None, instance)

    def update(self, s1, instance):
        return self.serialize(s1, instance)

    def delete(self, instance):
        return self.serialize(instance, None)

    def eat_entry(self, **kwargs):
        base_entry = {
            'entity_id': TEST_ENTITY_ID,
            'entity_type': EXTENDED_ATTRIBUTES_EMAIL_TYPE,
            'uid': TEST_UID,
        }
        return merge_dicts(base_entry, kwargs)


class TestSerializeEmail(BaseEmailSerializeTestCase):
    serializer_class = EmailEavSerializer

    def test_empty_with_address_and_created_dt(self):
        email = Email(address=TEST_ADDRESS)
        email.created_at = DatetimeNow()
        self.acc.emails[TEST_ADDRESS] = email
        eq_eav_queries(
            self.create(email),
            [
                email_bindings_table.insert().values({
                    'uid': TEST_UID,
                    'bound': zero_datetime,
                    'address': TEST_ADDRESS.encode('utf8'),
                    'email_id': TEST_ENTITY_ID,
                }),
                eat_insert_odk().values([
                    self.eat_entry(
                        type=EXT_ATTR_EMAIL['address'],
                        value=TEST_ADDRESS.encode('utf8'),
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_EMAIL['created'],
                        value=TimeNow(),
                    ),
                ]),
            ],
        )

    def test_update_set_flag_created_not_set(self):
        email = Email(address=TEST_ADDRESS)
        email.id = TEST_ENTITY_ID
        self.acc.emails[TEST_ADDRESS] = email
        s1 = email.snapshot()

        email.is_rpop = True

        eq_eav_queries(
            self.update(s1, email),
            [
                eat_insert_odk().values([
                    self.eat_entry(
                        type=EXT_ATTR_EMAIL['is_rpop'],
                        value=b'1',
                    ),
                ]),
            ],
        )

    def test_set_flags(self):
        email = Email(address=TEST_ADDRESS)
        self.acc.emails[TEST_ADDRESS] = email
        email.id = TEST_ENTITY_ID
        s1 = email.snapshot()

        email.is_silent = True
        email.is_unsafe = True
        email.is_rpop = True

        eq_eav_queries(
            self.update(s1, email),
            [
                eat_insert_odk().values(
                    [
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL[key],
                            value=b'1',
                        ) for key in ['is_unsafe', 'is_silent', 'is_rpop']
                    ],
                ),
            ],
        )

    def test_update_set_timestamps(self):
        email = Email(address=TEST_ADDRESS)
        self.acc.emails[TEST_ADDRESS] = email
        email.id = TEST_ENTITY_ID
        s1 = email.snapshot()

        email.created_at = datetime.fromtimestamp(1)
        email.confirmed_at = datetime.fromtimestamp(2)
        email.bound_at = datetime.fromtimestamp(3)

        eq_eav_queries(
            self.update(s1, email),
            [
                # При установке атрибута bound_at значение bound должно
                # обновиться
                email_bindings_table.update().values({
                    'bound': email.bound_at,
                }).where(
                    and_(email_bindings_table.c.email_id == TEST_ENTITY_ID),
                ),
                eat_insert_odk().values(
                    [
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['created'],
                            value=b'1',
                        ),
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['confirmed'],
                            value=b'2',
                        ),
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['bound'],
                            value=b'3',
                        ),
                    ],
                ),
            ],
        )

    def test_binding_converted_to_lowecase(self):
        mixedcase_address = 'Elon.Musk@yandex.ru'
        email = Email(
            address=mixedcase_address,
            created_at=datetime.fromtimestamp(1),
            confirmed_at=datetime.fromtimestamp(2),
            bound_at=datetime.fromtimestamp(3),
        )
        self.acc.emails[TEST_ADDRESS] = email

        eq_eav_queries(
            self.create(email),
            [
                email_bindings_table.insert().values({
                    'uid': TEST_UID,
                    'bound': datetime.fromtimestamp(3),
                    'address': mixedcase_address.lower().encode('utf8'),
                    'email_id': TEST_ENTITY_ID,
                }),
                eat_insert_odk().values(
                    [
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['created'],
                            value=b'1',
                        ),
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['confirmed'],
                            value=b'2',
                        ),
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['bound'],
                            value=b'3',
                        ),
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['address'],
                            value=mixedcase_address.encode('utf8'),
                        ),

                    ],
                ),
            ],
        )

    def test_serialize_cyrillic_as_utf8(self):
        email = Email(
            address=TEST_CYRILLIC_ADDRESS,
            created_at=datetime.fromtimestamp(1),
            confirmed_at=datetime.fromtimestamp(2),
            bound_at=datetime.fromtimestamp(3),
        )
        self.acc.emails[TEST_ADDRESS] = email

        eq_eav_queries(
            self.update(None, email),
            [
                email_bindings_table.insert().values({
                    'uid': TEST_UID,
                    'bound': datetime.fromtimestamp(3),
                    'address': TEST_CYRILLIC_ADDRESS.encode('utf-8'),
                    'email_id': TEST_ENTITY_ID,
                }),
                eat_insert_odk().values(
                    [
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['created'],
                            value=b'1',
                        ),
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['confirmed'],
                            value=b'2',
                        ),
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['bound'],
                            value=b'3',
                        ),
                        self.eat_entry(
                            type=EXT_ATTR_EMAIL['address'],
                            value=TEST_CYRILLIC_ADDRESS.encode('utf-8'),
                        ),
                    ],
                ),
            ],
        )

    def test_delete_single_email(self):
        email = Email(address=TEST_ADDRESS)
        self.acc.emails[TEST_ADDRESS] = email
        email.id = TEST_ENTITY_ID

        eq_eav_queries(
            self.delete(email),
            [
                email_bindings_table.delete().where(
                    and_(
                        email_bindings_table.c.uid == TEST_UID,
                        email_bindings_table.c.email_id == TEST_ENTITY_ID,
                    ),
                ),
                eat_delete().where(
                    and_(
                        eat.c.uid == TEST_UID,
                        eat.c.entity_id == TEST_ENTITY_ID,
                        eat.c.entity_type == EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                    ),
                ),
            ],
        )

    def test_on_delete_updates_are_discarded(self):
        email = Email(address=TEST_ADDRESS)
        self.acc.emails[TEST_ADDRESS] = email

        email.id = TEST_ENTITY_ID
        email.is_rpop = True

        eq_eav_queries(
            self.delete(email),
            [
                email_bindings_table.delete().where(
                    and_(
                        email_bindings_table.c.uid == TEST_UID,
                        email_bindings_table.c.email_id == TEST_ENTITY_ID,
                    ),
                ),
                eat_delete().where(
                    and_(
                        eat.c.uid == TEST_UID,
                        eat.c.entity_id == TEST_ENTITY_ID,
                        eat.c.entity_type == EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                    ),
                ),
            ],
        )

    def test_nothing_to_do_here_move_along(self):
        eq_eav_queries(
            self.serialize(None, None),
            [],
        )

    def test_email_unbound_binding_deleted(self):
        email = Email(address=TEST_ADDRESS)
        email.id = TEST_ENTITY_ID
        email.bound_at = datetime.fromtimestamp(1)

        self.acc.emails[TEST_ADDRESS] = email

        s1 = email.snapshot()
        email.bound_at = None

        eq_eav_queries(
            self.serialize(s1, email),
            [
                email_bindings_table.update().values({
                    'bound': zero_datetime,
                }).where(
                    and_(
                        email_bindings_table.c.email_id == TEST_ENTITY_ID,
                    ),
                ),
                eat_delete().where(
                    and_(
                        eat.c.uid == TEST_UID,
                        eat.c.entity_type == EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                        eat.c.entity_id == TEST_ENTITY_ID,
                        eat.c.type == EXT_ATTR_EMAIL['bound'],
                    ),
                ),
            ],
        )

    def test_update_email_binding_time(self):
        email = Email(address=TEST_ADDRESS)
        self.acc.emails[TEST_ADDRESS] = email

        email.id = TEST_ENTITY_ID
        email.bound_at = datetime.fromtimestamp(1)

        s1 = email.snapshot()
        email.bound_at = datetime.fromtimestamp(2)

        eq_eav_queries(
            self.serialize(s1, email),
            [
                (
                    email_bindings_table.update()
                    .values(bound=datetime.fromtimestamp(2))
                    .where(email_bindings_table.c.email_id == TEST_ENTITY_ID)
                ),
                eat_insert_odk().values([
                    self.eat_entry(type=EXT_ATTR_EMAIL['bound'], value=b'2'),
                ]),
            ],
        )

    @raises(ValueError)
    def test_error_create_email_without_address(self):
        email = Email()

        eq_eav_queries(
            self.create(email),
            [],
        )

    @raises(ValueError)
    def test_error_email_address_updated_to_none(self):
        email = Email(address=TEST_ADDRESS)
        self.acc.emails[TEST_ADDRESS] = email

        s1 = email.snapshot()
        email.address = None

        eq_eav_queries(
            self.serialize(s1, email),
            [],
        )

    def test_update_native_email(self):
        email = Email(address=TEST_ADDRESS, is_native=True)
        old_email = email.snapshot()
        email.confirmed_at = datetime.now()

        eq_eav_queries(self.update(old_email, email), [])


class TestSerializeEmailsList(BaseEmailSerializeTestCase):
    serializer_class = EmailsEavSerializer

    def test_empty_list_no_queries(self):
        eq_eav_queries(
            self.create(self.acc.emails),
            [],
        )

        eq_eav_queries(
            self.update(self.acc.emails, self.acc.emails),
            [],
        )

        eq_eav_queries(
            self.delete(self.acc.emails),
            [],
        )

    def test_create_list_add_email_get_queries(self):
        email = Email(address=TEST_ADDRESS)
        self.acc.emails[TEST_ADDRESS] = email

        eq_eav_queries(
            self.create(self.acc.emails),
            [
                'BEGIN',
                email_bindings_table.insert().values({
                    'uid': TEST_UID,
                    'bound': zero_datetime,
                    'address': TEST_ADDRESS.encode('utf8'),
                    'email_id': TEST_ENTITY_ID,
                }),
                eat_insert_odk().values(self.eat_entry(
                    type=EXT_ATTR_EMAIL['address'],
                    value=TEST_ADDRESS.encode('utf8'),
                )),
                'COMMIT',
            ],
        )

    def test_add_two_emails_get_two_sets_of_queries(self):
        email = Email(address=TEST_ADDRESS)
        self.acc.emails[TEST_ADDRESS] = email

        email2 = Email(address=TEST_ADDRESS2)
        self.acc.emails[TEST_ADDRESS2] = email2

        eq_eav_queries(
            self.create(self.acc.emails),
            [
                'BEGIN',
                email_bindings_table.insert().values({
                    'uid': TEST_UID,
                    'bound': zero_datetime,
                    'address': TEST_ADDRESS2.encode('utf8'),
                    'email_id': TEST_ENTITY_ID,
                }),
                eat_insert_odk().values(self.eat_entry(
                    type=EXT_ATTR_EMAIL['address'],
                    value=TEST_ADDRESS2.encode('utf8'),
                    entity_id=TEST_ENTITY_ID,
                )),
                email_bindings_table.insert().values({
                    'uid': TEST_UID,
                    'bound': zero_datetime,
                    'address': TEST_ADDRESS.encode('utf8'),
                    'email_id': TEST_ENTITY_ID + 1,
                }),
                eat_insert_odk().values(self.eat_entry(
                    type=EXT_ATTR_EMAIL['address'],
                    value=TEST_ADDRESS.encode('utf8'),
                    entity_id=TEST_ENTITY_ID + 1,
                )),
                'COMMIT',
            ],
        )

    def test_mixed_operations(self):
        email = Email(address=TEST_ADDRESS)
        email.id = TEST_ENTITY_ID
        self.acc.emails[TEST_ADDRESS] = email

        s1 = self.acc.emails.snapshot()

        email2 = Email(address=TEST_ADDRESS2)
        self.acc.emails[TEST_ADDRESS2] = email2

        self.acc.emails.pop(TEST_ADDRESS)

        eq_eav_queries(
            self.update(s1, self.acc.emails),
            [
                'BEGIN',
                email_bindings_table.insert().values({
                    'uid': TEST_UID,
                    'bound': zero_datetime,
                    'address': TEST_ADDRESS2.encode('utf8'),
                    'email_id': TEST_ENTITY_ID,
                }),
                eat_insert_odk().values(self.eat_entry(
                    type=EXT_ATTR_EMAIL['address'],
                    value=TEST_ADDRESS2.encode('utf8'),
                    entity_id=TEST_ENTITY_ID,
                )),
                email_bindings_table.delete().where(
                    and_(
                        email_bindings_table.c.uid == TEST_UID,
                        email_bindings_table.c.email_id == TEST_ENTITY_ID,
                    ),
                ),
                eat.delete().where(
                    and_(
                        eat.c.uid == TEST_UID,
                        eat.c.entity_id == TEST_ENTITY_ID,
                        eat.c.entity_type == EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                    ),
                ),
                'COMMIT',
            ],
        )

    def test_delete_everything(self):
        email = Email(address=TEST_ADDRESS)
        email.id = TEST_ENTITY_ID
        self.acc.emails[TEST_ADDRESS] = email

        email2 = Email(address=TEST_ADDRESS2)
        email2.id = TEST_ENTITY_ID + 1
        self.acc.emails[TEST_ADDRESS2] = email2

        eq_eav_queries(
            self.delete(self.acc.emails),
            [
                email_bindings_table.delete().where(
                    email_bindings_table.c.uid == TEST_UID,
                ),
                eat.delete().where(
                    and_(
                        eat.c.uid == TEST_UID,
                        eat.c.entity_type == EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                    ),
                ),
            ],
        )

    def test_nothing_to_do_here_move_along(self):
        eq_eav_queries(
            self.serialize(None, None),
            [],
        )

    def test_create_native_email(self):
        self.acc.emails[TEST_ADDRESS] = Email(address=TEST_ADDRESS, is_native=True)
        eq_eav_queries(self.create(self.acc.emails), [])

    def test_delete_native_email(self):
        self.acc.emails[TEST_ADDRESS] = Email(address=TEST_ADDRESS, is_native=True)
        self.acc.emails[TEST_ADDRESS2] = Email(address=TEST_ADDRESS2)
        old_emails = self.acc.emails.snapshot()
        del self.acc.emails[TEST_ADDRESS]

        eq_eav_queries(self.update(old_emails, self.acc.emails), [])
