# pylint: disable=redefined-outer-name
import pytest

from corp_clients.generated.cron import run_cron


@pytest.fixture
def get_partner_balances_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_partner_balances')
    async def _get_partner_balances(service_id, contract_ids):
        return load_json('get_partner_balances_response.json')


@pytest.fixture
def yt_mock(patch, load_json):
    @patch(
        'corp_clients.generated.cron.yt_wrapper.plugin.'
        'AsyncYTClient.read_table',
    )
    async def _read_table(*args, **kwargs):
        return load_json('crm_data.json')


@pytest.mark.config(CORP_SYNC_BILLING_POSTPAID_BALANCE_ENABLED=True)
async def test(db, get_partner_balances_mock, yt_mock):
    await run_cron.main(
        ['corp_clients.crontasks.activate_contracts_from_crm', '-t', '0'],
    )

    contracts = await db.corp_contracts.find().to_list(None)
    contracts_by_id = {contract['_id']: contract for contract in contracts}

    def assert_activated(contract_id):
        contract = contracts_by_id[contract_id]
        assert contract['settings']['is_active'] is True
        assert 'updated' in contract

    def assert_not_activated(contract_id):
        contract = contracts_by_id[contract_id]
        assert contract['settings']['is_active'] is False
        assert 'updated' not in contract

    assert_activated(101)
    assert_activated(105)
    assert_activated(107)
    assert_not_activated(102)
    assert_not_activated(103)
    assert_not_activated(104)
    assert_not_activated(106)
