import pytest

from taxi_billing_subventions.common import db as common_db
from taxi_billing_subventions.process_doc import contracts
from test_taxi_billing_subventions.test_process_doc import (
    BillingReplicationClient,
)


class Config:
    def __init__(
            self,
            park_account_history_usage: str,
            replication_contracts_usage: str = 'disable',
    ) -> None:
        # pylint: disable=invalid-name
        self.PARK_ACCOUNT_HISTORY_USAGE = park_account_history_usage
        self.REPLICATION_CONTRACTS_USAGE = replication_contracts_usage
        self.BILLING_REPLICATION_EXT_REQUEST_TIMEOUT_MS = 500


@pytest.mark.parametrize(
    'test_case_json',
    [
        'disable.json',
        'reconcile_same.json',
        'reconcile_different.json',
        'reconcile_error.json',
        'enable_same.json',
        'enable_different.json',
        'enable_error_no_contracts.json',
        'replication_enable_same.json',
        'replication_enable_different.json',
        'replication_enable_no_active_contracts.json',
        'replication_reconcile_different.json',
        'replication_reconcile_park_history_enable.json',
        'replication_enable_park_history_enable.json',
    ],
)
@pytest.mark.filldb(currency_rates='for_test_fetch_currency_data')
async def test_fetch_currency_data(test_case_json, load_py_json, db):
    test_case = load_py_json(f'test_fetch_currency_data/{test_case_json}')
    park = test_case['park']
    for_cash = test_case['for_cash']
    local_currency = test_case['local_currency']
    currency_data = test_case['currency_data']
    datetime = test_case['datetime']
    due = test_case['due']
    tzinfo = test_case['tzinfo']
    park_account_history_usage = test_case['park_account_history_usage']
    replication_contracts_usage = test_case['replication_contracts_usage']
    replication_contracts = test_case['replication_contracts']
    expected = test_case['expected']

    actual = await contracts.fetch_currency_data(
        database=db,
        billing_replication_client=BillingReplicationClient(
            replication_contracts,
        ),
        billing_client_id='billing_client_id',
        config=Config(park_account_history_usage, replication_contracts_usage),
        park=park,
        for_cash=for_cash,
        is_cargo=False,
        local_currency=local_currency,
        currency_data=currency_data,
        datetime=datetime,
        due=due,
        tzinfo=tzinfo,
        log_extra=None,
    )
    assert actual == expected


@pytest.mark.parametrize(
    'test_case_json',
    [
        'no_agent_contract_currency_rate.json',
        'no_marketing_contract_currency_rate.json',
    ],
)
@pytest.mark.filldb(currency_rates='for_test_no_currency_rate')
async def test_no_currency_rate(test_case_json, load_py_json, db):
    test_case = load_py_json(f'test_no_currency_rate/{test_case_json}')

    with pytest.raises(common_db.currency_rates.CurrencyRateNotFoundError):
        await contracts.fetch_currency_data(
            database=db,
            billing_replication_client=BillingReplicationClient(),
            billing_client_id='billing_client_id',
            is_cargo=False,
            config=Config('enable'),
            **test_case,
            log_extra=None,
        )
