# -*- coding: utf-8 -*-

from nose.tools import (
    assert_raises,
    assert_raises_regexp,
    eq_,
)
from passport.backend.core.test.test_utils import iterdiff


def test_dict_iterdiff1():
    with assert_raises(AssertionError):
        iterdiff(eq_)({'a': 1}, {'a': 2})


def test_dict_iterdiff2():
    try:
        iterdiff(eq_)({'a': 1}, {'a': 2})
    except AssertionError as e:
        eq_(
            e.args[0],
            "sequences not equal\n"
            "Do the transformations in order to get first from second:\n"
            "- ('a', 2)\n"
            "+ ('a', 1)\n"
        )


def test_list_iterdiff():
    with assert_raises_regexp(
        AssertionError,
        r'sequences not equal\n'
        r'Do the transformations in order to get first from second:\n'
        r'\- 1\n'
        r'\  2\n'
        r'\- 3\n'
        r'\+ 5\n'
        r'\+ 4\n',
    ):
        iterdiff(eq_)([2, 5, 4], [1, 2, 3])


def test_set_iterdiff():
    with assert_raises(AssertionError):
        iterdiff(eq_)(set([1, 2]), set([3, 4]))


def test_not_iterable_iterdiff():
    with assert_raises(AssertionError):
        iterdiff(eq_)(1, 2)


def test_iterdiff4():
    iterdiff(eq_)({'a': 1}, {'a': 1})
    iterdiff(eq_)({}, {})
    iterdiff(eq_)('a', 'a')
    iterdiff(eq_)(1, 1)
    iterdiff(eq_)(['a', 1], ['a', 1])
