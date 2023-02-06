# -*- coding: utf-8 -*-
import logging

import allure
import pytest
import re

from common import zen_extensions
from common import env
from common.client import MordaClient

logger = logging.getLogger(__name__)

alert_regex = re.compile(r'(informers)|(zen_alert_\d)')

ZEN_ID_FORMAT_ANDROID = 11010000
SHORT_FORMAT_ANDROID  = 20070300
# Алерты и информер не работают по схеме короткого ответа до версии 20080500
SHORT_FORMAT_ALERT_ANDROID = 20080500

ZEN_ID_FORMAT_IOS      = 38000000
SHORT_FORMAT_IOS       = 110000000
# не может быть меньше версии короткого ответа
SHORT_FORMAT_ALERT_IOS = 110000000

@allure.feature('api_search_v2', 'zen_extensions_api_search')
@allure.story('Check zen_extensions format')
@pytest.mark.parametrize(('platform', 'version', 'ab_flag'), [
    ['android', ZEN_ID_FORMAT_ANDROID - 1,  None],# old format
    ['android', ZEN_ID_FORMAT_ANDROID,      None],# zen_id format
    ['android', SHORT_FORMAT_ANDROID,       None],# short format
    ['android', SHORT_FORMAT_ALERT_ANDROID, None],# short format + short alert
    ['iphone',  ZEN_ID_FORMAT_IOS - 1,      None],# old format
    ['iphone',  ZEN_ID_FORMAT_IOS,          None],# zen_id format
    ['iphone',  SHORT_FORMAT_IOS,           None],# short format
    ['iphone',  SHORT_FORMAT_ALERT_IOS,     None],# short format + short alert

    # short format only for zen_id format
    ['android', ZEN_ID_FORMAT_ANDROID,      'zen_extensions_new_scheme'],
    ['android', SHORT_FORMAT_ANDROID,       'zen_extensions_new_scheme'],
    ['android', SHORT_FORMAT_ALERT_ANDROID, 'zen_extensions_new_scheme'],
    ['iphone',  ZEN_ID_FORMAT_IOS,          'zen_extensions_new_scheme'],
    ['iphone',  SHORT_FORMAT_IOS,           'zen_extensions_new_scheme'],
    ['iphone',  SHORT_FORMAT_ALERT_IOS,     'zen_extensions_new_scheme'],

    # short format only for zen_id format. bulk response
    ['iphone',  ZEN_ID_FORMAT_IOS,      'true_avocado=1:topnews_extended_from_avocado=1:topnews_extended=1'],
    ['iphone',  SHORT_FORMAT_IOS,       'true_avocado=1:topnews_extended_from_avocado=1:topnews_extended=1'],
    ['iphone',  SHORT_FORMAT_ALERT_IOS, 'true_avocado=1:topnews_extended_from_avocado=1:topnews_extended=1'],
])
def test_remapping(platform, version, ab_flag):
    params = {
        "ab_flags": ab_flag,
        "app_platform": platform,
        "app_version": version,
        "geo": "213",
        "informersCard": "2",
        "lang": "ru-RU",
        "processAssist": "1",
        "uuid": "0f730a00ff8a443ea2db355519bdd290",
        "zen_extensions": "true",
    }

    client   = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'

    response  = response.json()
    android = platform == 'android'
    iphone  = platform == 'iphone'

    # Сокращенный формат ответа
    short_format_android = android and ab_flag
    # на ios короткий формат включаяется либо флагом, либо версией
    short_format_iphone = iphone and ((ab_flag and 'zen_extensions_new_scheme' in ab_flag) or version >= SHORT_FORMAT_IOS)
    short_format = short_format_android or short_format_iphone    

    # Самый ранний формат ответа (без zen_id)
    old_format = ((android and version < ZEN_ID_FORMAT_ANDROID) or (iphone and version < ZEN_ID_FORMAT_IOS))

    for item in response.get('extension_block').get('zen_extensions'):
        zen_extensions.position_check(item)

        if old_format:
            zen_extensions.block_data_check(item)
            zen_extensions.base_check(item)
        else:
            # zen_id format
            if not short_format:
                zen_extensions.block_data_check(item)
                zen_extensions.base_check(item)
                zen_extensions.zen_id_check(item)
            else:
                if short_format_android:
                    # Алерты и информер не работают по схеме короткого ответа до версии SHORT_FORMAT_ALERT_ANDROID
                    short_format_check(item, version, SHORT_FORMAT_ALERT_ANDROID)
                else:
                    # Алерты и информер не работают по схеме короткого ответа до версии SHORT_FORMAT_ALERT_IOS
                    short_format_check(item, version, SHORT_FORMAT_ALERT_IOS)

def short_format_check(item, app_version, informer_version):
    zen_extensions.zen_id_check(item)
    if app_version < informer_version and alert_regex.search(item.get('zen_id')):
        zen_extensions.base_check(item)
        zen_extensions.block_data_check(item)
    else:
        zen_extensions.short_format_check(item)
