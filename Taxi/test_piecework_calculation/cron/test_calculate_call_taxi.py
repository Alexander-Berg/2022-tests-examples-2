# pylint: disable=too-many-lines
import datetime
import decimal

import pytest

from piecework_calculation import calculation_rules
from piecework_calculation import call_taxi
from piecework_calculation import cargo_callcenter
from piecework_calculation import constants
from piecework_calculation import utils
from piecework_calculation.generated.cron import run_cron

NOW = datetime.datetime(2021, 1, 16, 11, 0)
AGENT_EMPLOYEES = {
    'items': [
        {
            'country': 'ru',
            'login': 'ivanova',
            'half_time': False,
            'team': 'first',
        },
        {
            'country': 'ru',
            'login': 'petrova',
            'half_time': True,
            'team': 'second',
        },
        {
            'country': 'ru',
            'login': 'smirnova',
            'half_time': False,
            'team': 'second',
        },
    ],
}
EXPECTED_PAYDAY_REQUEST = {
    'name': 'draft_2021-01-16T11:00:00_0',
    'people': [
        {
            'login': 'test_1',
            'employeeTypes': [
                {
                    'employeeType': 'S',
                    'transactions': [
                        {
                            'paymentDate': '2021-01-20T00:00:00+07:00',
                            'transactionId': '1',
                            'paymentSum': 15.5,
                        },
                    ],
                },
            ],
        },
        {
            'login': 'test_2',
            'employeeTypes': [
                {
                    'employeeType': 'S',
                    'transactions': [
                        {
                            'paymentDate': '2021-01-15T23:00:00+08:00',
                            'transactionId': '2',
                            'paymentSum': 16.5,
                        },
                    ],
                },
            ],
        },
        {
            'login': 'test_3',
            'employeeTypes': [
                {
                    'employeeType': 'S',
                    'transactions': [
                        {
                            'paymentDate': '2021-01-24T15:00:00+03:00',
                            'transactionId': '3',
                            'paymentSum': 16.5,
                        },
                    ],
                },
            ],
        },
        {
            'login': 'test_4',
            'employeeTypes': [
                {
                    'employeeType': 'S',
                    'transactions': [
                        {
                            'paymentDate': '2021-01-26T23:00:00+05:00',
                            'transactionId': '4',
                            'paymentSum': 16.5,
                        },
                    ],
                },
            ],
        },
        {
            'login': 'test_5',
            'employeeTypes': [
                {
                    'employeeType': 'S',
                    'transactions': [
                        {
                            'paymentDate': '2021-01-28T23:00:00+03:00',
                            'transactionId': '5',
                            'paymentSum': 16.5,
                        },
                    ],
                },
            ],
        },
    ],
}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'rules_processor_class, calculation_rule_id, expected_pg_result, '
    'expected_pg_daily_result, expected_pg_detail_result',
    [
        (
            call_taxi.CallTaxiUnifiedRulesProcessor,
            'unified_rule_id',
            [
                {
                    'benefit_conditions': {
                        'claim_ratio': decimal.Decimal('0.6'),
                        'discipline_rating_weight': decimal.Decimal('0.1'),
                        'discipline_ratio': decimal.Decimal('0.85'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '864000.0',
                        ),
                        'qa_ratio': decimal.Decimal('0.27375'),
                        'unified_qa_rating_weight': decimal.Decimal('0.8'),
                        'unified_qa_ratio': decimal.Decimal('0.40425'),
                        'workshifts_duration_sec': decimal.Decimal('10800'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0.0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80.0'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'hour_cost_rating_weight': decimal.Decimal('0.1'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                    },
                    'benefits': decimal.Decimal('0.0'),
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'unified_rule_id',
                    'calls_completed': None,
                    'calls_converted': None,
                    'cargo_benefits': None,
                    'cargo_calls': None,
                    'conversion': None,
                    'conversion_benefits': None,
                    'conversion_benefits_weight': None,
                    'corporate_benefits': None,
                    'corporate_calls': None,
                    'daytime_cost': decimal.Decimal('90.18'),
                    'holidays_daytime_cost': decimal.Decimal('30.06'),
                    'holidays_night_cost': decimal.Decimal('24.05'),
                    'login': 'ivanova',
                    'min_qa_ratio': None,
                    'newbie_cargo_benefits': None,
                    'newbie_cargo_calls': None,
                    'newbie_corporate_benefits': None,
                    'newbie_corporate_calls': None,
                    'newbie_daytime_cost': None,
                    'newbie_holidays_daytime_cost': None,
                    'newbie_holidays_night_cost': None,
                    'newbie_night_cost': None,
                    'night_cost': decimal.Decimal('24.05'),
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 16),
                },
                {
                    'benefit_conditions': {
                        'claim_ratio': decimal.Decimal('0.0'),
                        'discipline_rating_weight': decimal.Decimal('0.1'),
                        'discipline_ratio': decimal.Decimal('0.75'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '432000.0',
                        ),
                        'qa_ratio': decimal.Decimal('0.248'),
                        'unified_qa_rating_weight': decimal.Decimal('0.8'),
                        'unified_qa_ratio': decimal.Decimal('0.1488'),
                        'workshifts_duration_sec': decimal.Decimal('7200'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0.0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80.0'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'hour_cost_rating_weight': decimal.Decimal('0.1'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                    },
                    'benefits': decimal.Decimal('0.0'),
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'unified_rule_id',
                    'calls_completed': None,
                    'calls_converted': None,
                    'cargo_benefits': None,
                    'cargo_calls': None,
                    'conversion': None,
                    'conversion_benefits': None,
                    'conversion_benefits_weight': None,
                    'corporate_benefits': None,
                    'corporate_calls': None,
                    'daytime_cost': decimal.Decimal('38.13'),
                    'holidays_daytime_cost': decimal.Decimal('15.05'),
                    'holidays_night_cost': decimal.Decimal('18.06'),
                    'login': 'petrova',
                    'min_qa_ratio': None,
                    'newbie_cargo_benefits': None,
                    'newbie_cargo_calls': None,
                    'newbie_corporate_benefits': None,
                    'newbie_corporate_calls': None,
                    'newbie_daytime_cost': None,
                    'newbie_holidays_daytime_cost': None,
                    'newbie_holidays_night_cost': None,
                    'newbie_night_cost': None,
                    'night_cost': decimal.Decimal('3.01'),
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 16),
                },
                {
                    'benefit_conditions': None,
                    'benefits': decimal.Decimal('0.0'),
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'unified_rule_id',
                    'calls_completed': None,
                    'calls_converted': None,
                    'cargo_benefits': None,
                    'cargo_calls': None,
                    'conversion': None,
                    'conversion_benefits': None,
                    'conversion_benefits_weight': None,
                    'corporate_benefits': None,
                    'corporate_calls': None,
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'smirnova',
                    'min_qa_ratio': None,
                    'newbie_cargo_benefits': None,
                    'newbie_cargo_calls': None,
                    'newbie_corporate_benefits': None,
                    'newbie_corporate_calls': None,
                    'newbie_daytime_cost': None,
                    'newbie_holidays_daytime_cost': None,
                    'newbie_holidays_night_cost': None,
                    'newbie_night_cost': None,
                    'night_cost': decimal.Decimal('0.0'),
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 16),
                },
            ],
            [
                {
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'unified_rule_id',
                    'daytime_cost': decimal.Decimal('50.10'),
                    'holidays_daytime_cost': decimal.Decimal('10.02'),
                    'holidays_night_cost': decimal.Decimal('9.02'),
                    'login': 'ivanova',
                    'night_cost': decimal.Decimal('20.04'),
                    'calc_date': datetime.date(2021, 1, 5),
                    'tariff_type': 'call-taxi-unified',
                },
                {
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'unified_rule_id',
                    'daytime_cost': decimal.Decimal('40.08'),
                    'holidays_daytime_cost': decimal.Decimal('20.04'),
                    'holidays_night_cost': decimal.Decimal('15.03'),
                    'login': 'ivanova',
                    'night_cost': decimal.Decimal('4.01'),
                    'calc_date': datetime.date(2021, 1, 7),
                    'tariff_type': 'call-taxi-unified',
                },
                {
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'unified_rule_id',
                    'daytime_cost': decimal.Decimal('38.13'),
                    'holidays_daytime_cost': decimal.Decimal('15.05'),
                    'holidays_night_cost': decimal.Decimal('18.06'),
                    'login': 'petrova',
                    'night_cost': decimal.Decimal('3.01'),
                    'calc_date': datetime.date(2021, 1, 6),
                    'tariff_type': 'call-taxi-unified',
                },
            ],
            [
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 5),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'calltaxi_common',
                    'daytime_count': 0,
                    'night_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 1,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 7),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'calltaxi_common',
                    'daytime_count': 0,
                    'night_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 5),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'cargo',
                    'daytime_count': 10,
                    'night_count': 4,
                    'holidays_daytime_count': 2,
                    'holidays_night_count': 1,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 7),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'corp',
                    'daytime_count': 8,
                    'night_count': 0,
                    'holidays_daytime_count': 4,
                    'holidays_night_count': 3,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 5),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('4.0'),
                    'cost_condition_key': 'calltaxi_order',
                    'line': 'calltaxi_common',
                    'daytime_count': 0,
                    'night_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 1,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 7),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('4.0'),
                    'cost_condition_key': 'calltaxi_order',
                    'line': 'calltaxi_common',
                    'daytime_count': 0,
                    'night_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 5),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('5.0'),
                    'cost_condition_key': 'calltaxi_order',
                    'line': 'cargo',
                    'daytime_count': 10,
                    'night_count': 4,
                    'holidays_daytime_count': 2,
                    'holidays_night_count': 1,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 7),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('5.0'),
                    'cost_condition_key': 'calltaxi_order',
                    'line': 'corp',
                    'daytime_count': 8,
                    'night_count': 0,
                    'holidays_daytime_count': 4,
                    'holidays_night_count': 3,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 6),
                    'country': 'ru',
                    'login': 'petrova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'calltaxi_common',
                    'daytime_count': 1,
                    'night_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 6),
                    'country': 'ru',
                    'login': 'petrova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'econom',
                    'daytime_count': 12,
                    'night_count': 1,
                    'holidays_daytime_count': 5,
                    'holidays_night_count': 6,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 6),
                    'country': 'ru',
                    'login': 'petrova',
                    'cost_action': decimal.Decimal('2.0'),
                    'cost_condition_key': 'calltaxi_order',
                    'line': 'calltaxi_common',
                    'daytime_count': 1,
                    'night_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                },
                {
                    'tariff_type': 'call-taxi-unified',
                    'tariff_id': 'unified_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'unified_rule_id',
                    'calc_date': datetime.date(2021, 1, 6),
                    'country': 'ru',
                    'login': 'petrova',
                    'cost_action': decimal.Decimal('3.0'),
                    'cost_condition_key': 'calltaxi_order',
                    'line': 'econom',
                    'daytime_count': 12,
                    'night_count': 1,
                    'holidays_daytime_count': 5,
                    'holidays_night_count': 6,
                },
            ],
        ),
        (
            cargo_callcenter.CargoCallcenterRulesProcessor,
            'cargo_rule_id',
            [
                {
                    'benefit_conditions': {
                        'claim_ratio': decimal.Decimal('0.6'),
                        'discipline_rating_weight': decimal.Decimal('0.1'),
                        'discipline_ratio': decimal.Decimal('0.85'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '864000.0',
                        ),
                        'qa_ratio': decimal.Decimal('0.27375'),
                        'unified_qa_rating_weight': decimal.Decimal('0.8'),
                        'unified_qa_ratio': decimal.Decimal('0.40425'),
                        'workshifts_duration_sec': decimal.Decimal('10800'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0.0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80.0'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'hour_cost_rating_weight': decimal.Decimal('0.1'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                    },
                    'benefits': decimal.Decimal('0.0'),
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calls_completed': None,
                    'calls_converted': None,
                    'cargo_benefits': None,
                    'cargo_calls': None,
                    'conversion': None,
                    'conversion_benefits': None,
                    'conversion_benefits_weight': None,
                    'corporate_benefits': None,
                    'corporate_calls': None,
                    'daytime_cost': decimal.Decimal('90.18'),
                    'holidays_daytime_cost': decimal.Decimal('30.06'),
                    'holidays_night_cost': decimal.Decimal('24.05'),
                    'login': 'ivanova',
                    'min_qa_ratio': None,
                    'newbie_cargo_benefits': None,
                    'newbie_cargo_calls': None,
                    'newbie_corporate_benefits': None,
                    'newbie_corporate_calls': None,
                    'newbie_daytime_cost': None,
                    'newbie_holidays_daytime_cost': None,
                    'newbie_holidays_night_cost': None,
                    'newbie_night_cost': None,
                    'night_cost': decimal.Decimal('24.05'),
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 16),
                },
                {
                    'benefit_conditions': {
                        'claim_ratio': decimal.Decimal('0.0'),
                        'discipline_rating_weight': decimal.Decimal('0.1'),
                        'discipline_ratio': decimal.Decimal('0.75'),
                        'plan_workshifts_duration_sec': decimal.Decimal(
                            '432000.0',
                        ),
                        'qa_ratio': decimal.Decimal('0.248'),
                        'unified_qa_rating_weight': decimal.Decimal('0.8'),
                        'unified_qa_ratio': decimal.Decimal('0.1488'),
                        'workshifts_duration_sec': decimal.Decimal('7200'),
                        'benefit_thresholds_strict': [
                            {
                                'threshold': decimal.Decimal('0.0'),
                                'value': decimal.Decimal('0.5'),
                            },
                            {
                                'threshold': decimal.Decimal('80.0'),
                                'value': decimal.Decimal('0.0'),
                            },
                        ],
                        'hour_cost_rating_weight': decimal.Decimal('0.1'),
                        'min_hour_cost': decimal.Decimal('10.0'),
                        'min_workshifts_ratio': decimal.Decimal('0.25'),
                    },
                    'benefits': decimal.Decimal('0.0'),
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calls_completed': None,
                    'calls_converted': None,
                    'cargo_benefits': None,
                    'cargo_calls': None,
                    'conversion': None,
                    'conversion_benefits': None,
                    'conversion_benefits_weight': None,
                    'corporate_benefits': None,
                    'corporate_calls': None,
                    'daytime_cost': decimal.Decimal('38.13'),
                    'holidays_daytime_cost': decimal.Decimal('15.05'),
                    'holidays_night_cost': decimal.Decimal('18.06'),
                    'login': 'petrova',
                    'min_qa_ratio': None,
                    'newbie_cargo_benefits': None,
                    'newbie_cargo_calls': None,
                    'newbie_corporate_benefits': None,
                    'newbie_corporate_calls': None,
                    'newbie_daytime_cost': None,
                    'newbie_holidays_daytime_cost': None,
                    'newbie_holidays_night_cost': None,
                    'newbie_night_cost': None,
                    'night_cost': decimal.Decimal('3.01'),
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 16),
                },
                {
                    'benefit_conditions': None,
                    'benefits': decimal.Decimal('0.0'),
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calls_completed': None,
                    'calls_converted': None,
                    'cargo_benefits': None,
                    'cargo_calls': None,
                    'conversion': None,
                    'conversion_benefits': None,
                    'conversion_benefits_weight': None,
                    'corporate_benefits': None,
                    'corporate_calls': None,
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'smirnova',
                    'min_qa_ratio': None,
                    'newbie_cargo_benefits': None,
                    'newbie_cargo_calls': None,
                    'newbie_corporate_benefits': None,
                    'newbie_corporate_calls': None,
                    'newbie_daytime_cost': None,
                    'newbie_holidays_daytime_cost': None,
                    'newbie_holidays_night_cost': None,
                    'newbie_night_cost': None,
                    'night_cost': decimal.Decimal('0.0'),
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 16),
                },
            ],
            [
                {
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'cargo_rule_id',
                    'daytime_cost': decimal.Decimal('50.10'),
                    'holidays_daytime_cost': decimal.Decimal('10.02'),
                    'holidays_night_cost': decimal.Decimal('9.02'),
                    'login': 'ivanova',
                    'night_cost': decimal.Decimal('20.04'),
                    'calc_date': datetime.date(2021, 1, 5),
                    'tariff_type': 'cargo-callcenter',
                },
                {
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'cargo_rule_id',
                    'daytime_cost': decimal.Decimal('40.08'),
                    'holidays_daytime_cost': decimal.Decimal('20.04'),
                    'holidays_night_cost': decimal.Decimal('15.03'),
                    'login': 'ivanova',
                    'night_cost': decimal.Decimal('4.01'),
                    'calc_date': datetime.date(2021, 1, 7),
                    'tariff_type': 'cargo-callcenter',
                },
                {
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'cargo_rule_id',
                    'daytime_cost': decimal.Decimal('38.13'),
                    'holidays_daytime_cost': decimal.Decimal('15.05'),
                    'holidays_night_cost': decimal.Decimal('18.06'),
                    'login': 'petrova',
                    'night_cost': decimal.Decimal('3.01'),
                    'calc_date': datetime.date(2021, 1, 6),
                    'tariff_type': 'cargo-callcenter',
                },
            ],
            [
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 5),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'calltaxi_common',
                    'daytime_count': 0,
                    'night_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 1,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 7),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'calltaxi_common',
                    'daytime_count': 0,
                    'night_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 5),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'cargo',
                    'daytime_count': 10,
                    'night_count': 4,
                    'holidays_daytime_count': 2,
                    'holidays_night_count': 1,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 7),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'corp',
                    'daytime_count': 8,
                    'night_count': 0,
                    'holidays_daytime_count': 4,
                    'holidays_night_count': 3,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 5),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('4.0'),
                    'cost_condition_key': 'calltaxi_order_first',
                    'line': 'calltaxi_common',
                    'daytime_count': 0,
                    'night_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 1,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 7),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('4.0'),
                    'cost_condition_key': 'calltaxi_order_first',
                    'line': 'calltaxi_common',
                    'daytime_count': 0,
                    'night_count': 1,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 5),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('5.0'),
                    'cost_condition_key': 'calltaxi_order_first_cargo',
                    'line': 'cargo',
                    'daytime_count': 10,
                    'night_count': 4,
                    'holidays_daytime_count': 2,
                    'holidays_night_count': 1,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 7),
                    'country': 'ru',
                    'login': 'ivanova',
                    'cost_action': decimal.Decimal('5.0'),
                    'cost_condition_key': 'calltaxi_order_first_corp',
                    'line': 'corp',
                    'daytime_count': 8,
                    'night_count': 0,
                    'holidays_daytime_count': 4,
                    'holidays_night_count': 3,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 6),
                    'country': 'ru',
                    'login': 'petrova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'calltaxi_common',
                    'daytime_count': 1,
                    'night_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 6),
                    'country': 'ru',
                    'login': 'petrova',
                    'cost_action': decimal.Decimal('0.01'),
                    'cost_condition_key': 'calltaxi_call',
                    'line': 'econom',
                    'daytime_count': 12,
                    'night_count': 1,
                    'holidays_daytime_count': 5,
                    'holidays_night_count': 6,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 6),
                    'country': 'ru',
                    'login': 'petrova',
                    'cost_action': decimal.Decimal('2.0'),
                    'cost_condition_key': 'calltaxi_order_second',
                    'line': 'calltaxi_common',
                    'daytime_count': 1,
                    'night_count': 0,
                    'holidays_daytime_count': 0,
                    'holidays_night_count': 0,
                },
                {
                    'tariff_type': 'cargo-callcenter',
                    'tariff_id': 'cargo_tariff_id',
                    'calc_type': 'general',
                    'calc_subtype': 'call-taxi',
                    'calculation_rule_id': 'cargo_rule_id',
                    'calc_date': datetime.date(2021, 1, 6),
                    'country': 'ru',
                    'login': 'petrova',
                    'cost_action': decimal.Decimal('3.0'),
                    'cost_condition_key': 'calltaxi_order_second_econom',
                    'line': 'econom',
                    'daytime_count': 12,
                    'night_count': 1,
                    'holidays_daytime_count': 5,
                    'holidays_night_count': 6,
                },
            ],
        ),
        (
            cargo_callcenter.CargoCallcenterRulesProcessor,
            'dismissal_cargo_rule_id',
            [
                {
                    'benefit_conditions': None,
                    'benefits': decimal.Decimal('0.0'),
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'dismissal_cargo_rule_id',
                    'calls_completed': None,
                    'calls_converted': None,
                    'cargo_benefits': None,
                    'cargo_calls': None,
                    'conversion': None,
                    'conversion_benefits': None,
                    'conversion_benefits_weight': None,
                    'corporate_benefits': None,
                    'corporate_calls': None,
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'ivanova',
                    'min_qa_ratio': None,
                    'newbie_cargo_benefits': None,
                    'newbie_cargo_calls': None,
                    'newbie_corporate_benefits': None,
                    'newbie_corporate_calls': None,
                    'newbie_daytime_cost': None,
                    'newbie_holidays_daytime_cost': None,
                    'newbie_holidays_night_cost': None,
                    'newbie_night_cost': None,
                    'night_cost': decimal.Decimal('0.0'),
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 1),
                },
                {
                    'benefit_conditions': None,
                    'benefits': decimal.Decimal('0.0'),
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'dismissal_cargo_rule_id',
                    'calls_completed': None,
                    'calls_converted': None,
                    'cargo_benefits': None,
                    'cargo_calls': None,
                    'conversion': None,
                    'conversion_benefits': None,
                    'conversion_benefits_weight': None,
                    'corporate_benefits': None,
                    'corporate_calls': None,
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'petrova',
                    'min_qa_ratio': None,
                    'newbie_cargo_benefits': None,
                    'newbie_cargo_calls': None,
                    'newbie_corporate_benefits': None,
                    'newbie_corporate_calls': None,
                    'newbie_daytime_cost': None,
                    'newbie_holidays_daytime_cost': None,
                    'newbie_holidays_night_cost': None,
                    'newbie_night_cost': None,
                    'night_cost': decimal.Decimal('0.0'),
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 1),
                },
                {
                    'benefit_conditions': None,
                    'benefits': decimal.Decimal('0.0'),
                    'calc_subtype': 'call-taxi',
                    'calc_type': 'general',
                    'calculation_rule_id': 'dismissal_cargo_rule_id',
                    'calls_completed': None,
                    'calls_converted': None,
                    'cargo_benefits': None,
                    'cargo_calls': None,
                    'conversion': None,
                    'conversion_benefits': None,
                    'conversion_benefits_weight': None,
                    'corporate_benefits': None,
                    'corporate_calls': None,
                    'daytime_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'login': 'smirnova',
                    'min_qa_ratio': None,
                    'newbie_cargo_benefits': None,
                    'newbie_cargo_calls': None,
                    'newbie_corporate_benefits': None,
                    'newbie_corporate_calls': None,
                    'newbie_daytime_cost': None,
                    'newbie_holidays_daytime_cost': None,
                    'newbie_holidays_night_cost': None,
                    'newbie_night_cost': None,
                    'night_cost': decimal.Decimal('0.0'),
                    'start_date': datetime.date(2021, 1, 1),
                    'stop_date': datetime.date(2021, 1, 1),
                },
            ],
            [],
            [],
        ),
    ],
)
async def test_unified_calculate(
        cron_context,
        rules_processor_class,
        calculation_rule_id,
        expected_pg_result,
        expected_pg_daily_result,
        expected_pg_detail_result,
        mock_agent_employees,
):
    mock_agent_employees(AGENT_EMPLOYEES)
    async with cron_context.pg.slave_pool.acquire() as conn:
        async with conn.transaction():
            rule = await calculation_rules.find_by_id(
                cron_context, calculation_rule_id, conn,
            )
            rules_processor = rules_processor_class(cron_context)
            rules_processor.conn = conn
            rules_processor.rule = rule
            await rules_processor.before_process()
            await rules_processor.process_rule()

        pg_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, start_date, stop_date, login, calc_type, '
            'calc_subtype, daytime_cost, night_cost, holidays_daytime_cost, '
            'holidays_night_cost, benefits, newbie_daytime_cost, '
            'newbie_night_cost, newbie_holidays_daytime_cost, '
            'newbie_holidays_night_cost, conversion, calls_completed, '
            'calls_converted, conversion_benefits_weight, '
            'conversion_benefits, cargo_calls, cargo_benefits, '
            'corporate_calls, corporate_benefits, newbie_cargo_calls, '
            'newbie_cargo_benefits, newbie_corporate_calls, '
            'newbie_corporate_benefits, min_qa_ratio, benefit_conditions '
            'FROM piecework.calculation_result WHERE calculation_rule_id = $1 '
            'ORDER BY login',
            calculation_rule_id,
        )
        pg_result = [dict(item) for item in pg_result]
        for item in pg_result:
            if item['benefit_conditions'] is None:
                continue
            item['benefit_conditions'] = utils.from_json(
                item['benefit_conditions'],
            )

        assert pg_result == expected_pg_result

        pg_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, calc_date, login, calc_type, '
            'calc_subtype, daytime_cost, night_cost, holidays_daytime_cost, '
            'holidays_night_cost, tariff_type '
            'FROM piecework.calculation_daily_result '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY login',
            calculation_rule_id,
        )
        pg_result = [dict(item) for item in pg_result]

        assert pg_result == expected_pg_daily_result

        pg_result = await conn.fetch(
            'SELECT '
            '   tariff_type,'
            '   tariff_id,'
            '   calc_type,'
            '   calc_subtype,'
            '   calculation_rule_id,'
            '   calc_date,'
            '   country,'
            '   login,'
            '   cost_action,'
            '   cost_condition_key,'
            '   line,'
            '   daytime_count,'
            '   night_count,'
            '   holidays_daytime_count,'
            '   holidays_night_count '
            'FROM piecework.calculation_detail '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY login, cost_condition_key, line, calc_date',
            calculation_rule_id,
        )
        pg_result = [dict(item) for item in pg_result]
        assert pg_result == expected_pg_detail_result


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    PIECEWORK_CALCULATION_PAYMENT_SETTINGS={
        'ru': {'ticket_locale': 'ru', 'destination': 'oebs'},
    },
    PIECEWORK_CALCULATION_YT_CHUNK_SIZE=2,
)
async def test_crontask(
        cron_context,
        mock_create_draft,
        mock_payday_upload,
        monkeypatch,
        mock,
        mock_agent_employees,
):
    mock_agent_employees({'items': []})
    mocked_payday_upload = mock_payday_upload(
        {'status': constants.PAYDAY_SUCCESS_STATUS},
    )

    @mock
    async def _dummy_salary():
        pass

    @mock
    async def _dummy_benefits():
        pass

    monkeypatch.setattr(
        call_taxi.CallTaxiUnifiedRulesProcessor, 'calc_salary', _dummy_salary,
    )
    monkeypatch.setattr(
        call_taxi.CallTaxiUnifiedRulesProcessor,
        'update_unified_benefits',
        _dummy_benefits,
    )

    await run_cron.main(
        ['piecework_calculation.crontasks.calculate_call_taxi', '-t', '0'],
    )

    assert _dummy_salary.calls
    assert _dummy_benefits.calls

    assert mocked_payday_upload.times_called == 1
    payday_request = mocked_payday_upload.next_call()['request'].json
    payday_request['people'] = list(
        sorted(payday_request['people'], key=lambda x: x['login']),
    )
    assert payday_request == EXPECTED_PAYDAY_REQUEST
