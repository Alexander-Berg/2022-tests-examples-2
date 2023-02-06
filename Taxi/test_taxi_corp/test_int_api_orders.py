import pytest

from taxi_corp.api import routes

BASE_RESPONSE: dict = {'orders': []}


@pytest.mark.parametrize(
    ['passport_mock', 'params', 'expected_code', 'expected_response'],
    [
        pytest.param('client3', None, 200, BASE_RESPONSE, id='client'),
        pytest.param(
            'client3',
            {'user_id': 'test_user_1'},
            200,
            BASE_RESPONSE,
            id='client-user',
        ),
        pytest.param(
            'client3',
            {'since_datetime': '2021-11-30T10:32:00', 'limit': '50'},
            200,
            BASE_RESPONSE,
            id='client-date-limit',
        ),
        pytest.param(
            'client3',
            {'user_id': 'client1_user1'},
            403,
            None,
            id='wrong_user',
        ),
        pytest.param(
            'client_id_unknown', None, 401, None, id='unknown_client',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_api_orders_tanker(
        taxi_corp_real_auth_client,
        mockserver,
        passport_mock,
        params,
        expected_code,
        expected_response,
):
    @mockserver.handler('/corp-orders/v2/orders/tanker')
    async def get_tanker_orders(request):
        return mockserver.make_response(json=BASE_RESPONSE, status=200)

    response = await taxi_corp_real_auth_client.get(
        f'{routes.API_PREFIX}/2.0/orders/tanker', params=params,
    )

    assert response.status == expected_code

    if expected_code == 200:
        response_data = await response.json()
        assert response_data == expected_response

        query = dict(get_tanker_orders.next_call()['request'].query)
        expected_params = {'client_id': passport_mock}
        if params:
            expected_params.update(params)
        assert query == expected_params
