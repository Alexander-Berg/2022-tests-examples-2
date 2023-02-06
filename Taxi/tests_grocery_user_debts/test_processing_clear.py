# pylint: disable=import-error

import datetime

from grocery_mocks.utils import helpers as mock_helpers
import pytest

from . import consts
from . import helpers
from . import models


CUSTOM_DT = consts.NOW_DT + datetime.timedelta(days=1)


@pytest.fixture(name='grocery_user_debts_clear')
def _grocery_user_debts_clear(taxi_grocery_user_debts):
    async def _inner(status_code=200, debt=None, **kwargs):
        response = await taxi_grocery_user_debts.post(
            '/processing/v1/debts/clear',
            json={
                'debt': debt or _make_request_debt(),
                'order': consts.ORDER_INFO,
                **kwargs,
            },
        )

        assert response.status_code == status_code

    return _inner


async def test_debt_collector(
        grocery_user_debts_clear, debt_collector, default_debt,
):
    request_debt = _make_request_debt(debt_id=consts.DEBT_ID)

    debt_collector.by_id.mock_response(version=1)
    debt_collector.update.check(
        id=consts.DEBT_ID,
        service=consts.SERVICE,
        reason=helpers.make_reason(),
        version=1,
        transactions_params=dict(trust_afs_params=dict(force_3ds=False)),
    )

    await grocery_user_debts_clear(debt=request_debt)
    assert debt_collector.update.times_called == 1


async def test_pgsql(grocery_user_debts_clear, grocery_user_debts_db):
    debt = models.Debt(debt_id=consts.DEBT_ID)
    grocery_user_debts_db.upsert(debt)

    await grocery_user_debts_clear()

    updated_debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert updated_debt.status == debt.status
    assert updated_debt.priority == debt.priority


async def test_no_debt(grocery_user_debts_clear):
    await grocery_user_debts_clear(status_code=404)


async def test_strategy_null(
        grocery_user_debts_clear,
        grocery_user_debts_configs,
        debt_collector,
        default_debt,
):
    grocery_user_debts_configs.strategy(value={'type': 'null'})

    debt_collector.update.check(
        collection=dict(strategy=consts.DEBT_NULL_STRATEGY),
    )

    await grocery_user_debts_clear()
    assert debt_collector.update.times_called == 1


@pytest.mark.now(consts.NOW)
async def test_strategy_delta(
        grocery_user_debts_clear,
        grocery_user_debts_configs,
        debt_collector,
        default_debt,
):
    delta_minutes = 5
    grocery_user_debts_configs.strategy(
        value={'type': 'pay_delta', 'minutes': delta_minutes},
    )

    debt_collector.update.check(
        collection=helpers.make_time_table_strategy(
            [consts.NOW_DT + datetime.timedelta(minutes=delta_minutes)],
        ),
    )

    await grocery_user_debts_clear()
    assert debt_collector.update.times_called == 1


@pytest.mark.parametrize('status', ['canceled', 'cleared'])
async def test_handled(
        grocery_user_debts_clear,
        grocery_user_debts_db,
        debt_collector,
        status,
):
    grocery_user_debts_db.upsert(models.Debt(status=status))

    await grocery_user_debts_clear()
    assert debt_collector.update.times_called == 0


@pytest.mark.now(consts.NOW)
async def test_exp_strategy(
        grocery_user_debts_clear,
        grocery_user_debts_configs,
        grocery_user_debts_db,
        experiments3,
):
    request_debt = _make_request_debt()
    reason = request_debt['reason']
    debt_lifetime_days = 2
    debt_lifetime_td = datetime.timedelta(days=debt_lifetime_days, minutes=50)

    debt = models.Debt(
        debt_id=consts.DEBT_ID, created=consts.NOW_DT - debt_lifetime_td,
    )
    grocery_user_debts_db.upsert(debt)

    exp3_recorder = experiments3.record_match_tries('grocery_debts_strategy')

    grocery_user_debts_configs.strategy(value={'type': 'null'})

    await grocery_user_debts_clear(debt=request_debt)

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs
    assert exp3_kwargs['consumer'] == 'grocery-user-debts/strategy'
    assert exp3_kwargs['yandex_uid'] == consts.YANDEX_UID
    assert exp3_kwargs['personal_phone_id'] == consts.PERSONAL_PHONE_ID
    assert exp3_kwargs['country_iso3'] == consts.COUNTRY_ISO3
    assert exp3_kwargs['originator'] == 'grocery'
    assert exp3_kwargs['primary_payment_type'] == reason['payment_type']
    assert exp3_kwargs['error_reason_code'] == reason['error_reason_code']
    assert exp3_kwargs['is_technical_error'] == reason['is_technical_error']
    assert exp3_kwargs['attempt'] == reason['attempt']
    assert exp3_kwargs['debt_lifetime_days'] == debt_lifetime_days


async def test_forgive_debt_collector(
        grocery_user_debts_clear,
        grocery_user_debts_configs,
        debt_collector,
        default_debt,
):
    request_debt = _make_request_debt(debt_id=consts.DEBT_ID)

    grocery_user_debts_configs.forgive(True)

    debt_collector.update.check(
        id=consts.DEBT_ID,
        items_by_payment_type=helpers.to_debt_collector_items([]),
        collection=dict(strategy=consts.DEBT_NULL_STRATEGY),
        service=consts.SERVICE,
        reason=helpers.make_reason('debt_forgive'),
        version=1,
    )

    await grocery_user_debts_clear(debt=request_debt)
    assert debt_collector.update.times_called == 1


async def test_forgive_psql(
        grocery_user_debts_clear,
        grocery_user_debts_configs,
        grocery_user_debts_db,
        default_debt,
):
    grocery_user_debts_configs.forgive(True)

    await grocery_user_debts_clear()

    updated_debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert updated_debt.status == 'forgiven'
    assert updated_debt.priority == default_debt.priority + 1


async def test_processing_name(
        grocery_user_debts_clear,
        grocery_user_debts_configs,
        debt_collector,
        default_debt,
):
    processing_name = 'some processing_name'

    grocery_user_debts_configs.processing_name(processing_name)

    debt_collector.update.check(
        transactions_params=mock_helpers.sub_dict(
            pass_params=dict(
                terminal_route_data=dict(
                    preferred_processing_cc=processing_name,
                ),
            ),
        ),
    )

    await grocery_user_debts_clear()
    assert debt_collector.update.times_called == 1


@pytest.mark.parametrize(
    'request_strategy, expected_strategy',
    [
        pytest.param({'type': 'null'}, {'kind': 'null', 'metadata': {}}),
        pytest.param(
            {'type': 'time_table', 'schedule': [CUSTOM_DT.isoformat()]},
            {
                'kind': 'time_table',
                'metadata': {'schedule': [CUSTOM_DT.isoformat()]},
            },
        ),
        pytest.param(
            {'type': 'now'},
            {'kind': 'time_table', 'metadata': {'schedule': [consts.NOW]}},
        ),
    ],
)
@pytest.mark.now(consts.NOW)
async def test_custom_pay_strategy(
        grocery_user_debts_clear,
        debt_collector,
        default_debt,
        request_strategy,
        expected_strategy,
):
    request_debt = _make_request_debt(
        debt_id=consts.DEBT_ID, strategy=request_strategy,
    )

    debt_collector.by_id.mock_response(version=1)
    debt_collector.update.check(collection=dict(strategy=expected_strategy))

    await grocery_user_debts_clear(debt=request_debt)
    assert debt_collector.update.times_called == 1


def _make_request_debt(*, debt_id=consts.DEBT_ID, **kwargs):
    return {
        'debt_id': debt_id,
        'idempotency_token': consts.DEBT_IDEMPOTENCY_TOKEN,
        'reason_code': consts.DEBT_REASON_CODE,
        'order': consts.ORDER_INFO,
        'reason': models.debt_reason(attempt=0),
        **kwargs,
    }
