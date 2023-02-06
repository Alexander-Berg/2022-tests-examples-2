import datetime

import pytest

from taxi.util import dates

from test_workforce_management.web import data as test_data
from workforce_management.storage.postgresql import db


URI = 'v1/operators/schedule/type/modify/bulk'
TST_UID = 'uid1'
TST_UID_2 = 'uid3'
STARTS_AT = '2020-08-01 00:00:00.0Z'
SECOND_STARTS_AT = '2020-09-01 00:00:00.0Z'
THIRD_STARTS_AT = '2020-07-01 00:00:00.0Z'
PARSED_STARTS_AT = datetime.datetime(
    2020, 6, 30, 21, 0, tzinfo=datetime.timezone.utc,
)
SHIFTS_STARTS_AT = datetime.datetime(
    2018, 6, 30, 21, 0, tzinfo=datetime.timezone.utc,
)
REVISION_ID = '2020-06-25T21:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-27T00:00:00.000000 +0000'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'allowed_periods.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res_len',
    [
        (
            {'records': [{'yandex_uid': TST_UID, 'schedule_type_id': 2}]},
            400,
            1,
        ),
        (
            {
                'records': [
                    {
                        'yandex_uid': TST_UID,
                        'schedule_type_id': 2,
                        'starts_at_with_tz': STARTS_AT,
                    },
                ],
            },
            200,
            2,
        ),
        (
            {
                'records': [
                    {
                        'record_id': 1,
                        'yandex_uid': TST_UID,
                        'schedule_type_id': 1,
                        'starts_at_with_tz': SECOND_STARTS_AT,
                        'revision_id': REVISION_ID,
                        'operator_revision_id': (
                            test_data.FIRST_OPERATOR_REVISION
                        ),
                    },
                    {
                        'yandex_uid': 'uid5',
                        'schedule_type_id': 1,
                        'starts_at_with_tz': THIRD_STARTS_AT,
                    },
                ],
            },
            400,
            1,
        ),
        pytest.param(
            {
                'records': [
                    {
                        'record_id': 1,
                        'yandex_uid': TST_UID,
                        'schedule_type_id': 1,
                        'starts_at_with_tz': THIRD_STARTS_AT,
                        'revision_id': REVISION_ID,
                        'operator_revision_id': (
                            test_data.FIRST_OPERATOR_REVISION
                        ),
                        'skills': [],
                    },
                    {
                        'yandex_uid': TST_UID_2,
                        'schedule_type_id': 1,
                        'expires_at_with_tz': '2021-09-01 00:00:00.0Z',
                        'starts_at_with_tz': SECOND_STARTS_AT,
                        'skills': ['hokage', 'pokemon'],
                    },
                ],
            },
            200,
            3,
            id='two_schedules',
        ),
        (
            {
                'records': [
                    {
                        'record_id': 1,
                        'yandex_uid': TST_UID,
                        'schedule_type_id': 1,
                        'starts_at_with_tz': SECOND_STARTS_AT,
                        'revision_id': REVISION_ID,
                        'operator_revision_id': REVISION_ID,  # wrong revision
                    },
                    {
                        'yandex_uid': TST_UID_2,
                        'schedule_type_id': 1,
                        'starts_at_with_tz': SECOND_STARTS_AT,
                        'skills': ['hokage', 'pokemon'],
                    },
                ],
            },
            409,
            2,
        ),
        (
            {
                'records': [
                    {
                        'record_id': 1,
                        'yandex_uid': TST_UID,
                        'schedule_type_id': 1,
                        'starts_at_with_tz': SECOND_STARTS_AT,
                        'operator_revision_id': WRONG_REVISION_ID,
                    },
                    {
                        'yandex_uid': TST_UID_2,
                        'schedule_type_id': 1,
                        'starts_at_with_tz': SECOND_STARTS_AT,
                    },
                ],
            },
            409,
            2,
        ),
    ],
)
async def test_schedule_bulk_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        mock_effrat_employees,
        expected_res_len,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master

    async with master_pool.acquire() as conn:
        res = await operators_db.get_operators_schedule_types(
            conn,
            yandex_uids=[
                data['yandex_uid'] for data in tst_request['records']
            ],
        )
        actual_records = {row['id']: row for row in res}
        for record in tst_request['records']:
            record_id = record.pop('record_id', None)
            if record_id:
                assert record_id in actual_records
                actual_record = actual_records[record_id]

                for key in record:
                    if key in [
                            'revision_id',
                            'operator_revision_id',
                            'yandex_uid',
                            'schedule_type_id',
                            'skills',
                    ]:
                        continue
                    key_for_actual_record = key.replace('_with_tz', '')
                    if isinstance(
                            actual_record[key_for_actual_record],
                            datetime.datetime,
                    ):
                        record[key] = dates.localize(
                            dates.parse_timestring(record[key]), 'UTC',
                        )
                    if success:
                        assert (
                            actual_record[key_for_actual_record] == record[key]
                        )
                    else:
                        assert (
                            actual_record[key_for_actual_record] != record[key]
                        )

                if 'skills' in record and record['skills'] is not None:
                    schedule_skills = (
                        await operators_db.get_operators_schedule_skills(
                            conn, [actual_record['id']],
                        )
                    )

                    assert [row['skill'] for row in schedule_skills] == record[
                        'skills'
                    ]
        assert len(res) == expected_res_len


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        (
            {
                'records': [
                    {
                        'record_id': 1,
                        'revision_id': '',
                        'operator_revision_id': (
                            test_data.FIRST_OPERATOR_REVISION
                        ),
                    },
                ],
            },
            200,
        ),
        (
            {
                'records': [
                    {
                        'record_id': 1,
                        'revision_id': '',
                        'operator_revision_id': WRONG_REVISION_ID,
                    },
                    {'record_id': 2, 'operator_revision_id': REVISION_ID},
                ],
            },
            409,
        ),
    ],
)
async def test_bulk_delete(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.delete(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return

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

    assert not found


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts_with_future.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, shifts_left',
    [
        (
            {
                'records': [
                    {'record_id': 3, 'revision_id': REVISION_ID},
                    {'record_id': 1, 'revision_id': REVISION_ID},
                    {'record_id': 2, 'revision_id': REVISION_ID},
                ],
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
                        '5': 'Shift 5 from 2023-08-16 15:00:00+00:00',
                    },
                },
                'message': 'Cannot modify schedule with future shifts',
            },
            [1, 2, 3, 4, 5],
        ),
        (
            {
                'records': [{'record_id': 3, 'revision_id': REVISION_ID}],
                'force_shift_delete': True,
            },
            200,
            {},
            [],
        ),
    ],
)
async def test_bulk_delete_with_shifts(
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
            conn, date=SHIFTS_STARTS_AT, operators_schedule_types_ids=[3],
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
                'records': [
                    {
                        'record_id': 3,
                        'yandex_uid': 'uid3',
                        'schedule_type_id': 4,
                        'starts_at_with_tz': '2023-08-13 00:00:00.0',
                        'expires_at_with_tz': '2023-08-16 00:00:00.0',
                        'revision_id': REVISION_ID,
                    },
                ],
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
                'message': 'Cannot modify schedule with future shifts',
            },
            [1, 2, 3, 4, 5],
        ),
        (
            {
                'records': [
                    {
                        'record_id': 3,
                        'yandex_uid': 'uid3',
                        'schedule_type_id': 4,
                        'starts_at_with_tz': '2023-08-13 00:00:00.0',
                        'expires_at_with_tz': '2023-08-16 00:00:00.0',
                        'revision_id': REVISION_ID,
                    },
                ],
                'force_shift_delete': True,
            },
            {},
            [3],
        ),
    ],
)
async def test_deleting_shifts_in_bulk_modifying(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_res,
        shifts_left,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )

    if res.status > 200:
        data = await res.json()
        assert data == expected_res

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master

    async with master_pool.acquire() as conn:
        res = await operators_db.get_shifts_from_date(
            conn, date=SHIFTS_STARTS_AT, operators_schedule_types_ids=[3],
        )
        assert shifts_left == [record['shift_id'] for record in res]
