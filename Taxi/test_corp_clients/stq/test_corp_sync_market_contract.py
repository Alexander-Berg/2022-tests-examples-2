import pytest

from corp_clients.stq import corp_sync_market_contract


@pytest.mark.parametrize(
    ['billing_client_id', 'contract_id'],
    [
        pytest.param('good', 2, id='new_contract'),
        pytest.param('good2', 103, id='already_saved_contract'),
    ],
)
async def test_corp_sync_market_contract(
        patch,
        mock_corp_edo,
        db,
        stq3_context,
        stq,
        billing_client_id,
        contract_id,
):
    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _get_client_contracts(*args, **kwargs):
        return [
            {
                'SERVICES': [650],
                'EXTERNAL_ID': 'taxi_contract',
                'ID': 1,
                'IS_ACTIVE': 1,
                'PERSON_ID': 1,
                'CURRENCY': 'RUR',
                'CONTRACT_TYPE': 9,
                'OFFER_ACCEPTED': 1,
                'PAYMENT_TYPE': 2,
                'FIRM_ID': 13,
            },
            {
                'SERVICES': [1173],
                'EXTERNAL_ID': 'market_contract',
                'ID': contract_id,
                'IS_ACTIVE': 1,
                'PERSON_ID': 1,
                'CURRENCY': 'RUR',
                'CONTRACT_TYPE': 9,
                'OFFER_ACCEPTED': 1,
                'PAYMENT_TYPE': 2,
                'FIRM_ID': 111,
            },
        ]

    await corp_sync_market_contract.task(
        stq3_context, billing_client_id=billing_client_id,
    )

    new_contract = await db.corp_contracts.find_one(
        {'billing_client_id': billing_client_id, 'service_ids': 1173},
        projection={'created': False, 'updated': False},
    )
    assert new_contract == {
        '_id': contract_id,
        'billing_client_id': billing_client_id,
        'billing_person_id': '1',
        'contract_external_id': 'market_contract',
        'firm_id': 111,
        'currency': 'RUB',
        'finish_dt': None,
        'is_active': True,
        'is_cancelled': False,
        'is_offer': True,
        'is_sent': False,
        'is_faxed': False,
        'is_signed': False,
        'is_suspended': False,
        'offer_accepted': True,
        'edo_accepted': False,
        'payment_term': None,
        'payment_type': 'prepaid',
        'service_ids': [1173],
        'settings': {
            'is_active': True,
            'is_auto_activate': True,
            'prepaid_deactivate_threshold': '0',
            'prepaid_deactivate_threshold_type': 'standard',
        },
        'start_dt': None,
    }
