# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from geopipeline_tools.geopipeline import (  # noqa: F401 C5521
    geopipeline_config,
)  # noqa: F401 C5521
import pytest
from yaga_metrolog_plugins import *  # noqa: F403 F401


# pylint: disable=redefined-outer-name
@pytest.fixture
async def taxi_yaga_metrolog_adv(
        taxi_yaga_metrolog, geopipeline_config,  # noqa: F811
):  # noqa: F811
    return await geopipeline_config(taxi_yaga_metrolog)
