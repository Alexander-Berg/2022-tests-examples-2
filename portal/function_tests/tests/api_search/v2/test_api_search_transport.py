# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from api_search_common import app_info, all_langs, validate_schema_for_block, gen_params, ids, dps, check_http_codes, \
    check_static_codes
from common import env
from common.client import MordaClient
from common.geobase import Regions
from common.url import ApiSearchUrl

logger = logging.getLogger(__name__)

BLOCK = 'transport'

app_info = {
    'android': [v for v in app_info['android'] if v < 6020001]
}


def get_regions():
    if env.is_monitoring():
        return [Regions.MOSCOW, Regions.SAINT_PETERSBURG,
                Regions.KYIV, Regions.VITEBSK,
                Regions.ASTANA, Regions.ALMATY,
                Regions.WASHINGTON]

    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG, Regions.YEKATERINBURG, Regions.VORONEZH, Regions.PERM,
            Regions.NIZHNY_NOVGOROD, Regions.ROSTOV_NA_DONU, Regions.KRASNODAR, Regions.CHELYABINSK,
            Regions.SAMARA, Regions.NOVOSIBIRSK, Regions.VOLGOGRAD, Regions.UFA, Regions.SARATOV,
            Regions.PETROPAVLOVSK,
            Regions.KYIV, Regions.VITEBSK,
            Regions.ASTANA, Regions.ALMATY,
            Regions.WASHINGTON]


def transport_schema_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=all_langs
    )


def transport_http_code_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def transport_static_code_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru'],
        dps=dps
    )


def get_transport_urls(app_platform, block_data):
    urls = set()
    urls.update([ApiSearchUrl.parse(app_platform, item['url']).url_to_ping()
                 for item in block_data['data']['list']])
    return urls


def get_transport_static_urls(block_data):
    urls = set()
    urls.update([item.get('icon', None) for item in block_data['data']['list']])
    return urls


@pytest.mark.skip(reason="Блок transport отключен")
@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', transport_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    validate_schema_for_block(client, BLOCK, params, yasm=yasm)


@pytest.mark.skip(reason="Блок transport отключен")
@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', transport_http_code_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_transport_urls)


@pytest.mark.skip(reason="Блок transport отключен")
@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_static')
@pytest.mark.parametrize('params', transport_static_code_params(), ids=ids)
def test_static_code(params, yasm):
    client = MordaClient()
    check_static_codes(client, yasm, BLOCK, params, get_transport_static_urls)
