from hamcrest import (
    assert_that,
    calling,
    raises,
)
from nose.tools import ok_
from passport.backend.core.test.form.deep_eq_matcher import deep_eq
import pytest


def test_should_match_on_equals():
    obj = {'key': 'val'}
    ok_(deep_eq(obj).matches(obj))


def test_should_not_match_on_diff():
    obj = {'key': 'val'}
    obj2 = {'key': 'val2'}
    ok_(not deep_eq(obj).matches(obj2))


@pytest.mark.parametrize(
    ('one', 'another', 'pattern'),
    [
        ({}, {'1': '2'}, 'transformations'),
        ([2], [1], 'transformations'),
        (1, 2, 'should be'),
        (set([1]), set([2]), 'In first'),
        (None, 1, 'was <None>'),
        ({}, 1, 'was <'),
        ([], {}, 'was <'),
    ],
)
def test_should_not_match(one, another, pattern):
    assert_that(calling(assert_that).with_args(one, deep_eq(another)), raises(AssertionError, pattern))
