# -*- coding: utf-8 -*-
import logging

import allure
import pytest
import re
import json

from common import env
from common.client import MordaClient

logger = logging.getLogger(__name__)
yellow_skin_regexp = re.compile(r'"yellowskin://([^"]+)"')
yellow_skin_regexp = re.compile(r'"yellowskin://([^"]+)"')
yellow_skin_colors = re.compile(r'[\?&](?:buttons_color|omnibox_color|status_bar_theme|background_color|text_color|primary_color|secondary_color)=')
geohelper_flag     = re.compile(r'[\?&]flags=[^&]+')

@pytest.mark.ticket('HOME-76751')
@allure.feature('function_tests_stable')
@pytest.mark.parametrize('with_palette', (0, 1))
def test_yellowsin(with_palette):
    params = {
        'app_platform': 'android',
        'app_version':  21110703,
        'geo_by_settings': 213,
        'informersCard': 2,
        'lang': 'ru-RU',
        'with_palette': with_palette,
        'ab_flags': 'topnews_extended=0', 
    }

    client   = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'

    content = response.content()
    ys = yellow_skin_regexp.findall(content)
    assert ys, 'can not find yellowskin marker in response'
    assert len(ys) > 10, 'too less yellowskin links'

    colors = []
    for item in ys:
        col = yellow_skin_colors.findall(item)
        if col:
            colors.append(col)

    json_data = response.json()
    assert 'heavy_req' in json_data and 'url' in json_data['heavy_req']
    heavy_req_url = json_data['heavy_req']['url']

    # с with_palette=1 в yellowskin не должно быть buttons_color omnibox_color status_bar_theme background_color text_color
    # а в heavy_req.url должен быть флаг not_force_ys_color
    mo = geohelper_flag.search(heavy_req_url)
    if with_palette:
        assert len(colors) == 0
        assert mo and 'not_force_ys_color' in mo.group(0)
    else:
        assert len(colors)
        assert (not mo) or ('not_force_ys_color' not in mo.group(0))

@pytest.mark.ticket('HOME-77649')
@allure.feature('function_tests_stable')
@pytest.mark.parametrize('with_palette', (0, 1))
def test_news_title_yellowsin(with_palette):
    params = {
        'app_platform': 'android',
        'app_version':  21110703,
        'geo_by_settings': 213,
        'informersCard': 2,
        'lang': 'ru-RU',
        'with_palette': with_palette,
        'ab_flags': 'topnews_extended=0', 
    }

    client   = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'

    json_data = response.json()
    topnews = None
    for item in json_data['block']:
        if item['id'] == 'topnews':
            topnews = item
            break
    assert topnews is not None, 'can not find block topnews'

    # проверяем что в блоке topnews yellowskin не пропали
    ys = yellow_skin_regexp.findall(json.dumps(topnews, indent=1))
    assert ys, 'can not find yellowskin marker in topnews'
    assert len(ys) > 10, 'too less yellowskin links'
