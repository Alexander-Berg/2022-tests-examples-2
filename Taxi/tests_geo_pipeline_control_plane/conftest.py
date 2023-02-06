# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from geo_pipeline_control_plane_plugins import *  # noqa: F403 F401

import pytest
import json


@pytest.fixture
async def fts_db_configs_by_version(load_json):
    """Returns all pipeline configs with specified version"""

    def get_config_by_version(filename, version):
        result = {}
        for pipeline_config in load_json(filename):
            if pipeline_config['version'] == version:
                result[pipeline_config['pipeline']] = json.loads(
                    pipeline_config['config'],
                )
        return result

    return get_config_by_version


@pytest.fixture(scope='session')
async def fts_current_version():
    return 4


@pytest.fixture(scope='session')
async def fts_previous_version():
    return 3
