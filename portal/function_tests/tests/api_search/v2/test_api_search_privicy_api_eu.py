# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from api_search_common import app_info, validate_schema_for_block, gen_params, ids
from common import env
from common.client import MordaClient

logger = logging.getLogger(__name__)

BLOCK = 'privacy_api_eu'

def params():
    return gen_params(
        app_info={
            'android': [29050000]
        },
        regions=[11481],
        langs=['en-ee'],
        os_versions={'android': ['7.0']}
    )

@pytest.mark.yasm
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient(env=env.morda_env())
    validate_schema_for_block(client, BLOCK, params, yasm=yasm, custom_schema="div2")
