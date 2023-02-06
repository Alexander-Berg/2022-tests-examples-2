# pylint: disable=redefined-outer-name
import datetime

import pytest

from taxi.clients import billing_v2

from corp_clients.generated.cron import run_cron


@pytest.fixture
def get_partner_balances_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_partner_balances')
    async def _get_partner_balances(service_id, contract_ids):
        contracts_by_service = load_json(
            'get_partner_balances_response.json',
        ).get(str(service_id), {})
        return [
            contract
            for contract in contracts_by_service
            if contract['ContractID'] in contract_ids
        ]


async def test_balance_changed(get_partner_balances_mock, db, stq):
    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_balances', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 101})
    assert 'updated' in contract
    assert contract['balance'].pop('balance_dt')
    assert contract['balance'].pop('receipt_dt')
    assert contract['balance'] == {
        'apx_sum': '25',
        'balance': '100.0',
        'discount_bonus_sum': '50',
        'receipt_sum': '100',
        'receipt_version': 0,
        'operational_balance': '105.0',
        'total_charge': '20.0',
        'act_sum': '10.0',
        'expired_debt_amount': '10.0',
    }

    contract = await db.corp_contracts.find_one({'_id': 107})
    assert 'updated' in contract
    assert contract['balance'].pop('receipt_dt')
    assert contract['balance'] == {
        'apx_sum': '25',
        'balance': '130.0',
        'balance_dt': datetime.datetime(2020, 7, 2, 4, 7, 50),
        'discount_bonus_sum': '50',
        'receipt_sum': '100',
        'receipt_version': 0,
        'operational_balance': '115.0',
        'total_charge': '10.0',
        'act_sum': '0',
        'expired_debt_amount': '0',
    }

    contract = await db.corp_contracts.find_one({'_id': 109})
    assert 'updated' in contract
    assert contract['balance'].pop('balance_dt')
    assert contract['balance'].pop('receipt_dt')
    assert contract['balance'] == {
        'apx_sum': '0',
        'balance': '99.0',
        'discount_bonus_sum': '0',
        'receipt_sum': '100',
        'receipt_version': 0,
        'operational_balance': '-210.0',
        'total_charge': '310.0',
        'act_sum': '0',
        'expired_debt_amount': '0',
    }

    assert stq.corp_notices_process_event.times_called == 2
    assert stq.corp_notices_process_event.next_call()['kwargs'] == {
        'event_name': 'BalanceChanged',
        'data': {
            'client_id': 'client_id_1',
            'contract_id': 101,
            'old_balance': '125',
            'new_balance': '105.0',
        },
    }
    assert stq.corp_notices_process_event.next_call()['kwargs'] == {
        'event_name': 'BalanceChanged',
        'data': {
            'client_id': 'client_id_1',
            'contract_id': 109,
            'old_balance': '125',
            'new_balance': '-210.0',
        },
    }


async def test_balance_not_changed(get_partner_balances_mock, db, stq):
    await db.corp_contracts.delete_many({'_id': {'$ne': 103}})
    contract_before_cron = await db.corp_contracts.find_one({'_id': 103})

    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_balances', '-t', '0'],
    )
    contract = await db.corp_contracts.find_one({'_id': 103})
    balance_before_cron = contract_before_cron['balance']
    balance_after_cron = contract['balance']
    assert 'updated' not in contract
    assert balance_after_cron['balance'] == balance_before_cron['balance']
    assert (
        balance_after_cron['balance_dt'] == balance_before_cron['balance_dt']
    )
    assert (
        balance_after_cron['receipt_sum'] == balance_before_cron['receipt_sum']
    )
    assert stq.corp_notices_process_event.times_called == 0


async def test_balance_initial(get_partner_balances_mock, db, stq):
    await db.corp_contracts.delete_many({'_id': {'$ne': 108}})
    contract_before_cron = await db.corp_contracts.find_one({'_id': 108})

    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_balances', '-t', '0'],
    )
    contract = await db.corp_contracts.find_one({'_id': 108})
    balance_before_cron = contract_before_cron.get('balance')
    assert balance_before_cron is None
    assert 'updated' in contract
    assert contract['balance'].pop('balance_dt')
    assert contract['balance'] == {
        'balance': '0',
        'operational_balance': '0',
        'total_charge': '0',
        'act_sum': '0',
        'expired_debt_amount': '0',
    }
    assert stq.corp_notices_process_event.times_called == 0


@pytest.mark.config(
    CORP_CRON_SYNC_CONTRACT_BALANCES_SETTINGS={'do_sync_inactive': True},
)
async def test_contract_inactive_signed(get_partner_balances_mock, db):
    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_balances', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 105})
    assert 'balance' in contract
    assert 'updated' in contract


@pytest.mark.config(
    CORP_CRON_SYNC_CONTRACT_BALANCES_SETTINGS={'do_sync_inactive': True},
)
async def test_old_does_not_sync(get_partner_balances_mock, db):
    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_balances', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 106})
    assert 'updated' not in contract


async def test_contract_not_exists(get_partner_balances_mock, db):
    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_balances', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 100})
    assert not contract


async def test_contract_unknown_service(get_partner_balances_mock, db):
    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_balances', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 104})
    assert 'balance' not in contract
    assert 'updated' not in contract


async def test_contract_unsigned(get_partner_balances_mock, db):
    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_balances', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 102})
    assert 'balance' not in contract
    assert 'updated' not in contract


async def test_billing_error(patch, db):
    @patch('taxi.clients.billing_v2.BalanceClient.get_partner_balances')
    async def _get_partner_balances(service_id, contract_ids):
        raise billing_v2.BillingError

    await run_cron.main(
        ['corp_clients.crontasks.sync_contract_balances', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 101})
    assert 'updated' not in contract
