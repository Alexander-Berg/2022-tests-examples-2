# flake8: noqa F401, IS001, I202
# pylint: disable=C1801, C5521, W0612
import pytest

from tests_atlas_drivers import driver_info
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers.reposition_fixture import _reposition
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers import drivers

_CHUNK_COUNT = 3
_DRIVERS_COUNT = 7


def _generate_is_frozens():
    unique_driver_ids = []
    car_ids = []
    for i in range(_DRIVERS_COUNT):
        is_frozen = drivers.generate_is_frozen(i)
        if is_frozen.freeze:
            unique_driver_ids.append(drivers.generate_id('udid', i))
            car_ids.append(drivers.generate_id('car_number', i))
    return {
        'unique_driver_ids': unique_driver_ids,
        'car_ids': car_ids,
        'timestamp': 1,
    }


def _generate_busy_drivers(sample_drivers):
    order_status_map = {'driving': 1, 'waiting': 2, 'transporting': 3}

    busy_drivers = []
    for driver in sample_drivers:
        if driver.statuses.order and driver.order_info:
            driver_id = driver.ids.park_id + '_' + driver.ids.driver_profile_id
            order_id = driver.order_info.order_id
            order_status = order_status_map[driver.statuses.order]
            busy_driver = {
                'driver_id': driver_id,
                'order_id': order_id,
                'taxi_status': order_status,
            }
            if driver.order_info.point_b:
                busy_driver['destination'] = {
                    'lat': driver.order_info.point_b.lat,
                    'lon': driver.order_info.point_b.lon,
                }
            busy_drivers.append(busy_driver)
    return busy_drivers


def _generate_payment_methods(index_driver: int) -> driver_info.PaymentMethods:
    return driver_info.PaymentMethods(
        actual=['card'], dispatch=['cash', 'coupon', 'corp'],
    )


@pytest.mark.parametrize('taximeter', [True, False])
async def test_basic(
        taxi_atlas_drivers,
        candidates,
        reposition,
        mockserver,
        driver_tags_mocks,
        frozen_drivers_mocks,
        parks_activation_mocks,
        busy_drivers_mocks,
        taximeter,
        taxi_config,
):
    taxi_config.set_values(
        dict(
            ATLAS_DRIVERS_FETCHERS_ENABLE={
                '__default__': True,
                'payment_methods_taximeter': taximeter,
            },
        ),
    )

    sample_drivers = drivers.generate_drivers(
        _DRIVERS_COUNT,
        point=drivers.generate_point,
        tags=drivers.generate_tags,
        is_frozen=drivers.generate_is_frozen,
        reposition=drivers.generate_reposition,
        payment_methods=drivers.generate_payment_methods
        if taximeter
        else _generate_payment_methods,
        statuses=drivers.generate_statuses,
        tariff_zone=drivers.generate_tariff_zone,
        order_info=drivers.generate_order_info,
        taximeter_versions=drivers.generate_taximeter_versions,
    )

    sample_repositions = drivers.generate_repositions(
        _DRIVERS_COUNT, reposition=drivers.generate_reposition,
    )

    candidates.set_drivers(sample_drivers)
    candidates.set_data_keys_wanted(
        [
            'status',
            'classes',
            'car_number',
            'unique_driver_id',
            'payment_methods',
            'license_id',
        ],
    )
    reposition.set_reposition(sample_repositions)

    categories = [
        'ids',
        'is_frozen',
        'tags',
        'statuses',
        'order_info',
        'payment_methods',
        'reposition',
        'tariff_zone',
        'taximeter_version',
    ]

    for driver in sample_drivers:
        driver_tags_mocks.set_tags_info(
            driver.ids.park_id,
            driver.ids.driver_profile_id,
            driver.tags.tag_names,
        )

    @mockserver.json_handler('/coord-control/atlas/performers-meta-info')
    def _performers_meta_info(_):
        return {'performers': []}

    frozen_drivers_mocks.set_frozen_drivers(_generate_is_frozens())
    parks_activation_mocks.set_parks(
        drivers.generate_parks_activation(sample_drivers),
    )
    busy_drivers_mocks.set_drivers(_generate_busy_drivers(sample_drivers))

    await taxi_atlas_drivers.invalidate_caches()

    driver_index = 0
    for chunk_index in range(_CHUNK_COUNT):
        request = {'chunk_index': chunk_index, 'chunk_count': _CHUNK_COUNT}
        response = await taxi_atlas_drivers.post('v1/snapshot', json=request)
        assert response.status_code == 200

        infos = fbs_parse.parse_drivers_info(response.content)
        infos = list(sorted(infos, key=lambda x: x.ids.park_id))
        for lhs in infos:
            rhs = sample_drivers[driver_index]
            driver_info.compare_drivers(lhs, rhs, categories)
            driver_index += 1

    assert driver_index == _DRIVERS_COUNT


@pytest.mark.config(ATLAS_DRIVERS_FETCHERS_ENABLE={'__default__': False})
async def test_exclude_by_config(taxi_atlas_drivers, candidates):
    sample_drivers = drivers.generate_drivers(
        _DRIVERS_COUNT,
        point=drivers.generate_point,
        tags=drivers.generate_tags,
        is_frozen=drivers.generate_is_frozen,
        reposition=drivers.generate_reposition,
        payment_methods=drivers.generate_payment_methods,
        statuses=drivers.generate_statuses,
        tariff_zone=drivers.generate_tariff_zone,
        order_info=drivers.generate_order_info,
    )

    candidates.set_drivers(sample_drivers)
    candidates.set_data_keys_wanted([])

    request = {'chunk_index': 0, 'chunk_count': 1}
    response = await taxi_atlas_drivers.post('v1/snapshot', json=request)
    assert response.status_code == 200

    infos = fbs_parse.parse_drivers_info(response.content)
    for driver_index, lhs in enumerate(infos):
        rhs = sample_drivers[driver_index]
        driver_info.compare_drivers(lhs, rhs, [])
