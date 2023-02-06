# pylint: disable=redefined-outer-name
import datetime
import decimal

import pytest

from piecework_calculation import driver_hiring
from piecework_calculation import utils

NOW = datetime.datetime(2020, 1, 18, 10, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations(
    piecework={
        'payment_ticket.summary': {
            'ru': 'Payment {country} per {start_date} - {stop_date}',
        },
        'payment_ticket.description': {
            'ru': 'Country: {country}\nPeriod: {start_date} - {stop_date}',
        },
    },
)
@pytest.mark.config(
    PIECEWORK_CALCULATION_PAYMENT_SETTINGS={
        'rus': {'ticket_locale': 'ru', 'destination': 'oebs'},
        'blr': {'ticket_locale': 'ru', 'destination': 'oebs', 'skip': True},
    },
)
async def test_update_benefits(cron_context, mock_uuid4_list):
    mock_uuid4_list()
    await driver_hiring.calculate(cron_context)
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status, description '
            'FROM piecework.calculation_rule WHERE calculation_rule_id = $1',
            'some_rule_id',
        )
        assert pg_result['status'] == 'success'
        assert pg_result['description']

        pg_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, start_date, stop_date, country, login, '
            'branch, daytime_cost, night_cost, holidays_daytime_cost, '
            'holidays_night_cost, benefits, benefit_conditions '
            'FROM piecework.payment WHERE calculation_rule_id = $1',
            'some_rule_id',
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
                'calculation_rule_id': 'some_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'country': 'rus',
                'login': 'ivanov',
                'branch': 'general',
                'daytime_cost': decimal.Decimal('10.0'),
                'night_cost': decimal.Decimal('5.0'),
                'holidays_daytime_cost': decimal.Decimal('8.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefits': decimal.Decimal('11.50'),
                'benefit_conditions': {
                    'rating': decimal.Decimal('52.0'),
                    'hour_cost': decimal.Decimal('2.3'),
                    'rating_pos': decimal.Decimal('1'),
                    'rating_prcnt': decimal.Decimal('0.0'),
                    'min_hour_cost': decimal.Decimal('1.0'),
                    'benefits_per_bo': decimal.Decimal('0.5'),
                    'hour_cost_ratio': decimal.Decimal('0.0'),
                    'conversion_ratio': decimal.Decimal('90.0'),
                    'unified_qa_ratio': decimal.Decimal('85.0'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'hour_cost_rating_weight': decimal.Decimal('0.3'),
                    'workshifts_duration_sec': decimal.Decimal('36000.0'),
                    'conversion_rating_weight': decimal.Decimal('0.2'),
                    'unified_qa_rating_weight': decimal.Decimal('0.4'),
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
                    'plan_workshifts_duration_sec': decimal.Decimal('36000.0'),
                },
            },
            {
                'calculation_rule_id': 'some_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'country': 'blr',
                'login': 'petrov',
                'branch': 'general',
                'daytime_cost': decimal.Decimal('15.0'),
                'night_cost': decimal.Decimal('10.0'),
                'holidays_daytime_cost': decimal.Decimal('13.0'),
                'holidays_night_cost': decimal.Decimal('3.0'),
                'benefits': decimal.Decimal('3.00'),
                'benefit_conditions': {
                    'rating': decimal.Decimal('45.3'),
                    'hour_cost': decimal.Decimal('4.0'),
                    'rating_pos': decimal.Decimal('2'),
                    'rating_prcnt': decimal.Decimal('100.0'),
                    'min_hour_cost': decimal.Decimal('1.0'),
                    'benefits_per_bo': decimal.Decimal('0.0'),
                    'hour_cost_ratio': decimal.Decimal('1.0'),
                    'conversion_ratio': decimal.Decimal('65.0'),
                    'unified_qa_ratio': decimal.Decimal('80.0'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'hour_cost_rating_weight': decimal.Decimal('0.3'),
                    'workshifts_duration_sec': decimal.Decimal('28800.0'),
                    'conversion_rating_weight': decimal.Decimal('0.2'),
                    'unified_qa_rating_weight': decimal.Decimal('0.4'),
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
                    'plan_workshifts_duration_sec': decimal.Decimal('36000.0'),
                },
            },
            {
                'calculation_rule_id': 'some_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'country': 'rus',
                'login': 'smirnoff',
                'branch': 'general',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'benefits': decimal.Decimal('0.0'),
                'benefit_conditions': {
                    'min_hour_cost': decimal.Decimal('1.0'),
                    'conversion_ratio': decimal.Decimal('95.0'),
                    'unified_qa_ratio': decimal.Decimal('90.0'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'hour_cost_rating_weight': decimal.Decimal('0.3'),
                    'workshifts_duration_sec': decimal.Decimal('7200.0'),
                    'conversion_rating_weight': decimal.Decimal('0.2'),
                    'unified_qa_rating_weight': decimal.Decimal('0.4'),
                    'benefit_thresholds_strict': [
                        {
                            'value': decimal.Decimal('0.5'),
                            'threshold': decimal.Decimal('0'),
                        },
                        {
                            'value': decimal.Decimal('0.0'),
                            'threshold': decimal.Decimal('80'),
                        },
                    ],
                    'plan_workshifts_duration_sec': decimal.Decimal('36000.0'),
                },
            },
        ]

        pg_result = await conn.fetch(
            'SELECT tariff_type, calculation_rule_id, country, start_date, '
            'stop_date, status, approvals_id '
            'FROM piecework.payment_draft WHERE calculation_rule_id = $1 '
            'ORDER BY status DESC',
            'some_rule_id',
        )
        pg_result = [dict(item) for item in pg_result]
        assert pg_result == [
            {
                'tariff_type': 'driver-hiring',
                'calculation_rule_id': 'some_rule_id',
                'country': 'rus',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'status': 'failed',
                'approvals_id': 123,
            },
        ]

        pg_result = await conn.fetchrow(
            'SELECT status, description '
            'FROM piecework.calculation_rule WHERE calculation_rule_id = $1',
            'corrected_rule_id',
        )
        assert pg_result['status'] == 'success'
        assert pg_result['description']

        pg_result = await conn.fetch(
            'SELECT tariff_type, calculation_rule_id, country, start_date, '
            'stop_date, status, approvals_id '
            'FROM piecework.payment_draft WHERE calculation_rule_id = $1',
            'corrected_rule_id',
        )
        pg_result = [dict(item) for item in pg_result]
        assert pg_result == [
            {
                'tariff_type': 'driver-hiring',
                'calculation_rule_id': 'corrected_rule_id',
                'country': 'rus',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'status': 'need_approval',
                'approvals_id': 1,
            },
        ]


def _clean_item(item, id_field=None):
    if id_field:
        item.pop(id_field)
    item.pop('created')
    item.pop('updated', None)


def _clean_list_items(items, id_field=None):
    for item in items:
        _clean_item(item, id_field)
