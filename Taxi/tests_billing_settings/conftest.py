import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from billing_settings_plugins import *  # noqa: F403 F401

BILLING_SETTINGS_DB_NAME = 'billing_settings'


@pytest.fixture
def billing_settings_postgres_db(pgsql):
    return pgsql[BILLING_SETTINGS_DB_NAME].cursor()
