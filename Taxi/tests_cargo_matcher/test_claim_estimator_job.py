import datetime

import pytest


@pytest.fixture(name='run_task_once')
def _run_task_once(taxi_cargo_matcher, run_cargo_distlock_worker):
    async def _wrapper(task_name):
        return await run_cargo_distlock_worker(taxi_cargo_matcher, task_name)

    return _wrapper


@pytest.fixture(name='run_claim_estimator')
def _run_claim_estimator(run_task_once):
    async def _wrapper():
        return await run_task_once('claim-estimator')

    return _wrapper


NOW = datetime.datetime(2020, 1, 14, 16, 10)


def get_work_mode(mode):
    return {
        'enabled': mode,
        'chunk-size': 10,
        'pg-timeout-ms': 2000,
        'job-throttling-delay-ms': 1000,
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CARGO_MATCHER_CLAIM_ESTIMATOR_JOB_SETTINGS=get_work_mode(True),
)
async def test_worker(
        taxi_cargo_matcher, testpoint, run_claim_estimator, stq, mockserver,
):
    @mockserver.json_handler('/cargo-claims/v1/claims/mark/estimate-start')
    def _cargo_claims_mark(request):
        return {
            'id': '123',
            'status': 'estimating',
            'version': 2,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/cargo-claims/v1/claims/list/ready-for-estimate')
    def _cargo_claims_list(request):
        return {
            'claims': [
                {
                    'id': '123',
                    'status': 'new',
                    'version': 1,
                    'user_request_revision': '123',
                    'skip_client_notify': True,
                },
                {
                    'id': '234',
                    'status': 'new',
                    'version': 1,
                    'user_request_revision': '123',
                    'skip_client_notify': True,
                },
                {
                    'id': '345',
                    'status': 'new',
                    'version': 1,
                    'user_request_revision': '123',
                    'skip_client_notify': True,
                },
            ],
        }

    await run_claim_estimator()

    assert _cargo_claims_list.times_called >= 1  # sometimes == 2

    assert _cargo_claims_mark.times_called == 3
    assert stq.cargo_matcher_claim_estimating.times_called == 3

    for _ in range(3):
        stq_params = stq.cargo_matcher_claim_estimating.next_call()
        assert stq_params['queue'] == 'cargo_matcher_claim_estimating'
        assert stq_params['args'] == []
        assert stq_params['id'] in {'123', '234', '345'}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CARGO_MATCHER_CLAIM_ESTIMATOR_JOB_SETTINGS=get_work_mode(False),
)
async def test_worker_disabled(
        taxi_cargo_matcher, run_claim_estimator, stq, mockserver,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _mock_stq_agent_queue(request, queue_name):
        return {}

    await taxi_cargo_matcher.invalidate_caches()
    await run_claim_estimator()
    assert stq.cargo_matcher_claim_estimating.times_called == 0
