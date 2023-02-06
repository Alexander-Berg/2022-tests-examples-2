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

PARENT_IDS = ['111', '222']


# Проверяем вызов удаления сущности.
async def test_delete(mock_entities, job_pipeline: JobPipeline):
    request_entity_index = 0
    id_name = PARENT_ENTITY.id_name
    job = models.Job(graph=DEFAULT_GRAPH)

    job_pipeline.db.upsert(
        job,
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=PARENT_IDS,
        ),
    )

    expected_request = {
        id_name: PARENT_IDS[request_entity_index],
        'till_dt': job.till_dt.isoformat(),
        'anonym_id': job.anonym_id,
    }

    mock_entities.orders.mock_delete_by_id(id_name=id_name)
    mock_entities.orders.delete_by_id.check_body(expected_request)

    await job_pipeline.run_entity_delete_by_id(
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        request_entity_index=request_entity_index,
    )

    assert mock_entities.orders.delete_by_id.times_called == 1


# Проверяем запуск следующей итерации.
async def test_run_next_iter(mock_entities, job_pipeline: JobPipeline):
    request_entity_index = 0

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=PARENT_IDS,
        ),
    )

    mock_entities.orders.mock_delete_by_id(id_name=PARENT_ENTITY.id_name)

    await job_pipeline.run_entity_delete_by_id(
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        request_entity_index=request_entity_index,
    )

    stq_events = job_pipeline.stq_entity_delete_by_id.events()
    stq_events.check_event(
        task_id=f'{consts.JOB_ID}:{ENTITY_TYPE}:{request_entity_index + 1}',
        job_id=consts.JOB_ID,
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        request_entity_index=request_entity_index + 1,
    )


# Проверяем запуск stq job_finalize
async def test_run_finalize(job_pipeline: JobPipeline):
    parent_ids = PARENT_IDS

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE,
            entity_ids=parent_ids,
            status=models.JobTaskStatus.done,
        ),
        models.JobEntityTask(entity_type=ENTITY_TYPE),
    )

    await job_pipeline.run_entity_delete_by_id(
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        request_entity_index=len(parent_ids),
    )

    stq_events = job_pipeline.stq_job_finalize.events()
    stq_events.check_event(task_id=f'{consts.JOB_ID}', job_id=consts.JOB_ID)


# Проверяем использование экспа grocery_takeout_entity_response_validator.
@pytest.mark.parametrize('status_code', [404])
async def test_response_validator(
        mock_entities,
        experiments3,
        grocery_takeout_configs,
        job_pipeline: JobPipeline,
        status_code,
):
    entity_type = ENTITY_TYPE
    request_entity_type = PARENT_ENTITY_TYPE
    request_entity_index = 0
    parent_ids = PARENT_IDS

    grocery_takeout_configs.entity_response_validator(is_valid=False)

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=parent_ids,
        ),
    )

    mock_entities.orders.mock_delete_by_id(
        id_name=PARENT_ENTITY.id_name, status_code=status_code,
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_takeout_entity_response_validator',
    )

    await job_pipeline.run_entity_delete_by_id(
        entity_type=entity_type,
        request_entity_type=request_entity_type,
        request_entity_index=request_entity_index,
        expect_fail=True,
    )

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs
    assert (
        exp3_kwargs['consumer'] == 'grocery-takeout/entity-response-validator'
    )
    assert exp3_kwargs['handle'] == 'delete_by_id'
    assert exp3_kwargs['entity_relation'] == ENTITY.relation
    assert exp3_kwargs['entity_type'] == entity_type
    assert exp3_kwargs['request_entity_type'] == request_entity_type
    assert exp3_kwargs['request_entity_id'] == parent_ids[request_entity_index]
    assert exp3_kwargs['response_code'] == status_code
    assert exp3_kwargs['response_len'] == 0


# Проверяем перепостановку задачи, если одна из сущностей еще in progress.
async def test_reschedule_delete_after(job_pipeline: JobPipeline):
    entity_type = 'fav-goods'
    dep_entity_type = 'orders'
    task_id = 'task_id'

    graph = models.EntityGraph(
        models.EntityNode(
            entity_type=entity_type, delete_after=[dep_entity_type],
        ),
        models.EntityNode(entity_type=dep_entity_type),
    )

    job_pipeline.db.upsert(
        models.Job(graph=graph),
        models.JobEntityTask(entity_type=entity_type),
        models.JobEntityTask(entity_type=dep_entity_type),
    )

    await job_pipeline.run_entity_delete_by_id(
        task_id=task_id,
        entity_type=entity_type,
        request_entity_type=entity_type,
    )

    stq_events = job_pipeline.stq_entity_delete_by_id.events()
    stq_events.check_event(task_id=task_id, reschedule=True)
