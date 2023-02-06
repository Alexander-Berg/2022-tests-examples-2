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

BLOCK = 'weather'


def get_regions():
    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG,
            Regions.MINSK, Regions.VITEBSK,
            Regions.KYIV, Regions.LVIV,
            Regions.ASTANA, Regions.ALMATY,
            Regions.ISTANBUL, Regions.ANKARA,
            Regions.LONDON, Regions.NEW_YORK, Regions.BERLIN]


def weather_schema_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=all_langs
    )


def weather_http_code_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def weather_static_code_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru'],
        dps=dps
    )


def get_weather_urls(app_platform, block_data):
    urls = {
        block_data['data']['url'],
        block_data['data']['notice_url'],
        ApiSearchUrl.parse(app_platform, block_data['data']['url_v5']).url_to_ping()
    }

    forecasts = []
    forecasts.extend(block_data['data']['forecast'])
    forecasts.extend(block_data['data']['short_forecast'])

    urls.update([ApiSearchUrl.parse(app_platform, forecast['url']).url_to_ping() for forecast in forecasts])
    return urls


def get_weather_static_urls(block_data):
    urls = {
        block_data['data']['icon_big_colored'],
        block_data['data']['icon'],
        block_data['data']['icon_white']
    }

    forecasts = []
    forecasts.extend(block_data['data']['forecast'])
    forecasts.extend(block_data['data']['short_forecast'])

    for forecast in forecasts:
        urls.update({
            forecast['icon'],
            forecast['icon_daynight'],
            forecast['icon_colored'],
            forecast['icon_white']
        })
    return urls


@pytest.mark.yasm
@allure.feature('api_search_v2', 'weather')
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', weather_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient(env=env.morda_env())
    validate_schema_for_block(client, 'weather', params, yasm=yasm)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', weather_http_code_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_weather_urls)


@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_static')
@pytest.mark.parametrize('params', weather_static_code_params(), ids=ids)
def test_static_code(params, yasm):
    client = MordaClient()
    check_static_codes(client, yasm, BLOCK, params, get_weather_static_urls)
