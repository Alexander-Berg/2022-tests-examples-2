# pylint: disable=redefined-outer-name
import datetime
import decimal

import pytest

from piecework_calculation import utils
from piecework_calculation.generated.cron import run_cron

NOW = datetime.datetime(2020, 1, 18, 10, 0)
AGENT_EMPLOYEES = {
    'items': [
        {
            'country': 'ru',
            'login': 'ivanov',
            'half_time': False,
            'team': 'general',
        },
        {
            'country': 'md',
            'login': 'petrov',
            'half_time': True,
            'team': 'other',
        },
        {
            'country': 'ru',
            'login': 'smirnoff',
            'half_time': False,
            'team': 'general',
        },
        {
            'country': 'ru',
            'login': 'popov',
            'half_time': False,
            'team': 'general',
        },
    ],
}
EXPECTED_AGENT_EMPLOYEES = [
    {
        'country': 'ru',
        'login': 'ivanov',
        'timezone': 'Europe/Moscow',
        'position_name': 'head_of_support_department',
        'rating_factor': 1,
        'branch': 'general',
    },
    {
        'country': 'md',
        'login': 'petrov',
        'timezone': 'Europe/Kiev',
        'position_name': 'support',
        'rating_factor': 2,
        'branch': 'other',
    },
    {
        'country': 'ru',
        'login': 'popov',
        'timezone': 'Europe/Moscow',
        'position_name': 'support',
        'rating_factor': 1,
        'branch': 'general',
    },
    {
        'country': 'ru',
        'login': 'smirnoff',
        'timezone': 'Europe/Volgograd',
        'position_name': 'support',
        'rating_factor': 1,
        'branch': 'general',
    },
]
OEBS_HOLIDAYS = {
    'logins': [
        {
            'login': 'ivanov',
            'holiday': [
                '2020-01-01',
                '2020-01-02',
                '2020-01-03',
                '2020-01-04',
                '2020-01-05',
                '2020-01-06',
                '2020-01-07',
            ],
        },
        {
            'login': 'petrov',
            'holiday': ['2020-01-01', '2020-01-02', '2020-01-07'],
        },
    ],
}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations(
    piecework={
        'payment_ticket.summary': {
            'ru': 'Payment {country} per {start_date} - ' '{stop_date}',
        },
        'payment_ticket.description': {
            'ru': 'Country: {country}\nPeriod: {start_date} - {stop_date}',
        },
    },
)
@pytest.mark.config(
    PIECEWORK_CALCULATION_PAYMENT_SETTINGS={
        'ru': {'ticket_locale': 'ru', 'destination': 'oebs'},
        'md': {'ticket_locale': 'md', 'destination': 'oebs'},
    },
    PIECEWORK_CALCULATION_EATS_SUPPORT_BRANCHES=['general', 'other'],
    PIECEWORK_CALCULATION_YT_CHUNK_SIZE=2,
)
async def test_calculate(
        cron_context,
        mock_create_draft,
        mock_agent_employees,
        mock_oebs_holidays,
):
    mock_oebs_holidays(OEBS_HOLIDAYS)
    mock_agent_employees(AGENT_EMPLOYEES)
    await run_cron.main(
        ['piecework_calculation.crontasks.calculate_eats', '-t', '0'],
    )
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status, description '
            'FROM piecework.calculation_rule WHERE calculation_rule_id = $1',
            'periodic_rule_id',
        )
        assert pg_result['status'] == 'success'
        assert pg_result['description']

    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, tariff_type, calc_type, calc_subtype, '
            'start_date, stop_date, login, daytime_cost, night_cost, '
            'holidays_daytime_cost, holidays_night_cost, benefit_conditions '
            'FROM piecework.calculation_result WHERE calculation_rule_id = $1 '
            'ORDER BY calc_type, calc_subtype, login',
            'periodic_rule_id',
        )
        pg_result = [dict(item) for item in pg_result]
        for item in pg_result:
            if item['benefit_conditions'] is None:
                continue
            item['benefit_conditions'] = utils.from_json(
                item['benefit_conditions'],
            )
        assert pg_result == [
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'ivanov',
                'daytime_cost': decimal.Decimal('1.8'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': {
                    'qa_ratio': decimal.Decimal('85.0'),
                    'csat_ratio': decimal.Decimal('95.0'),
                    'avg_duration': None,
                    'min_hour_cost': decimal.Decimal('10.0'),
                    'rating_factor': decimal.Decimal('1.0'),
                    'rating_qa_weight': decimal.Decimal('0.49875'),
                    'rating_csat_weight': decimal.Decimal('0.49875'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'rating_max_total_cost': decimal.Decimal('11000.0'),
                    'workshifts_duration_sec': decimal.Decimal('259200.0'),
                    'rating_total_cost_weight': decimal.Decimal('0.0025'),
                    'benefit_thresholds_strict': [
                        {
                            'value': decimal.Decimal('0.5'),
                            'threshold': decimal.Decimal('0.0'),
                        },
                        {
                            'value': decimal.Decimal('0.0'),
                            'threshold': decimal.Decimal('80.0'),
                        },
                    ],
                    'rating_avg_duration_weight': decimal.Decimal('0.0'),
                    'plan_workshifts_duration_sec': decimal.Decimal(
                        '259200.0',
                    ),
                },
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'petrov',
                'daytime_cost': decimal.Decimal('9.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': {
                    'qa_ratio': decimal.Decimal('85.5'),
                    'csat_ratio': decimal.Decimal('96.0'),
                    'avg_duration': None,
                    'min_hour_cost': decimal.Decimal('10.0'),
                    'rating_factor': decimal.Decimal('2.0'),
                    'rating_qa_weight': decimal.Decimal('0.49875'),
                    'rating_csat_weight': decimal.Decimal('0.49875'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'rating_max_total_cost': decimal.Decimal('11000.0'),
                    'workshifts_duration_sec': decimal.Decimal('345600.0'),
                    'rating_total_cost_weight': decimal.Decimal('0.0025'),
                    'benefit_thresholds_strict': [
                        {
                            'value': decimal.Decimal('0.5'),
                            'threshold': decimal.Decimal('0.0'),
                        },
                        {
                            'value': decimal.Decimal('0.0'),
                            'threshold': decimal.Decimal('80.0'),
                        },
                    ],
                    'rating_avg_duration_weight': decimal.Decimal('0.0'),
                    'plan_workshifts_duration_sec': decimal.Decimal(
                        '345600.0',
                    ),
                },
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'popov',
                'daytime_cost': decimal.Decimal('1.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': {
                    'avg_duration': None,
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
                    'csat_ratio': decimal.Decimal('0'),
                    'min_hour_cost': decimal.Decimal('10.0'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'plan_workshifts_duration_sec': decimal.Decimal('0'),
                    'qa_ratio': decimal.Decimal('0'),
                    'rating_avg_duration_weight': decimal.Decimal('0.0'),
                    'rating_csat_weight': decimal.Decimal('0.49875'),
                    'rating_factor': decimal.Decimal('1.0'),
                    'rating_max_total_cost': decimal.Decimal('11000.0'),
                    'rating_qa_weight': decimal.Decimal('0.49875'),
                    'rating_total_cost_weight': decimal.Decimal('0.0025'),
                    'workshifts_duration_sec': decimal.Decimal('0'),
                },
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'smirnoff',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'new_tel',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'ivanov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'new_tel',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'petrov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'new_tel',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'popov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'new_tel',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'smirnoff',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'call-oktell',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'ivanov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'call-oktell',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'petrov',
                'daytime_cost': decimal.Decimal('15.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': {
                    'qa_ratio': decimal.Decimal('85.5'),
                    'csat_ratio': decimal.Decimal('96.0'),
                    'avg_duration': decimal.Decimal('9.0'),
                    'min_hour_cost': decimal.Decimal('10.0'),
                    'rating_factor': decimal.Decimal('2.0'),
                    'rating_qa_weight': decimal.Decimal('0.49875'),
                    'rating_csat_weight': decimal.Decimal('0.49875'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'rating_max_total_cost': decimal.Decimal('11000.0'),
                    'workshifts_duration_sec': decimal.Decimal('345600.0'),
                    'rating_total_cost_weight': decimal.Decimal('0.0025'),
                    'benefit_thresholds_strict': [
                        {
                            'value': decimal.Decimal('0.5'),
                            'threshold': decimal.Decimal('0.0'),
                        },
                        {
                            'value': decimal.Decimal('0.0'),
                            'threshold': decimal.Decimal('80.0'),
                        },
                    ],
                    'rating_avg_duration_weight': decimal.Decimal('0.0'),
                    'plan_workshifts_duration_sec': decimal.Decimal(
                        '345600.0',
                    ),
                },
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'call-oktell',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'popov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'call-oktell',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'smirnoff',
                'daytime_cost': decimal.Decimal('5.5'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': {
                    'qa_ratio': decimal.Decimal('0'),
                    'csat_ratio': decimal.Decimal('0'),
                    'avg_duration': decimal.Decimal('5.0'),
                    'min_hour_cost': decimal.Decimal('10.0'),
                    'rating_factor': decimal.Decimal('1.0'),
                    'rating_qa_weight': decimal.Decimal('0.49875'),
                    'rating_csat_weight': decimal.Decimal('0.49875'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'rating_max_total_cost': decimal.Decimal('11000.0'),
                    'workshifts_duration_sec': decimal.Decimal('0'),
                    'rating_total_cost_weight': decimal.Decimal('0.0025'),
                    'benefit_thresholds_strict': [
                        {
                            'value': decimal.Decimal('0.5'),
                            'threshold': decimal.Decimal('0.0'),
                        },
                        {
                            'value': decimal.Decimal('0.0'),
                            'threshold': decimal.Decimal('80.0'),
                        },
                    ],
                    'rating_avg_duration_weight': decimal.Decimal('0.0'),
                    'plan_workshifts_duration_sec': decimal.Decimal('0'),
                },
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox_calls',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'ivanov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox_calls',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'petrov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox_calls',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'popov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'support-eats',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox_calls',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'smirnoff',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': None,
            },
        ]


@pytest.mark.now('2019-12-20T10:00:00')
async def test_no_calculate(cron_context):
    await run_cron.main(
        ['piecework_calculation.crontasks.calculate_eats', '-t', '0'],
    )
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status FROM piecework.calculation_rule '
            'WHERE calculation_rule_id = $1',
            'periodic_rule_id',
        )
        assert pg_result['status'] == 'waiting_agent'
