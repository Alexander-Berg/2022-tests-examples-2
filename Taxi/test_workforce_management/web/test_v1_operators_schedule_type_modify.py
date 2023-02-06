import datetime
import typing as tp

import pytest

from test_workforce_management.web import data as test_data
from workforce_management.common import utils
from workforce_management.storage.postgresql import db


URI = 'v1/operators/schedule/type/modify'
TST_UID = 'uid1'
TST_UID2 = 'uid3'
STARTS_AT = '2020-08-01 00:00:00.0Z'
SECOND_STARTS_AT = '2020-07-01 00:00:00.0Z'
STARTS_AT_UID3 = '2020-08-01 00:00:00.0Z'
PARSED_STARTS_AT = datetime.datetime(
    2020, 8, 1, 0, 0, tzinfo=datetime.timezone.utc,
)
START_TIME = datetime.datetime(2018, 8, 1, 0, 0, tzinfo=datetime.timezone.utc)
REVISION_ID = '2020-06-25T21:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-27T00:00:00.000000 +0000'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}
SCHEDULE_AUDIT_SETTINGS: tp.Dict[str, tp.Any] = {
    'startrack_queue': 'queue',
    'last_date_to_change_schedule': 20,
}


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'allowed_periods.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        (
            {
                'yandex_uid': 'uid1',
                'schedule_type_id': 2,
                'starts_at_with_tz': '2010-09-22 12:00:00.0 +0000',
                'expires_at_with_tz': '2010-10-20 12:00:00.0 +0000',
                'skills': ['pokemon'],
            },
            400,
        ),
        (
            {
                'yandex_uid': 'uid1',
                'schedule_type_id': 2,
                'starts_at_with_tz': '2010-09-22 12:00:00.0 +0000',
                'expires_at_with_tz': '2010-10-23 12:00:00.0 +0000',
                'skills': ['pokemon'],
            },
            200,
        ),
        (
            {
                'yandex_uid': 'uid1',
                'schedule_type_id': 2,
                'starts_at_with_tz': '2010-09-22 12:00:00.0 +0000',
                'expires_at_with_tz': '2010-10-23 12:00:00.0 +0000',
                'skills': ['pokemon'],
            },
            200,
        ),
    ],
)
async def test_schedule_intersecting_period(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'extra_schedule_types.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        pytest.param(
            {'yandex_uid': TST_UID, 'schedule_type_id': 2}, 400, {}, id='1',
        ),  # starts_at have to be provided
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': '1900-08-01 00:00:00.0Z',
            },
            400,
            {},
            id='2',
        ),  # intersection
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': STARTS_AT,
                'skills': ['unexists'],
            },
            400,
            {'starts_at': PARSED_STARTS_AT},
            id='3',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': STARTS_AT,
                'skills': ['pokemon'],
            },
            200,
            {'starts_at': PARSED_STARTS_AT},
            id='4',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': STARTS_AT,
                'skills': ['pokemon'],
            },
            200,
            {'starts_at': PARSED_STARTS_AT},
            id='5',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 1,
                'starts_at_with_tz': STARTS_AT,
            },
            200,
            {'starts_at': PARSED_STARTS_AT},
            id='6',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 1,
                'starts_at_with_tz': SECOND_STARTS_AT,
            },
            400,
            None,
            id='7',
        ),
        pytest.param(
            {
                'record_id': 1,
                'yandex_uid': TST_UID,
                'schedule_type_id': 1,
                'starts_at_with_tz': SECOND_STARTS_AT,
                'revision_id': REVISION_ID,
                'skills': [],
            },
            200,
            {},
            id='8',
        ),
        pytest.param(
            {
                'record_id': 1,
                'yandex_uid': TST_UID,
                'schedule_type_id': 10,
                'starts_at_with_tz': SECOND_STARTS_AT,
                'revision_id': REVISION_ID,
                'skills': [],
            },
            400,
            {},
            id='9',
        ),
        pytest.param(
            {
                'record_id': 1,
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': SECOND_STARTS_AT,
                'revision_id': REVISION_ID,
                'skills': ['hokage', 'pokemon'],
                'schedule_offset': 2,
            },
            200,
            {
                'schedule_type_info': {'schedule_type_id': 2},
                'schedule_offset': 2,
            },
            id='10',
        ),
        pytest.param(
            {
                'record_id': 1,
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': SECOND_STARTS_AT,
                'revision_id': REVISION_ID,
                'operator_revision_id': REVISION_ID,  # wrong revision
                'skills': ['hokage', 'pokemon'],
            },
            409,
            None,
            id='11',
        ),
        pytest.param(
            {
                'record_id': 1,
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': SECOND_STARTS_AT,
                'operator_revision_id': test_data.FIRST_OPERATOR_REVISION,
                'skills': ['hokage', 'pokemon'],
            },
            200,
            {'schedule_type_info': {'schedule_type_id': 2}},
            id='12',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': '2021-07-01 00:00:00.0+00',
                'operator_revision_id': test_data.FIRST_OPERATOR_REVISION,
                'skills': ['hokage', 'pokemon'],
            },
            200,
            {'schedule_type_info': {'schedule_type_id': 2}},
            id='13',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 800,
                'starts_at_with_tz': SECOND_STARTS_AT,
                'revision_id': '2020-06-26T00:00:00.000000 +0000',
            },
            400,
            None,
            id='14',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': '2020-07-15 00:00:00.0',
                'revision_id': REVISION_ID,
            },  # schedule intersects with existing
            400,
            None,
            id='15',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': '2020-08-15 00:00:00.0',
                'expires_at_with_tz': '2020-08-13 00:00:00.0',
                'revision_id': REVISION_ID,
            },  # expires < starts
            400,
            None,
            id='16',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': '2020-08-15 00:00:00.0',
                'expires_at_with_tz': '2020-08-13 00:00:00.0',
                'revision_id': '2020-08-13 00:00:00.0',
            },  # wrong revision format
            400,
            None,
            id='17',
        ),
        pytest.param(
            {
                'record_id': 1,
                'yandex_uid': TST_UID,
                'schedule_type_id': 1,
                'starts_at_with_tz': SECOND_STARTS_AT,
                'operator_revision_id': WRONG_REVISION_ID,
            },
            409,
            None,
            id='18',
        ),
        pytest.param(
            # deleted one
            {
                'yandex_uid': 'uid5',
                'schedule_type_id': 1,
                'starts_at_with_tz': SECOND_STARTS_AT,
                'revision_id': WRONG_REVISION_ID,
            },
            400,
            None,
            id='19',
        ),
    ],
)
async def test_schedule_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return
    data = await res.json()

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    yandex_uid = tst_request['yandex_uid']
    record_id = data['record_id']

    async with master_pool.acquire() as conn:
        res = await operators_db.get_operator_data(conn, [yandex_uid])

        schedule = {}
        for schedule in res[yandex_uid]['schedules']:
            if schedule['record_id'] == record_id:
                break
        assert schedule, 'Schedule not found.'

        expires_at = schedule.get('expires_at')
        assert bool(expires_at) == ('expires_at_with_tz' in tst_request)

        schedule_type_info = schedule.pop('schedule_type_info', {})
        expected_type_info = expected_res.pop('schedule_type_info', {})
        assert utils.expected_fields(
            [schedule, schedule_type_info], [expected_res, expected_type_info],
        ) == [expected_res, expected_type_info]

        if 'skills' in tst_request:
            assert schedule.get('skills', []) == tst_request['skills']


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        (
            {
                'record_id': 1,
                'revision_id': 'no matter what',
                'operator_revision_id': test_data.FIRST_OPERATOR_REVISION,
            },
            200,
        ),
        (
            {
                'record_id': 1,
                'revision_id': 'no matter what',
                'operator_revision_id': WRONG_REVISION_ID,
            },
            409,
        ),
    ],
)
async def test_delete(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.delete(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master

    async with master_pool.acquire() as conn:
        res = await operators_db.get_operator_data(conn, [TST_UID])
        found = False

        if TST_UID not in res:
            return

        for schedule in res[TST_UID]['schedules']:
            if schedule['record_id'] == tst_request['record_id']:
                found = True
                break

        res = await operators_db.get_deleted_operators_schedules(
            conn, ids=[tst_request['record_id']],
        )
        assert res and success or not (res or success)

    assert not found or not success


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts_with_future.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, shifts_left',
    [
        (
            {'record_id': 3, 'revision_id': REVISION_ID},
            400,
            {
                'code': 'shifts_exist',
                'details': {
                    'shifts': {
                        '1': 'Shift 1 from 2024-09-26 15:00:00+00:00',
                        '2': 'Shift 2 from 2020-09-26 15:00:00+00:00',
                        '3': 'Shift 3 from 2023-08-15 15:00:00+00:00',
                        '4': 'Shift 4 from 2023-08-12 15:00:00+00:00',
                        '5': 'Shift 5 from 2023-08-16 15:00:00+00:00',
                    },
                },
                'message': 'Cannot delete schedule with future shifts',
            },
            [1, 2, 3, 4, 5],
        ),
        (
            {
                'record_id': 3,
                'revision_id': REVISION_ID,
                'force_shift_delete': True,
            },
            200,
            {},
            [],
        ),
    ],
)
async def test_delete_schedule_and_shifts(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        shifts_left,
):
    res = await taxi_workforce_management_web.delete(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if res.status > 200:
        data = await res.json()
        assert data == expected_res

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master

    async with master_pool.acquire() as conn:
        res = await operators_db.get_shifts_from_date(
            conn, date=START_TIME, operators_schedule_types_ids=[3],
        )
        assert shifts_left == [record['shift_id'] for record in res]


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts_with_future.sql'],
)
@pytest.mark.now('2020-08-02T11:30:40')
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, shifts_left',
    [
        (
            {
                'yandex_uid': 'uid3',
                'schedule_type_id': 4,
                'record_id': 3,
                'starts_at_with_tz': STARTS_AT_UID3,
                'revision_id': REVISION_ID,
                'skills': ['tatarin', 'pokemon', 'hokage'],
            },
            200,
            {},
            [1, 2, 3, 4, 5],
        ),
        (
            {
                'yandex_uid': 'uid3',
                'schedule_type_id': 4,
                'record_id': 3,
                'starts_at_with_tz': STARTS_AT_UID3,
                'revision_id': REVISION_ID,
                'skills': ['tatarin', 'hokage'],
            },
            400,
            {
                'code': 'shifts_exist',
                'details': {
                    '3': {
                        '1': 'Shift 1 from 2024-09-26 15:00:00+00:00',
                        '2': 'Shift 2 from 2020-09-26 15:00:00+00:00',
                        '3': 'Shift 3 from 2023-08-15 15:00:00+00:00',
                        '4': 'Shift 4 from 2023-08-12 15:00:00+00:00',
                    },
                },
                'message': (
                    'Cannot modify a schedule with existing'
                    ' shifts on a given period or skills.'
                ),
            },
            [1, 2, 3, 4, 5],
        ),
        (
            {
                'yandex_uid': 'uid3',
                'schedule_type_id': 4,
                'record_id': 3,
                'starts_at_with_tz': STARTS_AT_UID3,
                'revision_id': REVISION_ID,
                'skills': ['tatarin', 'hokage'],
                'force_shift_delete': True,
            },
            200,
            {},
            [5],
        ),
    ],
)
async def test_change_or_delete_schedule_skills(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        shifts_left,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if res.status > 200:
        data = await res.json()
        assert data == expected_res

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master

    async with master_pool.acquire() as conn:
        res = await operators_db.get_shifts_from_date(
            conn, date=START_TIME, operators_schedule_types_ids=[3],
        )
        assert shifts_left == [record['shift_id'] for record in res]


@pytest.mark.now('2020-08-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts_with_future.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_res, shifts_left',
    [
        (
            {
                'record_id': 3,
                'yandex_uid': TST_UID2,
                'schedule_type_id': 4,
                'starts_at_with_tz': '2023-08-13 00:00:00.0',
                'expires_at_with_tz': '2023-08-16 00:00:00.0',
                'revision_id': REVISION_ID,
            },
            {
                'code': 'shifts_exist',
                'details': {
                    '3': {
                        '1': 'Shift 1 from 2024-09-26 15:00:00+00:00',
                        '2': 'Shift 2 from 2020-09-26 15:00:00+00:00',
                        '4': 'Shift 4 from 2023-08-12 15:00:00+00:00',
                        '5': 'Shift 5 from 2023-08-16 15:00:00+00:00',
                    },
                },
                'message': (
                    'Cannot modify a schedule with existing '
                    'shifts on a given period or skills.'
                ),
            },
            [1, 2, 3, 4, 5],
        ),
        (
            {
                'record_id': 3,
                'yandex_uid': TST_UID2,
                'schedule_type_id': 3,  # change schedule_type
                'starts_at_with_tz': '2023-08-13 00:00:00.0',
                'expires_at_with_tz': '2023-08-16 00:00:00.0',
                'revision_id': REVISION_ID,
            },
            {
                'code': 'shifts_exist',
                'details': {
                    '3': {
                        '1': 'Shift 1 from 2024-09-26 15:00:00+00:00',
                        '2': 'Shift 2 from 2020-09-26 15:00:00+00:00',
                        '3': 'Shift 3 from 2023-08-15 15:00:00+00:00',
                        '4': 'Shift 4 from 2023-08-12 15:00:00+00:00',
                        '5': 'Shift 5 from 2023-08-16 15:00:00+00:00',
                    },
                },
                'message': (
                    'Cannot modify a schedule with existing '
                    'shifts on a given period or skills.'
                ),
            },
            [1, 2, 3, 4, 5],
        ),
        (
            {
                'record_id': 3,
                'yandex_uid': TST_UID2,
                'schedule_type_id': 4,
                'starts_at_with_tz': '2023-08-13 00:00:00.0',
                'expires_at_with_tz': '2023-08-16 00:00:00.0',
                'revision_id': REVISION_ID,
                'force_shift_delete': True,
            },
            {},
            [3],
        ),
    ],
)
async def test_deleting_shifts_in_modifying(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_res,
        shifts_left,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    data = await res.json()

    if res.status > 200:
        assert data == expected_res

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master

    async with master_pool.acquire() as conn:
        res = await operators_db.get_shifts_from_date(
            conn, date=START_TIME, operators_schedule_types_ids=[3],
        )
        assert shifts_left == [record['shift_id'] for record in res]


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_SCHEDULE_AUDIT_SETTINGS={
        'taxi': SCHEDULE_AUDIT_SETTINGS,
    },
)
@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_stq_calls_count',
    [
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': '2020-09-01 00:00:00.0Z',
                'skills': ['pokemon'],
            },
            200,
            1,
            marks=pytest.mark.now('2020-08-02T11:30:40'),
            id='create_new_in_time',
        ),
        pytest.param(
            {
                'yandex_uid': 'uid10',
                'schedule_type_id': 2,
                'starts_at_with_tz': '2020-09-01 00:00:00.0Z',
                'skills': ['pokemon'],
            },
            200,
            1,
            marks=pytest.mark.now('2020-08-30T11:30:40'),
            id='create_new_in_time_preprofile',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': '2020-09-01 00:00:00.0Z',
                'skills': ['pokemon'],
            },
            400,
            0,
            marks=pytest.mark.now('2020-08-25T11:30:40'),
            id='create_new_too_late',
        ),
        pytest.param(
            {
                'record_id': 1,
                'yandex_uid': TST_UID,
                'schedule_type_id': 2,
                'starts_at_with_tz': '2020-09-01 00:00:00.0Z',
                'operator_revision_id': test_data.FIRST_OPERATOR_REVISION,
                'skills': ['hokage', 'pokemon'],
            },
            200,
            0,
            marks=pytest.mark.now('2020-08-19T11:30:40'),
            id='edit_ok_without_draft',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID2,
                'schedule_type_id': 4,
                'starts_at_with_tz': '2023-08-14 00:00:00.0Z',
                'operator_revision_id': '2020-08-25T21:00:00.000000 +0000',
                'skills': ['pokemon'],
            },
            400,
            0,
            marks=[pytest.mark.now('2023-08-12T11:30:40')],
            id='create_fail_skill_change',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID2,
                'schedule_type_id': 4,
                'starts_at_with_tz': '2023-08-14 00:00:00.0Z',
                'operator_revision_id': '2020-08-25T21:00:00.000000 +0000',
                'skills': ['pokemon'],
            },
            200,
            0,
            marks=[
                pytest.mark.now('2023-08-12T11:30:40'),
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_SCHEDULE_AUDIT_SETTINGS={
                        'taxi': {
                            **SCHEDULE_AUDIT_SETTINGS,
                            'skip_skill_change_draft': True,
                        },
                    },
                ),
            ],
            id='create_ok_skill_change_skip',
        ),
    ],
)
async def test_schedule_draft(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_stq_calls_count,
        stq,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return

    for _ in range(expected_stq_calls_count):
        task = stq.workforce_management_schedule_change_draft.next_call()
        assert task['kwargs']

    assert stq.is_empty


@pytest.mark.pgsql('workforce_management', files=['operator_with_shifts.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_shifts',
    [
        pytest.param(
            {
                'yandex_uid': TST_UID2,
                'schedule_type_id': 1,
                'starts_at_with_tz': '2023-09-01 00:00:00.0Z',
                'operator_revision_id': '2020-08-25T21:00:00.000000 +0000',
                'skills': ['hokage'],
                'outside_shift_policy': 'move_to_new_schedule',
            },
            200,
            [
                datetime.datetime(
                    2023, 8, 1, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(
                    2023, 9, 1, 0, 0, tzinfo=datetime.timezone.utc,
                ),
            ],
            [1, 2, 2],
            id='move_to_new_schedule',
        ),
        pytest.param(
            {
                'yandex_uid': TST_UID2,
                'schedule_type_id': 1,
                'starts_at_with_tz': '2023-09-01 00:00:00.0Z',
                'operator_revision_id': '2020-08-25T21:00:00.000000 +0000',
                'skills': ['sixth_hokage'],
                'outside_shift_policy': 'move_to_new_schedule',
            },
            200,
            [
                datetime.datetime(
                    2023, 8, 1, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(
                    2023, 9, 1, 0, 0, tzinfo=datetime.timezone.utc,
                ),
            ],
            [2, 2],
            id='move_to_new_skill',
        ),
    ],
)
async def test_auto_schedule_closing(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_shifts,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    yandex_uid = tst_request['yandex_uid']
    async with master_pool.acquire() as conn:
        res = await operators_db.get_operator_data(conn, [yandex_uid])
        assert [
            schedule['starts_at'] for schedule in res[yandex_uid]['schedules']
        ] == expected_res

        shifts = await operators_db.get_shifts(
            conn=conn,
            datetime_from=datetime.datetime(2000, 1, 1),
            datetime_to=datetime.datetime(3000, 1, 1),
            limit=100,
            yandex_uids=[yandex_uid],
            skills=tst_request['skills'],
        )
        assert [
            shift['operators_schedule_types_id'] for shift in shifts
        ] == expected_shifts


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, operators, expected_status, expected_res',
    [
        pytest.param(
            {
                'yandex_uid': 'uid3',
                'schedule_type_id': 5,
                'starts_at_with_tz': '2023-09-01 00:00:00.0Z',
                'operator_revision_id': '2020-08-26T00:00:00.000000 +0300',
                'skills': [],
                'outside_shift_policy': 'move_to_new_schedule',
            },
            [
                test_data.THIRD_OPERATOR_EFFRAT,
                {
                    **test_data.THIRD_OPERATOR_EFFRAT,
                    'source': 'lavka',
                    'employee_uid': '00000000-0000-0000-0001-000000000003',
                },
            ],
            200,
            [
                (
                    datetime.datetime(
                        2023, 8, 1, 0, 0, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2023, 9, 1, 0, 0, tzinfo=datetime.timezone.utc,
                    ),
                ),
                (
                    datetime.datetime(
                        2023, 9, 1, 0, 0, tzinfo=datetime.timezone.utc,
                    ),
                    None,
                ),
            ],
            id='domain_change',
        ),
    ],
)
async def test_domain_change(
        mock_effrat_employees,
        taxi_workforce_management_web,
        web_context,
        tst_request,
        operators,
        expected_status,
        expected_res,
):
    mock_effrat_employees(operators_list=operators)
    await taxi_workforce_management_web.invalidate_caches(clean_update=False)

    res = await taxi_workforce_management_web.post(
        URI,
        json=tst_request,
        headers={'X-Yandex-UID': 'uid3', 'X-WFM-Domain': 'lavka'},
    )
    assert res.status == expected_status
    if expected_status > 200:
        return

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    yandex_uid = tst_request['yandex_uid']
    async with master_pool.acquire() as conn:
        res = await operators_db.get_operator_data(conn, [yandex_uid])
        schedules = res[yandex_uid]['schedules']
        data = [
            (schedule['starts_at'], schedule['expires_at'])
            for schedule in schedules
        ]
        assert data == expected_res

    mock_effrat_employees()
    await taxi_workforce_management_web.invalidate_caches(clean_update=True)
