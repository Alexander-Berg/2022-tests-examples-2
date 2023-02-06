import pytest

from . import consts
from . import entity_graphs
from . import models
from .job_pipeline import JobPipeline  # pylint: disable=C5521


DEFAULT_GRAPH = entity_graphs.DEFAULT

PARENT_ENTITY = DEFAULT_GRAPH[0]
ENTITY = PARENT_ENTITY.children[0]

ENTITY_TYPE = ENTITY.entity_type
PARENT_ENTITY_TYPE = PARENT_ENTITY.entity_type

IDS_LIMIT = 2
PARENT_ID_1 = '111'
PARENT_ID_2 = '222'
IDS_BY_PARENT_ID = {PARENT_ID_1: ['1', '2'], PARENT_ID_2: ['3', '4', '5']}


@pytest.fixture(autouse=True)
def mock_orders_ids(mock_entities):
    mock_entities.orders.mock_load_ids(
        IDS_BY_PARENT_ID, id_name=PARENT_ENTITY.id_name, limit=IDS_LIMIT,
    )


# Проверяем вызов получения идентификаторов.
async def test_load_ids(mock_entities, job_pipeline: JobPipeline):
    id_name = PARENT_ENTITY.id_name
    job = models.Job(graph=DEFAULT_GRAPH)

    job_pipeline.db.upsert(
        job,
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=[PARENT_ID_1],
        ),
    )

    expected_request = {
        id_name: PARENT_ID_1,
        'till_dt': job.till_dt.isoformat(),
        'purpose': job.job_type,
    }

    mock_entities.orders.load_ids.check_body(expected_request)

    await job_pipeline.run_entity_load_ids(
        entity_type=ENTITY_TYPE, request_entity_type=PARENT_ENTITY_TYPE,
    )

    assert mock_entities.orders.load_ids.times_called == 1


# Проверяем добавление id в базу на первой итерации.
async def test_pg_append(job_pipeline: JobPipeline):
    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=[PARENT_ID_1],
        ),
        models.JobEntityTask(entity_type=ENTITY_TYPE, entity_ids=[]),
    )

    await job_pipeline.run_entity_load_ids(
        entity_type=ENTITY_TYPE, request_entity_type=PARENT_ENTITY_TYPE,
    )

    task = job_pipeline.db.load_job_entity_task(consts.JOB_ID, ENTITY_TYPE)
    assert task is not None
    assert task.entity_ids == IDS_BY_PARENT_ID[PARENT_ID_1]
    assert task.entity_ids_version == 1


# Проверяем кейс, когда загрузили часть id на первой итерации и проверяем,
# что вторая итерация догрузит остаток.
async def test_pg_second_append(job_pipeline: JobPipeline):
    offset = IDS_LIMIT

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=[PARENT_ID_2],
        ),
        models.JobEntityTask(
            entity_type=ENTITY_TYPE,
            entity_ids=IDS_BY_PARENT_ID[PARENT_ID_2][0:offset],
        ),
    )

    await job_pipeline.run_entity_load_ids(
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        iteration_number=1,
        cursor=dict(offset=offset),
    )

    task = job_pipeline.db.load_job_entity_task(consts.JOB_ID, ENTITY_TYPE)
    assert task is not None
    assert task.entity_ids == IDS_BY_PARENT_ID[PARENT_ID_2]
    assert task.entity_ids_version == 2


# Проверяем запуск следующей итерации загрузки списка id.
@pytest.mark.parametrize(
    'kwargs',
    [
        dict(
            parent_ids=[PARENT_ID_1],
            iteration_number=0,
            expected=dict(
                iteration_number=1, request_entity_index=1, cursor=None,
            ),
        ),
        dict(
            parent_ids=[PARENT_ID_2],
            iteration_number=0,
            expected=dict(
                iteration_number=1,
                request_entity_index=0,
                cursor=dict(offset=IDS_LIMIT),
            ),
        ),
        dict(
            parent_ids=[PARENT_ID_2],
            iteration_number=1,
            cursor=dict(offset=IDS_LIMIT),
            expected=dict(
                iteration_number=2, request_entity_index=1, cursor=None,
            ),
        ),
    ],
)
async def test_run_next_iter(job_pipeline: JobPipeline, kwargs):
    iteration_number = kwargs['iteration_number']

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=kwargs['parent_ids'],
        ),
    )

    await job_pipeline.run_entity_load_ids(
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        request_entity_index=0,
        iteration_number=iteration_number,
        cursor=kwargs.get('cursor'),
    )

    stq_events = job_pipeline.stq_entity_load_ids.events()
    stq_events.check_event(
        task_id=f'{consts.JOB_ID}:{ENTITY_TYPE}:{iteration_number+1}',
        job_id=consts.JOB_ID,
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        **kwargs.get('expected', {}),
    )


# Проверяем, что если request_entity_id по индексу не найден,
# то выгрузка индексов завершена и запускается таска на выгрузку сущностей.
async def test_run_load_by_id(job_pipeline: JobPipeline):
    entity_ids = ['1', '2']

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=entity_ids,
        ),
    )

    await job_pipeline.run_entity_load_ids(
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        request_entity_index=len(entity_ids),
        iteration_number=len(entity_ids),
    )

    stq_events = job_pipeline.stq_entity_load_by_id.events()
    stq_events.check_event(
        task_id=f'{consts.JOB_ID}:{ENTITY_TYPE}:0',
        job_id=consts.JOB_ID,
        entity_type=ENTITY_TYPE,
        request_entity_type=ENTITY_TYPE,
        request_entity_index=0,
    )

    stq_events = job_pipeline.stq_entity_load_ids.events()
    assert not stq_events
