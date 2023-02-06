# pylint: disable=redefined-outer-name
import decimal

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
@pytest.mark.now('2021-11-17T02:00:00+00:00')
async def test_debts_payoff(
        db, stq, patch, get_bound_payment_methods_mock, get_info_by_uid_mock,
):
    await db.corp_clients.update_many(
        {'_id': {'$in': ['good1', 'good2', 'good8', 'crm_dept']}},
        {'$set': {'features': ['cards']}},
    )

    sort_by = [('created', -1)]

    len_101 = await db.corp_contract_debts.count({'contract_id': 101})
    len_102 = await db.corp_contract_debts.count({'contract_id': 102})

    len_fixed_101 = await db.corp_contract_fixed_debts.count(
        {'contract_id': 101},
    )
    len_fixed_102 = await db.corp_contract_fixed_debts.count(
        {'contract_id': 102},
    )

    len_fixed_108 = await db.corp_contract_fixed_debts.count(
        {'contract_id': 108},
    )

    await run_cron.main(
        ['corp_clients.crontasks.contract_postpaid_debts_payoff', '-t', '0'],
    )

    debts = await db.corp_contract_debts.find({'contract_id': 101}).to_list(
        None,
    )
    debt_fixed = await db.corp_contract_fixed_debts.find(
        {'contract_id': 101},
    ).to_list(None)
    assert len(debts) == len_101
    assert len(debt_fixed) == len_fixed_101

    debts = (
        await db.corp_contract_debts.find({'contract_id': 102})
        .sort(sort_by)
        .to_list(None)
    )
    debt_fixed = await db.corp_contract_fixed_debts.find(
        {'contract_id': 102},
    ).to_list(None)

    assert debts[0]['payoff_status'] == 'started'
    assert debts[0]['card_id'] == 'card-123-short'
    assert (
        isinstance(debts[0]['debt'], str)
        and decimal.Decimal(debts[0]['debt']) > 0
    )
    assert len(debts) == len_102 + 1
    assert len(debt_fixed) == len_fixed_102 + 1

    assert (
        'debt_dt' in debt_fixed[0]
        and debt_fixed[0]['balance_info']['first_debt_amount'] is not None
        and debt_fixed[0]['balance_info']['first_debt_from_dt'] is not None
    )

    assert debts[0]['fixed_debt_id'] == debt_fixed[0]['_id']

    debt_fixed = await db.corp_contract_fixed_debts.find(
        {'contract_id': 108},
    ).to_list(None)

    assert len(debt_fixed) == len_fixed_108 + 1
    assert (
        isinstance(debt_fixed[0]['debt'], str)
        and decimal.Decimal(debt_fixed[0]['debt']) >= 0
    )

    assert stq.corp_contract_debt_payoff.has_calls


@pytest.mark.config(
    CORP_CONTRACT_DEBTS_PAYOFF_OBJ={'enable': False, 'contract_ids': []},
)
@pytest.mark.now('2021-11-16T02:00:00+00:00')
async def test_debts_payoff_earlier(db, stq):
    await db.corp_clients.update_many(
        {'_id': {'$in': ['good1', 'crm_dept']}},
        {'$set': {'features': ['cards']}},
    )

    len_101 = await db.corp_contract_debts.count({'contract_id': 101})

    await run_cron.main(
        ['corp_clients.crontasks.contract_postpaid_debts_payoff', '-t', '0'],
    )

    debts = await db.corp_contract_debts.find({'contract_id': 101}).to_list(
        None,
    )
    assert len(debts) == len_101

    assert stq.corp_contract_debt_payoff.has_calls is False


@pytest.mark.config(
    CORP_CONTRACT_DEBTS_PAYOFF_OBJ={'enable': False, 'contract_ids': []},
)
@pytest.mark.now('2021-11-18T02:00:00+00:00')
async def test_debts_payoff_trylater_1(
        db, patch, get_bound_payment_methods_mock, get_info_by_uid_mock, stq,
):
    await db.corp_clients.update_many(
        {'_id': {'$in': ['balance_debt']}}, {'$set': {'features': ['cards']}},
    )
    len_104 = await db.corp_contract_debts.count({'contract_id': 104})

    await run_cron.main(
        ['corp_clients.crontasks.contract_postpaid_debts_payoff', '-t', '0'],
    )

    debts = await db.corp_contract_debts.find({'contract_id': 104}).to_list(
        None,
    )
    assert len(debts) == len_104 + 1

    assert stq.corp_contract_debt_payoff.has_calls


@pytest.mark.config(
    CORP_CONTRACT_DEBTS_PAYOFF_OBJ={'enable': False, 'contract_ids': []},
)
@pytest.mark.now('2021-11-17T02:00:00+00:00')
async def test_debts_payoff_trylater_2(
        db, patch, get_bound_payment_methods_mock, get_info_by_uid_mock, stq,
):
    await db.corp_clients.update_many(
        {'_id': {'$in': ['balance_debt']}}, {'$set': {'features': ['cards']}},
    )

    len_104 = await db.corp_contract_debts.count({'contract_id': 104})

    await run_cron.main(
        ['corp_clients.crontasks.contract_postpaid_debts_payoff', '-t', '0'],
    )

    debts = await db.corp_contract_debts.find({'contract_id': 104}).to_list(
        None,
    )
    assert len(debts) == len_104
    assert stq.corp_contract_debt_payoff.has_calls is False
