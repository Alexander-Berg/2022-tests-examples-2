# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import pytest

from tips_plugins import *  # noqa: F403 F401


@pytest.fixture
def tips_postgres_db(pgsql):
    return pgsql['tips'].cursor()
