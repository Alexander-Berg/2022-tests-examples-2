# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_almost_equal,
    eq_,
)
from passport.backend.core.compare.compare import (
    compare_lastname_with_names,
    compare_strings,
    FACTOR_NOT_SET,
    find_best_names_factor_index,
    find_best_string_factor_index,
    FuzzyCompareResult,
    names_result_to_simple_factor,
    simple_string_factor_to_mnemonic,
    STRING_FACTOR_INEXACT_MATCH,
    STRING_FACTOR_MATCH,
    STRING_FACTOR_NO_MATCH,
    string_result_to_simple_factor,
)
from passport.backend.core.compare.equality.comparator import (
    CompoundFactorFieldsMetaclass,
    FuzzyComparatorBase,
    FuzzyNameComparator,
    FuzzyStringComparator,
)
from six import string_types


class TestCompoundComparatorFactor(unittest.TestCase):

    def test_compound_factor_class_default(self):
        factors = ('initial_equal', 'symbol_shrink', 'distance', 'xlit_used')
        test_comparator_data = {
            FuzzyComparatorBase: tuple(),
            FuzzyNameComparator: factors + ('aggressive_shrink', 'aggressive_equal'),
            FuzzyStringComparator: factors,
        }
        for comparator_cls, whole_factors in test_comparator_data.items():
            factor_object = comparator_cls.compound_factor_cls()
            eq_(factor_object._fields, whole_factors)
            whole_factors = (whole_factors,) if isinstance(whole_factors, string_types) else whole_factors
            for factor in whole_factors:
                eq_(-1, getattr(factor_object, factor))

    def test_duplicate_factors_ok(self):
        A = CompoundFactorFieldsMetaclass(
            'A',
            (FuzzyComparatorBase,),
            dict(factor_fields=['factor1', 'factor2']),
        )
        B = CompoundFactorFieldsMetaclass(
            'B',
            (A,),
            dict(factor_fields=['factor3', 'factor2']),
        )
        eq_(B.compound_factor_cls()._fields, ('factor3', 'factor2', 'factor1'))

    def test_fuzzy_name_comparator_factor(self):
        cmp = FuzzyNameComparator('ru')
        strings_factors = [
            (
                u'Василий',
                u'Василий',
                1, -1, -1, -1, -1, -1
            ),
            (
                u'Василий',
                u'',
                0, -1, -1, -1, -1, -1
            ),
            (
                u'',
                u'Василий',
                0, -1, -1, -1, -1, -1
            ),
            (
                u'',
                u'',
                0, -1, -1, -1, -1, -1
            ),
            (
                u'Василий',
                u'Вас\nилий',
                0, 0.875, 1.0, -1, -1, -1,
            ),
            (
                u'Василий',
                u'В\v\v\v\v\v\vас\nилий',
                0, 0.5, 1.0, -1, -1, -1,
            ),
            (
                u'Василий',
                u'Vasiliy',
                0, 1.0, 1.0, 1, -1, -1,
            ),
            (
                u'Анатолий',
                u'Евгений',
                0, 1.0, 0.571428571429, 0, 1.0, 0,
            ),
            (
                u'Анатолий',
                u'Евгенiy',
                0, 1.0, 0.533333333333, 1, 1.0, 0,
            ),
            (
                u'Ололоша3456',
                u'Ололоша',
                0, 1.0, 0.733333333333, 0, 0.636363636364, 1,
            ),
            (
                u'Ололоша345678910',
                u'Ололоша',
                0, 1.0, 0.64, 0, 0.4375, 1,
            ),
            (
                u'Ололоша',
                u'Ололоша12345678910',
                0, 1.0, 0.388888888889, 0, 0.388888888889, 1,
            ),
        ]
        for a, b, initial_equal, symbol_shrink, distance, xlit_used, aggressive_shrink, aggressive_equal in strings_factors:
            cmp.compare(a, b)
            assert_almost_equal(initial_equal, cmp.factor.initial_equal)
            assert_almost_equal(symbol_shrink, cmp.factor.symbol_shrink)
            assert_almost_equal(distance, cmp.factor.distance)
            assert_almost_equal(xlit_used, cmp.factor.xlit_used)
            assert_almost_equal(aggressive_shrink, cmp.factor.aggressive_shrink)
            assert_almost_equal(aggressive_equal, cmp.factor.aggressive_equal)

    def test_fuzzy_string_comparator_factor(self):
        cmp = FuzzyStringComparator('ru')
        strings_factors = [
            (
                u'Василий',
                u'Василий',
                1, -1, -1, -1,
            ),
            (
                u'Василий',
                u'',
                0, -1, -1, -1,
            ),
            (
                u'',
                u'Василий',
                0, -1, -1, -1,
            ),
            (
                u'',
                u'',
                0, -1, -1, -1,
            ),
            (
                u'Василий',
                u'Вас\nилий',
                0, 0.875, 1.0, -1,
            ),
            (
                u'Василий',
                u'В\v\v\v\v\v\vас\nилий',
                0, 0.5, 1.0, -1,
            ),
            (
                u'Василий',
                u'Vasiliy',
                0, 1.0, 1.0, 1,
            ),
            (
                u'Анатолий',
                u'Евгений',
                0, 1.0, 0.571428571429, 0,
            ),
            (
                u'Анатолий',
                u'Евгенiy',
                0, 1.0, 0.533333333333, 1,
            ),
            (
                u'Ололоша3456',
                u'Ололоша',
                0, 1.0, 0.733333333333, 0,
            ),
            (
                u'Ололоша345678910',
                u'Ололоша',
                0, 1.0, 0.64, 0,
            ),
        ]
        for i, (a, b, initial_equal, symbol_shrink, distance, xlit_used) in enumerate(strings_factors):
            cmp.compare(a, b)
            assert_almost_equal(initial_equal, cmp.factor.initial_equal)
            assert_almost_equal(symbol_shrink, cmp.factor.symbol_shrink)
            assert_almost_equal(distance, cmp.factor.distance)
            assert_almost_equal(xlit_used, cmp.factor.xlit_used)


class TestStringFactorCompare(unittest.TestCase):

    def test_best_string_factor_index(self):
        """
        Для определения лучшего фактора, используется сортировка по ключу. Ключ - кортеж, включающий в себя
        набор критериев сортировки. В тесте смотрим, как влияют различные критерии на результат для строкового
        фактора.
        """
        StringFactor = FuzzyStringComparator.compound_factor_cls
        factor_lists_results = [
            (
                [StringFactor(1, -1, -1, -1), StringFactor(0, -1, -1, -1)],
                0,
            ),
            (
                [StringFactor(0, -1, -1, -1), StringFactor(0, -1, -1, -1)],
                0,
            ),
            (
                [StringFactor(-1, -1, -1, -1), StringFactor(0, -1, -1, -1)],
                0,
            ),
            (
                [StringFactor(0, 1.0, 0.5, 0), StringFactor(0, 1.0, 0.6, 1), StringFactor(0, 1.0, 0.3, 0)],
                1,
            ),
            (
                [StringFactor(0, 1.0, 0.5, 0), StringFactor(0, 1.0, 0.6, 1), StringFactor(1, -1, -1, -1)],
                2,
            ),
        ]
        for factor_list, result in factor_lists_results:
            eq_(find_best_string_factor_index(factor_list), result)

    def test_best_names_factor_index(self):
        """
        Для определения лучшего фактора, используется сортировка по ключу. Ключ - кортеж, включающий в себя
        набор критериев сортировки. В тесте смотрим, как влияют различные критерии на результат для фактора
        сравнения имен.
        """
        NameFactor = FuzzyNameComparator.compound_factor_cls
        factor_lists_results = [
            (
                [
                    # выбор по критерию initial_equal
                    FuzzyCompareResult(
                        status=True,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(1, -1, -1, -1, -1, -1),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, -1, -1, -1, -1, -1),
                        ),
                    ),
                ],
                0,
            ),
            (
                [
                    # выбор по критерию symbol_shrink
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 0.3, 1.0, 0, -1, -1),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=True,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 0.8, 0.4, 1, 0.6, 1),
                        ),
                    ),
                ],
                1,
            ),
            (
                [
                    # случай одинакового ключа сортировки
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, -1, -1, -1, -1, -1),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, -1, -1, -1, -1, -1),
                        ),
                    ),
                ],
                0,
            ),
            (
                [
                    # случай одинакового ключа сортировки, другой вариант
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(-1, -1, -1, -1, -1, -1),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(0, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, -1, -1, -1, -1, -1),
                        ),
                    ),
                ],
                0,
            ),
            (
                [
                    # выбор по distance при отрицательном решении по distance
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.5, 0, 1.0, 0),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.6, 1, 1.0, 0),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.3, 0, 1.0, 0),
                        ),
                    ),
                ],
                1,
            ),
            (
                [
                    # выбор по distance при положительном решении по distance
                    FuzzyCompareResult(
                        status=True,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.8, 0, -1, -1),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=True,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.9, 1, -1, -1),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=True,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(0, 1.0, 0.9, 0, -1, -1),  # сравнение прошло по имени
                            lastname=NameFactor(0, -1, -1, -1, -1, -1),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=True,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.85, 0, -1, -1),
                        ),
                    ),
                ],
                2,
            ),
            (
                [
                    # выбор по успешному фактору aggressive_equal при различных значениях distance
                    FuzzyCompareResult(
                        status=True,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.5, 0, 0.4, 1),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.6, 1, 1.0, 0),
                        ),
                    ),
                ],
                0,
            ),
            (
                [
                    # выбор по успешному фактору aggressive_equal при одинаковых значениях distance
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.6, 1, 1.0, 0),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=True,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.6, 1, 0.8, 1),
                        ),
                    ),
                ],
                1,
            ),
            (
                [
                    # выбор по фактору aggressive_shrink
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.6, 1, 1.0, 0),
                        ),
                    ),
                    FuzzyCompareResult(
                        status=False,
                        reasons=None,
                        factors=dict(
                            firstname=NameFactor(-1, -1, -1, -1, -1, -1),
                            lastname=NameFactor(0, 1.0, 0.6, 1, 0.3, 1),
                        ),
                    ),
                ],
                0,
            ),
        ]
        for result_list, index in factor_lists_results:
            eq_(find_best_names_factor_index(result_list), index)


class TestSimpleStringFactor(unittest.TestCase):
    def test_equal_names(self):
        """
        Проверяем, что схожие имена считаются одинаковыми или неточно одинаковыми, в соответствии с критериями
        компаратора FuzzyNameComparator
        """
        names_factor = [
            (
                (u'Ivan', u'Petrov'),
                u'Petrov',
                STRING_FACTOR_MATCH,
            ),
            (
                (u'EUGENE', u'ivaNov'),
                u'Ivanov',
                STRING_FACTOR_MATCH,
            ),
            (
                (u'Aлексaндр', u'Kузнeцoв'),  # Латинские буквы с кириллицей
                u'Александр',
                STRING_FACTOR_INEXACT_MATCH,
            ),
            (
                (u'Иван', u'Петров'),
                u'Petrov',
                STRING_FACTOR_MATCH,
            ),
            (
                (u'Иван', u'Петров'),
                u'Petroff',
                STRING_FACTOR_INEXACT_MATCH,
            ),
            (
                (u'Vasia', u'Pupkin'),
                u'Пупкин',
                STRING_FACTOR_MATCH,
            ),
            (
                (u'Vasia', u'Pupkin'),
                u'Vasia666',
                STRING_FACTOR_INEXACT_MATCH,
            ),
        ]
        for n1, n2, factor in names_factor:
            result = compare_lastname_with_names(n1, n2)
            eq_(names_result_to_simple_factor(result), factor)

    def test_different_names(self):
        """
        Проверяем, что различные имена считаются различными, в соответствии с критериями
        компаратора FuzzyNameComparator
        """
        names = (
            (
                (u'A', u'B'),
                u'D',
            ),
            (
                (u'Игорь', u'Собакин'),
                u'Егор',
            ),
            (
                (u'\n\t\t', u'B'),
                u'C',
            ),
            (
                (u'C', u'\n\t\t'),
                u'D',
            ),
            (
                (u'C', u'123456'),
                u'zzz"""-"""',
            ),
        )
        for n1, n2 in names:
            result = compare_lastname_with_names(n1, n2)
            eq_(names_result_to_simple_factor(result), STRING_FACTOR_NO_MATCH)

    def test_equal_strings(self):
        """
        Проверяем, что схожие строки считаются одинаковыми или неточно одинаковыми, в соответствии с критериями
        компаратора FuzzyStringComparator
        """
        strings_factors = [
            (
                u'Пятница',
                u'Пятница',
                STRING_FACTOR_MATCH,
            ),
            (
                u'Олень',
                u'ОЛЕНЬ',
                STRING_FACTOR_MATCH,
            ),
            (
                u'Aлексaндр',  # Латинские буквы с кириллицей
                u'Александр',
                STRING_FACTOR_INEXACT_MATCH,
            ),
            (
                u'asd',
                u'as\nd',
                STRING_FACTOR_INEXACT_MATCH,
            ),
            (
                u'Петров',
                u'Petrov',
                STRING_FACTOR_MATCH,
            ),
            (
                u'Петров',
                u'Petroff',
                STRING_FACTOR_INEXACT_MATCH,
            ),
        ]
        for s1, s2, factor in strings_factors:
            result = compare_strings(s1, s2)
            eq_(string_result_to_simple_factor(result), factor)

    def test_different_strings(self):
        """
        Проверяем, что различные строки считаются различными, в соответствии с критериями
        компаратора FuzzyStringComparator
        """
        strings = (
            (
                u'asd',
                u'a\n\n\nsd',
            ),
            (
                u'пятница',
                u'четверг',
            ),
            (
                u'\n\t\t',
                u'\n',
            ),
        )
        for s1, s2 in strings:
            result = compare_strings(s1, s2)
            eq_(string_result_to_simple_factor(result), STRING_FACTOR_NO_MATCH)

    def test_simple_factor_mnemonics(self):
        eq_(simple_string_factor_to_mnemonic(STRING_FACTOR_MATCH), 'match')
        eq_(simple_string_factor_to_mnemonic(STRING_FACTOR_INEXACT_MATCH), 'inexact_match')
        eq_(simple_string_factor_to_mnemonic(STRING_FACTOR_NO_MATCH), 'no_match')
        eq_(simple_string_factor_to_mnemonic(FACTOR_NOT_SET), 'not_calculated')
        eq_(simple_string_factor_to_mnemonic(123), None)
