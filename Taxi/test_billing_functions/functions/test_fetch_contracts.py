import datetime as dt

import pytest

from billing_models.generated import models

from billing_functions.functions import fetch_contracts
from test_billing_functions import equatable
from test_billing_functions import mocks


@pytest.mark.parametrize(
    'test_data_json',
    [
        'no_contracts.json',
        'no_billing_client_id.json',
        'has_cargo_contracts.json',
        'no_billing_zone.json',
        'no_billing_zone_but_billing_client_id.json',
        'marketing_contract_not_required.json',
        'marketing_contract_timeout.json',
        'pending_marketing_contract.json',
        'payout_via_yandex_bank.json',
    ],
)
@pytest.mark.json_obj_hook(
    Query=fetch_contracts.Query,
    Result=fetch_contracts.Result,
    Contracts=equatable.codegen(models.Contracts),
    ServiceToContract=models.ServiceToContract,
    ActiveContract=models.ActiveContract,
    WaitPolicy=fetch_contracts.WaitPolicy,
    ValueError=ValueError,
)
async def test_fetch_contracts(
        test_data_json, *, load_py_json, stq3_context, make_context,
):
    test_data = load_py_json(test_data_json)
    expected_error = test_data.get('expected_error')
    context = make_context(test_data['contracts'])
    query = test_data['query']
    if expected_error:
        with pytest.raises(type(expected_error)) as exc_info:
            await fetch_contracts.execute(
                context.contracts, context.migration_mode, query,
            )
        assert exc_info.value.args == expected_error.args
    else:
        results = await fetch_contracts.execute(
            context.contracts, context.migration_mode, query,
        )
        assert results == test_data['expected_results']


@pytest.fixture(name='make_context')
def make_make_context(stq3_context):
    def _make_context(contracts):
        stq3_context.contracts = mocks.Contracts(contracts)
        return stq3_context

    return _make_context


def duration(value: int) -> dt.timedelta:
    return dt.timedelta(seconds=value)


def tick(value: int) -> dt.datetime:
    return dt.datetime(1, 1, 1) + duration(value)


@pytest.mark.parametrize(
    'timeout, retry_delay, start, now, expected_dl_reached, expected_next_dt',
    [
        (duration(0), duration(0), tick(0), tick(0), True, tick(0)),
        (duration(1), duration(0), tick(0), tick(0), False, tick(0)),
        (duration(10), duration(3), tick(0), tick(0), False, tick(3)),
        (duration(10), duration(3), tick(0), tick(9), False, tick(10)),
        (duration(0), duration(3), tick(0), tick(0), True, tick(0)),
        (duration(1), duration(3), tick(0), tick(2), True, tick(1)),
    ],
)
def test_wait_policy(
        timeout,
        retry_delay,
        start,
        now,
        expected_dl_reached,
        expected_next_dt,
):
    policy = fetch_contracts.WaitPolicy(timeout, retry_delay)
    assert policy.is_deadline_reached(start, now) == expected_dl_reached
    assert policy.get_next_attempt_dt(start, now) == expected_next_dt
