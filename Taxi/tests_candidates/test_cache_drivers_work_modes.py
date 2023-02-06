import datetime
import os
import pathlib
import shutil
import time
from typing import Dict

from aiohttp import web
# pylint: disable=import-error
from driver_mode_index.v1.drivers.snapshot.post.fbs import Request as fb_req
from driver_mode_index.v1.drivers.snapshot.post.fbs import Response as fb_resp
import pytest

from tests_candidates import driver_work_mode

DWM_CACHE_DUMP_FILENAME = 'cache_drivers_work_modes_dump.bin'

DWM_CACHE_DUMP = {
    'work_modes': ['orders', 'mode1', 'mode2'],
    'new_drivers_work_modes_indexes': [],
    'drivers_work_modes_updates': [
        ('dbid0_uuid0', 0, -1),
        ('dbid0_uuid1', 2, 0),
        ('dbid0_uuid2', 1, 1),
        ('dbid0_uuid3', 1, -1),
        ('dbid0_uuid4', 2, 1),
        ('dbid0_uuid5', 0, 0),
    ],
    'work_mode_properties': [
        ['time_based_subvention'],
        ['property1', 'property2'],
    ],
    'new_cursor': 100500,
}

DRIVERS_WORK_MODES = {
    'dbid0_uuid1': driver_work_mode.DriverMode(
        'mode2', ['time_based_subvention'],
    ),
    'dbid0_uuid2': driver_work_mode.DriverMode(
        'mode1', ['property1', 'property2'],
    ),
    'dbid0_uuid3': driver_work_mode.DriverMode('mode1'),
    'dbid0_uuid4': driver_work_mode.DriverMode(
        'mode2', ['property1', 'property2'],
    ),
    'dbid0_uuid5': driver_work_mode.DriverMode(
        'orders', ['time_based_subvention'],
    ),
}


DRIVER_POSITIONS_LIST = (
    {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
    {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
    {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
    {'dbid_uuid': 'dbid0_uuid3', 'position': [55, 35]},
    {'dbid_uuid': 'dbid0_uuid4', 'position': [55, 35]},
    {'dbid_uuid': 'dbid0_uuid5', 'position': [55, 35]},
)


def _decode_fbs_properties(properties):
    res = []
    for i in range(properties.WorkModePropertiesLength()):
        current_properties = []
        for j in range(properties.WorkModeProperties(i).PropertiesLength()):
            current_properties.append(
                properties.WorkModeProperties(i).Properties(j).decode('utf-8'),
            )
        res.append(sorted(current_properties))
    return res


def _compare_responses(lhs: fb_resp.Response, rhs: dict) -> None:
    assert lhs.NewCursor() == rhs['new_cursor']

    assert lhs.WorkModesLength() == len(rhs['work_modes'])
    to_rhs_map: Dict[int, int] = {}
    for i in range(lhs.WorkModesLength()):
        rhs_index = rhs['work_modes'].index(lhs.WorkModes(i).decode('utf-8'))
        to_rhs_map[i] = rhs_index

    assert lhs.NewDriversWorkModesIndexesLength() == len(
        rhs['new_drivers_work_modes_indexes'],
    )
    for i in range(lhs.NewDriversWorkModesIndexesLength()):
        rhs_index = rhs['new_drivers_work_modes_indexes'][i]
        assert to_rhs_map[lhs.NewDriversWorkModesIndexes(i)] == rhs_index

    assert lhs.DriversWorkModesUpdatesLength() == len(
        rhs['drivers_work_modes_updates'],
    )
    mode_updates_map: Dict[str, int] = {}
    properties_update_map: Dict[str, int] = {}
    for update in rhs['drivers_work_modes_updates']:
        mode_updates_map[update[0]] = update[1]
        properties_update_map[update[0]] = update[2]
    for i in range(lhs.DriversWorkModesUpdatesLength()):
        update = lhs.DriversWorkModesUpdates(i)
        rhs_index = mode_updates_map[
            update.ParkDriverProfileId().decode('utf-8')
        ]
        assert to_rhs_map[update.WorkModeIndex()] == rhs_index
        assert (
            properties_update_map[update.ParkDriverProfileId().decode('utf-8')]
            == update.WorkModePropertiesIndex()
        )
    assert rhs['work_mode_properties'] == _decode_fbs_properties(lhs)


@pytest.fixture(name='dwm_cache_dump_dir')
def _dwm_cache_dump_dir(build_dir: pathlib.Path) -> pathlib.Path:
    return build_dir.joinpath(
        'services/candidates/testsuite/cache/drivers_work_modes',
    )


@pytest.fixture(name='dwm_cache_dump_file')
def _dwm_cache_dump_file(dwm_cache_dump_dir: pathlib.Path) -> pathlib.Path:
    return dwm_cache_dump_dir / DWM_CACHE_DUMP_FILENAME


def _clear_dwm_cache(dwm_cache_dump_dir):
    shutil.rmtree(dwm_cache_dump_dir, True)


def _read_dwm_cache(dwm_cache_dump_file):
    with open(dwm_cache_dump_file, 'rb') as file:
        data_fbs = file.read()
        return data_fbs
    return None


def _write_dwm_cache(dwm_cache_dump_file, data_fbs, date=None):
    os.makedirs(os.path.dirname(dwm_cache_dump_file), exist_ok=True)
    with open(dwm_cache_dump_file, 'wb') as file:
        file.write(data_fbs)
    if date:
        modified_time = time.mktime(date.timetuple())
        os.utime(dwm_cache_dump_file, (modified_time, modified_time))


def _exist_dwm_cache(dwm_cache_dump_file):
    return os.path.isfile(dwm_cache_dump_file)


def _modified_dwm_cache(dwm_cache_dump_file):
    modified_time = os.path.getmtime(dwm_cache_dump_file)
    return datetime.datetime.fromtimestamp(modified_time)


async def test_dwm_cache_dump(
        taxi_candidates,
        mockserver,
        build_dir,
        taxi_config,
        testpoint,
        driver_positions,
        dwm_cache_dump_dir,
        dwm_cache_dump_file,
):
    @testpoint('dump')
    def _dump(request):
        return {}

    _clear_dwm_cache(dwm_cache_dump_dir)

    request_size = 2
    taxi_config.set_values(
        dict(
            CANDIDATES_DRIVER_WORK_MODE_CACHE={
                'enabled': True,
                'cache_file_enabled': True,
                'restore_interval_ms': 1800,
                'dump_interval_ms': 300,
                'request_interval_ms': 10,
                'request_size': request_size,
            },
        ),
    )

    @mockserver.json_handler('/driver-mode-index/v1/drivers/snapshot')
    def _mock_dmi_drivers_snapshot(request):
        req = fb_req.Request.GetRootAsRequest(bytearray(request.get_data()), 0)

        assert req.NewParkDriverProfileIdsLength() <= request_size

        new_drivers = []
        if req.CurrentCursor() == 0:
            for i in range(req.NewParkDriverProfileIdsLength()):
                driver = req.NewParkDriverProfileIds(i).decode('utf-8')
                new_drivers.append(driver)

        return web.Response(
            status=200,
            body=driver_work_mode.construct_dmi_fbs_post_response(
                new_drivers, [], DRIVERS_WORK_MODES, 100500,
            ),
            headers={'Content-Type': 'application/flatbuffer'},
        )

    await driver_positions(DRIVER_POSITIONS_LIST)
    await taxi_candidates.invalidate_caches()
    await _dump.wait_call()

    data_fbs = _read_dwm_cache(dwm_cache_dump_file)

    data = fb_resp.Response.GetRootAsResponse(bytearray(data_fbs), 0)

    _compare_responses(data, DWM_CACHE_DUMP)
    _clear_dwm_cache(dwm_cache_dump_dir)


async def test_dwm_cache_restore(
        taxi_candidates,
        mockserver,
        build_dir,
        taxi_config,
        testpoint,
        driver_positions,
        dwm_cache_dump_dir,
        dwm_cache_dump_file,
):
    @testpoint('dump')
    def _dump(request):
        return {}

    _clear_dwm_cache(dwm_cache_dump_dir)

    request_size = 3
    taxi_config.set_values(
        dict(
            CANDIDATES_DRIVER_WORK_MODE_CACHE={
                'enabled': True,
                'cache_file_enabled': True,
                'restore_interval_ms': 1800,
                'dump_interval_ms': 1,
                'request_interval_ms': 10,
                'request_size': request_size,
            },
        ),
    )

    all_drivers = [item['dbid_uuid'] for item in DRIVER_POSITIONS_LIST]

    @mockserver.json_handler('/driver-mode-index/v1/drivers/snapshot')
    def _mock_dmi_drivers_snapshot(request):
        req = fb_req.Request.GetRootAsRequest(bytearray(request.get_data()), 0)

        assert req.NewParkDriverProfileIdsLength() <= request_size

        return web.Response(
            status=200,
            body=driver_work_mode.construct_dmi_fbs_post_response(
                [], [], DRIVERS_WORK_MODES, 100500,
            ),
            headers={'Content-Type': 'application/flatbuffer'},
        )

    data_fbs = driver_work_mode.construct_dmi_fbs_post_response(
        [], all_drivers, DRIVERS_WORK_MODES, 100500,
    )
    _write_dwm_cache(dwm_cache_dump_file, data_fbs)

    await driver_positions(DRIVER_POSITIONS_LIST)
    await taxi_candidates.invalidate_caches()
    await _dump.wait_call()

    data_fbs = _read_dwm_cache(dwm_cache_dump_file)
    data = fb_resp.Response.GetRootAsResponse(bytearray(data_fbs), 0)

    _compare_responses(data, DWM_CACHE_DUMP)
    _clear_dwm_cache(dwm_cache_dump_dir)


@pytest.mark.parametrize('invalid', ('new_drivers', 'data'))
async def test_dwm_cache_invalid_restore(
        taxi_candidates,
        mockserver,
        build_dir,
        taxi_config,
        testpoint,
        driver_positions,
        dwm_cache_dump_dir,
        dwm_cache_dump_file,
        invalid,
):
    @testpoint('dump')
    def _dump(request):
        return {}

    _clear_dwm_cache(dwm_cache_dump_dir)

    request_size = 3
    taxi_config.set_values(
        dict(
            CANDIDATES_DRIVER_WORK_MODE_CACHE={
                'enabled': True,
                'cache_file_enabled': True,
                'restore_interval_ms': 1800,
                'dump_interval_ms': 1,
                'request_interval_ms': 10,
                'request_size': request_size,
            },
        ),
    )

    all_drivers = [item['dbid_uuid'] for item in DRIVER_POSITIONS_LIST]

    @mockserver.json_handler('/driver-mode-index/v1/drivers/snapshot')
    def _mock_dmi_drivers_snapshot(request):
        req = fb_req.Request.GetRootAsRequest(bytearray(request.get_data()), 0)

        assert req.NewParkDriverProfileIdsLength() <= request_size

        new_drivers = []
        if req.CurrentCursor() == 0:
            # full update
            assert invalid == 'data'
            for i in range(req.NewParkDriverProfileIdsLength()):
                driver = req.NewParkDriverProfileIds(i).decode('utf-8')
                new_drivers.append(driver)
        if invalid == 'new_drivers':
            # partial update
            assert req.CurrentCursor()

        return web.Response(
            status=200,
            body=driver_work_mode.construct_dmi_fbs_post_response(
                new_drivers, [], DRIVERS_WORK_MODES, 100500,
            ),
            headers={'Content-Type': 'application/flatbuffer'},
        )

    if invalid == 'new_drivers':
        data_fbs = driver_work_mode.construct_dmi_fbs_post_response(
            all_drivers, all_drivers, DRIVERS_WORK_MODES, 100500,
        )
        _write_dwm_cache(dwm_cache_dump_file, data_fbs)
    if invalid == 'data':
        invalid_data_fbs = b'INVALID DWM CACHE_DUMP'
        _write_dwm_cache(dwm_cache_dump_file, invalid_data_fbs)

    await driver_positions(DRIVER_POSITIONS_LIST)
    await taxi_candidates.invalidate_caches()
    await _dump.wait_call()

    data_fbs = _read_dwm_cache(dwm_cache_dump_file)
    data = fb_resp.Response.GetRootAsResponse(bytearray(data_fbs), 0)

    _compare_responses(data, DWM_CACHE_DUMP)
    _clear_dwm_cache(dwm_cache_dump_dir)
