import pytest

from . import consts
from . import models
from . import pytest_marks
from .job_pipeline import JobPipeline  # pylint: disable=C5521


# Проверяем happy path.
async def test_basic(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    entity_type = 'yandex_uid'

    entity_graph = models.EntityGraph(models.EntityNode(entity_type))

    job_pipeline.db.upsert(models.Job(job_id=job_id, graph=entity_graph))

    await job_pipeline.run_entity_post_load(
        job_id=job_id, entity_type=entity_type,
    )


# Проверяем, что должна быть job в базе.
async def test_no_job(job_pipeline: JobPipeline):
    await job_pipeline.run_entity_post_load(expect_fail=True)


# Проверяем, что в графе должна быть нода сущности.
async def test_no_entity_node(job_pipeline: JobPipeline):
    job_pipeline.db.upsert(models.Job())

    await job_pipeline.run_entity_post_load(expect_fail=True)


# Проверяем, что каждый ребенок сущности обработан.
# Пока что обработаны только indirect.
async def test_process_children(job_pipeline: JobPipeline):
    entity_type = 'yandex_uid'

    entity_graph = models.EntityGraph(
        models.EntityNode(
            entity_type=entity_type,
            children=[
                models.EntityNode(
                    entity_type='orders',
                    relation=models.EntityRelation.indirect,
                ),
                models.EntityNode(
                    entity_type='carts',
                    relation=models.EntityRelation.indirect,
                ),
                models.EntityNode(
                    entity_type='user_data',
                    relation=models.EntityRelation.direct,
                ),
            ],
        ),
    )

    job_pipeline.db.upsert(models.Job(graph=entity_graph))

    await job_pipeline.run_entity_post_load(entity_type=entity_type)

    stq_events = job_pipeline.stq_entity_load_ids.events()
    assert len(stq_events) == 2

    stq_events = job_pipeline.stq_entity_load_by_id.events()
    assert len(stq_events) == 1

    for child in entity_graph[0].children:
        task = job_pipeline.db.load_job_entity_task(
            consts.JOB_ID, child.entity_type,
        )
        assert task == models.JobEntityTask(
            entity_type=child.entity_type, entity_ids=[], entity_ids_version=0,
        )


# Проверяем обработку ребенка сущности со связью indirect.
async def test_child_indirect_stq(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    entity_type = 'yandex_uid'
    child_entity_type = 'orders'

    entity_graph = models.EntityGraph(
        models.EntityNode(
            entity_type=entity_type,
            children=[
                models.EntityNode(
                    entity_type=child_entity_type,
                    relation=models.EntityRelation.indirect,
                ),
            ],
        ),
    )

    job_pipeline.db.upsert(models.Job(job_id=job_id, graph=entity_graph))

    await job_pipeline.run_entity_post_load(
        job_id=job_id, entity_type=entity_type,
    )

    stq_events = job_pipeline.stq_entity_load_ids.events()
    stq_events.check_event(
        task_id=f'{job_id}:{child_entity_type}:0',
        times_called=1,
        job_id=job_id,
        entity_type=child_entity_type,
        request_entity_type=entity_type,
        request_entity_index=0,
        iteration_number=0,
        cursor=None,
    )


# Проверяем обработку ребенка сущности со связью direct.
async def test_child_direct_stq(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    entity_type = 'yandex_uid'
    child_entity_type = 'orders'

    entity_graph = models.EntityGraph(
        models.EntityNode(
            entity_type=entity_type,
            children=[
                models.EntityNode(
                    entity_type=child_entity_type,
                    relation=models.EntityRelation.direct,
                ),
            ],
        ),
    )

    job_pipeline.db.upsert(models.Job(job_id=job_id, graph=entity_graph))

    await job_pipeline.run_entity_post_load(
        job_id=job_id, entity_type=entity_type,
    )

    stq_events = job_pipeline.stq_entity_load_by_id.events()
    stq_events.check_event(
        task_id=f'{job_id}:{child_entity_type}:0',
        times_called=1,
        job_id=job_id,
        entity_type=child_entity_type,
        request_entity_type=entity_type,
        request_entity_index=0,
    )


# Проверяем создание таски на удаление данных.
@pytest.mark.parametrize('relation', models.EntityRelation.values)
async def test_run_delete_by_id(job_pipeline: JobPipeline, relation):
    job_id = consts.JOB_ID

    entity_graph = models.EntityGraph(
        models.EntityNode(
            entity_type='yandex_uid',
            id_name='yandex_uid',
            children=[
                models.EntityNode(
                    entity_type='orders',
                    id_name='order_id',
                    relation=relation,
                ),
            ],
        ),
    )

    parent_entity = entity_graph[0]
    entity = parent_entity.children[0]

    if relation == models.EntityRelation.direct:
        request_entity_type = parent_entity.entity_type
    else:
        request_entity_type = entity.entity_type

    job_pipeline.db.upsert(
        models.Job(
            job_id=job_id, job_type=models.JobType.delete, graph=entity_graph,
        ),
    )

    await job_pipeline.run_entity_post_load(
        job_id=job_id, entity_type=entity.entity_type,
    )

    stq_events = job_pipeline.stq_entity_delete_by_id.events()
    stq_events.check_event(
        task_id=f'{job_id}:{entity.entity_type}:0',
        job_id=job_id,
        entity_type=entity.entity_type,
        request_entity_type=request_entity_type,
        request_entity_index=0,
    )


# Проверяем, что таска на удаление не создалась, если job_type != delete.
@pytest_marks.JOB_TYPES
async def test_skip_delete_if_not_delete(job_pipeline: JobPipeline, job_type):
    entity_type = 'orders'

    entity_graph = models.EntityGraph(
        models.EntityNode(
            entity_type='yandex_uid',
            children=[models.EntityNode(entity_type)],
        ),
    )

    job_pipeline.db.upsert(models.Job(job_type=job_type, graph=entity_graph))

    await job_pipeline.run_entity_post_load(entity_type=entity_type)

    stq_events = job_pipeline.stq_entity_delete_by_id.events()
    assert len(stq_events) == int(job_type == models.JobType.delete)


# Проверяем, что таска на удаление не создалась, если у сущности нет родителя.
async def test_skip_delete_if_no_parent(job_pipeline: JobPipeline):
    entity_type = 'yandex_uid'

    entity_graph = models.EntityGraph(models.EntityNode(entity_type))

    job_pipeline.db.upsert(
        models.Job(job_type=models.JobType.delete, graph=entity_graph),
    )

    await job_pipeline.run_entity_post_load(entity_type=entity_type)

    stq_events = job_pipeline.stq_entity_delete_by_id.events()
    assert not stq_events


# Проверяем запуск stq job_finalize
@pytest_marks.JOB_TYPES
async def test_run_finalize(job_pipeline: JobPipeline, job_type):
    job_id = consts.JOB_ID
    entity_type = 'yandex_uid'

    entity_graph = models.EntityGraph(models.EntityNode(entity_type))

    job_pipeline.db.upsert(
        models.Job(job_id=job_id, job_type=job_type, graph=entity_graph),
        models.JobEntityTask(job_id=job_id, entity_type=entity_type),
    )

    await job_pipeline.run_entity_post_load(
        job_id=job_id, entity_type=entity_type,
    )

    stq_events = job_pipeline.stq_job_finalize.events()
    stq_events.check_event(task_id=f'{job_id}', job_id=job_id)


# Проверяем, запуск finalize произошел, когда все entity tasks стали done
async def test_finalize_after_all_done(job_pipeline: JobPipeline):
    job_id = consts.JOB_ID
    entity_type1 = 'yandex_uid'
    entity_type2 = 'orders'

    entity_graph = models.EntityGraph(
        models.EntityNode(
            entity_type1, children=[models.EntityNode(entity_type2)],
        ),
    )

    job_pipeline.db.upsert(
        models.Job(
            job_id=job_id, job_type=models.JobType.load, graph=entity_graph,
        ),
        models.JobEntityTask(job_id=job_id, entity_type=entity_type1),
        models.JobEntityTask(job_id=job_id, entity_type=entity_type2),
    )

    await job_pipeline.run_entity_post_load(
        job_id=job_id, entity_type=entity_type1,
    )

    stq_events = job_pipeline.stq_job_finalize.events()
    assert not stq_events

    await job_pipeline.run_entity_post_load(
        job_id=job_id, entity_type=entity_type2,
    )

    stq_events = job_pipeline.stq_job_finalize.events()
    assert len(stq_events) == 1
