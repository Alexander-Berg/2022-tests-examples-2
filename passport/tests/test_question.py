# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.types.question import Question
from passport.backend.core.undefined import Undefined
import six


class _TranslationSettings(object):
    QUESTIONS = {'en': {'0': 'Not selected'}}


@with_settings(translations=_TranslationSettings)
class TestQuestion(unittest.TestCase):
    def test_init(self):
        question = Question('question text', 1)
        eq_(question.text, 'question text')
        eq_(question.id, 1)
        eq_(question.language, None)

    def test_init_default_id(self):
        question = Question('question text')
        eq_(question.text, 'question text')
        eq_(question.id, 99)
        eq_(question.language, None)

    def test_serialization(self):
        question = Question('question text')
        eq_(six.text_type(question), u'99:question text')

    def test_from_id(self):
        question = Question.from_id('en', 0)
        eq_(question.id, 0)
        eq_(question.text, 'Not selected')
        eq_(question.language, 'en')

    def test_from_none_language__undefined(self):
        question = Question.from_id(None, 0)
        eq_(question, Undefined)

    def test_from_wrong_id__undefined(self):
        question = Question.from_id('en', 100500)
        eq_(question, Undefined)

    def test_parse_full(self):
        question = Question.parse('1:question text')
        eq_(question.text, 'question text')
        eq_(question.id, 1)
        eq_(question.language, None)

    def test_parse_no_id(self):
        question = Question.parse('question text')
        eq_(question.text, 'question text')
        eq_(question.id, 99)
        eq_(question.language, None)

    def test_parse_no_text(self):
        question = Question.parse('0:', 'en')
        eq_(question.text, 'Not selected')
        eq_(question.id, 0)
        eq_(question.language, 'en')

    def test_parse_text_with_semicolon(self):
        question = Question.parse('1:ques:tion te:xt')
        eq_(question.text, 'ques:tion te:xt')
        eq_(question.id, 1)
        eq_(question.language, None)

    def test_parse_text_with_semicolon_no_id(self):
        question = Question.parse(':ques:tion te:xt')
        eq_(question.text, ':ques:tion te:xt')
        eq_(question.id, 99)
        eq_(question.language, None)

    def test_is_empty_custom(self):
        question = Question.parse('')
        eq_(question.is_empty, True)

    def test_is_unknown(self):
        question = Question.parse('0:Not selected')
        eq_(question.is_empty, True)

    def test_repr(self):
        question = Question.parse(':ques:tion te:xt')
        ok_(repr(question))

    def test_eq_ne(self):
        question1 = Question.parse('ques:tion te:xt')
        question2 = Question.parse('ques:tion te:xt')

        ok_(question1 == question2)
        ok_(question1 == u'99:ques:tion te:xt')
        ok_(not question1 == u'test')
        ok_(not question1 != question2)

    def test_unicode_or_str(self):
        question = Question.parse(u'Текст')
        if six.PY2:
            assert type(six.text_type(question)).__name__ == 'unicode'
            assert type(six.binary_type(question)) is str
        assert six.text_type(question) == u'99:Текст'
        assert str(question) == '99:Текст'
