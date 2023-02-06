# pylint: disable=import-error
import datetime
import uuid

from grocery_mocks.utils import helpers as mock_helpers
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import models
from . import pytest_marks
from .job_pipeline import JobPipeline  # pylint: disable=C5521


@pytest.fixture(name='grocery_takeout_delete')
def _grocery_takeout_delete(taxi_grocery_takeout):
    async def _inner(
            request_id=consts.JOB_ID,
            yandex_uids=None,
            date_request_at: datetime.datetime = None,
            status_code=200,
            **kwargs,
    ):
        if yandex_uids is None:
            yandex_uids = [consts.YANDEX_UID]
        if date_request_at is None:
            date_request_at = datetime.datetime.now().astimezone()
        yandex_uids_request = [
            dict(uid=uid, is_portal=True) for uid in yandex_uids
        ]

        response = await taxi_grocery_takeout.post(
            '/takeout/v2/delete',
            json={
                'request_id': request_id,
                'date_request_at': date_request_at.isoformat(),
                'yandex_uids': yandex_uids_request,
                **kwargs,
            },
        )

        assert response.status_code == status_code

    return _inner


# Проверяем создание job'ы на delete.
async def test_job_start(grocery_takeout_delete, job_pipeline: JobPipeline):
    request_id = consts.JOB_ID
    yandex_uid = consts.YANDEX_UID
    date_request_at = consts.NOW_DT

    await grocery_takeout_delete(
        request_id, yandex_uids=[yandex_uid], date_request_at=date_request_at,
    )

    stq_events = job_pipeline.stq_job_start.events()
    stq_events.check_event(
        job_id=request_id,
        job_type=models.JobType.delete,
        till_dt=date_request_at.isoformat(),
        yandex_uids=[yandex_uid],
    )


# Проверяем создание job'ы c кастомным eta.
@pytest_marks.NOW
async def test_job_eta(
        grocery_takeout_delete,
        grocery_takeout_configs,
        job_pipeline: JobPipeline,
):
    start_eta = 1

    expected_job_eta = consts.NOW_DT + datetime.timedelta(hours=start_eta)

    grocery_takeout_configs.settings(job_start_eta_hours=start_eta)

    await grocery_takeout_delete()

    stq_events = job_pipeline.stq_job_start.events()
    stq_events.check_event(times_called=1, task_eta=expected_job_eta)


# Проверяем создание запроса в базе.
async def test_pg_delete_request(grocery_takeout_delete, grocery_takeout_db):
    request_id = consts.JOB_ID
    yandex_uids = [str(uuid.uuid4()), str(uuid.uuid4())]
    user_ids = [str(uuid.uuid4())]
    phone_ids = [str(uuid.uuid4())]
    personal_phone_ids = [str(uuid.uuid4())]
    personal_email_ids = [str(uuid.uuid4())]

    await grocery_takeout_delete(
        request_id=request_id,
        yandex_uids=yandex_uids,
        date_request_at=consts.NOW_DT,
        user_ids=user_ids,
        phone_ids=phone_ids,
        personal_phone_ids=personal_phone_ids,
        personal_email_ids=personal_email_ids,
    )

    request_pg = grocery_takeout_db.load_delete_request(request_id)
    assert request_pg == models.DeleteRequest(
        job_id=request_id,
        yandex_uids=yandex_uids,
        created=consts.NOW_DT,
        user_ids=user_ids,
        phone_ids=phone_ids,
        personal_phone_ids=personal_phone_ids,
        personal_email_ids=personal_email_ids,
    )


# Проверяем сохранение anonym_id.
async def test_store_anonym_id(grocery_takeout_delete, grocery_sensitive):
    request_id = consts.JOB_ID

    grocery_sensitive.store.check(
        request_id=request_id,
        objects=[
            dict(
                entity_id=mock_helpers.NotNone,
                entity_type='anonym_id',
                data={},
            ),
        ],
    )

    await grocery_takeout_delete(request_id=request_id)

    assert grocery_sensitive.store.times_called == 1


# Проверяем increment метрики job_requests
async def test_metric_job_request(
        grocery_takeout_delete, taxi_grocery_takeout_monitor,
):
    sensor = 'grocery_takeout_job_requests'

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_takeout_monitor, sensor=sensor,
    ) as collector:
        await grocery_takeout_delete()

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': sensor,
        'job_type': models.JobType.delete,
        'status': models.JobMetricStatus.requested,
    }
