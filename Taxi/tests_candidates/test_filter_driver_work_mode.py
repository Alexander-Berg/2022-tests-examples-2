from typing import List

from aiohttp import web
# pylint: disable=import-error
from driver_mode_index.v1.drivers.snapshot.post.fbs import Request as fb_req
import pytest

from tests_candidates import driver_work_mode


def _check_drivers(drivers_response, drivers: List[str]):
    assert len(drivers_response) == len(drivers)
    response = [item['dbid'] + '_' + item['uuid'] for item in drivers_response]
    response.sort()
    assert response == sorted(drivers)


@pytest.mark.parametrize('cache_enabled', (True, False))
@pytest.mark.parametrize(
    'work_modes',
    (
        None,
        tuple(),
        ('orders',),
        ('orders', 'mode1'),
        ('mode1',),
        ('mode1', 'mode2'),
        ('mode1', 'mode2', 'mode1'),
    ),
)
async def test_driver_work_mode(
        taxi_candidates,
        mockserver,
        taxi_config,
        driver_positions,
        work_modes,
        cache_enabled,
):
    taxi_config.set(
        CANDIDATES_DRIVER_WORK_MODE_CACHE={
            'enabled': cache_enabled,
            'cache_file_enabled': False,
            'restore_interval_ms': 10000,
            'dump_interval_ms': 5000,
            'request_interval_ms': 0,
            'request_size': 13000,
        },
    )
    driver_positions_list = (
        {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
        {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        {'dbid_uuid': 'dbid0_uuid3', 'position': [55, 35]},
        {'dbid_uuid': 'dbid0_uuid4', 'position': [55, 35]},
        {'dbid_uuid': 'dbid0_uuid5', 'position': [55, 35]},
    )
    all_drivers = [item['dbid_uuid'] for item in driver_positions_list]

    drivers_work_modes = {
        'dbid0_uuid1': driver_work_mode.DriverMode(
            'orders', properties=['property1', 'property2'],
        ),
        'dbid0_uuid2': driver_work_mode.DriverMode('mode1'),
        'dbid0_uuid3': driver_work_mode.DriverMode('mode2'),
        'dbid0_uuid4': driver_work_mode.DriverMode('mode1'),
        'dbid0_uuid5': driver_work_mode.DriverMode('mode3'),
    }

    @mockserver.json_handler('/driver-mode-index/v1/drivers/snapshot')
    def _mock_dmi_drivers_snapshot(request):
        assert cache_enabled
        req = fb_req.Request.GetRootAsRequest(bytearray(request.get_data()), 0)
        assert req.CurrentCursor() == 0
        assert req.NewParkDriverProfileIdsLength() == len(all_drivers)

        new_drivers = []
        if req.CurrentCursor() == 0:
            for i in range(req.NewParkDriverProfileIdsLength()):
                driver = req.NewParkDriverProfileIds(i).decode('utf-8')
                new_drivers.append(driver)

        return web.Response(
            status=200,
            body=driver_work_mode.construct_dmi_fbs_post_response(
                new_drivers, [], drivers_work_modes, 0,
            ),
            headers={'Content-Type': 'application/flatbuffer'},
        )

    await driver_positions(driver_positions_list)

    await taxi_candidates.invalidate_caches()

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'filters': ['efficiency/driver_work_mode'],
        'zone_id': 'moscow',
        'point': [55, 35],
    }
    if work_modes is not None:
        request_body['drivers_work_modes'] = work_modes
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    if work_modes is None:
        _check_drivers(drivers, all_drivers)
        return
    if not work_modes:
        _check_drivers(drivers, [])
        return
    if not cache_enabled:
        if 'orders' in work_modes:
            _check_drivers(drivers, all_drivers)
        else:
            _check_drivers(drivers, [])
        return
    expected_drivers = [
        k for k, v in drivers_work_modes.items() if v.work_mode in work_modes
    ]
    if 'orders' in work_modes:
        expected_drivers.append('dbid0_uuid0')
    _check_drivers(drivers, expected_drivers)
