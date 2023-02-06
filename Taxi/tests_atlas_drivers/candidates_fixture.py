# pylint: disable=C5521
import json
import math
from typing import List

import pytest

from . import driver_info
from .drivers import decode_license


_LON = 0
_LAT = 1
_SERVICE = '/candidates'
_LIST_PROFILES_URL = '/list-profiles'
_PROFILES_URL = '/profiles'
_PROFILES_SNAPSHOT_URL = '/profiles-snapshot'


def _generate_response(driver: driver_info.DriverInfo, data_keys: List[str]):
    driver_response = {
        'uuid': driver.ids.driver_profile_id,
        'dbid': driver.ids.park_id,
        'position': [driver.geopoint.lon, driver.geopoint.lat],
    }

    if 'unique_driver_id' in data_keys and driver.ids.udid:
        driver_response['unique_driver_id'] = driver.ids.udid
    if 'car_number' in data_keys and driver.ids.car_number:
        driver_response['car_number'] = driver.ids.car_number
    if 'license_id' in data_keys and driver.ids.driver_license_hash:
        driver_response['license_id'] = decode_license(
            driver.ids.driver_license_hash,
        )
    if (
            'classes' in data_keys
            and driver.car_classes is not None
            and driver.car_classes.actual
    ):
        driver_response['classes'] = driver.car_classes.actual
    if 'payment_methods' in data_keys and driver.payment_methods is not None:
        driver_response['payment_methods'] = driver.payment_methods.actual
    if 'status' in data_keys and driver.statuses is not None:
        driver_response['status'] = {
            'driver': driver.statuses.driver,
            'taximeter': driver.statuses.taximeter,
        }

    if driver.combo_order_ids is not None:
        route = []
        for combo_order_id in driver.combo_order_ids:
            route.append({'order_id': combo_order_id})

        driver_response['metadata'] = {'combo': {'route': route}}

    return driver_response


@pytest.fixture(name='candidates')
def _candidates(mockserver):
    class Context:
        def __init__(self):
            self.drivers: List[driver_info.DriverInfo] = []
            self.data_keys: List[str] = []

        def set_drivers(self, drivers: List[driver_info.DriverInfo]):
            self.drivers = drivers

        def set_data_keys_wanted(self, data_keys: List[str]):
            self.data_keys = data_keys

    ctx = Context()

    @mockserver.json_handler(_SERVICE + _LIST_PROFILES_URL)
    def _list_profiles(request):
        data = json.loads(request.get_data())
        assert sorted(data['data_keys']) == sorted(ctx.data_keys)
        ans = []
        for driver in ctx.drivers:
            position = driver.geopoint
            if (
                    data['tl'][_LON] <= position.lon <= data['br'][_LON]
                    and data['tl'][_LAT] <= position.lat <= data['br'][_LAT]
            ):
                driver_response = _generate_response(driver, ctx.data_keys)
                ans.append(driver_response)

        return {'drivers': ans}

    @mockserver.json_handler(_SERVICE + _PROFILES_URL)
    def _profile(request):
        data = json.loads(request.get_data())
        assert sorted(data['data_keys']) == sorted(ctx.data_keys)
        ids = data['driver_ids']
        assert len(ids) == 1
        dbid = ids[0]['dbid']
        uuid = ids[0]['uuid']
        for driver in ctx.drivers:
            if (
                    driver.ids.park_id == dbid
                    and driver.ids.driver_profile_id == uuid
            ):
                return {'drivers': [_generate_response(driver, ctx.data_keys)]}
        return {'drivers': []}

    @mockserver.json_handler(_SERVICE + _PROFILES_SNAPSHOT_URL)
    def _profiles_snapshot(request):
        data = json.loads(request.get_data())
        part = data['part']
        parts = data['parts']
        assert 0 <= part < parts
        assert sorted(data['data_keys']) == sorted(ctx.data_keys)

        drivers_count = len(ctx.drivers)
        part_size = math.ceil(drivers_count / parts)
        part_start = min(part * part_size, drivers_count)
        part_end = min(part_start + part_size, drivers_count)
        ans = []
        for driver in ctx.drivers[part_start:part_end]:
            driver_response = _generate_response(driver, ctx.data_keys)
            ans.append(driver_response)
        return {'drivers': ans}

    return ctx
