# -*- coding: utf-8 -*-
import logging

import allure
import pytest
import re

from common import zen_extensions
from common import env
from common.client import MordaClient

logger = logging.getLogger(__name__)
color_regexp = re.compile(r'"@{([^\}]+)}"')

@pytest.mark.ticket('HOME-76511')
@allure.feature('function_tests_stable')
@pytest.mark.parametrize('ab_flag', (0, 1))
def test_palette(ab_flag):
    params = {
        'ab_flags': 'news_degradation=0:topnews_extended=1:topnews_extended_from_avocado={}'.format(ab_flag),
        'app_platform': 'iphone',
        'app_version': 89000000,
        'geo_by_settings': 213,
        'informersCard': 2,
        'lang': 'ru-RU',
    }

    client   = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'

    content = response.content()
    colors  = color_regexp.findall(content)
    assert colors, 'can not find color marker \'@{\' in response'

    json_data  = response.json()
    assert 'palette' in json_data and 'dark' in json_data['palette'] and 'light' in json_data['palette']

    palette = {
        'dark': {},
        'light': {}
    }
    for theme in json_data['palette']:
        for item in json_data['palette'][theme]:
            palette[theme][item['name']] = 1

    errors = []
    for color in colors:
        for theme in palette:
            if color not in palette[theme]:
                errors.append("can not find color:{} in palette[{}]".format(color, theme))

    assert len(errors) == 0, errors
