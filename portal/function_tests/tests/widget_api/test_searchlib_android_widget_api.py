# -*- coding: utf-8 -*-
# import json

import allure
import pytest

from common import env, schema
from common.client import MordaClient
from common.geobase import Regions
from common.schema import get_schema_validator

TESTEE = 'widget_api'


"""
Урл для примера запроса
/android_widget_api/2/?app_version_name=7.60&app_version=7060003&app_build_number=49459&model=E6683&os_version=7.1.1&manufacturer=Sony&app_id=ru.yandex.searchplugin.beta&api_key=c8652fcf-2ed1-497e-9cce-3aef2c62d538&cellid=250%2C11%2C122670223%2C4784%2C0&uuid=d7010dc2baf8dd86966039968fa764d1&did=8ab7df65c9085b0780f754c9a4c84b6f&search_token=cc4c275f95500412d9dae0c84fe27e57%3Agejkivodaspehvtm%3A1530732313&lang=ru-RU&app_platform=android&dp=3.0
"""

app_info = {
    'android': ['7060000'],
}

os_versions = {
    'android': ['7.6'],
    'iphone': ['10.0'],
}


def get_regions():
    return [
        Regions.MOSCOW, Regions.SAINT_PETERSBURG,
        Regions.KYIV, Regions.VITEBSK,
        Regions.ASTANA, Regions.ALMATY,
        Regions.WASHINGTON
    ]


def gen_params(app_info, regions, langs, blocks, dps=None):
    res = []
    if dps is None:
        dps = ['1']

    for platform, versions in app_info.iteritems():
        res.extend([dict(app_version=version, app_platform=platform, geo=geo,
                         lang=lang, dp=dp, os_version=os_version, block=block)
                    for os_version in os_versions[platform]
                    for version in versions
                    for geo in regions
                    for lang in langs
                    for dp in dps
                    for block in blocks])

    return res


def test_params():
    params = gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=['ru'],
        blocks=['', 'forecast,short_forecast,traffic_forecast', 'weather']
    )
    return params


@allure.feature(TESTEE)
@allure.story('searchlib_android_widget_api_response')
@pytest.mark.parametrize('params', test_params())
def test_schema(params):
    client = MordaClient(env=env.morda_env())
    response = client.android_widget_api(**params).send().json()
    # print json.dumps(response, indent=4, ensure_ascii=False).encode('utf-8')
    validator = get_schema_validator('schema/widgetsapi_searchlib/widgetsapi-response.json')
    schema.validate_schema(response, validator)
