# pylint: disable=import-error

from metrics_aggregations import helpers as metrics_helpers

from . import consts
from . import entity_graphs
from . import models
from . import pytest_marks
from .job_pipeline import JobPipeline  # pylint: disable=C5521


# Проверяем, что создалась запись в базе.
@pytest_marks.JOB_TYPES
async def test_pg_job(job_pipeline: JobPipeline, job_type):
    job_id = consts.JOB_ID
    anonym_id = consts.ANONYM_ID

    job_pipeline.set_graph(entity_graphs.DEFAULT)

    await job_pipeline.run_start(
        job_id=job_id,
        job_type=job_type,
        till_dt=consts.NOW,
        anonym_id=anonym_id,
    )

    job = job_pipeline.db.load_job(job_id)

    assert job is not None
    assert job.job_type == job_type
    assert job.till_dt == consts.NOW_DT
    assert job.graph == entity_graphs.DEFAULT
    assert job.status == models.JobStatus.init
    assert job.anonym_id == anonym_id


# Проверяем кейс, когда по какой-то причине запись в базе уже есть.
async def test_retry_job(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID

    current_job = models.Job(job_id)
    job_pipeline.db.upsert(current_job)

    await job_pipeline.run_start(job_id=job_id)

    job = job_pipeline.db.load_job(job_id)

    assert job == current_job


# Проверяем создание записи в базе entity_ids для сущности yandex_uid
async def test_pg_ids_yandex_uid(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    entity_type = 'yandex_uid'
    yandex_uids = ['uid1', 'uid2']

    expected_task = models.JobEntityTask(
        job_id=job_id, entity_type=entity_type, entity_ids=yandex_uids,
    )

    await job_pipeline.run_start(job_id=job_id, yandex_uids=yandex_uids)

    task = job_pipeline.db.load_job_entity_task(job_id, entity_type)

    assert task == expected_task


# Проверяем старт таски для сущности yandex_uid
async def test_run_entity_post_load(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    entity_type = 'yandex_uid'

    await job_pipeline.run_start(job_id=job_id)

    stq_events = job_pipeline.stq_entity_post_load.events()
    stq_events.check_event(
        task_id=f'{job_id}:{entity_type}',
        times_called=1,
        job_id=job_id,
        entity_type=entity_type,
    )


# Проверяем increment метрики job_requests
@pytest_marks.JOB_TYPES
async def test_metric_job_request(
        job_pipeline: JobPipeline, taxi_grocery_takeout_monitor, job_type,
):
    sensor = 'grocery_takeout_job_requests'

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_takeout_monitor, sensor=sensor,
    ) as collector:
        await job_pipeline.run_start(job_type=job_type)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': sensor,
        'job_type': job_type,
        'status': models.JobMetricStatus.started,
    }
