import datetime
import json
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_weariness import const
from tests_driver_weariness import weariness_tools


_PROFILE_EVENTS = [
    # timestamp, status, order_statuses
    ('2018-01-21T15:30:00+0000', 'online', ['driving']),
    ('2018-01-21T15:42:00+0000', 'offline', None),
    ('2018-01-21T15:45:00+0000', 'online', ['waiting']),
    ('2018-01-21T15:53:00+0000', 'online', ['waiting']),
    ('2018-01-21T15:54:00+0000', 'offline', None),
]
_EVENTS = {
    'dbid_uuid40': [
        {
            'timestamp': weariness_tools.str_to_sec(event[0]),
            'status': event[1],
            'order_statuses': event[2],
        }
        if event[2]
        else {
            'timestamp': weariness_tools.str_to_sec(event[0]),
            'status': event[1],
        }
        for event in _PROFILE_EVENTS
    ],
}
_STATUS_HISTORY = {
    'dbid_uuid40': [
        {'timestamp': event[0], 'status': event[1], 'order_statuses': event[2]}
        if event[2]
        else {'timestamp': event[0], 'status': event[1]}
        for event in _PROFILE_EVENTS
    ],
}
_WORKING_INTERVALS = {
    'old': {
        'dbid_uuid40': [
            {
                'begin': '2021-02-19T15:30:00+0000',
                'end': '2021-02-19T15:42:00+0000',
            },
            {
                'begin': '2021-02-19T15:45:00+0000',
                'end': '2021-02-19T15:53:00+0000',
            },
        ],
    },
    'new': {
        'dbid_uuid40': [
            {
                'begin': '2021-02-18T15:30:00+0000',
                'end': '2021-02-18T15:42:00+0000',
            },
            {
                'begin': '2021-02-19T11:45:00+0000',
                'end': '2021-02-19T11:54:00+0000',
            },
        ],
    },
}


@pytest.mark.now('2021-02-19T19:00:00+0300')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.csh_extended_events(events=_EVENTS)
@pytest.mark.pgsql(
    'drivers_status_ranges', files=['pg_new_working_ranges.sql'],
)
@pytest.mark.parametrize(
    'udid, weariness_config, status_code, expected_response',
    [
        pytest.param('non-existed-udid', None, 404, None, id='no profiles'),
        pytest.param(
            'unique5',
            None,
            200,
            {
                'weariness': {
                    'tired_status': 'not_tired',
                    'updated': '2021-02-19T16:00:00+0000',
                    'working_time': 0,
                    'working_time_no_rest': 0,
                    'remaining_time': 54000,
                },
                'status_history': {},
                'working_intervals': {},
            },
            id='empty weariness',
        ),
        pytest.param(
            'unique4',
            None,
            200,
            {
                'weariness': {
                    'tired_status': 'not_tired',
                    'updated': '2021-02-19T11:54:00+0000',
                    'working_time': 540,
                    'working_time_no_rest': 540,
                    'remaining_time': 53460,
                },
                'status_history': _STATUS_HISTORY,
                'working_intervals': _WORKING_INTERVALS['new'],
            },
            id='not yet tired',
        ),
        pytest.param(
            'unique4',
            weariness_tools.WearinessConfig(300, 9, 8),
            200,
            {
                'weariness': {
                    'tired_status': 'no_long_rest',
                    'updated': '2021-02-19T11:54:00+0000',
                    'working_time': 540,
                    'working_time_no_rest': 540,
                    'remaining_time': 0,
                    'block_time': '2021-02-19T16:00:00+0000',
                    'block_till': '2021-02-19T16:54:00+0000',
                },
                'status_history': _STATUS_HISTORY,
                'working_intervals': _WORKING_INTERVALS['new'],
            },
            id='blocked driver',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_config_default.json')
async def test_driver_weariness_info(
        taxi_driver_weariness,
        udid: str,
        weariness_config: Optional[weariness_tools.WearinessConfig],
        status_code: int,
        expected_response: Optional[Dict[str, Any]],
        experiments3,
):
    if weariness_config is not None:
        weariness_tools.add_experiment(experiments3, weariness_config)
    await taxi_driver_weariness.invalidate_caches(clean_update=False)

    response = await taxi_driver_weariness.get(
        'v1/admin/driver-weariness', params={'unique_driver_id': udid},
    )

    assert response.status_code == status_code
    assert not expected_response or response.json() == expected_response


@pytest.mark.now('2021-02-19T19:00:00+0300')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.parametrize(
    'udid, login, uid, status_code',
    [
        pytest.param('unique1', None, 'uidx', 400, id='no login'),
        pytest.param('unique1', 'userx', None, 400, id='no uid'),
        pytest.param(
            'non-existed-udid', 'userx', 'uidx', 404, id='no profiles',
        ),
        pytest.param('unique1', 'userx', 'uidx', 200, id='update is run'),
    ],
)
async def test_update_working_ranges(
        taxi_driver_weariness,
        stq,
        udid: str,
        login: Optional[str],
        uid: Optional[str],
        status_code: int,
):
    headers = {}
    if login:
        headers['X-Yandex-Login'] = login
    if uid:
        headers['X-Yandex-Uid'] = uid

    response = await taxi_driver_weariness.post(
        'v1/admin/update-working-ranges',
        data=json.dumps({'unique_driver_id': udid}),
        headers=headers,
    )
    assert response.status_code == status_code

    if status_code == 200:
        assert stq.weariness_working_ranges_update.times_called == 1
        now_utc = datetime.datetime(2021, 2, 19, 16, 0, 0)
        stq_call = stq.weariness_working_ranges_update.next_call()
        assert stq_call['queue'] == 'weariness_working_ranges_update'
        assert stq_call['eta'] == now_utc
        assert stq_call['id'] == udid
        assert not stq_call['args']
