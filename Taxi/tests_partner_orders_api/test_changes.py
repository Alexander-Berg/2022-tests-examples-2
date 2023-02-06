import pytest

HEADERS = {'X-External-Service': 'Gpartner', 'Accept-Language': 'ru'}


@pytest.mark.pgsql('partner_orders_api', files=['add_user.sql'])
async def test_changes(taxi_partner_orders_api, mockserver, load_json):
    int_api_requests = []

    @mockserver.json_handler('/integration-api/v1/changes')
    def _int_api_changes(request):
        int_api_requests.append(request.json)
        return load_json('int_api_changes_response.json')

    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/order/changes',
        headers=HEADERS,
        json=load_json('changes_request.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json('changes_response.json')
    assert int_api_requests == [load_json('int_api_changes_request.json')]


@pytest.mark.pgsql('partner_orders_api', files=['add_user.sql'])
@pytest.mark.parametrize(
    'int_api_status, partner_status, response_json',
    [
        (
            401,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal Server Error'},
        ),
        (
            404,
            404,
            {'code': 'NOT_FOUND', 'message': 'Order or user not found'},
        ),
        (
            500,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal Server Error'},
        ),
    ],
)
async def test_errors(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        int_api_status,
        partner_status,
        response_json,
):
    @mockserver.json_handler('/integration-api/v1/changes')
    def _int_api_changes(request):
        return mockserver.make_response(
            '{"message": "some_text"}', status=int_api_status,
        )

    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/order/changes',
        headers=HEADERS,
        json=load_json('changes_request.json'),
    )
    assert response.status_code == partner_status
    assert response.json() == response_json


async def test_user_not_found(taxi_partner_orders_api, load_json):

    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/order/changes',
        headers=HEADERS,
        json=load_json('changes_request.json'),
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'USER_NOT_FOUND',
        'message': 'User not found',
    }
