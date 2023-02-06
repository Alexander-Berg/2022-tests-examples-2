# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging
import allure
import pytest
import re
import json

from common import schema
from common.client import GeohelperClient
from hamcrest import equal_to

logger = logging.getLogger(__name__)

langs = (
    'ru',
    'uk',
    'tr',
)

geoids = (213, 2)

sample_coordinates = (
    (55.73908704, 37.58369507),
)

sample_groups = (
    json.dumps({'poi': [{'group': 'food', 'subgroups': ['где поесть']},
                        {'group': 'shops', 'subgroups': ['магазины продуктов']},
                        {'group': 'gaz', 'subgroups': ['азс']},
                        {'group': 'atm', 'subgroups': ['банкоматы']},
                        {'group': 'drugstore', 'subgroups': ['аптеки']}]}),
)


regex = r'errors count: (\d*), (.*)'


# FIXME: Возможно имеет смысл сделать отправку сигналов YASM
# @pytest.mark.yasm
@allure.feature('geohelper')
@allure.story('check via /check')
def test_check_availability():
    client = GeohelperClient()
    res = client.get_check().send()
    assert res.is_ok(equal_to(200)), 'Failed to send geohelper check request'
    answer_content = res.response.content
    matches = re.search(regex, answer_content)
    assert matches.group(1) == '0', 'Geohelper check errors count not equal to zero'


# @pytest.mark.yasm
@allure.feature('geohelper')
@allure.story('check touch-morda exports')
@pytest.mark.parametrize('coordinates', sample_coordinates)
@pytest.mark.parametrize('lang', langs)
@pytest.mark.parametrize('geoid', geoids)
@pytest.mark.parametrize('groups', range(0, len(sample_groups)))
def test_morda_export(coordinates, lang, geoid, groups):
    client = GeohelperClient()
    res = client.simple_get(params={
        'lat': coordinates[0],
        'lon': coordinates[1],
        'lang': lang,
        'geoid': geoid,
    }, post_data=sample_groups[groups]).send()
    data = res.json()
    schema.validate_schema_by_service(data, 'geohelper')
