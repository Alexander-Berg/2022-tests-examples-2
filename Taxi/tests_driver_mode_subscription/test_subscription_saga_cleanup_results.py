from typing import List

import pytest

from tests_driver_mode_subscription import saga_tools


@pytest.mark.parametrize(
    'expected_task_call, expected_results_count, expected_results',
    (
        pytest.param(
            False,
            7,
            [
                (1, 'executed'),
                (2, 'compensated'),
                (3, 'executed'),
                (4, 'executed'),
                (5, 'compensated'),
                (6, 'executed'),
                (7, 'executed'),
            ],
            marks=[
                pytest.mark.config(DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={}),
            ],
            id='no settings',
        ),
        pytest.param(
            True,
            1,
            [(7, 'executed')],
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={
                        'saga_results_ttl_m': 60,
                        'saga_results_cleanup_chunk_size': 20,
                    },
                ),
            ],
            id='delete only outdated rows',
        ),
        pytest.param(
            True,
            5,
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={
                        'saga_results_ttl_m': 60,
                        'saga_results_cleanup_chunk_size': 2,
                    },
                ),
            ],
            id='delete not more than chunk_size',
        ),
    ),
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
@pytest.mark.pgsql('driver_mode_subscription', files=['saga_results.sql'])
async def test_periodic_task_runs_periodically(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        expected_results_count: int,
        expected_task_call: bool,
        expected_results: List[tuple],
):
    @testpoint('saga-results-cleanup')
    def worker_testpoint(data):
        pass

    @testpoint('saga-results-cleanup-executed')
    def task_testpoint(data):
        pass

    async with taxi_driver_mode_subscription.spawn_task(
            'distlock/saga-results-cleanup',
    ):
        await worker_testpoint.wait_call()

    if expected_task_call:
        assert task_testpoint.times_called == 1
        actual_results = saga_tools.get_saga_statuses(pgsql)
        assert len(actual_results) == expected_results_count
        if expected_results:
            assert actual_results == expected_results
    else:
        assert task_testpoint.times_called == 0
