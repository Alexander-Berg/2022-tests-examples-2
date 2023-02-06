# pylint: disable=redefined-outer-name
import http
import json

import pytest


@pytest.fixture
def expected_couriers_data(open_file):
    with open_file(
            'expected_couriers_info.json', mode='rb', encoding=None,
    ) as fp:
        test_data = json.load(fp)
    return test_data


@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas': {
            '/api/v2/foodtech/couriers': {
                'run_modes': {'atlas_clickhouse': False},
                'run_permission': False,
            },
        },
    },
)
async def test_get_couriers_disabled(atlas_blackbox_mock, web_app_client):
    response = await web_app_client.post(
        '/api/v2/foodtech/couriers',
        json={
            'area': {
                'tl': {'lat': 56.072737, 'lon': 36.902971},
                'br': {'lat': 55.313084, 'lon': 38.324771},
            },
            'free_time': 200,
        },
    )
    assert response.status == http.HTTPStatus.INTERNAL_SERVER_ERROR


async def test_get_couriers_disabled_no_config(
        atlas_blackbox_mock, web_app_client,
):
    response = await web_app_client.post(
        '/api/v2/foodtech/couriers',
        json={
            'area': {
                'tl': {'lat': 56.072737, 'lon': 36.902971},
                'br': {'lat': 55.313084, 'lon': 38.324771},
            },
            'free_time': 200,
        },
    )
    assert response.status == http.HTTPStatus.INTERNAL_SERVER_ERROR


@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas': {
            '/api/v2/foodtech/couriers': {
                'run_modes': {'atlas_clickhouse': False},
                'run_permission': True,
            },
        },
    },
)
@pytest.mark.now('2022-01-11T10:50:00+0300')
@pytest.mark.parametrize(
    'query_params, expected_courier_ids',
    [
        (
            {
                'area': {
                    'tl': {'lat': 56.072737, 'lon': 36.902971},
                    'br': {'lat': 55.313084, 'lon': 38.324771},
                },
            },
            ['1', '2', '3', '4'],
        ),
        (
            {
                'area': {
                    'tl': {'lat': 56.072737, 'lon': 36.902971},
                    'br': {'lat': 55.813084, 'lon': 38.324771},
                },
            },
            ['1'],
        ),
        (
            {
                'area': {
                    'tl': {'lat': 56.072737, 'lon': 36.902971},
                    'br': {'lat': 55.313084, 'lon': 38.324771},
                },
                'shift_type': 'plan',
            },
            ['4'],
        ),
        (
            {
                'area': {
                    'tl': {'lat': 56.072737, 'lon': 36.902971},
                    'br': {'lat': 55.313084, 'lon': 38.324771},
                },
                'service': 'lavka',
            },
            ['1', '2'],
        ),
        (
            {
                'area': {
                    'tl': {'lat': 56.072737, 'lon': 36.902971},
                    'br': {'lat': 55.313084, 'lon': 38.324771},
                },
                'status': 'free',
            },
            ['2', '3', '4'],
        ),
        (
            {
                'area': {
                    'tl': {'lat': 56.072737, 'lon': 36.902971},
                    'br': {'lat': 55.313084, 'lon': 38.324771},
                },
                'free_time': 1800,
            },
            ['3', '4'],
        ),
    ],
)
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['wms_couriers.sql'],
)
async def test_get_couriers(
        atlas_blackbox_mock,
        web_app_client,
        mock_positions,
        expected_couriers_data,
        query_params,
        expected_courier_ids,
):
    response = await web_app_client.post(
        '/api/v2/foodtech/couriers', json=query_params,
    )
    assert response.status == http.HTTPStatus.OK
    result = await response.json()

    assert len(result) == len(expected_courier_ids)
    for courier_info in result:
        cour_id = courier_info['courier']['id']
        assert cour_id in expected_courier_ids
        assert courier_info == expected_couriers_data[cour_id]
