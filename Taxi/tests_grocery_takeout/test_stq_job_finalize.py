# pylint: disable=import-error

from metrics_aggregations import helpers as metrics_helpers
import more_itertools
import pytest

from . import consts
from . import models
from . import pytest_marks
from .job_pipeline import JobPipeline  # pylint: disable=C5521


@pytest.fixture(name='passport_takeout_uploaded')
def _passport_takeout_uploaded(testpoint):
    @testpoint('takeout_upload')
    async def _testpoint(data):
        pass

    def _inner():
        calls = [
            _testpoint.next_call()['data']
            for _ in range(_testpoint.times_called)
        ]

        return {call['file']: call['data'] for call in calls}

    return _inner


# Проверяем, что в базе job status == done
async def test_pg_job_done(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID

    job_pipeline.db.upsert(
        models.Job(job_id=job_id, status=models.JobStatus.init),
    )

    await job_pipeline.run_finalize(job_id=job_id)

    job = job_pipeline.db.load_job(job_id)

    assert job is not None
    assert job.status == models.JobStatus.done


async def test_pg_delete_request_done(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID

    job_pipeline.db.upsert(
        models.Job(
            job_id=job_id,
            status=models.JobStatus.init,
            job_type=models.JobType.delete,
        ),
        models.DeleteRequest(job_id=job_id, status=models.DeleteStatus.init),
    )

    await job_pipeline.run_finalize(job_id=job_id)

    request = job_pipeline.db.load_delete_request(job_id)
    assert request is not None
    assert request.status == models.DeleteStatus.done


# Проверяем upload в passport takeout
async def test_takeout_upload(
        job_pipeline: JobPipeline, passport_takeout, passport_takeout_uploaded,
):
    entities = [
        models.JobEntity(
            entity_type='type1', entity_id='1', entity_data={'q': 1},
        ),
        models.JobEntity(
            entity_type='type1', entity_id='2', entity_data={'q': 2},
        ),
        models.JobEntity(
            entity_type='type2', entity_id='1', entity_data={'q': 3},
        ),
        models.JobEntity(
            entity_type='type3', entity_id='1', entity_data={'q': 4},
        ),
        models.JobEntity(
            entity_type='type3', entity_id='2', entity_data={'q': 5},
        ),
    ]

    job_pipeline.db.upsert(models.Job(job_type=models.JobType.load), *entities)

    await job_pipeline.run_finalize()

    expected_result = more_itertools.map_reduce(
        entities,
        keyfunc=lambda x: f'{x.entity_type}.json',
        valuefunc=lambda x: {'id': x.entity_id, 'data': x.entity_data},
    )

    uploaded = passport_takeout_uploaded()
    assert uploaded == expected_result

    assert passport_takeout.upload.times_called == len(expected_result.keys())
    assert passport_takeout.upload_done.times_called == 1


# Проверяем increment метрики job_requests
@pytest_marks.JOB_TYPES
async def test_metric_job_request(
        job_pipeline: JobPipeline, taxi_grocery_takeout_monitor, job_type,
):
    sensor = 'grocery_takeout_job_requests'

    job_pipeline.db.upsert(models.Job(job_type=job_type))

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_takeout_monitor, sensor=sensor,
    ) as collector:
        await job_pipeline.run_finalize()

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': sensor,
        'job_type': job_type,
        'status': models.JobMetricStatus.done,
    }


# Проверяем increment метрики job_entities
@pytest_marks.JOB_TYPES
async def test_metric_job_entities(
        job_pipeline: JobPipeline, taxi_grocery_takeout_monitor, job_type,
):
    sensor = 'grocery_takeout_job_entities'
    entity_type = 'entity_type'

    entities = [
        models.JobEntity(
            entity_type=entity_type, entity_id='1', entity_data={},
        ),
        models.JobEntity(
            entity_type=entity_type, entity_id='2', entity_data={},
        ),
    ]

    job_pipeline.db.upsert(models.Job(job_type=job_type), *entities)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_takeout_monitor, sensor=sensor,
    ) as collector:
        await job_pipeline.run_finalize()

    metric = collector.get_single_collected_metric()
    assert metric.value == len(entities)
    assert metric.labels == {
        'sensor': sensor,
        'job_type': job_type,
        'entity_type': entity_type,
    }
