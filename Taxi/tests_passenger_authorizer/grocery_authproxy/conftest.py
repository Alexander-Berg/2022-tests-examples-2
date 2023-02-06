# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import os

from grocery_authproxy_plugins import *  # noqa: F403 F401 E501
import pytest


@pytest.fixture
def am_proxy_name():
    return 'grocery-authproxy'


@pytest.fixture()
def collected_rules_filename():
    return os.path.join(
        os.path.dirname(__file__), 'static', 'default', 'collected-rules.json',
    )
