from aiohttp import web
import pytest

from supportai_lib.tasks import base_task

from supportai_tasks import models as db_models


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_tasks', files=['default.sql']),
    pytest.mark.config(
        TVM_RULES=[
            {'src': 'supportai-tasks', 'dst': 'supportai-context'},
            {'src': 'supportai-tasks', 'dst': 'stq-agent'},
        ],
    ),
    pytest.mark.config(
        SUPPORTAI_TASKS_RP_UPLOAD_SETTINGS={
            'batch_size': 2,
            'sleep_between_batches': 1,
        },
    ),
]


async def test_upload_rp_success(
        stq3_context, mockserver, stq_runner, create_task,
):
    rp_request_count = 0

    @mockserver.json_handler('/supportai-reference-phrases/v1/matrix')
    # pylint: disable=unused-variable
    async def handler_rp(request):
        nonlocal rp_request_count
        rp_request_count += 1

        return web.json_response(data={'matrix': []})

    db_task = create_task(
        type_='clustering_upload_rp_task',
        params={'topic_slug': 'totalchest', 'texts_ids': ['1', '2', '3']},
    )

    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': db_task.id},
    )

    assert db_task.status == base_task.TaskStatus.COMPLETED.value

    async with stq3_context.pg.slave_pool.acquire() as conn:
        results = await db_models.ClusteringResult.select_by_ids(
            stq3_context, conn, ids=[1, 2, 3],
        )

    assert not results
    assert rp_request_count == 2
