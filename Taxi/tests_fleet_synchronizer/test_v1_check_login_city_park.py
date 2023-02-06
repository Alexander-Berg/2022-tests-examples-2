import pytest

ENDPOINT_URL = '/fleet-synchronizer/v1/check-login-city-park'


@pytest.mark.config(
    PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
        'uberdriver': {
            'cities': ['Москва', 'CityOne'],
            'enabled': True,
            'park_ids': ['ParkSeven'],
        },
    },
)
@pytest.mark.parametrize(
    'params,expect_code,expect_body,fleet_parks_called',
    [
        pytest.param(
            {'app_family': 'uberdriver'},
            400,
            None,
            0,
            id='Not enough input params',
        ),
        pytest.param(
            {
                'app_family': 'uberdriver',
                'city_id': 'Москва',
                'park_id': 'some_park',
            },
            400,
            None,
            0,
            id='Too many input params',
        ),
        pytest.param(
            {'app_family': 'bad_app', 'city_id': 'Москва'},
            400,
            None,
            0,
            id='Unknown app family (not in config)',
        ),
        pytest.param(
            {'app_family': 'uberdriver', 'city_id': 'Москва'},
            200,
            {'allowed': True},
            0,
            id='Allowed by city',
        ),
        pytest.param(
            {'app_family': 'uberdriver', 'city_id': 'CityTwo'},
            200,
            {'allowed': False},
            0,
            id='Disallowed by city',
        ),
        pytest.param(
            {'app_family': 'uberdriver', 'park_id': 'ParkSeven'},
            200,
            {'allowed': True},
            0,
            id='Allowed by park',
        ),
        pytest.param(
            {'app_family': 'uberdriver', 'park_id': 'ParkOne'},
            200,
            {'allowed': True},
            1,
            id='Allowed by park city (CityOne)',
        ),
        pytest.param(
            {'app_family': 'uberdriver', 'park_id': 'ParkFour'},
            200,
            {'allowed': False},
            1,
            id='Disallowed by park and park city (CityTwo)',
        ),
    ],
)
async def test_v1_check_login_city_park_ok(
        taxi_fleet_synchronizer,
        mock_fleet_parks_list,
        params,
        expect_code,
        expect_body,
        fleet_parks_called,
):
    response = await taxi_fleet_synchronizer.get(ENDPOINT_URL, params=params)
    assert response.status_code == expect_code
    if expect_code == 200:
        assert response.json() == expect_body
    assert mock_fleet_parks_list.times_called == fleet_parks_called


@pytest.mark.config(
    PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
        'uberdriver': {'cities': ['Москва'], 'enabled': True, 'park_ids': []},
    },
)
async def test_v1_check_login_city_park_error(
        taxi_fleet_synchronizer, mock_fleet_parks_list,
):
    mock_fleet_parks_list.return_error = True

    params = {'app_family': 'uberdriver', 'park_id': 'ParkSeven'}
    response = await taxi_fleet_synchronizer.get(ENDPOINT_URL, params=params)
    assert response.status_code == 500
    assert mock_fleet_parks_list.times_called == 3
