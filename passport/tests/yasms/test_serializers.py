# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase

from nose.tools import eq_
from passport.backend.api.yasms.controllers.check_phone import build_check_phone_dict
from passport.backend.api.yasms.controllers.check_user import build_check_user_xml
from passport.backend.api.yasms.controllers.confirm import build_confirm_xml
from passport.backend.api.yasms.controllers.delete_phone import build_delete_phone_dict
from passport.backend.api.yasms.controllers.drop_phone import build_drop_phone_dict
from passport.backend.api.yasms.controllers.have_user_once_validated_phone import (
    build_have_user_once_validated_phone_xml,
)
from passport.backend.api.yasms.controllers.prolong_valid import build_prolong_valid_dict
from passport.backend.api.yasms.controllers.register import build_register_xml
from passport.backend.api.yasms.controllers.user_phones import build_user_phones_xml
from passport.backend.api.yasms.controllers.validations_number_of_user_phones import (
    build_validations_number_of_user_phones_xml,
)
from passport.backend.api.yasms.serializers import (
    bool_to_int,
    bool_to_onezero,
    bool_to_yesno,
    datetime_to_str,
    number_to_str,
)
from passport.backend.core.xml.test_utils import assert_xml_documents_equal


TEST_PHONE_NUMBER = u'+79887766441'


def test_build_validations_number_of_user_phones_xml():
    assert_xml_documents_equal(
        build_validations_number_of_user_phones_xml([
            {
                u'number': u'+79010000001',
                u'valid': u'valid-value',
                u'confirmed_date': datetime(2015, 5, 1, 5, 2, 5),
                u'validations_number': 42,
                u'other_accounts': 31,
            }
        ]),
        u'''
        <?xml version="1.0" encoding="utf-8"?>
        <doc>
            <phone number="+79010000001"
                   validations_number="42"
                   valid="valid-value"
                   confirmed_date="2015-05-01 05:02:05"
                   other_accounts="31" />
        </doc>
        ''',
    )


def test_build_have_user_once_validated_phone_xml():
    assert_xml_documents_equal(
        build_have_user_once_validated_phone_xml(True, u'ok'),
        u'''
        <?xml version="1.0" encoding="utf-8"?>
        <doc><have_user_once_validated_phone value="1" reason="ok"/></doc>
        ''',
    )
    assert_xml_documents_equal(
        build_have_user_once_validated_phone_xml(False, u'some shit'),
        u'''
        <?xml version="1.0" encoding="utf-8"?>
        <doc><have_user_once_validated_phone value="0" reason="some shit"/></doc>
        ''',
    )


def test_build_user_phones_xml():
    assert_xml_documents_equal(
        build_user_phones_xml(939, []),
        u'''
        <?xml version="1.0" encoding="utf-8"?>
        <doc><uid>939</uid></doc>
        ''',
    )
    assert_xml_documents_equal(
        build_user_phones_xml(
            972,
            [
                {
                    u'id': 19,
                    u'number': u'+79010000001',
                    u'masked_number': u'+7901000****',
                    u'active': True,
                    u'secure': False,
                    u'cyrillic': False,
                    u'valid': u'valid',
                    u'validation_date': datetime(2011, 1, 3, 3, 2, 1),
                    u'validations_left': 3,
                    u'autoblocked': False,
                    u'permblocked': False,
                    u'blocked': False,
                },
                {
                    u'id': 21,
                    u'number': u'+79020000002',
                    u'masked_number': u'+7902000****',
                    u'active': False,
                    u'secure': True,
                    u'cyrillic': True,
                    u'valid': u'msgsent',
                    u'validation_date': datetime(2011, 1, 5, 1, 2, 4),
                    u'validations_left': 0,
                    u'autoblocked': True,
                    u'permblocked': True,
                    u'blocked': True,
                },
            ],
        ),
        u'''
        <?xml version="1.0" encoding="utf-8"?>
        <doc>
            <uid>972</uid>
            <phone id="19"
                   number="+79010000001"
                   masked_number="+7901000****"
                   active="1"
                   secure="0"
                   cyrillic="0"
                   valid="valid"
                   validation_date="2011-01-03 03:02:01"
                   validations_left="3"
                   autoblocked="0"
                   permblocked="0"
                   blocked="0" />
            <phone id="21"
                   number="+79020000002"
                   masked_number="+7902000****"
                   active="0"
                   secure="1"
                   cyrillic="1"
                   valid="msgsent"
                   validation_date="2011-01-05 01:02:04"
                   validations_left="0"
                   autoblocked="1"
                   permblocked="1"
                   blocked="1" />
        </doc>
        ''',
    )
    assert_xml_documents_equal(
        build_user_phones_xml(
            972,
            [{
                u'id': 19,
                u'number': u'*******0001',
                u'active': True,
                u'secure': False,
                u'cyrillic': False,
                u'valid': u'valid',
                u'validation_date': datetime(2011, 1, 3, 3, 2, 1),
                u'validations_left': 3,
                u'autoblocked': False,
                u'permblocked': False,
                u'blocked': False,
            }],
        ),
        u'''
        <?xml version="1.0" encoding="utf-8"?>
        <doc>
            <uid>972</uid>
            <phone id="19"
                   number="*******0001"
                   active="1"
                   secure="0"
                   cyrillic="0"
                   valid="valid"
                   validation_date="2011-01-03 03:02:01"
                   validations_left="3"
                   autoblocked="0"
                   permblocked="0"
                   blocked="0" />
        </doc>
        ''',
    )


class TestBuildCheckPhoneDict(TestCase):
    def test_binding_limit_exceeded(self):
        d = build_check_phone_dict([], True)
        eq_(d[u'binding_limit_exceeded'], 1)

        d = build_check_phone_dict([], False)
        eq_(d[u'binding_limit_exceeded'], 0)

    def test_user_list(self):
        d = build_check_phone_dict(
            [
                {
                    u'uid': 1894,
                    u'active': True,
                    u'phoneid': 9457,
                    u'phone': u'+79020000002',
                    u'valid': u'valid',
                    u'validation_date': datetime(2031, 4, 21, 3, 7, 7),
                },
                {
                    u'uid': 4715,
                    u'active': False,
                    u'phoneid': 8141,
                    u'phone': u'+79030000003',
                    u'valid': u'msgsent',
                    u'validation_date': datetime(2002, 4, 16, 3, 4, 7),
                },
            ],
            False,
        )

        eq_(
            d[u'items'],
            [
                {
                    u'uid': u'1894',
                    u'active': u'1',
                    u'phoneid': u'9457',
                    u'phone': u'+79020000002',
                    u'valid': u'valid',
                    u'validation_date': u'2031-04-21 03:07:07',
                },
                {
                    u'uid': u'4715',
                    u'active': u'0',
                    u'phoneid': u'8141',
                    u'phone': u'+79030000003',
                    u'valid': u'msgsent',
                    u'validation_date': u'2002-04-16 03:04:07',
                },
            ],
        )

    def test_null_validation_date(self):
        d = build_check_phone_dict(
            [
                {
                    u'uid': 1894,
                    u'active': False,
                    u'phoneid': 9457,
                    u'phone': u'+79020000002',
                    u'valid': u'notyet',
                    u'validation_date': None,
                },
            ],
            False,
        )

        eq_(
            d[u'items'],
            [
                {
                    u'uid': u'1894',
                    u'active': u'0',
                    u'phoneid': u'9457',
                    u'phone': u'+79020000002',
                    u'valid': u'notyet',
                    u'validation_date': None,
                },
            ],
        )


class TestBuildCheckUserXml(TestCase):
    def test_has_current_phone(self):
        assert_xml_documents_equal(
            build_check_user_xml(431, True, u'+79070000007', True, False),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <uid>431</uid>
                <hascurrentphone>yes</hascurrentphone>
                <number>+79070000007</number>
                <cyrillic>yes</cyrillic>
                <blocked>no</blocked>
            </doc>
            ''',
        )

    def test_has_no_current_phone(self):
        assert_xml_documents_equal(
            build_check_user_xml(413, False, None, None, None),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <uid>413</uid>
                <hascurrentphone>no</hascurrentphone>
            </doc>
            ''',
        )


class TestBuildConfirmXml(TestCase):
    def test_all_attrs_are_filled(self):
        assert_xml_documents_equal(
            build_confirm_xml(795, u'+79019988777', 444, True, True, 7),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone id="795" number="+79019988777" uid="444" valid="1" current="1" left="7" />
            </doc>
            ''',
        )

    def test_all_attrs_are_missing(self):
        assert_xml_documents_equal(
            build_confirm_xml(None, None, None, None, None, None),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone id="" number="" uid="" valid="" current="" left="" />
            </doc>
            ''',
        )

    def test_valid_and_current_are_false(self):
        assert_xml_documents_equal(
            build_confirm_xml(28, u'+79028877666', 14, False, False, 0),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone id="28" number="+79028877666" uid="14" valid="0" current="0" left="0" />
            </doc>
            ''',
        )


def test_build_prolong_valid_dict():
    bpvd = build_prolong_valid_dict
    eq_(bpvd(124, u'ok'), {u'uid': u'124', u'status': u'OK'})
    eq_(bpvd(124, u'notfound'), {u'uid': u'124', u'status': u'NOTFOUND'})
    eq_(bpvd(u'124', u'ok'), {u'uid': u'124', u'status': u'OK'})


def test_build_delete_phone_dict():
    eq_(build_delete_phone_dict(7766, 'ok'), {u'uid': u'7766', u'status': u'OK'})
    eq_(
        build_delete_phone_dict(None, u'notfound'),
        {u'uid': u'', u'status': u'NOTFOUND'},
    )


def test_build_drop_phone_dict():
    eq_(build_drop_phone_dict(7766, 'ok'), {u'uid': u'7766', u'status': u'OK'})
    eq_(
        build_drop_phone_dict(None, u'notfound'),
        {u'uid': u'', u'status': u'NOTFOUND'},
    )


class TestBuildRegisterXml(TestCase):
    def test_revalidated(self):
        assert_xml_documents_equal(
            build_register_xml(2358, u'+79010099888', 459, True),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone id="2358" number="+79010099888" uid="459" revalidated="1"/>
            </doc>
            ''',
        )

    def test_added(self):
        assert_xml_documents_equal(
            build_register_xml(2358, u'+79010099888', 459, False),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone id="2358" number="+79010099888" uid="459" added="1"/>
            </doc>
            ''',
        )


def test_bool_to_onezero():
    btoz = bool_to_onezero
    eq_(btoz(True), u'1')
    eq_(btoz(False), u'0')
    eq_(btoz(None), u'')
    eq_(btoz(u's'), u's')


def test_number_to_str():
    nts = number_to_str
    eq_(nts(382), u'382')
    eq_(nts(None), u'')
    eq_(nts(u's'), u's')


def test_datetime_to_str():
    dts = datetime_to_str
    eq_(dts(datetime(2014, 4, 4, 15, 20, 1)), u'2014-04-04 15:20:01')
    eq_(dts(None), u'')
    eq_(dts(u's'), u's')


def test_bool_to_int():
    b2i = bool_to_int
    eq_(b2i(True), 1)
    eq_(b2i(False), 0)
    eq_(b2i(1), 1)
    eq_(b2i(0), 0)
    eq_(b2i(2), None)
    eq_(b2i(u'1'), None)
    eq_(b2i({u'a': u'b'}), None)


def test_bool_to_yesno():
    b2yn = bool_to_yesno
    eq_(b2yn(True), u'yes')
    eq_(b2yn(False), u'no')
    eq_(b2yn(None), u'')
    eq_(b2yn(u'd'), u'd')
