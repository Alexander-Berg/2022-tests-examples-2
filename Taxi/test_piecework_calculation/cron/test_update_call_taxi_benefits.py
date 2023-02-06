# pylint: disable=redefined-outer-name
import datetime
import decimal

import pytest

from piecework_calculation import call_taxi
from piecework_calculation import cargo_callcenter

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
        'ru': {'ticket_locale': 'ru', 'destination': 'oebs'},
        'by': {'ticket_locale': 'ru', 'destination': 'oebs', 'skip': True},
    },
)
@pytest.mark.parametrize(
    'rule_id, calculate_func, expected_payment, expected_drafts, '
    'expected_draft_call',
    [
        (
            'unified_rule_id',
            call_taxi.calculate,
            [
                {
                    'calculation_rule_id': 'unified_rule_id',
                    'tariff_type': 'call-taxi-unified',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'country': 'ru',
                    'login': 'ivanova',
                    'branch': 'first',
                    'daytime_cost': decimal.Decimal('7.0'),
                    'night_cost': decimal.Decimal('2.0'),
                    'holidays_daytime_cost': decimal.Decimal('5.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'total_cost': decimal.Decimal('14.0'),
                    'benefits': decimal.Decimal('0.0'),
                    'correction': (
                        '{'
                        '"intermediate": {'
                        '"login": "ivanova", "benefits": "8.0"'
                        '}'
                        '}'
                    ),
                    'benefit_conditions': (
                        '{'
                        '"rating": 0.71, '
                        '"hour_cost": 14.0, '
                        '"rating_pos": 2, '
                        '"rating_prcnt": 100.0, '
                        '"min_hour_cost": 10.0, '
                        '"benefits_per_bo": 0.0, '
                        '"hour_cost_ratio": 0.0, '
                        '"discipline_ratio": 0.7, '
                        '"unified_qa_ratio": 0.8, '
                        '"min_workshifts_ratio": 0.25, '
                        '"hour_cost_rating_weight": 0.1, '
                        '"workshifts_duration_sec": 3600.0, '
                        '"discipline_rating_weight": 0.1, '
                        '"unified_qa_rating_weight": 0.8, '
                        '"benefit_thresholds_strict": ['
                        '{"value": 0.5, "threshold": 0.0}, '
                        '{"value": 0.0, "threshold": 80.0}'
                        '], '
                        '"plan_workshifts_duration_sec": 7200.0'
                        '}'
                    ),
                },
                {
                    'calculation_rule_id': 'unified_rule_id',
                    'tariff_type': 'call-taxi-unified',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'country': 'ru',
                    'login': 'petrova',
                    'branch': 'first',
                    'daytime_cost': decimal.Decimal('15.0'),
                    'night_cost': decimal.Decimal('7.0'),
                    'holidays_daytime_cost': decimal.Decimal('10.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'total_cost': decimal.Decimal('32.0'),
                    'benefits': decimal.Decimal('19.0'),
                    'correction': (
                        '{"final": {"login": "petrova", "benefits": "3.0"}}'
                    ),
                    'benefit_conditions': (
                        '{'
                        '"rating": 0.88, '
                        '"hour_cost": 16.0, '
                        '"rating_pos": 1, '
                        '"rating_prcnt": 0.0, '
                        '"min_hour_cost": 10.0, '
                        '"benefits_per_bo": 0.5, '
                        '"hour_cost_ratio": 1.0, '
                        '"discipline_ratio": 0.6, '
                        '"unified_qa_ratio": 0.9, '
                        '"min_workshifts_ratio": 0.25, '
                        '"hour_cost_rating_weight": 0.1, '
                        '"workshifts_duration_sec": 7200.0, '
                        '"discipline_rating_weight": 0.1, '
                        '"unified_qa_rating_weight": 0.8, '
                        '"benefit_thresholds_strict": ['
                        '{"value": 0.5, "threshold": 0.0}, '
                        '{"value": 0.0, "threshold": 80.0}'
                        '], '
                        '"plan_workshifts_duration_sec": 7200.0'
                        '}'
                    ),
                },
                {
                    'calculation_rule_id': 'unified_rule_id',
                    'tariff_type': 'call-taxi-unified',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'country': 'ru',
                    'login': 'popova',
                    'branch': 'first',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'total_cost': decimal.Decimal('0.0'),
                    'benefits': decimal.Decimal('0.0'),
                    'correction': None,
                    'benefit_conditions': (
                        '{'
                        '"min_hour_cost": 10.0, '
                        '"discipline_ratio": 0.8, '
                        '"unified_qa_ratio": 0.7, '
                        '"min_workshifts_ratio": 0.25, '
                        '"hour_cost_rating_weight": 0.1, '
                        '"workshifts_duration_sec": 0, '
                        '"discipline_rating_weight": 0.1, '
                        '"unified_qa_rating_weight": 0.8, '
                        '"benefit_thresholds_strict": ['
                        '{"value": '
                        '0.5, "threshold": 0}, '
                        '{"value": 0.0, "threshold": 80}'
                        '], '
                        '"plan_workshifts_duration_sec": 7200'
                        '}'
                    ),
                },
                {
                    'calculation_rule_id': 'unified_rule_id',
                    'tariff_type': 'call-taxi-unified',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'country': 'ru',
                    'login': 'smirnova',
                    'branch': 'first',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'total_cost': decimal.Decimal('0.0'),
                    'benefits': decimal.Decimal('0.0'),
                    'correction': None,
                    'benefit_conditions': (
                        '{'
                        '"min_hour_cost": 10.0, '
                        '"discipline_ratio": 0.8, '
                        '"unified_qa_ratio": 0.7, '
                        '"min_workshifts_ratio": 0.25, '
                        '"hour_cost_rating_weight": 0.1, '
                        '"workshifts_duration_sec": 100, '
                        '"discipline_rating_weight": 0.1, '
                        '"unified_qa_rating_weight": 0.8, '
                        '"benefit_thresholds_strict": ['
                        '{"value": 0.5, "threshold": 0}, '
                        '{"value": 0.0, "threshold": 80}'
                        '], '
                        '"plan_workshifts_duration_sec": 7200'
                        '}'
                    ),
                },
            ],
            [
                {
                    'tariff_type': 'call-taxi-unified',
                    'calculation_rule_id': 'unified_rule_id',
                    'country': 'ru',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'status': 'need_approval',
                    'approvals_id': 1,
                },
            ],
            {
                'mode': 'poll',
                'service_name': 'piecework-calculation',
                'api_path': 'v1_payments_call-taxi-unified_process',
                'run_manually': False,
                'data': {
                    'payment': {
                        'payment_draft_id': 'uuid_5',
                        'calculation_rule_id': 'unified_rule_id',
                        'country': 'ru',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                    },
                },
                'tickets': {
                    'create_data': {
                        'summary': 'Payment ru per 2020-01-01 - 2020-01-16',
                        'description': (
                            'Country: ru\nPeriod: 2020-01-01 - 2020-01-16'
                        ),
                    },
                },
            },
        ),
        (
            'cargo_rule_id',
            cargo_callcenter.calculate,
            [
                {
                    'calculation_rule_id': 'cargo_rule_id',
                    'tariff_type': 'cargo-callcenter',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'country': 'ru',
                    'login': 'ivanova',
                    'branch': 'first',
                    'daytime_cost': decimal.Decimal('7.0'),
                    'night_cost': decimal.Decimal('2.0'),
                    'holidays_daytime_cost': decimal.Decimal('5.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'total_cost': decimal.Decimal('14.0'),
                    'benefits': decimal.Decimal('0.0'),
                    'correction': (
                        '{'
                        '"intermediate": {'
                        '"login": "ivanova", "benefits": "8.0"'
                        '}'
                        '}'
                    ),
                    'benefit_conditions': (
                        '{'
                        '"rating": 0.71, '
                        '"hour_cost": 14.0, '
                        '"rating_pos": 2, '
                        '"rating_prcnt": 100.0, '
                        '"min_hour_cost": 10.0, '
                        '"benefits_per_bo": 0.0, '
                        '"hour_cost_ratio": 0.0, '
                        '"discipline_ratio": 0.7, '
                        '"unified_qa_ratio": 0.8, '
                        '"min_workshifts_ratio": 0.25, '
                        '"hour_cost_rating_weight": 0.1, '
                        '"workshifts_duration_sec": 3600.0, '
                        '"discipline_rating_weight": 0.1, '
                        '"unified_qa_rating_weight": 0.8, '
                        '"benefit_thresholds_strict": ['
                        '{"value": 0.5, "threshold": 0.0}, '
                        '{"value": 0.0, "threshold": 80.0}'
                        '], '
                        '"plan_workshifts_duration_sec": 7200.0'
                        '}'
                    ),
                },
                {
                    'calculation_rule_id': 'cargo_rule_id',
                    'tariff_type': 'cargo-callcenter',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'country': 'ru',
                    'login': 'petrova',
                    'branch': 'first',
                    'daytime_cost': decimal.Decimal('15.0'),
                    'night_cost': decimal.Decimal('7.0'),
                    'holidays_daytime_cost': decimal.Decimal('10.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'total_cost': decimal.Decimal('32.0'),
                    'benefits': decimal.Decimal('19.0'),
                    'correction': (
                        '{"final": {"login": "petrova", "benefits": "3.0"}}'
                    ),
                    'benefit_conditions': (
                        '{'
                        '"rating": 0.88, '
                        '"hour_cost": 16.0, '
                        '"rating_pos": 1, '
                        '"rating_prcnt": 0.0, '
                        '"min_hour_cost": 10.0, '
                        '"benefits_per_bo": 0.5, '
                        '"hour_cost_ratio": 1.0, '
                        '"discipline_ratio": 0.6, '
                        '"unified_qa_ratio": 0.9, '
                        '"min_workshifts_ratio": 0.25, '
                        '"hour_cost_rating_weight": 0.1, '
                        '"workshifts_duration_sec": 7200.0, '
                        '"discipline_rating_weight": 0.1, '
                        '"unified_qa_rating_weight": 0.8, '
                        '"benefit_thresholds_strict": ['
                        '{"value": 0.5, "threshold": 0.0}, '
                        '{"value": 0.0, "threshold": 80.0}'
                        '], '
                        '"plan_workshifts_duration_sec": 7200.0'
                        '}'
                    ),
                },
                {
                    'calculation_rule_id': 'cargo_rule_id',
                    'tariff_type': 'cargo-callcenter',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'country': 'ru',
                    'login': 'smirnova',
                    'branch': 'first',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'total_cost': decimal.Decimal('0.0'),
                    'benefits': decimal.Decimal('0.0'),
                    'correction': None,
                    'benefit_conditions': (
                        '{'
                        '"min_hour_cost": 10.0, '
                        '"discipline_ratio": 0.8, '
                        '"unified_qa_ratio": 0.7, '
                        '"min_workshifts_ratio": 0.25, '
                        '"hour_cost_rating_weight": 0.1, '
                        '"workshifts_duration_sec": 100, '
                        '"discipline_rating_weight": 0.1, '
                        '"unified_qa_rating_weight": 0.8, '
                        '"benefit_thresholds_strict": ['
                        '{"value": 0.5, "threshold": 0}, '
                        '{"value": 0.0, "threshold": 80}'
                        '], '
                        '"plan_workshifts_duration_sec": 7200'
                        '}'
                    ),
                },
            ],
            [
                {
                    'tariff_type': 'cargo-callcenter',
                    'calculation_rule_id': 'cargo_rule_id',
                    'country': 'ru',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'status': 'need_approval',
                    'approvals_id': 1,
                },
            ],
            {
                'mode': 'poll',
                'service_name': 'piecework-calculation',
                'api_path': 'v1_payments_cargo-callcenter_process',
                'run_manually': False,
                'data': {
                    'payment': {
                        'payment_draft_id': 'uuid_4',
                        'calculation_rule_id': 'cargo_rule_id',
                        'country': 'ru',
                        'start_date': '2020-01-01',
                        'stop_date': '2020-01-16',
                    },
                },
                'tickets': {
                    'create_data': {
                        'summary': 'Payment ru per 2020-01-01 - 2020-01-16',
                        'description': (
                            'Country: ru\nPeriod: 2020-01-01 - 2020-01-16'
                        ),
                    },
                },
            },
        ),
    ],
)
async def test_update_call_taxi_benefits(
        cron_context,
        mock_create_draft,
        rule_id,
        calculate_func,
        expected_payment,
        expected_drafts,
        expected_draft_call,
        mock_uuid4_list,
):
    mock_uuid4_list()
    await calculate_func(cron_context)
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status, description '
            'FROM piecework.calculation_rule '
            'WHERE calculation_rule_id = $1',
            rule_id,
        )
        assert pg_result['status'] == 'success'
        assert pg_result['description']

        pg_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, tariff_type, start_date, stop_date, country,'
            'login, branch, daytime_cost, night_cost, holidays_daytime_cost, '
            'holidays_night_cost, total_cost, benefits, correction, '
            'benefit_conditions '
            'FROM piecework.payment '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY calculation_rule_id DESC, login',
            rule_id,
        )
        pg_result = [dict(item) for item in pg_result]
        assert pg_result == expected_payment

        pg_result = await conn.fetch(
            'SELECT tariff_type, calculation_rule_id, country, start_date, '
            'stop_date, status, approvals_id '
            'FROM piecework.payment_draft '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY status DESC, calculation_rule_id DESC',
            rule_id,
        )
        pg_result = [dict(item) for item in pg_result]
        assert pg_result == expected_drafts

    draft_call = mock_create_draft.next_call()['request'].json
    draft_call.pop('request_id')
    assert draft_call == expected_draft_call
    assert not mock_create_draft.has_calls
