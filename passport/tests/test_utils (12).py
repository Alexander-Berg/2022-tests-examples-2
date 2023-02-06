# -*- coding: utf-8 -*-
import ipaddress
import json
import pytz

from datetime import datetime
from mock import (
    Mock,
    patch,
)
from netaddr import IPNetwork
from operator import itemgetter

from django.core.exceptions import ValidationError
from django.test import TestCase
from nose.tools import eq_

from passport_grants_configurator.apps.core.exceptions import ProcessError
from passport_grants_configurator.apps.core.utils import (
    ascii_string,
    deep_merge,
    check_grants,
    get_project_id_and_network,
    get_trypo_network_and_mask,
    grouped,
    modify_dict,
    net_overlap_with_trypo,
    normalize_ip_name,
    normalize_network_name,
    not_empty_string,
    switch_keyboard_layout_to_eng,
    yesno_to_bool,
)


def test_deep_merge__ok():
    cases = [
        # Пустые аргументы
        ((None, None), None),
        ((None, {'a': True}), {'a': True}),
        (({'b': False}, None), {'b': False}),

        # Простой merge
        (
            ({'a': True, 'b': True}, {'b': False, 'c': False}),
            {'a': True, 'b': False, 'c': False},
        ),

        # Вложенные словари
        (
            (
                {'foo': {'a': True}, 'bar': 'baz'},
                {'foo': {'b': False}, 'lol': None},
            ),
            {'foo': {'a': True, 'b': False}, 'bar': 'baz', 'lol': None},
        ),
    ]

    for args, expected in cases:
        result = deep_merge(*args)
        eq_(result, expected)


def test_modify_dict():
    cases = [
        (
            ({'a': True}, {'b': False}, ['a']),  # оригинальный словарь, что добавить, что удалить
            {'b': False},
        ),
    ]

    for args, expected in cases:
        result = modify_dict(*args)
        eq_(result, expected)


def test_normalize_network_name__ok():
    cases = [
        ('192.168.1.10', '192.168.1.10'),
        ('192.168.1.10/24', '192.168.1.10/24'),

        (u'Passport.Яндекс.ru', u'passport.яндекс.ru'),
        ('_KOPALKA_', '_kopalka_'),
    ]

    for case, expected in cases:
        result = normalize_network_name(case)
        eq_(result, expected)


def test_normalize_ip_name__ok():
    cases = [
        ((123, IPNetwork('2a02:6b8:c00::/40')), '123@2a02:6b8:c00::/40'),
        (('123', IPNetwork('32:123:133::/32')), '123@32:123:133::/32'),
        ((None, IPNetwork('192.168.1.10/24')), '192.168.1.10/24'),
    ]
    for case, expected in cases:
        result = normalize_ip_name(case)
        yield eq_, result, expected


def test_get_project_id_and_network():
    cases = [
        (('123', IPNetwork('2a02:6b8:c00::/40')), '123@2a02:6b8:c00::/40'),
        (('123', IPNetwork('32:123:133::/32')), '123@32:123:133::/32'),
        ((None, IPNetwork('192.168.1.10/24')), '192.168.1.10/24'),
    ]
    for expected, case in cases:
        result = get_project_id_and_network(case)
        yield eq_, result, expected


def test_get_trypo_network_and_mask():
    network, trypo_mask = get_trypo_network_and_mask('123', IPNetwork('2a02:6b8:c00::/40'))
    eq_(network, IPNetwork('2a02:6b8:c00::123:0:0/40'))
    eq_(
        IPNetwork(str(ipaddress.ip_network(trypo_mask))).ip,
        IPNetwork('ffff:ffff:ff00:0:ffff:ffff::').ip,
    )


def test_net_overlap_with_trypo():
    cases = [
        (('123', IPNetwork('2a02:6b8:c00::/40'), '123', IPNetwork('2a02:6b8:c00::/40')), True),
        (('123', IPNetwork('32:123:133::/32'), '123', IPNetwork('32:123:133::/16')), True),
        ((None, IPNetwork('2a02:6b8:c00::/40'), '123', IPNetwork('2a02:6b8:c00::/40')), True),
        (('123', IPNetwork('2a02:6b8:c00::/40'), None, IPNetwork('2a02:6b8:c00::/40')), True),
        ((None, IPNetwork('2a02:6b8:c00:f80:0:1329::/96'), '1329', IPNetwork('2a02:6b8:c00::/40')), True),
        ((None, IPNetwork('2a02:6b8:c00::1329:0:1'), '1329', IPNetwork('2a02:6b8:c00::/96')), True),
        ((None, IPNetwork('192.168.1.10/24'), None, IPNetwork('192.168.1.10/8')), True),
        ((None, IPNetwork('192.168.1.10'), None, IPNetwork('192.168.1.10')), True),

        (('123', IPNetwork('32:123:133::/32'), '321', IPNetwork('32:123:133::/32')), False),
        (('123', IPNetwork('2a02:6b8:c00::/40'), '123', IPNetwork('2a02:2a02:c00::/40')), False),
        ((None, IPNetwork('192.168.1.10/24'), None, IPNetwork('2a02:6b8:c00::12')), False),
        ((None, IPNetwork('2a02:6b8:c00:f80:0:1329::/96'), None, IPNetwork('32:123:133::/16')), False),
        ((None, IPNetwork('2a02:6b8:c00::1329:0:1'), None, IPNetwork('2a02:6b8:c00::1329:0:3')), False),
    ]
    for case, expected in cases:
        result = net_overlap_with_trypo(*case)
        yield eq_, result, expected


def test_keyboard_layout_switch__ok():
    cases = [
        ('192.168.0.10', '192.168.0.10'),
        (u'passport.НФТВУЧ.net', 'passport.YANDEX.net'),
        (u'_ЛЩЗФДЛФ_', '_KOPALKA_'),
    ]

    for case, expected in cases:
        result = switch_keyboard_layout_to_eng(case)
        eq_(result, expected)


def test_yesno_to_bool__ok():
    cases = [
        ('yes', True),
        ('no', False),

        ('', None),
        (None, None),
        (u'я - пират!', None),
    ]

    for case, expected in cases:
        result = yesno_to_bool(case)
        eq_(result, expected)


def test_grouped__ok():
    cases = [
        (
            # Передаем в функцию список словарей, например
            # и функцию получения ключевого значения из словаря
            (
                [
                    {'a': 3, 'b': 1},
                    {'a': 1, 'b': 2},
                    {'a': 2, 'b': 3},
                    {'a': 3, 'b': 4},
                    {'a': 2, 'b': 5},
                ],
                itemgetter('a'),  # Будем группировать по значению из ключа 'a'
            ),
            # Получаем из функции список кортежей, где
            # первый элемент - уникальное значение ключевой функции
            # второй элемент - список оригинальных объектов, которые дают это значение
            [
                (1, [{'a': 1, 'b': 2}]),
                (2, [{'a': 2, 'b': 3}, {'a': 2, 'b': 5}]),
                (3, [{'a': 3, 'b': 1}, {'a': 3, 'b': 4}]),
            ],
        ),
        (
            # Передаем в функцию список кортежей
            # и функцию получения ключевого значения из кортежа
            (
                [
                    ('a', 2),
                    ('b', 1),
                    ('c', 2),
                    ('d', 3),
                    ('e', 1),
                ],
                itemgetter(1),  # Будем группировать по второму элементу кортежа
            ),
            # Получаем из функции сгруппированные списки оригинальных объектов
            [
                (1, [('b', 1), ('e', 1)]),
                (2, [('a', 2), ('c', 2)]),
                (3, [('d', 3)]),
            ],
        ),
    ]

    for args, expected in cases:
        result = grouped(*args)

        # Преобразуем вложенные итераторы в списки
        result = map(
            lambda key_and_iterator: (key_and_iterator[0], list(key_and_iterator[1])),
            result,
        )

        eq_(result, expected)


class NotEmptyStringValidatorTestCase(TestCase):

    def test_not_empty_string__valid(self):
        valid_cases = [
            'username',
            ' Burger ',
            '\trololo',
            '\night',
        ]

        for case in valid_cases:
            try:
                not_empty_string(case)
            except ValidationError as ex:
                self.fail('Exception %s raised for case %r' % (ex, case))

    def test_not_empty_string__invalid(self):
        invalid_cases = [
            '',
            '\t  \t',
            ' \n  \n\r',
        ]

        for case in invalid_cases:
            self.assertRaises(ValidationError, not_empty_string, case)


class ASCIIStringTestCase(TestCase):

    def test_ascii_string__valid(self):
        valid_cases = [
            'username',
            'vasyan9000',
            'h@ck3r!<script>alert("lol");</script>',
            'some text',
        ]

        for case in valid_cases:
            try:
                ascii_string(case)
            except ValidationError as ex:
                self.fail('Exception %s raised for case %r' % (ex, case))

    def test_ascii_string__invalid(self):
        invalid_cases = [
            u'Яndex',
            u'хацкер',
            u'yandex.ру',
        ]

        for case in invalid_cases:
            self.assertRaises(ValidationError, ascii_string, case)


class CheckGrantsTestCase(TestCase):
    TEST_DIR = '/tmp'
    TEST_PROJECT = 'oauth'
    TEST_SCRIPT = 'test.py'
    TEST_RETURN_CODE = 1

    def setUp(self):
        self.exists_mock = Mock()
        self.result_mock = Mock()

        self.exists_patch = patch(
            'os.path.exists',
            self.exists_mock,
        )
        self.exists_patch.start()

        self.popen_mock = Mock(
            returncode=self.TEST_RETURN_CODE,
            communicate=self.result_mock,
        )
        self.popen_patch = patch(
            'passport_grants_configurator.apps.core.utils.get_subprocess_pipe',
            Mock(return_value=self.popen_mock),
        )
        self.popen_patch.start()

    def tearDown(self):
        self.popen_patch.stop()
        self.exists_patch.stop()

    def setup_mocks(self, exists, result, errors):
        self.exists_mock.return_value = exists
        self.result_mock.return_value = result, errors

    def test_ok(self):
        data = {'production': {'oauth_cons': u'Ошибка'}}
        self.setup_mocks(
            exists=True,
            result=json.dumps(data),
            errors='',
        )
        out = check_grants(self.TEST_PROJECT, self.TEST_DIR, self.TEST_SCRIPT)

        self.assertEqual(out, data)

    def test_empty_data(self):
        data = {}
        self.setup_mocks(
            exists=True,
            result=json.dumps(data),
            errors='',
        )
        out = check_grants(self.TEST_PROJECT, self.TEST_DIR, self.TEST_SCRIPT)

        self.assertFalse(out)

    def test_errors(self):
        data = {'production': {'oauth_cons': 'mess'}}
        self.setup_mocks(
            exists=True,
            result=json.dumps(data),
            errors=u'Что-то не так',
        )
        with self.assertRaises(ProcessError):
            check_grants(self.TEST_PROJECT, self.TEST_DIR, self.TEST_SCRIPT)

    def test_no_file_checker_ok(self):
        data = {}
        self.setup_mocks(
            exists=False,
            result=json.dumps(data),
            errors='',
        )
        out = check_grants(self.TEST_PROJECT, self.TEST_DIR, self.TEST_SCRIPT)

        self.assertFalse(out)
