# pylint: disable=import-error
import datetime

from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import models
from . import pytest_marks
from .job_pipeline import JobPipeline  # pylint: disable=C5521


@pytest.fixture(name='grocery_takeout_create')
def _grocery_takeout_create(taxi_grocery_takeout):
    async def _inner(
            request_id=consts.JOB_ID,
            yandex_uid=consts.YANDEX_UID,
            status_code=200,
    ):
        response = await taxi_grocery_takeout.post(
            '/takeout/v1/create',
            data=f'job_id={request_id}&uid={yandex_uid}',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )

        assert response.status_code == status_code

    return _inner


# Проверяем создание job'ы на load.
@pytest_marks.NOW
async def test_job_start(grocery_takeout_create, job_pipeline: JobPipeline):
    request_id = consts.JOB_ID
    yandex_uid = consts.YANDEX_UID

    await grocery_takeout_create(request_id, yandex_uid=yandex_uid)

    stq_events = job_pipeline.stq_job_start.events()
    stq_events.check_event(
        task_id=request_id,
        job_id=request_id,
        job_type=models.JobType.load,
        till_dt=consts.NOW,
        yandex_uids=[yandex_uid],
        anonym_id=None,
    )


# Проверяем создание job'ы c кастомным eta.
@pytest_marks.NOW
async def test_job_eta(
        grocery_takeout_create,
        grocery_takeout_configs,
        job_pipeline: JobPipeline,
):
    start_eta = 1

    expected_job_eta = consts.NOW_DT + datetime.timedelta(hours=start_eta)

    grocery_takeout_configs.settings(job_start_eta_hours=start_eta)

    await grocery_takeout_create()

    stq_events = job_pipeline.stq_job_start.events()
    stq_events.check_event(times_called=1, task_eta=expected_job_eta)


# Проверяем increment метрики job_requests
async def test_metric_job_request(
        grocery_takeout_create, taxi_grocery_takeout_monitor,
):
    sensor = 'grocery_takeout_job_requests'

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_takeout_monitor, sensor=sensor,
    ) as collector:
        await grocery_takeout_create()

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': sensor,
        'job_type': models.JobType.load,
        'status': models.JobMetricStatus.requested,
    }
