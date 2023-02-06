import datetime
import logging

import pytest

from corp_clients.stq import corp_sync_contracts_info


logger = logging.getLogger(__name__)

NOW = datetime.datetime(year=2022, month=6, day=14)


TAXI_CONTRACT = {
    'SERVICES': [650],
    'EXTERNAL_ID': 'taxi_contract',
    'ID': 1,
    'IS_ACTIVE': 1,
    'IS_SENT': 0,
    'IS_FAXED': 0,
    'IS_SIGNED': 0,
    'PERSON_ID': 1,
    'CURRENCY': 'RUR',
    'CONTRACT_TYPE': 9,
    'OFFER_ACCEPTED': 1,
    'PAYMENT_TYPE': 2,
    'FIRM_ID': 13,
}

MARKET_CONTRACT = {
    'SERVICES': [1173],
    'EXTERNAL_ID': 'market_contract',
    'ID': 2,
    'IS_ACTIVE': 1,
    'IS_SENT': 0,
    'IS_FAXED': 0,
    'IS_SIGNED': 0,
    'PERSON_ID': 1,
    'CURRENCY': 'RUR',
    'CONTRACT_TYPE': 9,
    'OFFER_ACCEPTED': 1,
    'PAYMENT_TYPE': 2,
    'FIRM_ID': 111,
}

MONGO_CONTRACT = {
    'billing_person_id': '1',
    'currency': 'RUB',
    'edo_accepted': False,
    'finish_dt': None,
    'is_active': True,
    'is_cancelled': False,
    'is_offer': True,
    'is_sent': False,
    'is_faxed': False,
    'is_signed': False,
    'is_suspended': False,
    'offer_accepted': True,
    'payment_term': None,
    'payment_type': 'prepaid',
    'settings': {
        'is_active': True,
        'is_auto_activate': True,
        'prepaid_deactivate_threshold': '0',
        'prepaid_deactivate_threshold_type': 'standard',
    },
    'start_dt': None,
}


@pytest.mark.parametrize(
    [
        'billing_id',
        'client_id',
        'balance_response',
        'send_notice_count',
        'expected_contract',
    ],
    [
        pytest.param(
            'billing_1',
            'client_1',
            [TAXI_CONTRACT],
            1,
            dict(
                MONGO_CONTRACT,
                _id=1,
                billing_client_id='billing_1',
                contract_external_id='taxi_contract',
                firm_id=13,
                service_ids=[650],
            ),
            id='with-notices',
        ),
        pytest.param(
            'billing_2',
            'client_2',
            [TAXI_CONTRACT, MARKET_CONTRACT],
            0,
            dict(
                MONGO_CONTRACT,
                _id=2,
                billing_client_id='billing_2',
                contract_external_id='market_contract',
                firm_id=111,
                service_ids=[1173],
            ),
            id='without-notices',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_sync_contracts_info(
        patch,
        mock_corp_edo,
        db,
        stq3_context,
        stq,
        billing_id,
        client_id,
        balance_response,
        send_notice_count,
        expected_contract,
):
    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _get_client_contracts(*args, **kwargs):
        return balance_response

    await corp_sync_contracts_info.task(
        stq3_context, billing_client_id=billing_id, client_id=client_id,
    )

    assert stq.corp_notices_process_event.times_called == send_notice_count
    if send_notice_count:
        assert stq.corp_notices_process_event.next_call()['kwargs'] == {
            'event_name': 'ContractChanged',
            'data': {
                'client_id': client_id,
                'contract_id': 1,
                'new': {
                    'is_active': True,
                    'is_offer': True,
                    'offer_accepted_common': True,
                    'payment_type': 'prepaid',
                },
                'old': {
                    'is_active': None,
                    'is_offer': None,
                    'offer_accepted_common': None,
                    'payment_type': None,
                },
            },
        }

    contracts = await db.corp_contracts.find(
        {'billing_client_id': billing_id, 'updated': {'$gt': NOW}},
        projection={'updated': False, 'updated_at': False, 'created': False},
    ).to_list(None)
    assert len(contracts) == 1
    assert contracts == [expected_contract]
