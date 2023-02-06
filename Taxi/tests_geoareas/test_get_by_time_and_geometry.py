import json

import pytest

from tests_geoareas import common


@pytest.mark.filldb(subvention_geoareas='geo')
@pytest.mark.parametrize(
    'timestamp, top_left, bottom_right, expected_filename',
    [
        (
            1510000000,
            '1.0, 1.0',
            '5.0, 5.0',
            'expected_subvention_geoareas_1.json',
        ),
        (
            1510000000,
            '1.0,1.0',
            '1.0,5.0',
            'expected_subvention_geoareas_1.json',
        ),
        (
            1510000000,
            '1.0, 1.0',
            '1.0, 1.0',
            'expected_subvention_geoareas_1.json',
        ),
        (
            1510000000,
            '-1.0, -1.0',
            '-1.0, -1.0',
            'expected_subvention_geoareas_3.json',
        ),
        (
            1460000000,
            '1.0, 1.0',
            '1.0, 1.0',
            'expected_subvention_geoareas_1_old.json',
        ),
        (
            1550000000,
            '1.0, 1.0',
            '15.0, 15.0',
            'expected_subvention_geoareas_both.json',
        ),
        (
            1510000000,
            '18.0, 18.0',
            '19.0, 19.0',
            'expected_subvention_geoareas_empty.json',
        ),
    ],
)
async def test_get_subvention_geoareas_geometry(
        taxi_geoareas,
        load_json,
        timestamp,
        top_left,
        bottom_right,
        expected_filename,
):
    if top_left == bottom_right:
        params = {'point': top_left, 'timestamp': timestamp}
    else:
        params = {
            'top_left': top_left,
            'bottom_right': bottom_right,
            'timestamp': timestamp,
        }

    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/geoareas_by_time_and_geometry',
        params=params,
    )

    assert res.status_code == 200

    res_data = json.loads(res.content)
    expected = load_json(expected_filename)

    res_data_geoareas = sorted(res_data['geoareas'], key=lambda k: k['name'])
    expected_geoareas = sorted(expected['geoareas'], key=lambda k: k['name'])

    assert res_data_geoareas == common.deep_approx(expected_geoareas)


@pytest.mark.config(GEOAREAS_SERVICE_ENABLED=False)
async def test_break_service_check(taxi_geoareas):
    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/geoareas_by_time_and_geometry',
        params={'timestamp': 0},
    )

    assert res.status_code == 500
    assert res.json()['code'] == 'service_disabled'


@pytest.mark.parametrize(
    'params, error_msg',
    [
        (
            {
                'timestamp': 0,
                'point': '0,0',
                'top_left': '1,0',
                'bottom_right': '0,1',
            },
            'point and top_left, bottom_right cannot be '
            'specified at the same time',
        ),
        (
            {'timestamp': 0},
            'point or top_left, bottom_right must be specified',
        ),
        (
            {'timestamp': 0, 'top_left': '1,0'},
            'point or top_left, bottom_right must be specified',
        ),
        (
            {'timestamp': 0, 'bottom_right': '0,1'},
            'point or top_left, bottom_right must be specified',
        ),
    ],
)
async def test_break_wrong_parameters(taxi_geoareas, params, error_msg):
    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/geoareas_by_time_and_geometry',
        params=params,
    )

    assert res.status_code == 400
    assert res.json()['message'] == error_msg
