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

BLOCK = 'stream'


def get_regions():
    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG]


def stream_schema_params():
    android_versions = {version for version in app_info['android'] if version >= 7010000}
    android_versions |= {7010000, 7030000}
    ios_versions = {version for version in app_info['iphone'] if version >= 3050100}
    ios_versions |= {3050100, 3070000}
    return gen_params(
        # app_info=app_info,
        app_info={
            # 'android': [version for version in app_info[android] if version >= 6010000],
            'android': list(android_versions),
            'iphone': list(ios_versions),
        },
        regions=get_regions(),
        langs=all_langs
    )


def stream_http_code_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def stream_static_code_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru'],
        dps=dps
    )


def get_stream_urls(app_platform, block_data):
    yield ApiSearchUrl.parse(app_platform, block_data['data']['action_url']).url_to_ping()
    yield ApiSearchUrl.parse(app_platform, block_data['data']['url']).url_to_ping()
    for item in block_data['data']['items']:
        yield ApiSearchUrl.parse(app_platform, item['url']).url_to_ping()


def get_stream_static_urls(block_data):
    if block_data.get('type') == 'gallery':
        for item in block_data['data']['items']:
            yield item['image_url']


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', stream_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    custom_schema = False
    if params['app_platform'] == 'iphone' and params['app_version'] >= 3070000:
        custom_schema = 'div'
    if params['app_platform'] == 'android' and params['app_version'] >= 7030000:
        custom_schema = 'div'
    validate_schema_for_block(client, BLOCK, params, yasm=yasm, custom_schema=custom_schema)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', stream_http_code_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_stream_urls)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_static')
@pytest.mark.parametrize('params', stream_static_code_params(), ids=ids)
def test_static_code(params, yasm):
    client = MordaClient()
    check_static_codes(client, yasm, BLOCK, params, get_stream_static_urls)
