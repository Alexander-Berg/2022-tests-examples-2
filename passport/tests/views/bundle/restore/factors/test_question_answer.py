# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    answer_factors,
    answer_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.views.bundle.restore.factors import RESTORE_METHODS_CHANGE_INDICES
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
    events_response,
)
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_NOT_SET,
    STRING_FACTOR_INEXACT_MATCH,
    STRING_FACTOR_MATCH,
    STRING_FACTOR_NO_MATCH,
)
from passport.backend.core.compare.test.compare import compare_uas_factor
from passport.backend.core.historydb.events import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


FACTORS_COUNT = len(RESTORE_METHODS_CHANGE_INDICES)


@with_settings_hosts()
class ControlAnswerHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(
        self,
        question_answer_set=True,
        question=TEST_DEFAULT_HINT_QUESTION_TEXT,
        question_id=99,
        answer=TEST_DEFAULT_HINT_ANSWER,
    ):
        question_answer = {}
        if question_answer_set:
            question_answer = {
                'question': question,
                'question_id': question_id,
                'answer': answer,
            }
        return {'question_answer': question_answer}

    def test_nothing_entered(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(),
        )
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response, self.form_values(question_answer_set=False)) as view:
            factors = view.calculate_factors('question_answer')

            expected_factors = answer_factors(
                answer_entered=None,
                answer_question=None,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(answer_statbox_entry(), view.statbox)

    def test_no_matches(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(),
        )
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('question_answer')

            eq_(factors, answer_factors())
            self.assert_entry_in_statbox(answer_statbox_entry(), view.statbox)

    def test_exact_match_with_not_current_answer(self):
        """Точное совпадение с КВ/КО - КВ текущий, КО не текущий"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=2, name=EVENT_INFO_HINTQ, value=u'1:qqq', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_INFO_HINTA, value=u'КО', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_INFO_HINTQ, value=u'99:my question', user_ip=TEST_IP),
                event_item(timestamp=4, name=EVENT_INFO_HINTA, value=u'ответ', user_ip=TEST_IP),
                event_item(timestamp=5, name=EVENT_INFO_HINTA, value=u'ответ', user_ip=TEST_IP),
                event_item(timestamp=6, name=EVENT_INFO_HINTA, value=u'answer', user_ip=TEST_IP),
            ]),
        )
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values(answer=u'ответ', question=u'my question', question_id=99)
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('question_answer')

            expected_factors = answer_factors(
                answer_question=u'99:my question',
                answer_entered=u'ответ',
                answer_index_best=(1, 1),
                answer_factor_best=STRING_FACTOR_MATCH,
                answer_factor_current=STRING_FACTOR_NO_MATCH,
                answer_factor_change_count=3,
                answer_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH] * FACTORS_COUNT,
                answer_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH] * FACTORS_COUNT,
                answer_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH] * FACTORS_COUNT,
                answer_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                answer_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                answer_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                answer_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                answer_history=[
                    {
                        'question': u'1:qqq',
                        'answers': [
                            {
                                'value': u'КО',
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                                        'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'question': u'99:my question',
                        'answers': [
                            {
                                'value': u'КО',
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                                        'end': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                                    },
                                ],
                            },
                            {
                                'value': u'ответ',
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                                        'end': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                                    },
                                ],
                            },
                            {
                                'value': u'answer',
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                                        'end': None,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                answer_statbox_entry(
                    answer_factor_best=STRING_FACTOR_MATCH,
                    answer_factor_current=STRING_FACTOR_NO_MATCH,
                    answer_factor_change_count=3,
                    answer_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH] * FACTORS_COUNT,
                    answer_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH] * FACTORS_COUNT,
                    answer_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH] * FACTORS_COUNT,
                    answer_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    answer_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    answer_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                    answer_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_inexact_match_with_current_question_answer(self):
        """Неточное совпадение с КВ/КО, являющимися текущими"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_USERINFO_FT, hintq=u'99:КВ', hinta=u'ответ', user_ip=TEST_IP),
                event_item(timestamp=20, name=EVENT_INFO_HINTQ, value=u'99:КВ', user_ip=TEST_IP_2),
                event_item(timestamp=20, name=EVENT_INFO_HINTA, value=u'КО', user_ip=TEST_IP_2),
                event_item(timestamp=30, name=EVENT_INFO_HINTA, value=u'ответ25', user_ip=TEST_IP_3),
                event_item(timestamp=40, name=EVENT_INFO_HINTA, value=u'ответ345', user_ip=TEST_IP),
            ]),
        )
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values(answer=u'ответ34', question=u'КВ', question_id=99)
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('question_answer')

            expected_factors = answer_factors(
                answer_question=u'99:КВ',
                answer_entered=u'ответ34',
                answer_index_best=(0, 3),
                answer_factor_best=STRING_FACTOR_INEXACT_MATCH,
                answer_factor_current=STRING_FACTOR_INEXACT_MATCH,
                answer_factor_change_count=3,
                answer_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                answer_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                answer_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH] * FACTORS_COUNT,
                answer_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                answer_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                answer_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                answer_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                answer_history=[
                    {
                        'question': u'99:КВ',
                        'answers': [
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                                    },
                                ],
                                'value': u'ответ',
                            },
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                                        'end': events_info_interval_point(user_ip=TEST_IP_3, timestamp=30),
                                    },
                                ],
                                'value': u'КО',
                            },
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP_3, timestamp=30),
                                        'end': events_info_interval_point(user_ip=TEST_IP, timestamp=40),
                                    },
                                ],
                                'value': u'ответ25',
                            },
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=40),
                                        'end': None,
                                    },
                                ],
                                'value': u'ответ345',
                            },
                        ],
                    },
                ],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                answer_statbox_entry(
                    answer_factor_best=STRING_FACTOR_INEXACT_MATCH,
                    answer_factor_current=STRING_FACTOR_INEXACT_MATCH,
                    answer_factor_change_count=3,
                    answer_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                    answer_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                    answer_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH] * FACTORS_COUNT,
                    answer_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    answer_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    answer_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                    answer_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_unknown_question(self):
        """Выбран неизвестный КВ"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=2, name=EVENT_INFO_HINTQ, value=u'1:qqq', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_INFO_HINTA, value=u'КО', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_INFO_HINTQ, value=u'99:my question', user_ip=TEST_IP),
                event_item(timestamp=4, name=EVENT_INFO_HINTA, value=u'ответ', user_ip=TEST_IP),
                event_item(timestamp=5, name=EVENT_INFO_HINTA, value=u'ответ', user_ip=TEST_IP),
                event_item(timestamp=6, name=EVENT_INFO_HINTA, value=u'answer', user_ip=TEST_IP),
            ]),
        )
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values(answer=u'ответ', question=u'no such question', question_id=99)
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('question_answer')

            expected_factors = answer_factors(
                answer_question=u'99:no such question',
                answer_entered=u'ответ',
                answer_history=[
                    {
                        'question': u'1:qqq',
                        'answers': [
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                                        'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                                    },
                                ],
                                'value': u'КО',
                            },
                        ],
                    },
                    {
                        'question': u'99:my question',
                        'answers': [
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                                        'end': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                                    },
                                ],
                                'value': u'КО',
                            },
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                                        'end': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                                    },
                                ],
                                'value': u'ответ',
                            },
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                                        'end': None,
                                    },
                                ],
                                'value': u'answer',
                            },
                        ],
                    },
                ],
                answer_factor_change_count=3,
                answer_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH] * FACTORS_COUNT,
                answer_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH] * FACTORS_COUNT,
                answer_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH] * FACTORS_COUNT,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                answer_statbox_entry(
                    answer_factor_best=FACTOR_NOT_SET,
                    answer_factor_change_count=3,
                    answer_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH] * FACTORS_COUNT,
                    answer_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH] * FACTORS_COUNT,
                    answer_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH] * FACTORS_COUNT,
                ),
                view.statbox,
            )

    def test_inexact_match_with_current_question_answer_with_multiple_intervals(self):
        """Неточное совпадение с КВ/КО, являющимися текущими, с несколькими интервалами актуальности"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_USERINFO_FT, hintq=u'99:КВ', hinta=u'ответ', user_ip=TEST_IP_2),
                event_item(timestamp=10, name=EVENT_INFO_HINTQ, value=u'99:КВ', user_ip=TEST_IP_3),
                event_item(timestamp=10, name=EVENT_INFO_HINTA, value=u'КО', user_ip=TEST_IP_3),
                event_item(timestamp=20, name=EVENT_INFO_HINTA, value=u'ответ', user_ip=TEST_IP_2),
                event_item(timestamp=30, name=EVENT_INFO_HINTA, value=u'КО', user_ip=TEST_IP_3),
                event_item(timestamp=40, name=EVENT_INFO_HINTA, value=u'ответ', user_ip=TEST_IP, yandexuid=TEST_YANDEXUID_COOKIE),
            ]),
        )
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values(answer=u'ответ34', question=u'КВ', question_id=99)
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('question_answer')

            expected_factors = answer_factors(
                answer_question=u'99:КВ',
                answer_entered=u'ответ34',
                answer_index_best=(0, 0),
                answer_factor_best=STRING_FACTOR_INEXACT_MATCH,
                answer_factor_current=STRING_FACTOR_INEXACT_MATCH,
                answer_factor_change_count=4,
                answer_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                answer_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                answer_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, compare_uas_factor('yandexuid')],
                answer_factor_match_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                answer_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                answer_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, compare_uas_factor('yandexuid')],
                answer_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                answer_history=[
                    {
                        'question': u'99:КВ',
                        'answers': [
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=1),
                                        'end': events_info_interval_point(user_ip=TEST_IP_3, timestamp=10),
                                    },
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                                        'end': events_info_interval_point(user_ip=TEST_IP_3, timestamp=30),
                                    },
                                    {
                                        'start': events_info_interval_point(
                                            user_ip=TEST_IP,
                                            timestamp=40,
                                            yandexuid=TEST_YANDEXUID_COOKIE,
                                        ),
                                        'end': None,
                                    },
                                ],
                                'value': u'ответ',
                            },
                            {
                                'intervals': [
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP_3, timestamp=10),
                                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                                    },
                                    {
                                        'start': events_info_interval_point(user_ip=TEST_IP_3, timestamp=30),
                                        'end': events_info_interval_point(
                                            user_ip=TEST_IP,
                                            timestamp=40,
                                            yandexuid=TEST_YANDEXUID_COOKIE,
                                        ),
                                    },
                                ],
                                'value': u'КО',
                            },
                        ],
                    },
                ],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                answer_statbox_entry(
                    answer_factor_best=STRING_FACTOR_INEXACT_MATCH,
                    answer_factor_current=STRING_FACTOR_INEXACT_MATCH,
                    answer_factor_change_count=4,
                    answer_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                    answer_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                    answer_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, compare_uas_factor('yandexuid')],
                    answer_factor_match_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                    answer_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    answer_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, compare_uas_factor('yandexuid')],
                    answer_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                ),
                view.statbox,
            )
