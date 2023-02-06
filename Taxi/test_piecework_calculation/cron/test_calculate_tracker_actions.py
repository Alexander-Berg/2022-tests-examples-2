# pylint:disable=protected-access, too-many-lines
import datetime
import decimal

import pytest

from piecework_calculation import tracker
from piecework_calculation import utils

TARIFFS_BY_COUNTRY = {
    'rus': [
        {
            'tariff_id': 'rus_tariff_id',
            'countries': ['rus'],
            'start_date': datetime.date(2020, 1, 1),
            'stop_date': datetime.date(2020, 2, 10),
            'cost_conditions': {
                'rules': [
                    {
                        'key': 'mail',
                        'type': 'action',
                        'actions': ['mail'],
                        'cost_by_line': {
                            '__default__': decimal.Decimal('0.0'),
                            'tracker_dtpStrahovanie': decimal.Decimal('2.0'),
                        },
                    },
                    {
                        'key': 'sms',
                        'type': 'action',
                        'actions': ['sms'],
                        'cost_by_line': {
                            '__default__': decimal.Decimal('0.0'),
                            'tracker_dtpStrahovanie': decimal.Decimal('3.0'),
                        },
                    },
                    {
                        'key': 'call',
                        'type': 'call',
                        'min_duration': 16,
                        'direction': 'outgoing',
                        'status_completed': 'bridged',
                        'cost_by_line': {
                            '__default__': decimal.Decimal('0.0'),
                            'tracker_dtpStrahovanie': decimal.Decimal('5.0'),
                        },
                    },
                    {
                        'key': 'tracker_create',
                        'type': 'action',
                        'actions': ['tracker_create'],
                        'cost_by_line': {
                            '__default__': decimal.Decimal('0.0'),
                            'tracker_incident': decimal.Decimal('50.0'),
                        },
                    },
                ],
            },
            'calc_night': True,
            'calc_holidays': True,
            'calc_workshifts': True,
            'daytime_begins': datetime.time(6, 0),
            'daytime_ends': datetime.time(22, 0),
            'benefit_conditions': {
                'min_hour_cost': 10.0,
                'rating_avg_duration_weight': 0.0,
                'rating_total_cost_weight': 0.0025,
                'rating_csat_weight': 0.49875,
                'rating_qa_weight': 0.49875,
                'min_workshifts_ratio': 0.25,
                'rating_max_total_cost': 11000,
                'benefit_thresholds_strict': [
                    {'threshold': 0, 'value': 0.5},
                    {'threshold': 80, 'value': 0.0},
                ],
            },
        },
    ],
}
PERIOD_TARIFF_BY_COUNTRY = {
    country: tariffs[-1] for country, tariffs in TARIFFS_BY_COUNTRY.items()
}

CMPD_EMPLOYEES = {
    'ivanov': {
        'login': 'ivanov',
        'skip_calc': False,
        'country': 'rus',
        'timezone': 'Europe/Moscow',
        'start_dt': datetime.datetime(2019, 12, 31, 21, 0),
        'stop_dt': datetime.datetime(2020, 1, 15, 21, 0),
        'workshifts': [
            [
                datetime.datetime(2019, 12, 31, 17, 0),
                datetime.datetime(2020, 1, 1, 5, 0),
            ],
            [
                datetime.datetime(2020, 1, 2, 17, 0),
                datetime.datetime(2020, 1, 3, 5, 0),
            ],
            [
                datetime.datetime(2020, 1, 5, 17, 0),
                datetime.datetime(2020, 1, 6, 5, 0),
            ],
            [
                datetime.datetime(2020, 1, 7, 17, 0),
                datetime.datetime(2020, 1, 8, 5, 0),
            ],
            [
                datetime.datetime(2020, 1, 10, 17, 0),
                datetime.datetime(2020, 1, 11, 5, 0),
            ],
            [
                datetime.datetime(2020, 1, 12, 17, 0),
                datetime.datetime(2020, 1, 13, 5, 0),
            ],
            [
                datetime.datetime(2020, 1, 15, 17, 0),
                datetime.datetime(2020, 1, 16, 5, 0),
            ],
        ],
        'csat_ratio': 0.9,
        'qa_ratio': 0.85,
        'rating_factor': 1.0,
        'workshifts_duration_sec': 302400,
        'plan_workshifts_duration_sec': 302400,
    },
}

OEBS_HOLIDAYS = {
    'ivanov': [
        datetime.date(2020, 1, 1),
        datetime.date(2020, 1, 2),
        datetime.date(2020, 1, 3),
        datetime.date(2020, 1, 7),
    ],
}


@pytest.mark.parametrize(
    [
        'events',
        'expected_result',
        'expected_daily_result',
        'expected_detail_result',
    ],
    [
        # action close
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 1, 4, 59),
                    'comment': None,
                    'has_email_message_flg': True,
                    'ticket_type': 'incident',
                    'tracker_create': True,
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('50.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'total_calls': 0,
                    'total_duration': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'avg_duration': None,
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'csat_ratio': decimal.Decimal('0.9'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                    },
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('50.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('50.0'),
                    'country': 'rus',
                    'daytime_count': 0,
                    'holidays_daytime_count': 1,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # holiday, daytime, workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 1, 4, 59),
                    'comment': None,
                    'has_email_message_flg': True,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('2.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'total_calls': 0,
                    'total_duration': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': (
                            decimal.Decimal('302400')
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': None,
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('2.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('2.0'),
                    'country': 'rus',
                    'daytime_count': 0,
                    'holidays_daytime_count': 1,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # holiday, daytime, no workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 1, 5, 0),
                    'comment': None,
                    'has_email_message_flg': True,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('2.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': None,
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 0,
                    'total_duration': decimal.Decimal('0.0'),
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('2.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('2.0'),
                    'country': 'rus',
                    'daytime_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # holiday, night, workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 1, 2, 59),
                    'comment': None,
                    'has_email_message_flg': True,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('2.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': None,
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 0,
                    'total_duration': decimal.Decimal('0.0'),
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('2.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('2.0'),
                    'country': 'rus',
                    'daytime_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 1,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # no holiday, night, workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 2, 59),
                    'comment': None,
                    'has_email_message_flg': True,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('2.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': None,
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 0,
                    'total_duration': decimal.Decimal('0.0'),
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('2.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('2.0'),
                    'country': 'rus',
                    'daytime_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 1,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # no holiday, night, no workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 19, 0),
                    'comment': None,
                    'has_email_message_flg': True,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('2.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': None,
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 0,
                    'total_duration': decimal.Decimal('0.0'),
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('2.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('2.0'),
                    'country': 'rus',
                    'daytime_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # no holiday, daytime, workfshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'comment': None,
                    'has_email_message_flg': True,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('2.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': None,
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 0,
                    'total_duration': decimal.Decimal('0.0'),
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('2.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('2.0'),
                    'country': 'rus',
                    'daytime_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # unknown ticket type
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'comment': None,
                    'has_email_message_flg': True,
                    'ticket_type': 'unknown',
                    'close': False,
                },
            ],
            {},
            [],
            [],
        ),
        # unknown login
        (
            [
                {
                    'user_login': 'unknown',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'comment': None,
                    'has_email_message_flg': True,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {},
            [],
            [],
        ),
        # SMS
        (
            [
                {
                    'user_login': 'robotsupporttaxi',
                    'event_dt': datetime.datetime(2020, 1, 6, 4, 0),
                    'comment': (
                        '!!(зел)**Отправленные смс:**!!'
                        '!!(зел)Данные об СМС:!!\n'
                        '-----\n'
                        'create_dt: 2020-01-06T13:09:49.408+0000\n'
                        'intent: support_suptech\n'
                        'login: ivanov\n'
                        'message_id: 281ab7070da8420a8f7763127b9b3dda\n'
                        'phone: \'+700000000\'\n'
                        'process_dt: 2022-03-11T13:10:15.250048+0000\n'
                        'sender: go\n'
                        'status: sent\n'
                        'text: тестовый текст.\n'
                    ),
                    'has_email_message_flg': False,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('3.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': None,
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 0,
                    'total_duration': decimal.Decimal('0.0'),
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('3.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('3.0'),
                    'country': 'rus',
                    'daytime_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # Failed SMS
        (
            [
                {
                    'user_login': 'robotsupporttaxi',
                    'event_dt': datetime.datetime(2020, 1, 6, 4, 0),
                    'comment': (
                        'blablabla\n'
                        '-----\n'
                        'login: ivanov\n'
                        'status: failed\n'
                        'text: some text\n'
                        'create_dt: 2020-01-06T03:00:00\n'
                    ),
                    'has_email_message_flg': False,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {},
            [],
            [],
        ),
        # Invalid YAML
        (
            [
                {
                    'user_login': 'robotsupporttaxi',
                    'event_dt': datetime.datetime(2020, 1, 6, 4, 0),
                    'comment': (
                        'blablabla\n'
                        '-----\n'
                        'login: ivanov'
                        'status: sent'
                        'text: some text'
                        'create_dt: 2020-01-06T03:00:00'
                    ),
                    'has_email_message_flg': False,
                    'ticket_type': 'dtpStrahovanie',
                    'close': False,
                },
            ],
            {},
            [],
            [],
        ),
    ],
)
async def test_calc_actions(
        cron_context,
        events,
        expected_result,
        expected_daily_result,
        expected_detail_result,
):
    rule = {
        'calculation_rule_id': 'some_rule_id',
        'tariff_type': 'support-taxi',
        'start_date': datetime.date(2020, 1, 1),
        'stop_date': datetime.date(2020, 1, 16),
        'rule_type': 'regular',
    }
    async with cron_context.pg.slave_pool.acquire() as conn:
        result = await tracker._calc_events(
            context=cron_context,
            conn=conn,
            rule=rule,
            events_it=_aiter(events),
            events_type=tracker.TYPE_ACTION,
            cmpd_employees=CMPD_EMPLOYEES,
            tariffs_by_country=TARIFFS_BY_COUNTRY,
            period_tariff_by_country=PERIOD_TARIFF_BY_COUNTRY,
            oebs_holidays=OEBS_HOLIDAYS,
        )
        for item in result.values():
            if item['benefit_conditions'] is None:
                continue
            item['benefit_conditions'] = utils.from_json(
                item['benefit_conditions'],
            )
        assert result == expected_result

        pg_daily_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, tariff_type, calc_type, calc_subtype, '
            'calc_date, login, daytime_cost, night_cost, '
            'holidays_daytime_cost, holidays_night_cost '
            'FROM piecework.calculation_daily_result '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY calc_type, calc_subtype, login',
            'some_rule_id',
        )
        pg_daily_result = [dict(item) for item in pg_daily_result]
        assert pg_daily_result == expected_daily_result

        pg_detail_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, tariff_type, tariff_id, country, calc_type, '
            'calc_subtype, calc_date, login, cost_action, daytime_count, '
            'night_count, holidays_daytime_count, holidays_night_count '
            'FROM piecework.calculation_detail WHERE calculation_rule_id = $1 '
            'ORDER BY calc_type, calc_subtype, login',
            'some_rule_id',
        )
        pg_detail_result = [dict(item) for item in pg_detail_result]
        assert pg_detail_result == expected_detail_result


@pytest.mark.parametrize(
    [
        'events',
        'expected_result',
        'expected_daily_result',
        'expected_detail_result',
    ],
    [
        # holiday, daytime, workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 1, 4, 59),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 1, 5, 0),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 1, 5, 0, 16,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('5.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': decimal.Decimal('16.0'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 1,
                    'total_duration': 16,
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('5.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('5.0'),
                    'country': 'rus',
                    'daytime_count': 0,
                    'holidays_daytime_count': 1,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # holiday, daytime, no workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 1, 5, 0),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 1, 5, 1),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 1, 5, 1, 16,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('5.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': decimal.Decimal('16.0'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 1,
                    'total_duration': 16,
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('5.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('5.0'),
                    'country': 'rus',
                    'daytime_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # holiday, night, workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 1, 2, 59),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 1, 3, 0),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 1, 3, 0, 16,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('5.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': decimal.Decimal('16.0'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 1,
                    'total_duration': 16,
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('5.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 1),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('5.0'),
                    'country': 'rus',
                    'daytime_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 1,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # no holiday, night, workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 2, 59),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 6, 3, 0),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 6, 3, 0, 16,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('5.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': decimal.Decimal('16.0'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 1,
                    'total_duration': 16,
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('5.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('5.0'),
                    'country': 'rus',
                    'daytime_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 1,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # no holiday, night, no workshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 19, 0),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 6, 19, 1),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 6, 19, 1, 16,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('5.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': decimal.Decimal('16.0'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 1,
                    'total_duration': 16,
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('5.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('5.0'),
                    'country': 'rus',
                    'daytime_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # no holiday, daytime, workfshift
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 6, 3, 1),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 6, 3, 1, 16,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {
                'ivanov': {
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('5.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'benefit_conditions': {
                        'csat_ratio': decimal.Decimal('0.9'),
                        'qa_ratio': decimal.Decimal('0.85'),
                        'rating_factor': decimal.Decimal('1.0'),
                        'workshifts_duration_sec': decimal.Decimal('302400'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '302400',
                        ),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                        'rating_max_total_cost': decimal.Decimal('11000'),
                        'rating_total_cost_weight': decimal.Decimal('0.0025'),
                        'rating_qa_weight': decimal.Decimal('0.49875'),
                        'rating_csat_weight': decimal.Decimal('0.49875'),
                        'rating_avg_duration_weight': decimal.Decimal('0.0'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'avg_duration': decimal.Decimal('16.0'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                    },
                    'total_calls': 1,
                    'total_duration': 16,
                },
            },
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'daytime_cost': decimal.Decimal('5.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanov',
                    'night_cost': decimal.Decimal('0.0'),
                    'tariff_type': 'support-taxi',
                },
            ],
            [
                {
                    'calc_date': datetime.date(2020, 1, 6),
                    'calc_subtype': 'tracker_calls',
                    'calc_type': 'general',
                    'calculation_rule_id': 'some_rule_id',
                    'cost_action': decimal.Decimal('5.0'),
                    'country': 'rus',
                    'daytime_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                    'login': 'ivanov',
                    'night_count': 0,
                    'tariff_id': 'rus_tariff_id',
                    'tariff_type': 'support-taxi',
                },
            ],
        ),
        # unknown ticket type
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 6, 3, 1),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 6, 3, 1, 16,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'unknown',
                },
            ],
            {},
            [],
            [],
        ),
        # unknown login
        (
            [
                {
                    'user_login': 'unknown',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 1, 3, 1),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 1, 3, 1, 16,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {},
            [],
            [],
        ),
        # short call
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 1, 3, 1),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 1, 3, 1, 15,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {},
            [],
            [],
        ),
        # incoming call
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 1, 3, 1),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 1, 3, 1, 16,
                    ),
                    'direction_code': 'incoming',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {},
            [],
            [],
        ),
        # failed call
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 1, 3, 1),
                    'utc_completed_dttm': datetime.datetime(
                        2020, 1, 1, 3, 1, 16,
                    ),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'failed',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {},
            [],
            [],
        ),
        # completed time missing
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'utc_answered_dttm': datetime.datetime(2020, 1, 1, 3, 1),
                    'utc_completed_dttm': None,
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {},
            [],
            [],
        ),
        # answered time missing
        (
            [
                {
                    'user_login': 'ivanov',
                    'event_dt': datetime.datetime(2020, 1, 6, 3, 0),
                    'utc_answered_dttm': None,
                    'utc_completed_dttm': datetime.datetime(2020, 1, 1, 3, 1),
                    'direction_code': 'outgoing',
                    'call_completed_status': 'bridged',
                    'ticket_type': 'dtpStrahovanie',
                },
            ],
            {},
            [],
            [],
        ),
    ],
)
async def test_calc_calls(
        cron_context,
        events,
        expected_result,
        expected_daily_result,
        expected_detail_result,
):
    rule = {
        'calculation_rule_id': 'some_rule_id',
        'tariff_type': 'support-taxi',
        'start_date': datetime.date(2020, 1, 1),
        'stop_date': datetime.date(2020, 1, 16),
        'rule_type': 'regular',
    }
    async with cron_context.pg.slave_pool.acquire() as conn:
        result = await tracker._calc_events(
            context=cron_context,
            conn=conn,
            rule=rule,
            events_it=_aiter(events),
            events_type=tracker.TYPE_CALL,
            cmpd_employees=CMPD_EMPLOYEES,
            tariffs_by_country=TARIFFS_BY_COUNTRY,
            period_tariff_by_country=PERIOD_TARIFF_BY_COUNTRY,
            oebs_holidays=OEBS_HOLIDAYS,
        )
        for item in result.values():
            if item['benefit_conditions'] is None:
                continue
            item['benefit_conditions'] = utils.from_json(
                item['benefit_conditions'],
            )
        assert result == expected_result

        pg_daily_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, tariff_type, calc_type, calc_subtype, '
            'calc_date, login, daytime_cost, night_cost, '
            'holidays_daytime_cost, holidays_night_cost '
            'FROM piecework.calculation_daily_result '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY calc_type, calc_subtype, login',
            'some_rule_id',
        )
        pg_daily_result = [dict(item) for item in pg_daily_result]
        assert pg_daily_result == expected_daily_result

        pg_detail_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, tariff_type, tariff_id, country, calc_type, '
            'calc_subtype, calc_date, login, cost_action, daytime_count, '
            'night_count, holidays_daytime_count, holidays_night_count '
            'FROM piecework.calculation_detail WHERE calculation_rule_id = $1 '
            'ORDER BY calc_type, calc_subtype, login',
            'some_rule_id',
        )
        pg_detail_result = [dict(item) for item in pg_detail_result]
        assert pg_detail_result == expected_detail_result


async def _aiter(iterable):
    for item in iterable:
        yield item
