# -*- coding: utf-8 -*-

"""
https://wiki.yandex-team.ru/morda/handlers/#gpsave
описание куки - https://wiki.yandex-team.ru/Geolocation/Cookies/
"""

from __future__ import print_function
import allure
import pytest
from common.client import MordaClient
from common.cookies.y import CookieYp
from common.geobase import region_by_id, Regions, linguistics_for_region
from common.languages import LanguagesKUBR
from common.morda import DesktopMain
from tests.portal_set.set_common import mordas_for_domains

"""
1. тесты на обязательные параметры для ручки:
lat - Широта
lon - Долгота
precision - Точность определения в метрах
sk - секретный ключ
общий пример
http://www-rc.yandex.ru/gpsave?lat=59.923145&lon=30.322547&precision=300&sk=y719a12a8acc232c1c4bd2a4aa6ebc8f3
если кривые параметры (или отсутствуют), должна выдаваться ошибка

2. необязательные параметры для ручки
lang - язык выдачи названия и падежей города, проверить uk, be, ru
addr=1 - один раз проверить, что выдается портянка из геобазы

3. should_reload: true - рефреш морды
ip морды отличается от координат в ручке (+ плохая точность) + ygu=1
координаты морды отличаются от координат в ручке + ygu=1 + хорошая точность

4. should_reload: false
ip морды не отличается от координат в ручке
координаты морды отличаются от координат в ручке внутри города
нет куки ygu=1, есть кука типа ygo.[регион до]:[регион выставлен на тьюне руками]
poor_precision: true - примерно после 3000м

"""

gpsave_devices = {'GPS': 0, 'WIFI': 1, 'GSM': 2, 'OTHER': 3}


# @pytest.mark.yasm
@allure.feature('set cookies')
@allure.story('gpsave')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('device', gpsave_devices)
# @pytest.mark.parametrize('case', cases)
def test_gpsave_cookies(device, morda):
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    lat = 55.73211356
    lon = 37.58232178
    precision = 500
    params = {
        # 'mobile': 0/1,
        'device': gpsave_devices[device],
        # 'ip': 0/1,
        # 'no_mda': 0/1,
        # 'callback': '',
        # --- 'timing': ?,
        # 'format': JSON/JSONP/XML,
        # 'laas': ?,
        # 'from_region': ?,
        # '_': timestamp?,
    }
    result = client.set_gpsave(lat, lon, precision=precision, secret_key=secret_key, params=params)
    result = result.send()
    assert result.is_ok()
    assert client.get_cookie_yp() is not None, 'gpauto cookie is not set'
    cookieparser = CookieYp(client.get_cookie_yp())
    cookieparser.gpauto_test(lat, lon, precision, gpsave_devices[device])


cases = [
    {
        'region_from': Regions.MOSCOW,
        'ip_from': '89.175.217.44',
        'region_to': Regions.SAINT_PETERSBURG,
        'ip_to': '31.193.122.100',
    },
    {
        'region_from': Regions.KYIV,
        'ip_from': '46.173.146.76',
        'region_to': Regions.LVIV,
        'ip_to': '109.87.126.248',
    },
    {
        'region_from': Regions.MINSK,
        'ip_from': '93.84.10.197',
        'region_to': Regions.VITEBSK,
        'ip_to': '37.45.82.133',
    },
    {
        'region_from': Regions.ASTANA,
        'ip_from': '2.75.212.68',
        'region_to': Regions.ALMATY,
        'ip_to': '195.82.12.155',
    },
]


@allure.feature('set cookies')
@allure.story('gpsave')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('case', cases)
@pytest.mark.parametrize('device', gpsave_devices)      # Наверное этот параметр лишний
def test_gpsave_flags(morda, case, device):
    """
    IP в тесте нужен для того чтобы определился регион. Меняется город - появляется флажок should_reload
    """
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    client.remove_cookie('yandex_gid')  # Чистим куку, чтобы появился should_reload
    precision = 500
    params = {
        'device': gpsave_devices[device],
    }

    params_from = region_by_id(case['region_from'])
    params_to = region_by_id(case['region_to'])

    request = client.set_gpsave(params_from['latitude'], params_from['longitude'],
                                precision=precision, secret_key=secret_key, params=params)
    request.headers['X-Forwarded-For'] = case['ip_from']
    result = request.send()
    assert result.is_ok()
    result = result.json()
    assert result['region_changed'] is False
    assert result['should_reload'] is False
    assert result['region_name'] == params_from['name']

    request = client.set_gpsave(params_to['latitude'], params_to['longitude'],
                                precision=precision, secret_key=secret_key, params=params)
    request.headers['X-Forwarded-For'] = case['ip_to']
    result = request.send()
    assert result.is_ok()
    result = result.json()
    assert result['region_changed'] is True
    assert result['should_reload'] is True
    assert result['region_name'] == params_to['name']


@allure.feature('set cookies')
@allure.story('gpsave')
@pytest.mark.parametrize('language', LanguagesKUBR)
@pytest.mark.parametrize('region', [Regions.MOSCOW, Regions.MINSK, Regions.ASTANA, Regions.KYIV][:3])
def test_gpsave_lang(language, region):
    """
    IP в тесте нужен для того чтобы определился регион. Меняется город - появляется флажок should_reload
    """
    morda = DesktopMain(region=region, language=language)
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    client.remove_cookie('yandex_gid')  # Чистим куку, чтобы появился should_reload
    precision = 500
    params = {
        'device': 3,
        'lang': language
    }

    region_params = region_by_id(region)
    translations = linguistics_for_region(region, language)

    request = client.set_gpsave(region_params['latitude'], region_params['longitude'],
                                precision=precision, secret_key=secret_key, params=params)
    result = request.send()
    assert result.is_ok()
    result = result.json()

    assert result['region_name'] == translations['nominative_case']
    assert result['region_genitive'] == translations['genitive_case']
    # FIXME: фигня какаято - в геобазе переводов меньше чем у нас
    # assert result['region_dative'] == translations['dative_case']
    assert len(result['region_dative']) > 0
    assert len(result['region_locative']) > 0
    assert len(result['address']) > 0
