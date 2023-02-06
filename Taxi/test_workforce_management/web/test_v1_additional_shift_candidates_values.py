import pytest


URI = 'v1/additional-shift/candidates/values'
HEADERS = {'X-WFM-Domain': 'taxi'}


def prepare_status_update(status_update):
    status_update.pop('date')
    return status_update


FIRST_CANDIDATE = {
    'job_id': 1,
    'yandex_uid': 'uid1',
    'login': 'abd-damir',
    'full_name': 'Abdullin Damir',
    'status': 'picked',
    'status_updates': [{'status': 'picked'}, {'status': 'offered'}],
}

SECOND_CANDIDATE = {
    'job_id': 2,
    'yandex_uid': 'uid2',
    'login': 'chakchak',
    'full_name': 'Gilgenberg Valeria',
    'status': 'offered',
    'status_updates': [{'status': 'picked'}, {'status': 'offered'}],
}

THIRD_CANDIDATE = {
    'job_id': 1,
    'yandex_uid': 'uid2',
    'login': 'chakchak',
    'full_name': 'Gilgenberg Valeria',
    'status': 'offered',
    'status_updates': [{'status': 'picked'}, {'status': 'offered'}],
}


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'additional_shifts_jobs.sql',
        'additional_shifts_jobs_extra.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        pytest.param(
            {'job_id': 2, 'limit': 10, 'offset': 0},
            200,
            {'candidates': [SECOND_CANDIDATE]},
            id='job_id_only',
        ),
        pytest.param(
            {'job_id': 1, 'limit': 10, 'offset': 0},
            200,
            {'candidates': [FIRST_CANDIDATE, THIRD_CANDIDATE]},
            id='two_candidates',
        ),
        pytest.param(
            {'job_id': 1, 'statuses': ['offered'], 'limit': 10, 'offset': 0},
            200,
            {'candidates': [THIRD_CANDIDATE]},
            id='job_id_and_statuses',
        ),
        pytest.param(
            {
                'job_id': 1,
                'statuses': ['picked', 'accepted'],
                'limit': 10,
                'offset': 0,
            },
            200,
            {'candidates': [FIRST_CANDIDATE]},
            id='statuses_with_non_existing_status',
        ),
        pytest.param(
            {'job_id': 10, 'limit': 10, 'offset': 0},
            404,
            {},
            id='non_existsting_job_id',
        ),
        pytest.param(
            {'job_id': 2, 'statuses': ['rejected'], 'limit': 10, 'offset': 0},
            200,
            {'candidates': []},
            id='non_existing_status',
        ),
        pytest.param(
            {'job_id': 1, 'limit': 1, 'offset': 0},
            200,
            {'candidates': [FIRST_CANDIDATE]},
            id='check_limit',
        ),
        pytest.param(
            {'job_id': 1, 'limit': 10, 'offset': 1},
            200,
            {'candidates': [THIRD_CANDIDATE]},
            id='check_offset',
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
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if res.status > 200:
        return

    data = await res.json()

    candidates = {
        'candidates': [
            {
                'job_id': candidate['job_id'],
                'yandex_uid': candidate['yandex_uid'],
                'login': candidate['login'],
                'full_name': candidate['full_name'],
                'status': candidate['status'],
                'status_updates': [
                    prepare_status_update(record)
                    for record in candidate['status_updates']
                ],
            }
            for candidate in data['candidates']
        ],
    }
    assert candidates == expected_result
