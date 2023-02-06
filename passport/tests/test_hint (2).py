# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.core.db.faker.db import attribute_table_insert_on_duplicate_update_key as at_insert_odk
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import attributes_table as at
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import Account
from passport.backend.core.models.hint import Hint
from passport.backend.core.serializers.eav.hint import (
    hint_question_processor,
    HintEavSerializer,
)
from passport.backend.core.types.question import Question
from sqlalchemy import and_


class TestCreateHint(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        hint = Hint(acc)

        queries = HintEavSerializer().serialize(None, hint, diff(None, hint))
        eq_eav_queries(queries, [])

    def test_question(self):
        acc = Account(uid=123)
        hint = Hint(acc, question=Question(u'вопрос?', 2))

        queries = HintEavSerializer().serialize(None, hint, diff(None, hint))
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['hint.question.serialized'], 'value': b'2:%s' % u'вопрос?'.encode('utf-8')},
                ]),
            ],
        )

    def test_question_and_answer(self):
        acc = Account(uid=123)
        hint = Hint(acc, answer=u'ответ', question=Question('text', 2))

        queries = HintEavSerializer().serialize(None, hint, diff(None, hint))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['hint.question.serialized'], 'value': b'2:text'},
                    {'uid': 123, 'type': AT['hint.answer.encrypted'], 'value': u'ответ'.encode('utf-8')},
                ]),
            ],
        )


class TestChangeHint(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        hint = Hint(acc, answer='abc', question=Question('text', 5))

        s1 = hint.snapshot()
        queries = HintEavSerializer().serialize(s1, hint, diff(s1, hint))

        eq_eav_queries(queries, [])

    def test_answer(self):
        acc = Account(uid=123)
        hint = Hint(acc, answer='abc', question=Question('text', 5))

        s1 = hint.snapshot()
        hint.answer = 'new'
        queries = HintEavSerializer().serialize(s1, hint, diff(s1, hint))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['hint.answer.encrypted'], 'value': b'new'},
                ]),
            ],
        )

    def test_question_and_answer(self):
        acc = Account(uid=123)
        hint = Hint(acc, answer='abc', question=Question('text', 5))

        s1 = hint.snapshot()
        hint.answer = 'new'
        hint.question = Question('newtext', 4)
        queries = HintEavSerializer().serialize(s1, hint, diff(s1, hint))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['hint.question.serialized'], 'value': b'4:newtext'},
                    {'uid': 123, 'type': AT['hint.answer.encrypted'], 'value': b'new'},
                ]),
            ],
        )


class TestDeleteHint(unittest.TestCase):
    def test_ok(self):
        acc = Account(uid=123)
        hint = Hint(acc, answer='abc', question=Question('text', 5))

        s1 = hint.snapshot()
        queries = HintEavSerializer().serialize(s1, None, diff(s1, None))

        eq_eav_queries(queries, [
            at.delete().where(
                and_(
                    at.c.uid == 123,
                    at.c.type.in_(sorted([
                        AT['hint.answer.encrypted'],
                        AT['hint.question.serialized'],
                    ])),
                ),
            ),
        ])


class TestQuestionProcessors(unittest.TestCase):
    def test_question(self):
        eq_(hint_question_processor(None), None)
        eq_(hint_question_processor(''), None)
        eq_(hint_question_processor(Question(u'вопрос', 5)), '5:%s' % 'вопрос')
