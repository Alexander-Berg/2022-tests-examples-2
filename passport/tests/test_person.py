# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import get_parsed_blackbox_response
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import Account
from passport.backend.core.models.person import Person
from passport.backend.core.types.birthday import Birthday
from passport.backend.core.types.gender import Gender
from passport.backend.core.undefined import Undefined
import pytz


class TestPersonParse(TestCase):
    def test_basic_parse(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users": [
            {
                "dbfields": {
                    "accounts.ena.uid": "1",
                    "userinfo.sex.uid": "1"
                },
                "attributes": {
                    "27": "\\u0414",
                    "28": "\\u0424",
                    "30": "1963-05-15",
                    "31": "RU",
                    "32": "Москва",
                    "33": "Europe/Moscow",
                    "34": "ru",
                    "212": "\\u0044",
                    "213": "\\u0046"
                },
                "id": "1",
                "karma": { "value": 100 },
                "karma_status": { "value": 3000 },
                "login": "fel",
                "uid": {
                    "domain": "",
                    "domid": "",
                    "hosted": false,
                    "lite": false,
                    "mx": "",
                    "value": "10"
                },
                "display_name": {
                    "name": "dtest",
                    "avatar": {
                        "default": "avatar_key",
                        "empty": false
                    }
                } } ] } ''')
        pers = Person().parse(response)

        eq_(pers.firstname, u'Д')
        eq_(pers.firstname_global, u'D')
        eq_(pers.lastname, u'Ф')
        eq_(pers.lastname_global, u'F')
        eq_(pers.display_name.name, 'dtest')
        eq_(pers.default_avatar, 'avatar_key')
        ok_(not pers.is_avatar_empty)
        eq_(pers.gender, 1)
        eq_(pers.timezone.zone, 'Europe/Moscow')
        eq_(pers.language, 'ru')
        eq_(pers.country, 'RU')
        eq_(pers.city, u'Москва')
        ok_(isinstance(pers.birthday, Birthday))
        eq_(str(pers.birthday), '1963-05-15')

    def test_default_display_name_and_avatar(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users": [
            {
                "id": "1",
                "karma": { "value": 100 },
                "karma_status": { "value": 3000 },
                "login": "fel",
                "uid": {
                    "domain": "",
                    "domid": "",
                    "hosted": false,
                    "lite": false,
                    "mx": "",
                    "value": "10"
                },
                "display_name": {
                    "name": "dtest",
                    "avatar": {
                        "default": "0/0-0",
                        "empty": true
                    },
                    "display_name_empty": true
                }
            }
        ] } ''')
        pers = Person().parse(response)

        eq_(pers.default_avatar, '0/0-0')
        ok_(pers.is_avatar_empty)
        eq_(pers.display_name, 'p:dtest')
        ok_(pers.is_display_name_empty)

    def test_social_display_name(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users": [
            {
                "id": "1",
                "karma": { "value": 100 },
                "karma_status": { "value": 3000 },
                "login": "fel",
                "uid": {
                    "domain": "",
                    "domid": "",
                    "hosted": false,
                    "lite": false,
                    "mx": "",
                    "value": "10"
                },
                "display_name": {
                    "name": "dtest",
                    "social": {
                        "profile_id": "1",
                        "provider": "fb"
                    },
                    "display_name_empty": false
                }
            }
        ] } ''')
        pers = Person().parse(response)

        eq_(str(pers.display_name), 's:1:fb:dtest')
        ok_(not pers.is_display_name_empty)

    def test_parse_bad_timezone(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users": [
            {
                "attributes": {
                    "33": "Europe/Moscowww"
                },
                "id": "1",
                "karma_status": { "value": 3000 },
                "login": "fel",
                "uid": {
                    "domain": "",
                    "domid": "",
                    "hosted": false,
                    "lite": false,
                    "mx": "",
                    "value": "10"
                }
            }
        ] } ''')
        pers = Person().parse(response)

        eq_(str(pers.timezone), 'Europe/Moscow')

    def test_parse_empty_timezone(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users": [
            {
                "attributes": {
                    "33": null
                },
                "id": "1",
                "karma_status": { "value": 3000 },
                "login": "fel",
                "uid": {
                    "domain": "",
                    "domid": "",
                    "hosted": false,
                    "lite": false,
                    "mx": "",
                    "value": "10"
                }
            }
        ] } ''')
        pers = Person().parse(response)

        eq_(str(pers.timezone), 'Europe/Moscow')

    def test_parse_timezone_like_pytz_object(self):
        pers = Person().parse({'person.timezone': pytz.timezone('Europe/Moscow')})
        eq_(str(pers.timezone), 'Europe/Moscow')

    def test_parse_missing_avatar(self):
        pers = Person().parse({'display_name': {'name': 'foobar'}})
        eq_(pers.default_avatar, Undefined)
        eq_(pers.is_avatar_empty, Undefined)

    def test_parse_empty_display_name_and_avatar(self):
        pers = Person().parse({'display_name': {'name': 'foobar', 'avatar': {'default': ''}}})
        eq_(pers.default_avatar, Undefined)
        eq_(pers.is_avatar_empty, Undefined)
        eq_(pers.is_display_name_empty, Undefined)

    def test_parse_dont_use_displayname_as_public_name(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{{"users":[{{
                    "uid": {{ "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" }},
                    "login":"test",
                    "karma": {{ "value":85, "allow-until":1321965947 }},
                    "karma_status": {{ "value":85 }},
                    "regname":"test",
                    "attributes":{{
                        "{dont_use_displayname_as_public_name}":"1"
                    }} }} ] }}'''.format(
                dont_use_displayname_as_public_name=AT['person.dont_use_displayname_as_public_name'],
            ),
        )
        pers = Person().parse(response)
        eq_(pers.dont_use_displayname_as_public_name, True)

    def test_parse_show_fio_in_public_name(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{{"users":[{{
                    "uid": {{ "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" }},
                    "login":"test",
                    "karma": {{ "value":85, "allow-until":1321965947 }},
                    "karma_status": {{ "value":85 }},
                    "regname":"test",
                    "attributes":{{
                        "{show_fio_in_public_name}":"1"
                    }} }} ] }}'''.format(
                show_fio_in_public_name=AT['person.show_fio_in_public_name'],
            ),
        )
        pers = Person().parse(response)
        eq_(pers.show_fio_in_public_name, True)


class TestPerson(TestCase):
    def setUp(self):
        self.person = Person()

    def test_birthday(self):
        self.person.birthday = Birthday(month=11, day=12)
        eq_(str(self.person.birthday), '0000-11-12')

        self.person.birthday = Birthday.parse('1985-10-10')
        eq_(str(self.person.birthday), '1985-10-10')

        self.person.birthday = Birthday.parse('0000-09-09')
        eq_(str(self.person.birthday), '0000-09-09')

    def test_empty_birthday(self):
        self.person.parse({'person.birthday': None})
        eq_(self.person.birthday, None)

    def test_invalid_birthday(self):
        self.person.parse({'person.birthday': '1985-13-01'})
        eq_(self.person.birthday, None)

    def test_gender(self):
        self.person.parse({'userinfo.sex.uid': 1})
        ok_(self.person.is_male())
        ok_(not self.person.is_female())

    def test_gender_to_char(self):
        eq_(Gender.to_char(0), None)
        eq_(Gender.to_char(Gender.Male), 'm')
        eq_(Gender.to_char(Gender.Female), 'f')
        eq_(Gender.to_char(123), None)


class TestContactPhoneNumber(TestCase):

    def setUp(self):
        self.phone_number = '+79261234567'
        self.expected_phone_number = '79261234567'

    def create_account(self, subscriptions=None):
        acc = Account()
        if subscriptions is None:
            subscriptions = {}
        return acc.parse({'uid': 10, 'subscriptions': subscriptions})

    def test_no_contact_phone_number(self):
        acc = self.create_account()
        eq_(acc.person.contact_phone_number, None)

    def test_contact_phone_number_get(self):
        acc = self.create_account(subscriptions={
            10: {'sid': 10},
            Person.CONTACT_PHONE_NUMBER_SID: {'sid': 89, 'login': self.expected_phone_number},
        })
        eq_(acc.person.contact_phone_number, self.expected_phone_number)

    def test_contact_phone_number_set(self):
        sid = Person.CONTACT_PHONE_NUMBER_SID
        acc = self.create_account()
        eq_(acc.person.contact_phone_number, None)
        acc.person.contact_phone_number = self.phone_number
        eq_(acc.subscriptions[sid].login, self.expected_phone_number)
        eq_(acc.subscriptions[sid].sid, sid)

        acc.person.contact_phone_number = '89260000000'
        eq_(acc.subscriptions[sid].login, '89260000000')

    def test_contact_phone_number_set_none(self):
        sid = Person.CONTACT_PHONE_NUMBER_SID
        acc = self.create_account()
        acc.person.contact_phone_number = None
        eq_(acc.subscriptions[sid].login, None)
        eq_(acc.subscriptions[sid].sid, sid)
