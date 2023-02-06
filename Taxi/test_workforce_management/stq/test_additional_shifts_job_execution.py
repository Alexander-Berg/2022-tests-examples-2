import copy
import datetime
import typing as tp

import pytest
import pytz

from test_workforce_management.stq import test_job_execution
from workforce_management.api import (
    v1_additional_shifts_job_values_post as job_values_handler,
)
from workforce_management.common import constants
from workforce_management.common import exceptions
from workforce_management.common import utils
from workforce_management.common.jobs.setup import additional_shifts
from workforce_management.storage.postgresql import db


HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}

JOB_SETUP_URI = 'v1/additional-shifts/job/setup'
JOB_VALUES_URI = 'v1/additional-shifts/job/values'

CANDIDATES_SELECTION_COEF = 2


def prepare_stq_data(tst_request, tags: tp.Optional[tp.List[str]] = None):
    job_data = tst_request['job_data']
    operators_filter = tst_request.get('operators_filter')
    candidates_count = job_data.get('candidates_count')
    additional_shifts_count = job_data['additional_shifts_count']
    if candidates_count is None:
        candidates_count = additional_shifts_count * CANDIDATES_SELECTION_COEF
    data = {
        'datetime_from': (
            test_job_execution.parse_datetime(job_data['datetime_from'])
        ),
        'datetime_to': (
            test_job_execution.parse_datetime(job_data['datetime_to'])
        ),
        'skill': job_data['skill'],
        'ttl_time': (
            test_job_execution.parse_datetime(job_data['datetime_from'])
        ),
        'job_type': constants.JobTypes.additional_shifts.value,
        'extra': {
            'dry_run': job_data.get('dry_run') or False,
            'author_yandex_uid': 'uid1',
            'additional_shifts_count': additional_shifts_count,
            'candidates_count': candidates_count,
        },
    }
    if operators_filter:
        data['extra']['operators_filter'] = copy.deepcopy(operators_filter)
        if tags:
            data['extra']['operators_filter']['tag_filter']['tags'] = tags
    return data


def parse_pg_datetime(dtm):
    dtm_list = list(dtm)
    dtm_list[dtm.rfind(':')] = ''
    dtm_list.insert(dtm.rfind('+'), '.0 ')
    return test_job_execution.parse_datetime(''.join(dtm_list))


def prepare_job_data(raw_job):
    job = copy.deepcopy(raw_job)

    job.pop('created_at')
    job.pop('updated_at')
    job.pop('revision_id')

    job_data = job['job_data']
    datetime_from, datetime_to, ttl_time = (
        job_data['datetime_from'],
        job_data['datetime_to'],
        job_data['ttl_time'],
    )
    job_data['datetime_from'] = parse_pg_datetime(datetime_from)
    job_data['datetime_to'] = parse_pg_datetime(datetime_to)
    job_data['ttl_time'] = parse_pg_datetime(ttl_time)

    job['job_data'] = job_data
    return job


def prepare_candidate(candidate):
    return {
        'yandex_uid': candidate['yandex_uid'],
        'status': candidate['status'],
    }


FIRST_JOB = {
    'job_id': 1,
    'job_status': 'running',
    'shifts_distributed': 0,
    'author_yandex_uid': 'uid1',
    'author_login': 'abd-damir',
    'job_data': {
        'datetime_from': (
            test_job_execution.parse_datetime('2020-07-02T00:00:00.0 +0000')
        ),
        'datetime_to': (
            test_job_execution.parse_datetime('2020-07-02T10:00:00.0 +0000')
        ),
        'skill': 'pokemon',
        'dry_run': True,
        'additional_shifts_count': 1,
        'ttl_time': (
            test_job_execution.parse_datetime('2020-07-02T00:00:00.0 +0000')
        ),
        'candidates_count': 2,
    },
    'operators_filter': {
        'tag_filter': {
            'connection_policy': 'conjunction',
            'ownership_policy': 'include',
            'tags': ['naruto'],
        },
    },
}

SECOND_JOB = {
    'job_id': 1,
    'job_status': 'running',
    'shifts_distributed': 0,
    'author_yandex_uid': 'uid1',
    'author_login': 'abd-damir',
    'job_data': {
        'datetime_from': (
            test_job_execution.parse_datetime('2020-08-02T02:00:00.0 +0000')
        ),
        'datetime_to': (
            test_job_execution.parse_datetime('2020-08-02T12:00:00.0 +0000')
        ),
        'skill': 'hokage',
        'dry_run': False,
        'additional_shifts_count': 1,
        'ttl_time': (
            test_job_execution.parse_datetime('2020-08-02T02:00:00.0 +0000')
        ),
        'candidates_count': 2,
    },
}

THIRD_JOB = {
    'job_id': 1,
    'job_status': 'running',
    'shifts_distributed': 0,
    'author_yandex_uid': 'uid1',
    'author_login': 'abd-damir',
    'job_data': {
        'datetime_from': (
            test_job_execution.parse_datetime('2020-07-02T00:00:00.0 +0000')
        ),
        'datetime_to': (
            test_job_execution.parse_datetime('2020-07-02T10:00:00.0 +0000')
        ),
        'skill': 'pokemon',
        'dry_run': True,
        'additional_shifts_count': 1,
        'ttl_time': (
            test_job_execution.parse_datetime('2020-07-02T00:00:00.0 +0000')
        ),
        'candidates_count': 1,
    },
}

SETUP_REQUESTS = [
    {
        'job_data': {
            'datetime_from': '2020-07-02T00:00:00.0 +0000',
            'datetime_to': '2020-07-02T10:00:00.0 +0000',
            'skill': 'pokemon',
            'dry_run': True,
            'additional_shifts_count': 1,
        },
        'operators_filter': {
            'tag_filter': {
                'connection_policy': 'conjunction',
                'ownership_policy': 'include',
                'tags': ['naruto'],
            },
        },
    },
    {
        'job_data': {
            'datetime_from': '2020-08-02T02:00:00.0 +0000',
            'datetime_to': '2020-08-02T12:00:00.0 +0000',
            'skill': 'hokage',
            'additional_shifts_count': 1,
        },
    },
    {
        'job_data': {
            'datetime_from': '2020-08-02T02:00:00.0 +0000',
            'datetime_to': '2020-08-02T12:00:00.0 +0000',
            'skill': 'pokemon',
            'additional_shifts_count': 1,
        },
        'operators_filter': {
            'nearest_shift_filter': {
                'threshold_minutes': {'left': 180, 'right': 120},
            },
        },
    },
    {
        'job_data': {
            'datetime_from': '2020-07-02T00:00:00.0 +0000',
            'datetime_to': '2020-07-02T10:00:00.0 +0000',
            'skill': 'pokemon',
            'dry_run': True,
            'additional_shifts_count': 1,
            'candidates_count': 1,
        },
    },
]

VALUES_REQUESTS = [
    {
        'datetime_from': '2020-07-02T00:00:00.0 +0000',
        'datetime_to': '2020-07-02T10:00:00.0 +0000',
        'skill': 'pokemon',
    },
    {'datetime_from': '2020-07-02T00:00:00.0 +0000', 'skill': 'hokage'},
]

JOB_SETUP_KWARGS: tp.Dict[str, tp.Any] = {
    'datetime_from': datetime.datetime(2020, 8, 2, 2, tzinfo=pytz.UTC),
    'datetime_to': datetime.datetime(2020, 8, 2, 12, tzinfo=pytz.UTC),
    'skill': 'hokage',
    'ttl_time': datetime.datetime(2020, 8, 2, 2, tzinfo=pytz.UTC),
    'extra': {
        'dry_run': False,
        'additional_shifts_count': 1,
        'author_yandex_uid': 'uid1',
        'candidates_count': 1,
    },
    'job_type': constants.JobTypes.additional_shifts.value,
}


@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        pytest.param(
            SETUP_REQUESTS[0], 200, id='job_simple_0_with_operators_filter',
        ),
        pytest.param(SETUP_REQUESTS[1], 200, id='job_simple_1'),
        pytest.param(SETUP_REQUESTS[3], 200, id='job_with_candidates_count'),
    ],
)
async def test_setup_kwargs(
        taxi_workforce_management_web,
        stq,
        tst_request,
        expected_status,
        mock_effrat_employees,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.post(
        JOB_SETUP_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    task = stq.workforce_management_setup_additional_shifts_jobs.next_call()
    assert task['kwargs'] == prepare_stq_data(tst_request)


@pytest.mark.parametrize(
    'kwargs, expected_result',
    [
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[0]),
                'datetime_from': datetime.datetime(
                    2020, 7, 2, 0, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 7, 2, 10, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 7, 2, 0, tzinfo=pytz.UTC),
            },
            {'jobs': [FIRST_JOB]},
            id='job_created_simple_0',
        ),
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[1]),
                'datetime_from': datetime.datetime(
                    2020, 8, 2, 2, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 8, 2, 12, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 8, 2, 2, tzinfo=pytz.UTC),
            },
            {'jobs': [SECOND_JOB]},
            id='job_created_simple_1',
        ),
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[3]),
                'datetime_from': datetime.datetime(
                    2020, 7, 2, 0, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 7, 2, 10, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 7, 2, 0, tzinfo=pytz.UTC),
            },
            {'jobs': [THIRD_JOB]},
            id='job_created_with_candidates_count',
        ),
    ],
)
async def test_additional_shifts_job_existence(
        stq_runner,
        stq3_context,
        kwargs,
        expected_result,
        mock_effrat_employees,
):
    mock_effrat_employees()

    operators_db = db.OperatorsRepo(context=stq3_context)
    async with operators_db.master.acquire() as conn, conn.transaction():
        _ = await operators_db.create_additional_shifts_job(
            conn,
            datetime_from=kwargs['datetime_from'],
            datetime_to=kwargs['datetime_to'],
            skill=kwargs['skill'],
            ttl_time=kwargs['ttl_time'],
            extra=kwargs['extra'],
        )

    await stq_runner.workforce_management_setup_additional_shifts_jobs.call(
        task_id='1', args=(), kwargs=kwargs,
    )

    async with operators_db.master.acquire() as conn:
        raw_jobs = await operators_db.get_additional_shifts_jobs(
            conn,
            datetime_from=kwargs.get('datetime_from'),
            datetime_to=kwargs.get('datetime_to'),
            skill=kwargs.get('skill'),
            yandex_uid=kwargs.get('yandex_uid'),
            author_yandex_uid=kwargs.get('author_yandex_uid'),
            candidate_statuses=constants.CANDIDATES_STATUSES,
        )

    jobs_with_loaded_extra_data = [
        job
        for job in [utils.load_extra_job_data(job) for job in raw_jobs]
        if job is not None
    ]

    jobs = [
        utils.build_additional_shifts_job(job, constants.CANDIDATES_STATUSES)
        for job in job_values_handler.enrich_jobs(
            stq3_context.operators_cache, 'taxi', jobs_with_loaded_extra_data,
        )
    ]

    prepared_jobs = {
        'jobs': [prepare_job_data(job.serialize()) for job in jobs],
    }
    assert prepared_jobs == expected_result


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'kwargs, expected_result',
    [
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[1]),
                'datetime_from': datetime.datetime(
                    2020, 8, 2, 2, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 8, 2, 12, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 8, 2, 2, tzinfo=pytz.UTC),
            },
            [{'yandex_uid': 'uid2', 'status': 'offered'}],
            id='at_least_one_candidate_picked',
        ),
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[2]),
                'datetime_from': datetime.datetime(
                    2020, 8, 6, 17, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 8, 6, 20, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 8, 22, 2, tzinfo=pytz.UTC),
            },
            [],
            id='candidate_doesnt_matches_by_nearest_shift',
        ),
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[2]),
                'datetime_from': datetime.datetime(
                    2020, 8, 7, 18, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 8, 7, 20, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 8, 22, 2, tzinfo=pytz.UTC),
            },
            [{'yandex_uid': 'uid2', 'status': 'offered'}],
            id='candidate_matches_by_nearest_shift',
        ),
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[1]),
                'datetime_from': datetime.datetime(
                    2020, 7, 30, 2, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 8, 2, 12, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 8, 2, 2, tzinfo=pytz.UTC),
            },
            [],
            id='no_candidates',
        ),
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[0]),
                'datetime_from': datetime.datetime(
                    2020, 8, 2, 2, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 8, 2, 12, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 8, 2, 2, tzinfo=pytz.UTC),
            },
            [{'yandex_uid': 'uid2', 'status': 'offered'}],
            id='tags',
        ),
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[0], tags=['abracadabra']),
                'datetime_from': datetime.datetime(
                    2020, 8, 2, 2, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 8, 2, 12, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 8, 2, 2, tzinfo=pytz.UTC),
                'tags': ['abracadabra'],
            },
            [],
            id='wrong_tags',
        ),
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[3]),
                'datetime_from': datetime.datetime(
                    2020, 8, 2, 2, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 8, 2, 12, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 8, 2, 2, tzinfo=pytz.UTC),
            },
            [{'yandex_uid': 'uid2', 'status': 'offered'}],
            id='candidates_count_parameter',
        ),
    ],
)
async def test_candidates(
        stq_runner,
        stq3_context,
        kwargs,
        expected_result,
        mock_effrat_employees,
):
    mock_effrat_employees()

    operators_db = db.OperatorsRepo(context=stq3_context)
    async with operators_db.master.acquire() as conn, conn.transaction():
        _ = await operators_db.create_additional_shifts_job(
            conn,
            datetime_from=kwargs['datetime_from'],
            datetime_to=kwargs['datetime_to'],
            skill=kwargs['skill'],
            ttl_time=kwargs['ttl_time'],
            extra=kwargs['extra'],
        )

    await stq_runner.workforce_management_setup_additional_shifts_jobs.call(
        task_id='1', args=(), kwargs=kwargs,
    )

    async with operators_db.master.acquire() as conn:
        raw_candidates = await operators_db.get_additional_shift_candidates(
            conn, job_id=1,
        )

    candidates = [prepare_candidate(candidate) for candidate in raw_candidates]

    assert candidates == expected_result


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'kwargs, expected_result',
    [
        pytest.param(
            {
                **prepare_stq_data(SETUP_REQUESTS[1]),
                'datetime_from': datetime.datetime(
                    2020, 8, 2, 2, tzinfo=pytz.UTC,
                ),
                'datetime_to': datetime.datetime(
                    2020, 8, 2, 12, tzinfo=pytz.UTC,
                ),
                'ttl_time': datetime.datetime(2020, 8, 2, 2, tzinfo=pytz.UTC),
            },
            [],
            id='operators_without_break_rules',
        ),
    ],
)
async def test_candidates_without_break_rules(
        stq_runner,
        stq3_context,
        kwargs,
        expected_result,
        mock_effrat_employees,
):
    mock_effrat_employees()

    operators_db = db.OperatorsRepo(context=stq3_context)
    async with operators_db.master.acquire() as conn, conn.transaction():
        await operators_db.create_additional_shifts_job(conn, **kwargs)

    await stq_runner.workforce_management_setup_additional_shifts_jobs.call(
        task_id='1', args=(), kwargs=kwargs,
    )

    async with operators_db.master.acquire() as conn:
        raw_candidates = await operators_db.get_additional_shift_candidates(
            conn, job_id=1,
        )

    assert raw_candidates == expected_result


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'kwargs, expected_notify',
    [
        pytest.param(
            JOB_SETUP_KWARGS,
            {
                'messages': {
                    'uid2': [
                        {
                            'message_key': 'additional_shift_offer',
                            'message_kwargs': {
                                'job_data': {
                                    'job_id': 1,
                                    'datetime_from': (
                                        '2020-08-02T02:00:00.000000 +0000'
                                    ),
                                    'datetime_to': (
                                        '2020-08-02T12:00:00.000000 +0000'
                                    ),
                                },
                            },
                        },
                    ],
                },
            },
            id='candidate_notified',
        ),
        pytest.param(
            {**JOB_SETUP_KWARGS, 'skill': 'order'},
            None,
            id='no_candidates_because_of_skill',
        ),
    ],
)
async def test_trigger_telegram_shift_offer(
        stq3_context,
        stq_runner,
        stq,
        kwargs,
        expected_notify,
        mock_effrat_employees,
):
    mock_effrat_employees()

    operators_db = db.OperatorsRepo(context=stq3_context)
    job_runner = stq_runner.workforce_management_setup_additional_shifts_jobs
    async with operators_db.master.acquire() as conn:
        await operators_db.create_additional_shifts_job(conn, **kwargs)
        await job_runner.call(task_id=1, args=(), kwargs=kwargs)
    if not expected_notify:
        assert not stq.workforce_management_bot_sending.times_called
    else:
        assert (
            stq.workforce_management_bot_sending.next_call()['kwargs']
            == expected_notify
        )


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_break_rules.sql',
        'additional_shifts_jobs.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_job_id, expected_candidates',
    [
        pytest.param(1, ['uid1', 'uid2'], id='job_with_free_shifts'),
        pytest.param(2, ['uid1'], id='job_without_free_shifts'),
        pytest.param(
            123,
            [],
            id='unexistig_job_id',
            marks=pytest.mark.xfail(raises=exceptions.JobNotExists),
        ),
    ],
)
async def test_restart_addshift_job(
        stq3_context, stq_runner, stq, tst_job_id, expected_candidates,
):
    operators_db = db.OperatorsRepo(stq3_context)

    await additional_shifts.restart_job(
        stq_runner.workforce_management_setup_additional_shifts_jobs,
        tst_job_id,
    )

    async with operators_db.master.acquire() as conn:
        raw_candidates = await operators_db.get_additional_shift_candidates(
            conn, job_id=tst_job_id,
        )

    candidates = [candidate['yandex_uid'] for candidate in raw_candidates]

    assert candidates == expected_candidates
