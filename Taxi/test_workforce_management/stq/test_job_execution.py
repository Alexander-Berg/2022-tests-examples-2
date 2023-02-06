import collections
import copy
import datetime as dt
import math

import pytest
import pytz

from taxi.stq import async_worker_ng

from workforce_management.common import constants
from workforce_management.common import utils
from workforce_management.common.jobs.setup import setup
from workforce_management.common.jobs.setup import shifts as shifts_job
from workforce_management.storage.postgresql import db
from workforce_management.stq import setup_jobs

SHIFT_URI = 'v1/shift/values'
JOB_STATUS = 'v1/job/setup/status'
JOB_SETUP = 'v1/job/setup'
JOB_SINGLE_SETUP = 'v1/operators/job/setup'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}

V3_SHIFT_SETUP_CONFIG = {
    shifts_job.DEFAULT_CONFIG_KEY: {
        'approach': 'v3',
        'breaks_version': 'v1',
        'minimum_segment_length': 60,
        'maximum_segments_count': 2,
        'plan_demand_multiplier': 1.1,
        'plan_overlap_threshold': 70,
        'multiskill': False,
        'attempts': 5,
    },
}

V3_MULTISKILL_SHIFT_SETUP_BREAKS_CONFIG = copy.deepcopy(V3_SHIFT_SETUP_CONFIG)
V3_MULTISKILL_SHIFT_SETUP_BREAKS_CONFIG[shifts_job.DEFAULT_CONFIG_KEY].update(
    {'breaks_version': 'v2', 'multiskill': True},
)

UTC = pytz.UTC


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_break_rules.sql',
        'simple_shifts_with_breaks.sql',
    ],
)
@pytest.mark.parametrize(
    'kwargs, expected_status, expected_breaks_len',
    [
        pytest.param(
            {
                'datetime_from': dt.datetime(2000, 1, 1, tzinfo=UTC),
                'datetime_to': dt.datetime(2100, 1, 1, tzinfo=UTC),
                'skill': 'pokemon',
                'job_type': constants.JobTypes.breaks.value,
                'extra': {'period_type': None},
            },
            constants.JobStatus.completed.value,
            [1, 1, 0, 2, 0, 2],
            id='0',
        ),
        pytest.param(
            {
                'datetime_from': dt.datetime(2020, 7, 26, 13, tzinfo=UTC),
                'datetime_to': dt.datetime(2100, 1, 1, tzinfo=UTC),
                'skill': 'pokemon',
                'job_type': constants.JobTypes.breaks.value,
                'extra': {'period_type': None},
            },
            constants.JobStatus.completed.value,
            [1, 0, 2, 0, 2],
            id='1',
        ),
        pytest.param(
            {
                'datetime_from': dt.datetime(2020, 7, 26, 11, tzinfo=UTC),
                'datetime_to': dt.datetime(2020, 7, 26, 13, tzinfo=UTC),
                'skill': 'pokemon',
                'job_type': constants.JobTypes.breaks.value,
                'extra': {'period_type': 'starts'},
            },
            constants.JobStatus.completed.value,
            [1],
            id='2',
        ),
    ],
)
async def test_breaks_base(
        stq3_context, stq_runner, kwargs, expected_status, expected_breaks_len,
):
    operators_db = db.OperatorsRepo(context=stq3_context)
    async with operators_db.master.acquire() as conn:
        await operators_db.create_job(conn, **kwargs)
        await stq_runner.workforce_management_setup_jobs.call(
            task_id=1, args=(), kwargs=kwargs,
        )
        res = await operators_db.get_job_status(conn, job_id=1)
        assert res['status'] == expected_status

        shifts = await operators_db.get_shifts_no_cursor(
            conn,
            datetime_from=kwargs['datetime_from'],
            datetime_to=kwargs['datetime_to'],
            skills=[kwargs['skill']],
            period_type=constants.PeriodType.intersects.value,
        )
        breaks_len = [len(shift['breaks']) for shift in shifts]
        assert breaks_len == expected_breaks_len


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
        V3_MULTISKILL_SHIFT_SETUP_BREAKS_CONFIG
    ),
)
@pytest.mark.parametrize(
    'kwargs, expected_status, expected_shifts',
    [
        pytest.param(
            {
                'datetime_from': dt.datetime(2022, 2, 6, 21, tzinfo=UTC),
                'datetime_to': dt.datetime(2022, 2, 7, 21, tzinfo=UTC),
                'skill': 'group_1_2',
                'extra': {'skill_type': 'any'},
                'job_type': constants.JobTypes.shifts.value,
            },
            constants.JobStatus.completed.value,
            {
                'skill_1': [
                    {
                        'yandex_uid': 'uid3',
                        'start': dt.datetime(2022, 2, 7, 0, tzinfo=UTC),
                        'duration_minutes': 360,
                    },
                ],
            },
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['simple_shifts_setup_data.sql'],
                ),
            ],
            id='absences_over_plan_1',
        ),
        pytest.param(
            {
                'datetime_from': dt.datetime(2022, 3, 1, 21, tzinfo=UTC),
                'datetime_to': dt.datetime(2022, 3, 8, 21, tzinfo=UTC),
                'skill': 'group_1_2',
                'extra': {'skill_type': 'any'},
                'job_type': constants.JobTypes.shifts.value,
            },
            constants.JobStatus.completed.value,
            {
                'skill_1': [
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 4, 0, tzinfo=UTC),
                        'yandex_uid': 'uid1',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 5, 0, tzinfo=UTC),
                        'yandex_uid': 'uid1',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 4, 0, tzinfo=UTC),
                        'yandex_uid': 'uid2',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 5, 0, tzinfo=UTC),
                        'yandex_uid': 'uid2',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 4, 0, tzinfo=UTC),
                        'yandex_uid': 'uid3',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 5, 0, tzinfo=UTC),
                        'yandex_uid': 'uid3',
                    },
                ],
                'skill_2': [],
            },
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['simple_shifts_setup_data.sql'],
                ),
            ],
            id='any_skill_type',
        ),
        pytest.param(
            {
                'datetime_from': dt.datetime(2022, 3, 1, 21, tzinfo=UTC),
                'datetime_to': dt.datetime(2022, 3, 8, 21, tzinfo=UTC),
                'skill': 'group_1_2',
                'extra': {'skill_type': 'primary'},
                'job_type': constants.JobTypes.shifts.value,
            },
            constants.JobStatus.completed.value,
            {
                'skill_1': [
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 4, 0, tzinfo=UTC),
                        'yandex_uid': 'uid1',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 5, 0, tzinfo=UTC),
                        'yandex_uid': 'uid1',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 4, 0, tzinfo=UTC),
                        'yandex_uid': 'uid2',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 5, 0, tzinfo=UTC),
                        'yandex_uid': 'uid2',
                    },
                ],
                'skill_2': [],
            },
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['simple_shifts_setup_data.sql'],
                ),
            ],
            id='primary_skills',
        ),
        pytest.param(
            {
                'datetime_from': dt.datetime(2022, 3, 1, 21, tzinfo=UTC),
                'datetime_to': dt.datetime(2022, 3, 8, 21, tzinfo=UTC),
                'skill': 'group_1_2',
                'extra': {'skill_type': 'secondary'},
                'job_type': constants.JobTypes.shifts.value,
            },
            constants.JobStatus.completed.value,
            {
                'skill_1': [
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 4, 0, tzinfo=UTC),
                        'yandex_uid': 'uid3',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 5, 0, tzinfo=UTC),
                        'yandex_uid': 'uid3',
                    },
                ],
                'skill_2': [
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 4, 0, tzinfo=UTC),
                        'yandex_uid': 'uid1',
                    },
                    {
                        'duration_minutes': 360,
                        'start': dt.datetime(2022, 3, 5, 0, tzinfo=UTC),
                        'yandex_uid': 'uid1',
                    },
                ],
            },
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['simple_shifts_setup_data.sql'],
                ),
            ],
            id='secondary_skills',
        ),
    ],
)
async def test_shifts_v3(
        stq3_context, stq_runner, kwargs, expected_status, expected_shifts,
):
    operators_db = db.OperatorsRepo(context=stq3_context)
    async with operators_db.master.acquire() as conn:
        await operators_db.create_job(conn, **kwargs)
        await stq_runner.workforce_management_setup_jobs.call(
            task_id=1, args=(), kwargs=kwargs,
        )
        res = await operators_db.get_job_status(conn, job_id=1)
        assert res['status'] == expected_status

        shifts = {
            skill: utils.obj_to_dict(
                await operators_db.get_shifts_no_cursor(
                    conn,
                    datetime_from=kwargs['datetime_from'],
                    datetime_to=kwargs['datetime_to'],
                    skills=[skill],
                ),
                ['yandex_uid', 'start', 'duration_minutes'],
            )
            for skill in expected_shifts
        }
        assert shifts == expected_shifts


@pytest.mark.now('2020-07-27T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_break_rules.sql',
        'simple_shifts_with_breaks.sql',
    ],
)
@pytest.mark.parametrize(
    'kwargs, expected_status, expected_shift_count',
    [
        (
            {
                'datetime_from': dt.datetime(2020, 7, 14),
                'datetime_to': dt.datetime(2020, 10, 1),
                'skill': 'pokemon',
                'job_type': constants.JobTypes.shifts.value,
            },
            constants.JobStatus.completed.value,
            {'pokemon': 58},
        ),
        (
            {
                'datetime_from': dt.datetime(2020, 7, 2),
                'datetime_to': dt.datetime(2020, 7, 10),
                'skill': 'pokemon',
                'job_type': constants.JobTypes.shifts.value,
                'extra': {'yandex_uids': ['uid37']},
            },
            constants.JobStatus.completed.value,
            {'pokemon': 0},
        ),
    ],
)
async def test_shifts_base(
        stq3_context,
        stq_runner,
        kwargs,
        expected_status,
        expected_shift_count,
):
    operators_db = db.OperatorsRepo(context=stq3_context)
    async with operators_db.master.acquire() as conn:
        await operators_db.create_job(conn, **kwargs)
        await stq_runner.workforce_management_setup_jobs.call(
            task_id=1, args=(), kwargs=kwargs,
        )
        res = await operators_db.get_job_status(conn, job_id=1)
        assert res['status'] == expected_status

        shifts_count = collections.defaultdict(int)
        for skill in expected_shift_count:
            shifts_cursor = operators_db.get_shifts_cursor(
                conn,
                datetime_from=kwargs['datetime_from'],
                datetime_to=kwargs['datetime_to'],
                skills=[skill],
            )
            count = 0
            async with conn.transaction():
                async for _ in shifts_cursor:
                    count += 1
            shifts_count[skill] = count

        assert shifts_count == expected_shift_count


@pytest.mark.parametrize(
    'tst_request',
    [
        (
            {
                'data': {
                    'datetime_from': '2000-01-01T00:00:00.0 +0000',
                    'datetime_to': '2100-01-01T00:00:00.0 +0000',
                    'skill': 'pokemon',
                },
                'job_type': constants.JobTypes.breaks.value,
            }
        ),
        (
            {
                'data': {
                    'datetime_from': '2000-01-01T00:00:00.0 +0000',
                    'datetime_to': '2100-01-01T00:00:00.0 +0000',
                    'skill': 'pokemon',
                    'yandex_uids': ['uid1'],
                    'period_type': 'starts',
                },
                'job_type': constants.JobTypes.breaks.value,
            }
        ),
        (
            {
                'data': {
                    'datetime_from': '2000-01-01T00:00:00.0 +0000',
                    'datetime_to': '2100-01-01T00:00:00.0 +0000',
                    'skill': 'pokemon',
                },
                'job_type': constants.JobTypes.shifts.value,
            }
        ),
    ],
)
async def test_handle(taxi_workforce_management_web, tst_request, stq):
    res = await taxi_workforce_management_web.post(
        JOB_SETUP, json=tst_request, headers=HEADERS,
    )

    assert res.status == 200

    task = stq.workforce_management_setup_jobs.next_call()

    assert task['kwargs'] == prepare_stq_data(tst_request)


@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        (
            {
                'data': {
                    'datetime_from': '2000-01-01T00:00:00.0 +0000',
                    'datetime_to': '2100-01-01T00:00:00.0 +0000',
                    'skill': 'pokemon',
                },
                'job_type': constants.JobTypes.breaks.value,
            },
            400,
        ),
        (
            {
                'data': {
                    'datetime_from': '2000-01-01T00:00:00.0 +0000',
                    'datetime_to': '2100-01-01T00:00:00.0 +0000',
                    'skill': 'pokemon',
                    'yandex_uids': ['uid1'],
                    'period_type': 'starts',
                },
                'job_type': constants.JobTypes.breaks.value,
            },
            200,
        ),
        (
            {
                'data': {
                    'datetime_from': '2000-01-01T00:00:00.0 +0000',
                    'datetime_to': '2100-01-01T00:00:00.0 +0000',
                    'skill': 'pokemon',
                    'yandex_uids': ['uid1'],
                },
                'job_type': constants.JobTypes.shifts.value,
            },
            200,
        ),
    ],
)
async def test_single_handle(
        taxi_workforce_management_web, tst_request, expected_status, stq,
):
    res = await taxi_workforce_management_web.post(
        JOB_SINGLE_SETUP, json=tst_request, headers=HEADERS,
    )

    assert res.status == expected_status

    if expected_status > 200:
        return

    task = stq.workforce_management_setup_jobs.next_call()

    assert task['kwargs'] == prepare_stq_data(tst_request)


def parse_datetime(dtm):
    return {
        '$date': 1000 * int(
            dt.datetime.strptime(dtm, constants.DATE_FORMAT).timestamp(),
        ),
    }


def prepare_stq_data(tst_request):
    job_type = tst_request['job_type']
    return {
        'datetime_from': parse_datetime(
            tst_request['data'].pop('datetime_from'),
        ),
        'datetime_to': parse_datetime(tst_request['data'].pop('datetime_to')),
        'job_type': job_type,
        'skill': tst_request['data'].pop('skill'),
        'ttl_time': tst_request.get('ttl_time'),
        'extra': {'author_yandex_uid': 'uid1', **tst_request['data']},
    }


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_break_rules.sql',
        'simple_shifts_with_breaks.sql',
        'simple_job.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_progress',
    [
        (
            {
                'datetime_from': dt.datetime(2000, 1, 1, tzinfo=UTC),
                'datetime_to': dt.datetime(2100, 1, 1, tzinfo=UTC),
                'skill': 'pokemon',
                'job_type': constants.JobTypes.breaks.value,
            },
            [0, 16.6, 33.3, 50, 66.6, 83.3, 100, 100],
        ),
    ],
)
async def test_progress(stq3_context, patch, tst_request, expected_progress):
    task_info = async_worker_ng.TaskInfo(1, 0, 0, queue='')

    iterations_progress = []

    @patch(
        'workforce_management.storage.postgresql.db.'
        'OperatorsRepo.update_shift_setup_job',
    )
    async def update_shift_setup_job(*args, **kwargs):
        iterations_progress.append(kwargs['progress'])

    await setup_jobs.task(stq3_context, task_info, **tst_request)

    assert update_shift_setup_job.calls

    assert len(iterations_progress) == len(expected_progress)
    for progress, expected in zip(iterations_progress, expected_progress):
        assert math.isclose(progress, expected, abs_tol=0.1)


@pytest.mark.now('2020-07-19T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='default'),
        pytest.param(
            id='v3',
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_SHIFT_SETUP_SETTINGS=(
                    V3_MULTISKILL_SHIFT_SETUP_BREAKS_CONFIG
                ),
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'kwargs, expected_notify',
    [
        (
            {
                'datetime_from': dt.datetime(2020, 7, 28),
                'datetime_to': dt.datetime(2020, 8, 10),
                'skill': 'pokemon',
                'extra': {'skill_type': 'any'},
                'job_type': constants.JobTypes.shifts.value,
            },
            None,
        ),
        (
            {
                'datetime_from': dt.datetime(2020, 7, 19),
                'datetime_to': dt.datetime(2020, 7, 24),
                'skill': 'pokemon',
                'extra': {'skill_type': 'any'},
                'job_type': constants.JobTypes.shifts.value,
            },
            {'messages': {'uid1': [{'message_key': 'new_shifts'}]}},
        ),
    ],
)
async def test_trigger_telegram_job_shift(
        stq3_context,
        mock_effrat_employees,
        stq_runner,
        stq,
        kwargs,
        expected_notify,
):
    mock_effrat_employees()
    operators_db = db.OperatorsRepo(context=stq3_context)
    async with operators_db.master.acquire() as conn:
        await operators_db.create_job(conn, **kwargs)
        await stq_runner.workforce_management_setup_jobs.call(
            task_id=1, args=(), kwargs=kwargs,
        )
    if not expected_notify:
        assert not stq.workforce_management_bot_sending.times_called
    else:
        assert (
            stq.workforce_management_bot_sending.next_call()['kwargs']
            == expected_notify
        )


@pytest.mark.now('2020-07-19T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'kwargs',
    [
        pytest.param(
            {
                'extra': {'shift_id': 1, 'author_yandex_uid': 'uid1'},
                'job_type': constants.JobTypes.single_shift_violations.value,
            },
            id='default',
        ),
    ],
)
async def test_trigger_single_shift_violations(
        stq3_context, mock_effrat_employees, stq_runner, stq, kwargs,
):
    mock_effrat_employees()

    # test setup
    job_id = await setup.setup_job(
        stq3_context, **kwargs, queue_name=constants.StqQueueNames.setup_jobs,
    )
    job_kwargs = stq.workforce_management_setup_jobs.next_call()['kwargs']
    for field in kwargs:
        assert job_kwargs[field] == kwargs[field]

    # test run
    await stq_runner.workforce_management_setup_jobs.call(
        task_id=job_id, args=(), kwargs=kwargs,
    )


@pytest.mark.now('2020-07-19T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'kwargs',
    [
        pytest.param(
            {
                'extra': {'worker_num': 0, 'worker_count': 1},
                'job_type': constants.JobTypes.batch_shift_violations.value,
            },
            id='default',
        ),
    ],
)
async def test_trigger_batch_shift_violations(
        stq3_context, mock_effrat_employees, stq_runner, stq, kwargs,
):
    mock_effrat_employees()

    # test setup
    job_id = await setup.setup_constant_job(
        stq3_context,
        **kwargs,
        queue_name=constants.StqQueueNames.setup_shift_violations_jobs,
    )
    task = stq.workforce_management_setup_shift_violations_jobs.next_call()
    assert task['kwargs'] == kwargs

    # test run
    await stq_runner.workforce_management_setup_shift_violations_jobs.call(
        task_id=job_id, args=(), kwargs=kwargs,
    )
