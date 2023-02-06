# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.account.questions import forms
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestQuestionsForms(unittest.TestCase):
    def test_questionsaddoptional_form(self):
        valid_params = [
            (
                {
                    'uid': '123',
                    'question1': 'q1',
                    'question2': 'q2',
                    'question3': 'q3',
                    'answer1': 'a1',
                    'answer2': 'a2',
                    'answer3': 'a3',
                },
                {
                    'uid': 123,
                    'question1': 'q1',
                    'question2': 'q2',
                    'question3': 'q3',
                    'answer1': 'a1',
                    'answer2': 'a2',
                    'answer3': 'a3',
                },
            ),
        ]

        invalid_params = [
            (
                {},
                [
                    'answer1.empty', 'answer2.empty', 'answer3.empty',
                    'question1.empty', 'question2.empty', 'question3.empty',
                ],
            ),
            (
                {
                    'uid': '',
                    'question1': '',
                    'question2': '',
                    'question3': '',
                    'answer1': '',
                    'answer2': '',
                    'answer3': '',
                },
                [
                    'answer1.empty', 'answer2.empty', 'answer3.empty',
                    'question1.empty', 'question2.empty', 'question3.empty',
                    'uid.empty',
                ],
            ),
            (
                {
                    'uid': '123',
                    'question1': 'a' * 1024,
                    'question2': 'a' * 1024,
                    'question3': 'a' * 1024,
                    'answer1': 'a' * 1024,
                    'answer2': 'a' * 1024,
                    'answer3': 'a' * 1024,
                },
                [
                    'answer1.long', 'answer2.long', 'answer3.long',
                    'question1.long', 'question2.long', 'question3.long',
                ],
            ),
        ]

        check_form(forms.QuestionsAddOptionalForm(), invalid_params, valid_params, None)

    def test_get_question_form(self):
        valid_params = [
            (
                {
                    'uid': 1234,
                },
                {
                    'uid': 1234,
                    'is_pdd': False,
                },
            ),
            (
                {
                    'is_pdd': 'no',
                },
                {
                    'uid': None,
                    'is_pdd': False,
                },
            ),
        ]

        invalid_params = [
            (
                {
                    'uid': '',
                },
                ['uid.empty'],
            ),
        ]

        check_form(forms.QuestionsGetQuestionForm(), invalid_params, valid_params, None)

    def test_check_answer_form(self):
        valid_params = [
            (
                {
                    'answer': 'answer',
                },
                {
                    'answer': 'answer',
                },
            ),
        ]

        invalid_params = [
            (
                {
                    'answer': '',
                },
                ['answer.empty'],
            ),
            (
                {
                    'answer': 'a' * 1025,
                },
                ['answer.long'],
            ),
        ]

        check_form(forms.QuestionsCheckAnswerForm(), invalid_params, valid_params, None)

    def test_check_answer_history_form(self):
        valid_params = [
            (
                {
                    'answer': 'answer',
                    'question_id': '1',
                    'question': 'q1',
                },
                {
                    'answer': 'answer',
                    'question_id': 1,
                    'question': 'q1',
                },
            ),
        ]

        invalid_params = [
            (
                {},
                [
                    'answer.empty',
                    'question.empty',
                    'question_id.empty',
                ],
            ),
            (
                {
                    'answer': '',
                },
                [
                    'answer.empty',
                    'question.empty',
                    'question_id.empty',
                ],
            ),
            (
                {
                    'answer': 'a' * 1025,
                },
                [
                    'answer.long',
                    'question.empty',
                    'question_id.empty',
                ],
            ),
            (
                {
                    'question': 'a' * 1025,
                },
                [
                    'answer.empty',
                    'question.long',
                    'question_id.empty',
                ],
            ),
            (
                {
                    'question_id': 'a',
                },
                [
                    'answer.empty',
                    'question.empty',
                    'question_id.invalid',
                ],
            ),
        ]

        check_form(forms.CheckQuestionAnswerHistoryForm(), invalid_params, valid_params, None)

    def test_set_question_form(self):
        valid_params = [
            (
                {
                    'uid': 1,
                    'answer': 'answer',
                    'display_language': 'ru',
                    'question_id': '1',
                },
                {
                    'uid': 1,
                    'answer': 'answer',
                    'question': None,
                    'question_id': 1,
                    'display_language': 'ru',
                },
            ),
            (
                {
                    'uid': 1,
                    'answer': 'answer',
                    'question': 'Hello',
                },
                {
                    'uid': 1,
                    'answer': 'answer',
                    'question': 'Hello',
                    'question_id': None,
                    'display_language': None,
                },
            ),
            (
                {
                    'uid': 1,
                    'question': 'Hello',
                },
                {
                    'uid': 1,
                    'answer': None,
                    'question': 'Hello',
                    'question_id': None,
                    'display_language': None,
                },
            ),
            (
                {
                    'uid': 1,
                    'answer': 'Hello',
                },
                {
                    'uid': 1,
                    'answer': 'Hello',
                    'question': None,
                    'question_id': None,
                    'display_language': None,
                },
            ),
            (
                {
                    'uid': 1,
                    'question_id': '1',
                    'display_language': 'ru',
                },
                {
                    'uid': 1,
                    'answer': None,
                    'question': None,
                    'question_id': 1,
                    'display_language': 'ru',
                },
            ),
            (
                {
                    'question_id': '1',
                    'question': '?',
                    'display_language': 'ru',
                },
                {
                    'uid': None,
                    'answer': None,
                    'question': '?',
                    'question_id': 1,
                    'display_language': 'ru',
                },
            ),
        ]

        invalid_params = [
            (
                {},
                [
                    'question_or_answer.invalid',
                ],
            ),
            (
                {
                    'uid': 1,
                    'answer': '',
                },
                [
                    'answer.empty',
                ],
            ),
            (
                {
                    'uid': 1,
                    'answer': 'a' * 1025,
                },
                [
                    'answer.long',
                ],
            ),
            (
                {
                    'question': 'a' * 1025,
                },
                [
                    'question.long',
                ],
            ),
            (
                {
                    'uid': 1,
                    'question_id': 'a',
                },
                [
                    'question_id.invalid',
                ],
            ),
            (
                {
                    'uid': 1,
                    'question_id': '1',
                },
                [
                    'display_language.empty',
                ],
            ),
            (
                {
                    'question': 'WAT?',
                    'question_id': '1',
                    'answer': '--',
                    'display_language': 'en',
                },
                [
                    'question_or_answer.invalid',
                ],
            ),
        ]
        check_form(forms.QuestionsSetQuestionForm(), invalid_params, valid_params, None)

    def test_change_question_form(self):
        valid_params = [
            (
                {
                    'answer': 'old ',
                    'question_id': '1 ',
                    'display_language': 'ru',
                    'new_answer': 'new',
                },
                {
                    'answer': 'old',
                    'question_id': 1,
                    'display_language': 'ru',
                    'new_answer': 'new',
                    'question': None,
                },
            ),
            (
                {
                    'current_password': 'abc',
                    'question': 'Where is my mind?',
                    'new_answer': 'Way out',
                },
                {
                    'answer': None,
                    'question_id': None,
                    'display_language': None,
                    'new_answer': 'Way out',
                    'question': 'Where is my mind?',
                },
            ),
            (
                {
                    'answer': 'a' * 1024,
                    'question': 'question',
                    'display_language': 'ru',
                    'new_answer': 'answer',
                },
                {
                    'answer': 'a' * 1024,
                    'question': 'question',
                    'display_language': 'ru',
                    'new_answer': 'answer',
                    'question_id': None,
                },
            ),
        ]

        invalid_params = [
            (
                {
                    'answer': 'q' * 1025,
                    'question_id': 30,
                    'display_language': 'ru',
                    'new_answer': 'b',
                },
                [
                    'question_id.invalid',
                    'answer.long',
                ],
            ),
            (
                {
                    'answer': 'abs',
                    'question': 'question',
                    'new_answer': 'a' * 31,
                },
                [
                    'new_answer.long',
                ],
            ),
            (
                {
                    'answer': '',
                    'question': 'question',
                    'new_answer': 'answer',
                },
                [
                    'answer.empty',
                ],
            ),
            (
                {
                    'answer': 'old',
                    'current_password': 'abc',
                    'question_id': 1,
                    'new_answer': 'answer',
                },
                [
                    'form.invalid',
                ],
            ),
            (
                {
                    'answer': 'answer',
                    'current_password': 'abc',
                    'display_language': 'ru',
                    'new_answer': 'answer',
                    'question_id': 1,
                    'question': 'question',
                },
                [
                    'form.invalid',
                ],
            ),
        ]
        check_form(forms.QuestionsChangeForm(), invalid_params, valid_params, None)
