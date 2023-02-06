# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.compare import (
    compare_emails,
    compare_lastname_with_names,
    compare_names,
    compare_phones,
    compare_strings,
    STRING_FACTOR_INEXACT_MATCH,
    STRING_FACTOR_MATCH,
    STRING_FACTOR_NO_MATCH,
)
from passport.backend.core.compare.compare import (
    serialize_names_factor,
    serialize_string_factor,
)


class TestCompareNames(unittest.TestCase):
    def test_compare_names(self):
        names_factors = [
            (
                (u'Ivan', u'Petrov'),
                (u'Ivan', u'Petrov'),
                [
                    STRING_FACTOR_MATCH,
                    STRING_FACTOR_MATCH,
                ],
            ),
            (
                (u'EUGENE', u'ivaNov'),
                (u'eugene', u'Ivanov'),
                [
                    STRING_FACTOR_MATCH,
                    STRING_FACTOR_MATCH,
                ],
            ),
            (
                (u'Aлексaндр', u'Kузнeцoв'),  # Латинские буквы с кириллицей
                (u'Кузнецов', u'Александр'),
                [
                    STRING_FACTOR_MATCH,
                    STRING_FACTOR_INEXACT_MATCH,
                ],
            ),
            (
                (u'Иван', u'Петров'),
                (u'Ivan', u'Petrov'),
                [
                    STRING_FACTOR_MATCH,
                    STRING_FACTOR_MATCH,
                ],
            ),
            (
                (u'Иван', u'Петров'),
                (u'Ivan', u'Petroff'),
                [
                    STRING_FACTOR_MATCH,
                    STRING_FACTOR_INEXACT_MATCH,
                ],
            ),
            (
                (u'Vasia', u'Pupkin'),
                (u'Вася', u'Пупкин'),
                [
                    STRING_FACTOR_MATCH,
                    STRING_FACTOR_MATCH,
                ],
            ),
            (
                (u'Козлов', u'Николай'),
                (u'Nikolay', u'Kozlov'),
                [
                    STRING_FACTOR_MATCH,
                    STRING_FACTOR_MATCH,
                ],
            ),
            (
                (u'Козлов', u'Николай'),
                (u'Kozlov', u'Kozlov'),
                [
                    STRING_FACTOR_NO_MATCH,
                    STRING_FACTOR_MATCH,
                ],
            ),
            (
                (u'Ivan', u'Ivan'),
                (u'Petrov', u'Ivan'),
                [
                    STRING_FACTOR_NO_MATCH,
                    STRING_FACTOR_MATCH,
                ],
            ),
            (
                (u'Vasia', u'Pupkin'),
                (u'Vasia666', u'Pupkinn'),
                [
                    STRING_FACTOR_INEXACT_MATCH,
                    STRING_FACTOR_INEXACT_MATCH,
                ],
            ),
            (
                (u'A', u'B'),
                (u'C', u'D'),
                [
                    STRING_FACTOR_NO_MATCH,
                    STRING_FACTOR_NO_MATCH,
                ],
            ),
            (
                (u'Игорь', u'Собакин'),
                (u'Егор', u'Собакин'),
                [
                    STRING_FACTOR_NO_MATCH,
                    STRING_FACTOR_MATCH,
                ],
            ),
            (
                (u'\n\t\t', u'B'),
                (u'C', u'D'),
                [
                    STRING_FACTOR_NO_MATCH,
                    STRING_FACTOR_NO_MATCH,
                ],
            ),
            (
                (u'C', u'\n\t\t'),
                (u'C', u'D'),
                [
                    STRING_FACTOR_MATCH,
                    STRING_FACTOR_NO_MATCH,
                ],
            ),
            (
                (u'C', u'"""-"""'),
                (u'С', u'zzz"""-"""'),
                [
                    STRING_FACTOR_MATCH,
                    STRING_FACTOR_NO_MATCH,
                ],
            ),
            (
                (u'C', u'"""-"""'),
                (u'zzz"""-"""', u'С'),
                [
                    STRING_FACTOR_NO_MATCH,
                    STRING_FACTOR_MATCH,
                ],
            ),
        ]
        for index, (n1, n2, expected_factors) in enumerate(names_factors):
            factors = compare_names(n1, n2)
            eq_(factors, expected_factors, '%d: %s != %s' % (index, factors, expected_factors))


DEFAULT_NOT_CALCULATED_FACTOR = [
    ('initial_equal', -1),
    ('symbol_shrink', -1),
    ('distance', -1),
    ('xlit_used', -1),
    ('aggressive_shrink', -1),
    ('aggressive_equal', -1),
]


class TestCompareLastNameWithNames(unittest.TestCase):
    def test_equal_names(self):
        names_reasons_factors = [
            (
                (u'Ivan', u'Petrov'),
                u'Petrov',
                ['InitialComparator.equal'],
                {
                    'lastname': [('initial_equal', 1), ('symbol_shrink', -1), ('distance', -1), ('xlit_used', -1), ('aggressive_shrink', -1), ('aggressive_equal', -1)],
                    'firstname': DEFAULT_NOT_CALCULATED_FACTOR,
                },
            ),
            (
                (u'EUGENE', u'ivaNov'),
                u'Ivanov',
                ['DistanceComparator.equal'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 1.0), ('xlit_used', -1), ('aggressive_shrink', -1), ('aggressive_equal', -1)],
                    'firstname': DEFAULT_NOT_CALCULATED_FACTOR,
                },
            ),
            (
                (u'Aлексaндр', u'Kузнeцoв'),  # Латинские буквы с кириллицей
                u'Александр',
                [
                    'DistanceComparator.equal',
                    'reversed_order',
                ],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.5), ('xlit_used', 1), ('aggressive_shrink', 1.0), ('aggressive_equal', 0)],
                    'firstname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 9.0 / 11), ('xlit_used', -1), ('aggressive_shrink', -1), ('aggressive_equal', -1)],
                },
            ),
            (
                (u'Иван', u'Петров'),
                u'Petrov',
                ['TransliteratedAndDistanceComparator.equal'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 1.0), ('xlit_used', 1), ('aggressive_shrink', -1), ('aggressive_equal', -1)],
                    'firstname': DEFAULT_NOT_CALCULATED_FACTOR,
                },
            ),
            (
                (u'Иван', u'Петров'),
                u'Petroff',
                ['TransliteratedAndDistanceComparator.equal_suffixes'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.75), ('xlit_used', 1), ('aggressive_shrink', -1), ('aggressive_equal', -1)],
                    'firstname': DEFAULT_NOT_CALCULATED_FACTOR,
                },
            ),
            (
                (u'Vasia', u'Pupkin'),
                u'Пупкин',
                ['TransliteratedAndDistanceComparator.equal'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 1.0), ('xlit_used', 1), ('aggressive_shrink', -1), ('aggressive_equal', -1)],
                    'firstname': DEFAULT_NOT_CALCULATED_FACTOR,
                },
            ),
            (
                (u'Vasia', u'Pupkin'),
                u'Vasia666',
                ['NFDFilterComparator.equal', 'reversed_order'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 3.0 / 7), ('xlit_used', 0), ('aggressive_shrink', 0.625), ('aggressive_equal', 0)],
                    'firstname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.625), ('xlit_used', 0), ('aggressive_shrink', 0.625), ('aggressive_equal', 1)],
                },
            ),
        ]
        for n1, n2, reasons, factors in names_reasons_factors:
            result = compare_lastname_with_names(n1, n2)
            ok_(result.status, '%s not in %s %s' % (n2, n1[0], n1[1]))
            eq_(result.reasons, reasons)
            eq_(serialize_names_factor(result.factors), factors)

    def test_different_names(self):
        names_reasons_factors = (
            (
                (u'A', u'B'),
                u'D',
                ['FuzzyComparatorBase.no_match'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.5), ('xlit_used', 0), ('aggressive_shrink', 1.0), ('aggressive_equal', 0)],
                    'firstname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.5), ('xlit_used', 0), ('aggressive_shrink', 1.0), ('aggressive_equal', 0)],
                },
            ),
            (
                (u'Игорь', u'Собакин'),
                u'Егор',
                ['FuzzyComparatorBase.no_match'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.5), ('xlit_used', 0), ('aggressive_shrink', 1.0), ('aggressive_equal', 0)],
                    'firstname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 5.0 / 7), ('xlit_used', 0), ('aggressive_shrink', 1.0), ('aggressive_equal', 0)],
                },
            ),
            (
                (u'\n\t\t', u'B'),
                u'C',
                ['FuzzyComparatorBase.no_match'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.5), ('xlit_used', 0), ('aggressive_shrink', 1.0), ('aggressive_equal', 0)],
                    'firstname': [('initial_equal', 0), ('symbol_shrink', 0.0), ('distance', 0.0), ('xlit_used', 0), ('aggressive_shrink', 0.0), ('aggressive_equal', 0)],
                },
            ),
            (
                (u'C', u'\n\t\t'),
                u'D',
                ['NFKCLowerConverter.empty_normalized'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 0.0), ('distance', 0.0), ('xlit_used', 0), ('aggressive_shrink', 0.0), ('aggressive_equal', 0)],
                    'firstname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.5), ('xlit_used', 0), ('aggressive_shrink', 1.0), ('aggressive_equal', 0)],
                },
            ),
            (
                (u'C', u'123456'),
                u'zzz"""-"""',
                ['NFDFilterComparator.empty_normalized'],
                {
                    'lastname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.375), ('xlit_used', 0), ('aggressive_shrink', 0.0), ('aggressive_equal', 0)],
                    'firstname': [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.1), ('xlit_used', 1), ('aggressive_shrink', 0.3), ('aggressive_equal', 0)],
                },
            ),
        )
        for n1, n2, reasons, factors in names_reasons_factors:
            result = compare_lastname_with_names(n1, n2)
            eq_(result.status, False, '%s in %s %s' % (n2, n1[0], n1[1]))
            eq_(result.reasons, reasons)
            eq_(serialize_names_factor(result.factors), factors)


class TestCompareStrings(unittest.TestCase):
    def test_equal_strings(self):
        strings_reasons_factors = [
            (
                u'Пятница',
                u'Пятница',
                ['InitialComparator.equal'],
                [('initial_equal', 1), ('symbol_shrink', -1), ('distance', -1), ('xlit_used', -1)],
            ),
            (
                u'Олень',
                u'ОЛЕНЬ',
                ['DistanceComparator.equal'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 1.0), ('xlit_used', -1)],
            ),
            (
                u'Aлексaндр',  # Латинские буквы с кириллицей
                u'Александр',
                ['DistanceComparator.equal'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 9.0 / 11), ('xlit_used', -1)],
            ),
            (
                u'Петров',
                u'Petrov',
                ['TransliteratedAndDistanceComparator.equal'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 1.0), ('xlit_used', 1)],
            ),
            (
                u'Петров',
                u'Petroff',
                ['TransliteratedAndDistanceComparator.equal_suffixes'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.75), ('xlit_used', 1)],
            ),
        ]
        for a1, a2, reasons, factors in strings_reasons_factors:
            result = compare_strings(a1, a2)
            ok_(result.status, '%s != %s' % (a1, a2))
            eq_(result.reasons, reasons)
            eq_(serialize_string_factor(result.factors), factors)

    def test_different_strings(self):
        strings_reasons_factors = (
            (
                u'пятница',
                u'четверг',
                ['FuzzyComparatorBase.no_match'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 7.0 / 13), ('xlit_used', 0)],
            ),
            (
                u'\n\t\t',
                u'\n',
                ['NFKCLowerConverter.empty_normalized'],
                [('initial_equal', 0), ('symbol_shrink', 0.0), ('distance', 1.0), ('xlit_used', 1)],
            ),
        )
        for a1, a2, reasons, factors in strings_reasons_factors:
            result = compare_strings(a1, a2)
            eq_(result.status, False, '%s == %s' % (a1, a2))
            eq_(result.reasons, reasons)
            eq_(serialize_string_factor(result.factors), factors)

    def test_compare_with_distance_threshold(self):
        strings_thresholds_statuses = (
            # из-за транслитерации расстояние между этими словами - 3
            ('cakes1967', 'cakecake67', 0.75, True),
            ('cakes1967', 'cakecake67', 0.9, False),
        )
        for s1, s2, threshold, status in strings_thresholds_statuses:
            result = compare_strings(s1, s2, distance_threshold=threshold)
            eq_(result.status, status)


class TestCompareEmails(unittest.TestCase):
    def test_equal_strings(self):
        strings_reasons_factors = [
            (
                u'vasiliy@yandex.ru',
                u'vasiliy@yandex.ru',
                ['InitialComparator.equal'],
                [('initial_equal', 1), ('symbol_shrink', -1), ('distance', -1)],
            ),
            (
                u'vasiliy@yandex.ru',
                u'vasiliy@yandex.com',
                ['DistanceComparator.equal'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.85)],
            ),
            (
                u'василий@yandex.ru',
                u'васильев@yandex.ru',
                ['DistanceComparator.equal'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.85)],
            ),
        ]
        for a1, a2, reasons, factors in strings_reasons_factors:
            result = compare_emails(a1, a2)
            ok_(result.status, '%s != %s' % (a1, a2))
            eq_(result.reasons, reasons)
            eq_(serialize_string_factor(result.factors), factors)

    def test_different_strings(self):
        strings_reasons_factors = (
            (
                u'пятница',
                u'четверг',
                ['FuzzyComparatorBase.no_match'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 7.0 / 13)],
            ),
            (
                u'v@ya.ru',
                u'v@ya.com',
                ['FuzzyComparatorBase.no_match'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 0.7)],
            ),
        )
        for a1, a2, reasons, factors in strings_reasons_factors:
            result = compare_emails(a1, a2)
            eq_(result.status, False, '%s == %s' % (a1, a2))
            eq_(result.reasons, reasons)
            eq_(serialize_string_factor(result.factors), factors)


class TestComparePhones(unittest.TestCase):
    def test_equal_strings(self):
        strings_reasons_factors = [
            (
                u'89121234567',
                u'89121234567',
                ['InitialComparator.equal'],
                [('initial_equal', 1), ('symbol_shrink', -1), ('distance', -1)],
            ),
            (
                u'89121234567',
                u'+79121234567',
                ['DistanceComparator.equal'],
                [('initial_equal', 0), ('symbol_shrink', 11.0 / 12), ('distance', 11.0 / 12)],
            ),
            (
                u'89121234511',
                u'79121234512',
                ['DistanceComparator.equal'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 11.0 / 13)],
            ),

        ]
        for a1, a2, reasons, factors in strings_reasons_factors:
            result = compare_phones(a1, a2)
            ok_(result.status, '%s != %s' % (a1, a2))
            eq_(result.reasons, reasons)
            eq_(serialize_string_factor(result.factors), factors)

    def test_different_strings(self):
        strings_reasons_factors = (
            (
                u'пятница',
                u'четверг',
                ['FuzzyComparatorBase.no_match'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 7.0 / 13)],
            ),
            (
                u'89121111111',
                u'89121111222',
                ['FuzzyComparatorBase.no_match'],
                [('initial_equal', 0), ('symbol_shrink', 1.0), ('distance', 11.0 / 14)],
            ),
        )
        for a1, a2, reasons, factors in strings_reasons_factors:
            result = compare_phones(a1, a2)
            eq_(result.status, False, '%s == %s' % (a1, a2))
            eq_(result.reasons, reasons)
            eq_(serialize_string_factor(result.factors), factors)
