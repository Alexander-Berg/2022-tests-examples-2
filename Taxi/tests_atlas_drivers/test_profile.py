# flake8: noqa F401, IS001, I202
# pylint: disable=C1801, C5521
import pytest

from tests_atlas_drivers import driver_info
from tests_atlas_drivers.drivers import encode_license
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import fbs_parse


_SAMPLE_DRIVER = driver_info.DriverInfo(
    driver_info.Point(55, 37),
    driver_info.DriverIds(
        '789', '123456', 'udid1', 'A007AA', encode_license('license00'),
    ),
    driver_info.CarClasses(['econom'], [], [], []),
    driver_info.Tags(['tag1', 'tag2']),
)


@pytest.mark.parametrize(
    'required_categories, data_keys',
    [
        (['ids'], ['unique_driver_id', 'car_number', 'license_id']),
        (
            ['ids', 'car_classes'],
            ['unique_driver_id', 'classes', 'car_number', 'license_id'],
        ),
    ],
)
async def test_basic(
        taxi_atlas_drivers, required_categories, data_keys, candidates,
):
    candidates.set_drivers([_SAMPLE_DRIVER])
    candidates.set_data_keys_wanted(data_keys)

    request = {
        'park_id': _SAMPLE_DRIVER.ids.park_id,
        'driver_profile_id': _SAMPLE_DRIVER.ids.driver_profile_id,
        'required_fields': required_categories,
    }
    response = await taxi_atlas_drivers.post('v1/profile', json=request)

    assert response.status_code == 200
    info = fbs_parse.parse_driver_info(response.content)

    driver_info.compare_drivers(info, _SAMPLE_DRIVER, required_categories)


@pytest.mark.config(
    ATLAS_DRIVERS_FETCHERS_ENABLE={
        '__default__': True,
        'car_classes': False,
        'tags': False,
    },
)
async def test_exclude_by_config(taxi_atlas_drivers, candidates):
    candidates.set_drivers([_SAMPLE_DRIVER])
    candidates.set_data_keys_wanted(
        ['unique_driver_id', 'car_number', 'license_id'],
    )

    request = {
        'park_id': _SAMPLE_DRIVER.ids.park_id,
        'driver_profile_id': _SAMPLE_DRIVER.ids.driver_profile_id,
        'required_fields': ['ids', 'car_classes', 'tags'],
    }
    response = await taxi_atlas_drivers.post('v1/profile', json=request)

    assert response.status_code == 200
    info = fbs_parse.parse_driver_info(response.content)

    driver_info.compare_drivers(info, _SAMPLE_DRIVER, ['ids'])


async def test_unknown_driver(taxi_atlas_drivers, candidates):
    candidates.set_drivers([_SAMPLE_DRIVER])
    candidates.set_data_keys_wanted(
        ['unique_driver_id', 'car_number', 'license_id'],
    )

    request = {
        'park_id': 'unknown_park_id',
        'driver_profile_id': _SAMPLE_DRIVER.ids.driver_profile_id,
        'required_fields': ['ids'],
    }
    response = await taxi_atlas_drivers.post('v1/profile', json=request)

    assert response.status_code == 200
    info = fbs_parse.parse_driver_info(response.content)

    assert info is None
