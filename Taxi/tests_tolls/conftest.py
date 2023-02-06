import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from tolls_plugins import *  # noqa: F403 F401

from tests_tolls import util


@pytest.fixture
def db_toll_roads(pgsql):
    return util.DbTollRoads(pgsql[util.DB_NAME_TOLL_ROADS].cursor())
