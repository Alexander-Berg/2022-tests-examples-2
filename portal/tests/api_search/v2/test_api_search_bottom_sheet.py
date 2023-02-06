# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from api_search_common import gen_params, ids, get_top_level_data, create_app_info
from common.client import MordaClient
from common.geobase import Regions
from common import schema

logger = logging.getLogger(__name__)

BLOCK = 'services'

app_info_conf = {
    'android': {'start': 8070000}
}


def bottom_sheet_schema_params():
    app_info = create_app_info(app_info_conf)
    return gen_params(
        app_info=app_info,
        regions=[Regions.MOSCOW],
        langs=['ru']
    )


@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', bottom_sheet_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    params['ab_flags'] = 'bottom_sheet_api'
    block_data = get_top_level_data(client, BLOCK, params)
    validator = schema.get_api_search_2_validator_top_level(params['app_platform'], params['app_version'], BLOCK)
    schema.validate_schema(block_data, validator)
