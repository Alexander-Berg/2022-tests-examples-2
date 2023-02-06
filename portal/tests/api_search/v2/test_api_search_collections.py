# -*- coding: utf-8 -*-
import logging

import allure
import pytest
import re

from api_search_common import app_info, validate_schema_for_block, gen_params, ids, dps, check_http_codes, \
    check_static_codes, create_app_info
from common.client import MordaClient
from common.geobase import Regions

logger = logging.getLogger(__name__)

BLOCK = 'collections'


def get_regions():
    return [Regions.MOSCOW, Regions.MINSK, Regions.ASTANA]


def collections_schema_params():
    app_info_add = create_app_info(
        {
            'android': {'start': 8010000},
            'iphone':  {'start': 3010000}
        }
    )

    app_info_new = {
        'android': set(map(int, app_info['android'] + app_info_add['android'])),
        'iphone': set(map(int, app_info['iphone'] + app_info_add['iphone'])),
    }

    return gen_params(
        app_info=app_info_new,
        regions=get_regions(),
        langs=['ru']
    )


def collections_http_code_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def collections_static_code_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru'],
        dps=dps
    )


def get_collections_urls(app_platform, block_data):
    urls = set()

    items_key = 'items'
    if block_data.get('type') == 'afisha':
        items_key = 'events'

    url = block_data['data']['url']

    if re.compile(r'^https?').match(url):
        urls.add(url)

    for item in block_data['data'][items_key]:
        url = item.get('url')
        if (re.compile(r'^https?').match(url)):
            urls.add(url)

    return urls


def get_collections_static_urls(block_data):
    urls = set()
    if block_data.get('type') == 'gallery':
        urls.update([item.get('image_url') for item in block_data['data']['items']])

    if block_data.get('type') == 'afisha':
        urls.update([item.get('poster') for item in block_data['data']['events']])

    return urls


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', collections_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    validate_schema_for_block(client, BLOCK, params, yasm=yasm)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', collections_http_code_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_collections_urls)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_static')
@pytest.mark.parametrize('params', collections_static_code_params(), ids=ids)
def test_static_code(params, yasm):
    client = MordaClient()
    check_static_codes(client, yasm, BLOCK, params, get_collections_static_urls)
