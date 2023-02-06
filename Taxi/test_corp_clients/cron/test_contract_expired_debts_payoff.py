# pylint: disable=redefined-outer-name
import pytest

from corp_clients.generated.cron import run_cron
from test_corp_clients.web import test_utils


@pytest.fixture
def get_partner_balances_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_partner_balances')
    async def _get_partner_balances(service_id, contract_ids):
        res = load_json('get_partner_balances_response.json')
        res = [item for item in res if item['ContractID'] in contract_ids]
        return res


@pytest.fixture
def get_bound_payment_methods_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_bound_payment_methods')
    async def _get_bound_payment_methods(operator_uid, service_id):
        return test_utils.GET_BOUND_PAYMENT_METHODS_RESP


@pytest.fixture
def get_info_by_uid_mock(patch, load_json):
    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_info_by_uid(*args, **kwargs):
        return {'login': 'company_login', 'attributes': {'200': '1'}}


@pytest.mark.now('2021-02-17T02:00:00+00:00')
@pytest.mark.config(
    CORP_CONTRACT_DEBTS_PAYOFF_OBJ={'enable': True, 'contract_ids': [101]},
)
async def test_debts_payoff(
        db,
        stq,
        patch,
        get_bound_payment_methods_mock,
        get_info_by_uid_mock,
        get_partner_balances_mock,
):
    await db.corp_clients.update_many(
        {'_id': {'$in': ['good1']}}, {'$set': {'features': ['cards']}},
    )

    len_101 = await db.corp_contract_debts.count({'contract_id': 101})

    len_fixed_101 = await db.corp_contract_fixed_debts.count(
        {'contract_id': 101},
    )

    await run_cron.main(
        ['corp_clients.crontasks.contract_expired_debts_payoff', '-t', '0'],
    )

    debts = await db.corp_contract_debts.find({'contract_id': 101}).to_list(
        None,
    )
    debt_fixed = await db.corp_contract_fixed_debts.find(
        {'contract_id': 101},
    ).to_list(None)
    assert len(debts) == len_101 + 1
    assert len(debt_fixed) == len_fixed_101 + 1

    assert debt_fixed[0]['is_final']

    assert stq.corp_contract_debt_payoff.has_calls
