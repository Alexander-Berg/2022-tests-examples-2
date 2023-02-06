# -*- coding: utf-8 -*-
from __future__ import print_function
import allure
import pytest
# from api_search_common import app_info
from api_search_common import gen_params, ids, validate_schema_for_block, check_http_codes
from common import env
from common.client import MordaClient
from common.geobase import Regions
from common.url import ApiSearchUrl
from common.utils import get_field


BLOCK = 'district'

"""
Урл для примера запроса
yandex.ru/portal/api/search/2?app_version=7010000&os_version=6.0.1&app_platform=android&geo_by_settings=213
"""

app_info = {
    'android': [7030000],     # [v for v in app_info['android'] if v >= 7010000],
    'iphone': [3070100],      # [v for v in app_info['iphone'] if v >= 3070100],
}


def get_regions():
    return [
        Regions.MOSCOW,
    ]


def district_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru']
    )


def district_http_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def district_static_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


@pytest.mark.skip(reason="Блок район отключен")
@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', district_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient(env=env.morda_env())
    validate_schema_for_block(client, BLOCK, params, yasm, False, 'div')


def get_district_urls(app_platform, block_data):
    district_data = get_field(block_data, 'data.states.0.blocks')
    urls = set((d['action']['url'] for d in district_data if 'action' in d and 'url' in d['action']))
    urls_to_ping = [ApiSearchUrl.parse(app_platform, url).url_to_ping() for url in urls]
    return urls_to_ping


@pytest.mark.skip(reason="Блок район отключен")
@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', district_http_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_district_urls)
