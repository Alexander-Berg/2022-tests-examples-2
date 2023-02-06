import http

import pytest

OPERATION_DATA = {
    'params': {
        'type': 'nmfg-subventions',
        'tariff_zone': 'moscow',
        'maxtrips': 10,
        'commission': 10,
        'start_date': '01.01.2020',
        'end_date': '01.01.2021',
        'tariffs': ['econom'],
        'price_increase': 1.5,
        'sub_nobrand': 211837,
        'sub_brand': 170317,
        'a1': 5,
        'a2': 0,
        'm': 20,
        'hours': [1],
        'week_days': ['mon'],
        'subvenion_start_date': '01.01.2020',
        'subvenion_end_date': '01.01.2021',
    },
}


@pytest.mark.parametrize(
    'create_data, body, expected_status, expected_content',
    (
        pytest.param(
            OPERATION_DATA,
            {
                'limit': 10,
                'statuses': ['CREATED'],
                'param_types': ['nmfg-subventions'],
            },
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2020-01-01T04:00:00+03:00',
                        'created_by': 'test_robot',
                        'id': 'c76ba14187e0ffd7b8360e9c50ee3cd8',
                        'params_type': 'nmfg-subventions',
                        'status': 'CREATED',
                        'tariff_zone': 'moscow',
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 1,
            },
            id='Without custom filter',
        ),
        pytest.param(
            OPERATION_DATA,
            {
                'limit': 10,
                'calculate_continuous_subventions': {'tariff_zone': 'moscow'},
            },
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2020-01-01T04:00:00+03:00',
                        'created_by': 'test_robot',
                        'id': 'c76ba14187e0ffd7b8360e9c50ee3cd8',
                        'params_type': 'nmfg-subventions',
                        'status': 'CREATED',
                        'tariff_zone': 'moscow',
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 1,
            },
            id='With custom filter by moscow',
        ),
        pytest.param(
            OPERATION_DATA,
            {'limit': 10, 'tariff_zone': 'moscow'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2020-01-01T04:00:00+03:00',
                        'created_by': 'test_robot',
                        'id': 'c76ba14187e0ffd7b8360e9c50ee3cd8',
                        'params_type': 'nmfg-subventions',
                        'status': 'CREATED',
                        'tariff_zone': 'moscow',
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 1,
            },
            id='With filter by moscow',
        ),
        pytest.param(
            OPERATION_DATA,
            {
                'limit': 10,
                'calculate_continuous_subventions': {'tariff_zone': 'invalid'},
            },
            http.HTTPStatus.OK,
            {'items': [], 'limit': 10, 'offset': 0, 'total': 0},
            id='With custom filter by invalid zone',
        ),
        pytest.param(
            None,
            {'limit': 10},
            http.HTTPStatus.OK,
            {'items': [], 'limit': 10, 'offset': 0, 'total': 0},
            id='Empty list',
        ),
    ),
)
@pytest.mark.now('2020-01-01T01:00:00')
async def test_v1_operations_get(
        web_app_client, create_data, body, expected_status, expected_content,
):
    if create_data is not None:
        response = await web_app_client.post(
            '/v1/operations/',
            json=create_data,
            headers={'X-Yandex-Login': 'test_robot'},
        )
        assert response.status == http.HTTPStatus.OK, await response.json()
    response = await web_app_client.post('/v1/operations/filter/', json=body)
    assert response.status == expected_status, await response.json()
    assert await response.json() == expected_content
