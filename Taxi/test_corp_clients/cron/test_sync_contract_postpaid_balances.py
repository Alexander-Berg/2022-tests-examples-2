# pylint: disable=redefined-outer-name
import pytest

from taxi.clients import billing_v2

from corp_clients.generated.cron import run_cron


@pytest.fixture
def get_partner_balances_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_partner_balances')
    async def _get_partner_balances(service_id, contract_ids):
        res = load_json('get_partner_balances_response.json')
        res = [item for item in res if item['ContractID'] in contract_ids]
        return res


@pytest.mark.now('2020-11-01T00:00:00+00:00')
async def test_sync_debts(get_partner_balances_mock, db):
    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_postpaid_balances', '-t', '0'],
    )

    contracts = await db.corp_contracts.find(
        {'payment_type': 'postpaid'},
    ).to_list(None)

    contract_dict = {contract['_id']: contract for contract in contracts}

    assert (
        contract_dict[101]['balance']['expired_debt_amount'] == '100'
        and contract_dict[101]['balance']['first_debt_from_dt'] is not None
    )

    assert contract_dict[102]['balance']['expired_debt_amount'] == '200'
    assert contract_dict[103]['balance']['expired_debt_amount'] == '0'
    assert contract_dict[104]['balance']['expired_debt_amount'] == '0'
    assert 'balance' not in contract_dict[105]
    assert 'balance' not in contract_dict[106]
    assert 'balance' not in contract_dict[107]


async def test_billing_error(patch, db):
    @patch('taxi.clients.billing_v2.BalanceClient.get_partner_balances')
    async def _get_partner_balances(service_id, contract_ids):
        raise billing_v2.BillingError

    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_postpaid_balances', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 101})
    assert 'balance' not in contract
