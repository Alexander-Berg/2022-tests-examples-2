import pytest

ENDPOINT = '/driver/v1/deptrans-status/v1/profile/available'


def _get_headers(park_id, profile_driver_id):
    return {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': profile_driver_id,
        'X-Request-Application-Version': '9.60 (1234)',
    }


@pytest.mark.parametrize(
    'park_id, profile_driver_id, result, lon, lat, categories',
    [
        pytest.param(
            'park1',
            'driver1',
            True,
            0,
            0,
            ['comfort'],
            id='Has permanent profile',
        ),
        pytest.param(
            'park2',
            'driver1',
            True,
            0,
            0,
            ['comfort'],
            id='Has temporary profile',
        ),
        pytest.param(
            'park1',
            'driver2',
            True,
            0,
            0,
            ['comfort'],
            id="""Does not have anything only falses, but available
                because in deptrans_profiles""",
        ),
        pytest.param(
            'park2',
            'driver2',
            True,
            37.5,
            55.5,
            ['econom'],
            id="""Does not have anything even falses, but available
                because of coordinates, category and country""",
        ),
        pytest.param(
            'park2', 'driver2', False, 0, 0, ['econom'], id='Bad coordinates',
        ),
        pytest.param(
            'park2',
            'driver2',
            False,
            37.5,
            55.5,
            ['comfort'],
            id='Bad category',
        ),
        pytest.param(
            'park3',
            'driver2',
            False,
            37.5,
            55.5,
            ['comfort'],
            id='Bad country',
        ),
        pytest.param(
            'park3',
            'driver6',
            False,
            37.5,
            55.5,
            ['comfort'],
            id="""Does not have anything even falses, but available
                because country is null, and coordinates, category
                are appropriate""",
        ),
        pytest.param(
            'park2',
            'driver2',
            False,
            0,
            0,
            ['comfort'],
            id='Is not in deptrans_profiles',
        ),
    ],
)
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={'supported_zones': ['moscow']},
    DEPTRANS_DRIVER_STATUS_SUPPORTED_COUNTRIES={
        'supported_countries': ['rus', 'oth', 'blr'],
    },
    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
        'supported_categories': ['econom'],
    },
)
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_get_deptrans_profile_available(
        taxi_deptrans_driver_status,
        park_id,
        profile_driver_id,
        result,
        lon,
        lat,
        categories,
        driver_trackstory,
        personal,
        driver_categories_api,
):
    driver_trackstory.set_data(f'{park_id}_{profile_driver_id}', lon, lat)
    driver_categories_api.set_data(
        f'{park_id}_{profile_driver_id}', categories,
    )

    response = await taxi_deptrans_driver_status.get(
        ENDPOINT, headers=_get_headers(park_id, profile_driver_id),
    )
    assert response.status_code == 200
    assert response.json() == {'is_available': result}


@pytest.mark.parametrize(
    [
        'park_id',
        'profile_driver_id',
        'lon',
        'lat',
        'categories',
        'is_zone_excluded',
        'is_categories_excluded',
        'zones_timeout',
        'categories_timeout',
    ],
    [
        pytest.param(
            'park2',
            'driver2',
            37.5,
            55.5,
            ['econom'],
            True,
            False,
            0,
            0,
            id="""Not in deptrans_profiles. Good country, but zone is empty""",
        ),
        pytest.param(
            'park2',
            'driver2',
            37.5,
            55.5,
            ['econom'],
            False,
            True,
            0,
            0,
            id="""Not in deptrans_profiles. Good country,
                but categories are empty""",
        ),
        pytest.param(
            'park2',
            'driver2',
            37.5,
            55.5,
            ['econom'],
            True,
            True,
            0,
            0,
            id="""Not in deptrans_profiles. Good country,
                but zone and categories are empty""",
        ),
        pytest.param(
            'park2',
            'driver2',
            37.5,
            55.5,
            ['econom'],
            False,
            False,
            1000,
            0,
            id="""Not in deptrans_profiles. Good country,
                but zone is unavailable""",
        ),
        pytest.param(
            'park2',
            'driver2',
            37.5,
            55.5,
            ['econom'],
            False,
            False,
            0,
            1000,
            id="""Not in deptrans_profiles. Good country,
                but categories are unavailable""",
        ),
        pytest.param(
            'park2',
            'driver2',
            37.5,
            55.5,
            ['econom'],
            False,
            False,
            1000,
            1000,
            id="""Not in deptrans_profiles. Good country,
                but categories and zones are unavailable""",
        ),
    ],
)
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={'supported_zones': ['moscow']},
    DEPTRANS_DRIVER_STATUS_SUPPORTED_COUNTRIES={
        'supported_countries': ['rus', 'oth', 'blr'],
    },
    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
        'supported_categories': ['econom'],
    },
)
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_get_deptrans_profile_not_available(
        taxi_deptrans_driver_status,
        park_id,
        profile_driver_id,
        lon,
        lat,
        categories,
        driver_trackstory,
        personal,
        is_zone_excluded,
        is_categories_excluded,
        zones_timeout,
        categories_timeout,
        driver_categories_api,
):
    driver_id = f'{park_id}_{profile_driver_id}'

    if is_zone_excluded:
        driver_trackstory.exclude_driver(driver_id)
    else:
        driver_trackstory.set_data(driver_id, lon, lat)
    driver_trackstory.set_timeouts_count(zones_timeout)

    if is_categories_excluded:
        driver_categories_api.exclude_driver(driver_id)
    else:
        driver_categories_api.set_data(driver_id, categories)
    driver_categories_api.set_timeouts_count(categories_timeout)

    response = await taxi_deptrans_driver_status.get(
        ENDPOINT, headers=_get_headers(park_id, profile_driver_id),
    )
    if zones_timeout or categories_timeout:
        assert response.status_code == 500
        assert response.json()['message'] == 'Internal Server Error'
    else:
        assert response.status_code == 200
        assert response.json() == {'is_available': False}
