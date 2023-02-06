# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
import psycopg2.tz  # noqa: F403 F401
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from cargo_performer_fines_plugins import *  # noqa: F403 F401


@pytest.fixture(name='default_headers')
def _default_headers():
    return {'Accept-Language': 'en', 'X-Remote-IP': '12.34.56.78'}
