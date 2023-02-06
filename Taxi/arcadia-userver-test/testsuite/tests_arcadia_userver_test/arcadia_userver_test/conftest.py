import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from arcadia_userver_test_plugins import *  # noqa: F403 F401


@pytest.fixture()
def common_fixture():
    return 'foo'
