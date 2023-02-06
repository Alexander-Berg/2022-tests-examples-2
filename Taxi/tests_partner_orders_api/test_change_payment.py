import pytest

HEADERS = {'X-External-Service': 'Gpartner', 'Accept-Language': 'ru'}


@pytest.mark.pgsql('partner_orders_api', files=['agent_users.sql'])
async def test_v1_change_payment_positive(
        taxi_partner_orders_api, mockserver, load_json,
):
    @mockserver.json_handler('/integration-api/v1/changepayment')
    def _change_payment(request):
        int_api_request = load_json('int_api_request.json')
        assert request.json == int_api_request
        return load_json('int_api_response.json')

    request = load_json('request.json')
    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/order/change-payment',
        headers=HEADERS,
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json('response.json')


@pytest.mark.pgsql('partner_orders_api', files=['agent_users.sql'])
@pytest.mark.parametrize(
    'int_api_code,response_code,response_json',
    [
        (400, 400, {'code': 'BAD_REQUEST', 'message': 'Invalid request'}),
        (
            401,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
        (404, 404, {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}),
        (
            405,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
        (
            406,
            406,
            {'code': 'NOT_ACCEPTABLE', 'message': 'Change not acceptable'},
        ),
        (
            409,
            409,
            {'code': 'ALREADY_CHANGED', 'message': 'Payment already changed'},
        ),
        (
            429,
            429,
            {'code': 'TOO_MANY_REQUESTS', 'message': 'Too many requests'},
        ),
        (
            500,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
    ],
)
async def test_v1_change_payment(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        int_api_code,
        response_code,
        response_json,
):
    @mockserver.json_handler('/integration-api/v1/changepayment')
    def _change_payment(_):
        return mockserver.make_response('{}', int_api_code)

    request = load_json('request.json')
    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/order/change-payment',
        headers=HEADERS,
        json=request,
    )

    assert response.status_code == response_code
    assert response.json() == response_json


async def test_v1_change_payment_user_not_found(
        taxi_partner_orders_api, mockserver, load_json,
):
    @mockserver.json_handler('/integration-api/v1/changepayment')
    def _change_payment(_):
        return mockserver.make_response('{}', 200)

    request = load_json('request.json')
    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/order/change-payment',
        headers=HEADERS,
        json=request,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'USER_NOT_FOUND',
        'message': 'User not found',
    }
