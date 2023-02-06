# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from common import zen_extensions
from common import env
from common.client import MordaClient

logger = logging.getLogger(__name__)

app_info = {
    'android': ['2001100000', '2011100000'],
    'iphone' : ['42000000']
}


def gen_params(app_info):
    params = []

    zen_extensions = ['true']
    zenkit_experiments = ['abro_zenplaceholders=exp']
    ab_flags = [None, 'zen_extensions_new_scheme_yabro']

    for platform, versions in app_info.iteritems():
        informers = '2' if platform == 'android' else None
        params.extend([dict(app_version=version, app_platform=platform, geo='213', lang='ru-RU', informersCard=informers, processAssist='1',
                         uuid='0f730a00ff8a443ea2db355519bdd290', zen_extensions=zen_ext, zenkit_experiments=zen_exp, ab_flags=ab)
                       for version in versions
                       for zen_ext in zen_extensions
                       for zen_exp in zenkit_experiments
                       for ab in ab_flags])
    return params


def test_params():
    return gen_params(app_info=app_info)

@allure.feature('api_yabrowser_2', 'zen_extensions_api_yabrowser')
@allure.story('Check zen_extensions format')
@pytest.mark.parametrize('params', test_params())
def test_remapping(params):
    client   = MordaClient(env=env.morda_env())
    response = client.api_yabrowser_2(**params).send()
    assert response.is_ok(), 'Failed to get api-yabrowser response'
    response  = response.json()
    # Самый ранний формат ответа (без zen_id)
    old_format = params['app_platform'] == 'android' and params['app_version'] < '2011100000'

    extension_block = response.get('extension_block')
    topnews_passed  = False
    for item in extension_block.get('zen_extensions'):
        zen_extensions.position_check(item)
        if params['ab_flags'] == 'zen_extensions_new_scheme_yabro':
            if old_format:
                topnews_passed  = True
                continue
            if item.get('zen_id') == 'zen_topnews_vertical':
                topnews_passed  = True
            zen_extensions.zen_id_check(item)
            zen_extensions.short_format_check(item)
            continue
        zen_extensions.base_check(item)
        zen_extensions.block_data_check(item)
        block = item.get('block')
        if old_format:
            # Проверка формата без zen_id
            zen_extensions.no_zen_id_check(item)
            if block and block.get('id') == 'zen_topnews_vertical':
                topnews_passed = True
        else:
            # Проверка формата с zen_id
            zen_extensions.zen_id_check(item)
            if block and block.get('id') == 'topnews_vertical':
                topnews_passed = True
                assert item.get('zen_id') == 'zen_topnews_vertical'
    assert topnews_passed, 'Bad topnews_vertical id or block not found'
