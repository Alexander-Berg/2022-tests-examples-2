import json

import pytest

from workforce_management.common import constants
from workforce_management.storage.postgresql import db

URI = '/v1/additional-shift/fail'
UID_TO_UOID = {'uid1': 1, 'uid2': 2}


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'additional_shifts_jobs.sql',
        'additional_shifts_jobs_extra.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, tst_headers, expected_status',
    [
        pytest.param(
            {
                'job_id': 1,
                'yandex_uid': 'uid1',
                'revision_id': '2020-07-02T00:00:00.0 +0000',
            },
            {'X-Yandex-UID': 'uid1'},
            200,
            id='simple',
        ),
        pytest.param(
            {
                'job_id': 1,
                'yandex_uid': 'uid1',
                'revision_id': '2020-07-02T00:00:00.0 +0000',
                'message': 'fail message',
            },
            {'X-Yandex-UID': 'uid1'},
            200,
            id='with_message',
        ),
        pytest.param(
            {
                'job_id': 10,
                'yandex_uid': 'uid1',
                'revision_id': '2020-07-02T00:00:00.0 +0000',
            },
            {'X-Yandex-UID': 'uid1'},
            404,
            id='non_existing_job_id',
        ),
        pytest.param(
            {
                'job_id': 1,
                'yandex_uid': 'uid1',
                'revision_id': '2020-08-02T00:00:00.0 +0000',
            },
            {'X-Yandex-UID': 'uid1'},
            409,
            id='wrong_revision_id',
        ),
        pytest.param(
            {'job_id': 1, 'yandex_uid': 'uid1'},
            {'X-Yandex-UID': 'uid1'},
            400,
            id='no_revision_id_with_x_yandex_uid',
        ),
        pytest.param(
            {'job_id': 1, 'yandex_uid': 'uid1'},
            {},
            200,
            id='no_revision_id_no_x_yandex_uid',
        ),
        pytest.param(
            {
                'job_id': 8,
                'yandex_uid': 'uid2',
                'revision_id': '2020-08-02T00:00:00.0 +0000',
            },
            {'X-Yandex-UID': 'uid1'},
            400,
            id='wrong_current_candidate_status',
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        tst_headers,
        expected_status,
):
    operators_db = db.OperatorsRepo(web_context)

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=tst_headers,
    )

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
            conn, job_id=job_id, unique_operator_id=UID_TO_UOID[yandex_uid],
        )

    assert len(candidates) == 1

    candidate = candidates[0]

    status_updates = [
        json.loads(status_update)
        for status_update in candidate['status_updates']
    ]

    failed = constants.AdditionalShiftCandidateStatus.failed

    assert job['shifts_distributed'] == 0
    assert candidate['status'] == failed.value
    assert len(status_updates) > 1
    assert status_updates[-1]['status'] == failed.value
    assert status_updates[-1].get('reason') == tst_request.get('message')
