# pylint: disable=protected-access, invalid-name, import-only-modules
import asyncio
import datetime

import pytest

from metrics_processing_distlocks import DistributedLockBase
from metrics_processing_distlocks import DistributedMasterWorker


class FakeDistLock(DistributedLockBase):
    owner = None
    prolong_call = 0

    async def acquire(self, ttl_sec: float) -> bool:
        if FakeDistLock.owner is None:
            FakeDistLock.owner = self.owner
        return FakeDistLock.owner == self.owner

    async def prolong(self, ttl_sec: float) -> bool:
        self.prolong_call += 1
        return FakeDistLock.owner == self.owner

    async def release(self) -> bool:
        if FakeDistLock.owner == self.owner:
            FakeDistLock.owner = None
        return True


@pytest.mark.config(
    RIDER_METRICS_EVENTS_PROCESSING_PARAMS={
        'events_batch_size': 3,
        'master_worker_interval_msec': 0,
        'max_delay_for_worker_spawn_msec': 50,
        'min_delay_for_worker_spawn_msec': 50,
        'workers_num': 3,
    },
)
async def test_breath(web_context, stq):
    fds = FakeDistLock('key')
    dl = DistributedMasterWorker(
        web_context,
        fds,
        'rider_metrics_processing',
        'RIDER_METRICS_EVENTS_PROCESSING_PARAMS',
    )
    now = datetime.datetime.now()
    assert not dl.has_lock
    assert not dl._task

    await dl._do(now)
    assert dl.has_lock
    assert not fds.prolong_call

    fds2 = FakeDistLock('key', owner='an')
    dl2 = DistributedMasterWorker(
        web_context,
        fds2,
        'rider_metrics_processing',
        'RIDER_METRICS_EVENTS_PROCESSING_PARAMS',
    )
    assert not dl2.has_lock
    assert not dl2._task

    await dl2._do(now)
    assert not dl2.has_lock
    assert fds2.prolong_call == 0

    await dl.release()
    # wait for lock expiration
    await asyncio.sleep(0.003)
    assert not dl.has_lock
    await dl2._do(now)
    await dl2._do(now)
    assert dl2.has_lock
    assert not dl.is_emergency_mode()
    assert not dl2.is_emergency_mode()
    assert fds2.prolong_call == 1
    assert stq.rider_metrics_processing.times_called == 9


@pytest.mark.config(
    RIDER_METRICS_EVENTS_PROCESSING_PARAMS={
        'events_batch_size': 3,
        'master_worker_interval_msec': 0,
        'max_delay_for_worker_spawn_msec': 50,
        'min_delay_for_worker_spawn_msec': 50,
        'workers_num': 3,
        'dist_master_worker_emergency_multiplier': 1,
        'dist_master_worker_emergency_failure_threshold': 2,
    },
)
async def test_emergency(web_context, stq):
    dl = DistributedMasterWorker(
        web_context,
        # pass Base to raise an exception on any call
        DistributedLockBase('key'),
        'rider_metrics_processing',
        'RIDER_METRICS_EVENTS_PROCESSING_PARAMS',
    )
    now = datetime.datetime.now()

    await dl._do(now)
    assert not dl.is_emergency_mode()
    assert stq.rider_metrics_processing.times_called == 0
    await dl._do(now)
    assert dl.is_emergency_mode()
    assert stq.rider_metrics_processing.times_called == 3


@pytest.mark.config(
    RIDER_METRICS_EVENTS_PROCESSING_PARAMS={
        'events_batch_size': 3,
        'master_worker_interval_msec': 0,
        'max_delay_for_worker_spawn_msec': 50,
        'min_delay_for_worker_spawn_msec': 50,
        'workers_num': 3,
        'dist_master_worker_emergency_multiplier': 1,
        'dist_master_worker_emergency_failure_threshold': 2,
        'dist_master_worker_emergency_mode_enabled': True,
    },
)
async def test_manual_emergency(web_context, stq):
    dl = DistributedMasterWorker(
        web_context,
        # pass Base to raise an exception on any call
        DistributedLockBase('key'),
        'rider_metrics_processing',
        'RIDER_METRICS_EVENTS_PROCESSING_PARAMS',
    )
    now = datetime.datetime.now()

    await dl._do(now)
    assert dl.is_emergency_mode()
    assert stq.rider_metrics_processing.times_called == 3


@pytest.mark.config(
    RIDER_METRICS_EVENTS_PROCESSING_PARAMS={
        'events_batch_size': 3,
        'master_worker_interval_msec': 1,
        'max_delay_for_worker_spawn_msec': 50,
        'min_delay_for_worker_spawn_msec': 50,
        'workers_num': 3,
        'mode': 'distlock',
    },
)
async def test_integration(web_context, stq, mockserver):
    dl = web_context.dist_master_worker._impl

    @mockserver.json_handler('/distlocks/v1/locks/acquire/')
    def _acquire(request):
        assert request.json['namespace'] == 'metrics-processing'
        assert request.json['name'] == 'metrics-distlock_rider-metrics'
        assert request.json['ttl'] == 1  # ceil 0.001*x to 1
        return {
            'status': 'acquired',
            'namespace': 'metrics-processing',
            'name': 'metrics-distlock_rider-metrics',
        }

    @mockserver.json_handler('/distlocks/v1/locks/prolong/')
    def _prolong(request):
        assert request.json['namespace'] == 'metrics-processing'
        assert request.json['name'] == 'metrics-distlock_rider-metrics'
        assert request.json['ttl'] == 1  # ceil 0.001*x to 1
        return {
            'status': 'acquired',
            'namespace': 'metrics-processing',
            'name': 'metrics-distlock_rider-metrics',
        }

    dl = web_context.dist_master_worker._impl
    assert not dl.is_emergency_mode()
    assert not dl._task
    dl.start()
    cnt = 10
    while not dl.has_lock and cnt > 0:
        cnt -= 1
        await asyncio.sleep(0.3)
    assert cnt >= 0
    assert dl._task
    assert dl.has_lock
    assert _acquire.times_called == 1
    assert _prolong.times_called >= 1
    assert stq.rider_metrics_processing.times_called >= 3
