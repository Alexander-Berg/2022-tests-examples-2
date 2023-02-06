# pylint: disable=redefined-outer-name
import datetime
import decimal

import pytest

from piecework_calculation import call_taxi
from piecework_calculation.generated.cron import run_cron

NOW = datetime.datetime(2020, 1, 10, 10, 0)
NOW_PARTIAL_CALL_TAXI = datetime.datetime(2020, 1, 10, 10, 55)
NOW_PARTIAL_SUPPORT = datetime.datetime(2020, 1, 10, 10, 5)
PERIOD_END = datetime.datetime(2020, 1, 18, 10, 0)

AGENT_RESPONSE_OK = {
    'items': [
        {'login': 'ivanova', 'team': 'first', 'country': 'ru'},
        {'login': 'petrova', 'team': 'second', 'country': 'ru'},
        {'login': 'smirnova', 'team': 'second', 'country': 'ru'},
    ],
}


@pytest.fixture
def mock_gp_with_error(monkeypatch, cron_context):
    def _dummy_get_connection():
        raise RuntimeError

    monkeypatch.setattr(
        cron_context.greenplum, 'get_connection', _dummy_get_connection,
    )


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
    },
)
@pytest.mark.parametrize(
    'expected_payment',
    [
        [
            {
                'calculation_rule_id': 'unified_rule_id',
                'tariff_type': 'call-taxi-unified',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'country': 'ru',
                'login': 'ivanova',
                'branch': 'first',
                'daytime_cost': decimal.Decimal('90.18'),
                'night_cost': decimal.Decimal('24.05'),
                'holidays_daytime_cost': decimal.Decimal('30.06'),
                'holidays_night_cost': decimal.Decimal('24.05'),
                'total_cost': decimal.Decimal('168.34'),
                'benefits': decimal.Decimal('0.000'),
                'correction': (
                    '{"intermediate": {"login": "ivanova", "benefits": "8.0"}}'
                ),
                'benefit_conditions': (
                    '{"rating": 0.0, "qa_ratio": 0.2725, '
                    '"hour_cost": 56.11333333333334, "rating_pos": 1, '
                    '"claim_ratio": 0.6, "rating_prcnt": 0.0, '
                    '"min_hour_cost": 10.0, "benefits_per_bo": 0.0, '
                    '"hour_cost_ratio": 1.0, "discipline_ratio": 0.85, '
                    '"unified_qa_ratio": 0.4035, '
                    '"min_workshifts_ratio": 0.25, '
                    '"hour_cost_rating_weight": 0.1, '
                    '"workshifts_duration_sec": 10800.0, '
                    '"discipline_rating_weight": 0.1, '
                    '"unified_qa_rating_weight": 0.8, '
                    '"benefit_thresholds_strict": ['
                    '{"value": 0.5, "threshold": 0.0}, '
                    '{"value": 0.0, "threshold": 80.0}], '
                    '"plan_workshifts_duration_sec": 864000.0}'
                ),
            },
            {
                'calculation_rule_id': 'unified_rule_id',
                'tariff_type': 'call-taxi-unified',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'country': 'ru',
                'login': 'petrova',
                'branch': 'second',
                'daytime_cost': decimal.Decimal('38.13'),
                'night_cost': decimal.Decimal('3.01'),
                'holidays_daytime_cost': decimal.Decimal('15.05'),
                'holidays_night_cost': decimal.Decimal('18.06'),
                'total_cost': decimal.Decimal('74.25'),
                'benefits': decimal.Decimal('3.0'),
                'correction': (
                    '{"final": {"login": "petrova", "benefits": "3.0"}}'
                ),
                'benefit_conditions': (
                    '{"rating": 0.0, "qa_ratio": 0.246, '
                    '"hour_cost": 37.125, "rating_pos": 1, '
                    '"claim_ratio": 0.0, "rating_prcnt": 0.0, '
                    '"min_hour_cost": 10.0, "benefits_per_bo": 0.0, '
                    '"hour_cost_ratio": 1.0, "discipline_ratio": 0.75, '
                    '"unified_qa_ratio": 0.1476, '
                    '"min_workshifts_ratio": 0.25, '
                    '"hour_cost_rating_weight": 0.1, '
                    '"workshifts_duration_sec": 7200.0, '
                    '"discipline_rating_weight": 0.1, '
                    '"unified_qa_rating_weight": 0.8, '
                    '"benefit_thresholds_strict": ['
                    '{"value": 0.5, "threshold": 0.0}, '
                    '{"value": 0.0, "threshold": 80.0}], '
                    '"plan_workshifts_duration_sec": 0.0}'
                ),
            },
            {
                'calculation_rule_id': 'unified_rule_id',
                'tariff_type': 'call-taxi-unified',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'country': 'ru',
                'login': 'smirnova',
                'branch': 'second',
                'daytime_cost': decimal.Decimal('0.0'),
                'night_cost': decimal.Decimal('0.0'),
                'holidays_daytime_cost': decimal.Decimal('0.0'),
                'holidays_night_cost': decimal.Decimal('0.0'),
                'total_cost': decimal.Decimal('0.0'),
                'benefits': decimal.Decimal('0.0'),
                'correction': None,
                'benefit_conditions': None,
            },
        ],
    ],
)
async def test_restart_partial(
        cron_context, expected_payment, mock_uuid4_list, mock_agent_employees,
):
    mock_agent_employees(AGENT_RESPONSE_OK)
    mock_uuid4_list()
    await call_taxi.calculate(cron_context)
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status, description '
            'FROM piecework.calculation_rule '
            'WHERE calculation_rule_id = $1',
            'unified_rule_id',
        )
        assert pg_result['status'] == 'success_partial_period'
        assert pg_result['description']

        pg_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, tariff_type, start_date, stop_date, country,'
            'login, branch, daytime_cost, night_cost, holidays_daytime_cost, '
            'holidays_night_cost, total_cost, benefits, correction, '
            'benefit_conditions '
            'FROM piecework.payment '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY login',
            'unified_rule_id',
        )
        pg_result = [dict(item) for item in pg_result]
        assert pg_result == expected_payment

        pg_result = await conn.fetch(
            'SELECT tariff_type, calculation_rule_id, country, start_date, '
            'stop_date, status, approvals_id '
            'FROM piecework.payment_draft '
            'WHERE calculation_rule_id = $1 '
            'ORDER BY status DESC',
            'unified_rule_id',
        )
        assert pg_result == []


@pytest.mark.now(PERIOD_END.isoformat())
@pytest.mark.config(
    PIECEWORK_CALCULATION_PAYMENT_SETTINGS={
        'ru': {'ticket_locale': 'ru', 'destination': 'oebs'},
    },
)
async def test_finalize(
        cron_context,
        mock_create_draft,
        mock_uuid4_list,
        mock_agent_employees,
        mock_oebs_holidays,
):
    mock_agent_employees(AGENT_RESPONSE_OK)
    mock_uuid4_list()
    await call_taxi.calculate(cron_context)
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status, description '
            'FROM piecework.calculation_rule '
            'WHERE calculation_rule_id = $1',
            'unified_rule_id',
        )
        assert pg_result['status'] == 'success'
        assert pg_result['description']

    assert mock_create_draft.has_calls


@pytest.mark.now(NOW.isoformat())
async def test_unhandled_error(
        cron_context,
        mock_gp_with_error,
        mock_uuid4_list,
        mock_agent_employees,
        mock_oebs_holidays,
):
    mock_agent_employees(AGENT_RESPONSE_OK)
    mock_uuid4_list()
    with pytest.raises(RuntimeError):
        await call_taxi.calculate(cron_context)
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status, description '
            'FROM piecework.calculation_rule '
            'WHERE calculation_rule_id = $1',
            'unified_rule_id',
        )
        assert pg_result['status'] == 'waiting_restart'
        assert pg_result['description']


@pytest.mark.now(NOW_PARTIAL_CALL_TAXI.isoformat())
@pytest.mark.config(PIECEWORK_CALCULATION_YT_CHUNK_SIZE=2)
async def test_crontask(cron_context):
    await run_cron.main(
        ['piecework_calculation.crontasks.restart_partial', '-t', '0'],
    )
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status, description '
            'FROM piecework.calculation_rule '
            'WHERE calculation_rule_id = $1',
            'partial_rule_id',
        )
        assert pg_result['status'] == 'waiting_restart'


@pytest.mark.now(NOW_PARTIAL_SUPPORT.isoformat())
@pytest.mark.config(PIECEWORK_CALCULATION_YT_CHUNK_SIZE=2)
async def test_crontask_support(cron_context):
    await run_cron.main(
        ['piecework_calculation.crontasks.restart_partial', '-t', '0'],
    )
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT status, description '
            'FROM piecework.calculation_rule '
            'WHERE calculation_rule_id = $1',
            'partial_rule_id_support',
        )
        assert pg_result['status'] == 'waiting_restart'
