# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import os

import pytest

from passenger_authorizer_plugins import *  # noqa: F403 F401 E501


# TODO remove the fixture below when TAXICOMMON-1067 is fixed
@pytest.fixture(name='ignore_trace_id', autouse=True)
def _ignore_trace_id(mockserver):
    with mockserver.ignore_trace_id():
        yield


@pytest.fixture
def service_client_default_headers():
    return {
        'User-Agent': 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv client)',
    }


@pytest.fixture
def am_proxy_name():
    return 'passenger-authorizer'


@pytest.fixture()
def collected_rules_filename():
    return os.path.join(
        os.path.dirname(__file__), 'static', 'default', 'collected-rules.json',
    )
