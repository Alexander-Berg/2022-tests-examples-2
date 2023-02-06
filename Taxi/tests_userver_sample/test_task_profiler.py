import pytest


@pytest.mark.config(
    USERVER_TASK_PROCESSOR_PROFILER_DEBUG={
        'main-task-processor': {
            'enabled': True,
            'execution-slice-threshold-us': 1,
        },
    },
)
async def test_profiling_smoketest(taxi_userver_sample):
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 200
