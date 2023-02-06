# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.models.account import Account
from passport.backend.core.models.hint import Hint
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.types.question import Question
from passport.backend.core.undefined import Undefined


class _TranslationSettings(object):
    QUESTIONS = {'en': {'0': 'Not selected'}}


@with_settings(translations=_TranslationSettings)
class TestHint(unittest.TestCase):

    def test_hint_parse(self):
        hint = Hint().parse({'userinfo_safe.hintq.uid': '1:text', 'userinfo_safe.hinta.uid': 'answer'})
        eq_(hint.answer, 'answer')
        eq_(hint.question.id, 1)
        eq_(hint.question.text, 'text')
        ok_(hint.is_set)

    def test_hint_parse_empty_fields(self):
        hint = Hint().parse({'userinfo_safe.hintq.uid': '', 'userinfo_safe.hinta.uid': ''})
        eq_(hint.answer, '')
        eq_(hint.question, Undefined)
        ok_(not hint.is_set)

    def test_hint_parse_null_fields(self):
        hint = Hint().parse({'userinfo_safe.hintq.uid': None, 'userinfo_safe.hinta.uid': None})
        eq_(hint.answer, None)
        eq_(hint.question, Undefined)
        ok_(not hint.is_set)

    def test_hint_parse_only_question(self):
        hint = Hint().parse({'userinfo_safe.hintq.uid': '1:text', 'userinfo_safe.hinta.uid': None})
        eq_(hint.answer, None)
        eq_(hint.question.id, 1)
        eq_(hint.question.text, 'text')
        ok_(not hint.is_set)

    def test_hint_parse_only_answer(self):
        hint = Hint().parse({'userinfo_safe.hintq.uid': None, 'userinfo_safe.hinta.uid': 'answer'})
        eq_(hint.answer, 'answer')
        eq_(hint.question, Undefined)
        ok_(not hint.is_set)

    def test_hint_parse_from_question_object(self):
        hint = Hint().parse({'userinfo_safe.hintq.uid': Question('text'), 'userinfo_safe.hinta.uid': 'answer'})
        eq_(hint.answer, 'answer')
        eq_(hint.question.id, 99)
        eq_(hint.question.text, 'text')
        ok_(hint.is_set)

    def test_hint_parse_requires_language(self):
        hint = Hint().parse({'userinfo_safe.hintq.uid': '0:', 'userinfo_safe.hinta.uid': 'answer',
                             'person.language': 'en'})
        eq_(hint.answer, 'answer')
        eq_(hint.question.id, 0)
        eq_(hint.question.text, 'Not selected')
        ok_(hint.is_set)

    def test_hint_without_language_when_language_is_required(self):
        hint = Hint().parse({'userinfo_safe.hintq.uid': '0:', 'userinfo_safe.hinta.uid': 'answer'})
        eq_(hint.answer, 'answer')
        eq_(hint.question, Undefined)
        ok_(not hint.is_set)

    def test_hint_custom_question_and_empty(self):
        hint = Hint().parse({'userinfo_safe.hintq.uid': '99:', 'userinfo_safe.hinta.uid': 'answer'})
        eq_(hint.answer, 'answer')
        eq_(hint.question, Question('', question_id=99))
        ok_(hint.is_set)

    def test_account_with_hint_parse(self):
        acc = Account(uid=10).parse({'userinfo_safe.hintq.uid': '0:text', 'userinfo_safe.hinta.uid': 'answer'})
        eq_(acc.hint.question.text, 'text')
        eq_(acc.hint.question.id, 0)
        eq_(acc.hint.answer, 'answer')
        ok_(acc.hint.is_set)
