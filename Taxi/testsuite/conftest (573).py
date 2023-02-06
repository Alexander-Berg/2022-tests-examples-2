import uuid

import pytest


# root conftest for service scooters-ops-relocation
pytest_plugins = ['scooters_ops_relocation_plugins.pytest_plugins']


@pytest.fixture
def getuuid():
    return uuid.uuid4().hex
