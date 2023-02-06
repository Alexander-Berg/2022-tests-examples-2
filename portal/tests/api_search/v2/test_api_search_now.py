# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from api_search_common import validate_schema_for_block, gen_params, ids, create_app_info
from common.client import MordaClient
from common.geobase import Regions

logger = logging.getLogger(__name__)

BLOCK = 'now'


def get_regions():
    return [Regions.MOSCOW, Regions.MINSK, Regions.ASTANA]


def now_params():
    app_info = create_app_info({'android': {}, 'iphone':  {}})
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru']
    )


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', now_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    validate_schema_for_block(client, BLOCK, params, allow_not_exist=True, yasm=yasm)
