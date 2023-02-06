import copy
import datetime
import typing as tp

import pytest
import pytz

from workforce_management.common.jobs.setup import (
    actual_shifts as actual_shifts_job,
)
from workforce_management.storage.postgresql import (
    actual_shifts as actual_shifts_db,
)

START = datetime.datetime(2021, 1, 1, tzinfo=pytz.UTC)
COMMON_EXPECTED_SHIFT_DATA: tp.Dict[str, tp.Any] = {
    'duration_minutes': 60.0,
    'source': 'taxi_callcenter',
    'start': START,
    'yandex_uid': 'uid1',
}


def override_common_shift_data(**kwargs):
    data_copy = COMMON_EXPECTED_SHIFT_DATA.copy()
    for key, value in kwargs.items():
        data_copy[key] = value

    return data_copy


def add_minutes(minutes):
    return START + datetime.timedelta(minutes=minutes)


BASE_CASES = [
    pytest.param(
        [
            {
                'yandex_uid': 'uid1',
                'events': [
                    (0, START, 'connected', None, ['order']),
                    (1, add_minutes(60), 'disconnected', None, ['order']),
                ],
            },
        ],
        {'min_flap_interval_sec': 15},
        [{**COMMON_EXPECTED_SHIFT_DATA, 'events': []}],
        id='0',
    ),
    pytest.param(
        [
            {
                'yandex_uid': 'uid1',
                'events': [
                    (0, START, 'connected', None, ['order']),
                    (1, add_minutes(25), 'paused', None, ['order']),
                    (2, add_minutes(30), 'connected', None, ['order']),
                    (3, add_minutes(45), 'disconnected', None, ['order']),
                ],
            },
        ],
        {'min_flap_interval_sec': 15},
        [
            {
                **override_common_shift_data(duration_minutes=45),
                'events': [
                    {
                        'start': datetime.datetime(
                            2021, 1, 1, 0, 25, tzinfo=pytz.UTC,
                        ),
                        'type': 'pause',
                        'sub_type': None,
                        'duration_minutes': 5.0,
                    },
                ],
            },
        ],
        id='1',
    ),
    pytest.param(
        [
            {
                'yandex_uid': 'uid1',
                'events': [
                    (0, START, 'connected', None, ['order']),
                    (1, add_minutes(25), 'disconnected', None, ['order']),
                    (2, add_minutes(30), 'connected', None, ['order']),
                    (3, add_minutes(45), 'disconnected', None, ['order']),
                ],
            },
        ],
        {'min_flap_interval_sec': 900},
        [{**override_common_shift_data(duration_minutes=45), 'events': []}],
        id='2',
    ),
    pytest.param(
        [
            {
                'yandex_uid': 'uid1',
                'events': [
                    (0, START, 'connected', None, ['order']),
                    (1, add_minutes(1), 'connected', None, ['order']),
                    (2, add_minutes(2), 'connected', None, ['order']),
                    (3, add_minutes(25), 'disconnected', None, ['order']),
                    (4, add_minutes(30), 'connected', None, ['order']),
                    (5, add_minutes(60), 'disconnected', None, ['order']),
                ],
            },
        ],
        {'min_flap_interval_sec': 900},
        [{**COMMON_EXPECTED_SHIFT_DATA, 'events': []}],
        id='3',
    ),
    pytest.param(
        [
            {
                'yandex_uid': 'uid1',
                'events': [
                    (0, START, 'connected', None, ['order']),
                    (1, add_minutes(25), 'paused', 'dinner', ['order']),
                    (2, add_minutes(60), 'disconnected', None, ['order']),
                ],
            },
        ],
        {'min_flap_interval_sec': 15},
        [
            {
                **COMMON_EXPECTED_SHIFT_DATA,
                'events': [
                    {
                        'start': datetime.datetime(
                            2021, 1, 1, 0, 25, tzinfo=pytz.UTC,
                        ),
                        'type': 'pause',
                        'sub_type': 'dinner',
                        'duration_minutes': 35.0,
                    },
                ],
            },
        ],
        id='4',
    ),
    pytest.param(
        [
            {
                'yandex_uid': 'missing_uid',
                'events': [
                    (0, START, 'connected', None, ['order']),
                    (1, add_minutes(25), 'paused', 'dinner', ['order']),
                    (2, add_minutes(60), 'disconnected', None, ['order']),
                ],
            },
        ],
        {'min_flap_interval_sec': 15},
        [
            {
                **COMMON_EXPECTED_SHIFT_DATA,
                'yandex_uid': 'missing_uid',
                'events': [
                    {
                        'start': datetime.datetime(
                            2021, 1, 1, 0, 25, tzinfo=pytz.UTC,
                        ),
                        'type': 'pause',
                        'sub_type': 'dinner',
                        'duration_minutes': 35.0,
                    },
                ],
            },
        ],
        id='5_missing_uid',
    ),
    pytest.param(
        [
            {
                'yandex_uid': 'uid1',
                'events': [
                    (0, START, 'connected', None, ['non_existing']),
                    (
                        2,
                        add_minutes(60),
                        'disconnected',
                        None,
                        ['non_existing'],
                    ),
                ],
            },
        ],
        {'min_flap_interval_sec': 15},
        [],
        id='6_non_existing_queue',
    ),
]


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={'phone_queues': ['order']},
)
@pytest.mark.parametrize('events, conf, expected_res', BASE_CASES)
async def test_base(stq3_context, events, conf, expected_res):
    async def cs_events():
        for event in events:
            yield event

    expected_res = copy.deepcopy(expected_res)
    for shift in expected_res:
        #  serialize events
        shift['events'] = actual_shifts_job.dump_events(shift['events'])
    job = actual_shifts_job.ActualShiftsSetupJob(stq3_context)
    triggered_events = {}
    for full_event in events:
        triggered_events[full_event['yandex_uid']] = {
            'id': full_event['events'][-1][0],
        }
    res, _ = await job.filter_out_flaps(cs_events(), triggered_events, conf)
    assert res == expected_res


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={'order': 'order'},
)
@pytest.mark.parametrize('events, conf, expected_res', BASE_CASES)
async def test_base_old_config(stq3_context, events, conf, expected_res):
    await test_base(stq3_context, events, conf, expected_res)


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'phone_queues': ['pokemon'],
    },
)
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_actual_events.sql',
        'simple_shifts.sql',
    ],
)
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        (
            {
                'job_type': 'actual_shifts_creator',
                'yandex_uids': ['uid1', 'uid2'],
                'triggered_events': {'uid1': {'id': 2}, 'uid2': {'id': 6}},
            },
            [
                {
                    'id': 1,
                    'duration_minutes': 120.0,
                    'events': '[]',
                    'start': datetime.datetime(
                        2020, 7, 26, 12, 0, tzinfo=datetime.timezone.utc,
                    ),
                    'yandex_uid': 'uid1',
                    'shift_id': 1,
                },
                {
                    'id': 2,
                    'duration_minutes': 180.0,
                    'events': (
                        '[{"type": "pause", '
                        '"start": "2020-07-26T13:00:00+00:00", '
                        '"sub_type": "dinner", "duration_minutes": 30.0}]'
                    ),
                    'start': datetime.datetime(
                        2020, 7, 26, 12, 0, tzinfo=datetime.timezone.utc,
                    ),
                    'yandex_uid': 'uid2',
                    'shift_id': None,
                },
            ],
        ),
    ],
)
async def test_shift_creator(stq_runner, stq3_context, kwargs, expected_res):
    await stq_runner.workforce_management_setup_jobs.call(
        task_id='actual_shifts_creator_0.1', args=(), kwargs=kwargs,
    )
    db = actual_shifts_db.ActualShiftsRepo(stq3_context)
    async with db.master.acquire() as conn, conn.transaction():
        shifts = await db.get_operators_actual_shifts(
            conn,
            kwargs['yandex_uids'],
            datetime_from=datetime.datetime(
                2020, 7, 26, 12, 0, tzinfo=datetime.timezone.utc,
            ),
            datetime_to=datetime.datetime(
                2020, 7, 27, 12, 0, tzinfo=datetime.timezone.utc,
            ),
        )
    shifts = [dict(shift) for shift in shifts]
    assert shifts == expected_res
