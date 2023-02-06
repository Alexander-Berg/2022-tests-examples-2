# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.cookies.cookie_y import (
    CookieY,
    CookieYContainer,
    CookieYPackError,
    CookieYUnpackError,
    NameAndValueCookie,
    NameAndValueCookieContainer,
    PermanentCookieY,
    PermanentCookieYContainer,
    SessionCookieY,
    SessionCookieYContainer,
    TestCookie,
    TestCookieContainer,
)
from passport.backend.utils.string import smart_text
import pytest
import six


class CookieYTestCase(unittest.TestCase):
    def test_unpack_basic(self):
        cy = CookieY(
            ['name', 'value'],
            {'name': lambda x: x.upper(), 'value': lambda x: x.upper()},
        )
        blocks, not_unpacked_tail = cy.unpack('field1.field2#field1_2.field2_2')

        eq_(not_unpacked_tail, '')
        eq_(
            blocks,
            [
                {'name': 'FIELD1', 'value': 'FIELD2'},
                {'name': 'FIELD1_2', 'value': 'FIELD2_2'},
            ],
        )

    def test_unpack_empty(self):
        cy = CookieY(['name', 'value'])

        blocks, not_unpacked_tail = cy.unpack('')
        eq_(not_unpacked_tail, '')
        eq_(blocks, [])

    def test_unpack_custom_delimeters(self):
        cy = CookieY(
            ['name', 'value'],
            {'name': lambda x: x.upper(), 'value': lambda x: x.upper()},
            blocks_delimiter='!',
            fields_delimiter='~',
        )
        blocks, not_unpacked_tail = cy.unpack('field1~field2!field1_2~field2_2')
        eq_(not_unpacked_tail, '')
        eq_(
            blocks,
            [
                {'name': 'FIELD1', 'value': 'FIELD2'},
                {'name': 'FIELD1_2', 'value': 'FIELD2_2'},
            ],
        )

    def test_unpack_bad_fields_count(self):
        cy = CookieY(
            ['name', 'value'],
            {'name': lambda x: x.upper(), 'value': lambda x: x.upper()},
        )
        blocks, not_unpacked_tail = cy.unpack('field1.field2#field1_2.field2_2#field1_3.field2_3.field3_3#field1_4')

        eq_(not_unpacked_tail, 'field1_4')
        eq_(
            blocks,
            [
                {'name': 'FIELD1', 'value': 'FIELD2'},
                {'name': 'FIELD1_2', 'value': 'FIELD2_2'},
                {'name': 'FIELD1_3', 'value': 'FIELD2_3.FIELD3_3'}
            ],
        )

    @pytest.mark.skipif(six.PY3, reason='not applicable for Python 3')
    def test_unpack_with_bad_urlencode(self):
        cy = CookieY(
            ['name', 'value'],
            {'name': CookieY.unpack_urlencoded_value, 'value': lambda x: x.upper()},
        )
        blocks, not_unpacked_tail = cy.unpack('field1%D0%B1%D0%BB%D0%B0.field2#field1_2%E9%98%00.field2_2')
        eq_(not_unpacked_tail, 'field1_2%E9%98%00.field2_2')
        eq_(
            blocks,
            [
                {'name': u'field1бла', 'value': 'FIELD2'},
            ],
        )

    def test_unpack_with_bad_int_value(self):
        cy = CookieY(
            ['name', 'value'],
            {'name': CookieY.unpack_int_value, 'value': lambda x: x.upper()},
        )
        blocks, not_unpacked_tail = cy.unpack('234.field2#field1_2.field2_2')
        eq_(not_unpacked_tail, 'field1_2.field2_2')
        eq_(
            blocks,
            [
                {'name': 234, 'value': 'FIELD2'},
            ],
        )

    def test_pack_basic(self):
        cy = CookieY(
            ['name', 'value'],
            fields_packers={'name': lambda x: x.upper(), 'value': lambda x: x.upper()},
            unique_field='name',
        )
        cookie = cy.pack(
            [
                {'name': 'field1', 'value': 'field2'},
                {'name': 'field1_2', 'value': 'field2_2'}
            ],
        )
        eq_(cookie, 'FIELD1.FIELD2#FIELD1_2.FIELD2_2')

    def test_pack_custom_delimeters(self):
        cy = CookieY(
            ['name', 'value'],
            fields_packers={'name': lambda x: x.upper(), 'value': lambda x: x.upper()},
            unique_field='name',
            blocks_delimiter='!',
            fields_delimiter='~',
        )
        cookie = cy.pack(
            [
                {'name': 'field1', 'value': 'field2'},
                {'name': 'field1_2', 'value': 'field2_2'}
            ],

        )
        eq_(cookie, 'FIELD1~FIELD2!FIELD1_2~FIELD2_2')

    def test_pack_with_urldecode(self):
        cy = CookieY(
            ['name', 'value'],
            fields_packers={'name': CookieY.pack_urldecoded_value, 'value': CookieY.pack_urldecoded_value},
            unique_field='name',
        )
        cookie = cy.pack(
            [
                {'name': u'тест', 'value': 'f i e l d 2'},
                {'name': 'name', 'value': 'field2_2'}
            ],
        )
        eq_(cookie, '%D1%82%D0%B5%D1%81%D1%82.f%20i%20e%20l%20d%202#name.field2_2')

    def test_pack_with_int_value(self):
        cy = CookieY(
            ['name', 'value'],
            fields_packers={'name': lambda x: x, 'value': CookieY.pack_int_value},
            unique_field='name',
        )
        cookie = cy.pack(
            [
                {'name': 'name1', 'value': 2},
                {'name': 'name2', 'value': 34}
            ],
        )
        eq_(cookie, 'name1.2#name2.34')

    @raises(CookieYPackError)
    def test_pack_not_unique_field(self):
        cy = CookieY(
            ['name', 'value'],
            fields_packers={'name': lambda x: x.upper(), 'value': lambda x: x.upper()},
            unique_field='name',
        )
        cy.pack(
            [
                {'name': 'field1', 'value': 'field2'},
                {'name': 'field1', 'value': 'field2_2'}
            ],
        )

    @raises(CookieYPackError)
    def test_pack_bad_fields_set(self):
        cy = CookieY(
            ['name', 'value'],
            fields_packers={'name': lambda x: x.upper(), 'value': lambda x: x.upper()},
            unique_field='name',
        )
        cy.pack(
            [
                {'name': 'field1', 'value': 'field2', 'bla': 'bla'},
                {'name': 'field1_2', 'value': 'field2_2'}
            ],
        )

    @raises(CookieYPackError)
    def test_pack_with_bad_int_value(self):
        cy = CookieY(
            ['name', 'value'],
            fields_packers={'name': CookieY.pack_int_value, 'value': lambda x: x.upper()},
            unique_field='name',
        )
        cy.pack(
            [
                {'name': '123', 'value': 'field2'},
            ],
        )


class NameAndValueCookieTestCase(unittest.TestCase):
    """Тесты базовой куки ключ-значение"""

    def get_cookie(self):
        return NameAndValueCookie()

    def test_unpack_basic(self):
        cookie = self.get_cookie()
        blocks, not_unpacked_tail = cookie.unpack('name1.value1#name2.value2')
        eq_(not_unpacked_tail, '')
        eq_(
            blocks,
            [
                {'name': 'name1', 'value': 'value1'},
                {'name': 'name2', 'value': 'value2'},
            ],
        )

    @pytest.mark.skipif(six.PY3, reason='not applicable for Python 3')
    def test_unpack_bad_cookie(self):
        cookie = self.get_cookie()
        _blocks, not_unpacked_tail = cookie.unpack('name1.value1#name2.%E9%98%00')
        eq_(not_unpacked_tail, 'name2.%E9%98%00')

    def test_unpack_urlencode(self):
        cookie = self.get_cookie()
        blocks, not_unpacked_tail = cookie.unpack('name1.value1#first%20name.%D0%B2%D0%B0%D1%81%D1%8F')
        eq_(not_unpacked_tail, '')
        eq_(
            blocks,
            [
                {'name': 'name1', 'value': 'value1'},
                {'name': u'first name', 'value': u'вася'},
            ],
        )

    def test_pack_basic(self):
        cookie = self.get_cookie()
        cookie = cookie.pack(
            [
                {'name': 'name1', 'value': 'value1'},
                {'name': u'first name', 'value': u'вася'},
            ],
        )

        eq_(cookie, 'name1.value1#first%20name.%D0%B2%D0%B0%D1%81%D1%8F')

    @raises(CookieYPackError)
    def test_pack_bad_fields_set(self):
        cookie = self.get_cookie()
        cookie.pack(
            [
                {'name': 'name1', 'value': 'value1', 'bla': 'bla'},
            ],
        )

    @raises(CookieYPackError)
    def test_pack_not_unique_field(self):
        cookie = self.get_cookie()
        cookie.pack(
            [
                {'name': 'name1', 'value': 'value1'},
                {'name': 'name1', 'value': 'value2'},
            ],
        )


class TestCookieYStaticMethods(unittest.TestCase):
    def test_unpack_int_value(self):
        valid_values = [
            ('0', 0),
            (str(2**64+1), 2**64+1),
            ('12345', 12345),
        ]
        for t in valid_values:
            self.assertEqual(CookieY.unpack_int_value(t[0]), t[1])

        invalid_values = [
            '',
            '   ',
            'arhibot',
            u'архибот'.encode('utf-8'),
        ]
        for t in invalid_values:
            with self.assertRaises(CookieYUnpackError):
                CookieY.unpack_int_value(t)

    def test_pack_int_value(self):
        valid_values = [
            (0, '0'),
            (2**64+1, str(2**64+1)),
            (12345, '12345'),
        ]
        for t in valid_values:
            self.assertEqual(CookieY.pack_int_value(t[0]), t[1])

        invalid_values = [
            '',
            '12345',
            'arhibot',
            u'архибот'.encode('utf-8'),
        ]
        for t in invalid_values:
            with self.assertRaises(CookieYPackError):
                CookieY.pack_int_value(t)


class TestCookieTestCase(NameAndValueCookieTestCase):
    """Тесты для "тестовой куки" - наследника от куки ключ-значение"""
    def get_cookie(self):
        return TestCookie()


class SessionCookieYTestCase(NameAndValueCookieTestCase):
    """Тесты сессионной куки-контейнера"""
    def get_cookie(self):
        return SessionCookieY()


class TestPermanentCookieY(unittest.TestCase):

    def get_cookie(self):
        return PermanentCookieY()

    def test_unpack_basic(self):
        yp = self.get_cookie()
        blocks, not_unpacked_tail = yp.unpack('123.name1.value1#456.name2.value2')
        eq_(not_unpacked_tail, '')
        eq_(
            blocks,
            [
                {'name': 'name1', 'value': 'value1', 'expire': 123},
                {'name': 'name2', 'value': 'value2', 'expire': 456},
            ],
        )

    @pytest.mark.skipif(six.PY3, reason='not applicable for Python 3')
    def test_unpack_bad_value(self):
        yp = self.get_cookie()
        _blocks, not_unpacked_tail = yp.unpack('123.name1.value1#456.name2.%E9%98%00')
        eq_(not_unpacked_tail, '456.name2.%E9%98%00')

    def test_unpack_bad_expire(self):
        yp = self.get_cookie()
        _blocks, not_unpacked_tail = yp.unpack('123.name1.value1#456x.name2.value')
        eq_(not_unpacked_tail, '456x.name2.value')

    def test_unpack_urlencode(self):
        yp = self.get_cookie()
        blocks, not_unpacked_tail = yp.unpack('123.name1.value1#456.first%20name.%D0%B2%D0%B0%D1%81%D1%8F')
        eq_(not_unpacked_tail, '')
        eq_(
            blocks,
            [
                {'name': 'name1', 'value': 'value1', 'expire': 123},
                {'name': u'first name', 'value': u'вася', 'expire': 456},
            ],
        )

    def test_pack_basic(self):
        yp = self.get_cookie()
        cookie = yp.pack(
            [
                {'name': 'name1', 'value': 'value1', 'expire': 555},
                {'name': u'first name', 'value': u'вася', 'expire': 666},
            ],
        )

        eq_(cookie, '555.name1.value1#666.first%20name.%D0%B2%D0%B0%D1%81%D1%8F')

    @raises(CookieYPackError)
    def test_pack_bad_fields_set(self):
        yp = self.get_cookie()
        yp.pack(
            [
                {'name': 'name1', 'value': 'value1', 'bla': 'bla', 'expire': 789},
            ],
        )

    @raises(CookieYPackError)
    def test_pack_not_unique_field(self):
        yp = self.get_cookie()
        yp.pack(
            [
                {'name': 'name1', 'value': 'value1', 'expire': 123},
                {'name': 'name1', 'value': 'value2', 'expure': 456},
            ],
        )


class CookieYContainerTestCase(unittest.TestCase):
    def test_basic(self):
        y_container = CookieYContainer(CookieY(['name', 'value'], unique_field='name'))
        cookie = 'name1.value1#name2.value2#name3.value3'
        eq_(
            cookie,
            y_container.parse(cookie).serialize(),
        )

        y_container.erase('name1')
        eq_(
            'name2.value2#name3.value3',
            y_container.serialize(),
        )

        y_container.insert({'name': 'name1', 'value': 'value1'})
        eq_(
            'name2.value2#name3.value3#name1.value1',
            y_container.serialize(),
        )

    @raises(ValueError)
    def test_need_unique_field(self):
        CookieYContainer(CookieY(['name', 'value']))

    def test_get__on_empty_cookie_body__returns_default_object(self):
        y_container = CookieYContainer(CookieY(['name', 'value'], unique_field='name'))
        cookie_value = ''
        y_container.parse(cookie_value)
        block = y_container.get('somename')

        eq_(block, {})

    def test_get(self):
        y_container = CookieYContainer(CookieY(['name', 'value'], unique_field='name'))
        cookie = 'name1.value1#name2.value2#name3.value3'
        y_container.parse(cookie)

        block = y_container.get('name1')
        eq_(block, {'name': 'name1', 'value': 'value1'})
        # Значение блока было скопировано из куки - изменения не отражаются на куке
        block['name'] = 'blablabla'
        eq_(
            cookie,
            y_container.serialize(),
        )


class NameAndValueCookieContainerTestCase(unittest.TestCase):

    def get_container(self):
        return NameAndValueCookieContainer()

    def test_basic(self):
        bytes_cookie = b'second%20name.petrov%D0%AB#first%20name.%D0%B2%D0%B0%D1%81%D1%8F'
        text_cookie = bytes_cookie.decode('utf-8')
        for cookie in [bytes_cookie, text_cookie]:
            container = self.get_container()
            container.parse(cookie)
            eq_(
                smart_text(cookie),
                container.serialize()
            )

            container.insert(u'Я', u'Ы')
            eq_(
                'second%20name.petrov%D0%AB#first%20name.%D0%B2%D0%B0%D1%81%D1%8F#%D0%AF.%D0%AB',
                container.serialize(),
            )

    def test_get(self):
        container = self.get_container()
        cookie = 'second%20name.petrov#first%20name.%D0%B2%D0%B0%D1%81%D1%8F#%D0%AF.%D0%AB'
        container.parse(cookie)

        block = container.get(u'Я')
        eq_(block, {'name': u'Я', 'value': u'Ы'})


class TestCookieContainerTestCase(NameAndValueCookieContainerTestCase):
    def get_container(self):
        return TestCookieContainer()


class SessionCookieYContainerTestCase(NameAndValueCookieContainerTestCase):
    def get_container(self):
        return SessionCookieYContainer()

    def test_parse_value_with_dot(self):
        container = self.get_container()
        cookie = 'bar.ff.8.0.2#vb.ff.2.8.0'
        container.parse(cookie)

        eq_(container.serialize(), 'bar.ff.8.0.2#vb.ff.2.8.0')


class PermanentCookieYContainerTestCase(unittest.TestCase):
    def test_basic(self):
        bytes_cookie = b'123.second%20name.petrov%D0%AB#456.first%20name.%D0%B2%D0%B0%D1%81%D1%8F'
        text_cookie = bytes_cookie.decode('utf-8')
        for cookie in [bytes_cookie, text_cookie]:
            yp_container = PermanentCookieYContainer()
            yp_container.parse(cookie)
            eq_(
                smart_text(cookie),
                yp_container.serialize()
            )

            yp_container.insert(u'Я', u'Ы', 999)
            eq_(
                '123.second%20name.petrov%D0%AB#456.first%20name.%D0%B2%D0%B0%D1%81%D1%8F#999.%D0%AF.%D0%AB',
                yp_container.serialize(),
            )

    def test_get(self):
        yp_container = PermanentCookieYContainer()
        cookie = '123.second%20name.petrov#456.first%20name.%D0%B2%D0%B0%D1%81%D1%8F#789.%D0%AF.%D0%AB'
        yp_container.parse(cookie)

        block = yp_container.get(u'Я')
        eq_(block, {'name': u'Я', 'value': u'Ы', 'expire': 789})

    def test_parse_value_with_dot(self):
        container = PermanentCookieYContainer()
        cookie = '1392991025.clh.1923017#1708091836.yb.13.1'
        container.parse(cookie)

        eq_(container.serialize(), '1392991025.clh.1923017#1708091836.yb.13.1')
