import pytest

from testsuite.databases.mongo import ensure_db_indexes


@pytest.mark.nofilldb
def test_ensure_db_indexes(mongodb, mongodb_settings):
    ensure_db_indexes.ensure_db_indexes(mongodb, mongodb_settings)
