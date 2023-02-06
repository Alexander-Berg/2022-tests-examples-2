# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from api_search_common import app_info, all_langs, validate_schema_for_block, gen_params, ids, dps, check_http_codes, \
    check_static_codes
from common.client import MordaClient
from common.geobase import Regions
from common.url import ApiSearchUrl

logger = logging.getLogger(__name__)

BLOCK = 'search'


def get_regions():
    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG,
            Regions.KYIV, Regions.LVIV,
            Regions.MINSK, Regions.VITEBSK,
            Regions.ASTANA, Regions.ALMATY,
            Regions.ISTANBUL, Regions.ANKARA,
            Regions.WASHINGTON]


def search_schema_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=all_langs
    )


def search_http_code_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def search_static_code_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru'],
        dps=dps
    )


def get_search_urls(app_platform, block_data):
    urls = set()

    for informer in block_data['data']['informer']:
        url = informer.get('url')
        if url:
            urls.add(ApiSearchUrl.parse(app_platform, informer.get('url', None)).url_to_ping())

    return urls


def get_search_static_urls(block_data):
    urls = set()
    urls.update([group.get('icon', None) for group in block_data['data']['informer']])
    urls.update([group.get('inner_icon', None) for group in block_data['data']['informer']])
    return urls


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', search_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    validate_schema_for_block(client, BLOCK, params, yasm=yasm)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', search_http_code_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_search_urls)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_static')
@pytest.mark.parametrize('params', search_static_code_params(), ids=ids)
def test_static_code(params, yasm):
    client = MordaClient()
    check_static_codes(client, yasm, BLOCK, params, get_search_static_urls)
