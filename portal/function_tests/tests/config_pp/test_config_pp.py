# -*- coding: utf-8 -*-
from common import schema
from common.client import ConfigppClient
from deepdiff import DeepDiff
from hamcrest import equal_to
import allure
import json
import pytest

devices = [
    {
        'file': 'android_7_answer.json',
        'app_id': 'ru.yandex.searchplugin',
        'app_platform': 'android',
        'app_version': 7000000
    },
    {
        'file': 'iphone_3_5_answer.json',
        'app_id': 'ru.yandex.mobile',
        'app_platform': 'iphone',
        'app_version': 3050000
    },
    {
        'file': 'iphone_4_4_answer.json',
        'app_id': 'ru.yandex.mobile',
        'app_platform': 'iphone',
        'app_version': 4040000
    },
    {
        'file': 'apad_7_answer.json',
        'app_id': 'ru.yandex.searchplugin',
        'app_platform': 'apad',
        'app_version': 7000000
    }
]

recent_services_matchers_devices = [
    {
        'app_platform': 'android',
        'app_version': 9049999,
        'recent_services_matchers': False,
    },
    {
        'app_platform': 'android',
        'app_version': 9050000,
        'recent_services_matchers': True,
    },
    {
        'app_platform': 'iphone',
        'app_version': 63999999,
        'recent_services_matchers': False,
    },
    {
        'app_platform': 'iphone',
        'app_version': 64000000,
        'recent_services_matchers': True,
    }
]


@allure.feature('config_pp')
def test_availability():
    client = ConfigppClient()
    res = client.simple_get().send()
    assert res.is_ok(equal_to(200))


@allure.feature('config_pp')
def test_schema():
    client = ConfigppClient()
    res = client.simple_get().send()
    data = res.json()
    schema.validate_schema_by_service(data, 'config_pp')


@allure.feature('config_pp')
def test_cgi_params_zero():
    json_exp = {}
    with open('./tests/config_pp/default_answer.json') as f:
        json_exp = json.load(f)

    client = ConfigppClient()
    res = client.simple_get().send()
    data = res.json()

    assert not DeepDiff(data, json_exp, ignore_order=True)


@allure.feature('config_pp')
@pytest.mark.parametrize('device', devices)
def test_cgi_params_device(device):
    json_exp = {}
    with open('./tests/config_pp/' + device['file']) as f:
        json_exp = json.load(f)

    client = ConfigppClient()
    res = client.simple_get(params={
        'app_id': device['app_id'],
        'app_platform': device['app_platform'],
        'app_version': device['app_version']
        }).send()
    data = res.json()
    # В metaInfoTemplate лежит json,
    # хочется его сравнивать отдельно как json, а не как строку
    # Поэтому тут исключаем из сравнения
    # и сравниваем в отдельном тесте
    ddiff = DeepDiff(data, json_exp, ignore_order=True,
                     exclude_paths={"root['ru']['yandex']['se']['mobile']['services']['search']['metaInfoTemplate']"})
    assert not ddiff


@allure.feature('config_pp')
def test_cgi_params_meta_android():
    with open('./tests/config_pp/metaInfoTemplate.json') as f:
        meta_exp_json = json.load(f)

    client = ConfigppClient()
    res = client.simple_get(params={
        'app_id': 'ru.yandex.searchplugin',
        'app_platform': 'android',
        'app_version': 7020000
        }).send()
    data = res.json()

    meta_got = data['ru']['yandex']['se']['mobile']['services']['search']['metaInfoTemplate']
    meta_got_json = json.loads(meta_got)
    ddiff = DeepDiff(meta_got_json, meta_exp_json, ignore_order=True, exclude_paths={"root['webViewPages'][4]"})
    assert not ddiff


@allure.feature('config_pp')
def test_cgi_params_meta_apad():
    with open('./tests/config_pp/metaInfoTemplate_apad.json') as f:
        meta_exp_json = json.load(f)

    client = ConfigppClient()
    res = client.simple_get(params={
        'app_id': 'ru.yandex.searchplugin',
        'app_platform': 'apad',
        'app_version': 7020000
        }).send()
    data = res.json()

    meta_got = data['ru']['yandex']['se']['mobile']['services']['search']['metaInfoTemplate']
    meta_got_json = json.loads(meta_got)
    ddiff = DeepDiff(meta_got_json, meta_exp_json, ignore_order=True)
    assert not ddiff


@allure.feature('config_pp')
def test_cgi_params_headers():
    client = ConfigppClient()
    res = client.get(headers={'Cookie': 'yandexuid=9415156421521630788', 'X-Yandex-RandomUID': '42'}).send()
    headers = res.headers
    assert not headers.get('X-Yandex-RandomUID')

    res = client.get(headers={'Cookie': '', 'X-Yandex-RandomUID': '42'}).send()
    headers = res.headers
    assert headers.get('X-Yandex-RandomUID')


@allure.feature('config_pp')
@pytest.mark.parametrize('device', recent_services_matchers_devices)
def test_recent_services_matchers(device):
    client = ConfigppClient()
    res = client.simple_get(params={
        'app_id': 'ru.yandex.searchplugin',
        'app_platform': device['app_platform'],
        'app_version': device['app_version']
        }).send()
    data = res.json()

    if not device['recent_services_matchers']:
        assert 'recent_services_matchers' not in data
        return

    assert 'recent_services_matchers' in data
    matchers = data['recent_services_matchers']
    assert type(matchers) == list

    has_ski = False
    for matcher in matchers:
        assert type(matcher) == dict
        assert 'button_id' in matcher
        assert 'url_regexps' in matcher

        has_ski = has_ski or matcher['button_id'].startswith('ski_')

    assert has_ski
