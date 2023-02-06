# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from api_search_common import gen_params, ids, get_top_level_data, create_app_info
from common.client import MordaClient
from common.geobase import Regions
from common import schema
from common.url import ApiSearchUrl, check_urls_params

logger = logging.getLogger(__name__)

BLOCK = 'services'

app_info_conf = {
    'android': {'start': 8080000},
    'iphone': {'start': 5040000}
}

services_require_utm = {
    'keyboard': True,
}


def bottom_sheet_schema_params():
    app_info = create_app_info(app_info_conf)
    return gen_params(
        app_info=app_info,
        regions=[Regions.MOSCOW],
        langs=['ru']
    )


def bottom_sheet_utm_params():
    return gen_params(
        app_info={
            'android': ['21550000']
        },
        regions=[Regions.MOSCOW],
        langs=['ru']
    )


@allure.feature('api_search_v2_unstable', 'bottom_sheet', BLOCK)
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', bottom_sheet_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient()
    block_data = get_top_level_data(client, BLOCK, params)
    validator = schema.get_api_search_2_validator_top_level(params['app_platform'], params['app_version'], BLOCK)
    schema.validate_schema(block_data, validator)


def get_services_urls(app_platform, block_data, services_names=None):
    urls = list()
    for section in block_data.get('sections'):
        for service in section.get('buttons') or []:
            if services_names and not services_names.get(service.get('id')):
                continue
            urls.append(ApiSearchUrl.parse(app_platform, service.get('actionUrl', None)).to_url())

    return urls


@allure.feature('api_search_v2', 'bottom_sheet', BLOCK)
@allure.story('Check bottom sheet utm_source')
@pytest.mark.parametrize('params', bottom_sheet_utm_params(), ids=ids)
def test_utm_source(params, yasm):
    params['app_id'] = 'ru.yandex.searchplugin'

    client = MordaClient()
    block_data = get_top_level_data(client, BLOCK, params)
    urls = get_services_urls(params['app_platform'], block_data, services_require_utm)
    check_urls_params(urls, 'utm_source', '', True)
