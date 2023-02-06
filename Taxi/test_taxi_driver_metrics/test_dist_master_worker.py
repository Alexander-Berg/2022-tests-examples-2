# pylint: disable=protected-access, invalid-name, import-only-modules
import pytest


@pytest.mark.config(
    DRIVER_METRICS_EVENT_PROCESSING_PARAMS={
        'events_batch_size': 3,
        'master_worker_interval_msec': 1,
        'max_delay_for_worker_spawn_msec': 50,
        'min_delay_for_worker_spawn_msec': 50,
        'workers_num': 3,
        'mode': 'distlock',
    },
)
async def test_integration(web_context, stq, mockserver):
    @mockserver.json_handler('/distlocks/v1/locks/acquire/')
    def _acquire(request):
        assert request.json['namespace'] == 'metrics-processing'
        assert request.json['name'] == 'metrics-distlock_driver-metrics'
        assert request.json['ttl'] == 1  # ceil 0.001*x to 1
        return {
            'status': 'acquired',
            'namespace': 'metrics-processing',
            'name': 'metrics-distlock_driver-metrics',
        }

    @mockserver.json_handler('/distlocks/v1/locks/prolong/')
    def _prolong(request):
        assert request.json['namespace'] == 'metrics-processing'
        assert request.json['name'] == 'metrics-distlock_driver-metrics'
        assert request.json['ttl'] == 1  # ceil 0.001*x to 1
        return {
            'status': 'acquired',
            'namespace': 'metrics-processing',
            'name': 'metrics-distlock_driver-metrics',
        }

    dl = web_context.dist_master_worker._impl
    assert not dl.is_emergency_mode()
    assert not dl._task
    dl.start()
    await _prolong.wait_call()
    assert dl._task
    assert dl.has_lock
    assert _acquire.times_called == 1
    assert stq.driver_metrics_processing.times_called >= 3
    data = stq.driver_metrics_processing.next_call()
    assert data['id'] == 'slave/0/3'
