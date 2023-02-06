# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict

import pytest
# import uuid

from common import schema
from common.http import get_request_results_parallel
from common.client import GeohelperClient
from common.utils import get_field
from os import listdir
import re

logger = logging.getLogger(__name__)

app_info = {
    'android': [5080001, 6010001, 6020001, 6030000, 6040101, 6040501, 8010000],
    'iphone': [3010000, 3010100, 3020100]
}

os_versions = {
    'android': ['7.6'],
    'iphone': ['10.0'],
}

all_langs = ['ru', 'uk', 'be', 'kk']
dps = ['1', '1.5', '2', '3', '4']

user_agents = {
    'android': 'Mozilla/5.0 (Linux; Android 7.0; FS518 Build/NRD90M; wv) AppleWebKit/537.36' +
               ' (KHTML, like Gecko) Version/4.0 Chrome/64.0.3282.137 Mobile Safari/537.36 YandexSearch/{}',
    'iphone': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15' +
               ' (KHTML, like Gecko) Mobile/16D57 YaBrowser/19.5.2.38.10 YaApp_iOS/{}'
}


def get_app_version_name(app_version):
    int_app_version = int(app_version)
    major = int_app_version // 1000000
    minor = (int_app_version % 1000000) / 10000
    fix = (int_app_version % 10000) / 100

    return '{}.{}{}'.format(major, minor, fix)


def create_user_agent(app_platform, app_version):
    if app_platform not in user_agents:
        return None
    return user_agents[app_platform].format(get_app_version_name(app_version))


def get_block_data(client, block, params):
    params['block'] = block
    res = client.api_search_2(**params).send()
    assert res.is_ok(), 'Failed to get api-search response'
    data = res.json()

    if block in ['edadeal']:
        gohelper_client = GeohelperClient(url=get_field(data, 'heavy_req.url'))
        res = gohelper_client.searchapp_get(post_data=get_field(data, 'heavy_req.payload')).send()
        data = res.json()

    return next((b for b in data.get('block', []) if b['id'] == block), None)


def get_top_level_data(client, key, params):
    res = client.api_search_2(**params).send()
    assert res.is_ok(), 'Failed to get api-search response'
    data = res.json()

    return data.get(key)


def validate_schema_for_block(client, block, params, yasm=None, allow_not_exist=False, custom_schema=False):
    block_data = get_block_data(client, block, params)

    if block_data is None:
        msg = 'Block {} not found in response'.format(block)
        if allow_not_exist:
            logger.debug(msg)
            add_schema_signal(yasm, block, params['app_platform'], params['app_version'], True)
            return
        else:
            add_schema_signal(yasm, block, params['app_platform'], params['app_version'], False)
            pytest.fail(msg)

    validator = schema.get_api_search_2_validator(params['app_platform'], params['app_version'],
                                                  custom_schema if custom_schema else block)
    try:
        schema.validate_schema(block_data, validator)
        add_schema_signal(yasm, block, params['app_platform'], params['app_version'], True)
    except Exception as e:
        add_schema_signal(yasm, block, params['app_platform'], params['app_version'], False)
        raise e


def add_schema_signal(yasm, block, platform, version, is_ok):
    if not yasm:
        return
    passed = 1 if is_ok else 0
    failed = 1 - passed

    yasm.add_to_signal('morda_api_search_2_{}_schema_{}_{}_passed_tttt'.format(block, platform, version), passed)
    yasm.add_to_signal('morda_api_search_2_{}_schema_{}_{}_failed_tttt'.format(block, platform, version), failed)


def check_http_codes(client, yasm, block, params, urls_provider):
    block_data = get_block_data(client, block, params)
    if (block_data['type'] == 'div'):
        return
    urls = urls_provider(params['app_platform'], block_data)
    ping_urls(urls, yasm, 'morda_api_search_2_' + block + '_http_code_{}_tttt')


def check_static_codes(client, yasm, block, params, urls_provider):
    block_data = get_block_data(client, block, params)
    urls = urls_provider(block_data)
    ping_urls(urls, yasm, 'morda_api_search_2_' + block + '_static_code_{}_tttt')


def gen_params(app_info, regions, langs, dps=None, uuids=None, os_versions=os_versions):
    res = []
    if dps is None:
        dps = ['1']
    if uuids is None:
        uuids = ['0f730a00ff8a443ea2db355519bdd290']  # [uuid.uuid4()]

    for platform, versions in app_info.iteritems():
        res.extend([dict(app_version=version, app_platform=platform, geo=geo, lang=lang, dp=dp, os_version=os_version,
                         uuid=uuid_local, user_agent=create_user_agent(platform, version))
                    for os_version in os_versions[platform]
                    for version in versions
                    for geo in regions
                    for lang in langs
                    for dp in dps
                    for uuid_local in uuids])

    return res


def get_all_version(platform):
    if platform == 'iphone':
        platform = 'ios'
    versions_short = listdir('schema/{}'.format(platform))
    versions = list()
    for v in versions_short:
        (major, minor, fix) = (0, 0, 0)
        split_version = v.split('.') + [0, 0, 0]
        major = split_version[0]
        minor = split_version[1]
        fix = split_version[2]

        if (major.isdigit() and minor.isdigit()):
            int_major = int(major);
            int_minor = int(minor);
            int_fix = int(fix);

            if (int_minor < 10):
                int_minor = int_minor * 10

            int_minor = int_minor % 10 + (int_minor - int_minor % 10) * 10
            versions.append(int_major * 1000000 + int_minor * 100 + int_fix)

    versions.sort()
    return versions


def create_app_info(app_info_conf):
    app_info = dict()
    for platform in app_info_conf:
        versions = get_all_version(platform)
        start_index = 0
        finish_index = len(versions)

        start = app_info_conf[platform].get('start')
        finish = app_info_conf[platform].get('finish')
        if start:
            list_version_for_start = [v for v in versions if v >= int(start)]
            if len(list_version_for_start) == 0:
                app_info[platform] = []
                continue

            start_vers = min(list_version_for_start)
            start_index = versions.index(start_vers)

        if finish:
            list_version_for_finish = [v for v in versions if v <= int(finish)]
            if len(list_version_for_finish) == 0:
                app_info[platform] = []
                continue
            finish_vers = max(list_version_for_finish)
            finish_index = versions.index(finish_vers)

        app_info[platform] = versions[start_index:finish_index+1]

    return app_info


def ping_urls(urls, yasm=None, signal=None):
    urls = [url for url in urls if url]
    ping_results = get_request_results_parallel(urls)

    result = {
        '2xx': len([res for res in ping_results if res.response is not None and 200 <= res.response.status_code < 300]),
        '3xx': len([res for res in ping_results if res.response is not None and 300 <= res.response.status_code < 400]),
        '4xx': len([res for res in ping_results if res.response is not None and 400 <= res.response.status_code < 500]),
        '5xx': len([res for res in ping_results if
                    res.error or (res.response is not None and res.response.status_code >= 500)])
    }

    if yasm is not None and signal is not None:
        for k, v in result.iteritems():
            yasm.add_to_signal(signal.format(k), v)

    if result['4xx'] + result['5xx']:
        failed = '\n'.join([res.format_error() for res in ping_results
                            if res.error or (res.response is not None and res.response.status_code >= 400)])
        logger.error('Failed requests:\n' + failed)
        pytest.fail('Some requests returned 4xx or 5xx')

    return result

def ids(value):
    if isinstance(value, (dict,)):
        ordered = OrderedDict(sorted(value.items()))
        return ', '.join(['='.join([str(k), str(v)]) for k, v in ordered.items()])

def ids_without_spaces(value):
    if isinstance(value, (dict,)):
        print(value)
        ordered = OrderedDict(sorted(value.items()))
        # we must not use spaces in ids. Because in this case we can not use -k(e.g. -k 'test_static_code[app_platform=android, app_version=5080001'
        # doesn't work)
        def replace_spaces(text):
            return re.sub(r'\s+', '-', text)

        return '-'.join(['='.join([replace_spaces(str(k)), replace_spaces(str(v))]) for k, v in ordered.items()])
