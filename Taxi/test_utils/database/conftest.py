import asyncio
import os

import pytest
import yatest

from taxi.robowarehouse.lib.concepts import database
from taxi.robowarehouse.lib.config import settings


@pytest.fixture(scope='session', autouse=True)
def migrate_db(event_loop):
    """Apply db migrations"""

    migration_path = os.environ['APP_MIGRATION_PATH']
    migration_path = os.path.join(yatest.common.build_path(), migration_path)
    os.environ['APP_MIGRATION_PATH'] = migration_path
    settings.database_migrations_abs_path = migration_path

    command_path = yatest.common.binary_path(os.environ['MIGRATOR_BIN'])

    yatest.common.execute(
        f'{command_path} upgrade head',
        shell=True,
        check_exit_code=True,
        wait=True,
    )


@pytest.fixture(scope='function', autouse=True)
async def truncate_db(event_loop):
    async def _truncate(table):
        async with database.db_session() as session:
            await session.execute('SELECT pg_advisory_xact_lock(1);')
            await session.execute(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE;')

    coros = []
    for table in database.Base.metadata.sorted_tables:
        coros.append(_truncate(table))

    await asyncio.gather(*coros)
