# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from api_search_common import app_info, all_langs, validate_schema_for_block, gen_params, ids, check_http_codes, \
    check_static_codes, create_app_info
from common.client import MordaClient
from common.geobase import Regions
from common.url import ApiSearchUrl

logger = logging.getLogger(__name__)

BLOCK = 'afisha'


def get_regions():
    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG, Regions.MINSK, Regions.ASTANA]


def afisha_schema_params():
    app_info_add = create_app_info(
        {
            'android': {'start': 8070000},
        }
    )

    app_info_new = {
        'android': set(app_info['android'] + app_info_add['android']),
        'iphone': set(app_info['iphone']),
    }
    return gen_params(
        app_info=app_info_new,
        regions=get_regions(),
        langs=all_langs
    )


def afisha_http_code_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def afisha_static_code_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru'],
        dps=['1', '1.5', '2', '3', '4']
    )


def get_afisha_urls(app_platform, block_data):
    urls = {block_data['data']['url']}
    urls.update([ApiSearchUrl.parse(app_platform, event['url']).url_to_ping()
                 for event in block_data['data']['events']])
    return urls


def get_afisha_static_urls(block_data):
    urls = set()
    urls.update([event.get('background_image', None) for event in block_data['data']['events']])
    urls.update([event.get('poster', None) for event in block_data['data']['events']])
    return set(urls)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', afisha_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    validate_schema_for_block(client, BLOCK, params, yasm=yasm)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', afisha_http_code_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_afisha_urls)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_static')
@pytest.mark.parametrize('params', afisha_static_code_params(), ids=ids)
def test_static_code(params, yasm):
    client = MordaClient()
    check_static_codes(client, yasm, BLOCK, params, get_afisha_static_urls)
