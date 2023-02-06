import pytest


async def test_cancel(
        taxi_cargo_c2c,
        default_pa_headers,
        order_processing_order_cancel_requested,
        create_cargo_c2c_orders,
):
    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/cancel',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'cancel_type': 'free',
            'request_id': '123',
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    assert order_processing_order_cancel_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_1',
                'cancel_type': 'free',
                'accept_language': 'en',
                'request_id': '123',
            },
            'kind': 'order-cancel-requested',
        },
    }


@pytest.mark.parametrize('cancel_type', ['free', 'paid'])
async def test_internal_cancel_handler(
        taxi_cargo_c2c, create_cargo_c2c_orders, mockserver, cancel_type,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/c2c/cancel')
    def _claims_cancel(request):
        assert request.json['cancel_state'] == cancel_type
        return {
            'id': 'id',
            'status': 'cancelled',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/v1/actions/cancel-client-order',
        json={
            'id': {
                'order_provider_id': 'cargo-c2c',
                'order_id': order_id,
                'phone_pd_id': 'phone_pd_id_1',
            },
            'cancel_type': cancel_type,
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200

    response_with_ticket = await taxi_cargo_c2c.post(
        '/v1/actions/cancel-client-order',
        json={
            'id': {
                'order_provider_id': 'cargo-c2c',
                'order_id': order_id,
                'phone_pd_id': 'phone_pd_id_1',
            },
            'cancel_type': cancel_type,
            'user_ticket': 'ticket-123',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response_with_ticket.status_code == 200


async def test_internal_cancel_handler_400(
        taxi_cargo_c2c, create_cargo_c2c_orders, mockserver,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/c2c/cancel')
    def _claims_cancel(request):
        return mockserver.make_response(
            json={'code': 'state_mismatch', 'message': 'message'}, status=409,
        )

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/v1/actions/cancel-client-order',
        json={
            'id': {
                'order_provider_id': 'cargo-c2c',
                'order_id': order_id,
                'phone_pd_id': 'phone_pd_id_1',
            },
            'cancel_type': 'free',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 400
    assert response.json() == {'code': 'state_mismatch', 'message': 'message'}


MARKET_ORDER_ID = 32779352
MARKET_CORP_CLIENT_ID = 'market_corp_client_id____size_32'


@pytest.mark.experiments3(filename='experiment.json')
async def test_market_cancel_old_flow(
        taxi_cargo_c2c,
        default_pa_headers,
        order_processing_order_cancel_requested,
        create_cargo_c2c_orders,
        create_market_orders,
        mockserver,
        get_default_order_id,
        load_json,
):
    await create_market_orders()
    response = await taxi_cargo_c2c.post(
        '/v1/actions/cancel-client-order',
        json={
            'id': {
                'order_provider_id': 'cargo-claims',
                'order_id': 'some_market_id',
                'phone_pd_id': 'phone_pd_id_1',
            },
            'cancel_type': 'free',
            'user_ticket': 'ticket-123',
        },
        headers={'Accept-Language': 'ru'},
    )
    # market no longer works through cargo claims, no cancelation possible
    assert response.status_code == 400


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize('file_name', ['delivering.json'])
async def test_market_cancel(
        taxi_cargo_c2c,
        default_pa_headers,
        order_processing_order_cancel_requested,
        create_logistic_platform_orders,
        mockserver,
        get_default_order_id,
        file_name,
        load_json,
        mock_logistic_platform,
        mock_order_statuses_history,
):
    @mockserver.json_handler('/market-ipa-cancel-orders/api/v1')
    def _market_ipa_cancel_orders_mock(request):
        assert request.json == {
            'params': [
                {'orderId': MARKET_ORDER_ID, 'substatus': 'USER_CHANGED_MIND'},
            ],
        }
        assert request.headers['X-Ya-User-Ticket'] == 'ticket-123'
        return {}

    mock_logistic_platform.file_name = file_name
    mock_order_statuses_history.file_name = file_name
    await create_logistic_platform_orders()
    response = await taxi_cargo_c2c.post(
        '/v1/actions/cancel-client-order',
        json={
            'id': {
                'order_provider_id': 'logistic-platform',
                'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                'phone_pd_id': 'phone_pd_id_1',
            },
            'cancel_type': 'free',
            'user_ticket': 'ticket-123',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize('file_name', ['delivering.json'])
async def test_market_cancel_market_fault(
        taxi_cargo_c2c,
        default_pa_headers,
        order_processing_order_cancel_requested,
        create_logistic_platform_orders,
        mockserver,
        get_default_order_id,
        file_name,
        load_json,
        mock_logistic_platform,
        mock_order_statuses_history,
):
    @mockserver.json_handler('/market-ipa-cancel-orders/api/v1')
    def _market_ipa_cancel_orders_mock(request):
        return mockserver.make_response(
            json=load_json('market_not_found_response.json'),
        )

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response.json')
        return mockserver.make_response(json=resp)

    mock_logistic_platform.file_name = file_name
    mock_order_statuses_history.file_name = file_name
    await create_logistic_platform_orders()
    response = await taxi_cargo_c2c.post(
        '/v1/actions/cancel-client-order',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                'order_provider_id': 'logistic-platform',
            },
            'cancel_type': 'free',
            'user_ticket': 'ticket-123',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'not_found',
        'message': 'Market FAPI request failed',
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_logistic_platform_c2c(
        taxi_cargo_c2c, create_logistic_platform_c2c_orders, mockserver,
):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/c2c/platform/request/cancel',
    )
    def _lp_c2c_cancel(request):
        return {'status': 'CREATED', 'description': 'some_text'}

    order_id = await create_logistic_platform_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/v1/actions/cancel-client-order',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_3',
                'order_id': order_id,
                'order_provider_id': 'logistic-platform-c2c',
            },
            'cancel_type': 'free',
            'user_ticket': 'ticket-123',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
