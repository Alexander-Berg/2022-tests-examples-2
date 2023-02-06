# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from feeds_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(scope='session')
def pgsql_cleanup_exclude_tables():
    return frozenset({'public.spatial_ref_sys'})
