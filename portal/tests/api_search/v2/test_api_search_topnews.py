# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from api_search_common import app_info, all_langs, validate_schema_for_block, gen_params, ids, check_http_codes
from common.client import MordaClient
from common.geobase import Regions
from common.url import ApiSearchUrl

logger = logging.getLogger(__name__)

BLOCK = 'topnews'


def get_regions():
    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG,
            Regions.MINSK, Regions.VITEBSK,
            Regions.KYIV, Regions.LVIV,
            Regions.ASTANA, Regions.ALMATY,
            Regions.LONDON, Regions.NEW_YORK, Regions.BERLIN]


def topnews_schema_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=all_langs
    )


def topnews_http_code_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def get_topnews_urls(app_platform, block_data):
    urls = set()

    if 'special' in block_data['data']:
        urls.add(ApiSearchUrl.parse(app_platform, block_data['data']['special']['url']).url_to_ping())

    urls.add(ApiSearchUrl.parse(app_platform, block_data['data']['url']).url_to_ping())

    for tab in block_data['data']['tab']:
        urls.update([
            ApiSearchUrl.parse(app_platform, tab['full_list_button']['url']).url_to_ping(),
            ApiSearchUrl.parse(app_platform, tab['url']).url_to_ping()
        ])
        urls.update([ApiSearchUrl.parse(app_platform, item['url']).url_to_ping()
                     for item in tab['news']])

    return urls


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', topnews_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    validate_schema_for_block(client, BLOCK, params, yasm=yasm)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', topnews_http_code_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_topnews_urls)
