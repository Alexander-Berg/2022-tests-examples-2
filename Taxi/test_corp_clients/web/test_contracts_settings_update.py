import copy

BASE_CONTRACT = {
    '_id': 12345,
    'billing_client_id': '123',
    'settings': {},
    'service_ids': [],
}
BASE_TEST_DATA = {
    'is_active': True,
    'is_auto_activate': True,
    'low_balance_threshold': '100',
    'low_balance_notification_enabled': True,
    'contract_limit': {'limit': '200.0', 'threshold': '300.0'},
}


async def test_contract_not_found(web_app_client):
    response = await web_app_client.post(
        '/v1/contracts/settings/update',
        params={'contract_id': BASE_CONTRACT['_id']},
        json=BASE_TEST_DATA,
    )
    assert response.status == 404


async def test_contract_settings_update(web_app_client, db):
    await db.corp_contracts.insert_one(BASE_CONTRACT)
    response = await web_app_client.post(
        '/v1/contracts/settings/update',
        params={'contract_id': BASE_CONTRACT['_id']},
        json=BASE_TEST_DATA,
    )
    assert response.status == 200
    contract = await db.secondary.corp_contracts.find_one(
        {'_id': BASE_CONTRACT['_id']}, projection=['settings'],
    )
    assert contract['settings']['is_active'] == BASE_TEST_DATA['is_active']
    assert (
        contract['settings']['contract_limit']
        == BASE_TEST_DATA['contract_limit']
    )


async def test_contract_settings_set_limit_null(web_app_client, db):
    await db.corp_contracts.insert_one(dict(BASE_CONTRACT, **BASE_TEST_DATA))

    response = await web_app_client.post(
        '/v1/contracts/settings/update',
        params={'contract_id': BASE_CONTRACT['_id']},
        json={'is_active': True},
    )
    assert response.status == 200
    contract = await db.secondary.corp_contracts.find_one(
        {'_id': BASE_CONTRACT['_id']}, projection=['settings'],
    )
    assert contract['settings'] == {'is_active': True}


async def test_contract_wrong_request(web_app_client):
    test_data = copy.copy(BASE_TEST_DATA)
    test_data['is_active'] = 'wrong'
    test_data['contract_limit'] = 'wrong'
    response = await web_app_client.post(
        '/v1/contracts/settings/update',
        params={'contract_id': BASE_CONTRACT['_id']},
        json=test_data,
    )
    assert response.status == 400


async def test_changed_services_low_balance_threshold(
        web_app_client, patch, db, personal_mock, corp_billing_mock,
):
    await db.corp_contracts.insert_one(
        dict(BASE_CONTRACT, service_ids=[650, 668]),
    )
    await db.corp_clients.insert_one(
        {
            '_id': 'check_low_balance_change',
            'billing_id': BASE_CONTRACT['billing_client_id'],
            'services': {'taxi': {}, 'drive': {}, 'eats2': {}},
        },
    )

    response = await web_app_client.post(
        '/v1/contracts/settings/update',
        params={'contract_id': BASE_CONTRACT['_id']},
        json=BASE_TEST_DATA,
    )
    assert response.status == 200

    # check client.services updated
    client = await db.secondary.corp_clients.find_one(
        {'_id': 'check_low_balance_change'},
    )

    assert client['services']['drive'] == {}
    taxi_service = client['services']['taxi']
    assert taxi_service['low_balance_threshold'] == 100
    assert taxi_service['low_balance_notification_enabled'] is True
    eats2_service = client['services']['eats2']
    assert eats2_service['low_balance_threshold'] == 100
    assert eats2_service['low_balance_notification_enabled'] is True
