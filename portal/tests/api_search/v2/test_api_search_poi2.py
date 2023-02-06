# -*- coding: utf-8 -*-
from __future__ import print_function
import allure
import pytest
from api_search_common import app_info, gen_params, ids, validate_schema_for_block, \
    check_http_codes, check_static_codes, create_app_info
from common.client import MordaClient
from common.geobase import Regions
from common.url import ApiSearchUrl

BLOCK = 'poi2'

app_info = {
    'android': [v for v in app_info['android'] if v > 6000000],
    'iphone': app_info['iphone'],
}


def get_regions():
    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG,
            Regions.KYIV, Regions.LVIV,
            Regions.MINSK, Regions.VITEBSK,
            Regions.ASTANA, Regions.ALMATY]


def poi2_params():
    app_info_add = create_app_info(
        {
            'android': {'start': 6000000},
            'iphone':  {'start': 3010000}
        }
    )
    return gen_params(
        app_info=app_info_add,
        regions=get_regions(),
        langs=['ru']
    )


def poi2_http_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def poi2_static_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', poi2_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    validate_schema_for_block(client, BLOCK, params, yasm)


def get_poi2_urls(app_platform, block_data):
    urls = {ApiSearchUrl.parse(app_platform, block_data['data']['action_url']).url_to_ping()}

    for group in block_data['data']['groups']:
        if 'action_url' in group and ApiSearchUrl.parse(app_platform, group['action_url']).url_to_ping() is not None:
            urls.add(ApiSearchUrl.parse(app_platform, group['action_url']).url_to_ping())
        for item in group['items']:
            if 'url' in item and ApiSearchUrl.parse(app_platform, item['url']).url_to_ping() is not None:
                urls.add(ApiSearchUrl.parse(app_platform, item['url']).url_to_ping())

    print('\n'.join(urls))
    return urls


def get_poi2_static_urls(block_data):
    urls = set()
    for group in block_data['data']['groups']:
        for item in group['items']:
            if 'image_url' in item and item['image_url'] is not None:
                urls.add(item['image_url'])
    return urls


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', poi2_http_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_poi2_urls)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_static')
@pytest.mark.parametrize('params', poi2_static_params(), ids=ids)
def test_static_code(params, yasm):
    client = MordaClient()
    check_static_codes(client, yasm, BLOCK, params, get_poi2_static_urls)
