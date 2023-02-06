import copy
import typing as tp

import pytest


JOB_VALUES_URI = 'v1/additional-shifts/job/values'
HEADERS = {'X-WFM-Domain': 'taxi'}


def remove_redundant_fields(raw_job):
    job = copy.deepcopy(raw_job)

    job.pop('created_at')
    job.pop('updated_at')
    job.pop('revision_id')
    job['job_data'].pop('datetime_from')
    job['job_data'].pop('datetime_to')
    job['job_data'].pop('ttl_time')
    return job


FIRST_JOB = {
    'job_id': 1,
    'job_status': 'running',
    'shifts_distributed': 0,
    'author_login': 'tatarstan',
    'author_yandex_uid': 'uid3',
    'candidates_statistic': [{'status': 'picked', 'value': 1}],
    'job_data': {
        'skill': 'hokage',
        'dry_run': False,
        'additional_shifts_count': 1,
    },
}

SECOND_JOB = {
    'job_id': 2,
    'job_status': 'running',
    'shifts_distributed': 0,
    'author_login': 'tatarstan',
    'author_yandex_uid': 'uid3',
    'candidates_statistic': [{'status': 'offered', 'value': 1}],
    'operators_filter': {
        'nearest_shift_filter': {
            'threshold_minutes': {'left': 180, 'right': 180},
        },
        'tag_filter': {
            'connection_policy': 'conjunction',
            'ownership_policy': 'include',
            'tags': ['новичок'],
        },
    },
    'job_data': {
        'skill': 'tatarin',
        'dry_run': True,
        'additional_shifts_count': 1,
    },
}

THIRD_JOB: tp.Dict = {
    **SECOND_JOB,
    'shifts_distributed': 1,
    'job_id': 3,
    'author_login': 'chakchak',
    'author_yandex_uid': 'uid2',
}
THIRD_JOB.pop('operators_filter')

FOURTH_JOB = {
    'author_login': 'tatarstan',
    'author_yandex_uid': 'uid3',
    'candidates_statistic': [{'status': 'offered', 'value': 2}],
    'job_data': {
        'additional_shifts_count': 1,
        'candidates_count': 2,
        'dry_run': False,
        'skill': 'tatarin',
    },
    'job_id': 4,
    'job_status': 'running',
    'shifts_distributed': 1,
}

SIMPLE_REQUEST = {
    'datetime_from': '2020-07-02T00:00:00.0 +0000',
    'skill': 'tatarin',
}


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'additional_shifts_jobs.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        pytest.param(
            {
                'datetime_from': '2020-07-02T00:00:00.0 +0000',
                'datetime_to': '2020-07-05T00:00:00.0 +0000',
                'skill': 'hokage',
            },
            200,
            {'jobs': [FIRST_JOB]},
            id='only_first_job_period_matches',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-02T00:00:00.0 +0000',
                'datetime_to': '2020-08-02T10:00:00.0 +0000',
                'skill': 'tatarin',
            },
            200,
            {'jobs': [SECOND_JOB, THIRD_JOB]},
            id='jobs_with_exact_skill',
        ),
        pytest.param(
            {
                'author_yandex_uid': 'uid2',
                'datetime_from': '2020-07-02T00:00:00.0 +0000',
                'skill': 'tatarin',
            },
            200,
            {'jobs': [THIRD_JOB]},
            id='jobs_with_exact_skill_and_author_uid',
        ),
        pytest.param(
            {'yandex_uid': 'uid2'},
            200,
            {'jobs': [SECOND_JOB]},
            id='jobs_suits_to_uid2_candidate',
        ),
        pytest.param({'skill': 'tatarin'}, 400, {}, id='wrong_request_0'),
        pytest.param(
            {'datetime_from': '2020-07-02T00:00:00.0 +0000'},
            400,
            {},
            id='wrong_request_1',
        ),
        pytest.param(
            {
                'datetime_from': '2020-09-02T00:00:00.0 +0000',
                'datetime_to': '2020-09-02T10:00:00.0 +0000',
                'skill': 'tatarin',
            },
            200,
            {'jobs': [FOURTH_JOB]},
            id='job_with_candidates_count',
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
):
    res = await taxi_workforce_management_web.post(
        JOB_VALUES_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if res.status > 200:
        return

    data = await res.json()

    prepared_data = {
        'jobs': [remove_redundant_fields(job) for job in data['jobs']],
    }
    assert prepared_data == expected_result


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'additional_shifts_jobs.sql'],
)
@pytest.mark.parametrize(
    'tst_statuses, expected_status, expected_jobs',
    [
        pytest.param(['running'], 200, [2, 3, 4], id='jobs_found'),
        pytest.param(['expired'], 200, [], id='no jobs'),
        pytest.param(
            ['bla-bla-bla'], 400, {'jobs': []}, id='wrong statuses value',
        ),
    ],
)
async def test_statuses_filter(
        taxi_workforce_management_web,
        tst_statuses,
        expected_status,
        expected_jobs,
):
    request = SIMPLE_REQUEST.copy()
    request['statuses'] = tst_statuses
    res = await taxi_workforce_management_web.post(
        JOB_VALUES_URI, json=request, headers=HEADERS,
    )
    assert res.status == expected_status

    if res.status > 200:
        return

    data = await res.json()

    prepared_data = [job['job_id'] for job in data['jobs']]

    assert prepared_data == expected_jobs
