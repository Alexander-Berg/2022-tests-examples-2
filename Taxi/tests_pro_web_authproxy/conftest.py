# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from pro_web_authproxy_plugins import *  # noqa: F403 F401


@pytest.fixture(name='ignore_trace_id', autouse=True)
def _ignore_trace_id(mockserver):
    with mockserver.ignore_trace_id():
        yield


@pytest.fixture
def am_proxy_name():
    return 'pro-web-authproxy'
