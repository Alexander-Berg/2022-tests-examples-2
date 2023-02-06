# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bson import json_util
from geoareas_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(name='bson_hook')
def _bson_hook():
    def hook(dct):
        return json_util.object_hook(
            dct, json_options=json_util.JSONOptions(tz_aware=False),
        )

    return hook
