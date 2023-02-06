import pytest

HEADERS = {'X-External-Service': 'Gpartner', 'Accept-Language': 'ru'}
RIGHT_AGENT_USER_ID = '241406a0972b4c4abbf5187e684f0061'
WRONG_AGENT_USER_ID = '1234567890abcdef1234567890abcdef'


@pytest.mark.parametrize(
    'agent_user_id, int_api_status, expected_response, expected_code',
    [
        (
            RIGHT_AGENT_USER_ID,
            'pending',
            {
                'change_id': 'b0d2e97f806b49ef822bd250dd2c5934',
                'name': 'user_ready',
                'status': 'pending',
            },
            202,
        ),
        (
            RIGHT_AGENT_USER_ID,
            'success',
            {
                'change_id': 'b0d2e97f806b49ef822bd250dd2c5934',
                'name': 'user_ready',
                'status': 'success',
            },
            200,
        ),
        (
            WRONG_AGENT_USER_ID,
            'success',
            {'code': 'USER_NOT_FOUND', 'message': 'User not found'},
            404,
        ),
    ],
)
@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_v1rider_is_coming_base(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        agent_user_id,
        int_api_status,
        expected_response,
        expected_code,
):
    request = load_json('request.json')
    request.update({'agent_user_id': agent_user_id})

    @mockserver.json_handler('/integration-api/v1/changeaction')
    def _change_action(request):
        int_api_request = load_json('int_api_request.json')
        assert request.json == int_api_request
        response = load_json('int_api_response.json')
        response.update({'status': int_api_status})
        return response

    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/rider-is-coming',
        headers=HEADERS,
        json=request,
    )
    assert response.json() == expected_response
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'int_api_code,response_code,response_json',
    [
        (
            404,
            404,
            {'code': 'NOT_FOUND', 'message': 'Some data record not found'},
        ),
        (
            406,
            406,
            {'code': 'NOT_ACCEPTABLE', 'message': 'Change not acceptable'},
        ),
        (
            409,
            409,
            {
                'code': 'CONFLICT',
                'message': (
                    'Notification "rider_is_coming" has been already sent'
                ),
            },
        ),
        (
            500,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
    ],
)
@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_forwarding_in_api_errors(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        int_api_code,
        response_code,
        response_json,
):
    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/changeaction')
    def _change_destinations(_):
        return mockserver.make_response('{}', int_api_code)

    response = await taxi_partner_orders_api.post(
        '/agent/partner-orders-api/v1/rider-is-coming',
        headers=HEADERS,
        json=request,
    )

    assert response.status_code == response_code
    assert response.json() == response_json
