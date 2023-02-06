import pytest

ERROR_RESPONSE = {'message': 'Invalid'}
HEADERS = {'X-External-Service': 'Gpartner', 'Accept-Language': 'ru'}
RIGHT_AGENT_USER_ID = '241406a0972b4c4abbf5187e684f0061'
WRONG_AGENT_USER_ID = '1234567890abcdef1234567890abcdef'


@pytest.mark.parametrize(
    'agent_user_id, expected_response',
    [
        (RIGHT_AGENT_USER_ID, {}),
        (
            WRONG_AGENT_USER_ID,
            {
                'code': 'USER_NOT_FOUND',
                'message': 'User not found by agent_user_id',
            },
        ),
    ],
)
@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_order_commit(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        agent_user_id,
        expected_response,
):
    request = load_json('request.json')
    request.update({'agent_user_id': agent_user_id})

    @mockserver.json_handler('/integration-api/v1/orders/commit')
    def _order_commit(_):
        return load_json('int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/commit',
        headers=HEADERS,
        json=request,
    )
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'int_api_status, partner_status, response_json',
    [
        (
            404,
            404,
            {
                'code': 'NOT_FOUND',
                'message': (
                    'Some data record not found or route cannot be constructed'
                ),
            },
        ),
        (406, 406, {'code': 'NOT_ACCEPTABLE', 'message': 'Not acceptable'}),
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
@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_order_commit_forwarding_int_api_errors(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        int_api_status,
        partner_status,
        response_json,
):
    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/orders/commit')
    def _order_commit(request):
        int_api_request = load_json('int_api_request.json')
        assert request.json == int_api_request
        return mockserver.make_response(
            json=ERROR_RESPONSE, status=int_api_status,
        )

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/commit',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == partner_status
    assert response.json() == response_json
