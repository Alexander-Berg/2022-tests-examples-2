# -*- coding: utf-8 -*-
from __future__ import print_function
import allure
import pytest
from api_search_common import app_info, gen_params, ids, validate_schema_for_block,\
    check_http_codes, check_static_codes, create_app_info

#     check_static_codes
from common import env
from common.client import MordaClient
from common.geobase import Regions
from common.url import ApiSearchUrl

BLOCK = 'edadeal'

app_info = {
    'android': [v for v in app_info['android'] if v > 6000000],
    'iphone': app_info['iphone'],
}


def get_regions():
    return [Regions.MOSCOW]


def edadeal_params():
    app_info_add = create_app_info(
        {
            'android': {'start': 8070000},
            'iphone':  {'start': app_info['iphone'][-1]}
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


def edadeal_http_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )


def edadeal_static_params():
    return gen_params(
        app_info={
            'android': [app_info['android'][-1]]
        },
        regions=get_regions(),
        langs=['ru']
    )

@pytest.skip('edadeal disabled')
@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', edadeal_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient(env=env.morda_env())
    custom_schema = False
    if params['app_platform'] == 'iphone' and params['app_version'] >= 3070000:
        custom_schema = 'div'
    if params['app_platform'] == 'android' and params['app_version'] >= 7030000:
        custom_schema = 'div'
    validate_schema_for_block(client, BLOCK, params, yasm, custom_schema=custom_schema)


def get_edadeal_urls(app_platform, block_data):
    urls = {ApiSearchUrl.parse(app_platform, block_data['data']['action_url']).url_to_ping()}
    urls.add(ApiSearchUrl.parse(app_platform, block_data['data']['url']).url_to_ping())

    for item in block_data['data']['items']:
        if 'url' in item and ApiSearchUrl.parse(app_platform, item['url']).url_to_ping() is not None:
            urls.add(ApiSearchUrl.parse(app_platform, item['url']).url_to_ping())

    print('\n'.join(urls))
    return urls


def get_edadeal_static_urls(block_data):
    urls = set()
    if block_data['type'] == 'div':
        return urls
    for item in block_data['data']['items']:
        if 'image_url' in item and item['image_url'] is not None:
            urls.add(item['image_url'])
    print('\n'.join(urls))
    return urls


@pytest.skip('edadeal disabled')
@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_http_code')
@pytest.mark.parametrize('params', edadeal_http_params(), ids=ids)
def test_http_code(params, yasm):
    client = MordaClient()
    check_http_codes(client, yasm, BLOCK, params, get_edadeal_urls)


@pytest.skip('edadeal disabled')
@pytest.mark.yasm
@allure.feature('api_search_v2', BLOCK)
@allure.story('api_search_v2_static')
@pytest.mark.parametrize('params', edadeal_static_params(), ids=ids)
def test_static_code(params, yasm):
    client = MordaClient()
    check_static_codes(client, yasm, BLOCK, params, get_edadeal_static_urls)
