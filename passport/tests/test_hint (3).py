# -*- coding: utf-8 -*

import string

from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import (
    HintAnswer,
    HintQuestion,
    HintQuestionId,
    HintString,
)
import pytest


@pytest.mark.parametrize('valid_value', range(1, 12))
def test_hint_question_id(valid_value):
    check_equality(HintQuestionId(), (valid_value, int(valid_value)))


@pytest.mark.parametrize('invalid_value', ['', '-1', '0', '100', '255'])
def test_hint_question_id_invalid(invalid_value):
    check_raise_error(HintQuestionId(), invalid_value)


@pytest.mark.parametrize('valid_value', [
    'a',
    'My question',
    u'Тестовый вопрос',
    string.ascii_letters,
    string.digits,
    '  3 4  ',
    ])
def test_hint_string(valid_value):
    check_equality(HintString(), (valid_value, valid_value.strip()))


@pytest.mark.parametrize('invalid_value', [
    '',
    '-' * 101,
    'a' * 1000,
    '     ',
    ])
def test_hint_string_invalid(invalid_value):
    check_raise_error(HintString(), invalid_value)


@pytest.mark.parametrize('valid_value', [
    'a',
    'My question',
    u'Тестовый вопрос',
    string.ascii_letters[:37],
    string.digits,
    '  3 4  ',
    '-' * 37,
    ])
def test_hint_answer(valid_value):
    check_equality(HintQuestion(), (valid_value, valid_value.strip()))


@pytest.mark.parametrize('invalid_value', [
    '',
    '-' * 38,
    'a' * 1000,
    '     ',
    ])
def test_hint_answer_invalid(invalid_value):
    check_raise_error(HintQuestion(), invalid_value)


@pytest.mark.parametrize('valid_value', [
    'a',
    'My question',
    u'Тестовый вопрос',
    string.ascii_letters[:30],
    string.digits,
    '  3 4  ',
    '-' * 30,
    ])
def test_hint_question(valid_value):
    check_equality(HintAnswer(), (valid_value, valid_value.strip()))


@pytest.mark.parametrize('invalid_value', [
    '',
    '-' * 31,
    'a' * 1000,
    '     ',
    ])
def test_hint_question_invalid(invalid_value):
    check_raise_error(HintAnswer(), invalid_value)


@pytest.mark.parametrize('value', [
    0,
    {1: 2},
    ['value'],
    object(),
    ])
@pytest.mark.parametrize('validator', [HintString, HintQuestion, HintAnswer])
def test_hints_with_strict_option(value, validator):
    check_raise_error(validator(strict=True), value)
