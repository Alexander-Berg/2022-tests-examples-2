from hamcrest import (
    anything,
    assert_that,
    calling,
    is_not,
    raises,
)
import mock
from nose.tools import ok_
from passport.backend.core.test.form.common_matchers import raises_invalid
from passport.backend.core.test.form.submitted_form_matcher import submitted_with


def test_can_match():
    ok_(submitted_with({}, anything()).matches(mock.Mock()))


def test_can_not_match():
    ok_(not submitted_with({}, is_not(anything())).matches(mock.Mock()))


def test_should_not_match():
    assert_that(
        calling(assert_that).with_args(mock.Mock(), submitted_with({}, is_not(anything()))),
        raises(AssertionError, 'form submitted'),
    )


def test_should_use_raise_callable():
    assert_that(
        calling(assert_that).with_args(mock.Mock(), submitted_with({}, raises_invalid())),
        raises(AssertionError),
    )
