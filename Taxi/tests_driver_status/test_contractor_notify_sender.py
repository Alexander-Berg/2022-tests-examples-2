import json

import pytest


@pytest.mark.config(
    DRIVER_STATUS_ENABLE_EVENT_LISTENERS={
        '__default__': False,
        'contractor-notify-sender': True,
    },
    DRIVER_STATUS_UPDATE_PUSH={'max_push_size': 10, 'parallel_requests': 3},
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'n_drivers,initial_status,push_status',
    [
        pytest.param(1, 'free', 'busy'),
        pytest.param(9, 'busy', 'free'),
        pytest.param(10, 'free', 'busy'),
        pytest.param(11, 'busy', 'free'),
        pytest.param(15, 'free', 'busy'),
        pytest.param(19, 'busy', 'free'),
        pytest.param(30, 'free', 'busy'),
        pytest.param(55, 'busy', 'free'),
    ],
)
async def test_contractor_push(
        taxi_driver_status,
        mockserver,
        taxi_config,
        n_drivers,
        initial_status,
        push_status,
):
    park_id = 'park0'
    driver_prefix = 'driver'

    @mockserver.json_handler('/client-notify/v2/push')
    def _client_notify_push(request):
        return {'notification_id': '123123'}

    for i in range(0, n_drivers):
        driver_id = driver_prefix + str(i)

        response = await taxi_driver_status.post(
            'v2/status/client',
            headers={
                'X-YaTaxi-Park-Id': park_id,
                'X-YaTaxi-Driver-Profile-Id': driver_id,
                'X-Request-Application-Version': '9.40',
                'X-Request-Version-Type': '',
                'X-Request-Platform': 'android',
            },
            data=json.dumps({'target_status': initial_status}),
        )
        assert response.status_code == 200

    await taxi_driver_status.invalidate_caches()

    # trigger push sending
    drivers = [
        {
            'park_id': park_id,
            'driver_id': driver_prefix + str(i),
            'status': push_status,
        }
        for i in range(0, n_drivers)
    ]
    response = await taxi_driver_status.post(
        'v1/internal/status/bulk', data=json.dumps({'items': drivers}),
    )
    assert response.status_code == 200

    # check that number of requests to client-notify is the same as expected
    # and that pushes for all drivers were sent
    expected_driver_ids = {
        f'{driver["park_id"]}-{driver["driver_id"]}' for driver in drivers
    }
    sent_driver_ids = set()

    for _ in range(0, n_drivers):
        arguments = await _client_notify_push.wait_call()
        content = json.loads(arguments['request'].get_data())
        sent_driver_ids.add(content['client_id'])
        assert content['intent'] == 'DRIVER_STATUS_UPDATE'
        assert content['service'] == 'taximeter'
        assert content['collapse_key'] == 'DRIVER_STATUS_UPDATE'
        assert content['data']['code'] == 401
        # allow only legacy 'free' and 'busy'
        # don't allow 'online' or 'offline'
        assert content['data']['driver_status_info']['value'] in (
            'free',
            'busy',
        )

    assert expected_driver_ids == sent_driver_ids
