import http

import pytest


@pytest.mark.parametrize(
    'create_data, operation_id, expected_status, expected_content',
    (
        pytest.param(
            {
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
            },
            'c76ba14187e0ffd7b8360e9c50ee3cd8',
            http.HTTPStatus.OK,
            {
                'created_at': '2020-01-01T04:00:00+03:00',
                'created_by': 'test_robot',
                'id': 'c76ba14187e0ffd7b8360e9c50ee3cd8',
                'params': {
                    'commission': 10,
                    'end_date': '2021-01-01',
                    'maxtrips': 10,
                    'price_increase': 1.5,
                    'start_date': '2020-01-01',
                    'tariff_zone': 'moscow',
                    'tariffs': ['econom'],
                    'type': 'nmfg-subventions',
                    'sub_nobrand': 211837,
                    'sub_brand': 170317,
                    'a1': 5,
                    'a2': 0,
                    'm': 20,
                    'hours': [1],
                    'week_days': ['mon'],
                    'subvenion_end_date': '2021-01-01',
                    'subvenion_start_date': '2020-01-01',
                },
                'status': 'CREATED',
                'updated_at': '2020-01-01T04:00:00+03:00',
                'updated_by': 'test_robot',
            },
            id='ok',
        ),
        pytest.param(
            None,
            '6a2887fcca1b786df81ee11dd86d97f3',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'OPERATION_NOT_FOUND',
                'message': (
                    'Operation with '
                    'id="6a2887fcca1b786df81ee11dd86d97f3" not found'
                ),
            },
            id='not_found',
        ),
    ),
)
@pytest.mark.now('2020-01-01T01:00:00+00:00')
async def test_v1_operations_operation_id_get(
        web_app_client,
        create_data,
        operation_id,
        expected_status,
        expected_content,
):
    if create_data is not None:
        await web_app_client.post(
            '/v1/operations/',
            json=create_data,
            headers={'X-Yandex-Login': 'test_robot'},
        )
    response = await web_app_client.get(f'/v1/operations/{operation_id}')
    assert response.status == expected_status, await response.json()
    assert await response.json() == expected_content
