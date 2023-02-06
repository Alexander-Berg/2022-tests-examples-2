import pytest


@pytest.mark.parametrize(
    ['user_id', 'expected_result'],
    [
        pytest.param(
            'client1_user2',
            {
                'items': [
                    {
                        'geo': {
                            'center': [37.642453, 55.735596],
                            'radius': 1000,
                        },
                        'geo_type': 'circle',
                        'id': 'destination_restriction_id',
                        'name': 'dest_name_1',
                    },
                    {
                        'geo': {
                            'center': [37.642453, 55.735596],
                            'radius': 1000,
                        },
                        'geo_type': 'circle',
                        'id': 'source_restriction_1',
                        'name': 'source_name_1',
                    },
                ],
            },
        ),
    ],
)
async def test_geo_restrictions_by_user(
        web_app_client, user_id, expected_result,
):
    response = await web_app_client.get(
        '/v1/geo_restrictions/search_by_user', params={'user_id': user_id},
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    assert response_json == expected_result


@pytest.mark.parametrize(
    ['user_id', 'status_code'],
    [pytest.param('not_existed_user', 404, id='not found')],
)
async def test_geo_restrictions_by_user_fail(
        web_app_client, user_id, status_code,
):
    response = await web_app_client.get(
        '/v1/geo_restrictions/search_by_user', params={'user_id': user_id},
    )
    assert response.status == status_code
    response_data = await response.json()
    assert response_data == {
        'code': 'NOT_FOUND',
        'message': 'Not found',
        'reason': 'User not_existed_user not found',
    }
