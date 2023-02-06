import datetime
import json

import pytest
import pytz

from test_workforce_management.web import test_v2_shifts_values as shifts_test
from workforce_management.storage.postgresql import db

URI = 'v1/additional-shift/accept'
SHIFTS_URI = 'v2/shifts/values'
HEADERS = {'X-WFM-Domain': 'taxi'}

DEFAULT_KWARGS = {
    'skill': 'hokage',
    'datetime_from': (datetime.datetime(2000, 1, 1, 1, tzinfo=pytz.UTC)),
    'datetime_to': (datetime.datetime(2100, 1, 1, 1, tzinfo=pytz.UTC)),
}


def remove_extra_fields(records):
    for record in records:
        if not record:
            continue
        record.pop('operator')
        record['shift'].pop('audit')
        record['shift'].pop('breaks')
    return records


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'additional_shifts_jobs.sql',
        'additional_shifts_jobs_extra.sql',
        'simple_shifts.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        pytest.param({'job_id': 2, 'yandex_uid': 'uid2'}, 200, id='simple'),
        pytest.param(
            {'job_id': 10, 'yandex_uid': 'uid1'},
            404,
            id='non_existing_job_id',
        ),
        pytest.param(
            {'job_id': 1, 'yandex_uid': 'uid3'},
            404,
            id='non_existing_candidate',
        ),
        pytest.param(
            {
                'job_id': 2,
                'yandex_uid': 'uid2',
                'revision_id': '2020-07-02T00:00:00.0 +0000',
            },
            200,
            id='with_revision_id',
        ),
        pytest.param(
            {'job_id': 1, 'yandex_uid': 'uid1'}, 400, id='picked_not_offered',
        ),
    ],
)
async def test_records_modified(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    operators_db = db.OperatorsRepo(web_context)

    res = await taxi_workforce_management_web.post(URI, json=tst_request)

    assert res.status == expected_status

    if res.status > 200:
        return

    job_id = tst_request['job_id']
    yandex_uid = tst_request['yandex_uid']

    async with operators_db.slave.acquire() as conn:
        job = await operators_db.get_additional_shifts_job_by_id(
            conn, job_id=job_id,
        )

        candidates = await operators_db.get_additional_shift_candidates(
            conn, job_id=job_id,
        )

    filtered_candidates = [
        candidate
        for candidate in candidates
        if candidate['yandex_uid'] == yandex_uid
    ]

    assert filtered_candidates

    candidate = filtered_candidates[0]

    status_updates = [
        json.loads(status_update)
        for status_update in candidate['status_updates']
    ]

    assert job['shifts_distributed'] > 0
    assert job['status'] == 2
    assert candidate['status'] == 'accepted'
    assert len(status_updates) > 1
    assert status_updates[-1]['status'] == 'accepted'


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'additional_shifts_jobs.sql',
        'additional_shifts_jobs_extra.sql',
        'simple_shifts.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'accept_request, shifts_request, expected_status, expected_result',
    [
        pytest.param(
            {'job_id': 2, 'yandex_uid': 'uid2'},
            {
                'datetime_from': '2020-08-01 13:00:00.0 +0000',
                'datetime_to': '2020-08-03 15:00:00.0 +0000',
                'yandex_uids': ['uid2'],
                'limit': 1,
            },
            200,
            [
                {
                    'shift': {
                        'shift_id': 2,
                        'yandex_uid': 'uid2',
                        'type': 'additional',
                        'start': shifts_test.parse_and_make_step(
                            '2020-08-02 00:00:00.0 +0000', 0,
                        ),
                        'operators_schedule_types_id': 2,
                        'duration_minutes': 600,
                        'skill': 'tatarin',
                    },
                },
            ],
            id='simple',
        ),
    ],
)
async def test_shifts(
        taxi_workforce_management_web,
        web_context,
        accept_request,
        shifts_request,
        expected_status,
        expected_result,
):
    res = await taxi_workforce_management_web.post(URI, json=accept_request)

    assert res.status == expected_status

    if res.status > 200:
        return

    data = await res.json()

    new_res = await taxi_workforce_management_web.post(
        URI, json=accept_request,
    )

    # job now is completed
    assert new_res.status == 404

    raw_shifts = await taxi_workforce_management_web.post(
        SHIFTS_URI, json=shifts_request, headers=HEADERS,
    )
    shifts = await raw_shifts.json()
    records = shifts['records']

    assert remove_extra_fields(records) == expected_result

    shift = records[0]['shift']
    for field in data:
        assert data[field] == shift[field]


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'additional_shifts_jobs.sql',
        'additional_shifts_jobs_extra.sql',
        'bad_additional_shifts_jobs.sql',
        'simple_shifts.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        pytest.param(
            {
                'job_id': 2,
                'yandex_uid': 'uid2',
                'revision_id': '2020-07-01T00:00:00.0 +0000',
            },
            409,
            id='wrong_revision',
        ),
        pytest.param(
            {'job_id': 9, 'yandex_uid': 'uid1'}, 400, id='busy_candidate',
        ),
        pytest.param(
            {'job_id': 8, 'yandex_uid': 'uid1'},
            400,
            id='all_shifts_distributed',
        ),
        pytest.param(
            {'job_id': 13, 'yandex_uid': 'uid1'},
            400,
            id='period_is_not_covered_by_any_schedule',
        ),
    ],
)
async def test_transactions_rollback(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    operators_db = db.OperatorsRepo(context=web_context)

    async with operators_db.master.acquire() as conn:
        old_jobs = await operators_db.get_additional_shifts_jobs(
            conn, skill=DEFAULT_KWARGS['skill'],
        )

        old_candidates = await operators_db.get_additional_shift_candidates(
            conn, job_id=tst_request['job_id'],
        )

        old_shifts = await operators_db.get_shifts(
            conn,
            datetime_from=DEFAULT_KWARGS['datetime_from'],
            datetime_to=DEFAULT_KWARGS['datetime_to'],
            limit=100,
        )

        old_breaks = await operators_db.get_operator_breaks(conn)

    res = await taxi_workforce_management_web.post(URI, json=tst_request)

    assert res.status == expected_status

    if res.status == 200:
        return

    async with operators_db.master.acquire() as conn:
        new_jobs = await operators_db.get_additional_shifts_jobs(
            conn, skill=DEFAULT_KWARGS['skill'],
        )

        new_candidates = await operators_db.get_additional_shift_candidates(
            conn, job_id=tst_request['job_id'],
        )

        new_shifts = await operators_db.get_shifts(
            conn,
            datetime_from=DEFAULT_KWARGS['datetime_from'],
            datetime_to=DEFAULT_KWARGS['datetime_to'],
            limit=10,
        )

        new_breaks = await operators_db.get_operator_breaks(conn)

    assert old_jobs == new_jobs
    assert old_candidates == new_candidates
    assert old_shifts == new_shifts
    assert old_breaks == new_breaks


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'additional_shifts_jobs.sql',
        'additional_shifts_jobs_extra.sql',
        'simple_shifts.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, tst_headers, expected_author_yandex_uid',
    [
        pytest.param(
            {'job_id': 2, 'yandex_uid': 'uid2'},
            {'X-Yandex-UID': 'uid1'},
            'uid1',
            id='yandex_uid != X-Yandex-UID',
        ),
        pytest.param(
            {
                'job_id': 2,
                'yandex_uid': 'uid2',
                'revision_id': '2020-07-02T00:00:00.0 +0000',
            },
            {'X-Yandex-UID': 'uid2'},
            'uid2',
            id='yandex_uid == X-Yandex-UID',
        ),
        pytest.param(
            {
                'job_id': 2,
                'yandex_uid': 'uid2',
                'revision_id': '2020-07-02T00:00:00.0 +0000',
            },
            {},
            'uid2',
            id='no X-Yandex-UID',
        ),
    ],
)
async def test_shift_author_uid(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        tst_headers,
        expected_author_yandex_uid,
):
    operators_db = db.OperatorsRepo(web_context)

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=tst_headers,
    )
    data = await res.json()
    async with operators_db.slave.acquire() as conn:
        shift_data = await operators_db.get_shift_by_id(
            conn, shift_id=data['shift_id'],
        )
    assert shift_data['author_yandex_uid'] == expected_author_yandex_uid
