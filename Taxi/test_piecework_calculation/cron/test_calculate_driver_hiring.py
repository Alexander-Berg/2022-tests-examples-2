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
            'country': 'ru',
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
    ],
}
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
        ['piecework_calculation.crontasks.calculate_driver_hiring', '-t', '0'],
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
                'tariff_type': 'driver-hiring',
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
                    'min_hour_cost': decimal.Decimal('10.0'),
                    'conversion_ratio': decimal.Decimal('90.0'),
                    'unified_qa_ratio': decimal.Decimal('85.0'),
                    'conversion_rating_weight': decimal.Decimal('0.4'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'hour_cost_rating_weight': decimal.Decimal('0.3'),
                    'workshifts_duration_sec': decimal.Decimal('259200.0'),
                    'unified_qa_rating_weight': decimal.Decimal('0.2'),
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
                    'plan_workshifts_duration_sec': decimal.Decimal(
                        '259200.0',
                    ),
                },
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
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
                    'min_hour_cost': decimal.Decimal('10.0'),
                    'conversion_ratio': decimal.Decimal('62.5'),
                    'unified_qa_ratio': decimal.Decimal('85.5'),
                    'conversion_rating_weight': decimal.Decimal('0.4'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'hour_cost_rating_weight': decimal.Decimal('0.3'),
                    'workshifts_duration_sec': decimal.Decimal('345600.0'),
                    'unified_qa_rating_weight': decimal.Decimal('0.2'),
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
                    'plan_workshifts_duration_sec': decimal.Decimal(
                        '345600.0',
                    ),
                },
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
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
                'tariff_type': 'driver-hiring',
                'calc_type': 'general',
                'calc_subtype': 'sf-oktell',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'login': 'ivanov',
                'daytime_cost': decimal.Decimal('60.0'),
                'night_cost': decimal.Decimal('40.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefit_conditions': {
                    'min_hour_cost': decimal.Decimal('10.0'),
                    'conversion_ratio': decimal.Decimal('90.0'),
                    'unified_qa_ratio': decimal.Decimal('85.0'),
                    'conversion_rating_weight': decimal.Decimal('0.4'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'hour_cost_rating_weight': decimal.Decimal('0.3'),
                    'workshifts_duration_sec': decimal.Decimal('259200.0'),
                    'unified_qa_rating_weight': decimal.Decimal('0.2'),
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
                    'plan_workshifts_duration_sec': decimal.Decimal(
                        '259200.0',
                    ),
                },
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'calc_type': 'general',
                'calc_subtype': 'sf-oktell',
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
                'tariff_type': 'driver-hiring',
                'calc_type': 'general',
                'calc_subtype': 'sf-oktell',
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

        pg_daily_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, tariff_type, calc_type, calc_subtype, '
            'calc_date, login, daytime_cost, night_cost, '
            'holidays_daytime_cost, holidays_night_cost '
            'FROM piecework.calculation_daily_result '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY calc_type, calc_subtype, login, calc_date',
            'periodic_rule_id',
        )
        pg_daily_result = [dict(item) for item in pg_daily_result]
        assert pg_daily_result == [
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'calc_date': datetime.date(2020, 1, 5),
                'login': 'ivanov',
                'daytime_cost': decimal.Decimal('1.8'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'calc_date': datetime.date(2020, 1, 11),
                'login': 'ivanov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'calc_date': datetime.date(2020, 1, 5),
                'login': 'petrov',
                'daytime_cost': decimal.Decimal('8.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'calc_date': datetime.date(2020, 1, 11),
                'login': 'petrov',
                'daytime_cost': decimal.Decimal('1.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'calc_type': 'general',
                'calc_subtype': 'sf-oktell',
                'calc_date': datetime.date(2020, 1, 11),
                'login': 'ivanov',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('40.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'calc_type': 'general',
                'calc_subtype': 'sf-oktell',
                'calc_date': datetime.date(2020, 1, 12),
                'login': 'ivanov',
                'daytime_cost': decimal.Decimal('60.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
            },
        ]

        pg_detail_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, tariff_type, tariff_id, country, calc_type, '
            'calc_subtype, calc_date, login, cost_condition_key, line, '
            'cost_action, daytime_count, night_count, holidays_daytime_count, '
            'holidays_night_count '
            'FROM piecework.calculation_detail WHERE calculation_rule_id = $1 '
            'ORDER BY calc_type, calc_subtype, login, cost_condition_key, '
            'line',
            'periodic_rule_id',
        )
        pg_detail_result = [dict(item) for item in pg_detail_result]
        assert pg_detail_result == [
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'tariff_id': 'ru_tariff_id',
                'country': 'ru',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'calc_date': datetime.date(2020, 1, 5),
                'login': 'ivanov',
                'cost_condition_key': 'close',
                'line': 'first',
                'cost_action': decimal.Decimal('1.0'),
                'daytime_count': 1,
                'night_count': 0,
                'holidays_daytime_count': 0,
                'holidays_night_count': 0,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'tariff_id': 'ru_tariff_id',
                'country': 'ru',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'calc_date': datetime.date(2020, 1, 11),
                'login': 'ivanov',
                'cost_condition_key': 'communicate',
                'line': 'first',
                'cost_action': decimal.Decimal('0.0'),
                'daytime_count': 1,
                'night_count': 0,
                'holidays_daytime_count': 0,
                'holidays_night_count': 0,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'tariff_id': 'ru_tariff_id',
                'country': 'ru',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'calc_date': datetime.date(2020, 1, 5),
                'login': 'ivanov',
                'cost_condition_key': 'forward',
                'line': 'first',
                'cost_action': decimal.Decimal('0.8'),
                'daytime_count': 1,
                'night_count': 0,
                'holidays_daytime_count': 0,
                'holidays_night_count': 0,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'tariff_id': 'ru_tariff_id',
                'country': 'ru',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'calc_date': datetime.date(2020, 1, 11),
                'login': 'petrov',
                'cost_condition_key': 'close',
                'line': 'urgent',
                'cost_action': decimal.Decimal('1.0'),
                'daytime_count': 1,
                'night_count': 0,
                'holidays_daytime_count': 0,
                'holidays_night_count': 0,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'tariff_id': 'ru_tariff_id',
                'country': 'ru',
                'calc_type': 'general',
                'calc_subtype': 'chatterbox',
                'calc_date': datetime.date(2020, 1, 5),
                'login': 'petrov',
                'cost_condition_key': 'smm',
                'line': 'smm',
                'cost_action': decimal.Decimal('8.0'),
                'daytime_count': 1,
                'night_count': 0,
                'holidays_daytime_count': 0,
                'holidays_night_count': 0,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'tariff_id': 'ru_tariff_id',
                'country': 'ru',
                'calc_type': 'general',
                'calc_subtype': 'sf-oktell',
                'calc_date': datetime.date(2020, 1, 11),
                'login': 'ivanov',
                'cost_condition_key': 'sf_oktell_call',
                'line': 'first',
                'cost_action': decimal.Decimal('10.0'),
                'daytime_count': 0,
                'night_count': 4,
                'holidays_daytime_count': 0,
                'holidays_night_count': 0,
            },
            {
                'calculation_rule_id': 'periodic_rule_id',
                'tariff_type': 'driver-hiring',
                'tariff_id': 'ru_tariff_id',
                'country': 'ru',
                'calc_type': 'general',
                'calc_subtype': 'sf-oktell',
                'calc_date': datetime.date(2020, 1, 12),
                'login': 'ivanov',
                'cost_condition_key': 'sf_oktell_call',
                'line': 'second',
                'cost_action': decimal.Decimal('15.0'),
                'daytime_count': 4,
                'night_count': 0,
                'holidays_daytime_count': 0,
                'holidays_night_count': 0,
            },
        ]


@pytest.mark.now('2019-12-20T10:00:00')
async def test_no_calculate(cron_context):
    await run_cron.main(
        ['piecework_calculation.crontasks.calculate_driver_hiring', '-t', '0'],
    )
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status FROM piecework.calculation_rule '
            'WHERE calculation_rule_id = $1',
            'periodic_rule_id',
        )
        assert pg_result['status'] == 'waiting_agent'
