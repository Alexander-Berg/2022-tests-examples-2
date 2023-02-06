# pylint: disable=redefined-outer-name
import datetime
import decimal

import pytest

from piecework_calculation import support_taxi
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
        'blr': {'ticket_locale': 'ru', 'destination': 'oebs'},
    },
)
async def test_update_benefits(
        cron_context, mock_create_draft, mock_uuid4_list,
):
    mock_uuid4_list()
    await support_taxi.calculate(cron_context)
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
                'benefits': decimal.Decimal('0.00'),
                'benefit_conditions': {
                    'rating': decimal.Decimal('188.0'),
                    'qa_ratio': decimal.Decimal('85.0'),
                    'csat_ratio': decimal.Decimal('90.0'),
                    'rating_pos': decimal.Decimal('2'),
                    'avg_duration': decimal.Decimal('10.0'),
                    'rating_prcnt': decimal.Decimal('100.0'),
                    'min_hour_cost': decimal.Decimal('1.0'),
                    'hour_cost': decimal.Decimal('2.3'),
                    'rating_factor': decimal.Decimal('1.0'),
                    'benefits_per_bo': decimal.Decimal('0.0'),
                    'rating_qa_weight': decimal.Decimal('1.0'),
                    'rating_csat_weight': decimal.Decimal('1.0'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'rating_max_total_cost': decimal.Decimal('30.0'),
                    'workshifts_duration_sec': decimal.Decimal('36000.0'),
                    'rating_total_cost_weight': decimal.Decimal('1.0'),
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
                    'rating_avg_duration_weight': decimal.Decimal('1.0'),
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
                'benefits': decimal.Decimal('19.00'),
                'benefit_conditions': {
                    'rating': decimal.Decimal('205.0'),
                    'qa_ratio': decimal.Decimal('80.0'),
                    'csat_ratio': decimal.Decimal('95.0'),
                    'rating_pos': decimal.Decimal('1'),
                    'rating_prcnt': decimal.Decimal('0.0'),
                    'min_hour_cost': decimal.Decimal('1.0'),
                    'hour_cost': decimal.Decimal('4.0'),
                    'rating_factor': decimal.Decimal('2.0'),
                    'benefits_per_bo': decimal.Decimal('0.5'),
                    'rating_qa_weight': decimal.Decimal('1.0'),
                    'rating_csat_weight': decimal.Decimal('1.0'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'rating_max_total_cost': decimal.Decimal('30.0'),
                    'workshifts_duration_sec': decimal.Decimal('28800.0'),
                    'rating_total_cost_weight': decimal.Decimal('1.0'),
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
                    'qa_ratio': decimal.Decimal('90.0'),
                    'csat_ratio': decimal.Decimal('85.0'),
                    'min_hour_cost': decimal.Decimal('1.0'),
                    'rating_factor': decimal.Decimal('1.0'),
                    'rating_qa_weight': decimal.Decimal('1.0'),
                    'rating_csat_weight': decimal.Decimal('1.0'),
                    'min_workshifts_ratio': decimal.Decimal('0.25'),
                    'rating_max_total_cost': decimal.Decimal('100.0'),
                    'workshifts_duration_sec': decimal.Decimal('7200.0'),
                    'plan_workshifts_duration': decimal.Decimal('36000.0'),
                    'rating_total_cost_weight': decimal.Decimal('1.0'),
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
                    'rating_avg_duration_weight': decimal.Decimal('0.0'),
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
                'tariff_type': 'support-taxi',
                'calculation_rule_id': 'some_rule_id',
                'country': 'rus',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'status': 'failed',
                'approvals_id': 123,
            },
            {
                'tariff_type': 'support-taxi',
                'calculation_rule_id': 'some_rule_id',
                'country': 'blr',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'status': 'need_approval',
                'approvals_id': 1,
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
                'tariff_type': 'support-taxi',
                'calculation_rule_id': 'corrected_rule_id',
                'country': 'rus',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'status': 'need_approval',
                'approvals_id': 1,
            },
            {
                'tariff_type': 'support-taxi',
                'calculation_rule_id': 'corrected_rule_id',
                'country': 'blr',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'status': 'need_approval',
                'approvals_id': 1,
            },
        ]

    create_draft_call = mock_create_draft.next_call()['request'].json
    create_draft_call.pop('request_id')
    next_draft_call = mock_create_draft.next_call()['request'].json
    next_draft_call.pop('request_id')
    assert not mock_create_draft.has_calls

    calls_by_rule_id = {
        create_draft_call['data']['payment'][
            'calculation_rule_id'
        ]: create_draft_call,
        next_draft_call['data']['payment'][
            'calculation_rule_id'
        ]: next_draft_call,
    }
    assert calls_by_rule_id == {
        'some_rule_id': {
            'mode': 'poll',
            'service_name': 'piecework-calculation',
            'api_path': 'v1_payments_support-taxi_process',
            'run_manually': False,
            'data': {
                'payment': {
                    'payment_draft_id': 'uuid_4',
                    'calculation_rule_id': 'some_rule_id',
                    'country': 'blr',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            'tickets': {
                'create_data': {
                    'summary': 'Payment blr per 2020-01-01 - 2020-01-16',
                    'description': (
                        'Country: blr\nPeriod: 2020-01-01 - 2020-01-16'
                    ),
                },
            },
        },
        'corrected_rule_id': {
            'mode': 'poll',
            'service_name': 'piecework-calculation',
            'api_path': 'v1_payments_support-taxi_process',
            'run_manually': False,
            'data': {
                'payment': {
                    'payment_draft_id': 'uuid_7',
                    'calculation_rule_id': 'corrected_rule_id',
                    'country': 'blr',
                    'start_date': '2020-01-01',
                    'stop_date': '2020-01-16',
                },
            },
            'tickets': {
                'create_data': {
                    'summary': 'Payment blr per 2020-01-01 - 2020-01-16',
                    'description': (
                        'Country: blr\nPeriod: 2020-01-01 - 2020-01-16'
                    ),
                },
            },
        },
    }


def _clean_item(item, id_field=None):
    if id_field:
        item.pop(id_field)
    item.pop('created')
    item.pop('updated', None)


def _clean_list_items(items, id_field=None):
    for item in items:
        _clean_item(item, id_field)
