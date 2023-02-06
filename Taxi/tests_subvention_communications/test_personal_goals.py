# pylint: disable=C0302

import datetime
import typing

import dateutil.parser
import pytest
import pytz

import testsuite

from . import test_common


def _parse_time(as_str: str, default_tz='UTC') -> datetime.datetime:
    """
    Parses string with time of almost any format to datetime.datetime
    with awared timezone. You can compare returned datetimes between
    each other and don't care about difference in time zones.
    """
    _dt = dateutil.parser.parse(as_str)
    if not _dt.tzinfo:
        utc = pytz.timezone(default_tz)
        _dt = utc.localize(_dt)
    return _dt


def _parse_time_range(
        rng: typing.Tuple[str, ...],
) -> typing.Tuple[datetime.datetime, ...]:
    return tuple(_parse_time(t) for t in rng)


def _get_last_update_cursor(pgsql):
    cursor = pgsql[test_common.PG_CLUSTER].cursor()

    cursor.execute(
        """SELECT last_time, last_cursor
           FROM sc.personal_goal_updates_last_time""",
    )

    row = cursor.fetchone()

    if row is None:
        return (None, None)

    return row


def _set_last_update_cursor(
        pgsql,
        last_time: typing.Union[datetime.datetime, str, None],
        last_cursor: typing.Optional[str],
):
    cursor = pgsql[test_common.PG_CLUSTER].cursor()

    if last_time is None:
        cursor.execute("""TRUNCATE sc.personal_goal_updates_last_time""")
        return

    if isinstance(last_time, str):
        last_time = _parse_time(last_time)

    cursor.execute(
        """INSERT INTO sc.personal_goal_updates_last_time (last_time, last_cursor)
           VALUES (%s, %s)""",
        (last_time, last_cursor),
    )


def _get_last_update_time(pgsql):
    return _get_last_update_cursor(pgsql)[0]


def _set_last_update_time(pgsql, last_time):
    return _set_last_update_cursor(pgsql, last_time, None)


@pytest.mark.parametrize(
    'now_time, last_update_time',
    [
        (
            # now_time
            '2021-01-01T12:31:05+00:00',
            # last_update_time
            None,
        ),
        (
            # now_time
            '2021-01-01T12:31:05+00:00',
            # last_update_time
            '2021-01-01T12:18:00+00:00',
        ),
    ],
)
@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_SCHEDULES_UPDATES_LIMIT=1,
    SUBVENTION_COMMUNICATIONS_PERSONAL_GOALS={
        'enabled': True,
        'notify_before_h': 12,
    },
)
@test_common.suspend_periodic_tasks
async def test_updates_request(
        taxi_subvention_communications,
        mocked_time,
        pgsql,
        load_json,
        mock_bsx,
        now_time,
        last_update_time,
):
    mocked_time.set(_parse_time(now_time))
    _set_last_update_time(pgsql, last_time=last_update_time)
    mock_bsx.set_docs(load_json('bsx_default_3_schedules.json'))

    await test_common.run_personal_goal_updates_task_once(
        taxi_subvention_communications,
    )

    if last_update_time is None:
        assert mock_bsx.get_schedules_updates_calls() == []
        return

    assert mock_bsx.get_schedules_updates_calls() == [
        {
            'time_range': {'start': last_update_time, 'end': now_time},
            'rule_type': 'goal',
            'is_personal': True,
            'limit': 1,
        },
        {
            'time_range': {'start': last_update_time, 'end': now_time},
            'rule_type': 'goal',
            'is_personal': True,
            'cursor': {'mock_cursor': '1'},
            'limit': 1,
        },
        {
            'time_range': {'start': last_update_time, 'end': now_time},
            'rule_type': 'goal',
            'is_personal': True,
            'cursor': {'mock_cursor': '2'},
            'limit': 1,
        },
    ]


@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_SCHEDULES_UPDATES_LIMIT=1,
    SUBVENTION_COMMUNICATIONS_PERSONAL_GOALS={
        'enabled': True,
        'notify_before_h': 12,
    },
)
@test_common.suspend_periodic_tasks
async def test_updates_request_paging(
        taxi_subvention_communications,
        mocked_time,
        pgsql,
        load_json,
        mockserver,
):
    now_time = '2021-01-01T12:31:05+00:00'
    last_update_time = '2021-01-01T12:18:00+00:00'

    @mockserver.json_handler('/billing-subventions-x/v2/schedules/updates')
    def schedules_updates(request):
        return {'schedules': load_json('bsx_default_3_schedules.json')[1:2]}

    mocked_time.set(_parse_time(now_time))
    _set_last_update_cursor(pgsql, last_update_time, '{"mock_cursor":"1"}')

    await test_common.run_personal_goal_updates_task_once(
        taxi_subvention_communications,
    )

    next_call = schedules_updates.next_call()
    request_json = next_call['request'].json

    assert request_json == {
        'time_range': {'start': last_update_time, 'end': now_time},
        'rule_type': 'goal',
        'is_personal': True,
        'cursor': {'mock_cursor': '1'},
        'limit': 1,
    }

    last_update_time_real, last_cursor_real = _get_last_update_cursor(pgsql)

    assert last_update_time_real == _parse_time(now_time)
    assert last_cursor_real is None


def _extract_task_parameters(queue):
    result = []
    while True:
        try:
            next_call = queue.next_call()
            # log_extra is set implicitly and has random value
            del next_call['kwargs']['log_extra']
            result.append(
                {
                    'kwargs': next_call['kwargs'],
                    'eta': next_call['eta'].isoformat(),
                    'id': next_call['id'],
                },
            )
        except testsuite.utils.callinfo.CallQueueEmptyError:
            break
    return result


def _extract_goal_schedules_stats(pgsql):
    cursor = pgsql[test_common.PG_CLUSTER].cursor()
    cursor.execute(
        """SELECT schedule_ref_udid, rule_ends_at FROM sc.goal_rule_stats""",
    )
    return {row[0]: {'rule_ends_at': row[1].isoformat()} for row in cursor}


def _set_goal_rule_stats(
        pgsql, schedule_ref_udid, rule_ends_at, last_window_notified,
):
    if isinstance(rule_ends_at, str):
        rule_ends_at = _parse_time(rule_ends_at)

    cursor = pgsql[test_common.PG_CLUSTER].cursor()
    cursor.execute(
        """
        INSERT INTO sc.goal_rule_stats (
            schedule_ref_udid, rule_ends_at, last_window_notified
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (schedule_ref_udid)
          DO UPDATE SET
            rule_ends_at = excluded.rule_ends_at,
            last_window_notified = excluded.last_window_notified
        """,
        (schedule_ref_udid, rule_ends_at, last_window_notified),
    )


def _get_goal_rule_stats(pgsql):
    cursor = pgsql[test_common.PG_CLUSTER].cursor()
    cursor.execute(
        """
        SELECT schedule_ref_udid, rule_ends_at, last_window_notified
        FROM sc.goal_rule_stats
        """,
    )
    return {
        row[0]: {
            'rule_ends_at': row[1].isoformat(),
            'last_window_notified': row[2],
        }
        for row in cursor
    }


@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_PERSONAL_GOALS={
        'enabled': True,
        'notify_before_h': 12,
    },
)
@test_common.suspend_periodic_tasks
async def test_personal_goal_updates_job(
        taxi_subvention_communications,
        mocked_time,
        pgsql,
        load_json,
        mock_bsx,
        stq,
):
    mocked_time.set(_parse_time('2020-01-01T12:20:00+00:00'))
    _set_last_update_time(pgsql, last_time='2020-01-01T12:18:00+00:00')
    mock_bsx.set_docs(load_json('bsx_default_3_schedules.json'))

    await test_common.run_personal_goal_updates_task_once(
        taxi_subvention_communications,
    )

    assert _extract_task_parameters(
        stq.subvention_communications_personal_goals,
    ) == load_json('expected_task_parameters.json')

    assert _get_goal_rule_stats(pgsql) == {
        'schref1_A_udid1': {
            'rule_ends_at': '2020-01-04T00:00:00+03:00',
            'last_window_notified': None,
        },
        'schref1_B_udid1': {
            'rule_ends_at': '2020-01-04T00:00:00+03:00',
            'last_window_notified': None,
        },
        'schref2_A_udid2': {
            'rule_ends_at': '2020-01-04T00:00:00+03:00',
            'last_window_notified': None,
        },
        'schref3_A_udid3': {
            'rule_ends_at': '2020-01-03T23:00:00+03:00',
            'last_window_notified': None,
        },
    }

    assert (
        _get_last_update_time(pgsql).isoformat() == '2020-01-01T15:20:00+03:00'
    )


@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_PERSONAL_GOALS={
        'enabled': True,
        'notify_before_h': 12,
    },
)
@test_common.suspend_periodic_tasks
async def test_personal_goal_updates_job_paging(
        taxi_subvention_communications,
        mocked_time,
        pgsql,
        load_json,
        mockserver,
        stq,
):
    @mockserver.json_handler('/billing-subventions-x/v2/schedules/updates')
    def schedules_updates(_):
        if schedules_updates.times_called >= 1:
            return mockserver.make_response(
                status=500,
                json={'code': '500', 'message': 'Internal Server Error'},
            )

        return {
            'schedules': load_json('bsx_default_3_schedules.json')[1:2],
            'next_cursor': {'mock_cursor': '2'},
        }

    last_update_time = '2020-01-01T12:18:00+00:00'

    mocked_time.set(_parse_time('2020-01-01T12:20:00+00:00'))
    _set_last_update_time(pgsql, last_update_time)

    await test_common.run_personal_goal_updates_task_once(
        taxi_subvention_communications,
    )

    assert _extract_task_parameters(
        stq.subvention_communications_personal_goals,
    ) == load_json('expected_task_parameters.json')

    assert _get_goal_rule_stats(pgsql) == {
        'schref2_A_udid2': {
            'rule_ends_at': '2020-01-04T00:00:00+03:00',
            'last_window_notified': None,
        },
    }

    last_update_time_real, last_cursor_real = _get_last_update_cursor(pgsql)

    assert last_update_time_real == _parse_time(last_update_time)
    assert last_cursor_real == '{"mock_cursor":"2"}'


SCHEDULE_FOR_ALL_DAYS = {
    'schedule': [{'counter': 'A', 'start': '00:00', 'week_day': 'mon'}],
    'steps': [{'id': 'A', 'steps': [{'amount': '4000', 'nrides': 133}]}],
}

SCHEDULE_MON_TUE = {
    'schedule': [
        {'counter': 'A', 'start': '00:00', 'week_day': 'mon'},
        {'counter': '0', 'start': '18:00', 'week_day': 'tue'},
    ],
    'steps': [{'id': 'A', 'steps': [{'amount': '4000', 'nrides': 133}]}],
}

SCHEDULE_WED_THU_FRI = {
    'schedule': [
        {'counter': 'A', 'start': '00:00', 'week_day': 'wed'},
        {'counter': '0', 'start': '18:00', 'week_day': 'fri'},
    ],
    'steps': [{'id': 'A', 'steps': [{'amount': '4000', 'nrides': 133}]}],
}

SCHEDULE_WED_FRI = {
    'schedule': [
        {'counter': 'A', 'start': '00:00', 'week_day': 'wed'},
        {'counter': '0', 'start': '18:00', 'week_day': 'wed'},
        {'counter': 'A', 'start': '00:00', 'week_day': 'fri'},
        {'counter': '0', 'start': '18:00', 'week_day': 'fri'},
    ],
    'steps': [{'id': 'A', 'steps': [{'amount': '4000', 'nrides': 133}]}],
}

SCHEDULE_WED = {
    'schedule': [
        {'counter': 'A', 'start': '00:00', 'week_day': 'wed'},
        {'counter': '0', 'start': '18:00', 'week_day': 'wed'},
    ],
    'steps': [{'id': 'A', 'steps': [{'amount': '4000', 'nrides': 133}]}],
}

EMPTY_SCHEDULE = {
    'schedule': [],
    'steps': [{'id': 'A', 'steps': [{'amount': '4000', 'nrides': 133}]}],
}


@pytest.mark.parametrize(
    'time_now,window,last_window_notified,schedule,'
    'expected_last_window_notified,should_notify_for_window,'
    'should_reschedule',
    [
        pytest.param(
            # now
            '2020-01-14T11:00:00+03:00',
            # window
            3,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            None,
            # should_notify_for_window
            None,
            # should_reschedule
            '2020-01-14T12:00:00+03:00',
            id='too early',
        ),
        pytest.param(
            # now
            '2020-01-14T12:09:00+03:00',
            # window
            3,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            0,
            # should_notify_for_window
            ('2020-01-15T00:00:00+03:00', '2020-01-18T00:00:00+03:00'),
            # should_reschedule
            '2020-01-17T12:00:00+03:00',
            id='first window before start',
        ),
        pytest.param(
            # now
            '2020-01-15T04:01:00+03:00',
            # window
            3,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            0,
            # should_notify_for_window
            ('2020-01-15T00:00:00+03:00', '2020-01-18T00:00:00+03:00'),
            # should_reschedule
            '2020-01-17T12:00:00+03:00',
            id='first window after start',
        ),
        pytest.param(
            # now
            '2020-01-18T03:05:00+03:00',
            # window
            3,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            0,
            # should_notify_for_window
            None,
            # should_reschedule
            '2020-01-17T12:00:00+03:00',
            id='first window too late',
        ),
        pytest.param(
            # now
            '2020-01-17T03:05:00+03:00',
            # window
            3,
            # last_window_notified
            0,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            0,
            # should_notify_for_window
            None,
            # should_reschedule
            '2020-01-17T12:00:00+03:00',
            id='second window too early',
        ),
        pytest.param(
            # now
            '2020-01-17T12:05:00+03:00',
            # window
            3,
            # last_window_notified
            0,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            1,
            # should_notify_for_window
            ('2020-01-18T00:00:00+03:00', '2020-01-21T00:00:00+03:00'),
            # should_reschedule
            '2020-01-20T12:00:00+03:00',
            id='second window before start',
        ),
        pytest.param(
            # now
            '2020-01-20T14:25:00+03:00',
            # window
            3,
            # last_window_notified
            0,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            1,
            # should_notify_for_window
            ('2020-01-18T00:00:00+03:00', '2020-01-21T00:00:00+03:00'),
            # should_reschedule
            '2020-01-20T12:00:00+03:00',
            id='second window after start',
        ),
        pytest.param(
            # now
            '2020-01-20T14:25:00+03:00',
            # window
            3,
            # last_window_notified
            0,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            1,
            # should_notify_for_window
            ('2020-01-18T00:00:00+03:00', '2020-01-21T00:00:00+03:00'),
            # should_reschedule
            '2020-01-20T12:00:00+03:00',
            id='second window after start',
        ),
        pytest.param(
            # now
            '2020-01-29T12:00:00+03:00',
            # window
            3,
            # last_window_notified
            5,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            5,
            # should_notify_for_window
            None,
            # should_reschedule
            None,
            id='no more windows',
        ),
        pytest.param(
            # now
            '2020-01-14T12:00:00+03:00',
            # window
            3,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_MON_TUE,
            # expected_last_window_notified
            None,
            # should_notify_for_window
            None,
            # should_reschedule
            '2020-01-19T12:00:00+03:00',
            id='no workdays in first window',
        ),
        pytest.param(
            # now
            '2020-01-19T12:00:00+03:00',
            # window
            3,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_MON_TUE,
            # expected_last_window_notified
            1,
            # should_notify_for_window
            ('2020-01-20T00:00:00+03:00', '2020-01-21T00:00:00+03:00'),
            # should_reschedule
            '2020-01-20T12:00:00+03:00',
            id='no workdays in first window, rescheduled',
        ),
        pytest.param(
            # now
            '2020-01-19T12:00:00+03:00',
            # window
            4,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_MON_TUE,
            # expected_last_window_notified
            1,
            # should_notify_for_window
            ('2020-01-20T00:00:00+03:00', '2020-01-22T00:00:00+03:00'),
            # should_reschedule
            '2020-01-22T12:00:00+03:00',
            id='no workdays in first window and half of second window',
        ),
        pytest.param(
            # now
            '2020-01-14T12:00:00+03:00',
            # window
            1,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_last_window_notified
            6,
            # should_notify_for_range
            ('2020-01-15T00:00:00+03:00', '2020-01-22T00:00:00+03:00'),
            # should_reschedule
            '2020-01-21T12:00:00+03:00',
            id='7 one-day windows at once',
        ),
        pytest.param(
            # now
            '2020-01-14T12:00:00+03:00',
            # window
            1,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_MON_TUE,
            # expected_last_window_notified
            None,
            # should_notify_for_range
            None,
            # should_reschedule
            '2020-01-19T12:00:00+03:00',
            id='7 one-day windows, mon-tue',
        ),
        pytest.param(
            # now
            '2020-01-19T12:00:00+03:00',
            # window
            1,
            # last_window_notified
            None,
            # schedule
            SCHEDULE_MON_TUE,
            # expected_last_window_notified
            11,
            # should_notify_for_range
            ('2020-01-20T00:00:00+03:00', '2020-01-22T00:00:00+03:00'),
            # should_reschedule
            '2020-01-26T12:00:00+03:00',
            id='7 one-day windows, mon-tue, its time',
        ),
        pytest.param(
            # now
            '2020-01-17T12:00:00+03:00',
            # window
            1,
            # last_window_notified
            2,
            # schedule
            SCHEDULE_WED_THU_FRI,
            # expected_last_window_notified
            2,
            # should_notify_for_range
            None,
            # should_reschedule
            '2020-01-21T12:00:00+03:00',
            id='7 one-day windows, wed-thu-fri',
        ),
    ],
)
@pytest.mark.now('2020-01-15T12:20:00+00:00')
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_when_notify(
        taxi_subvention_communications,
        stq_runner,
        stq,
        load_json,
        mocked_time,
        testpoint,
        pgsql,
        time_now,
        window,
        last_window_notified,
        schedule,
        expected_last_window_notified,
        should_notify_for_window,
        should_reschedule,
):
    notified_windows = []

    @testpoint('notify')
    def _notify(data):
        notified_windows.append(
            (data['stripped_range_start'], data['stripped_range_end']),
        )

    mocked_time.set(_parse_time(time_now))
    _set_goal_rule_stats(
        pgsql,
        schedule_ref_udid='schref_A_udid',
        rule_ends_at='2020-02-01T00:00:00+03:00',
        last_window_notified=last_window_notified,
    )

    kwargs = load_json('test_task_params.json')
    kwargs['schedule_for_goal']['window'] = window
    kwargs['schedule_for_goal']['schedule'] = schedule

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id', args=[], kwargs=kwargs,
    )

    if should_notify_for_window:
        notified_windows = [_parse_time_range(wnd) for wnd in notified_windows]
        assert notified_windows == [
            _parse_time_range(should_notify_for_window),
        ]
    else:
        assert notified_windows == []

    if should_reschedule:
        params = _extract_task_parameters(
            stq.subvention_communications_personal_goals,
        )
        assert len(params) == 1
        assert _parse_time(params[0]['eta']) == _parse_time(should_reschedule)
        assert params[0]['kwargs'] == kwargs

        assert (
            _get_goal_rule_stats(pgsql)['schref_A_udid'][
                'last_window_notified'
            ]
            == expected_last_window_notified
        )
    else:
        assert (
            _extract_task_parameters(
                stq.subvention_communications_personal_goals,
            )
            == []
        )
        assert _get_goal_rule_stats(pgsql) == {}


@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_NOTIFICATIONS=test_common.create_config(
        'personal_goals', 'new', ['sms'],
    ),
)
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_send_sms_to_unique_phones(
        stq_runner,
        mocked_time,
        pgsql,
        load_json,
        clients,
        mock_unique_drivers,
        mock_driver_profiles,
):
    mock_unique_drivers.set_udid_to_profiles(
        {
            'udid': [
                {'driver_profile_id': 'uuid1', 'park_id': 'dbid1'},
                {'driver_profile_id': 'uuid2', 'park_id': 'dbid2'},
                {'driver_profile_id': 'uuid3', 'park_id': 'dbid3'},
            ],
        },
    )
    mock_driver_profiles.set_dbiduuid_to_data(
        {
            'dbid1_uuid1': {'phone_pd_ids': [{'pd_id': 'pdid1'}]},
            'dbid2_uuid2': {'phone_pd_ids': [{'pd_id': 'pdid2'}]},
            'dbid3_uuid3': {'phone_pd_ids': [{'pd_id': 'pdid1'}]},
        },
    )

    mocked_time.set(_parse_time('2020-01-14T12:09:00+03:00'))
    _set_goal_rule_stats(
        pgsql,
        schedule_ref_udid='schref_A_udid',
        rule_ends_at='2020-01-24T00:00:00+03:00',
        last_window_notified=None,
    )

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id',
        args=[],
        kwargs=load_json('default_test_task_params.json'),
    )

    calls = test_common.extract_all_requests(clients.send_sms)
    phone_ids = {c.json['phone_id'] for c in calls}
    assert phone_ids == {'pdid1', 'pdid2'}

    idempotency_tokens = {c.headers['X-Idempotency-Token'] for c in calls}
    assert (
        len(idempotency_tokens) == 2
    ), 'Idempotency tokens should be different for different profiles'


@pytest.mark.parametrize('use_client_notify', [True, False])
@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_NOTIFICATIONS=test_common.create_config(
        'personal_goals', 'new', ['sms', 'wall', 'push'],
    ),
)
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_send_notification(
        stq_runner,
        taxi_config,
        mocked_time,
        pgsql,
        load_json,
        clients,
        mock_unique_drivers,
        mock_driver_profiles,
        use_client_notify,
):
    taxi_config.set_values(
        {'SUBVENTION_COMMUNICATIONS_USE_CLIENT_NOTIFY': use_client_notify},
    )

    mock_unique_drivers.set_udid_to_profiles(
        {'udid': [{'driver_profile_id': 'uuid1', 'park_id': 'dbid1'}]},
    )
    mock_driver_profiles.set_dbiduuid_to_data(
        {'dbid1_uuid1': {'phone_pd_ids': [{'pd_id': 'pdid1'}]}},
    )

    mocked_time.set(_parse_time('2020-01-14T12:09:00+03:00'))
    _set_goal_rule_stats(
        pgsql,
        schedule_ref_udid='schref_A_udid',
        rule_ends_at='2020-01-24T00:00:00+03:00',
        last_window_notified=None,
    )

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id',
        args=[],
        kwargs=load_json('default_test_task_params.json'),
    )

    test_common.check_handler(
        clients.send_sms,
        1,
        {
            'intent': 'personal_goal_new',
            'phone_id': 'pdid1',
            'sender': 'go',
            # this test doesn't check the content of the text
            'text': (test_common.DOESNT_MATTER),
        },
    )

    test_common.check_handler(
        clients.driver_wall_add,
        1,
        {
            'filters': {'drivers': ['dbid1_uuid1']},
            'id': '60d74d0f3fe2a7f57b483456353e0c04',
            'template': {
                'alert': False,
                # this test doesn't check the content of the text
                'text': (test_common.DOESNT_MATTER),
                'title': {
                    'key': (
                        'subvention_communications.goals.new_window_wall_title'
                    ),
                    'keyset': 'taximeter_messages',
                },
                'type': 'newsletter',
            },
        },
    )

    if use_client_notify:
        test_common.check_handler(
            clients.client_notify,
            1,
            {
                'intent': 'PersonalOffer',
                'service': 'taximeter',
                'client_id': 'dbid1-uuid1',
                'notification': {
                    # this test doesn't check the content of the text
                    'text': test_common.DOESNT_MATTER,
                },
                'data': {'code': 1300},
            },
        )
    else:
        test_common.check_handler(
            clients.driver_bulk_push,
            1,
            {
                'action': 'MessageNew',
                'code': 1300,
                # this test doesn't check the content of the text
                'data': {'text': test_common.DOESNT_MATTER},
                'drivers': [{'dbid': 'dbid1', 'uuid': 'uuid1'}],
            },
        )


@pytest.mark.parametrize(
    'error_code,skip_ucomm_400,throw_error,send_calls_num',
    [
        (None, False, False, 1),
        (400, False, True, 1),
        (400, True, False, 1),
        (500, True, True, 3),
    ],
)
@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_NOTIFICATIONS=test_common.create_config(
        'personal_goals', 'new', ['sms'],
    ),
)
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_send_sms_fail(
        stq,
        stq_runner,
        taxi_config,
        mocked_time,
        pgsql,
        load_json,
        clients,
        mockserver,
        mock_unique_drivers,
        mock_driver_profiles,
        error_code,
        skip_ucomm_400,
        throw_error,
        send_calls_num,
):
    taxi_config.set_values(
        {'SUBVENTION_COMMUNICATIONS_SKIP_400_ON_SMS_SEND': skip_ucomm_400},
    )

    mock_unique_drivers.set_udid_to_profiles(
        {'udid': [{'driver_profile_id': 'uuid1', 'park_id': 'dbid1'}]},
    )
    mock_driver_profiles.set_dbiduuid_to_data(
        {'dbid1_uuid1': {'phone_pd_ids': [{'pd_id': 'pdid1'}]}},
    )

    mocked_time.set(_parse_time('2020-01-14T12:09:00+03:00'))
    _set_goal_rule_stats(
        pgsql,
        schedule_ref_udid='schref_A_udid',
        rule_ends_at='2020-01-18T00:00:00+03:00',
        last_window_notified=None,
    )

    if error_code:
        clients.set_send_sms_error_code(error_code)

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id',
        args=[],
        kwargs=load_json('default_test_task_params.json'),
        expect_fail=throw_error,
    )

    test_common.check_handler(
        clients.send_sms,
        send_calls_num,
        {
            'intent': 'personal_goal_new',
            'phone_id': 'pdid1',
            'sender': 'go',
            # this test doesn't check the content of the text
            'text': (test_common.DOESNT_MATTER),
        },
    )

    assert (
        _extract_task_parameters(stq.subvention_communications_personal_goals)
        == []
    )


@pytest.fixture(name='default_param_test_setup')
def _default_param_test_setup(
        mocked_time,
        pgsql,
        taxi_config,
        mock_unique_drivers,
        mock_driver_profiles,
):
    taxi_config.set_values(
        {
            'SUBVENTION_COMMUNICATIONS_NOTIFICATIONS': (
                test_common.create_config(
                    'personal_goals', 'new', ['sms', 'wall', 'push'],
                )
            ),
        },
    )

    mock_unique_drivers.set_udid_to_profiles(
        {'udid': [{'driver_profile_id': 'uuid1', 'park_id': 'dbid1'}]},
    )
    mock_driver_profiles.set_dbiduuid_to_data(
        {'dbid1_uuid1': {'phone_pd_ids': [{'pd_id': 'pdid1'}]}},
    )

    mocked_time.set(_parse_time('2020-01-14T12:09:00+03:00'))
    _set_goal_rule_stats(
        pgsql,
        schedule_ref_udid='schref_A_udid',
        rule_ends_at='2020-01-24T00:00:00+03:00',
        last_window_notified=None,
    )


def _assert_that_subset(subset, checked_set):
    checked_subset = {}
    for key in subset.keys():
        try:
            checked_subset[key] = checked_set[key]
        except KeyError:
            pass
    assert subset == checked_subset


def _check_params_subset(clients, expected_params):
    calls = test_common.extract_all_bodies(clients.send_sms)
    assert len(calls) == 1
    _assert_that_subset(expected_params, calls[0]['text']['params'])

    calls = test_common.extract_all_bodies(clients.driver_wall_add)
    assert len(calls) == 1
    _assert_that_subset(
        expected_params, calls[0]['template']['text']['params'],
    )

    calls = test_common.extract_all_bodies(clients.driver_bulk_push)
    assert len(calls) == 1
    _assert_that_subset(expected_params, calls[0]['data']['text']['params'])


@pytest.mark.parametrize(
    'schedule,expected_params',
    [
        pytest.param(
            # schedule
            {
                'schedule': [
                    {'counter': 'A', 'start': '00:00', 'week_day': 'mon'},
                ],
                'steps': [
                    {'id': 'A', 'steps': [{'amount': '800', 'nrides': 10}]},
                ],
            },
            # expected_params
            {
                'bonus': {
                    'keyset': 'taximeter_messages',
                    'key': 'subventions.rule_sum',
                    'params': {'currency_sign': '₽', 'sum': '800'},
                },
                'rides': {
                    'keyset': 'taximeter_messages',
                    'key': 'subvention_communications.goals.rides.single',
                    'params': {'rides': {'value': 10, 'count': 10}},
                },
            },
            id='single',
        ),
        pytest.param(
            # schedule
            {
                'schedule': [
                    {'counter': 'A', 'start': '00:00', 'week_day': 'mon'},
                ],
                'steps': [
                    {
                        'id': 'A',
                        'steps': [
                            {'amount': '90', 'nrides': 10},
                            {'amount': '30', 'nrides': 5},
                            {'amount': '50', 'nrides': 8},
                        ],
                    },
                ],
            },
            # expected_params
            {
                'bonus': {
                    'keyset': 'taximeter_messages',
                    'key': 'subvention_communications.goals.bonus.range',
                    'params': {
                        'from': {
                            'keyset': 'taximeter_messages',
                            'key': 'subventions.rule_sum',
                            'params': {'currency_sign': '₽', 'sum': '30'},
                        },
                        'to': {
                            'keyset': 'taximeter_messages',
                            'key': 'subventions.rule_sum',
                            'params': {'currency_sign': '₽', 'sum': '90'},
                        },
                    },
                },
                'rides': {
                    'keyset': 'taximeter_messages',
                    'key': 'subvention_communications.goals.rides.range',
                    'params': {'from': 5, 'to': 10},
                },
            },
            id='range',
        ),
    ],
)
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_param_bonus_rides(
        stq_runner,
        default_param_test_setup,
        load_json,
        clients,
        expected_params,
        schedule,
):
    task_kwargs = load_json('default_test_task_params.json')
    task_kwargs['schedule_for_goal']['schedule'] = schedule

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id', args=[], kwargs=task_kwargs,
    )

    _check_params_subset(clients, expected_params)


@pytest.mark.parametrize(
    'window,rule_starts,rule_ends,schedule,expected_params',
    [
        pytest.param(
            # window
            1,
            # rule_starts
            '2020-01-15T00:00:00+03:00',
            # rule_ends
            '2020-01-18T00:00:00+03:00',
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_params
            {
                'every_day': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'subvention_communications.goals.every_day',
                        },
                    },
                },
            },
            id='1 day window, every day',
        ),
        pytest.param(
            # window
            1,
            # rule_starts
            '2020-01-15T00:00:00+03:00',
            # rule_ends
            '2020-01-22T00:00:00+03:00',
            # schedule
            SCHEDULE_WED_THU_FRI,
            # expected_params
            {
                'every_day': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'subvention_communications.goals.every_day',
                        },
                    },
                },
            },
            id='1 day window, schedule for 3 days',
        ),
        pytest.param(
            # window
            1,
            # rule_starts
            '2020-01-15T00:00:00+03:00',
            # rule_ends
            '2020-01-22T00:00:00+03:00',
            # schedule
            SCHEDULE_WED_FRI,
            # expected_params
            {'every_day': ''},
            id='1 day window, schedule with gap',
        ),
        pytest.param(
            # window
            1,
            # rule_starts
            '2020-01-15T00:00:00+03:00',
            # rule_ends
            '2020-01-22T00:00:00+03:00',
            # schedule
            SCHEDULE_WED,
            # expected_params
            {'every_day': ''},
            id='1 day window, schedule for 1 days',
        ),
        pytest.param(
            # window
            5,
            # rule_starts
            '2020-01-15T00:00:00+03:00',
            # rule_ends
            '2020-01-20T00:00:00+03:00',
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_params
            {'every_day': ''},
            id='5 day window',
        ),
    ],
)
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_param_every_day(
        stq_runner,
        default_param_test_setup,
        pgsql,
        load_json,
        clients,
        window,
        schedule,
        rule_starts,
        rule_ends,
        expected_params,
):
    task_kwargs = load_json('default_test_task_params.json')
    task_kwargs['schedule_for_goal']['start'] = rule_starts
    task_kwargs['schedule_for_goal']['window'] = window
    task_kwargs['schedule_for_goal']['schedule'] = schedule

    _set_goal_rule_stats(
        pgsql,
        schedule_ref_udid='schref_udid',
        rule_ends_at=rule_ends,
        last_window_notified=None,
    )

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id', args=[], kwargs=task_kwargs,
    )

    _check_params_subset(clients, expected_params)


@pytest.mark.parametrize(
    'rule_starts,rule_ends,window,schedule,expected_params',
    [
        pytest.param(
            # rule_starts
            '2020-01-15T00:00:00+03:00',  # wed
            # rule_ends
            '2020-01-23T00:00:00+03:00',
            # window
            4,
            # schedule
            [
                {'counter': 'A', 'start': '09:00', 'week_day': 'wed'},
                {'counter': '0', 'start': '17:00', 'week_day': 'thu'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'sat'},
                {'counter': '0', 'start': '17:00', 'week_day': 'sat'},
            ],
            # expected_params
            {
                'weekdays': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'compound_2',
                            'params': {
                                '_1': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'subvention_communications.goals.weekdays.range',  # noqa: E501
                                    'params': {
                                        'from': {
                                            'keyset': 'taximeter_messages',
                                            'key': 'from_weekday_3',
                                        },
                                        'to': {
                                            'keyset': 'taximeter_messages',
                                            'key': 'to_weekday_4',
                                        },
                                    },
                                },
                                '_2': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'on_weekday_6',
                                },
                            },
                        },
                    },
                },
            },
            id='from wednesday to thursday and saturday',
        ),
        pytest.param(
            # rule_starts
            '2020-01-15T00:00:00+03:00',  # wed
            # rule_ends
            '2020-01-24T00:00:00+03:00',
            # window
            1,
            # schedule
            [
                {'counter': 'A', 'start': '09:00', 'week_day': 'wed'},
                {'counter': '0', 'start': '17:00', 'week_day': 'wed'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'fri'},
                {'counter': '0', 'start': '17:00', 'week_day': 'fri'},
            ],
            # expected_params
            {
                'weekdays': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'compound_2',
                            'params': {
                                '_1': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'on_weekday_3',
                                },
                                '_2': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'on_weekday_5',
                                },
                            },
                        },
                    },
                },
            },
            id='on wednesday and friday',
        ),
        pytest.param(
            # rule_starts
            '2020-01-15T00:00:00+03:00',
            # rule_ends
            '2020-01-24T00:00:00+03:00',
            # window
            3,
            # schedule
            [
                {'counter': 'A', 'start': '09:00', 'week_day': 'wed'},
                {'counter': '0', 'start': '12:00', 'week_day': 'wed'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'fri'},
                {'counter': '0', 'start': '12:00', 'week_day': 'fri'},
            ],
            # expected_params
            {
                'weekdays': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'compound_2',
                            'params': {
                                '_1': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'on_weekday_3',
                                },
                                '_2': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'on_weekday_5',
                                },
                            },
                        },
                    },
                },
            },
            id='on wednesday and on friday',
        ),
        pytest.param(
            # rule_starts
            '2020-01-15T00:00:00+03:00',
            # rule_ends
            '2020-01-23T00:00:00+03:00',
            # window
            7,
            # schedule
            [
                {'counter': 'A', 'start': '09:00', 'week_day': 'wed'},
                {'counter': '0', 'start': '12:00', 'week_day': 'wed'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'thu'},
                {'counter': '0', 'start': '12:00', 'week_day': 'thu'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'fri'},
                {'counter': '0', 'start': '12:00', 'week_day': 'fri'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'sat'},
                {'counter': '0', 'start': '12:00', 'week_day': 'sat'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'mon'},
                {'counter': '0', 'start': '12:00', 'week_day': 'mon'},
            ],
            # expected_params
            {
                'weekdays': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'compound_2',
                            'params': {
                                '_1': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'subvention_communications.goals.weekdays.range',  # noqa: E501
                                    'params': {
                                        'from': {
                                            'keyset': 'taximeter_messages',
                                            'key': 'from_weekday_3',
                                        },
                                        'to': {
                                            'keyset': 'taximeter_messages',
                                            'key': 'to_weekday_6',
                                        },
                                    },
                                },
                                '_2': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'on_weekday_1',
                                },
                            },
                        },
                    },
                },
            },
            id='from wednesday to saturday and monday',
        ),
        pytest.param(
            # rule_starts
            '2020-01-15T00:00:00+03:00',  # wed
            # rule_ends
            '2020-01-17T00:00:00+03:00',  # fri
            # window
            2,
            # schedule
            [
                {'counter': 'A', 'start': '09:00', 'week_day': 'tue'},
                {'counter': '0', 'start': '12:00', 'week_day': 'tue'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'wed'},
                {'counter': '0', 'start': '12:00', 'week_day': 'wed'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'thu'},
                {'counter': '0', 'start': '12:00', 'week_day': 'thu'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'fri'},
                {'counter': '0', 'start': '12:00', 'week_day': 'fri'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'sat'},
                {'counter': '0', 'start': '12:00', 'week_day': 'sat'},
            ],
            # expected_params
            {'weekdays': ''},
            id='schedule is bigger than workrange',
        ),
        pytest.param(
            # rule_starts
            '2020-01-15T00:00:00+03:00',  # wed
            # rule_ends
            '2020-01-18T00:00:00+03:00',  # fri
            # window
            3,
            # schedule
            [
                {'counter': 'A', 'start': '00:00', 'week_day': 'wed'},
                {'counter': '0', 'start': '18:00', 'week_day': 'wed'},
                {'counter': 'A', 'start': '00:00', 'week_day': 'thu'},
                {'counter': '0', 'start': '18:00', 'week_day': 'thu'},
                {'counter': 'A', 'start': '00:00', 'week_day': 'fri'},
                {'counter': '0', 'start': '18:00', 'week_day': 'fri'},
            ],
            # expected_params
            {'weekdays': ''},
            id='all days, 3day window',
        ),
        pytest.param(
            # rule_starts
            '2020-01-15T00:00:00+03:00',  # wed
            # rule_ends
            '2020-01-18T00:00:00+03:00',  # fri
            # window
            1,
            # schedule
            [
                {'counter': 'A', 'start': '00:00', 'week_day': 'wed'},
                {'counter': '0', 'start': '18:00', 'week_day': 'wed'},
                {'counter': 'A', 'start': '00:00', 'week_day': 'thu'},
                {'counter': '0', 'start': '18:00', 'week_day': 'thu'},
                {'counter': 'A', 'start': '00:00', 'week_day': 'fri'},
                {'counter': '0', 'start': '18:00', 'week_day': 'fri'},
            ],
            # expected_params
            {'weekdays': ''},
            id='all days, 1day window',
        ),
        pytest.param(
            # rule_starts
            '2020-01-15T00:00:00+03:00',  # wed
            # rule_ends
            '2020-01-22T00:00:00+03:00',  # fri
            # window
            7,
            # schedule
            [{'counter': 'A', 'start': '00:00', 'week_day': 'mon'}],
            # expected_params
            {'weekdays': ''},
            id='whole week',
        ),
        pytest.param(
            # rule_starts
            '2020-01-15T00:00:00+03:00',  # wed
            # rule_ends
            '2020-01-24T00:00:00+03:00',  # fri
            # window
            9,
            # schedule
            [
                {'counter': 'A', 'start': '09:00', 'week_day': 'mon'},
                {'counter': '0', 'start': '14:00', 'week_day': 'mon'},
                {'counter': 'A', 'start': '00:00', 'week_day': 'wed'},
                {'counter': '0', 'start': '00:00', 'week_day': 'fri'},
                {'counter': 'A', 'start': '09:00', 'week_day': 'sat'},
                {'counter': '0', 'start': '11:00', 'week_day': 'sat'},
            ],
            # expected_params
            {
                'weekdays': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'compound_3',
                            'params': {
                                '_1': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'on_weekday_1',
                                },
                                '_2': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'subvention_communications.goals.weekdays.range',  # noqa: E501
                                    'params': {
                                        'from': {
                                            'keyset': 'taximeter_messages',
                                            'key': 'from_weekday_3',
                                        },
                                        'to': {
                                            'keyset': 'taximeter_messages',
                                            'key': 'to_weekday_4',
                                        },
                                    },
                                },
                                '_3': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'on_weekday_6',
                                },
                            },
                        },
                    },
                },
            },
            id='window > week',
        ),
    ],
)
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_param_weekdays(
        stq_runner,
        default_param_test_setup,
        load_json,
        clients,
        pgsql,
        rule_starts,
        rule_ends,
        window,
        schedule,
        expected_params,
):
    task_kwargs = load_json('default_test_task_params.json')
    task_kwargs['schedule_for_goal']['start'] = rule_starts
    task_kwargs['schedule_for_goal']['window'] = window
    task_kwargs['schedule_for_goal']['schedule']['schedule'] = schedule

    _set_goal_rule_stats(
        pgsql,
        schedule_ref_udid='schref_udid',
        rule_ends_at=rule_ends,
        last_window_notified=None,
    )

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id', args=[], kwargs=task_kwargs,
    )

    _check_params_subset(clients, expected_params)


@pytest.mark.parametrize(
    'now,last_window_notified,start,end,window,schedule,expected_params',
    [
        pytest.param(
            # now
            '2020-01-14T12:09:00+03:00',
            # last_window_notified
            None,
            # start
            '2020-01-15T00:00:00+03:00',
            # end
            '2020-01-29T00:00:00+03:00',
            # window
            7,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_params
            {
                'active_range': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': (
                                'subvention_communications.goals.active_range'
                            ),
                            'params': {
                                'from_day': '15',
                                'from_month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                                'to_day': '21',
                                'to_month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                            },
                        },
                    },
                },
            },
            id='15 jan - 21 jan',
        ),
        pytest.param(
            # now
            '2020-01-21T20:01:00+03:00',
            # last_window_notified
            0,
            # start
            '2020-01-15T00:00:00+03:00',
            # end
            '2020-01-29T00:00:00+03:00',
            # window
            7,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_params
            {
                'active_range': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': (
                                'subvention_communications.goals.active_range'
                            ),
                            'params': {
                                'from_day': '22',
                                'from_month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                                'to_day': '28',
                                'to_month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                            },
                        },
                    },
                },
            },
            id='22 jan - 28 jan',
        ),
        pytest.param(
            # now
            '2020-01-22T05:01:00+03:00',
            # last_window_notified
            0,
            # start
            '2020-01-15T00:00:00+03:00',
            # end
            '2020-01-29T00:00:00+03:00',
            # window
            7,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_params
            {
                'active_range': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': (
                                'subvention_communications.goals.active_till'
                            ),
                            'params': {
                                'to_day': '28',
                                'to_month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                            },
                        },
                    },
                },
            },
            id='till 29 jan',
        ),
        pytest.param(
            # now
            '2020-01-14T12:09:00+03:00',
            # last_window_notified
            None,
            # start
            '2020-01-15T00:00:00+03:00',
            # end
            '2020-01-29T00:00:00+03:00',
            # window,
            1,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_params
            {
                'active_range': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': (
                                'subvention_communications.goals.active_range'
                            ),
                            'params': {
                                'from_day': '15',
                                'from_month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                                'to_day': '21',
                                'to_month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                            },
                        },
                    },
                },
            },
            id='7 windows at once',
        ),
        pytest.param(
            # now
            '2020-01-14T12:09:00+03:00',
            # last_window_notified
            None,
            # start
            '2020-01-15T00:00:00+03:00',
            # end
            '2020-01-16T00:00:00+03:00',
            # window,
            1,
            # schedule
            SCHEDULE_FOR_ALL_DAYS,
            # expected_params
            {
                'active_range': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'subvention_communications.goals.active_on',
                            'params': {
                                'day': '15',
                                'month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                            },
                        },
                    },
                },
            },
            id='one day',
        ),
        pytest.param(
            # now
            '2020-01-14T12:09:00+03:00',
            # last_window_notified
            None,
            # start
            '2020-01-15T00:00:00+03:00',
            # end
            '2020-01-22T00:00:00+03:00',
            # window,
            7,
            # schedule
            SCHEDULE_WED_THU_FRI,
            # expected_params
            {
                'active_range': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': (
                                'subvention_communications.goals.active_range'
                            ),
                            'params': {
                                'from_day': '15',
                                'from_month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                                'to_day': '17',
                                'to_month': {
                                    'keyset': 'notify',
                                    'key': 'helpers.month_1_part',
                                },
                            },
                        },
                    },
                },
            },
            id='3 days',
        ),
    ],
)
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_param_active_range(
        stq_runner,
        default_param_test_setup,
        mocked_time,
        pgsql,
        load_json,
        clients,
        now,
        last_window_notified,
        start,
        end,
        window,
        schedule,
        expected_params,
):
    task_kwargs = load_json('default_test_task_params.json')
    task_kwargs['schedule_for_goal']['start'] = start
    task_kwargs['schedule_for_goal']['window'] = window
    task_kwargs['schedule_for_goal']['schedule'] = schedule

    _set_goal_rule_stats(
        pgsql,
        schedule_ref_udid='schref_A_udid',
        rule_ends_at=end,
        last_window_notified=last_window_notified,
    )

    mocked_time.set(_parse_time(now))

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id', args=[], kwargs=task_kwargs,
    )

    _check_params_subset(clients, expected_params)


@pytest.mark.parametrize(
    'zones,expected_params',
    [
        pytest.param(
            # zones
            ['br_root/br_russia/br_moscow_adm/br_moscow'],
            # expected_params
            {
                'beginning': {
                    'keyset': 'taximeter_messages',
                    'key': (
                        'subvention_communications.goals.beginning_with_zones'
                    ),
                    'params': {
                        'zones': {'keyset': 'geoareas', 'key': 'moscow'},
                    },
                },
            },
            id='moscow',
        ),
        pytest.param(
            # zones
            [
                'br_root/br_russia/br_spb',
                'br_root/br_russia/br_moscow_adm/br_moscow',
            ],
            # expected_params
            {
                'beginning': {
                    'keyset': 'taximeter_messages',
                    'key': (
                        'subvention_communications.goals.beginning_with_zones'
                    ),
                    'params': {
                        'zones': {
                            'keyset': 'taximeter_messages',
                            'key': 'enumeration_2',
                            'params': {
                                '_1': {'keyset': 'geoareas', 'key': 'moscow'},
                                '_2': {'keyset': 'geoareas', 'key': 'spb'},
                            },
                        },
                    },
                },
            },
            id='moscow,svo,vko',
        ),
        pytest.param(
            # zones
            [
                'br_root/br_russia/br_moscow_adm',
                'br_root/br_russia/br_moscow_adm/br_moscow',
            ],
            # expected_params
            {
                'beginning': {
                    'keyset': 'taximeter_messages',
                    'key': 'subvention_communications.goals.beginning_simple',
                },
            },
            id='moscow,moscow,svo,vko',
        ),
    ],
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'root',
            'parent_name': 'br_root',
            'region_id': '225',
        },
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['moscow', 'vko', 'svo'],
            'region_id': '213',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'root',
            'parent_name': 'br_moscow_adm',
            'tariff_zones': ['moscow'],
        },
        {
            'name': 'br_spb',
            'name_en': 'St. Petersburg',
            'name_ru': 'Cанкт-Петербург',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['spb'],
            'region_id': '2',
        },
    ],
)
@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_PERSONAL_GOALS={
        'enabled': True,
        'notify_before_h': 12,
        'max_zones_in_list': 2,
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_param_beginning(
        stq_runner,
        default_param_test_setup,
        pgsql,
        load_json,
        clients,
        zones,
        expected_params,
):
    task_kwargs = load_json('default_test_task_params.json')
    task_kwargs['schedule_for_goal']['zones'] = zones

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id', args=[], kwargs=task_kwargs,
    )

    _check_params_subset(clients, expected_params)


@pytest.mark.parametrize(
    'tariff_classes,expected_params',
    [
        pytest.param(
            # tariff_classes
            ['econom'],
            # expected_params
            {
                'tariffs': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'subvention_communications.goals.in_tariff',
                            'params': {
                                'tariffs': {
                                    'keyset': 'tariff',
                                    'key': 'old_category_name.econom',
                                },
                            },
                        },
                    },
                },
            },
            id='econom',
        ),
        pytest.param(
            # tariff_classes
            ['econom', 'comfort'],
            # expected_params
            {
                'tariffs': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': (
                                'subvention_communications.goals.in_tariffs'
                            ),
                            'params': {
                                'tariffs': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'enumeration_2',
                                    'params': {
                                        '_1': {
                                            'keyset': 'tariff',
                                            'key': 'old_category_name.econom',
                                        },
                                        '_2': {
                                            'keyset': 'tariff',
                                            'key': 'old_category_name.comfort',
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            id='econom,comfort',
        ),
        pytest.param(
            # tariff_classes
            ['econom', 'comfort', 'business'],
            # expected_params
            {'tariffs': ''},
            id='3 classes',
        ),
        pytest.param(
            # tariff_classes
            ['comfort', 'econom', 'uberx', 'mkk_antifraud'],
            # expected_params
            {
                'tariffs': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': (
                                'subvention_communications.goals.in_tariffs'
                            ),
                            'params': {
                                'tariffs': {
                                    'keyset': 'taximeter_messages',
                                    'key': 'enumeration_2',
                                    'params': {
                                        '_1': {
                                            'keyset': 'tariff',
                                            'key': 'old_category_name.econom',
                                        },
                                        '_2': {
                                            'keyset': 'tariff',
                                            'key': 'old_category_name.comfort',
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            id='mapped classes',
        ),
    ],
)
@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_PERSONAL_GOALS={
        'enabled': True,
        'notify_before_h': 12,
        'max_classes_in_list': 2,
    },
    TARIFF_CLASSES_MAPPING={
        'mkk_antifraud': {'classes': ['econom']},
        'uberx': {'classes': ['econom']},
    },
    TARIFF_CLASSES_ORDER={
        '__default__': {'order': 10000},
        'comfort': {'order': 5},
        'econom': {'order': 3},
    },
)
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_param_tariffs(
        stq_runner,
        default_param_test_setup,
        pgsql,
        load_json,
        clients,
        tariff_classes,
        expected_params,
):
    task_kwargs = load_json('default_test_task_params.json')
    task_kwargs['schedule_for_goal']['tariff_classes'] = tariff_classes

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id', args=[], kwargs=task_kwargs,
    )

    _check_params_subset(clients, expected_params)


@pytest.mark.parametrize(
    'branding_type,expected_params',
    [
        pytest.param(
            # branding_type
            'sticker_and_lightbox',
            # expected_params
            {
                'branding': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'subvention_communications.goals.restrictions.branding.sticker_and_lightbox',  # noqa: E501
                        },
                    },
                },
            },
            id='sticker_and_lightbox',
        ),
        pytest.param(
            # branding_type
            'without_sticker',
            # expected_params
            {
                'branding': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'subvention_communications.goals.restrictions.branding.without_sticker',  # noqa: E501
                        },
                    },
                },
            },
            id='without_sticker',
        ),
        pytest.param(
            # branding_type
            'sticker',
            # expected_params
            {
                'branding': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'subvention_communications.goals.restrictions.branding.sticker',  # noqa: E501
                        },
                    },
                },
            },
            id='sticker',
        ),
        pytest.param(
            # branding_type
            'no_full_branding',
            # expected_params
            {
                'branding': {
                    'keyset': 'taximeter_messages',
                    'key': 'space_before',
                    'params': {
                        'text': {
                            'keyset': 'taximeter_messages',
                            'key': 'subvention_communications.goals.restrictions.branding.no_full_branding',  # noqa: E501
                        },
                    },
                },
            },
            id='no_full_branding',
        ),
    ],
)
@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_PERSONAL_GOALS={
        'enabled': True,
        'notify_before_h': 12,
    },
)
@pytest.mark.geo_nodes(filename='geo_nodes.json')
async def test_param_branding(
        stq_runner,
        default_param_test_setup,
        pgsql,
        load_json,
        clients,
        branding_type,
        expected_params,
):
    task_kwargs = load_json('default_test_task_params.json')
    task_kwargs['schedule_for_goal']['branding_type'] = branding_type

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id', args=[], kwargs=task_kwargs,
    )

    _check_params_subset(clients, expected_params)


@pytest.mark.parametrize(
    'tariff_classes,zones,expected_params',
    [
        pytest.param(
            # tariff_classes
            ['econom'],
            # zones
            ['br_root/moscow'],
            # expected_params
            {
                'additional_info': {
                    'keyset': 'taximeter_messages',
                    'key': 'subvention_communications.goals.additional_info',
                },
            },
            id='1 class, 1 zone',
        ),
        pytest.param(
            # tariff_classes
            ['econom', 'comfort', 'business'],
            # zones
            ['br_root/moscow', 'br_root/spb'],
            # expected_params
            {
                'additional_info': {
                    'keyset': 'taximeter_messages',
                    'key': 'subvention_communications.goals.additional_info.tariffs',  # noqa: E501
                },
            },
            id='3 classes, 2 zones',
        ),
        pytest.param(
            # tariff_classes
            ['econom', 'comfort'],
            # zones
            ['br_root/moscow', 'br_root/spb', 'br_root/vko'],
            # expected_params
            {
                'additional_info': {
                    'keyset': 'taximeter_messages',
                    'key': 'subvention_communications.goals.additional_info.zones',  # noqa: E501
                },
            },
            id='2 classes, 3 zones',
        ),
        pytest.param(
            # tariff_classes
            ['econom', 'comfort', 'business'],
            # zones
            ['br_root/moscow', 'br_root/spb', 'br_root/vko'],
            # expected_params
            {
                'additional_info': {
                    'keyset': 'taximeter_messages',
                    'key': 'subvention_communications.goals.additional_info.zones_tariffs',  # noqa: E501
                },
            },
            id='3 classes, 3 zones',
        ),
    ],
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'root',
            'parent_name': 'br_root',
            'tariff_zones': ['moscow'],
        },
        {
            'name': 'spb',
            'name_en': 'St. Petersburg',
            'name_ru': 'Cанкт-Петербург',
            'node_type': 'root',
            'parent_name': 'br_root',
            'tariff_zones': ['spb'],
        },
        {
            'name': 'vko',
            'name_en': 'Vnukovo',
            'name_ru': 'Внуково',
            'node_type': 'root',
            'parent_name': 'br_root',
            'tariff_zones': ['vko'],
        },
    ],
)
@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_PERSONAL_GOALS={
        'enabled': True,
        'notify_before_h': 12,
        'max_classes_in_list': 2,
        'max_zones_in_list': 2,
    },
    TARIFF_CLASSES_MAPPING={
        'mkk_antifraud': {'classes': ['econom']},
        'uberx': {'classes': ['econom']},
    },
    TARIFF_CLASSES_ORDER={
        '__default__': {'order': 10000},
        'comfort': {'order': 5},
        'econom': {'order': 3},
    },
)
async def test_param_additional_info(
        stq_runner,
        default_param_test_setup,
        pgsql,
        load_json,
        clients,
        tariff_classes,
        zones,
        expected_params,
):
    task_kwargs = load_json('default_test_task_params.json')
    task_kwargs['schedule_for_goal']['tariff_classes'] = tariff_classes
    task_kwargs['schedule_for_goal']['zones'] = zones

    await stq_runner.subvention_communications_personal_goals.call(
        task_id='mock_task_id', args=[], kwargs=task_kwargs,
    )

    _check_params_subset(clients, expected_params)
