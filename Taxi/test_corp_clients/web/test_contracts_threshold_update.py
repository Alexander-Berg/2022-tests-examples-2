import decimal

import pytest

CORP_COUNTRIES_SUPPORTED = {'rus': {'deactivate_threshold': 100}}


@pytest.mark.parametrize(
    'contract_id, client_id',
    [pytest.param(101, 'client_id_1'), pytest.param(204, 'client_id_6')],
)
async def test_threshold_update(
        web_app_client, contract_id, client_id, db, stq,
):
    data = {
        'contract_id': contract_id,
        'prepaid_deactivate_threshold': '123',
        'prepaid_deactivate_threshold_type': 'quasi',
    }

    # prepare expected client
    old_client = await db.secondary.corp_clients.find_one({'_id': client_id})
    expected_client = old_client

    # prepare expected contract
    old_contract = await db.corp_contracts.find_one({'_id': contract_id})

    expected_contract = old_contract
    settings = expected_contract['settings']
    settings['prepaid_deactivate_threshold'] = '123'
    settings['prepaid_deactivate_threshold_type'] = 'quasi'
    del settings['prepaid_deactivate_threshold_id']

    response = await web_app_client.post(
        '/v1/contracts/threshold/update', json=data,
    )
    assert response.status == 200

    # check contract
    contract = await db.corp_contracts.find_one({'_id': contract_id})

    for key in ['created', 'updated']:
        expected_contract.pop(key, None)
        contract.pop(key, None)

    assert contract == expected_contract

    # ContractThresholdUpdated event
    assert stq.corp_notices_process_event.times_called == 1
    assert stq.corp_notices_process_event.next_call()['kwargs'] == {
        'event_name': 'ContractThresholdUpdated',
        'data': {
            'client_id': client_id,
            'contract_id': contract_id,
            'old': {'threshold': '123.34', 'threshold_type': 'standard'},
            'new': {'threshold': '123', 'threshold_type': 'quasi'},
        },
    }

    # check client
    client = await db.corp_clients.find_one(
        {'billing_id': contract['billing_client_id']},
    )

    for key in ['created', 'updated', 'updated_at']:
        expected_client.pop(key, None)
        client.pop(key, None)

    assert client == expected_client


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=CORP_COUNTRIES_SUPPORTED)
async def test_standard_type(web_app_client, db):

    contract_id = 101
    data = {
        'contract_id': contract_id,
        'prepaid_deactivate_threshold_type': 'standard',
    }

    # prepare expected contract
    old_contract = await db.corp_contracts.find_one({'_id': contract_id})
    client = await db.corp_clients.find_one(
        {'billing_id': old_contract['billing_client_id']},
    )

    expected_contract = old_contract
    settings = expected_contract['settings']
    default_threshold = str(
        CORP_COUNTRIES_SUPPORTED[client['country']]['deactivate_threshold'],
    )
    settings['prepaid_deactivate_threshold'] = default_threshold
    settings['prepaid_deactivate_threshold_type'] = 'standard'
    settings.pop('prepaid_deactivate_threshold_id')

    response = await web_app_client.post(
        '/v1/contracts/threshold/update', json=data,
    )
    assert response.status == 200

    # check contract
    contract = await db.corp_contracts.find_one({'_id': contract_id})
    for key in ['created', 'updated']:
        expected_contract.pop(key, None)
        contract.pop(key, None)

    assert contract == expected_contract


async def test_big_quasi_type(web_app_client, db):
    threshold = decimal.Decimal('-10000')

    contract_id = 102
    data = {
        'contract_id': contract_id,
        'prepaid_deactivate_threshold_type': 'big_quasi',
        'prepaid_deactivate_threshold': str(threshold.to_integral_value()),
    }
    response = await web_app_client.post(
        '/v1/contracts/threshold/update', json=data,
    )
    assert response.status == 200
    contract = await db.corp_contracts.find_one({'_id': contract_id})
    new_threshold = decimal.Decimal(
        contract['settings']['low_balance_threshold'],
    )
    assert threshold * decimal.Decimal('0.8') == new_threshold


@pytest.mark.parametrize(
    'data, reason',
    [
        pytest.param(
            {
                'contract_id': 555,
                'prepaid_deactivate_threshold': '123',
                'prepaid_deactivate_threshold_type': 'quasi',
            },
            'Contract 555 not found',
            id='contract_not_found',
        ),
        pytest.param(
            {
                'contract_id': 203,
                'prepaid_deactivate_threshold': '123',
                'prepaid_deactivate_threshold_type': 'quasi',
            },
            'Client with billing_id billing_id_not_exists not found',
            id='client_not_found',
        ),
        pytest.param(
            {
                'contract_id': 101,
                'prepaid_deactivate_threshold': '123',
                'prepaid_deactivate_threshold_type': 'standard',
            },
            'Threshold is not expected for threshold_type: standard',
            id='standard_type_error',
        ),
        pytest.param(
            {
                'contract_id': 202,
                'prepaid_deactivate_threshold': '123',
                'prepaid_deactivate_threshold_type': 'quasi',
            },
            'Contract is not prepaid',
            id='not_prepaid',
        ),
    ],
)
async def test_threshold_update_error(web_app_client, stq, data, reason):
    response = await web_app_client.post(
        '/v1/contracts/threshold/update', json=data,
    )
    assert response.status == 400
    assert await response.json() == {
        'code': 'REQUEST_ERROR',
        'details': {'reason': reason},
        'message': 'Request error',
    }

    # ContractThresholdUpdated event
    assert not stq.corp_notices_process_event.times_called


async def test_threshold_update_null_threshold(web_app_client, stq, db):
    contract_id = 101

    contract = await db.corp_contracts.find_one({'_id': contract_id})
    old_threshold = contract['settings']['prepaid_deactivate_threshold']

    data = {
        'contract_id': contract_id,
        'prepaid_deactivate_threshold_type': 'quasi',
    }

    response = await web_app_client.post(
        '/v1/contracts/threshold/update', json=data,
    )
    assert response.status == 200

    contract = await db.corp_contracts.find_one({'_id': contract_id})
    assert contract['settings']['prepaid_deactivate_threshold_type'] == 'quasi'
    assert (
        old_threshold == contract['settings']['prepaid_deactivate_threshold']
    )

    # ContractThresholdUpdated event
    assert stq.corp_notices_process_event.times_called == 0
