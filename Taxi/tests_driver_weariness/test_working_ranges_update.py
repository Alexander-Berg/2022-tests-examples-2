import datetime
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_weariness import const
from tests_driver_weariness import weariness_tools

_UNIQUE_DRIVERS = {
    'licenses_by_unique_drivers': {
        'last_revision': '111112_1',
        'items': [
            {
                'id': 'too_many_profiles_udid',
                'is_deleted': False,
                'revision': '111111_1',
                'data': {'license_ids': [f'license_a_{x}' for x in range(43)]},
            },
            {
                'id': 'uuid',
                'is_deleted': False,
                'revision': '111112_1',
                'data': {'license_ids': ['license_2_1']},
            },
            {
                'id': 'dummy_uuid',
                'is_deleted': False,
                'revision': '111113_1',
                'data': {'license_ids': ['license_dummy_1']},
            },
        ],
    },
    'license_by_driver_profile': {
        'last_revision': '780_0',
        'items': (
            [
                {
                    'id': f'dbid{x}_uuid{x}',
                    'is_deleted': False,
                    'revision': f'779_{x}',
                    'data': {'license_id': f'license_a_{x}'},
                }
                for x in range(43)
            ]
            + [
                {
                    'id': 'dbid_uuid',
                    'is_deleted': False,
                    'revision': '780_0',
                    'data': {'license_id': 'license_2_1'},
                },
                {
                    'id': 'dummy_dbid_uuid',
                    'is_deleted': False,
                    'revision': '781_0',
                    'data': {'license_id': 'license_dummy_1'},
                },
            ]
        ),
    },
}


@pytest.mark.uservice_oneshot
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.unique_drivers(stream=_UNIQUE_DRIVERS)
@pytest.mark.parametrize(
    'udid, no_profiles_call, too_many_profiles_call, config_enabled',
    [
        ('no_profiles_udid', True, False, True),
        ('too_many_profiles_udid', False, True, True),
        ('uuid', False, False, True),
        ('uuid', False, False, False),
    ],
)
async def test_weariness_working_ranges_update_no_process(
        stq,
        stq_runner,
        taxi_config,
        testpoint,
        udid: str,
        no_profiles_call: bool,
        too_many_profiles_call: bool,
        config_enabled: bool,
):
    @testpoint('no_profiles')
    def _no_profiles(args):
        pass

    @testpoint('too_many_profiles')
    def _too_many_profiles(args):
        pass

    taxi_config.set_values(
        {'DRIVER_WEARINESS_WORKING_RANGES_UPDATE_ENABLED': config_enabled},
    )

    await stq_runner.weariness_working_ranges_update.call(task_id=udid)

    assert _no_profiles.has_calls is no_profiles_call
    assert _too_many_profiles.has_calls is too_many_profiles_call
    assert stq.weariness_working_ranges_update.times_called == 0


_EVENTS = {
    'park1_driverSS1': [
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T18:55:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T18:58:58+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
    ],
    'dbid_uuid40': [
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T14:45:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T14:55:00+0300',
            ),
            'status': 'offline',
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T15:15:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T15:20:00+0300',
            ),
            'status': 'offline',
        },
    ],
    'dbid_uuid41': [
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T16:45:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['waiting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T16:55:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
    ],
    'dbid_uuid51': [
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T14:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T14:05:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T14:10:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T14:20:00+0300',
            ),
            'status': 'online',
            'order_statuses': [],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T15:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T15:01:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['none'],
        },
        {  # single on_order status should not create work interval
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T16:00:00+0300',
            ),
            'status': 'busy',
            'order_statuses': ['driving'],
        },
    ],
    'dbid_uuid70': [
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T19:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T19:20:00+0300',
            ),
            'status': 'offline',
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T20:15:00+0300',
            ),
            'status': 'offline',
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T20:55:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T20:56:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['waiting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T20:56:01+0300',
            ),
            'status': 'busy',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T21:56:01+0300',
            ),
            'status': 'busy',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T21:57:01+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
    ],
    'dbid_uuid80': [
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T23:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['driving'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T23:10:00+0300',
            ),
            'status': 'offline',
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T02:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T02:10:00+0300',
            ),
            'status': 'busy',
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T08:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T08:10:00+0300',
            ),
            'status': 'busy',
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T14:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T14:10:00+0300',
            ),
            'status': 'busy',
        },
    ],
    'dbid_uuid90': [
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T23:00:00+0300',
            ),
            'status': 'offline',
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T23:10:00+0300',
            ),
            'status': 'offline',
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-19T02:00:00+0300',
            ),
            'status': 'offline',
        },
    ],
    'dbid_uuid100': [
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-17T00:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-17T15:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-17T16:00:00+0300',
            ),
            'status': 'offline',
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T10:00:00+0300',
            ),
            'status': 'offline',
        },
    ],
    'dbid_uuid110': [
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-17T00:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-17T15:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-17T20:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T00:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T09:00:00+0300',
            ),
            'status': 'online',
            'order_statuses': ['transporting'],
        },
        {
            'timestamp': weariness_tools.str_to_sec(
                '2021-02-18T10:00:00+0300',
            ),
            'status': 'offline',
        },
    ],
}


@pytest.mark.uservice_oneshot
@pytest.mark.now('2021-02-19T19:00:00+03:00')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.pgsql(
    'drivers_status_ranges', files=['pg_new_working_ranges.sql'],
)
@pytest.mark.experiments3(filename='exp3_config_default.json')
@pytest.mark.csh_extended_events(events=_EVENTS)
@pytest.mark.config(
    DRIVER_WEARINESS_WORKING_RANGES_UPDATE={
        'max_status_history_request_interval_h': 24,
        'max_interval_time_minutes': 20,
        'max_driver_profiles': 43,
        'chunk_profiles_size': 1,
        'update_reschedule': [
            {'expire_time_m': 60, 'next_call_time_m': 5},
            {'expire_time_m': 120, 'next_call_time_m': 20},
            {'expire_time_m': 180, 'next_call_time_m': 30},
            {'expire_time_m': 240, 'next_call_time_m': 40},
            {'expire_time_m': 360, 'next_call_time_m': 60},
            {'expire_time_m': 600, 'next_call_time_m': 240},
            {'expire_time_m': 780, 'next_call_time_m': 360},
        ],
    },
    DRIVER_WEARINESS_PG_SETTINGS={
        '__default__': {
            'execute_timeout_ms': 1000,
            'statement_timeout_ms': 750,
            'chunk_size': 1,
            'pause_ms': 0,
        },
    },
)
@pytest.mark.parametrize(
    'udid, profiles, config, expected_ranges, csh_events_calls,'
    'next_call_minutes',
    [
        pytest.param(
            'unique1',
            ['park1_driverSS1'],
            None,
            {
                'park1_driverSS1': {
                    '2021-02-19T15:35:00+0300': '2021-02-19T15:45:00+0300',
                    '2021-02-19T15:51:00+0300': '2021-02-19T15:53:00+0300',
                    '2021-02-19T17:01:00+0300': '2021-02-19T18:50:00+0300',
                    '2021-02-19T18:55:00+0300': '2021-02-19T18:58:58+0300',
                },
            },
            1,
            360,
            id='append working interval',
        ),
        pytest.param(
            'unique4',
            ['dbid_uuid40', 'dbid_uuid41'],
            None,
            {
                'dbid_uuid40': {
                    '2021-02-18T18:30:00+0300': '2021-02-18T18:42:00+0300',
                    '2021-02-19T14:45:00+0300': '2021-02-19T14:55:00+0300',
                    '2021-02-19T15:15:00+0300': '2021-02-19T15:20:00+0300',
                },
                'dbid_uuid41': {
                    '2021-02-19T16:45:00+0300': '2021-02-19T16:55:00+0300',
                },
            },
            2,
            360,
            id='multi profiles',
        ),
        pytest.param(
            'unique5',
            ['dbid_uuid50', 'dbid_uuid51'],
            None,
            {
                'dbid_uuid51': {
                    '2021-02-19T14:00:00+0300': '2021-02-19T14:20:00+0300',
                    '2021-02-19T15:00:00+0300': '2021-02-19T15:01:00+0300',
                },
            },
            2,
            360,
            id='no history, some events',
        ),
        pytest.param(
            'unique6',
            ['dbid_uuid60', 'dbid_uuid61'],
            None,
            {},
            2,
            None,
            id='no working intervals and events at all',
        ),
        pytest.param(
            'unique9',
            ['dbid_uuid90', 'dbid_uuid91'],
            None,
            {},
            2,
            None,
            id='offline events only',
        ),
        pytest.param(
            'unique7',
            ['dbid_uuid70', 'dbid_uuid71'],
            None,
            {
                'dbid_uuid70': {
                    '2021-02-18T19:00:00+0300': '2021-02-18T19:20:00+0300',
                    '2021-02-18T20:55:00+0300': '2021-02-18T20:56:01+0300',
                    '2021-02-18T21:56:01+0300': '2021-02-18T21:57:01+0300',
                },
            },
            2,
            360,
            id='exclude and merge intervals',
        ),
        pytest.param(
            'unique7',
            ['dbid_uuid70', 'dbid_uuid71'],
            weariness_tools.WearinessConfig(
                360, 1080, 900, None, ['driving', 'transporting'],
            ),
            {
                'dbid_uuid70': {
                    '2021-02-18T19:00:00+0300': '2021-02-18T19:20:00+0300',
                    '2021-02-18T20:55:00+0300': '2021-02-18T20:56:00+0300',
                    '2021-02-18T21:56:01+0300': '2021-02-18T21:57:01+0300',
                },
            },
            2,
            360,
            id='working order statuses: driving & transporting',
        ),
        pytest.param(
            'unique7',
            ['dbid_uuid70', 'dbid_uuid71'],
            weariness_tools.WearinessConfig(
                360, 1080, 900, ['online'], ['driving', 'transporting'],
            ),
            {
                'dbid_uuid70': {
                    '2021-02-18T19:00:00+0300': '2021-02-18T19:20:00+0300',
                    '2021-02-18T20:55:00+0300': '2021-02-18T20:56:00+0300',
                },
            },
            2,
            360,
            id='working order statuses: driving & transporting, online only',
        ),
        pytest.param(
            'unique7',
            ['dbid_uuid70', 'dbid_uuid71'],
            weariness_tools.WearinessConfig(
                360, 1080, 900, ['busy'], ['driving', 'transporting'],
            ),
            {
                'dbid_uuid70': {
                    '2021-02-18T21:56:01+0300': '2021-02-18T21:57:01+0300',
                },
            },
            2,
            360,
            id='working order statuses: driving & transporting, busy only',
        ),
        pytest.param(
            'unique7',
            ['dbid_uuid70', 'dbid_uuid71'],
            weariness_tools.WearinessConfig(
                360, 1080, 900, None, ['transporting'],
            ),
            {
                'dbid_uuid70': {
                    '2021-02-18T19:00:00+0300': '2021-02-18T19:20:00+0300',
                    '2021-02-18T21:56:01+0300': '2021-02-18T21:57:01+0300',
                },
            },
            2,
            360,
            id='working order statuses: transporting only',
        ),
        pytest.param(
            'unique8',
            ['dbid_uuid80', 'dbid_uuid81'],
            None,
            {
                'dbid_uuid80': {
                    '2021-02-18T23:00:00+0300': '2021-02-18T23:10:00+0300',
                    '2021-02-19T02:00:00+0300': '2021-02-19T02:10:00+0300',
                    '2021-02-19T08:00:00+0300': '2021-02-19T08:10:00+0300',
                    '2021-02-19T14:00:00+0300': '2021-02-19T14:10:00+0300',
                },
            },
            2,
            15,
            marks=pytest.mark.config(
                DRIVER_WEARINESS_ENABLE_REMAINING_TIME_PREDICTION_USAGE=True,
            ),
            id='predict block for time on line, next call after 15 minutes',
        ),
        pytest.param(
            'unique8',
            ['dbid_uuid80', 'dbid_uuid81'],
            None,
            {
                'dbid_uuid80': {
                    '2021-02-18T23:00:00+0300': '2021-02-18T23:10:00+0300',
                    '2021-02-19T02:00:00+0300': '2021-02-19T02:10:00+0300',
                    '2021-02-19T08:00:00+0300': '2021-02-19T08:10:00+0300',
                    '2021-02-19T14:00:00+0300': '2021-02-19T14:10:00+0300',
                },
            },
            2,
            30,
            id='less than 3 hours left, next call after 30 minutes',
        ),
    ],
)
async def test_weariness_working_ranges_update(
        taxi_driver_weariness,
        stq,
        stq_runner,
        csh_mock,
        pgsql,
        experiments3,
        udid: str,
        profiles: List[str],
        config: Optional[weariness_tools.WearinessConfig],
        expected_ranges: Dict[str, Dict[str, str]],
        csh_events_calls: int,
        next_call_minutes: Optional[int],
        mockserver,
):
    @mockserver.json_handler('/tags/v1/assign')
    def mock_assign_tags(request):
        assert False

    if config:
        weariness_tools.add_experiment(experiments3, config)
        await taxi_driver_weariness.invalidate_caches()

    await stq_runner.weariness_working_ranges_update.call(task_id=udid)
    assert not mock_assign_tags.has_calls

    weariness_response = await taxi_driver_weariness.post(
        'v1/driver-weariness', data=json.dumps({'unique_driver_id': udid}),
    )
    assert weariness_response.status_code == 200

    tired_status = weariness_response.json()['tired_status']
    assert tired_status == 'not_tired'

    ranges = weariness_tools.select_working_ranges(
        pgsql['drivers_status_ranges'], profiles,
    )
    assert ranges == expected_ranges

    assert csh_mock.times_called == csh_events_calls

    if next_call_minutes:
        assert stq.weariness_working_ranges_update.times_called == 1
        now_utc = datetime.datetime(2021, 2, 19, 16, 0, 0)
        stq_call = stq.weariness_working_ranges_update.next_call()
        assert stq_call['queue'] == 'weariness_working_ranges_update'
        assert stq_call['eta'] == now_utc + datetime.timedelta(
            minutes=next_call_minutes,
        )
        assert stq_call['id'] == udid
        assert not stq_call['args']
    else:
        assert stq.weariness_working_ranges_update.times_called == 0


@pytest.mark.now('2021-02-19T15:00:00+03:00')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.pgsql(
    'drivers_status_ranges', files=['pg_new_working_ranges.sql'],
)
@pytest.mark.experiments3(filename='exp3_config_default.json')
@pytest.mark.csh_extended_events(events=_EVENTS)
@pytest.mark.config(
    DRIVER_WEARINESS_TAGGING_TIRED_DRIVERS={
        'is_enabled': True,
        'thresholds': [
            {
                'long_rest_time_left_m': 0,
                'orders_time_left_m': 0,
                'tag': 'tired_block',
            },
            {
                'long_rest_time_left_m': 60,
                'orders_time_left_m': 30,
                'tag': 'very_tired',
            },
            {
                'long_rest_time_left_m': 240,
                'orders_time_left_m': 120,
                'tag': 'little_tired',
            },
            {
                'long_rest_time_left_m': 600,
                'orders_time_left_m': 300,
                'tag': 'not_tired',
            },
        ],
    },
)
# driver has 40 minutes on orders and 910 minutes without long rest
@pytest.mark.parametrize(
    'weariness_bounds, expected_tags, next_call_minutes, remaining_minutes',
    [
        pytest.param(
            weariness_tools.WearinessConfig(360, 1080, 900),
            {'little_tired': {'until': '2021-02-19T17:10:00+0000'}},
            20,
            170,
            id='put tag on long_rest threshold',
        ),
        pytest.param(
            weariness_tools.WearinessConfig(360, 1080, 50),
            {'very_tired': {'until': '2021-02-19T17:10:00+0000'}},
            5,
            10,
            id='put tag on orders_time threshold',
        ),
        # TODO: этот тест делает то же самое, что и 1?
        pytest.param(
            weariness_tools.WearinessConfig(360, 1080, 900),
            {'little_tired': {'until': '2021-02-19T17:10:00+0000'}},
            20,
            170,
            id='put tag on little_tired threshold',
        ),
        pytest.param(
            weariness_tools.WearinessConfig(360, 970, 900),
            {'very_tired': {'until': '2021-02-19T17:10:00+0000'}},
            10,
            60,
            id='put tag on very_tired threshold',
        ),
        pytest.param(
            weariness_tools.WearinessConfig(360, 910, 900),
            {'tired_block': {'until': '2021-02-19T17:10:00+0000'}},
            15,
            0,
            id='0 minutes left, put tired_block tag',
        ),
        pytest.param(
            weariness_tools.WearinessConfig(10, 910, 900),
            None,
            240,
            900,
            id='driver after long rest, no new tags required',
        ),
        pytest.param(
            weariness_tools.WearinessConfig(70, 1080, 5),
            {'tired_block': {'until': '2021-02-19T12:20:00+0000'}},
            15,
            0,
            id='tag should be active only for 10 minutes, when driver will be '
            'unblocked',
        ),
    ],
)
async def test_tired_driver_tagging(
        taxi_driver_weariness,
        stq,
        stq_runner,
        csh_mock,
        pgsql,
        experiments3,
        mockserver,
        weariness_bounds: weariness_tools.WearinessConfig,
        expected_tags: Optional[Dict[str, Any]],
        next_call_minutes: Optional[int],
        remaining_minutes: int,
):
    udid = 'unique8'
    driver_profiles = ['dbid_uuid80', 'dbid_uuid81']

    @mockserver.json_handler('/tags/v1/assign')
    def mock_assign_tags(request):
        data = request.json
        assert data['provider'] == 'driver-weariness'
        entities: List[Dict[str, Any]] = data['entities']
        expected_entity = {
            'name': udid,
            'type': 'udid',
            'tags': expected_tags or {},
        }
        assert entities == [expected_entity]

        return {'status': 'ok'}

    weariness_tools.add_experiment(experiments3, weariness_bounds)
    await taxi_driver_weariness.invalidate_caches()

    await stq_runner.weariness_working_ranges_update.call(task_id=udid)
    assert mock_assign_tags.times_called == 1
    assert csh_mock.times_called == 1

    await taxi_driver_weariness.invalidate_caches()
    weariness_response = await taxi_driver_weariness.post(
        'v1/driver-weariness', data=json.dumps({'unique_driver_id': udid}),
    )
    assert weariness_response.status_code == 200

    weariness_data = weariness_response.json()
    assert weariness_data['remaining_time'] == remaining_minutes * 60

    working_ranges = weariness_tools.select_working_ranges(
        pgsql['drivers_status_ranges'], driver_profiles,
    )
    assert working_ranges == {
        'dbid_uuid80': {
            '2021-02-18T23:00:00+0300': '2021-02-18T23:10:00+0300',
            '2021-02-19T02:00:00+0300': '2021-02-19T02:10:00+0300',
            '2021-02-19T08:00:00+0300': '2021-02-19T08:10:00+0300',
            '2021-02-19T14:00:00+0300': '2021-02-19T14:10:00+0300',
        },
    }

    if expected_tags and 'tired_block' in expected_tags:
        actual_stq_queue = stq.weariness_working_ranges_update_tired
        stq_name = 'weariness_working_ranges_update_tired'
    else:
        actual_stq_queue = stq.weariness_working_ranges_update
        stq_name = 'weariness_working_ranges_update'

    if next_call_minutes:
        assert actual_stq_queue.times_called == 1
        now_utc = datetime.datetime(2021, 2, 19, 12, 0, 0)
        stq_call = actual_stq_queue.next_call()
        assert stq_call['queue'] == stq_name
        assert stq_call['eta'] == now_utc + datetime.timedelta(
            minutes=next_call_minutes,
        )
        assert stq_call['id'] == udid
        assert not stq_call['args']
    else:
        assert (
            stq.weariness_working_ranges_update.times_called
            + stq.weariness_working_ranges_update_tired.times_called
        ) == 0


@pytest.mark.now('2021-02-18T11:00:00+0300')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.pgsql(
    'drivers_status_ranges', files=['pg_new_working_ranges.sql'],
)
@pytest.mark.experiments3(filename='exp3_config_default.json')
@pytest.mark.csh_extended_events(events=_EVENTS)
@pytest.mark.config(
    DRIVER_WEARINESS_TAGGING_TIRED_DRIVERS={
        'is_enabled': True,
        'thresholds': [
            {
                'long_rest_time_left_m': 0,
                'orders_time_left_m': 0,
                'tag': 'tired_block',
            },
            {
                'long_rest_time_left_m': 60,
                'orders_time_left_m': 30,
                'tag': 'very_tired',
            },
            {
                'long_rest_time_left_m': 240,
                'orders_time_left_m': 120,
                'tag': 'little_tired',
            },
            {
                'long_rest_time_left_m': 600,
                'orders_time_left_m': 300,
                'tag': 'not_tired',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'udid, push_required',
    [
        pytest.param(
            'unique9', False, id='driver last worked long ago, no push',
        ),
        pytest.param('unique10', True, id='driver rested well enough, push'),
        pytest.param('unique11', False, id='driver still tired, no push'),
    ],
)
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'driver_weariness.end_block.text': {
            'ru': ['Ваш блок по усталости окончен'],
        },
    },
)
async def test_rested_driver_push(
        taxi_driver_weariness,
        stq_runner,
        taxi_config,
        experiments3,
        mockserver,
        udid,
        push_required,
):
    @mockserver.json_handler('/tags/v1/assign')
    def _mock_assign_tags(request):
        return {'status': 'ok'}

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == {
            'service': 'taximeter',
            'notification': {'text': 'Ваш блок по усталости окончен'},
            'intent': 'PersonalOffer',
            'client_id': 'dbid-uuid100',
            'data': {},
        }
        return {'notification_id': 'throwaway'}

    weariness_tools.add_experiment(
        experiments3, weariness_tools.WearinessConfig(360, 1080, 900),
    )

    await taxi_driver_weariness.invalidate_caches()

    await stq_runner.weariness_working_ranges_update_tired.call(task_id=udid)

    if push_required:
        assert mock_client_notify.times_called == 1
    else:
        assert mock_client_notify.times_called == 0
