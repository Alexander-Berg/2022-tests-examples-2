# pylint: disable=redefined-outer-name
import pytest

from corp_clients.generated.cron import run_cron
from test_corp_clients.web import test_utils


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


@pytest.mark.config(
    CORP_CONTRACT_DEBTS_PAYOFF_OBJ={'enable': False, 'contract_ids': []},
)
@pytest.mark.config(CORP_PAYOFF_RETRY_DELAY_MINUTES=1)
@pytest.mark.now('2021-11-17T02:00:00+00:00')
async def test_debts_payoff(
        db, stq, patch, get_bound_payment_methods_mock, get_info_by_uid_mock,
):
    await db.corp_clients.update_many(
        {'_id': {'$in': ['good1']}}, {'$set': {'features': ['cards']}},
    )

    sort_by = [('created', -1)]

    len_101 = await db.corp_contract_debts.count({'contract_id': 101})

    await run_cron.main(
        ['corp_clients.crontasks.contract_postpaid_debts_payoff', '-t', '0'],
    )

    debts = (
        await db.corp_contract_debts.find({'contract_id': 101})
        .sort(sort_by)
        .to_list(None)
    )

    assert len(debts) == len_101 + 1
    assert stq.corp_contract_debt_payoff.has_calls


@pytest.mark.config(
    CORP_CONTRACT_DEBTS_PAYOFF_OBJ={'enable': False, 'contract_ids': []},
)
@pytest.mark.config(CORP_PAYOFF_RETRY_DELAY_MINUTES=1)
@pytest.mark.now('2021-11-17T02:00:00+00:00')
async def test_debts_payoff_104(
        db, stq, patch, get_bound_payment_methods_mock, get_info_by_uid_mock,
):
    await db.corp_clients.update_many(
        {'_id': {'$in': ['balance_debt']}}, {'$set': {'features': ['cards']}},
    )

    sort_by = [('created', -1)]

    len_104 = await db.corp_contract_debts.count({'contract_id': 104})

    await run_cron.main(
        ['corp_clients.crontasks.contract_postpaid_debts_payoff', '-t', '0'],
    )

    debts = (
        await db.corp_contract_debts.find({'contract_id': 104})
        .sort(sort_by)
        .to_list(None)
    )

    assert len(debts) == len_104 + 1
    assert stq.corp_contract_debt_payoff.has_calls
