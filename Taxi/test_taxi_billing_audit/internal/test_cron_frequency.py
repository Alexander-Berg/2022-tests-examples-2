import asyncio
import datetime as dt
import typing

import pytest

from taxi.maintenance import run

from taxi_billing_audit.internal import cron_frequency


@cron_frequency.limit_runs
async def do_stuff_successful(
        task_context: run.StuffContext,
        loop: asyncio.AbstractEventLoop,
        *,
        log_extra: typing.Optional[dict] = None,
) -> None:
    pass


@cron_frequency.limit_runs
async def do_stuff_error(
        task_context: run.StuffContext,
        loop: asyncio.AbstractEventLoop,
        *,
        log_extra: typing.Optional[dict] = None,
) -> None:
    raise Exception


@pytest.mark.parametrize(
    'stuff_func, expected_acquire_calls, expected_release_calls',
    [
        pytest.param(
            do_stuff_successful,
            0,
            0,
            marks=pytest.mark.config(
                BILLING_AUDIT_LIMIT_CRON_FREQUENCY={
                    '__default__': {'enabled': False},
                },
            ),
        ),
        pytest.param(
            do_stuff_error,
            0,
            0,
            marks=pytest.mark.config(
                BILLING_AUDIT_LIMIT_CRON_FREQUENCY={
                    '__default__': {'enabled': False},
                },
            ),
        ),
        pytest.param(
            do_stuff_successful,
            1,
            0,
            marks=pytest.mark.config(
                BILLING_AUDIT_LIMIT_CRON_FREQUENCY={
                    '__default__': {'enabled': False},
                    'test_taxi_billing_audit-internal-test_cron_frequency': {
                        'enabled': True,
                        'offset': {'hours': 1},
                    },
                },
            ),
        ),
        pytest.param(
            do_stuff_error,
            1,
            1,
            marks=pytest.mark.config(
                BILLING_AUDIT_LIMIT_CRON_FREQUENCY={
                    '__default__': {'enabled': False},
                    'test_taxi_billing_audit-internal-test_cron_frequency': {
                        'enabled': True,
                        'offset': {'hours': 1},
                    },
                },
            ),
        ),
    ],
)
async def test_start_of_week(
        stuff_func,
        expected_acquire_calls,
        expected_release_calls,
        patched_secdist,
        cron_context,
        patch,
):
    @patch('taxi.distlock.service.DistributedLock.acquire')
    async def _acquire(self):
        return True

    @patch('taxi.distlock.service.DistributedLock.release')
    async def _release(self):
        return True

    stuff_context = run.StuffContext(
        lock=None,
        task_id='task_id',
        start_time=dt.datetime(2020, 9, 14, 0, 0, 0, 0),
        data=cron_context,
    )
    try:
        await stuff_func(
            task_context=stuff_context, loop=asyncio.get_running_loop(),
        )
    except:  # noqa pylint: disable=bare-except
        pass

    assert len(_acquire.calls) == expected_acquire_calls
    assert len(_release.calls) == expected_release_calls
