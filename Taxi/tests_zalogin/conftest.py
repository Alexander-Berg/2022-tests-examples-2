# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest
from zalogin_plugins import *  # noqa: F403 F401


@pytest.fixture
def service_client_default_headers():
    return {'Accept-Language': 'en'}
