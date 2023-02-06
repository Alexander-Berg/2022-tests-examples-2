import pytest

from supportai_tasks import models as db_models
from supportai_tasks.generated.cron import run_cron


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql']),
]


@pytest.mark.config(
    SUPPORTAI_TASKS_CLUSTERING_SETTINGS={
        'default_settings': {
            'nirvana_instance_id': (
                'bb951dc5-975b-4b3f-944c-9de56aae8beb/'
                '828f5201-f124-4c36-8815-cc2b55fb673f'
            ),
            'yt_root_dir': '//home/taxi_ml/imports/support',
            'messages_count': 10,
        },
        'projects': [],
    },
)
async def test_clustering_cron_nothing(cron_context):
    await run_cron.main(
        ['supportai_tasks.crontasks.run_clustering', '-t', '0'],
    )

    async with cron_context.pg.slave_pool.acquire() as conn:
        tasks = await db_models.Task.select_by_project(
            cron_context,
            conn,
            project_id=1,
            types=['clustering'],
            ref_task_id=None,
            limit=None,
            older_than=None,
        )

        assert not tasks


@pytest.mark.config(
    SUPPORTAI_TASKS_CLUSTERING_SETTINGS={
        'default_settings': {
            'nirvana_instance_id': (
                'bb951dc5-975b-4b3f-944c-9de56aae8beb/'
                '828f5201-f124-4c36-8815-cc2b55fb673f'
            ),
            'yt_root_dir': '//home/taxi_ml/imports/support',
            'messages_count': 10,
        },
        'projects': [
            {'project_slug': 'ya_market'},
            {'project_slug': 'ya_market'},
        ],
    },
    SUPPORTAI_TASKS_SETTINGS={
        'base_path': '',
        'task_queues': [
            {
                'queue_name': 'supportai_admin_export',
                'task_types': ['clustering'],
            },
        ],
    },
)
async def test_clustering_cron_two(cron_context):
    await run_cron.main(
        ['supportai_tasks.crontasks.run_clustering', '-t', '0'],
    )

    async with cron_context.pg.slave_pool.acquire() as conn:
        tasks = await db_models.Task.select_by_project(
            cron_context,
            conn,
            project_id=1,
            types=['clustering'],
            ref_task_id=None,
            limit=None,
            older_than=None,
        )

        assert len(tasks) == 2
