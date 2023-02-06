# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from common import env, schema
from common.client import MordaClient
from common.geobase import Regions
from common.schema import get_schema_validator
from collections import OrderedDict

logger = logging.getLogger(__name__)

TESTEE = 'widget_api'


# Sample request:
# /portal/api/ios_widget/2/?afisha_version=3&app_build_number=352&app_id=ru.yandex.mobile.navigator.SearchWidgetIntegration&app_platform=iphone&app_version=2.0.2&app_version_name=2.02&country=RU&did=F6BE23AB-B01B-403B-8FA6-6A0DC7B283B3&dp=3.0&lang=ru&lat=56.0126042384481&lon=37.84743896476396&manufacturer=Apple&model=iPhone10%2C5&os_version=12.1.4&size=1242%2C2208&uuid=8b98de0b78d6d51d0ee5c3e4ba394019
#


app_info = {
    'iphone': ['2.0.2']
}

os_versions = {
    'iphone': ['12.1.4'],
}

all_langs = ['ru', 'uk', 'be', 'kk']
dps = ['1', '1.5', '2', '3', '4']


def get_regions():
    return [Regions.MOSCOW, Regions.MINSK, Regions.KYIV, Regions.LVIV, Regions.ASTANA, Regions.LONDON]


def gen_params(app_info, regions, langs, dps=None, uuids=None):
    res = []
    if dps is None:
        dps = ['1']
    if uuids is None:
        uuids = ['d56634c1-812e-4919-88e8-ce1a93c9b229']  # [uuid.uuid4()]

    for platform, versions in app_info.iteritems():
        res.extend([dict(app_version=version, app_platform=platform, geo=geo, lang=lang, dp=dp, os_version=os_version,
                         uuid=uuid_local)
                    for os_version in os_versions[platform]
                    for version in versions
                    for geo in regions
                    for lang in langs
                    for dp in dps
                    for uuid_local in uuids])

    return res


def test_params():
    params = gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=all_langs,
        dps=dps
    )
    return params


def ids(value):
    if isinstance(value, (dict,)):
        ordered = OrderedDict(sorted(value.items()))
        return ', '.join(['='.join([str(k), str(v)]) for k, v in ordered.items()])


@pytest.mark.yasm
@allure.feature(TESTEE)
@allure.story('api_ioswidget_2_response')
@pytest.mark.parametrize('params', test_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient(env=env.morda_env())
    response = client.api_ioswidget_2(**params).send()
    assert response.is_ok(), 'Failed to get api-ioswidget response'
    data = response.json()
    # print json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8')
    validator = get_schema_validator('schema/api/widgets/ios/widgetsapi-response.json')

    try:
        schema.validate_schema(data, validator)
        add_schema_signal(yasm, params['app_platform'], params['app_version'], True)
    except Exception as e:
        add_schema_signal(yasm, params['app_platform'], params['app_version'], False)
        raise e


def add_schema_signal(yasm, platform, version, is_ok):
    if not yasm:
        return
    passed = 1 if is_ok else 0
    failed = 1 - passed

    yasm.add_to_signal('morda_api_ioswidget_2_schema_{}_{}_passed_tttt'.format(platform, version), passed)
    yasm.add_to_signal('morda_api_ioswidget_2_schema_{}_{}_failed_tttt'.format(platform, version), failed)
