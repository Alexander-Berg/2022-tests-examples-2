# pylint: disable=redefined-outer-name

import datetime
import json

import pytest

from corp_clients.generated.cron import run_cron


@pytest.fixture
def logbroker_mock(patch, load_json):
    @patch(
        'corp_clients.crontasks.lb_sync_contract_receipts.'
        'LogbrokerWrapper.read',
    )
    def _read(topic, consumer):
        data = load_json('topic-partner-fast-balance.json')
        if topic == 'balance/test/partner-fast-balance/zaxi':
            data = load_json('partner-fast-balance-zaxi.json')
        data = [json.dumps(i).encode() for i in data]
        yield data


async def test_base(logbroker_mock, db, stq):
    await run_cron.main(
        ['corp_clients.crontasks.lb_sync_contract_receipts', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 101})
    assert 'updated' in contract
    assert contract['balance'] == {
        'apx_sum': '25',
        'balance': '-10',
        'discount_bonus_sum': '50',
        'receipt_sum': '100',
        'balance_dt': datetime.datetime.fromisoformat('2021-02-01T00:00:00'),
        'receipt_dt': datetime.datetime.fromisoformat('2021-03-01T00:00:00'),
        'receipt_version': 2,
        'operational_balance': '115',
        'total_charge': '10',
    }

    tanker_contract = await db.corp_contracts.find_one({'_id': 103})
    assert 'updated' in tanker_contract
    assert tanker_contract['balance'] == {
        'apx_sum': '0',
        'balance': '-10',
        'discount_bonus_sum': '0',
        'receipt_sum': '100',
        'balance_dt': datetime.datetime.fromisoformat('2021-02-01T00:00:00'),
        'receipt_dt': datetime.datetime.fromisoformat('2021-03-01T00:00:00'),
        'receipt_version': 2,
        'operational_balance': '90',
        'total_charge': '10',
    }

    assert stq.corp_notices_process_event.times_called == 2
    assert stq.corp_notices_process_event.next_call()['kwargs'] == {
        'event_name': 'BalanceChanged',
        'data': {
            'client_id': 'client_id_1',
            'contract_id': 101,
            'old_balance': '-10',
            'new_balance': '115',
        },
    }
    assert stq.corp_notices_process_event.next_call()['kwargs'] == {
        'event_name': 'BalanceChanged',
        'data': {
            'client_id': 'client_id_1',
            'contract_id': 103,
            'old_balance': '-10',
            'new_balance': '90',
        },
    }


async def test_not_changed(logbroker_mock, db):
    await run_cron.main(
        ['corp_clients.crontasks.lb_sync_contract_receipts', '-t', '0'],
    )

    contract = await db.corp_contracts.find_one({'_id': 102})
    assert 'updated' not in contract
