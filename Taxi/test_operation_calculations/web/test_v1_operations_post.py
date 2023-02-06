import http

import pytest


@pytest.mark.parametrize(
    'body, try_twice, expected_status, expected_content',
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
                    'a1': 5.1,
                    'a2': 0,
                    'm': 20,
                    'hours': [1],
                    'week_days': ['mon'],
                    'subvenion_start_date': '01.01.2020',
                    'subvenion_end_date': '01.01.2021',
                },
            },
            False,
            http.HTTPStatus.OK,
            {
                'created_at': '2020-01-01T04:00:00+03:00',
                'created_by': 'test_robot',
                'id': 'a5dcff20c0881c533076436fbc2bf6b0',
                'params': {
                    'type': 'nmfg-subventions',
                    'commission': 10,
                    'end_date': '2021-01-01',
                    'maxtrips': 10,
                    'price_increase': 1.5,
                    'start_date': '2020-01-01',
                    'tariff_zone': 'moscow',
                    'tariffs': ['econom'],
                    'sub_nobrand': 211837,
                    'sub_brand': 170317,
                    'a1': 5.1,
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
            id='ok-brand-and-nobrand',
        ),
        pytest.param(
            {
                'params': {
                    'type': 'brand-nmfg-subventions',
                    'tariff_zone': 'moscow',
                    'maxtrips': 10,
                    'commission': 10,
                    'start_date': '01.01.2020',
                    'end_date': '01.01.2021',
                    'tariffs': ['econom'],
                    'price_increase': 1.5,
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
            False,
            http.HTTPStatus.OK,
            {
                'created_at': '2020-01-01T04:00:00+03:00',
                'created_by': 'test_robot',
                'id': 'fc4ab68da77fbd58834c69c90c3fb3a4',
                'params': {
                    'type': 'brand-nmfg-subventions',
                    'commission': 10,
                    'end_date': '2021-01-01',
                    'maxtrips': 10,
                    'price_increase': 1.5,
                    'start_date': '2020-01-01',
                    'tariff_zone': 'moscow',
                    'tariffs': ['econom'],
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
            id='ok-brand',
        ),
        pytest.param(
            {
                'params': {
                    'type': 'nobrand-nmfg-subventions',
                    'tariff_zone': 'moscow',
                    'maxtrips': 10,
                    'commission': 10,
                    'start_date': '01.01.2020',
                    'end_date': '01.01.2021',
                    'tariffs': ['econom'],
                    'price_increase': 1.5,
                    'sub_nobrand': 170317,
                    'a1': 5,
                    'a2': 0,
                    'm': 20,
                    'hours': [1],
                    'week_days': ['mon'],
                    'subvenion_start_date': '01.01.2020',
                    'subvenion_end_date': '01.01.2021',
                },
            },
            False,
            http.HTTPStatus.OK,
            {
                'created_at': '2020-01-01T04:00:00+03:00',
                'created_by': 'test_robot',
                'id': 'c6d943d84a7fa34c8e290ab9df1a5565',
                'params': {
                    'type': 'nobrand-nmfg-subventions',
                    'commission': 10,
                    'end_date': '2021-01-01',
                    'maxtrips': 10,
                    'price_increase': 1.5,
                    'start_date': '2020-01-01',
                    'tariff_zone': 'moscow',
                    'tariffs': ['econom'],
                    'sub_nobrand': 170317,
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
            id='ok-nobrand',
        ),
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
            True,
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'DUPLICATE', 'message': 'operations already exist'},
            id='duplicate',
        ),
    ),
)
@pytest.mark.now('2020-01-01T01:00:00+00:00')
async def test_v1_calculate_subventions_continuous_post(
        web_app_client, body, expected_status, expected_content, try_twice,
):
    if try_twice:
        await web_app_client.post(
            '/v1/operations/',
            json=body,
            headers={'X-Yandex-Login': 'test_robot'},
        )
    response = await web_app_client.post(
        '/v1/operations/', json=body, headers={'X-Yandex-Login': 'test_robot'},
    )
    assert response.status == expected_status, await response.json()
    assert await response.json() == expected_content

    if response.status == http.HTTPStatus.OK:
        operation_id = expected_content['id']
        response_get = await web_app_client.get(
            f'/v1/operations/{operation_id}/',
        )
        assert response_get.status == http.HTTPStatus.OK
        assert await response_get.json() == expected_content
