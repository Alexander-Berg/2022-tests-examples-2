# flake8: noqa F401, IS001, I202
# pylint: disable=C1801, C5521, W0612
import pytest

from tests_atlas_drivers import driver_info
from tests_atlas_drivers import drivers
from tests_atlas_drivers.drivers import encode_license
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import fbs_parse


_PAYMENT_METHODS = ['cash', 'card']
_SAMPLE_DRIVERS = [
    driver_info.DriverInfo(
        driver_info.Point(37.5, 55.5),
        driver_info.DriverIds(
            '789', '123456', 'udid1', 'A007AA', encode_license('license00'),
        ),
        car_classes=driver_info.CarClasses(['econom'], [], [], []),
        payment_methods=driver_info.PaymentMethods(
            _PAYMENT_METHODS, [], _PAYMENT_METHODS,
        ),
        statuses=driver_info.Statuses('busy', 'order', None),
    ),
    driver_info.DriverInfo(
        driver_info.Point(131.5, 43.5),
        driver_info.DriverIds(
            '790', '123457', 'udid2', 'A007AB', encode_license('license01'),
        ),
        car_classes=driver_info.CarClasses(['econom'], [], [], []),
        payment_methods=driver_info.PaymentMethods(
            _PAYMENT_METHODS, [], _PAYMENT_METHODS,
        ),
        statuses=driver_info.Statuses('busy', 'order', None),
    ),
]


UNKNOWN_SEARCH_AREA = {
    'top_left': {'lon': 131, 'lat': 43},
    'bottom_right': {'lon': 132, 'lat': 44},
}


@pytest.mark.parametrize(
    'required_categories, data_keys',
    [
        (['ids'], ['unique_driver_id', 'car_number', 'license_id']),
        (
            ['ids', 'car_classes'],
            ['unique_driver_id', 'classes', 'car_number', 'license_id'],
        ),
        (['statuses'], ['status']),
        (
            ['payment_methods', 'payment_methods_taximeter'],
            ['payment_methods'],
        ),
    ],
)
async def test_basic(
        taxi_atlas_drivers, required_categories, data_keys, candidates,
):
    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted(data_keys)

    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': required_categories,
    }
    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)

    assert response.status_code == 200
    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == 1
    info = infos[0]

    driver_info.compare_drivers(info, _SAMPLE_DRIVERS[0], required_categories)


async def test_required_zone(taxi_atlas_drivers, candidates):
    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted(
        ['license_id', 'unique_driver_id', 'car_number'],
    )

    request = {
        'search_area': UNKNOWN_SEARCH_AREA,
        'required_fields': ['payment_methods', 'car_classes', 'ids'],
    }
    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)

    assert response.status_code == 200
    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == 1
    info = infos[0]

    driver_info.compare_drivers(info, _SAMPLE_DRIVERS[1], ['ids'])


@pytest.mark.config(
    ATLAS_DRIVERS_FETCHERS_ENABLE={
        '__default__': True,
        'ids': False,
        'payment_methods': False,
        'payment_methods_taximeter': False,
    },
)
async def test_exclude_by_config(taxi_atlas_drivers, candidates):
    required_categories = ['ids', 'statuses', 'payment_methods']
    data_keys = ['status']

    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted(data_keys)

    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': required_categories,
    }
    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)

    assert response.status_code == 200
    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == 1
    driver_info.compare_drivers(infos[0], _SAMPLE_DRIVERS[0], ['statuses'])
