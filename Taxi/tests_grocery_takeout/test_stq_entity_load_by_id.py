import pytest

from . import consts
from . import entity_graphs
from . import models
from . import pytest_marks
from .job_pipeline import JobPipeline  # pylint: disable=C5521

DEFAULT_GRAPH = entity_graphs.DEFAULT

PARENT_ENTITY = DEFAULT_GRAPH[0]
ENTITY = PARENT_ENTITY.children[0]

ENTITY_TYPE = ENTITY.entity_type
PARENT_ENTITY_TYPE = PARENT_ENTITY.entity_type

DEFAULT_ENTITY_DATA = {'field1': 'some string', 'field2': 123}

DEFAULT_SENSITIVE_DATA = {'personal_phone_id': 'personal_phone_id'}

PARENT_ID = '111'

ENTITY_OBJECT_1: dict = {
    'id': '1',
    'data': DEFAULT_ENTITY_DATA,
    'sensitive_data': DEFAULT_SENSITIVE_DATA,
}
ENTITY_OBJECT_2: dict = {'id': '2', 'data': {}}


# Проверяем вызов выгрузки сущности.
async def test_load(mock_entities, job_pipeline: JobPipeline):
    id_name = PARENT_ENTITY.id_name
    job = models.Job(graph=DEFAULT_GRAPH)

    job_pipeline.db.upsert(
        job,
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=[PARENT_ID],
        ),
    )

    expected_request = {
        id_name: PARENT_ID,
        'till_dt': job.till_dt.isoformat(),
        'purpose': job.job_type,
    }

    mock_entities.orders.mock_load_by_id(id_name=id_name)
    mock_entities.orders.delete_by_id.check_body(expected_request)

    await job_pipeline.run_entity_load_by_id(
        entity_type=ENTITY_TYPE, request_entity_type=PARENT_ENTITY_TYPE,
    )

    assert mock_entities.orders.load_by_id.times_called == 1


# Проверяем запуск следующей итерации.
async def test_run_next_iter(mock_entities, job_pipeline: JobPipeline):
    request_entity_index = 0

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=[PARENT_ID],
        ),
    )

    mock_entities.orders.mock_load_by_id(id_name=PARENT_ENTITY.id_name)

    await job_pipeline.run_entity_load_by_id(
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        request_entity_index=request_entity_index,
    )

    stq_events = job_pipeline.stq_entity_load_by_id.events()
    stq_events.check_event(
        task_id=f'{consts.JOB_ID}:{ENTITY_TYPE}:{request_entity_index + 1}',
        job_id=consts.JOB_ID,
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        request_entity_index=request_entity_index + 1,
    )


# Проверяем загрузку сущностей и их добавление в базу.
async def test_pg_append(mock_entities, job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    entity_objects = [ENTITY_OBJECT_1, ENTITY_OBJECT_2]

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=[PARENT_ID],
        ),
        models.JobEntityTask(entity_type=ENTITY_TYPE, entity_ids=[]),
    )

    mock_entities.orders.mock_load_by_id(
        mapping={PARENT_ID: entity_objects}, id_name=PARENT_ENTITY.id_name,
    )

    await job_pipeline.run_entity_load_by_id(
        job_id=job_id,
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
    )

    for entity_object in entity_objects:
        obj = job_pipeline.db.load_job_entity(
            job_id, ENTITY_TYPE, entity_object['id'],
        )
        assert obj is not None
        assert obj.entity_data == entity_object['data']

    task = job_pipeline.db.load_job_entity_task(job_id, ENTITY_TYPE)
    assert task is not None
    assert task.entity_ids == [it['id'] for it in entity_objects]


# Проверяем, что если entity_type == request_entity_type,
# то ids не должны добавляться в базу.
async def test_with_eq_type(mock_entities, job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    entity_id = '1'

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(entity_type=ENTITY_TYPE, entity_ids=[entity_id]),
    )

    mock_entities.orders.mock_load_by_id(
        mapping={entity_id: [{'id': entity_id}]}, id_name=ENTITY.id_name,
    )

    await job_pipeline.run_entity_load_by_id(
        job_id=job_id,
        entity_type=ENTITY_TYPE,
        request_entity_type=ENTITY_TYPE,
    )

    task = job_pipeline.db.load_job_entity_task(job_id, ENTITY_TYPE)
    assert task is not None
    assert task.entity_ids == [entity_id]


# Проверяем отгрузку sensitive данных, если job_type == delete.
@pytest_marks.JOB_TYPES
async def test_store_sensitive_data(
        mock_entities, grocery_sensitive, job_pipeline: JobPipeline, job_type,
):
    entity_objects = [ENTITY_OBJECT_1, ENTITY_OBJECT_2]

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH, job_type=job_type),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=[PARENT_ID],
        ),
        models.JobEntityTask(entity_type=ENTITY_TYPE, entity_ids=[]),
    )

    mock_entities.orders.mock_load_by_id(
        mapping={PARENT_ID: entity_objects}, id_name=PARENT_ENTITY.id_name,
    )

    grocery_sensitive.store.check(
        request_id=consts.JOB_ID,
        objects=[
            dict(
                entity_id=it['id'],
                entity_type=ENTITY_TYPE,
                data=it['sensitive_data'],
            )
            for it in entity_objects
            if 'sensitive_data' in it
        ],
    )

    await job_pipeline.run_entity_load_by_id(
        entity_type=ENTITY_TYPE, request_entity_type=PARENT_ENTITY_TYPE,
    )

    expected_times_called = int(job_type == models.JobType.delete)
    assert grocery_sensitive.store.times_called == expected_times_called


# Проверяем, что должна быть job в базе.
async def test_no_job(job_pipeline: JobPipeline):
    await job_pipeline.run_entity_load_by_id(expect_fail=True)


# Проверяем запуск stq post_load после того, как все объекты выгружены.
async def test_run_post_load(mock_entities, job_pipeline: JobPipeline):
    entity_ids = [PARENT_ID]

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=entity_ids,
        ),
    )

    mock_entities.orders.mock_load_by_id(
        mapping={}, id_name=PARENT_ENTITY.id_name,
    )

    await job_pipeline.run_entity_load_by_id(
        entity_type=ENTITY_TYPE,
        request_entity_type=PARENT_ENTITY_TYPE,
        request_entity_index=len(entity_ids),
    )

    stq_events = job_pipeline.stq_entity_post_load.events()
    stq_events.check_event(
        task_id=f'{consts.JOB_ID}:{ENTITY_TYPE}',
        job_id=consts.JOB_ID,
        entity_type=ENTITY_TYPE,
    )

    stq_events = job_pipeline.stq_entity_load_by_id.events()
    assert not stq_events


# Проверяем переключение settings_name в графе.
async def test_entity_settings_name(mock_entities, job_pipeline: JobPipeline):
    entity_ids = ['q']
    settings_name = 'orders_v2'

    entity_graph = models.EntityGraph(
        models.EntityNode(entity_type='orders', settings_name=settings_name),
    )
    entity = entity_graph[0]
    entity_mock = mock_entities[settings_name]

    job_pipeline.db.upsert(
        models.Job(graph=entity_graph),
        models.JobEntityTask(
            entity_type=entity.entity_type, entity_ids=entity_ids,
        ),
    )

    entity_mock.mock_load_by_id(mapping={}, id_name=entity.id_name)

    await job_pipeline.run_entity_load_by_id(
        entity_type=entity.entity_type, request_entity_type=entity.entity_type,
    )

    assert entity_mock.load_by_id.times_called == 1


# Проверяем использование экспа grocery_takeout_entity_response_validator.
@pytest.mark.parametrize('status_code', [200, 404])
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
    parent_ids = [PARENT_ID]
    expected_objects = [ENTITY_OBJECT_1, ENTITY_OBJECT_2]

    grocery_takeout_configs.entity_response_validator(is_valid=False)

    job_pipeline.db.upsert(
        models.Job(graph=DEFAULT_GRAPH),
        models.JobEntityTask(
            entity_type=PARENT_ENTITY_TYPE, entity_ids=parent_ids,
        ),
    )

    mock_entities.orders.mock_load_by_id(
        mapping={PARENT_ID: expected_objects},
        id_name=PARENT_ENTITY.id_name,
        status_code=status_code,
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_takeout_entity_response_validator',
    )

    await job_pipeline.run_entity_load_by_id(
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
    assert exp3_kwargs['handle'] == 'load_by_id'
    assert exp3_kwargs['entity_relation'] == ENTITY.relation
    assert exp3_kwargs['entity_type'] == entity_type
    assert exp3_kwargs['request_entity_type'] == request_entity_type
    assert exp3_kwargs['request_entity_id'] == parent_ids[request_entity_index]
    assert exp3_kwargs['response_code'] == status_code
    if status_code == 200:
        assert exp3_kwargs['response_len'] == len(expected_objects)
    else:
        assert exp3_kwargs['response_len'] == 0
