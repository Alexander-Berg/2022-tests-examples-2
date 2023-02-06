import uuid

import pytest


# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from scooters_misc_plugins import *  # noqa: F403 F401


@pytest.fixture
def generate_uuid():
    return str(uuid.uuid4())
