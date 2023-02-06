# -*- coding: utf-8 -*-

from collections import OrderedDict

from nose.tools import eq_
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
)
from passport.backend.core.historydb.analyzer.event_handlers.question_answer import (
    flatten_question_answer_mapping,
    serialize_question_answer_mapping,
)
from passport.backend.core.historydb.events import (
    EVENT_ACTION,
    EVENT_INFO_HINTA,
    EVENT_INFO_HINTQ,
    EVENT_USER_AGENT,
    EVENT_USERINFO_FT,
)
from passport.backend.core.test.test_utils import with_settings_hosts

from ..data import (
    TEST_HINTQ_HINTA_TS_OFFSET,
    TEST_IP,
    TEST_IP_2,
    TEST_USER_AGENT,
    TEST_YANDEXUID,
    TranslationSettings,
)
from ..test_events import BaseEventsAnalyzerTestCase


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class QuestionAnswerAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_qa_mapping_basic_userinfo_ft_event(self):
        response = [
            event_item(name=EVENT_USERINFO_FT, timestamp=1, hintq='99:q', hinta='answer', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        mapping = OrderedDict([
            (
                '99:q',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=1),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
            questions=['99:q'],
            answers=['answer'],
        )
        eq_(
            flatten_question_answer_mapping(serialize_question_answer_mapping(mapping)),
            [
                {
                    'question': u'99:q',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(timestamp=1),
                        'end': None,
                    },
                },
            ],
        )

    def test_qa_mapping_missing_origin_info(self):
        response = [
            event_item(name=EVENT_USERINFO_FT, timestamp=1, hintq='99:q', hinta='answer', user_ip=None, yandexuid=None),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        mapping = OrderedDict([
            (
                '99:q',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=None, yandexuid=None),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
            questions=['99:q'],
            answers=['answer'],
        )
        eq_(
            flatten_question_answer_mapping(serialize_question_answer_mapping(mapping)),
            [
                {
                    'question': u'99:q',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(user_ip=None, yandexuid=None),
                        'end': None,
                    },
                },
            ],
        )

    def test_qa_mapping_userinfo_ft_event_hintq_not_specified_no_hinta(self):
        response = [
            event_item(name=EVENT_USERINFO_FT, timestamp=1, hintq='0:not specified', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            question_answer_mapping=OrderedDict(),
            questions=['0:not specified'],
            answers=[],
        )

    def test_qa_mapping_userinfo_ft_event_hintq_without_text(self):
        """
        Перл не пишет текст КВ, только "id:". Проверим, что не ломаемся,
        если передали язык.
        """
        response = [
            event_item(name=EVENT_USERINFO_FT, timestamp=1, hintq='11:', hinta='answer', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, language='en', events=response)
        mapping = OrderedDict([
            (
                '11:Your favourite teacher',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=1),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
        )
        eq_(
            flatten_question_answer_mapping(serialize_question_answer_mapping(mapping)),
            [
                {
                    'question': u'11:Your favourite teacher',
                    'answer': 'answer',
                    'interval': {'start': events_info_interval_point(timestamp=1), 'end': None},
                },
            ],
        )

    def test_qa_mapping_basic_info_events_two(self):
        response = [
            event_item(name=EVENT_INFO_HINTQ, timestamp=1, value='99:q', user_ip=TEST_IP),
            event_item(name=EVENT_USER_AGENT, timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET, value=TEST_USER_AGENT),
            event_item(name=EVENT_INFO_HINTA, timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET, value='answer', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTQ, timestamp=2, value='99:q', user_ip=TEST_IP_2),
            event_item(name=EVENT_INFO_HINTA, timestamp=2 + TEST_HINTQ_HINTA_TS_OFFSET, value='answer', user_ip=TEST_IP_2),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        mapping = OrderedDict([
            (
                '99:q',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(
                                        timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET,
                                        user_agent=TEST_USER_AGENT,
                                    ),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
            questions=['99:q', '99:q'],
            answers=['answer', 'answer'],
        )
        eq_(
            flatten_question_answer_mapping(serialize_question_answer_mapping(mapping)),
            [
                {
                    'question': '99:q',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(
                            timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET,
                            user_agent=TEST_USER_AGENT,
                        ),
                        'end': None,
                    },
                },
            ],
        )

    def test_qa_mapping_basic_mixed_events(self):
        response = [
            event_item(name=EVENT_USER_AGENT, timestamp=1, value=TEST_USER_AGENT),
            event_item(name=EVENT_ACTION, timestamp=1, value='action', yandexuid=TEST_YANDEXUID, user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTQ, timestamp=1, value='99:q', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTA, timestamp=1, value='answer', user_ip=TEST_IP_2),
            event_item(name=EVENT_USERINFO_FT, timestamp=10, hintq='99:q2', hinta='answer', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTA, timestamp=20, value='answer2', user_ip=TEST_IP_2),
            event_item(name=EVENT_INFO_HINTQ, timestamp=20 + TEST_HINTQ_HINTA_TS_OFFSET, value='99:q', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        mapping = OrderedDict([
            (
                '99:q',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(
                                        user_ip=TEST_IP_2,
                                        user_agent=TEST_USER_AGENT,
                                        yandexuid=TEST_YANDEXUID,
                                    ),
                                    'end': events_info_interval_point(timestamp=10),
                                },
                            ],
                        },
                    ),
                    (
                        'answer2',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=20 + TEST_HINTQ_HINTA_TS_OFFSET),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
            (
                '99:q2',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=10),
                                    'end': events_info_interval_point(timestamp=20 + TEST_HINTQ_HINTA_TS_OFFSET),
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
            questions=['99:q', '99:q2', '99:q'],
            answers=['answer', 'answer', 'answer2'],
        )
        eq_(
            flatten_question_answer_mapping(serialize_question_answer_mapping(mapping)),
            [
                {
                    'question': '99:q',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(
                            user_ip=TEST_IP_2,
                            user_agent=TEST_USER_AGENT,
                        ),
                        'end': events_info_interval_point(timestamp=10),
                    },
                },
                {
                    'question': '99:q2',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(timestamp=10),
                        'end': events_info_interval_point(timestamp=20 + TEST_HINTQ_HINTA_TS_OFFSET),
                    },
                },
                {
                    'question': '99:q',
                    'answer': 'answer2',
                    'interval': {
                        'start': events_info_interval_point(timestamp=20 + TEST_HINTQ_HINTA_TS_OFFSET),
                        'end': None,
                    },
                },
            ],
        )

    def test_qa_mapping_question_change(self):
        response = [
            event_item(name=EVENT_INFO_HINTQ, timestamp=1, value='99:q', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTA, timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET, value='answer', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTQ, timestamp=20, value='99:q', user_ip=TEST_IP),  # 1
            event_item(name=EVENT_INFO_HINTQ, timestamp=21, value='99:q2', user_ip=TEST_IP),  # 2
            event_item(name=EVENT_USERINFO_FT, timestamp=30, hintq='99:q', hinta='answer2', user_ip=TEST_IP),
            event_item(name=EVENT_USER_AGENT, timestamp=30, value=TEST_USER_AGENT),
            event_item(name=EVENT_INFO_HINTQ, timestamp=41, value='99:q4', user_ip=TEST_IP),  # 3
        ]

        info = self.load_and_analyze_events(
            question_answer_mapping=True,
            questions=True,
            answers=True,
            registration_env=True,
            events=response,
        )
        mapping = OrderedDict([
            (
                '99:q',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET),
                                    'end': events_info_interval_point(timestamp=21),
                                },
                            ],
                        },
                    ),
                    (
                        'answer2',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=30, user_agent=TEST_USER_AGENT),
                                    'end': events_info_interval_point(timestamp=41),
                                },
                            ],
                        },
                    ),
                ]),
            ),
            (
                '99:q2',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=21),
                                    'end': events_info_interval_point(timestamp=30, user_agent=TEST_USER_AGENT),
                                },
                            ],
                        },
                    ),
                ]),
            ),
            (
                '99:q4',
                OrderedDict([
                    (
                        'answer2',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=41),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
            questions=['99:q', '99:q', '99:q2', '99:q', '99:q4'],
            answers=['answer', 'answer2'],
            registration_env=events_info_interval_point(timestamp=30, user_agent=TEST_USER_AGENT),
        )
        eq_(
            flatten_question_answer_mapping(serialize_question_answer_mapping(mapping)),
            [
                {
                    'question': u'99:q',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET),
                        'end': events_info_interval_point(timestamp=21),
                    },
                },
                {
                    'question': u'99:q2',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(timestamp=21),
                        'end': events_info_interval_point(timestamp=30, user_agent=TEST_USER_AGENT),
                    },
                },
                {
                    'question': u'99:q',
                    'answer': 'answer2',
                    'interval': {
                        'start': events_info_interval_point(timestamp=30, user_agent=TEST_USER_AGENT),
                        'end': events_info_interval_point(timestamp=41),
                    },
                },
                {
                    'question': u'99:q4',
                    'answer': 'answer2',
                    'interval': {
                        'start': events_info_interval_point(timestamp=41),
                        'end': None,
                    },
                },
            ],
        )

    def test_qa_mapping_answer_change(self):
        response = [
            event_item(name=EVENT_USERINFO_FT, timestamp=3, hintq='99:q', hinta='answer2', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTQ, timestamp=20, value='99:q2', user_ip=TEST_IP_2),
            event_item(name=EVENT_INFO_HINTA, timestamp=21, value='answer3', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTA, timestamp=41, value='answer4', user_ip=TEST_IP_2),
            event_item(name=EVENT_USER_AGENT, timestamp=41, value=TEST_USER_AGENT),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        mapping = OrderedDict([
            (
                '99:q',
                OrderedDict([
                    (
                        'answer2',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=3),
                                    # в TS 20 изменился только КВ, соответственно, время жизни данного ответа на
                                    # данный КВ окончилось
                                    'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                                },
                            ],
                        },
                    ),
                ]),
            ),
            (
                '99:q2',
                OrderedDict([
                    (
                        'answer2',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                                    'end': events_info_interval_point(timestamp=21),
                                },
                            ],
                        },
                    ),
                    (
                        'answer3',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=21),
                                    'end': events_info_interval_point(
                                        timestamp=41,
                                        user_ip=TEST_IP_2,
                                        user_agent=TEST_USER_AGENT,
                                    ),
                                },
                            ],
                        },
                    ),
                    (
                        'answer4',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(
                                        timestamp=41,
                                        user_ip=TEST_IP_2,
                                        user_agent=TEST_USER_AGENT,
                                    ),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
            questions=['99:q', '99:q2'],
            answers=['answer2', 'answer3', 'answer4'],
        )
        eq_(
            flatten_question_answer_mapping(serialize_question_answer_mapping(mapping)),
            [
                {
                    'question': '99:q',
                    'answer': 'answer2',
                    'interval': {
                        'start': events_info_interval_point(timestamp=3),
                        # в TS 20 изменился только КВ, соответственно, время жизни данного ответа на
                        # данный КВ окончилось
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                    },
                },
                {
                    'question': '99:q2',
                    'answer': 'answer2',
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                        'end': events_info_interval_point(timestamp=21),
                    },
                },
                {
                    'question': '99:q2',
                    'answer': 'answer3',
                    'interval': {
                        'start': events_info_interval_point(timestamp=21),
                        'end': events_info_interval_point(
                            timestamp=41,
                            user_ip=TEST_IP_2,
                            user_agent=TEST_USER_AGENT,
                        ),
                    },
                },
                {
                    'question': '99:q2',
                    'answer': 'answer4',
                    'interval': {
                        'start': events_info_interval_point(
                            timestamp=41,
                            user_ip=TEST_IP_2,
                            user_agent=TEST_USER_AGENT,
                        ),
                        'end': None,
                    },
                },
            ],
        )

    def test_qa_mapping_mixed_change(self):
        response = [
            event_item(timestamp=1, name=EVENT_USERINFO_FT, hintq=u'12:asdf', hinta=u'ответ2', user_ip=TEST_IP),
            event_item(timestamp=3, name=EVENT_INFO_HINTA, value=u'КО', user_ip=TEST_IP),
            event_item(timestamp=4, name=EVENT_INFO_HINTQ, value=u'99:КВ', user_ip=TEST_IP),
            event_item(timestamp=5, name=EVENT_USER_AGENT, value=TEST_USER_AGENT),
            event_item(timestamp=5, name=EVENT_INFO_HINTA, value=u'ответ', user_ip=TEST_IP),
            event_item(timestamp=6, name=EVENT_INFO_HINTA, value=u'ответ', user_ip=TEST_IP_2),
            event_item(timestamp=7, name=EVENT_INFO_HINTA, value=u'ответ4', user_ip=TEST_IP_2),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        mapping = OrderedDict([
            (
                '12:asdf',
                OrderedDict([
                    (
                        u'ответ2',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=1),
                                    'end': events_info_interval_point(timestamp=3),
                                },
                            ],
                        },
                    ),
                    (
                        u'КО',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=3),
                                    'end': events_info_interval_point(timestamp=4),
                                },
                            ],
                        },
                    ),
                ]),
            ),
            (
                u'99:КВ',
                OrderedDict([
                    (
                        u'КО',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=4),
                                    'end': events_info_interval_point(timestamp=5, user_agent=TEST_USER_AGENT),
                                },
                            ],
                        },
                    ),
                    (
                        u'ответ',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=5, user_agent=TEST_USER_AGENT),
                                    'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=7),
                                },
                            ],
                        },
                    ),
                    (
                        u'ответ4',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=7),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
            questions=['12:asdf', u'99:КВ'],
            answers=[u'ответ2', u'КО', u'ответ', u'ответ', u'ответ4'],
        )
        eq_(
            flatten_question_answer_mapping(serialize_question_answer_mapping(mapping)),
            [
                {
                    'question': u'12:asdf',
                    'answer': u'ответ2',
                    'interval': {
                        'start': events_info_interval_point(timestamp=1),
                        'end': events_info_interval_point(timestamp=3),
                    },
                },
                {
                    'question': u'12:asdf',
                    'answer': u'КО',
                    'interval': {
                        'start': events_info_interval_point(timestamp=3),
                        'end': events_info_interval_point(timestamp=4),
                    },
                },
                {
                    'question': u'99:КВ',
                    'answer': u'КО',
                    'interval': {
                        'start': events_info_interval_point(timestamp=4),
                        'end': events_info_interval_point(timestamp=5, user_agent=TEST_USER_AGENT),
                    },
                },
                {
                    'question': u'99:КВ',
                    'answer': u'ответ',
                    'interval': {
                        'start': events_info_interval_point(timestamp=5, user_agent=TEST_USER_AGENT),
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=7),
                    },
                },
                {
                    'question': u'99:КВ',
                    'answer': u'ответ4',
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=7),
                        'end': None,
                    },
                },
            ],
        )

    def test_qa_mapping_multiple_intervals_for_question_answer(self):
        """КО не меняется, проверяем правильность обработки интервалов актуальности КВ/КО"""
        response = [
            event_item(timestamp=1, name=EVENT_USERINFO_FT, hintq=u'99:q', hinta=u'answer', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTQ, timestamp=3, value='99:q', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTA, timestamp=3 + TEST_HINTQ_HINTA_TS_OFFSET, value='answer', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTA, timestamp=4, value='answer', user_ip=TEST_IP_2),
            event_item(name=EVENT_INFO_HINTQ, timestamp=4, value='99:q', user_ip=TEST_IP_2),
            event_item(name=EVENT_INFO_HINTQ, timestamp=5, value='99:q2', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTQ, timestamp=6, value='99:q', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTA, timestamp=6, value='answer', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        mapping = OrderedDict([
            (
                '99:q',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=1),
                                    'end': events_info_interval_point(timestamp=5),
                                },
                                {
                                    'start': events_info_interval_point(timestamp=6),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
            (
                '99:q2',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=5),
                                    'end': events_info_interval_point(timestamp=6),
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
            questions=['99:q', '99:q', '99:q', '99:q2', '99:q'],
            answers=['answer', 'answer', 'answer', 'answer'],
        )
        eq_(
            flatten_question_answer_mapping(serialize_question_answer_mapping(mapping)),
            [
                {
                    'question': '99:q',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(timestamp=1),
                        'end': events_info_interval_point(timestamp=5),
                    },
                },
                {
                    'question': '99:q2',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(timestamp=5),
                        'end': events_info_interval_point(timestamp=6),
                    },
                },
                {
                    'question': '99:q',
                    'answer': 'answer',
                    'interval': {
                        'start': events_info_interval_point(timestamp=6),
                        'end': None,
                    },
                },
            ],
        )

    def test_qa_mapping_registration_events_repaired(self):
        """События при регистрации преобразованы"""
        response = [
            event_item(timestamp=1, name=EVENT_USERINFO_FT, hintq=u'99:q', hinta=u'answer', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTA, timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET, value='answer', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTQ, timestamp=1.1, value='99:q', user_ip=TEST_IP),
            event_item(name=EVENT_INFO_HINTA, timestamp=2, value='answer', user_ip=TEST_IP_2),
            event_item(name=EVENT_INFO_HINTQ, timestamp=2, value='99:q2', user_ip=TEST_IP_2),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        mapping = OrderedDict([
            (
                '99:q',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=1),
                                    'end': events_info_interval_point(timestamp=2, user_ip=TEST_IP_2),
                                },
                            ],
                        },
                    ),
                ]),
            ),
            (
                '99:q2',
                OrderedDict([
                    (
                        'answer',
                        {
                            'intervals': [
                                {
                                    'start': events_info_interval_point(timestamp=2, user_ip=TEST_IP_2),
                                    'end': None,
                                },
                            ],
                        },
                    ),
                ]),
            ),
        ])
        self.assert_events_info_ok(
            info,
            question_answer_mapping=mapping,
            questions=['99:q', '99:q2'],
            answers=['answer', 'answer'],
        )

    def test_qa_mapping_validation_fail_initial_values_no_pairs(self):
        response = [
            event_item(name=EVENT_INFO_HINTQ, timestamp=20, value='99:q2'),
            event_item(name=EVENT_INFO_HINTA, timestamp=21, value='answer3'),
            event_item(name=EVENT_INFO_HINTA, timestamp=41, value='answer4'),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            question_answer_mapping={},
            questions=['99:q2'],
            answers=['answer3', 'answer4'],
        )

    def test_qa_mapping_validation_fail_initial_values_with_pair(self):
        response = [
            event_item(name=EVENT_INFO_HINTA, timestamp=1, value='answer4'),
            event_item(name=EVENT_USERINFO_FT, timestamp=3, hintq='99:q2', hinta='answer2', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            question_answer_mapping={},
            questions=['99:q2'],
            answers=['answer4', 'answer2'],
        )

    def test_qa_mapping_validation_fail_consequent_pairs_1(self):
        response = [
            event_item(name=EVENT_INFO_HINTQ, timestamp=1, value='99:q'),
            event_item(name=EVENT_INFO_HINTA, timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET, value='answer'),
            event_item(
                name=EVENT_INFO_HINTQ,
                timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET + TEST_HINTQ_HINTA_TS_OFFSET,
                value='99:q2',
            ),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            question_answer_mapping={},
            questions=['99:q', '99:q2'],
            answers=['answer'],
        )

    def test_qa_mapping_validation_fail_consequent_pairs_2_no_q_a(self):
        response = [
            event_item(name=EVENT_INFO_HINTQ, timestamp=1, value='99:q'),
            event_item(name=EVENT_INFO_HINTA, timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET, value='answer'),
            event_item(
                name=EVENT_USERINFO_FT,
                timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET + TEST_HINTQ_HINTA_TS_OFFSET,
                hintq='99:q2',
                hinta='answer2',
                user_ip=TEST_IP,
            ),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, events=response)
        self.assert_events_info_ok(
            info,
            question_answer_mapping={},
        )

    def test_qa_mapping_validation_fail_bad_pattern_two_questions(self):
        response = [
            event_item(name=EVENT_INFO_HINTQ, timestamp=1, value='99:q'),
            event_item(name=EVENT_INFO_HINTQ, timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET, value='99:q2'),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            question_answer_mapping={},
            questions=['99:q', '99:q2'],
        )

    def test_qa_mapping_validation_fail_bad_pattern_two_answers_at_the_same_time(self):
        response = [
            event_item(name=EVENT_INFO_HINTA, timestamp=1, value='answer1'),
            event_item(name=EVENT_INFO_HINTA, timestamp=1, value='answer2'),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            question_answer_mapping={},
            answers=['answer1', 'answer2'],
        )

    def test_qa_mapping_validation_fail_bad_pattern_two_answers(self):
        response = [
            event_item(name=EVENT_INFO_HINTA, timestamp=1, value='answer1'),
            event_item(name=EVENT_INFO_HINTA, timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET, value='answer2'),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            question_answer_mapping={},
            answers=['answer1', 'answer2'],
        )

    def test_qa_mapping_validation_fail_bad_pattern_mixed(self):
        response = [
            event_item(
                name=EVENT_INFO_HINTQ,
                timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET,
                value='99:q',
            ),
            event_item(
                name=EVENT_INFO_HINTA,
                timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET,
                value='answer',
                user_ip=TEST_IP,
            ),
            event_item(
                name=EVENT_INFO_HINTA,
                timestamp=1 + TEST_HINTQ_HINTA_TS_OFFSET + TEST_HINTQ_HINTA_TS_OFFSET,
                value='answer1',
            ),
        ]

        info = self.load_and_analyze_events(question_answer_mapping=True, questions=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            question_answer_mapping={},
            questions=['99:q'],
            answers=['answer', 'answer1'],
        )
