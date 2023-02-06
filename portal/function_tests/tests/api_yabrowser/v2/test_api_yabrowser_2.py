# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from collections import OrderedDict
from common import env, schema
from common.client import MordaClient
from common.geobase import Regions
from common.schema import get_schema_validator

from common.url import check_urls_params, check_urls
from urlparse import urlsplit, parse_qs

logger = logging.getLogger(__name__)

TESTEE = 'api_yabrowser_2'


app_info = {
    'android': ['1901000000', '1901100000'],
    'iphone': ['1901000000']
}

os_versions = {
    'android': ['7.6'],
    'iphone': ['10.0'],
}

user_agents = {
    'android': 'Mozilla/5.0 (Linux; Android 8.1.0; Redmi 6) AppleWebKit/537.36' +
               ' (KHTML, like Gecko) Chrome/73.0.3683.103 YaBrowser/{} Mobile Safari/537.36',
    'iphone': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.15' +
               ' (KHTML, like Gecko) Version/12.0 YaBrowser/{} Mobile/15E148 Safari/605.1'
}

all_langs = ['ru', 'uk', 'be', 'kk']
dps = ['1', '1.5', '2', '3', '4']
make_morda_first_feeds = [None, 0, 1]


def get_app_version_name(app_version):
    int_app_version = int(app_version)
    major = int_app_version // 100000000
    minor = (int_app_version % 100000000) / 1000000
    fix = ((int_app_version % 1000000) / 100000)

    return '{}.{}.{}'.format(major, minor, fix)


def create_user_agent(app_platform, app_version):
    if app_platform not in user_agents:
        return None
    return user_agents[app_platform].format(get_app_version_name(app_version))


def get_regions():
    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG,
            Regions.MINSK, Regions.VITEBSK, Regions.ASTANA]


def gen_params(app_info, regions, langs, dps=None, uuids=None, make_morda_first_feeds=None):
    res = []
    if dps is None:
        dps = ['1']
    if uuids is None:
        uuids = ['0f730a00ff8a443ea2db355519bdd290']  # [uuid.uuid4()]

    for platform, versions in app_info.iteritems():
        res.extend([dict(app_version=version, app_platform=platform, geo=geo, lang=lang, dp=dp, os_version=os_version,
                         uuid=uuid_local, make_morda_first_feed=make_morda_first_feed,
                         user_agent=create_user_agent(platform, version))
                    for os_version in os_versions[platform]
                    for version in versions
                    for geo in regions
                    for lang in langs
                    for dp in dps
                    for uuid_local in uuids
                    for make_morda_first_feed in make_morda_first_feeds])

    return res


def test_params():
    params = gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=all_langs,
        dps=dps,
        make_morda_first_feeds=make_morda_first_feeds,
    )

    return params


def ids(value):
    if isinstance(value, (dict,)):
        ordered = OrderedDict(sorted(value.items()))
        return ', '.join(['='.join([str(k), str(v)]) for k, v in ordered.items()])


@pytest.mark.yasm
@allure.feature(TESTEE, 'api_yabrowser_2_schema')
@allure.story('api_yabrowser_2_schema')
@pytest.mark.parametrize('params', test_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient(env=env.morda_env())
    response = client.api_yabrowser_2(**params).send()
    assert response.is_ok(), 'Failed to get api-yabrowser response'
    data = response.json()

    validator = get_schema_validator('schema/yabrowserapi/{}/{}/api/search/2/yabrowserapi-response.json'.format(
        params['app_platform'],
        get_app_version_name(params['app_version'])))

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

    yasm.add_to_signal('morda_api_yabrowser_2_schema_{}_{}_passed_tttt'.format(platform, version), passed)
    yasm.add_to_signal('morda_api_yabrowser_2_schema_{}_{}_failed_tttt'.format(platform, version), failed)


@allure.feature(TESTEE, 'yabrowser_vertical')
class TestApiYabrowserVertical(object):
    def setup_class(cls):
        client = MordaClient(env=env.morda_env())
        params = dict(
            app_version='1901100000',
            app_platform='android',
            geo='213',
            lang='ru',
            make_morda_first_feed=1,
        )
        response = client.api_yabrowser_2(**params).send()
        cls.response = response.json()

    # В карточках ябро не должно быть урлов со схемами, отличными от  http/https
    @allure.story('check urls on http/https')
    def test_check_urls_schem(self):
        skip_fields = ['menu', 'menu_item_collapse', 'menu_item_expand', 'menu_items']
        for block in self.response.get('block'):
            check_urls(block.get('data'), '^https?', skip_fields)

    # В урлах get-параметр  utm_source равен yabro
    @allure.story('utm_source=yabro')
    def test_check_urls_utm(self):
        for block in self.response.get('block'):
            if (block.get('id') == 'search'):
                continue
            check_urls_params(block.get('data'), 'utm_source', 'yabro|yabro_newtab|widget|morda|alert')


@allure.feature(TESTEE, 'yabrowser_mordanavigate')
class TestApiYabrowserMordanavigate(object):
    def setup_class(cls):
        client = MordaClient(env=env.morda_env())
        params = dict(
            app_version='1905426832',
            app_platform='android',
            geo='213',
            lang='ru',
            make_morda_first_feed=1,
        )
        response = client.api_yabrowser_2(**params).send()
        cls.response = response.json()

    # В карточках ябро с версии 1905426832 могут быть урлы со схемой mordanavigate
    @allure.story('check urls on http/https/mordanavigate')
    def test_check_urls_schema(self):
        skip_fields = ['menu', 'menu_item_collapse', 'menu_item_expand', 'menu_items']
        for block in self.response.get('block'):
            check_urls(block.get('data'), '^(https?|mordanavigate)', skip_fields)

