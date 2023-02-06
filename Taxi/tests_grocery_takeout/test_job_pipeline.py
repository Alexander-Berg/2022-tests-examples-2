import more_itertools
import pytest

from . import consts
from . import entity_graphs
from . import models
from .job_pipeline import JobPipeline  # pylint: disable=C5521

YANDEX_UID_1 = 'uid1'
YANDEX_UID_2 = 'uid2'
YANDEX_UID_3 = 'uid3'

YANDEX_UID_TO_ORDER_ID = {
    YANDEX_UID_1: ['order_1'],
    YANDEX_UID_2: ['order_2', 'order_3', 'order_4'],
    YANDEX_UID_3: ['order_5'],
}


@pytest.fixture(autouse=True)
def default_entity_graph(grocery_takeout_configs):
    grocery_takeout_configs.entity_graph(entity_graphs.DEFAULT)


@pytest.fixture(autouse=True)
def default_mock_entities(mock_entities):
    mock_entities.orders.mock_load_ids(
        mapping=YANDEX_UID_TO_ORDER_ID, id_name='yandex_uid', limit=2,
    )

    order_ids = more_itertools.flatten(YANDEX_UID_TO_ORDER_ID.values())
    mock_entities.orders.mock_load_by_id(
        mapping={order_id: [{'id': order_id}] for order_id in order_ids},
        id_name='order_id',
    )

    mock_entities.orders.mock_delete_by_id(id_name='order_id')


# Проверяем полный happy path job'ы на load.
async def test_basic_load(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    job_type = models.JobType.load
    yandex_uids = [YANDEX_UID_1, YANDEX_UID_2]

    # expect
    order_ids = []
    for uid in yandex_uids:
        order_ids.extend(YANDEX_UID_TO_ORDER_ID[uid])

    await job_pipeline.run_start(job_type=job_type, yandex_uids=yandex_uids)

    await job_pipeline.process()

    yandex_uids_task = job_pipeline.db.load_job_entity_task(
        job_id, entity_type='yandex_uid',
    )
    assert yandex_uids_task is not None
    assert yandex_uids_task.entity_ids == yandex_uids

    orders_ids_task = job_pipeline.db.load_job_entity_task(
        job_id, entity_type='orders',
    )
    assert orders_ids_task is not None
    assert orders_ids_task.entity_ids == order_ids

    orders_objs = job_pipeline.db.load_job_entities(
        job_id, entity_type='orders',
    )
    assert len(orders_objs) == len(order_ids)

    job = job_pipeline.db.load_job(job_id)
    assert job is not None
    assert job.status == models.JobStatus.done


# Проверяем полный happy path job'ы на delete.
async def test_basic_delete(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    job_type = models.JobType.delete
    yandex_uids = [YANDEX_UID_1, YANDEX_UID_2]

    await job_pipeline.run_start(
        job_type=job_type, yandex_uids=yandex_uids, anonym_id=consts.ANONYM_ID,
    )

    await job_pipeline.process()

    job = job_pipeline.db.load_job(job_id)
    assert job is not None
    assert job.status == models.JobStatus.done
