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

BLOCK = 'services'


def get_regions():
    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG,
            Regions.KYIV,
            Regions.MINSK,
            Regions.ASTANA, Regions.ALMATY,
            Regions.WASHINGTON]


def services_schema_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=all_langs
    )


def services_http_code_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def services_static_code_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru'],
        dps=dps
    )


def get_services_urls(app_platform, block_data):
    urls = set()
    urls.update([ApiSearchUrl.parse(app_platform, service.get('url', None)).url_to_ping()
                 for service in block_data['data']['list'] if not service['url'].startswith('native')])
    urls.update([ApiSearchUrl.parse(app_platform, service.get('url', None)).url_to_ping()
                 for service in block_data['data']['more']['list'] if not service['url'].startswith('native')])
    return urls


def get_services_static_urls(block_data):
    urls = set()
    urls.update([service.get('icon', None) for service in block_data['data']['list']])
    urls.update([service.get('icon', None) for service in block_data['data']['more']['list']])
    return urls


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', services_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    validate_schema_for_block(client, BLOCK, params, yasm=yasm)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', services_http_code_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_services_urls)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_static')
@pytest.mark.parametrize('params', services_static_code_params(), ids=ids)
def test_static_code(params, yasm):
    client = MordaClient()
    check_static_codes(client, yasm, BLOCK, params, get_services_static_urls)
