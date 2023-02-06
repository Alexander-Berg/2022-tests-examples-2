import datetime
import json

import pytest

from testsuite.utils import callinfo

from tests_driver_weariness import const


_NOW = datetime.datetime(2021, 2, 26, 12, 25, 59)
_DEFAULT_DELAY = datetime.timedelta(minutes=10)
_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.parametrize(
    'park_id, driver_id, status, config_enabled, enqueued_task',
    [
        pytest.param(
            'park1',
            'non-exist',
            'online',
            True,
            None,
            id='non-exist unique-driver-id',
        ),
        pytest.param(
            'park1', 'driverSS1', 'offline', True, None, id='offline event',
        ),
        pytest.param(
            'park1',
            'driverSS1',
            'online',
            False,
            None,
            id='disabled by config #1',
        ),
        pytest.param(
            'park1',
            'driverSS1',
            'online',
            True,
            'unique1',
            id='enabled by config #1',
        ),
        pytest.param(
            'dbid',
            'uuid40',
            'online',
            True,
            'unique4',
            id='enqueued stq-task for unique4',
        ),
        pytest.param(
            'dbid',
            'uuid40',
            'online',
            False,
            None,
            id='disabled by config #2',
        ),
    ],
)
async def test_basic(
        taxi_driver_weariness,
        taxi_config,
        stq,
        park_id,
        driver_id,
        status,
        config_enabled,
        enqueued_task,
):
    taxi_config.set_values(
        {'DRIVER_WEARINESS_ONLINE_EVENTS_CONSUMER_ENABLED': config_enabled},
    )

    data = {
        'park_id': park_id,
        'driver_id': driver_id,
        'status': status,
        'updated_at': (_NOW - datetime.timedelta(seconds=1)).strftime(
            _TIME_FORMAT,
        ),
    }
    response = await taxi_driver_weariness.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'driver-online-events-consumer',
                'data': json.dumps(data),
                'topic': '/taxi/contractor-online-events',
                'cookie': 'my_cookie',
            },
        ),
    )
    assert response.status_code == 200

    # check stq queue, stq-task is put async
    try:
        stq_call = await stq.weariness_working_ranges_update.wait_call(
            timeout=0.1,
        )
        assert stq_call['queue'] == 'weariness_working_ranges_update'
        assert stq_call['id'] == enqueued_task
        assert stq_call['eta'] == _NOW + _DEFAULT_DELAY
        assert stq_call['args'] == []
    except callinfo.CallQueueTimeoutError:
        assert enqueued_task is None
