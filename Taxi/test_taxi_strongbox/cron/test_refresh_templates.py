# pylint: disable=redefined-outer-name,redefined-builtin,unused-variable
import os
import shutil

import pytest

from taxi.pg import pool

from taxi_strongbox.generated.cron import run_cron

TEMPLATE_CONTENT_1 = """{
    "mongo_settings": {
        {{ MONGODB_TEST }}
    },
    "settings_override": {
        "TEST_KEY": "{{ TEST_VALUE }}",
    }
}
"""
TEMPLATE_CONTENT_2 = """new_content
"""


@pytest.mark.pgsql('strongbox', files=['test_refresh_templates.sql'])
async def test_refresh_templates_with_arc(patch, cron_context, pgsql):
    @patch('arc.components.ShellExecuter._run_shell')
    async def _run_shell(*args, **kwargs):
        if args[0] == 'mount':
            static_dir_name = os.path.splitext(os.path.basename(__file__))[0]
            cron_dir_path = os.path.dirname(os.path.abspath(__file__))
            test_arc_dir = os.path.join(
                cron_dir_path, 'static', static_dir_name, 'arcadia',
            )
            arc_dir = str(args[2].resolve())
            shutil.copytree(test_arc_dir, arc_dir)
        elif args[0] == 'unmount':
            shutil.rmtree(args[1])
        return {}

    @patch('pathlib.Path.mkdir')
    def _mkdir(*args, **kwargs):
        pass

    await run_cron.main(
        ['taxi_strongbox.crontasks.refresh_templates', '-t', '0'],
    )

    master_pool: pool.Pool = cron_context.pg.master_pool
    async with master_pool.acquire() as conn:
        rows = await conn.fetch(
            'SELECT * FROM secrets.templates ORDER BY service_name;',
        )
        relations = await conn.fetch(
            'SELECT * FROM secrets.secrets_templates ORDER BY id;',
        )
        relations = [dict(r) for r in relations]
    assert rows[0]['content'] == TEMPLATE_CONTENT_1
    assert rows[1]['content'] == TEMPLATE_CONTENT_2
    assert relations == [
        {'id': 1, 'secret_id': 4, 'template_id': 1},
        {'id': 4, 'secret_id': 3, 'template_id': 1},
        {'id': 5, 'secret_id': 1, 'template_id': 1},
        {'id': 6, 'secret_id': 2, 'template_id': 1},
    ]
