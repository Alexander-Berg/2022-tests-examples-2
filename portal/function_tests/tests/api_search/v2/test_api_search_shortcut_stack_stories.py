# -*- coding: utf-8 -*-
import logging

import allure
import pytest
import re

from common import env
from common.client import MordaClient

logger = logging.getLogger(__name__)

app_info = {
    'android': ['211103031'],
}
madm_mocks = 'div_fullscreens=div_fullscreens_mock_1:shortcuts_settings_v2=shortcuts_settings_v2_mock_1:shortcuts_settings_stack=shortcuts_settings_stack_mock_1'

def gen_params(app_info):
    params = []

    for platform, versions in app_info.iteritems():
        params.extend([dict(app_version=version, app_platform=platform, geo='213', lang='ru-RU', processAssist='1', morda_ng='1',
                         zen_extensions='true', informersCard='2', bs_promo='1', madm_mocks=madm_mocks, ab_flags='geoblock_pp:redesign_div_pp')
                       for version in versions])
    return params

def test_params():
    return gen_params(app_info=app_info)

# Раскомментить когда выкатится фронт фулскрина
'''
@allure.feature('function_tests_stable', 'bs_promo')
@allure.story('Check stack shortcut and stories')
@pytest.mark.parametrize('params', test_params())
def test_remapping(params):
    client   = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get response'
    response  = response.json()

    logger.info(response.get('madm_mock_error'))

    # Проверяем ошибку при подстановке моков
    assert response.get('madm_mock_error') == None, response.get('madm_mock_error')

    # Фуллскринов не должно быть в layout
    for layout_item in response.get('layout'):
        assert layout_item.get('id') != 'fullscreen1', 'Found fullscreen1 in layout'
        assert layout_item.get('id') != 'fullscreen2', 'Found fullscreen2 in layout'
        assert layout_item.get('id') != 'fullscreen3', 'Found fullscreen3 in layout'
        assert layout_item.get('id') != 'fullscreen4', 'Found fullscreen4 in layout'
    for layout_item in response.get('offline_layout'):
        assert layout_item.get('id') != 'fullscreen1', 'Found fullscreen1 in layout'
        assert layout_item.get('id') != 'fullscreen2', 'Found fullscreen2 in layout'
        assert layout_item.get('id') != 'fullscreen3', 'Found fullscreen3 in layout'
        assert layout_item.get('id') != 'fullscreen4', 'Found fullscreen4 in layout'

    # Фуллскрины должны быть в block
    found_fullscreen1 = 0
    found_fullscreen2 = 0
    found_fullscreen3 = 0
    found_fullscreen4 = 0
    for block_item in response.get('block'):
        if block_item.get('id') == 'fullscreen1':
            found_fullscreen1 = 1
        if block_item.get('id') == 'fullscreen2':
            found_fullscreen2 = 1
        if block_item.get('id') == 'fullscreen3':
            found_fullscreen3 = 1
        if block_item.get('id') == 'fullscreen4':
            found_fullscreen4 = 1

    assert found_fullscreen1, 'found_fullscreen1 should be in block'
    assert found_fullscreen2, 'found_fullscreen2 should be in block'
    assert found_fullscreen3, 'found_fullscreen3 should be in block'
    assert found_fullscreen4, 'found_fullscreen4 should be in block'

    # Проверяем наличие шортката stack в блоке информеров и диплинки в нем
    found_informers = 0
    correct_url1 = 'div-stories://open?stories=fullscreen1,fullscreen2;fullscreen3,fullscreen4;'
    correct_url2 = 'div-stories://open?stories=fullscreen3,fullscreen4;fullscreen1,fullscreen2;'
    for zen_item in response.get('extension_block').get('zen_extensions'):
        if zen_item.get('zen_id') == 'informers':
            found_informers = 1
            id = zen_item.get('block').get('data').get('states')[0].get('div').get('items')[0].get('items')[0].get('items')[0].get('div_id')
            assert id == 'shortcuts_stack', 'Cannot find stack shortcut in informers block'
            url1 = zen_item.get('block').get('data').get('states')[0].get('div').get('items')[0].get('items')[0].get('items')[0].get('states')[0].get('div').get('action').get('url')
            assert url1 == correct_url1, 'Wrong deeplink in stack shortcut, should be: ' + correct_url1
            url2 = zen_item.get('block').get('data').get('states')[0].get('div').get('items')[0].get('items')[0].get('items')[0].get('states')[1].get('div').get('action').get('url')
            assert url2 == correct_url2, 'Wrong deeplink in stack shortcut, should be: ' + correct_url2

    assert found_informers, 'informers block should be in zen_extensions'
'''