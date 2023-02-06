# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.core.db.faker.db import attribute_table_insert_on_duplicate_update_key as at_insert_odk
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import attributes_table as at
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import Account
from passport.backend.core.models.person import (
    DisplayName,
    Person,
)
from passport.backend.core.serializers.eav.person import (
    person_birthday_processor,
    person_country_processor,
    person_gender_processor,
    person_language_processor,
    person_timezone_processor,
    PersonEavSerializer,
)
from passport.backend.core.types.birthday import Birthday
import pytz
from sqlalchemy.sql.expression import and_


class TestCreatePerson(unittest.TestCase):
    def test_all_fields(self):
        uid = 123
        acc = Account(uid=uid)
        per = Person(acc)
        per.firstname = 'newa'
        per.firstname_global = 'newa'
        per.lastname = 'newb'
        per.lastname_global = 'newb'
        per.gender = 1
        per.city = 'Moscow'
        per.language = 'en'
        per.display_name = DisplayName(u'Имя', None, None)
        per.country = 'UA'
        per.timezone = pytz.timezone('Europe/Paris')
        per.birthday = Birthday.parse('1900-10-10')
        per.default_avatar = 'ava'
        per.dont_use_displayname_as_public_name = True
        per.show_fio_in_public_name = True

        queries = PersonEavSerializer().serialize(None, per, diff(None, per))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['person.firstname'], 'value': b'newa'},
                    {'uid': uid, 'type': AT['person.firstname_global'], 'value': b'newa'},
                    {'uid': uid, 'type': AT['person.lastname'], 'value': b'newb'},
                    {'uid': uid, 'type': AT['person.lastname_global'], 'value': b'newb'},
                    {'uid': uid, 'type': AT['person.gender'], 'value': b'm'},
                    {'uid': uid, 'type': AT['person.city'], 'value': b'Moscow'},
                    {'uid': uid, 'type': AT['person.language'], 'value': b'en'},
                    {'uid': uid, 'type': AT['account.display_name'], 'value': b'p:%s' % u'Имя'.encode('utf-8')},
                    {'uid': uid, 'type': AT['person.country'], 'value': b'ua'},
                    {'uid': uid, 'type': AT['person.timezone'], 'value': b'Europe/Paris'},
                    {'uid': uid, 'type': AT['person.birthday'], 'value': b'1900-10-10'},
                    {'uid': uid, 'type': AT['avatar.default'], 'value': b'ava'},
                    {'uid': uid, 'type': AT['person.dont_use_displayname_as_public_name'], 'value': b'1'},
                    {'uid': uid, 'type': AT['person.show_fio_in_public_name'], 'value': b'1'},
                ]),
            ],
        )

    def test_ignore_default_values(self):
        uid = 123
        acc = Account(uid=uid)
        per = Person(acc)
        per.firstname = ''
        per.firstname_global = ''
        per.lastname = ''
        per.lastname_global = ''
        per.gender = 0
        per.city = ''
        per.language = 'ru'
        per.display_name = DisplayName(u'', None, None)
        per.country = 'ru'
        per.timezone = pytz.timezone('Europe/Moscow')
        per.birthday = Birthday.parse('0000-00-00')
        per.default_avatar = ''
        per.dont_use_displayname_as_public_name = False

        queries = PersonEavSerializer().serialize(None, per, diff(None, per))

        eq_eav_queries(queries, [])

    def test_firstname(self):
        uid = 123
        acc = Account(uid=uid)
        per = Person(acc, firstname=u'Имя', lastname=u'Фамилия', language='ru')

        queries = PersonEavSerializer().serialize(None, per, diff(None, per))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['person.firstname'], 'value': u'Имя'.encode('utf-8')},
                    {'uid': uid, 'type': AT['person.lastname'], 'value': u'Фамилия'.encode('utf-8')},
                ]),
            ],
        )


class TestChangePerson(unittest.TestCase):
    def test_empty_diff(self):
        acc = Account(uid=123)
        per = Person(acc, firstname='a', lastname='b')

        s1 = per.snapshot()
        queries = PersonEavSerializer().serialize(s1, per, diff(s1, per))
        eq_eav_queries(queries, [])

    def test_firstname(self):
        acc = Account(uid=123)
        per = Person(acc, firstname='a', lastname='b')

        s1 = per.snapshot()
        per.firstname = 'newa'
        queries = PersonEavSerializer().serialize(s1, per, diff(s1, per))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([{'uid': 123, 'type': AT['person.firstname'], 'value': b'newa'}]),
            ],
        )

    def test_all_fields(self):
        uid = 123
        acc = Account(uid=uid)
        per = Person(acc, firstname='a', lastname='b', dont_use_displayname_as_public_name=False)

        s1 = per.snapshot()
        per.firstname = 'newa'
        per.lastname = 'newb'
        per.gender = 1
        per.city = 'Moscow'
        per.language = 'en'
        per.display_name = DisplayName(u'Имя', None, None)
        per.country = 'UA'
        per.timezone = pytz.timezone('Europe/Paris')
        per.birthday = Birthday.parse('1900-10-10')
        per.default_avatar = 'ava'
        per.dont_use_displayname_as_public_name = True
        per.show_fio_in_public_name = True

        queries = PersonEavSerializer().serialize(s1, per, diff(s1, per))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['person.firstname'], 'value': b'newa'},
                    {'uid': uid, 'type': AT['person.lastname'], 'value': b'newb'},
                    {'uid': uid, 'type': AT['person.gender'], 'value': b'm'},
                    {'uid': uid, 'type': AT['person.city'], 'value': b'Moscow'},
                    {'uid': uid, 'type': AT['person.language'], 'value': b'en'},
                    {'uid': uid, 'type': AT['account.display_name'], 'value': b'p:%s' % u'Имя'.encode('utf-8')},
                    {'uid': uid, 'type': AT['person.country'], 'value': b'ua'},
                    {'uid': uid, 'type': AT['person.timezone'], 'value': b'Europe/Paris'},
                    {'uid': uid, 'type': AT['person.birthday'], 'value': b'1900-10-10'},
                    {'uid': uid, 'type': AT['avatar.default'], 'value': b'ava'},
                    {'uid': uid, 'type': AT['person.dont_use_displayname_as_public_name'], 'value': b'1'},
                    {'uid': uid, 'type': AT['person.show_fio_in_public_name'], 'value': b'1'},
                ]),
            ],
        )

    def test_ignore_default_values(self):
        uid = 123
        acc = Account(uid=uid)
        per = Person(
            acc,
            firstname='a',
            language='tr',
            gender=127,
            country='tr',
            timezone=pytz.timezone('Europe/Paris'),
            default_avatar='ava',
        )
        s1 = per.snapshot()

        per.firstname = ''
        per.lastname = ''
        per.country = 'ru'
        per.language = 'ru'
        per.gender = 25
        per.timezone = pytz.timezone('Europe/Moscow')
        per.default_avatar = ''

        queries = PersonEavSerializer().serialize(s1, per, diff(s1, per))

        deleted_types = sorted([
            AT[name] for name in [
                'avatar.default',
                'person.firstname',
                'person.lastname',
                'person.country',
                'person.language',
                'person.timezone',
            ]
        ])
        eq_eav_queries(
            queries,
            [
                at.delete().where(and_(at.c.uid == uid, at.c.type.in_(deleted_types))),
            ],
        )

    def test_empty_birthday(self):
        acc = Account(uid=123)
        per = Person(acc, firstname='a', lastname='b')

        s1 = per.snapshot()
        per.birthday = ''

        queries = PersonEavSerializer().serialize(s1, per, diff(s1, per))
        eq_eav_queries(
            queries,
            [
                at.delete().where(and_(at.c.uid == 123, at.c.type.in_([AT['person.birthday']]))),
            ],
        )

    def test_delete_default_avatar(self):
        acc = Account(uid=123)
        per = Person(acc, firstname='a', lastname='b')

        s1 = per.snapshot()
        per.default_avatar = None

        queries = PersonEavSerializer().serialize(s1, per, diff(s1, per))
        eq_eav_queries(
            queries,
            [
                at.delete().where(and_(at.c.uid == 123, at.c.type.in_([AT['avatar.default']]))),
            ],
        )

    def test_bad_timezone(self):
        acc = Account(uid=123)
        per = Person(acc).parse({'person.timezone': 'Moscowww'})

        s1 = per.snapshot()
        per.timezone = 'Europe/Paris'
        queries = PersonEavSerializer().serialize(s1, per, diff(s1, per))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['person.timezone'], 'value': b'Europe/Paris'},
                ]),
            ],
        )

    def test_change_displayname_deletes_attribute_174(self):
        uid = 123
        acc = Account(uid=uid)
        per = Person(
            acc,
            display_name=DisplayName(u'Имя', 'fb', 10),
            dont_use_displayname_as_public_name=True,
        )

        s1 = per.snapshot()
        per.display_name = DisplayName(u'Новое имя', 'fb', 10)

        queries = PersonEavSerializer().serialize(s1, per, diff(s1, per))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {
                        'uid': uid,
                        'type': AT['account.display_name'],
                        'value': b's:10:fb:%s' % u'Новое имя'.encode('utf-8'),
                    },
                ]),
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type.in_(
                            [AT['person.dont_use_displayname_as_public_name']],
                        ),
                    ),
                ),
            ],
        )

    def test_delete_dont_use_displayname_as_public_name(self):
        uid = 123
        acc = Account(uid=uid)
        per = Person(acc, dont_use_displayname_as_public_name=True)

        s1 = per.snapshot()
        per.dont_use_displayname_as_public_name = False

        queries = PersonEavSerializer().serialize(s1, per, diff(s1, per))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type.in_(
                            [AT['person.dont_use_displayname_as_public_name']],
                        ),
                    ),
                ),
            ],
        )


class TestPersonProcessors(unittest.TestCase):
    def test_gender(self):
        # "m" если == 1, "f" если == 2, остальные значения
        # считаем за неизвестное (например, null, -128, 127, 0 и др.)
        eq_(person_gender_processor(1), 'm')
        eq_(person_gender_processor(2), 'f')
        eq_(person_gender_processor(None), None)
        eq_(person_gender_processor(-128), None)
        eq_(person_gender_processor(0), None)

    def test_country(self):
        # переходим с lower+upper на lower; при значении "ru" атрибут удаляем
        eq_(person_country_processor('be'), 'be')
        eq_(person_country_processor('by'), 'by')
        eq_(person_country_processor('BY'), 'by')
        eq_(person_country_processor('bla'), 'bla')
        eq_(person_country_processor('ru'), None)
        eq_(person_country_processor(None), None)
        eq_(person_country_processor(''), None)

    def test_birthday(self):
        # userinfo.birth_date, если не null, непустое и не '0000-00-00'
        eq_(person_birthday_processor(None), None)
        eq_(person_birthday_processor(''), None)
        eq_(person_birthday_processor(Birthday.parse('0000-00-00')), None)
        eq_(person_birthday_processor(Birthday.parse('0000-01-12')), '0000-01-12')

    def test_language(self):
        # userinfo.lang, если не null, непустое, и != "ru"
        eq_(person_language_processor(None), None)
        eq_(person_language_processor(''), None)
        eq_(person_language_processor('uk'), 'uk')
        eq_(person_language_processor('ru'), None)

    def test_timezone(self):
        # userinfo.tz, если не null, непустое и не Europe/Moscow
        eq_(person_timezone_processor(None), None)
        eq_(person_timezone_processor(''), None)
        eq_(person_timezone_processor(pytz.timezone('Europe/Moscow')), None)
        eq_(person_timezone_processor(pytz.timezone('Europe/Paris')), 'Europe/Paris')
        eq_(person_timezone_processor('Europe/Moscow'), None)
        eq_(person_timezone_processor('Europe/Paris'), 'Europe/Paris')
