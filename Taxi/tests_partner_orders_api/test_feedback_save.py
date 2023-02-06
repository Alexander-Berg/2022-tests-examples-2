import pytest

HEADERS = {'X-External-Service': 'Gpartner', 'Accept-Language': 'ru'}


@pytest.mark.pgsql('partner_orders_api', files=['add_user.sql'])
@pytest.mark.parametrize(
    'feedback_request, api_proxy_request',
    [
        (
            'feedback_request_percent_tips.json',
            'api_proxy_feedback_request_percent_tips.json',
        ),
        (
            'feedback_request_flat_tips.json',
            'api_proxy_feedback_request_flat_tips.json',
        ),
    ],
)
async def test_feedback(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        feedback_request,
        api_proxy_request,
):
    api_proxy_requests = []

    @mockserver.json_handler('/api-proxy/3.0/feedback')
    def _api_proxy_feedback(request):
        api_proxy_requests.append(request.json)
        return {}

    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/feedback/save',
        headers=HEADERS,
        json=load_json(feedback_request),
    )
    assert response.status_code == 200, response.text
    assert response.json() == {}
    assert api_proxy_requests == [load_json(api_proxy_request)]


@pytest.mark.pgsql('partner_orders_api', files=['add_user.sql'])
@pytest.mark.parametrize(
    'api_proxy_status, partner_status, response_json',
    [
        (400, 400, {'code': 'BAD_REQUEST', 'message': 'Bad request'}),
        (
            404,
            404,
            {'code': 'NOT_FOUND', 'message': 'Order or user not found'},
        ),
        (409, 409, {'code': 'CONFLICT', 'message': 'Feedback conflict'}),
        (
            429,
            429,
            {'code': 'TOO_MANY_REQUESTS', 'message': 'Too many requests'},
        ),
    ],
)
async def test_errors(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        api_proxy_status,
        partner_status,
        response_json,
):
    @mockserver.json_handler('/api-proxy/3.0/feedback')
    def _api_proxy_feedback(request):
        return mockserver.make_response(
            '{"code": "some_error"}', status=api_proxy_status,
        )

    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/feedback/save',
        headers=HEADERS,
        json=load_json('feedback_request_percent_tips.json'),
    )
    assert response.status_code == partner_status
    assert response.json() == response_json


async def test_user_not_found(taxi_partner_orders_api, load_json):
    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/feedback/save',
        headers=HEADERS,
        json=load_json('feedback_request_percent_tips.json'),
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'USER_NOT_FOUND',
        'message': 'User not found',
    }
