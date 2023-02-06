# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_almost_equal,
    eq_,
    ok_,
)
from passport.backend.core.compare.equality.comparator import (
    _get_reason,
    DistanceComparator,
    FuzzyComparatorBase,
    FuzzyControlAnswersComparator,
    FuzzyNameComparator,
    FuzzyStrictComparator,
    FuzzyStringComparator,
    InitialComparator,
    NFDFilterComparator,
    NFKCLowerConverter,
    REASON_MATCH,
    REASON_MATCH_SUFFIX,
    REASON_NO_MATCH,
    REASON_NO_MATCH_EMPTY,
    REASON_NO_MATCH_EMPTY_NORMALIZED,
    TransliteratedAndDistanceComparator,
    TransliteratedTrigramsAndDistanceComparator,
    TrigramsAndDistanceComparator,
)
from six import string_types


INVALID_UTF_CHAR = u'\udf00'


def assert_compound_factor_eq(pairs, factor):
    fields = [factor._fields] if isinstance(factor._fields, string_types) else factor._fields
    for pair, field in zip(pairs, fields):
        eq_(pair[0], field)
        assert_almost_equal(pair[1], getattr(factor, field), delta=0.015)


class TestInitialComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = InitialComparator()

    def test_equal_strings(self):
        eq_strings = [
            (u'1', u'1'),
            (u'Фыва', u'Фыва'),
            (INVALID_UTF_CHAR, INVALID_UTF_CHAR),
        ]
        for i, (a, b) in enumerate(eq_strings):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            eq_(result.reasons, _get_reason(self.cmp.__class__, REASON_MATCH))
            assert_compound_factor_eq([('initial_equal', 1)], self.cmp.factor)

    def test_different_strings(self):
        diff_strings = [
            (u'', u''),
            (u'a', u'A'),
            (u'ÇAĞATAY', u'CAGATAY'),
            (u'ÇETİN', u'CETIN'),
            (INVALID_UTF_CHAR, u'1'),
        ]
        for i, (a, b) in enumerate(diff_strings):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            ok_(result.reasons[0] in
                _get_reason(FuzzyComparatorBase, REASON_NO_MATCH) +
                _get_reason(InitialComparator, REASON_NO_MATCH_EMPTY))
            assert_compound_factor_eq([('initial_equal', 0)], self.cmp.factor)


class TestNFKCLowerConverter(unittest.TestCase):
    def setUp(self):
        # используем InitialComparator чтобы сравнить результаты преобразования
        self.cmp_type = type('TestNFKC', (NFKCLowerConverter, InitialComparator), {})
        self.cmp = self.cmp_type()

    def test_equal_strings(self):
        eq_strings_shrink_factors = [
            (u'a', u'a', 1.0),
            (u'ab', u'ab', 1.0),
            (u'a-bcdefghjkl', u'\va\b-b\r\n\f\acdefghjkl', 12.0 / 18),  # удаление совсем левых символов
            (u'abcdef', u'abcdef\n\n\n\n', 0.6),  # граница shrink-фактора
            (u'Vasiliy', u'vAsIliy', 1.0),  # регистр
            (u'\u212b', u'\u00c5', 1.0),  # композиция, в т.ч. compatibility-символы
            (u'\u00c5', u'a\u030a', 1.0),
            (u'q\u0307\u0323', u'q\u0323\u0307', 1.0),  # еще примеры см. http://www.unicode.org/reports/tr15/
        ]
        for i, (a, b, shrink_factor) in enumerate(eq_strings_shrink_factors):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            eq_(result.reasons, _get_reason(InitialComparator, REASON_MATCH))
            assert_compound_factor_eq(
                [('symbol_shrink', shrink_factor), ('initial_equal', 1)],
                self.cmp.factor,
            )

    def test_different_strings(self):
        diff_strings_shrink_factors = [
            (u'\n\r\t', u'', 0.0, 0),
            (u'a', u'', 0.0, 0),
            (u'ab\v\v', u'ab', 0.5, 1),
            (u'a' * 59 + '\v' * 41, u'a' * 59, 0.59, 1),
            (u'a', u'b', 1.0, 0),
            (u'ab', u'ba', 1.0, 0),
            (u'ab', u'a b', 1.0, 0),
            (u'abc', u'abс\u0308', 1.0, 0),  # отличия в лишних комбинирующих символах
            (u'q\u0307\u0323', u'q\u0323\u0307\u0307', 1.0, 0),
            (u'ÇAĞATAY', u'CAGATAY', 1.0, 0),
            (u'ÇETİN', u'CETIN', 1.0, 0),
            (INVALID_UTF_CHAR, INVALID_UTF_CHAR, 0.0, 0),  # становится пустым после нормализации
        ]
        for i, (a, b, shrink_factor, equal) in enumerate(diff_strings_shrink_factors):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            ok_(result.reasons[0] in
                _get_reason(FuzzyComparatorBase, REASON_NO_MATCH) +
                _get_reason(NFKCLowerConverter, REASON_NO_MATCH_EMPTY_NORMALIZED))
            assert_compound_factor_eq(
                [('symbol_shrink', shrink_factor), ('initial_equal', equal)],
                self.cmp.factor,
            )

    def test_i_behavior(self):
        en = self.cmp_type('en')
        tr = self.cmp_type('tr')
        names_upper = u'BÜNYAMİN', u'BARIŞ'
        names_lower_en = u'bünyami\u0307n', u'bariş'
        # Используем алгоритм приведения к общему регистру, не зависящий от языка
        names_lower_tr = names_lower_en
        ok_(en.compare(names_upper[0], names_lower_en[0]).status)
        ok_(en.compare(names_upper[1], names_lower_en[1]).status)
        ok_(tr.compare(names_upper[0], names_lower_tr[0]).status)
        ok_(tr.compare(names_upper[1], names_lower_tr[1]).status)


class TestDistanceComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = DistanceComparator()

    def test_equal_strings(self):
        eq_strings_distance_factors = [
            (u'a', u'a', 1.0),
            (u'ab', u'ab', 1.0),
            (u'abc', u'abc', 1.0),
            (INVALID_UTF_CHAR, INVALID_UTF_CHAR, 1.0),
            (u'abc', u'acb', 0.75),  # 1 опечатка, длина исходной строки 3 => значение 3/(3+1)
            (u'abc', u'abcd', 0.75),
            (u'abcdef', u'abcdefgh', 0.75),
            (u'abcdef', u'bacedf', 0.75),
            (u'abcdefфывфыв', u'bacedfфывфыв', 12.0 / 14),
            (u'ктото пришел', u'кто-то пришол!', 12.0 / 15),
            # опечатки от саппортов
            (u'Гаврикова', u'Гварикова', 0.9),
            (u'Борисова', u'Барисова', 8.0 / 9),
            (u'Прокопенко', u'Пракопенко', 10.0 / 11),
            (u'Тефтелька', u'Тевтелька', 0.9),
            (u'романова', u'ронамова', 0.8),
            (u'зимина', u'зимена', 6.0 / 7),
            (u'зейгер', u'зегер', 6.0 / 7),
            (u'Дорохина', u'орохина', 8.0 / 9),
            (u'нимфа-карелла', u'нимфа-карэлла', 13.0 / 14),
            (u'ярочкина', u'zрочкина', 8.0 / 9),
            (u'Горелова', u'Гарелова', 8.0 / 9),
            (u'животягина', u'животчгина', 10.0 / 11),
            (u'Сыс', u'Сыс', 1.0),
            (u'Потураева', u'Потурвева', 0.9),
            (u'Семенова', u'Сеёнова', 0.8),
            (u'гайдай', u'гайлай', 6.0 / 7),
            (u'сергей петрович', u'сургей петрович', 15.0 / 16),
            (u'Лавелина', u'Лавенина', 8.0 / 9),
            (u'Давыдова', u'Давыова', 8.0 / 9),
            (u'Вострухина', u'Воструин', 10.0 / 12),
            (u'саликова', u'салиикова', 8.0 / 9),
            (u'Карамышева', u'Караьышева', 10.0 / 11),
            (u'Сумеречный щит и крылья надежы', u'Сумеречный щит и копьё света', 30.0 / 39),
            (u'Шульгина', u'Булыгина', 8.0 / 10),
        ]
        for i, (a, b, distance_factor) in enumerate(eq_strings_distance_factors):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            eq_(result.reasons, _get_reason(self.cmp.__class__, REASON_MATCH))
            assert_compound_factor_eq(
                [('distance', distance_factor)],
                self.cmp.factor,
            )

    def test_different_strings(self):
        diff_strings_distance_factors = [
            (u'', u'1', 0.0),
            (u'a', u'', 0.5),
            (u'a', u'b', 0.5),
            (u'a', u'A', 0.5),
            (u'ab', u'ba', 2.0 / 3),
            (u'ab', u'abc', 2.0 / 3),
            (u'abc', u'abbbc', 0.6),
            (u'abcdeff', u'abcdefghl', 0.7),
            (u'ш' * 74, u'ш' * 100, 0.74),  # граница - 0.75
            (u'rbcddf', u'bacedf', 6.0 / 9),
            (u'abcdefфывsфыв', u'bacedfфsывфывw', 13.0 / 18),
            (u'ктото пришел', u'кто-то пришол и!', 12.0 / 17),
            (u'ÇETİN', u'CETIN', 5.0 / 7),
        ]
        for i, (a, b, distance_factor) in enumerate(diff_strings_distance_factors):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            eq_(result.reasons, _get_reason(FuzzyComparatorBase, REASON_NO_MATCH))
            assert_compound_factor_eq(
                [('distance', distance_factor)],
                self.cmp.factor,
            )

    def test_equal_strings_custom_threshold(self):
        eq_strings_distance_factors_statuses = [
            (u'a', u'a', 1.0, True),
            (u'ab', u'ab', 1.0, True),
            (u'abc', u'abc', 1.0, True),
            (u'abcdefghj', u'abcdefghjk', 0.9, True),
            (u'abc', u'acb', 0.75, False),
        ]
        cmp = DistanceComparator(distance_threshold=0.9)
        for i, (a, b, distance_factor, status) in enumerate(eq_strings_distance_factors_statuses):
            result = cmp.compare(a, b)
            eq_(result.status, status, u'%d: %s != %s' % (i, a, b))
            assert_compound_factor_eq(
                [('distance', distance_factor)],
                cmp.factor,
            )


class TestTrigramsAndDistanceComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = TrigramsAndDistanceComparator()

    def test_equal_strings(self):
        eq_strings_distance_factors = [
            (u'a', u'a', 1.0, 1.0),
            (u'ab', u'ab', 1.0, 1.0),
            (INVALID_UTF_CHAR, INVALID_UTF_CHAR, 1.0, 1.0),
            (u'abc', u'abc', 1.0, 1.0),
            (u'abc', u'abcd', 0.75, 0.55),
            (u'abcdef', u'abcdefgh', 0.75, 0.67),
            (u'abcdefфывфыв', u'bacedfфывфыв', 12.0 / 14, 0.5),
            (u'ктото пришел', u'кто-то пришол!', 12.0 / 15, 0.53),
            # опечатки от саппортов
            (u'Гаврикова', u'Гварикова', 0.9, 0.64),
            (u'Борисова', u'Барисова', 8.0 / 9, 0.7),
            (u'Прокопенко', u'Пракопенко', 10.0 / 11, 0.75),
            (u'Тефтелька', u'Тевтелька', 0.9, 0.73),
            (u'романова', u'ронамова', 0.8, 0.5),
            (u'зимина', u'зимена', 6.0 / 7, 0.63),
            (u'зейгер', u'зегер', 6.0 / 7, 0.67),
            (u'Дорохина', u'орохина', 8.0 / 9, 0.74),
            (u'нимфа-карелла', u'нимфа-карэлла', 13.0 / 14, 0.8),
            (u'ярочкина', u'zрочкина', 8.0 / 9, 0.7),
            (u'Горелова', u'Гарелова', 8.0 / 9, 0.7),
            (u'животягина', u'животчгина', 10.0 / 11, 0.75),
            (u'Сыс', u'Сыс', 1.0, 1.0),
            (u'Потураева', u'Потурвева', 0.9, 0.73),
            (u'Семенова', u'Сеёнова', 0.8, 0.63),
            (u'гайдай', u'гайлай', 6.0 / 7, 0.63),
            (u'сергей петрович', u'сургей петрович', 15.0 / 16, 0.82),
            (u'Лавелина', u'Лавенина', 8.0 / 9, 0.7),
            (u'Давыдова', u'Давыова', 8.0 / 9, 0.74),
            (u'Вострухина', u'Воструин', 10.0 / 12, 0.55),
            (u'саликова', u'салиикова', 8.0 / 9, 0.86),
            (u'Карамышева', u'Караьышева', 10.0 / 11, 0.75),
            (u'Сумеречный щит и крылья надежы', u'Сумеречный щит и копьё света', 30.0 / 39, 0.58),
        ]
        for i, (a, b, distance_factor, similarity_factor) in enumerate(eq_strings_distance_factors):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            eq_(result.reasons, _get_reason(self.cmp.__class__, REASON_MATCH))
            assert_compound_factor_eq(
                [('distance', distance_factor), ('similarity', similarity_factor)],
                self.cmp.factor,
            )

    def test_different_strings(self):
        diff_strings_distance_factors = [
            (u'', u'1', 0.0, 0.0),
            (u'a', u'', 0.5, 0.0),
            (u'a', u'b', 0.5, 0.0),
            (u'a', u'A', 0.5, 0.0),
            (u'ab', u'ba', 2.0 / 3, 0.0),
            (u'ab', u'abc', 2.0 / 3, 0.44),
            (u'abc', u'abbbc', 0.6, 0.67),
            (u'abc', u'acb', 0.75, 0.2),
            (u'abcdef', u'bacedf', 0.75, 0.13),
            (u'abcdeff', u'abcdefghl', 0.7, 0.6),
            (u'ш' * 74, u'ш' * 100, 0.74, 0.85),  # граница - 0.75
            (u'rbcddf', u'bacedf', 6.0 / 9, 0.25),
            (u'abcdefфывsфыв', u'bacedfфsывфывw', 13.0 / 18, 0.06),
            (u'ктото пришел', u'кто-то пришол и!', 12.0 / 17, 0.5),
            (u'ÇETİN', u'CETIN', 5.0 / 7, 0.14),
            (u'Шульгина', u'Булыгина', 8.0 / 10, 0.4),
        ]
        for i, (a, b, distance_factor, similarity_factor) in enumerate(diff_strings_distance_factors):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            eq_(result.reasons, _get_reason(FuzzyComparatorBase, REASON_NO_MATCH))
            assert_compound_factor_eq(
                [('distance', distance_factor), ('similarity', similarity_factor)],
                self.cmp.factor,
            )

    def test_equal_strings_custom_threshold(self):
        eq_strings_distance_factors_statuses = [
            (u'a', u'a', 1.0, 1.0, True),
            (u'ab', u'ab', 1.0, 1.0, True),
            (u'abc', u'abc', 1.0, 1.0, True),
            (u'abcdefghj', u'abcdefghjk', 0.9, 0.78, True),
            (u'abc', u'acb', 0.75, 0.2, False),
            (u'Давыдова', u'Давыова', 8.0 / 9, 0.74, False),
        ]
        cmp = TrigramsAndDistanceComparator(distance_threshold=0.9, similarity_threshold=0.7)
        for i, (a, b, distance_factor, similarity_factor, status) in enumerate(eq_strings_distance_factors_statuses):
            result = cmp.compare(a, b)
            eq_(result.status, status, u'%d: %s != %s' % (i, a, b))
            assert_compound_factor_eq(
                [('distance', distance_factor), ('similarity', similarity_factor)],
                cmp.factor,
            )


class TestTransliteratedAndDistanceComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = TransliteratedAndDistanceComparator()

    def test_equal_strings(self):
        # сама транслитерация тестируется в test_xlit_compare.py
        eq_strings = [
            (u'', u''),
            (u'a', u'a'),
            (u'ab', u'ab'),
            (u'abc', u'abc'),
            (u'евгений', u'evgeniy'),
            (INVALID_UTF_CHAR, INVALID_UTF_CHAR),
        ]
        for i, (a, b) in enumerate(eq_strings):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            eq_(result.reasons, _get_reason(self.cmp.__class__, REASON_MATCH))
            assert_compound_factor_eq(
                [('distance', 1.0), ('xlit_used', 1)],
                self.cmp.factor,
            )

    def test_equal_suffix_strings(self):
        eq_strings_distance_factors = [
            (u'abc', u'ab', 0.75),
            (u'abc', u'acb', 0.75),
            (u'abc', u'abcd', 0.75),
            (u'abc', u'abc' + INVALID_UTF_CHAR, 1.0),  # INVALID_UTF_CHAR при базовой транслитерации отбрасывается
            (u'abcdef', u'abcdefgh', 0.75),
            (u'abcdef', u'bacedf', 0.75),
            (u'abcdefфывфыв', u'bacedfфывфыв', 12.0 / 14),
            (u'ктото пришел', u'кто-то пришол!', 13.0 / 16),
            (u'вася', u'vasiaa', 4.0 / 5),
            (u'вегений', u'evgeniy', 7.0 / 9),
            (u'евгений', u'evgenia', 6.0 / 7),
            (u'eugeniy', u'eugeni', 7.0 / 8),
            (u'ira', u'iray', 3.0 / 4),
            (u'ÇETİN', u'CETIN', 1.0),  # при транслитерации нормализованные символы с диакритическими знаками также преобразуются
        ]
        for i, (a, b, distance_factor) in enumerate(eq_strings_distance_factors):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            eq_(result.reasons, _get_reason(self.cmp.__class__, REASON_MATCH_SUFFIX))
            assert_compound_factor_eq(
                [('distance', distance_factor), ('xlit_used', 1)],
                self.cmp.factor,
            )

    def test_different_strings(self):
        diff_strings_distance_factors = [
            (u'a', u'', 0.5),
            (u'a', u'b', 0.5),
            (u'a', u'am', 0.5),
            (u'ab', u'ba', 2.0 / 3),
            (u'ab', u'abc', 2.0 / 3),
            (u'abc', u'abbbc', 0.6),
            (u'abcdeff', u'abcdefghl', 0.7),
            (u'rbcddf', u'bacedf', 6.0 / 9),
            (u'abcdefфывsфыв', u'bacedfфsывфывw', 13.0 / 18),
            (u'ктото пришел', u'кто-то пришол и!', 13.0 / 18),
            (u'вегений', u'eugeniy', 0.7),
        ]
        for i, (a, b, distance_factor) in enumerate(diff_strings_distance_factors):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            eq_(result.reasons, _get_reason(FuzzyComparatorBase, REASON_NO_MATCH))
            assert_compound_factor_eq(
                [('distance', distance_factor), ('xlit_used', 1)],
                self.cmp.factor,
            )


class TestTransliteratedTrigramsAndDistanceComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = TransliteratedTrigramsAndDistanceComparator()

    def test_equal_strings(self):
        # сама транслитерация тестируется в test_xlit_compare.py
        eq_strings = [
            (u'', u''),
            (u'a', u'a'),
            (u'ab', u'ab'),
            (u'abc', u'abc'),
            (u'евгений', u'evgeniy'),
            (INVALID_UTF_CHAR, INVALID_UTF_CHAR),
        ]
        for i, (a, b) in enumerate(eq_strings):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            eq_(result.reasons, _get_reason(self.cmp.__class__, REASON_MATCH))
            assert_compound_factor_eq(
                [('translit_similarity', -1), ('distance', 1.0), ('xlit_used', 1)],
                self.cmp.factor,
            )

    def test_equal_suffix_strings(self):
        eq_strings_distance_factors = [
            # (u'вегений', u'evgeniy', 7.0 / 9, 0.22),
            (u'abc', u'ab', 0.75, 0.44),
            (u'abc', u'abcd', 0.75, 0.55),
            (u'abc', u'abc' + INVALID_UTF_CHAR, 1.0, 1.0),  # INVALID_UTF_CHAR при базовой транслитерации отбрасывается
            (u'abcdef', u'abcdefgh', 0.75, 0.67),
            (u'abcdefфывфыв', u'bacedfфывфыв', 12.0 / 14, 0.5),
            (u'ктото пришел', u'кто-то пришол!', 13.0 / 16, 0.56),
            (u'вася', u'vasiaa', 4.0 / 5, 0.8),
            (u'евгений', u'evgenia', 6.0 / 7, 0.67),
            (u'eugeniy', u'eugeni', 7.0 / 8, 0.71),
            (u'ira', u'iray', 3.0 / 4, 0.55),
            (u'ÇETİN', u'CETIN', 1.0, 1.0),  # при транслитерации нормализованные символы с диакритическими знаками также преобразуются
        ]
        for i, (a, b, distance_factor, similarity) in enumerate(eq_strings_distance_factors):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            eq_(result.reasons, _get_reason(self.cmp.__class__, REASON_MATCH_SUFFIX))
            assert_compound_factor_eq(
                [('translit_similarity', similarity), ('distance', distance_factor), ('xlit_used', 1)],
                self.cmp.factor,
            )

    def test_different_strings(self):
        diff_strings_distance_factors = [
            (u'a', u'', 0.5, 0.0),
            (u'a', u'b', 0.5, 0.0),
            (u'a', u'am', 0.5, 0.29),
            (u'ab', u'ba', 2.0 / 3, 0.0),
            (u'ab', u'abc', 2.0 / 3, 0.44),
            (u'abc', u'abbbc', 0.6, 0.67),
            (u'abc', u'acb', 0.75, 0.2),
            (u'abcdef', u'bacedf', 0.75, 0.13),
            (u'abcdeff', u'abcdefghl', 0.7, 0.6),
            (u'rbcddf', u'bacedf', 6.0 / 9, 0.25),
            (u'abcdefфывsфыв', u'bacedfфsывфывw', 13.0 / 18, 0.06),
            (u'ктото пришел', u'кто-то пришол и!', 13.0 / 18, 0.53),
            (u'вегений', u'eugeniy', 0.7, 0.22),
        ]
        for i, (a, b, distance_factor, similarity) in enumerate(diff_strings_distance_factors):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            eq_(result.reasons, _get_reason(FuzzyComparatorBase, REASON_NO_MATCH))
            assert_compound_factor_eq(
                [('translit_similarity', similarity), ('distance', distance_factor), ('xlit_used', 1)],
                self.cmp.factor,
            )


class TestNFDFilterComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = NFDFilterComparator()

    def test_equal_strings(self):
        eq_strings_shrink_factors = [
            (u'a', u'a', 1.0),
            (u'a3b', u'a33 b', 0.4),
            (u'aaaaaaaaa-b', u'aaaaaaaa\va\b-?123b\r\n\f\a', 10.0 / 21),
            (u'\u212b', u'\u00c5', 1.0),
            (u'\u00c5', u'A\u030a', 0.5),
            (u'q\u0307\u0323werty', u'q\u0323\u0307werty', 6.0 / 8),
            (u'abc', u'abc͠', 3.0 / 4),
            (u'q\u0307\u0323werty', u'q\u0323\u0307\u0307werty', 6.0 / 9),
            (u'ÇAĞATAY', u'CAGATAY', 1.0),  # турецкое имя
            (u'ÇETİN', u'CETIN', 1.0),  # еще турецкое
            (u'ÅSA', u'ASA', 1.0),  # норвежское
            (u'ASLÖG', u'ASLOG', 1.0),  # шведское
            (u'*********Валерий', u'Валерий', 7.0 / 16),
            (u'*************Манахов -Гусев', u'Манахов -Гусев', 12.0 / 27),
            (u'a' * 4 + '5' * 6, u'a' * 4 + '5' * 6, 0.4),
        ]
        for i, (a, b, shrink_factor) in enumerate(eq_strings_shrink_factors):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            eq_(result.reasons, _get_reason(self.cmp.__class__, REASON_MATCH))
            assert_compound_factor_eq(
                [('aggressive_shrink', shrink_factor), ('aggressive_equal', 1)],
                self.cmp.factor,
            )

    def test_different_strings(self):
        diff_strings_shrink_factors = [
            (u'a', u'b', 1.0),
            (u'ab', u'ba', 1.0),
            (u'Vasiliy', u'vAsIliy', 1.0),  # регистр - в этом компараторе важен!
            (u'ab', u'a c', 2.0 / 3),
            (u'abc', u'abс\u0308', 3.0 / 4),  # в каких-то случаях акцент становится неотъемлемой частью буквы
            (u'qqqq\u0307\u0323', u'qqqq\u0323\u0307\u0307a', 5.0 / 8),
            (u'ÇAĞATAY', u'CAGATAYy', 1.0),
            (u'ASBJØRN', u'ASBJORN', 1.0),  # норвежская буква Ø
        ]
        for i, (a, b, shrink_factor) in enumerate(diff_strings_shrink_factors):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            eq_(result.reasons, _get_reason(FuzzyComparatorBase, REASON_NO_MATCH))
            assert_compound_factor_eq(
                [('aggressive_shrink', shrink_factor), ('aggressive_equal', 0)],
                self.cmp.factor,
            )

    def test_filtered_below_threshold_differs(self):
        # пустые и сводящиеся к пустым строки считаем различными
        diff_strings_shrink_factors = [
            (u'', u'', 0.0, 1),
            (u'3', u'3', 0.0, 1),
            (u'33a', u'33a', 1.0 / 3, 1),
            (u'a' * 39 + '5' * 61, u'33a', 1.0 / 3, 0),
            (u'33a', u'a' * 39 + '5' * 61, 1.0 / 3, 0),
            (u'a' * 39 + '5' * 61, u'a' * 39 + '5' * 61, 0.39, 1),
            (u'a', u'', 0.0, 0),
            (u'\u0308', u'\u0308', 0.0, 1),
        ]
        for i, (a, b, shrink_factor, equal_factor) in enumerate(diff_strings_shrink_factors):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            eq_(result.reasons, _get_reason(self.cmp.__class__, REASON_NO_MATCH_EMPTY_NORMALIZED))
            assert_compound_factor_eq(
                [('aggressive_shrink', shrink_factor), ('aggressive_equal', equal_factor)],
                self.cmp.factor,
            )


class TestFuzzyNameComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = FuzzyNameComparator()

    def test_equal_strings(self):
        for i, (a, b) in enumerate(KV_KO_DATA + KV_KO_DATA_NFD):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            ok_(result.reasons[0].startswith(tuple(b.__name__ for b in self.cmp.__class__.__bases__)))
            ok_(result.reasons[0].endswith((REASON_MATCH, REASON_MATCH_SUFFIX)))


class TestFuzzyStringComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = FuzzyStringComparator()

    def test_equal_strings(self):
        for i, (a, b) in enumerate(KV_KO_DATA):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            ok_(result.reasons[0].startswith(tuple(b.__name__ for b in self.cmp.__class__.__bases__)))
            ok_(result.reasons[0].endswith((REASON_MATCH, REASON_MATCH_SUFFIX)))


class TestFuzzyControlAnswersComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = FuzzyControlAnswersComparator()

    def test_equal_strings(self):
        for i, (a, b) in enumerate(KV_KO_DATA):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            ok_(result.reasons[0].startswith(tuple(b.__name__ for b in self.cmp.__class__.__bases__)))
            ok_(result.reasons[0].endswith((REASON_MATCH, REASON_MATCH_SUFFIX)))

    def test_different_strings(self):
        different_strings = [
            (u'Шульгина', u'Булыгина'),
        ]
        for i, (a, b) in enumerate(different_strings):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            eq_(result.reasons, _get_reason(FuzzyComparatorBase, REASON_NO_MATCH))


class TestFuzzyStrictComparator(unittest.TestCase):
    def setUp(self):
        self.cmp = FuzzyStrictComparator()

    def test_equal_strings(self):
        equal_strings = [
            ('1', '1'),
            ('79241353222', '79241353111'),
            ('abcd@gmail.ru', 'ABcd@gmail.com'),
        ]
        for i, (a, b) in enumerate(equal_strings):
            result = self.cmp.compare(a, b)
            ok_(result.status, u'%d: %s != %s' % (i, a, b))
            ok_(result.reasons[0].startswith(tuple(b.__name__ for b in self.cmp.__class__.__bases__)))
            ok_(result.reasons[0].endswith((REASON_MATCH, REASON_MATCH_SUFFIX)))

    def test_different_strings(self):
        different_strings = [
            ('1', '12'),
            (u'абцд@гмайл.ру', 'abcd@gmail.ru'),
            ('79241352222', '79241351111'),
        ]
        for i, (a, b) in enumerate(different_strings):
            result = self.cmp.compare(a, b)
            eq_(result.status, False, u'%d: %s == %s' % (i, a, b))
            eq_(result.reasons, _get_reason(FuzzyComparatorBase, REASON_NO_MATCH))


# Данные КВ/КО от саппортов - часть отброшена
KV_KO_DATA = (
    # (u'Стайл!', u'Style'),
    (u'мерилин', u'Marylin'),
    (u'нужная', u'nuznaya'),
    (u'орсилова', u'forsilowa'),
    (u'Савченко', u'cavhenko'),
    (u'Сеничева', u'cenecheva'),
    (u'1919', u'1919'),
    (u'<ALEX>', u'Алекс'),
    (u'<BYKOV>', u'Быков'),
    (u'CyBerr_BOT_1921344442A', u'CyBerr_BOT_19213442A'),
    (u'E3323THG', u'(e3323thg)'),
    (u'ivan', u'Иван'),
    (u'krokozyabra', u'крокозябра'),
    (u'kuznecova', u'Кузнецова'),
    (u'mansur', u'Мансур'),
    (u'n-95)', u'n95)'),
    (u'Reiden21', u'Reiden'),
    (u'sen86jlo', u'сен86джейло'),
    (u'stepanez', u'Степанец'),
    (u'Акимова', u'окимова'),
    (u'андреева', u'andreeva'),
    (u'Антощенко', u'antoshenko'),
    (u'анфиска', u'anfisa'),
    (u'Анчар', u'anthar'),
    (u'Аршавин', u'ARSHAVIN'),
    (u'Афанасенко', u'Afanasenko'),
    (u'Бабенко', u'babenko'),
    (u'Бадунова', u'Бодунова'),
    (u'борщ', u'борьщь'),
    (u'В блокноте', u'В блокноте .'),
    (u'Варфоломеева', u'varfolomeeva'),
    (u'Власенко', u'Vlasenko'),
    (u'Гайнц', u'Gaints'),
    (u'Годзилла', u'GodziLL@'),
    (u'Гусева', u'гусева'),
    (u'Дончак', u'donchac'),
    (u'Егорова', u'Egorova'),
    (u'ЕК732132', u'732132'),
    (u'ивонина', u'ivonina'),
    (u'Климкович', u'Klimkovich'),
    (u'Колосова', u'kolosowa'),
    (u'Конфета', u'конфеты'),
    (u'Кравчук', u'kravchuk'),
    (u'Курдюмова', u'Kudumova'),
    (u'лисина', u'lisina'),
    (u'лобина', u'lobina'),
    (u'Малыш', u'malysh'),
    (u'морозова', u'morozova'),
    (u'мюллер', u'мюлер'),
    (u'Новик', u'Novik'),
    (u'окрошка', u'крошка'),
    (u'Онучина', u'Onuchina'),
    (u'Отдых', u'отды'),
    (u'Пельмени', u'пельмени'),
    (u'Пермякова', u'permjacova'),
    (u'Позинская', u'Pozinskaya'),
    (u'Попова', u'popova'),
    (u'Пуся', u'PUSYA'),
    (u'пушка', u'Пушки'),
    (u'Реиден', u'Reiden'),
    (u'Родивилова', u'rodivlova'),
    (u'Саид', u'caid'),
    (u'Себастьян Перейра', u'Сибостьян Перейро'),
    (u'Снайпер', u'sniper'),
    (u'Султанова', u'syltanova'),
    (u'Тирамиссу', u'tiramisoo'),
    (u'Уракова', u'уракова7'),
    (u'Федор Кибальник', u'федор кибальник'),
    (u'Хакимуллина', u'hakimulina'),
    (u'Хамитова', u'xamitova'),
    (u'Ходор', u'xodor'),
    (u'Целовальникова', u'Целовальника'),
    (u'Шин', u'Shin'),
)

# Данные от саппортов, которые матчатся NFDFilterComparator
KV_KO_DATA_NFD = (
    (u'н.а.л.', u'н, а, л'),
    (u'Рыкунова', u'рык865унова'),
    (u'nthrekjd1985', u'nthrekjd'),
    (u'муравьева', u'Муравьева483968'),
    (u'др', u'др.'),
)
