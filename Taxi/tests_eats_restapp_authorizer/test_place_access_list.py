import pytest


@pytest.mark.parametrize(
    'partner_id, restaurants, mock_times, expected_response',
    [
        pytest.param(111, [], 0, {'place_ids': [1, 2, 5]}),
        pytest.param(112, [], 1, {'place_ids': []}),
        pytest.param(113, [2, 10], 1, {'place_ids': [2, 10]}),
    ],
)
@pytest.mark.redis_store(['sadd', 'partner:places:111', '1', '2', '5'])
async def test_place_access_list(
        taxi_eats_restapp_authorizer,
        partner_id,
        expected_response,
        mockserver,
        restaurants,
        mock_times,
):
    @mockserver.json_handler(f'/eats-vendor/api/v1/server/users/{partner_id}')
    def mock_vendor(request):
        return mockserver.make_response(
            status=200,
            json={
                'isSuccess': True,
                'payload': {
                    'id': 7,
                    'restaurants': restaurants,
                    'isFastFood': True,
                    'timezone': 'Europe/Moscow',
                    'roles': [
                        {
                            'id': 3,
                            'title': 'Оператор',
                            'role': 'ROLE_OPERATOR',
                        },
                        {
                            'id': 4,
                            'title': 'Управляющий',
                            'role': 'ROLE_MANAGER',
                        },
                    ],
                    'firstLoginAt': '2020-08-28T15:11:25+03:00',
                },
            },
        )

    response = await taxi_eats_restapp_authorizer.post(
        '/place-access/list', json={'partner_id': partner_id},
    )

    assert mock_vendor.times_called == mock_times

    assert response.status_code == 200
    response_json = response.json()
    response_json['place_ids'].sort()
    assert response_json == expected_response
