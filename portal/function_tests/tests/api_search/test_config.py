# -*- coding: utf-8 -*-
import json
import logging
from pprint import pformat

import allure
import pytest
from deepdiff import DeepDiff

from common import env
from common.http import Req
from common.morda import Morda

logger = logging.getLogger(__name__)

PARAMS = [
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '5000000', 'app_platform': 'android', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '5000000', 'app_platform': 'apad', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '5050004', 'app_platform': 'android', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '5050004', 'app_platform': 'apad', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '5060000', 'app_platform': 'android', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '5060000', 'app_platform': 'apad', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '5090000', 'app_platform': 'android', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '5090000', 'app_platform': 'apad', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '6000000', 'app_platform': 'android', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '6000000', 'app_platform': 'apad', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '6000000', 'app_platform': 'android', 'os_version': '6.0',
     'manufacturer': 'huawei', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '6000000', 'app_platform': 'apad', 'os_version': '6.0',
     'manufacturer': 'huawei', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '6000000', 'app_platform': 'android', 'os_version': '6.1',
     'manufacturer': 'huawei', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '6000000', 'app_platform': 'apad', 'os_version': '6.1',
     'manufacturer': 'huawei', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '2000000',
     'app_platform': 'iphone', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '2000000',
     'app_platform': 'ipad', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '2030100',
     'app_platform': 'iphone', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '2030100',
     'app_platform': 'ipad', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '2030200',
     'app_platform': 'iphone', 'lang': 'tr-TR'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '2030200',
     'app_platform': 'ipad', 'lang': 'tr-TR'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '2030000',
     'app_platform': 'iphone', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin', 'app_version': '2030000',
     'app_platform': 'ipad', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin.fb', 'app_version': '4000000', 'app_platform': 'android', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'},
    {'app_id': 'ru.yandex.searchplugin.fb', 'app_version': '4000000', 'app_platform': 'apad', 'os_version': '5.1.1',
     'manufacturer': 'samsung', 'lang': 'ru-RU'}
]


def get_params(filename):
    with open(filename) as f:
        content = f.readlines()
    return [json.loads(a) for a in content]


def modify_float_2_int(data):
    if isinstance(data, list):
        for i, d in enumerate(data):
            if isinstance(d, float) and int(d) == d:
                data[i] = int(d)
            else:
                modify_float_2_int(d)
    elif isinstance(data, dict):
        for key in data:
            d = data[key]
            if isinstance(d, float) and int(d) == d:
                data[key] = int(d)
            else:
                modify_float_2_int(d)
    else:
        return 1


def get_old_config(host, params):
    data = Req('https://{}/mobilesearch/config/searchapp'.format(host),
               params=params, allow_retry=True, retries=10).send().json()
    data['plugins'] = data['plugins'].replace(' ', '')
    data['banners'] = data['banners'].replace(' ', '')
    data['snippets'] = data['snippets'].replace(' ', '')
    data['wizards'] = data['wizards'].replace(' ', '')
    data['ranking']['voice']['type_or_counter_prefix_list'] = data['ranking']['voice'][
        'type_or_counter_prefix_list'].replace(' ', '')
    modify_float_2_int(data)
    return data


def get_new_config(params):
    return Req('https://{}.yandex.ru/portal/mobilesearch/config/searchapp'.format(
        Morda._get_env_prefix('www', env=env.morda_env())), params=params, allow_retry=True, retries=10).send().json()


@allure.feature('api_search')
@allure.story('config')
@pytest.mark.parametrize('params', get_params('a.dat'))
def test_config_compare(params):
    old = get_old_config('mobile.yandex.net', params)
    new = get_new_config(params)

    with allure.step('Compare configs'):
        ddiff = DeepDiff(old, new, ignore_order=True)
        if ddiff != {}:
            allure.attach('diff', pformat(ddiff))
            logger.error(pformat(ddiff))
            pytest.fail('Configs are different')


@allure.feature('api_search')
@allure.story('config_beta')
@pytest.mark.parametrize('params', get_params('b.dat'))
def test_config_compare_beta(params):
    old = get_old_config('beta.mobsearch.yandex.ru', params)
    new = get_new_config(params)

    with allure.step('Compare configs'):
        ddiff = DeepDiff(old, new, ignore_order=True)
        if ddiff != {}:
            allure.attach('diff', pformat(ddiff))
            logger.error(pformat(ddiff))
            pytest.fail('Configs are different')
