import pytest

from rida import consts
from test_rida import experiments_utils
from test_rida import helpers

IOS_PARAMS = {
    'deviceType': 'iPhone',
    'deviceScale': '2',
    'osVersion': '12.5.3',
    'applicationVersion': '200700',
    'applicationVersionName': '2.4.0',
    'deviceBrandModel': 'iPhone7,1',
    'applicationId': '05CD3E1E-39DC-48FA-B217-00705B75CE68',
}


@pytest.mark.now('2020-02-26T13:50:00.000')
@pytest.mark.translations()
@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.parametrize(
    ['header', 'request_body', 'expected_driver_coordinates'],
    [
        pytest.param(
            {},
            {'lat': 0.00, 'lng': 0.00, 'country_id': 1},
            [],
            id='zero-position',
            marks=experiments_utils.get_dispatch_exp(
                nearest_visible_drivers_limit=5,
            ),
        ),
        pytest.param(
            {},
            {'lat': 20.00001, 'lng': 20.00001, 'country_id': 1},
            [
                [20.00001, 20.00001],
                [20.00002, 20.00002],
                [20.00003, 20.00003],
                [20.00004, 20.00004],
                [20.00005, 20.00005],
                [20.00006, 20.00006],
            ],
            id='max-10-visible[not-authorized]',
        ),
        pytest.param(
            helpers.get_auth_headers(1234),
            {'lat': 20.00001, 'lng': 20.00001, 'country_id': 1},
            [[20.00002, 20.00002]],
            id='max-2-visible[driver-as-passenger]',
            marks=experiments_utils.get_dispatch_exp(
                nearest_visible_drivers_limit=2,
            ),
        ),
        pytest.param(
            helpers.get_auth_headers(1234),
            {'lat': 20.00001, 'lng': 20.00001, 'country_id': 1},
            [
                [20.00002, 20.00002],
                [20.00003, 20.00003],
                [20.00004, 20.00004],
                [20.00005, 20.00005],
                [20.00006, 20.00006],
            ],
            id='max-10-visible[driver-as-passenger]',
            marks=experiments_utils.get_dispatch_exp(
                nearest_visible_drivers_limit=(
                    consts.NEAR_VISIBLE_DRIVERS_LIMIT
                ),
            ),
        ),
        pytest.param(
            helpers.get_auth_headers(1234),
            {'lat': '20.00001', 'lng': '20.00001', 'country_id': 1},
            [
                [20.00002, 20.00002],
                [20.00003, 20.00003],
                [20.00004, 20.00004],
                [20.00005, 20.00005],
                [20.00006, 20.00006],
            ],
            id='max-10-visible[location-as-string]',
            marks=experiments_utils.get_dispatch_exp(
                nearest_visible_drivers_limit=(
                    consts.NEAR_VISIBLE_DRIVERS_LIMIT
                ),
            ),
        ),
        pytest.param(
            helpers.get_auth_headers(1234),
            {'lat': 20.00001, 'lng': 20.00001, 'country_id': 1},
            [],
            id='max-10-visible[small-radius]',
            marks=experiments_utils.get_dispatch_exp(
                nearest_visible_drivers_limit=(
                    consts.NEAR_VISIBLE_DRIVERS_LIMIT
                ),
                max_search_distance_meters=1,
            ),
        ),
        pytest.param(
            helpers.get_auth_headers(1234),
            {'lat': 20.00001, 'lng': 20.00001, 'country_id': 1},
            [
                [20.00002, 20.00002],
                [20.00003, 20.00003],
                [20.00004, 20.00004],
                [20.00005, 20.00005],
                [20.00006, 20.00006],
            ],
            id='max-10-visible[nearest_visible_drivers_limit-is-None]',
            marks=experiments_utils.get_dispatch_exp(),
        ),
    ],
)
@pytest.mark.filldb()
async def test_get_near_drivers_logic(
        web_app_client, header, request_body, expected_driver_coordinates,
):
    response = await web_app_client.post(
        '/v1/getNearDrivers', headers=header, json=request_body,
    )
    data = await response.json()
    assert data['data'] == expected_driver_coordinates


@pytest.mark.now('2020-02-26T13:50:00.000')
@pytest.mark.translations()
@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.parametrize(
    ['request_body_as_query'],
    [
        pytest.param(False, id='request_body_as_json'),
        pytest.param(True, id='request_body_as_query'),
    ],
)
@pytest.mark.filldb()
async def test_get_near_drivers_format(web_app_client, request_body_as_query):
    header = helpers.get_auth_headers(1234)
    request_body = {'lat': 20.00001, 'lng': 20.00001, 'country_id': 1}
    expected_driver_coordinates = [
        [20.00002, 20.00002],
        [20.00003, 20.00003],
        [20.00004, 20.00004],
        [20.00005, 20.00005],
        [20.00006, 20.00006],
    ]
    if request_body_as_query:
        request_params = {'data': request_body}
        header['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        request_params = {'json': request_body}
        header['Content-Type'] = 'application/json'
    request_params['headers'] = header
    response = await web_app_client.post(
        '/v1/getNearDrivers', **request_params,
    )
    data = await response.json()
    assert data['data'] == expected_driver_coordinates
