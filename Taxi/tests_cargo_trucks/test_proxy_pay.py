async def test_pay_shipping_contract_calls(
        taxi_cargo_trucks, load_json, mockserver,
):
    contract_version = 2
    json_request = load_json('shipping_contract_details.json')
    order_id = 'trucks_order_id'
    json_request['order_id'] = order_id
    json_request['event_version'] = contract_version

    @mockserver.json_handler(
        '/cargo-finance-proxy/internal/cargo-finance/events/dummy-init',
    )
    def _dummy_init(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler(
        '/cargo-finance-proxy/internal/cargo-finance/flow/trucks/events/pay-shipping-contract',
    )
    def _pay_shipping_contract(request):
        return mockserver.make_response(status=200, json={})

    response = await taxi_cargo_trucks.post(
        '/v1/pay/shipping-contract',
        headers={'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json=json_request,
    )
    assert response.status_code == 200

    dummy_init_call = _dummy_init.next_call()
    assert dummy_init_call['request'].query['entity_id'] == order_id
    assert dummy_init_call['request'].query['flow'] == 'trucks'

    pay_shipping_contract_call = _pay_shipping_contract.next_call()
    json_finance = load_json('shipping_contract_details.json')
    json_finance['contract_version'] = contract_version
    assert pay_shipping_contract_call['request'].json == json_finance
    assert pay_shipping_contract_call['request'].query == {
        'trucks_order_id': order_id,
    }


async def test_pay_shipping_contract_no_auth(taxi_cargo_trucks, load_json):
    json_request = load_json('shipping_contract_details.json')
    json_request['order_id'] = 'trucks_order_id'
    json_request['event_version'] = 2
    response = await taxi_cargo_trucks.post(
        '/v1/pay/shipping-contract',
        headers={'x-api-key': 'ololo'},
        json=json_request,
    )
    assert response.status_code == 403


async def test_pay_shipping_contract_db(
        taxi_cargo_trucks, load_json, mockserver,
):
    @mockserver.json_handler(
        '/cargo-finance-proxy/internal/cargo-finance/events/dummy-init',
    )
    def _dummy_init(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler(
        '/cargo-finance-proxy/internal/cargo-finance/flow/trucks/events/pay-shipping-contract',
    )
    def _pay_shipping_contract(request):
        return mockserver.make_response(status=200, json={})

    contract_version = 2
    handler_name = '/v1/pay/shipping-contract'
    json_request = load_json('shipping_contract_details.json')
    json_request['order_id'] = 'trucks_order_id'
    json_request['event_version'] = contract_version
    json_request_new = load_json('shipping_contract_details_new.json')
    json_request_new['order_id'] = 'trucks_order_id_new'
    json_request_new['event_version'] = contract_version

    response = await taxi_cargo_trucks.post(
        handler_name,
        headers={'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json=json_request,
    )
    assert response.status_code == 200
    assert _dummy_init.times_called == 1
    assert _pay_shipping_contract.times_called == 1

    response = await taxi_cargo_trucks.post(
        handler_name,
        headers={'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json=json_request,
    )
    assert response.status_code == 200
    assert _dummy_init.times_called == 1
    assert _pay_shipping_contract.times_called == 2

    response = await taxi_cargo_trucks.post(
        handler_name,
        headers={'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json=json_request_new,
    )
    assert response.status_code == 200
    assert _dummy_init.times_called == 2
    assert _pay_shipping_contract.times_called == 3

    response = await taxi_cargo_trucks.post(
        handler_name,
        headers={'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json=json_request_new,
    )
    assert response.status_code == 200
    assert _dummy_init.times_called == 2
    assert _pay_shipping_contract.times_called == 4

    response = await taxi_cargo_trucks.post(
        handler_name,
        headers={'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json=json_request,
    )
    assert response.status_code == 200
    assert _dummy_init.times_called == 2
    assert _pay_shipping_contract.times_called == 5


async def test_pay_shipping_contract_400_dummy(
        taxi_cargo_trucks, load_json, mockserver,
):
    dummy_response_400_code = 400
    dummy_response_400_json = {'message': 'Parse error at pos 247'}

    @mockserver.json_handler(
        '/cargo-finance-proxy/internal/cargo-finance/events/dummy-init',
    )
    def _dummy_init(request):
        return mockserver.make_response(
            status=dummy_response_400_code, json=dummy_response_400_json,
        )

    contract_version = 2
    json_request = load_json('shipping_contract_details.json')
    order_id = 'trucks_order_id'
    json_request['order_id'] = order_id
    json_request['event_version'] = contract_version

    response = await taxi_cargo_trucks.post(
        '/v1/pay/shipping-contract',
        headers={'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json=json_request,
    )
    assert response.status_code == dummy_response_400_code
    assert response.json() == dummy_response_400_json


async def test_pay_shipping_contract_400_pay(
        taxi_cargo_trucks, load_json, mockserver,
):
    pay_response_400_code = 400
    pay_response_400_json = {'message': 'Parse error at pos 257'}

    @mockserver.json_handler(
        '/cargo-finance-proxy/internal/cargo-finance/events/dummy-init',
    )
    def _dummy_init(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler(
        '/cargo-finance-proxy/internal/cargo-finance/flow/trucks/events/pay-shipping-contract',
    )
    def _pay_shipping_contract(request):
        return mockserver.make_response(
            status=pay_response_400_code, json=pay_response_400_json,
        )

    contract_version = 2
    json_request = load_json('shipping_contract_details.json')
    order_id = 'trucks_order_id'
    json_request['order_id'] = order_id
    json_request['event_version'] = contract_version

    response = await taxi_cargo_trucks.post(
        '/v1/pay/shipping-contract',
        headers={'x-api-key': 'dGVzdF9zZWNyZXRfa2V5'},
        json=json_request,
    )
    assert response.status_code == pay_response_400_code
    assert response.json() == pay_response_400_json
