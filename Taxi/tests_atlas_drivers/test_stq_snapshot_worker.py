# flake8: noqa F401, IS001, I202
# pylint: disable=C1801, C5521, W0612
import copy
import datetime
import json

import pytest

import taxi_efficiency.libs.quadkey as quadkey

from tests_atlas_drivers import driver_info
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers.reposition_fixture import _reposition
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers import driver_info
from tests_atlas_drivers import drivers


_CHUNKS_COUNT = 3
_DRIVERS_COUNT = 7

_NOW = datetime.datetime(2021, 2, 2, 15, 22, 7, 562)


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


def _generate_lb_message(driver):
    quadkey_zoom = 18

    seconds = int(_NOW.replace(tzinfo=datetime.timezone.utc).timestamp())
    minute_start = seconds - seconds % 60

    order_id = (
        driver.order_info.order_id if driver.order_info is not None else ''
    )
    order_ids = []
    if driver.combo_order_ids:
        order_ids.extend(driver.combo_order_ids)

    if order_id:
        order_ids.append(order_id)

    result = {
        'timestamp': seconds,
        'dttm_utc_1_min': minute_start,
        'driver_id': '',
        'payment_method': driver.payment_methods.actual[0],
        'allowed_payment_methods': driver.payment_methods.taximeter,
        'car_classes': (
            [] if driver.car_classes is None else driver.car_classes.actual
        ),
        'chain_free': (
            [] if driver.car_classes is None else driver.car_classes.chain
        ),
        'driver_license_hash': '',
        'driver_status': (
            '' if driver.statuses is None else driver.statuses.driver
        ),
        'tx_status': (
            '' if driver.statuses is None else driver.statuses.taximeter
        ),
        'driver_uuid': driver.ids.driver_profile_id,
        'home_button': (
            False if driver.reposition is None else driver.reposition.enabled
        ),
        'is_frozen': (
            False if driver.is_frozen is None else driver.is_frozen.freeze
        ),
        'park_db_id': driver.ids.park_id,
        'tags': [] if driver.tags is None else driver.tags.tag_names,
        'unique_driver_id': (
            '' if driver.ids.udid is None else driver.ids.udid
        ),
        'lon': driver.geopoint.lon,
        'lat': driver.geopoint.lat,
        'quadkey': quadkey.latlon2quadkey(
            driver.geopoint.lat, driver.geopoint.lon, quadkey_zoom,
        ),
        'tariff_zone': (
            '' if driver.tariff_zone is None else driver.tariff_zone
        ),
        'city': driver.city,
        'order_id': order_id,
        'order_ids': order_ids,
    }

    if driver.statuses is not None and driver.statuses.order is not None:
        result['order_taxi_status'] = driver.statuses.order

    if driver.reposition is not None:
        if driver.reposition.mode is not None:
            result['reposition'] = driver.reposition.mode

        if driver.reposition.geopoint is not None:
            result['reposition_dest_lon'] = driver.reposition.geopoint.lon
            result['reposition_dest_lat'] = driver.reposition.geopoint.lat
            result['reposition_quadkey'] = quadkey.latlon2quadkey(
                driver.reposition.geopoint.lat,
                driver.reposition.geopoint.lon,
                quadkey_zoom,
            )

    if driver.taximeter_version is not None:
        if driver.taximeter_version.taximeter_brand is not None:
            result[
                'taximeter_brand'
            ] = driver.taximeter_version.taximeter_brand
        if driver.taximeter_version.taximeter_platform is not None:
            result[
                'taximeter_platform'
            ] = driver.taximeter_version.taximeter_platform
        if driver.taximeter_version.taximeter_version is not None:
            result[
                'taximeter_version'
            ] = driver.taximeter_version.taximeter_version
        if driver.taximeter_version.taximeter_version_type is not None:
            result[
                'taximeter_version_type'
            ] = driver.taximeter_version.taximeter_version_type

    return result


def _compare_lb_messages(expected, received):
    expected = copy.deepcopy(expected)
    received = copy.deepcopy(received)

    expected_point = driver_info.Point(
        expected.pop('lon'), expected.pop('lat'),
    )
    received_point = driver_info.Point(
        received.pop('lon'), received.pop('lat'),
    )

    assert expected_point == received_point

    if 'reposition_dest_lon' in expected:
        expected_rep_point = driver_info.Point(
            expected.pop('reposition_dest_lon'),
            expected.pop('reposition_dest_lat'),
        )
        received_rep_point = driver_info.Point(
            received.pop('reposition_dest_lon'),
            received.pop('reposition_dest_lat'),
        )

        assert expected_rep_point == received_rep_point

    else:
        assert 'reposition_dest_lon' not in received
        assert 'reposition_dest_lat' not in received
        assert 'reposition_quadkey' not in received

    expected_tags = set(expected.pop('tags'))
    received_tags = set(received.pop('tags'))

    assert expected_tags == received_tags

    assert expected == received


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize('rescheduling_chunk_count', [None, 2])
async def test_stq(
        taxi_atlas_drivers,
        candidates,
        reposition,
        mockserver,
        driver_tags_mocks,
        frozen_drivers_mocks,
        parks_activation_mocks,
        busy_drivers_mocks,
        stq_runner,
        stq,
        testpoint,
        mock_tariffs,
        taxi_config,
        rescheduling_chunk_count,
):
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
        city=drivers.generate_city,
        combo_order_ids=drivers.generate_combo_order_ids,
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

    if rescheduling_chunk_count is not None:
        taxi_config.set_values(
            {
                'ATLAS_DRIVERS_SNAPSHOTS_CHUNK_COUNT': (
                    rescheduling_chunk_count
                ),
                'ATLAS_DRIVERS_SNAPSHOTS_RESCHEDULING_ENABLE': True,
            },
        )

    await taxi_atlas_drivers.invalidate_caches()

    expected_messages = [_generate_lb_message(x) for x in sample_drivers]

    data_counter = 0
    data_buffer = []

    result_buffer = []

    @testpoint('logbroker_publish')
    def commit(data):
        nonlocal data_counter
        nonlocal data_buffer
        nonlocal result_buffer
        data_counter += 1
        data_buffer.append(data['data'])

        assert data['name'] == 'atlas-drivers-snapshot'

        local_result = [json.loads(x) for x in data['data'].splitlines()]
        result_buffer.extend(local_result)

    for chunk_index in range(_CHUNKS_COUNT):
        await stq_runner.atlas_drivers_snapshots.call(
            task_id=f'process_chunk_{chunk_index}',
            args=[],
            kwargs={
                'timestamp': {'$date': _NOW.strftime('%Y-%m-%dT%H:%M:00Z')},
                'chunk_index': chunk_index,
                'chunk_count': _CHUNKS_COUNT,
            },
        )

    assert (
        stq.atlas_drivers_snapshots.times_called == 0
        if rescheduling_chunk_count is None
        else rescheduling_chunk_count
    )

    assert len(result_buffer) == len(expected_messages)

    for received, expected in zip(result_buffer, expected_messages):
        _compare_lb_messages(expected, received)
