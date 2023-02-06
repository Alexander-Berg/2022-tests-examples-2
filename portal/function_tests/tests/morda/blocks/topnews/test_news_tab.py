# -*- coding: utf-8 -*-
import logging

import allure
import pytest
import re
import json

from common.client import MordaClient
from common.morda import Morda

logger = logging.getLogger(__name__)

@pytest.mark.ticket('HOME-77513')
@allure.feature('function_tests_stable')
@pytest.mark.parametrize('topnews_full', (0, 1))
@pytest.mark.parametrize('geo', (213, 2))
def test_news_tab(topnews_full, geo):
    params = {
        'cleanvars': 'topnews',
        'geo': geo,
        'ab_flags': 'topnews_from_avocado=0:topnews_full={}'.format(topnews_full),
    }
    client = MordaClient()
    url = Morda.get_origin(no_prefix=True, env=client.env)
    response = client.request(params=params, url=url).send()
    assert response.is_ok(), 'Failed to get api-search response'

    json_data = response.json()
    assert 'Topnews' in json_data and 'tabs' in json_data['Topnews']
    tabs = json_data['Topnews']['tabs']

    data = {}
    need_items = {'news': 1, 'region': 1}
    # найти элементы с ключами news и region, элементов всего два
    for item in tabs:
        if item['key'] in need_items:
            data[item['key']] = item
            need_items.pop(item['key'])
            if len(need_items) == 0:
                break
    assert len(data) == 2

    if topnews_full:
        assert data['news']['title'] == u'Главное'
        assert data['region']['title'] == u'Москва' if geo == 213 else u'Санкт-Петербург'
    else:
        assert data['news']['title'] != u'Главное'
        assert data['region']['title'] == u'в Москве' if geo == 213 else u'в Санкт-Петербурге'
