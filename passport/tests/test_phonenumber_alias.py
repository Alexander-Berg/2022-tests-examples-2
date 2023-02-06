# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ATT
from passport.backend.core.models.alias import PhonenumberAlias
from passport.backend.core.test.consts import TEST_PHONE_NUMBER1
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.undefined import Undefined


PHONENUMBER_ALIAS_TYPE = str(ATT['phonenumber'])


class TestPhonenumberAlias(PassportTestCase):
    def test_parse_phone_number_from_string(self):
        alias = PhonenumberAlias().parse({
            'aliases': {PHONENUMBER_ALIAS_TYPE: '79030915478'},
        })

        eq_(alias.number.e164, '+79030915478')
        eq_(alias.alias, '79030915478')

    def test_parse_phone_number_from_object(self):
        alias = PhonenumberAlias().parse({
            'aliases': {PHONENUMBER_ALIAS_TYPE: PhoneNumber.parse('+79030915478')},
        })

        eq_(alias.number.e164, '+79030915478')
        eq_(alias.alias, '79030915478')

    def test_parse_invalid_phone_number(self):
        alias = PhonenumberAlias().parse({
            'aliases': {PHONENUMBER_ALIAS_TYPE: '381234'},
        })
        eq_(alias.number.e164, '+381234')
        eq_(alias.alias, '381234')

    def test_empty(self):
        alias = PhonenumberAlias().parse({})
        eq_(alias.number, Undefined)
        eq_(alias.alias, Undefined)
        eq_(alias.enable_search, Undefined)

    def test_no_enable_search_attribute(self):
        alias = PhonenumberAlias().parse({
            'aliases': {PHONENUMBER_ALIAS_TYPE: TEST_PHONE_NUMBER1.digital},
        })
        ok_(alias.enable_search is Undefined)

    def test_enable_search_attribute_is_set(self):
        alias = PhonenumberAlias().parse({
            'aliases': {PHONENUMBER_ALIAS_TYPE: TEST_PHONE_NUMBER1.digital},
            'account.enable_search_by_phone_alias': '1',
        })
        ok_(alias.enable_search is True)

    def test_enable_search_attribute_is_unset(self):
        alias = PhonenumberAlias().parse({
            'aliases': {PHONENUMBER_ALIAS_TYPE: TEST_PHONE_NUMBER1.digital},
        })
        ok_(alias.enable_search is Undefined)

        alias = PhonenumberAlias().parse({
            'aliases': {PHONENUMBER_ALIAS_TYPE: TEST_PHONE_NUMBER1.digital},
            'account.enable_search_by_phone_alias': '0',
        })
        ok_(alias.enable_search is False)

    def test_enable_search_attribute_is_garbage(self):
        alias = PhonenumberAlias().parse({'account.enable_search_by_phone_alias': '1'})
        eq_(alias.enable_search, True)

    def test_eq(self):
        data = {'aliases': {PHONENUMBER_ALIAS_TYPE: '79030915478'}}
        alias = PhonenumberAlias().parse(data)
        alias_other = PhonenumberAlias().parse(data)

        ok_(alias == '+79030915478')
        ok_(alias == '79030915478')
        ok_(alias == PhoneNumber.parse('+79030915478'))
        eq_(alias, alias_other)

        ok_(alias != '+79030915479')
        ok_(alias != '79030915479')
        ok_(alias != PhoneNumber.parse('+79030915479'))
        ok_(alias != '+999234')
        alias_other.number = PhoneNumber.parse('+79030915479')
        ok_(alias != alias_other)
        ok_(alias != object())

        alias3 = PhonenumberAlias().parse({
            'aliases': {PHONENUMBER_ALIAS_TYPE: '79030915478'},
            'account.enable_search_by_phone_alias': '1',
        })
        eq_(alias3, alias)
