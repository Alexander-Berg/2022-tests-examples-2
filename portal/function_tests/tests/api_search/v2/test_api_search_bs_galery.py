# -*- coding: utf-8 -*-
import logging

import allure
import pytest
import re

from common import env
from common.client import MordaClient

logger = logging.getLogger(__name__)

app_info = {
    'android': ['20110400'],
}

def gen_params(app_info):
    params = []

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 YaBrowser/20.3.2.282 (beta) Yowser/2.5 Safari/537.36'
    for platform, versions in app_info.iteritems():
        params.extend([dict(app_version=version, app_platform=platform, geo='213', lang='ru-RU', processAssist='1',
                         uuid='0f730a00ff8a443ea2db355519bdd290', zen_extensions='true', informersCard='2', ab_flags='bs_promo_and_popup',
                         bs_promo='1')
                       for version in versions])
    return params

def test_params():
    return gen_params(app_info=app_info)

@allure.feature('api_search_v2', 'bs_promo')
@allure.story('Check bottom sheet promo')
@pytest.mark.parametrize('params', test_params())
def test_remapping(params):
    pytest.skip("very old flapping test, skipping")

    client   = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-yabrowser response'
    response  = response.json()

    # Блоков promo_popup_div и promo_bs_gallery_div не должно быть в layout
    for layout_item in response.get('layout'):
        assert layout_item.get('id') != 'promo_popup_div', 'Found promo_popup_div in layout'
        assert layout_item.get('id') != 'promo_bs_gallery_div', 'Found promo_bs_gallery_div in layout'
    for layout_item in response.get('offline_layout'):
        assert layout_item.get('id') != 'promo_popup_div', 'Found promo_popup_div in layout'
        assert layout_item.get('id') != 'promo_bs_gallery_div', 'Found promo_bs_gallery_div in layout'

    # Блоки promo_popup_div и promo_bs_gallery_div должны быть в block
    # Сейчас promo_popup_div отключен, но могут включить обратно и мы потеряем проверку.
    # Если были бы вечные данные, то не пришлось бы отключать
    # promo_popup_div_exists = False
    promo_bs_gallery_div_exists = False
    for block_item in response.get('block'):
        # if block_item.get('id') == 'promo_popup_div':
            # promo_popup_div_exists = True
        if block_item.get('id') == 'promo_bs_gallery_div':
            promo_bs_gallery_div_exists = True
    # assert promo_popup_div_exists, 'promo_popup_div should be in block'
    assert promo_bs_gallery_div_exists, 'promo_bs_gallery_div should be in block'

    # Проверка формата popup_promos в корне ответа морды
    # assert response.get('popup_promos'), 'no popup_promos in root'
    # for popup_promos_item in response.get('popup_promos'):
    #     assert popup_promos_item.get('id'), 'no id in popup_promos'
    #     layout = popup_promos_item.get('layout')
    #     assert layout, 'no layout in popup_promos'
    #     assert layout.get('type'), 'no type in popup_promos layout'
    #     assert layout.get('id'), 'no id in popup_promos layout'
    #     assert layout.get('heavy') == 0 or layout.get('heavy') == 1, 'no heavy in popup_promos layout'

    # Проверка промо секции в боттом щите
    promo_gallery_section = False
    for section in response.get('services').get('sections'):
        if section.get('id') == 'promo_gallery':
            promo_gallery_section = True
    assert promo_gallery_section, 'promo_gallery_section should be in services->sections'
