import pytest

ERROR_RESPONSE = {'message': 'Invalid'}
HEADERS = {'X-External-Service': 'Gpartner', 'Accept-Language': 'ru'}


@pytest.mark.pgsql('partner_orders_api', files=['agent_users.sql'])
async def test_order_cancel_base(
        taxi_partner_orders_api, mockserver, load_json,
):
    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/orders/cancel')
    def _order_cancel(request):
        int_api_request = load_json('int_api_request.json')
        assert request.json == int_api_request
        return load_json('int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/cancel',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    'int_api_status, int_api_response_json, partner_status, response_json',
    [
        (
            400,
            {'code': 'BAD_REQUEST', 'message': 'BAD_REQUEST'},
            400,
            {'code': 'BAD_REQUEST', 'message': 'Invalid request parameters'},
        ),
        (
            401,
            {},
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
        (
            404,
            {},
            404,
            {
                'code': 'NOT_FOUND',
                'message': (
                    'Some data record not found or route cannot be constructed'
                ),
            },
        ),
        (
            409,
            {'error': {'code': 'PROC_NOT_FOUND', 'text': 'PROC_NOT_FOUND'}},
            404,
            {
                'message': 'Cancelable order not found, cannot cancel',
                'code': 'ORDER_NOT_FOUND',
            },
        ),
        (
            409,
            {'error': {'code': 'IS_CARGO_ORDER', 'text': 'IS_CARGO_ORDER'}},
            404,
            {
                'message': 'Cancelable order not found, cannot cancel',
                'code': 'ORDER_NOT_FOUND',
            },
        ),
        (
            409,
            {'error': {'code': 'NOT_YOUR_ORDER', 'text': 'NOT_YOUR_ORDER'}},
            404,
            {
                'message': 'Cancelable order not found, cannot cancel',
                'code': 'ORDER_NOT_FOUND',
            },
        ),
        (
            409,
            {
                'error': {
                    'code': 'NOT_PENDING_ANYMORE',
                    'text': 'NOT_PENDING_ANYMORE',
                },
            },
            409,
            {
                'message': 'Conflict while canceling order',
                'code': 'NOT_CANCELABLE_STATUS',
            },
        ),
        (
            409,
            {
                'error': {
                    'code': 'NOT_CANCELLABLE_STATUS',
                    'text': 'NOT_CANCELLABLE_STATUS',
                },
            },
            409,
            {
                'message': 'Conflict while canceling order',
                'code': 'NOT_CANCELABLE_STATUS',
            },
        ),
        (
            409,
            {
                'error': {
                    'code': 'BY_ALGORITHM_DECISION',
                    'text': 'BY_ALGORITHM_DECISION',
                },
            },
            409,
            {
                'message': 'Conflict while canceling order',
                'code': 'NOT_CANCELABLE_STATUS',
            },
        ),
        (
            409,
            {
                'error': {
                    'code': 'PAID_CANCEL_IS_DISABLED',
                    'text': 'PAID_CANCEL_IS_DISABLED',
                },
            },
            409,
            {
                'message': 'Conflict while canceling order',
                'code': 'NOT_CANCELABLE_STATUS',
            },
        ),
        (
            409,
            {
                'error': {
                    'code': 'NOT_A_FREE_CANCEL',
                    'text': 'NOT_A_FREE_CANCEL',
                },
            },
            409,
            {
                'message': 'Conflict while canceling order',
                'code': 'NOT_CANCELABLE_STATUS',
            },
        ),
        (
            409,
            {
                'error': {
                    'code': 'CANNOT_CANCEL_YOU_ARE_IN_CAR',
                    'text': 'CANNOT_CANCEL_YOU_ARE_IN_CAR',
                },
            },
            409,
            {
                'message': 'Conflict while canceling order',
                'code': 'CANNOT_CANCEL_YOU_ARE_IN_CAR',
            },
        ),
        (
            409,
            {
                'error': {
                    'code': 'INCOMPATIBLE_CANCEL_STATE',
                    'text': 'INCOMPATIBLE_CANCEL_STATE',
                },
                'cancel_rules': {
                    'message': 'Cancellation time is over',
                    'message_support': (
                        'Please indicate if the driver\'s at fault. Describe'
                        ' what happened — we will check everything,'
                        ' and correct the situation.'
                    ),
                    'state': 'disabled',
                    'title': 'Cancellation is unavailable',
                },
            },
            409,
            {
                'message': 'Conflict while canceling order',
                'code': 'INCOMPATIBLE_CANCEL_STATE',
                'cancel_rules': {
                    'state': 'disabled',
                    'title': 'Cancellation is unavailable',
                    'message': 'Cancellation time is over',
                },
            },
        ),
        (
            500,
            {},
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
    ],
)
@pytest.mark.pgsql('partner_orders_api', files=['agent_users.sql'])
async def test_order_cancel_forwarding_error_response(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        int_api_status,
        int_api_response_json,
        partner_status,
        response_json,
):
    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/orders/cancel')
    def _order_cancel(request):
        int_api_request = load_json('int_api_request.json')
        assert request.json == int_api_request
        return mockserver.make_response(
            json=int_api_response_json, status=int_api_status,
        )

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/cancel',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == partner_status
    assert response.json() == response_json
