import pytest


ERROR_JSON = {
    'random': 'keys',
    'with': 'random',
    'values': 123,
    'ololo': {'ololo': 'ololo'},
}

BALANCE_PERSONAL_ACCOUNTS_MOCK_RESPONSE_EMPTY = {
    'accounts_by_contracts': [{'personal_accounts': []}],
}

BALANCE_PERSONAL_ACCOUNTS_MOCK_RESPONSE = {
    'accounts_by_contracts': [
        {
            'personal_accounts': [
                {
                    'id': 12345,
                    'external_id': '123456',
                    'service_code': 'my_service_code',
                },
            ],
        },
    ],
}

CARRIER_ACCOUNTS_RESPONSE = {
    'accounts': [{'number': '123456', 'service_code': 'my_service_code'}],
}


async def test_shipper_create(taxi_cargo_trucks, mockserver):
    @mockserver.json_handler(
        '/cargo-crm-proxy/internal/cargo-crm/flow/trucks_register_shipper/state-interpretaion',
    )
    def _state_interpretation(request):
        return mockserver.make_response(
            status=200, json={'status': 'done', 'message': 'SUCCESS'},
        )

    @mockserver.json_handler(
        '/cargo-crm-proxy/internal/cargo-crm/flow/trucks_register_shipper/init',
    )
    def _initial_request(request):
        return mockserver.make_response(status=200, json={})

    response = await taxi_cargo_trucks.post(
        '/v1/shipper/create',
        headers={
            'accept-language': 'ru',
            'x-idempotency-token': '13245',
            'x-api-key': 'dGVzdF9zZWNyZXRfa2V5',
        },
        json={'some_key': 'some_value', 'external_ref': 'external_ref'},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    ['status_code'],
    (pytest.param(400, id='400'), pytest.param(409, id='409')),
)
async def test_errors(taxi_cargo_trucks, mockserver, status_code):
    @mockserver.json_handler(
        '/cargo-crm-proxy/internal/cargo-crm/flow/trucks_register_shipper/init',
    )
    def _initial_shipper_request(request):
        return mockserver.make_response(status=status_code, json=ERROR_JSON)

    @mockserver.json_handler(
        '/cargo-crm-proxy/internal/cargo-crm/flow/trucks_register_carrier/init',
    )
    def _initial_carrier_request(request):
        return mockserver.make_response(status=status_code, json=ERROR_JSON)

    for entity in ['shipper', 'carrier']:
        response = await taxi_cargo_trucks.post(
            '/v1/{entity}/create'.format(entity=entity),
            headers={
                'accept-language': 'ru',
                'x-idempotency-token': '13245',
                'x-api-key': 'dGVzdF9zZWNyZXRfa2V5',
            },
            json={'some_key': 'some_value', 'external_ref': 'external_ref'},
        )
        assert response.status_code == status_code
        assert response.json() == ERROR_JSON


async def test_shipper_update(taxi_cargo_trucks):
    response = await taxi_cargo_trucks.post(
        '/v1/shipper/update',
        headers={
            'accept-language': 'ru',
            'x-idempotency-token': '13245',
            'x-api-key': 'dGVzdF9zZWNyZXRfa2V5',
        },
        json={'some_key': 'some_value'},
    )
    assert response.status_code == 200


async def test_shipper_status(taxi_cargo_trucks, mockserver):
    @mockserver.json_handler(
        '/cargo-crm-proxy/internal/cargo-crm/flow/trucks_register_shipper/state-interpretaion',
    )
    def _state_interpretation(request):
        return mockserver.make_response(
            status=200, json={'status': 'done', 'message': 'SUCCESS'},
        )

    response = await taxi_cargo_trucks.post(
        '/v1/shipper/status',
        headers={'accept-language': 'ru', 'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json={'external_ref': '123'},
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'done', 'message': 'SUCCESS'}


@pytest.mark.pgsql('cargo_trucks', files=['pg_shippers.sql'])
async def test_shipper_accounts(taxi_cargo_trucks, mockserver):
    @mockserver.json_handler(
        '/cargo-crm-proxy/functions/balance-personal-accounts',
    )
    def _balance_personal_accounts(request):
        if request.json['contract_ids'] == [99999]:
            return mockserver.make_response(
                status=200, json=BALANCE_PERSONAL_ACCOUNTS_MOCK_RESPONSE,
            )
        return mockserver.make_response(
            status=200, json=BALANCE_PERSONAL_ACCOUNTS_MOCK_RESPONSE_EMPTY,
        )

    response = await taxi_cargo_trucks.get(
        '/v1/shipper/accounts?external_ref=123',
        headers={'accept-language': 'ru', 'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
    )
    assert response.status_code == 200
    assert response.json() == CARRIER_ACCOUNTS_RESPONSE


async def test_carrier_create(taxi_cargo_trucks, mockserver):
    @mockserver.json_handler(
        '/cargo-crm-proxy/internal/cargo-crm/flow/trucks_register_carrier/init',
    )
    def _initial_request(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler(
        '/cargo-crm-proxy/internal/cargo-crm/flow/trucks_register_carrier/state-interpretaion',
    )
    def _state_interpretation(request):
        return mockserver.make_response(
            status=200, json={'status': 'done', 'message': 'SUCCESS'},
        )

    response = await taxi_cargo_trucks.post(
        '/v1/carrier/create',
        headers={
            'accept-language': 'ru',
            'x-idempotency-token': '13245',
            'x-api-key': 'dGVzdF9zZWNyZXRfa2V5',
        },
        json={'some_key': 'some_value', 'external_ref': 'external_ref'},
    )
    assert response.status_code == 200


async def test_carrier_update(taxi_cargo_trucks):
    response = await taxi_cargo_trucks.post(
        '/v1/carrier/update',
        headers={
            'accept-language': 'ru',
            'x-idempotency-token': '13245',
            'x-api-key': 'dGVzdF9zZWNyZXRfa2V5',
        },
        json={'some_key': 'some_value'},
    )
    assert response.status_code == 200


async def test_carrier_status(taxi_cargo_trucks, mockserver):
    @mockserver.json_handler(
        '/cargo-crm-proxy/internal/cargo-crm/flow/trucks_register_carrier/state-interpretaion',
    )
    def _state_interpretation(request):
        return mockserver.make_response(
            status=200, json={'status': 'done', 'message': 'SUCCESS'},
        )

    response = await taxi_cargo_trucks.post(
        '/v1/carrier/status',
        headers={'accept-language': 'ru', 'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json={'external_ref': '123'},
    )
    assert response.status_code == 200


@pytest.mark.pgsql('cargo_trucks', files=['pg_carriers.sql'])
async def test_carrier_accounts(taxi_cargo_trucks, mockserver):
    @mockserver.json_handler(
        '/cargo-crm-proxy/functions/balance-personal-accounts',
    )
    def _balance_personal_accounts(request):
        if request.json['contract_ids'] == [88888]:
            return mockserver.make_response(
                status=200, json=BALANCE_PERSONAL_ACCOUNTS_MOCK_RESPONSE,
            )
        return mockserver.make_response(
            status=200, json=BALANCE_PERSONAL_ACCOUNTS_MOCK_RESPONSE_EMPTY,
        )

    response = await taxi_cargo_trucks.get(
        '/v1/carrier/accounts?external_ref=123',
        headers={'accept-language': 'ru', 'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
    )
    assert response.status_code == 200
    assert response.json() == CARRIER_ACCOUNTS_RESPONSE


@pytest.mark.parametrize(
    ['json_request'],
    (
        pytest.param({'cursor': '0', 'limit': 1}, id='with limit'),
        pytest.param({'cursor': '99902'}, id='without limit'),
        pytest.param({}, id='without anything'),
    ),
)
async def test_balances_updates(taxi_cargo_trucks, json_request):
    response = await taxi_cargo_trucks.post(
        '/v1/balances/updates',
        headers={'accept-language': 'ru', 'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json=json_request,
    )
    assert response.status_code == 200


@pytest.mark.pgsql('cargo_trucks', files=['pg_payments.sql'])
async def test_balances_updates_with_db(taxi_cargo_trucks):
    response = await taxi_cargo_trucks.post(
        '/v1/balances/updates',
        headers={'accept-language': 'ru', 'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json={'cursor': '0', 'limit': 2},
    )
    assert response.status_code == 200
    assert response.json() == {
        'balances': [
            {
                'amount': '103.4',
                'currency': 'RUB',
                'purpose_of_payment': 'trx1',
                'account_number': '12345',
                'creation_date': '2022-01-03T12:00:00+00:00',
                'effective_date': '2022-01-01T12:00:00+00:00',
                'customer_text': 'cstmr text',
                'inn': '140000001',
                'payment_num': '1234',
                'payment_date': '2022-01-02T12:00:00+00:00',
                'bik': '100000001',
                'account_name': 'account',
            },
            {
                'amount': '1009.89',
                'currency': 'USD',
                'purpose_of_payment': 'trx2',
                'account_number': '12345',
                'creation_date': '2022-01-03T12:00:00+00:00',
                'effective_date': '2022-01-01T12:00:00+00:00',
                'customer_text': 'cstmr text',
                'inn': '140000001',
                'payment_num': '1234',
                'payment_date': '2022-01-02T12:00:00+00:00',
                'bik': '100000001',
                'account_name': 'account',
            },
        ],
        'cursor': '2',
    }

    response_second = await taxi_cargo_trucks.post(
        '/v1/balances/updates',
        headers={'accept-language': 'ru', 'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json={'cursor': response.json()['cursor'], 'limit': 3},
    )
    assert response_second.status_code == 200
    assert response_second.json() == {
        'balances': [
            {
                'amount': '0.9',
                'currency': 'RUB',
                'purpose_of_payment': 'trx3',
                'account_number': '12345',
                'creation_date': '2022-01-06T12:00:00+00:00',
                'effective_date': '2022-01-01T12:00:00+00:00',
                'customer_text': 'cstmr text',
                'inn': '140000001',
                'payment_num': '1234',
                'payment_date': '2022-01-02T12:00:00+00:00',
                'bik': '100000001',
                'account_name': 'account',
            },
            {'amount': '1.9', 'currency': 'RUB'},
        ],
        'cursor': '4',
    }


@pytest.mark.config(CARGO_TRUCKS_BALANCES_UPDATES_LIMIT_MAX=1)
@pytest.mark.pgsql('cargo_trucks', files=['pg_payments.sql'])
async def test_balances_updates_config(taxi_cargo_trucks):
    response = await taxi_cargo_trucks.post(
        '/v1/balances/updates',
        headers={'accept-language': 'ru', 'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json={'limit': 2},
    )
    assert response.status_code == 200
    assert response.json() == {
        'balances': [
            {
                'amount': '103.4',
                'currency': 'RUB',
                'purpose_of_payment': 'trx1',
                'account_number': '12345',
                'creation_date': '2022-01-03T12:00:00+00:00',
                'effective_date': '2022-01-01T12:00:00+00:00',
                'customer_text': 'cstmr text',
                'inn': '140000001',
                'payment_num': '1234',
                'payment_date': '2022-01-02T12:00:00+00:00',
                'bik': '100000001',
                'account_name': 'account',
            },
        ],
        'cursor': '1',
    }


@pytest.mark.pgsql('cargo_trucks', files=['pg_payments.sql'])
async def test_balances_updates_big_cursor(taxi_cargo_trucks):
    response = await taxi_cargo_trucks.post(
        '/v1/balances/updates',
        headers={'accept-language': 'ru', 'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json={'limit': 2, 'cursor': '1000'},
    )
    assert response.status_code == 200
    assert response.json() == {'balances': [], 'cursor': '4'}


async def test_balances_updates_no_auth(taxi_cargo_trucks):
    response = await taxi_cargo_trucks.post(
        '/v1/balances/updates',
        headers={'accept-language': 'ru', 'x-api-key': 'ololo'},
        json={'cursor': '0', 'limit': 100},
    )
    assert response.status_code == 403


async def test_no_auth_post(taxi_cargo_trucks):
    for handler in [
            '/v1/shipper/create',
            '/v1/carrier/status',
            '/v1/carrier/update',
            '/v1/carrier/create',
            '/v1/shipper/status',
            '/v1/shipper/update',
    ]:
        response = await taxi_cargo_trucks.post(
            handler,
            headers={
                'accept-language': 'ru',
                'x-idempotency-token': '13245',
                'x-api-key': 'ololo',
            },
            json={'external_ref': '123'},
        )
        assert response.status_code == 403


async def test_no_auth_get(taxi_cargo_trucks):
    for handler in [
            '/v1/shipper/accounts?external_ref=123',
            '/v1/carrier/accounts?external_ref=123',
    ]:
        response = await taxi_cargo_trucks.get(
            handler,
            headers={
                'accept-language': 'ru',
                'x-idempotency-token': '13245',
                'x-api-key': 'ololo',
            },
        )
        assert response.status_code == 403
