# -*- coding: utf-8 -*-
import string

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.conf import settings
from passport.backend.core.password.password_quality import (
    PasswordQualifier,
    STANDARD_SEQUENCES,
)
from passport.backend.core.test.test_utils import with_settings


def test_prepare_sequences():
    sequences = [
        {'chars': 'abcdef', 'min_length': 2, 'max_length': 4},
    ]

    pq = PasswordQualifier(sequences, [])

    expected_sequences = [
        ['a', 'b', 'c', 'd'],
        ['b', 'c', 'd', 'e'],
        ['f', 'a', 'b', 'c'],
        ['d', 'e', 'f'],
        ['f', 'a', 'b'],
        ['e', 'f'],
        ['f', 'a']
    ]
    not_expected_sequences = [
        [''], ['a'], ['b'], ['f'],
        ['abcd'], ['abcdef'],
        ['a', 'b', 'c', 'd', 'e'],
        ['a', 'b', 'c', 'd', 'e', 'f'],
    ]

    actual_sequences = pq.sequences

    for expected_sequence in expected_sequences:
        ok_(expected_sequence in actual_sequences, [expected_sequence, actual_sequences])

    for expected_sequence in not_expected_sequences:
        ok_(expected_sequence not in actual_sequences, [expected_sequence, actual_sequences])


def check_sequences(pq, params):
    str = params[0]
    sequences_iter = list(pq._find_sequences(str))
    for sequence in sequences_iter:
        ok_(sequence in params[1], [params[1], sequences_iter])


def test_find_sequences():
    sequences = [
        {'chars': 'abcdef', 'min_length': 2, 'max_length': 4},
        {'chars': string.digits, 'min_length': 3, 'max_length': 10},
        {'chars': reversed(string.digits), 'min_length': 3, 'max_length': 10},
    ]

    pq = PasswordQualifier(sequences, [])

    params = [
        ('baobab', [(4, 6, 'ab')]),
        ('beef', [(2, 4, 'ef')]),
        ('cool123456', [(4, 10, '123456')]),
        ('abc098765432', [(0, 3, 'abc'), (3, 12, '098765432')]),
    ]

    for param in params:
        yield check_sequences, pq, param


def check_quality(pq, password, result):
    actual_result = pq.get_quality(password, [], [])
    for k, v in result.items():
        eq_(actual_result[k], v, [actual_result[k], v, actual_result.get('quality'), password, k])


@with_settings
def test_get_quality():
    pq = PasswordQualifier(STANDARD_SEQUENCES, settings.PASSWORD_BLACKLIST)

    params = [
        ['aaa', {'grade': 1, 'quality': 1}],
        ['aaa1', {'grade': 1, 'quality': 5}],
        ['aaabbb', {'grade': 1, 'quality': 4}],
        ['aaa1bbb', {'grade': 2, 'quality': 21}],
        ['aaabbbccc', {'grade': 1, 'quality': 18}],
        ['aaabbbccc1', {'grade': 4, 'quality': 70}],
        ['aaa1bbbccc', {'grade': 5, 'quality': 80}],
        ['aaaabbbbcccc', {'grade': 2, 'quality': 24}],
        ['aaaa1bbbb.cccc', {'grade': 6, 'quality': 100}],
        ['foobar', {'grade': 1, 'quality': 15}],
        ['foobar123', {'grade': 3, 'quality': 49}],
        ['fooBar123', {'grade': 4, 'quality': 63}],
        ['foo.bar213', {'grade': 6, 'quality': 100}],
        ['foobar!11', {'grade': 6, 'quality': 100}],
        ['foo?bar11!', {'grade': 6, 'quality': 100}],
        ['jgjhgjk', {'grade': 1, 'quality': 14}],
        ['qktysb', {'grade': 1, 'quality': 18}],
        ['qktysbpa', {'grade': 4, 'quality': 64}],
        ['allyouneedislov', {'grade': 6, 'quality': 100}],
        ['allyouneedislove', {'grade': 6, 'quality': 100}],
        ['redfoxjustjumped', {'grade': 6, 'quality': 100}],
        ['redfoxjustjumpedoverahence', {'grade': 6, 'quality': 100}],
        ['$flv^onWQ', {'grade': 6, 'quality': 100}],
        ['Kolokol123', {'grade': 4, 'quality': 60}],
        ['vasya75', {'grade': 3, 'quality': 56}],
        ['vasya.pupkin1976', {'grade': 6, 'quality': 100}],
        ['abcabcabc', {'grade': 1, 'quality': 12}],
        ['abcabcab', {'grade': 1, 'quality': 8}],
        ['qwerty', {'grade': 1, 'quality': 0}],
        ['qwertyuiop', {'grade': 1, 'quality': 0}],
        ['qweqwe', {'grade': 1, 'quality': 4}],
        ['qweqweqwe', {'grade': 1, 'quality': 12}],
        ['qweqweqweqwe', {'grade': 1, 'quality': 16}],
        ['q1w2e3', {'grade': 1, 'quality': 0}],
        ['q1w2e3r4', {'grade': 1, 'quality': 0}],
        ['q1w2e3r4t5', {'grade': 1, 'quality': 1}],
        ['q1w2e3R4', {'grade': 3, 'quality': 52}],
        ['Q1w2e3r4T5', {'grade': 5, 'quality': 80}],
        ['qw1er2rt3', {'grade': 6, 'quality': 100}],
        ['qw1er2ty3ui4', {'grade': 6, 'quality': 100}],
        ['qA1wS2eD3', {'grade': 6, 'quality': 100}],
        ['fghjjhgf', {'grade': 1, 'quality': 16}],
    ]

    for password, result in params:
        yield check_quality, pq, password, result


@with_settings
def test_words_and_subwords():
    pq = PasswordQualifier(STANDARD_SEQUENCES, settings.PASSWORD_BLACKLIST)

    result = pq.get_quality('aaa1bbbccc', [], [])
    eq_(result['quality'], 80)

    result = pq.get_quality('aaa1bbbccc', ['  '], ['  '])
    eq_(result['quality'], 80)
    ok_(not result['is_additional_word'])
    ok_(not result['additional_subwords'])
    eq_(result['additional_subwords_number'], 0)

    result = pq.get_quality('aaa1bbbccc', ['  aaa1bbbccc  '], ['  a1b  '])
    ok_(result['is_additional_word'])
    ok_('a1b' in result['additional_subwords'])
    eq_(result['additional_subwords_number'], 1)
