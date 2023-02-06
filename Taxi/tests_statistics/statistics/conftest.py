# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import os

import pytest
from statistics_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
async def cleanup_local_cache(taxi_statistics, pgsql):
    # This is a crutch to make complete statistics clean
    # It is required, because statistics have local write & read buffer
    # todo make an explicit handle to discard write buffer and read from db
    try:
        yield
    finally:
        # 1. write local changes
        await taxi_statistics.invalidate_caches()

        # 2. remove everything from db
        pgsql['statistics'].cursor().execute('DELETE FROM statistics.metrics')
        pgsql['statistics'].cursor().execute(
            'DELETE FROM statistics.fallbacks',
        )

        # 3. fetch empty statistics
        await taxi_statistics.invalidate_caches()

        # 4. Now service state is clean


@pytest.fixture(name='remove_trash', scope='function', autouse=True)
def _remove_trash():
    try:
        yield
    finally:
        sha1 = '5701320dc521426d6ec146f324723fb0e29906af'
        conf = '/tmp/taxi-statistics-autogen_service_fallbacks'
        os.system('rm -f ' + conf + '_' + sha1 + '.conf')
