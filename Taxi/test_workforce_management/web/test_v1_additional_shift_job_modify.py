import pytest


JOB_MODIFY_URI = '/v1/additional-shift/job/modify'
JOB_VALUES_URI = '/v1/additional-shifts/job/values'
CANDIDATES_VALUES_URI = '/v1/additional-shift/candidates/values'
REVISION_ID = '2020-07-01T00:00:00.000000 +0000'
HEADERS = {'X-WFM-Domain': 'taxi'}

JOB_VALUES_REQUEST = {
    'datetime_from': '2020-08-01T00:00:00.0 +0000',
    'datetime_to': '2020-08-10T00:00:00.0 +0000',
    'skill': 'tatarin',
}


@pytest.mark.parametrize(
    'tst_request, expected_response_status, expected_candidates_statuses',
    [
        pytest.param(
            {
                'job_id': 2,
                'job_status': 'rejected',
                'revision_id': REVISION_ID,
            },
            200,
            {'uid2': 'cancelled'},
            id='reject job, ok',
        ),
        pytest.param(
            {
                'job_id': 4,
                'job_status': 'rejected',
                'revision_id': REVISION_ID,
            },
            200,
            {'uid3': 'cancelled', 'uid1': 'accepted', 'uid2': 'rejected'},
            id='terminal_statuses_not_changed',
        ),
        pytest.param(
            {
                'job_id': 451,
                'job_status': 'rejected',
                'revision_id': REVISION_ID,
            },
            404,
            None,
            id='reject job, job not found',
        ),
        pytest.param(
            {
                'job_id': 2,
                'job_status': 'rejected',
                'revision_id': '2020-07-02T00:00:00.000000 +0000',
            },
            409,
            None,
            id='bad revision_id',
        ),
        pytest.param(
            {'job_id': 2, 'revision_id': '2020-07-02T00:00:00.000000 +0000'},
            400,
            None,
            id='modify without job_status',
        ),
    ],
)
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'additional_shifts_jobs.sql'],
)
async def test_update_status_rejected(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_response_status,
        expected_candidates_statuses,
):
    modify_job_response = await taxi_workforce_management_web.post(
        JOB_MODIFY_URI, json=tst_request,
    )
    assert modify_job_response.status == expected_response_status

    if modify_job_response.status > 200:
        return

    get_job_response = await taxi_workforce_management_web.post(
        JOB_VALUES_URI, json=JOB_VALUES_REQUEST, headers=HEADERS,
    )

    assert get_job_response.status == 200
    if get_job_response.status > 200:
        return

    data = await get_job_response.json()
    jobs = data['jobs']

    modified_job = None
    for job in jobs:
        if job['job_id'] == tst_request['job_id']:
            modified_job = job
            break
    else:
        assert modified_job
        return
    assert modified_job['job_status'] == 'rejected'

    get_candidates_request = {
        'job_id': tst_request['job_id'],
        'limit': 10,
        'offset': 0,
    }

    get_candidates_response = await taxi_workforce_management_web.post(
        CANDIDATES_VALUES_URI, json=get_candidates_request, headers=HEADERS,
    )

    data = await get_candidates_response.json()
    candidates = data['candidates']
    for candidate in candidates:
        assert (
            candidate['status']
            == expected_candidates_statuses[candidate['yandex_uid']]
        )
