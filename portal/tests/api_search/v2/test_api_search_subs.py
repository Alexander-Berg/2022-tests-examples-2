# -*- coding: utf-8 -*-
import allure
import pytest

from api_search_common import gen_params
from common import env
from common.client import MordaClient
from common.geobase import Regions


REQUIRED_FIELDS = ['default', 'description', 'title', 'type']

CONFIG = {
    'acards': {
        'app': {
            'android': 6060000,
            'iphone': 3050100
        },
        'required_fields': ['topic_card', 'topic_push'] + REQUIRED_FIELDS
    },
    'cards': {
        'app': {
            'android': 6060000
        },
        'required_fields': ['topic_card'] + REQUIRED_FIELDS
    },
    'pushes': {
        'app': {
            'android': 6000000
        },
        'required_fields': ['topic_push'] + REQUIRED_FIELDS
    },
    'push_groups': {
        'app': {
            'android': 0,
            'iphone': 0
        },
        'required_fields': ['group', 'description', 'title']
    }
}

BLOCK = 'subs'

"""
Урл для примера запроса
yandex.ru/portal/subs/config/0?app_version=7010000&os_version=6.0.1&app_platform=android&geo_by_settings=213
"""

app_info = {
    'android': [5010000, 6000000, 6060000],
    'iphone': [2050100, 3050100],
}


def get_regions():
    return [
        Regions.MOSCOW,
    ]


def subs_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru']
    )


@allure.step('Validate subs response')
def validate_response(response, app_platform=None, app_version=None, **kwargs):
    valid_response_text = 'Subs response valid for platform {} and version {}'.format(app_platform, app_version)
    assert sorted(response.keys()) == sorted(CONFIG.keys()), valid_response_text
    for name, settings in CONFIG.items():
        if app_platform not in settings['app'] or app_version < settings['app'][app_platform]:
            assert len(response[name]) == 0, valid_response_text
            continue
        for row in response[name]:
            for field in settings['required_fields']:
                assert field in row, valid_response_text


@allure.feature('morda', BLOCK)
@allure.story('api_search_v2_subs_response')
@pytest.mark.parametrize('params', subs_params())
def test_subs_response(params):
    client = MordaClient(env=env.morda_env())
    response = client.subs_config_0(**params).send().json()
    validate_response(response, **params)
