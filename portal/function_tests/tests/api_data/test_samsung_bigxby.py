# -*- coding: utf-8 -*-
# import json

import allure
import pytest

from common import env, schema
from common.client import MordaClient
from common.geobase import Regions
from common.schema import get_schema_validator

TESTEE = 'api_data_samsung_bixby'


"""
Урл для примера запроса
/samsung-bixby/?geo_by_settings=213
"""


def get_regions():
    return [
        Regions.MOSCOW, Regions.SAINT_PETERSBURG,
        Regions.KYIV, Regions.VITEBSK,
        Regions.ASTANA, Regions.VORONEZH,
        Regions.YEKATERINBURG, Regions.PETROPAVLOVSK,
        Regions.SAMARA
    ]


def gen_params(regions):
    return [dict(geo=geo) for geo in regions]


def test_params():
    return gen_params(regions=get_regions())

@pytest.skip("won't fix it")
@allure.feature('morda', TESTEE)
@allure.story('api_data_samsung_bixby_response')
@pytest.mark.parametrize('params', test_params())
def test_schema(params):
    client = MordaClient(env=env.morda_env())
    response = client.api_data_samsung_bixby(**params).send().json()
    # print json.dumps(response, indent=4, ensure_ascii=False).encode('utf-8')
    validator = get_schema_validator('schema/samsungbixby/samsungbixby-response.json')
    schema.validate_schema(response, validator)
