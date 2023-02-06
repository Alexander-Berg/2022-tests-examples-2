# pylint: disable=C0302
# pylint: disable=import-only-modules
import json

import pytest

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import OrderStatus
# pylint: enable=import-error,import-only-modules


ORDER_PROVIDER = {
    0: 'unknown',
    1: 'park',
    2: 'yandex',
    16: 'upup',
    128: 'formula',
    1024: 'offtaxi',
}


def _old_status_to_driver_status(status):
    if status == 'free':
        return 'online'
    return status


def _make_drivers_bulk(reccount, order_provider):
    drivers = dict()
    for i in range(0, reccount):
        body = {
            'driver_id': f'driverid{i}',
            'park_id': f'parkid{i}',
            'status': f'free',
        }

        body['order_id'] = f'order_{i}'
        body['order_provider'] = order_provider
        drivers[body['driver_id']] = body
    return drivers


def _make_bulk_request(drivers):
    request = list()
    for key in drivers:
        request.append(drivers[key])
    return request


@pytest.mark.config(
    DRIVER_STATUS_ENABLE_EVENT_LISTENERS={
        '__default__': False,
        'georeceiver-sender': True,
    },
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'params',
    [
        (
            {
                'driver': {'park_id': 'parkid000', 'uuid': 'driverid000'},
                'data': {'target_status': 'free'},
                'driver-status-check-result': {
                    'block_reason': 'none',
                    'onlycard': False,
                },
                'expected-status-store': {
                    'status': 'free',
                    'status_int': 2,
                    'onlycard': 0,
                    'dont_chain': 0,
                },
            }
        ),
        (
            {
                'driver': {'park_id': 'parkid000', 'uuid': 'driverid001'},
                'data': {'target_status': 'free'},
                'driver-status-check-result': {
                    'block_reason': 'by_driver',
                    'onlycard': False,
                },
            }
        ),
        (
            {
                'driver': {'park_id': 'parkid000', 'uuid': 'driverid002'},
                'data': {'target_status': 'busy'},
                'driver-status-check-result': {
                    'block_reason': 'none',
                    'onlycard': False,
                },
            }
        ),
        (
            {
                'driver': {'park_id': 'parkid000', 'uuid': 'driverid003'},
                'data': {'target_status': 'busy'},
                'driver-status-check-result': {
                    'block_reason': 'by_driver',
                    'onlycard': False,
                },
            }
        ),
        (
            {
                'driver': {'park_id': 'parkid000', 'uuid': 'driverid004'},
                'data': {'target_status': 'free'},
                'driver-status-check-result': {
                    'block_reason': '',
                    'onlycard': True,
                },
            }
        ),
    ],
)
async def test_georeceiver_send(
        mockserver, taxi_driver_status, params, taxi_config,
):
    @mockserver.json_handler('/georeceiver/service/driver-status/store/')
    def _store_status(request):
        return mockserver.make_response('OK', status=200)

    response = await taxi_driver_status.post(
        'v2/status/client',
        headers={
            'X-YaTaxi-Park-Id': params['driver']['park_id'],
            'X-YaTaxi-Driver-Profile-Id': params['driver']['uuid'],
            'X-Request-Application-Version': '9.40',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
        },
        data=json.dumps(params['data']),
    )
    assert response.status_code == 200, json.dumps(response.json())

    call_args = await _store_status.wait_call()

    request_body = call_args['request'].json
    assert len(request_body) == 1
    item = request_body[0]
    assert item['dbid'] == params['driver']['park_id']
    assert item['uuid'] == params['driver']['uuid']
    new_status = _old_status_to_driver_status(params['data']['target_status'])
    assert item['status'] == new_status
    assert item['order_status'] == 'none'


@pytest.mark.config(
    DRIVER_STATUS_ENABLE_EVENT_LISTENERS={
        '__default__': False,
        'georeceiver-sender': True,
    },
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'order_provider',
    [
        pytest.param(0, id='provider=unknown'),
        pytest.param(1, id='provider=park'),
        pytest.param(2, id='provider=yandex'),
        pytest.param(16, id='provider=upup'),
    ],
)
async def test_georeceiver_bulk(
        mockserver,
        taxi_driver_status,
        order_provider,
        mocked_time,
        taxi_config,
):
    @mockserver.json_handler('/georeceiver/service/driver-status/store/')
    def _store_status(request):
        return mockserver.make_response('OK', status=200)

    drivers_count = 10
    for i in range(0, drivers_count):
        response = await taxi_driver_status.post(
            'v2/status/client',
            headers={
                'X-YaTaxi-Park-Id': f'parkid{i}',
                'X-YaTaxi-Driver-Profile-Id': f'driverid{i}',
                'X-Request-Application-Version': '9.40',
                'X-Request-Version-Type': '',
                'X-Request-Platform': 'android',
            },
            data=json.dumps({'target_status': 'free'}),
        )
        assert response.status_code == 200, json.dumps(response.json())
        await _store_status.wait_call()

    mocked_time.sleep(20)
    await taxi_driver_status.invalidate_caches(clean_update=False)

    drivers = _make_drivers_bulk(drivers_count, order_provider)
    request = _make_bulk_request(drivers)

    response = await taxi_driver_status.post(
        'v1/internal/status/bulk', data=json.dumps({'items': request}),
    )

    assert response.status_code == 200
    arguments = await _store_status.wait_call()
    content = json.loads(arguments['request'].get_data())
    assert len(content) == len(drivers)
    for item in content:
        assert item['uuid'] in drivers
        driver = drivers[item['uuid']]
        assert item['dbid'] == driver['park_id']
        assert item['uuid'] == driver['driver_id']
        new_status = _old_status_to_driver_status(driver['status'])
        assert item['status'] == new_status
        if 'order_id' in driver:
            assert item['order_status'] == OrderStatus.kDriving
            assert 'order_provider' in item
            assert (
                item['order_provider']
                == ORDER_PROVIDER[driver['order_provider']]
            )
        else:
            assert item['order_status'] == 'none'
