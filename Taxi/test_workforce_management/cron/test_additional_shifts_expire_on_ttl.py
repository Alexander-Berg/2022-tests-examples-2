# pylint: disable=redefined-outer-name
import pytest

from workforce_management.common import constants
from workforce_management.generated.cron import run_cron
from workforce_management.storage.postgresql import db


FIRST_JOB = {'id': 1, 'status': 0, 'message': None}
SECOND_JOB = {
    'id': 2,
    'status': 4,
    'message': constants.ADDITIONAL_SHIFT_EXPIRED_TTL_MESSAGE,
}
THIRD_JOB = {'id': 3, 'status': 2, 'message': None}
FIRST_JOB_CANDIDATES = [
    {'yandex_uid': 'uid1', 'status': 'picked'},
    {'yandex_uid': 'uid2', 'status': 'offered'},
]
SECOND_JOB_CANDIDATES = [
    {'yandex_uid': 'uid2', 'status': 'rejected'},
    {'yandex_uid': 'uid3', 'status': 'accepted'},
    {'yandex_uid': 'uid1', 'status': 'expired'},
    {'yandex_uid': 'uid4', 'status': 'expired'},
]
THIRD_JOB_CANDIDATES = [{'yandex_uid': 'uid2', 'status': 'accepted'}]


def prepare_job_data(raw_job):
    return {
        'id': raw_job['id'],
        'status': raw_job['status'],
        'message': raw_job['message'],
    }


def prepare_candidate_data(raw_candidate):
    return {
        'yandex_uid': raw_candidate['yandex_uid'],
        'status': raw_candidate['status'],
    }


@pytest.mark.now('2021-05-06T12:00:00.0')
@pytest.mark.parametrize(
    'expected_job, expected_job_candidates',
    [
        pytest.param(FIRST_JOB, FIRST_JOB_CANDIDATES, id='unexpired_ttl'),
        pytest.param(
            SECOND_JOB, SECOND_JOB_CANDIDATES, id='expired_ttl_job_unfinished',
        ),
        pytest.param(
            THIRD_JOB, THIRD_JOB_CANDIDATES, id='expired_ttl_job_finished',
        ),
    ],
)
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'additional_shifts_jobs.sql'],
)
async def test_additional_shifts_expire_on_ttl(
        cron_context, expected_job, expected_job_candidates,
):
    await run_cron.main(
        [
            'workforce_management.crontasks.additional_shifts_expire_on_ttl',
            '-t',
            '0',
        ],
    )

    operators_db = db.OperatorsRepo(cron_context)
    async with operators_db.master.acquire() as connection:
        job = await operators_db.get_additional_shifts_job_by_id(
            connection, job_id=expected_job['id'],
        )
    assert prepare_job_data(job) == expected_job

    async with operators_db.master.acquire() as connection:
        candidates = await operators_db.get_additional_shift_candidates(
            connection, job_id=job['id'],
        )
    candidates = [
        prepare_candidate_data(candidate) for candidate in candidates
    ]
    assert candidates == expected_job_candidates
