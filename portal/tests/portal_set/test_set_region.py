# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging
import allure
import pytest
from common.client import MordaClient
from common.morda import DesktopMain, DesktopCom, DesktopComTr
from common.geobase import Regions, get_domain_by_region

logger = logging.getLogger(__name__)

mordas_for_domains = {
    'ru': DesktopMain(Regions.MOSCOW),
    'ua': DesktopMain(Regions.KYIV),
    'by': DesktopMain(Regions.MINSK),
    'kz': DesktopMain(Regions.ASTANA),
    'com': DesktopCom(),
    'com.tr': DesktopComTr(),
    'com.ge': DesktopComTr(),
    'uz': DesktopComTr(),
}

"""
/set/region
Изменяет куки yandex_gid, yp (ygo, ygu, ygd, gpauto) и my (блок 43)

блок 43 - PDA морда - история городов: 4 последние города, выбранные пользователем

ОСНОВНОЕ - id&from - установка региона
"""

cases = [
    # 'Domain=ru,ua,kz,by to ru,ua,kz,by',
    {
        'domain': 'ru',
        'params': {'id': 969},
        'check': [
            {'cookie': 'yp', 'check': '.ygu.0', 'domain': '.yandex.ru'},
            {'cookie': 'yp', 'check_re': '.ygo.(\d*):969', 'domain': '.yandex.ru'},
            {'cookie': 'yandex_gid', 'check': '969', 'domain': '.yandex.ru'},
            {'cookie': 'my', 'check': 'YysBg8kA', 'domain': '.yandex.ru'},
        ]
    },
]


def generate_check(region_from, region_to, cookie_my):
    domain_from = get_domain_by_region(region_from)
    domain_to = get_domain_by_region(region_to)

    check = []
    if domain_to in ['ru', 'ua', 'by', 'kz']:
        check = [
            {'cookie': 'yp', 'check': '.ygu.0', 'domain': '.yandex.ru'},
            {'cookie': 'yp', 'check': '.ygo.{}:{}'.format(region_from, region_to), 'domain': '.yandex.ru'},
            {'cookie': 'yandex_gid', 'check': region_to, 'domain': '.yandex.ru'},
            {'cookie': 'my', 'check': cookie_my, 'domain': '.yandex.ru'},
        ]
        if domain_to != 'ru':
            check += [
                {'cookie': 'yp', 'check': '.ygu.0', 'domain': '.yandex.{}'.format(domain_to)},
                {'cookie': 'yp', 'check': '.ygo.{}:{}'.format(region_from, region_to),
                 'domain': '.yandex.{}'.format(domain_to)},
                {'cookie': 'yandex_gid', 'check': region_to, 'domain': '.yandex.{}'.format(domain_to)},
                {'cookie': 'my', 'check': cookie_my, 'domain': '.yandex.{}'.format(domain_to)},
            ]
    else:
        if domain_to in ['com', 'com.tr', 'com.ge', 'uz']:
            check = [
                {'cookie': 'yp', 'check': '.ygu.0', 'domain': '.yandex.{}'.format(domain_to)},
                {'cookie': 'yp', 'check': '.ygo.{}:{}'.format(region_from, region_to),
                 'domain': '.yandex.{}'.format(domain_to)},
                {'cookie': 'yandex_gid', 'check': region_to, 'domain': '.yandex.{}'.format(domain_to)},
                {'cookie': 'my', 'check': cookie_my, 'domain': '.yandex.{}'.format(domain_to)},
            ]
    return {
        'domain': domain_from,
        'params': {'from': region_from, 'id': region_to},
        'check': check
    }


cases += [
    generate_check(2, 969, 'YysBg8kA'),
    generate_check(143, 147, 'YysBgJMA'),
    generate_check(190, 162, 'YysBgKIA'),
    generate_check(155, 154, 'YysBgJoA'),
    # Domain=ru to ua,kz,by
    # generate_check(2, 147, 'YysBgJMA'),           // Отключено для yandex.fr
    generate_check(2, 190, 'YysBgL4A'),
    generate_check(2, 154, 'YysBgJoA'),
    # Domain=ua,kz,by to ru
    generate_check(147, 2, 'YysBAgA='),
    generate_check(163, 2, 'YysBAgA='),
    generate_check(157, 2, 'YysBAgA='),

    # generate_check(190, 143, 'YysBgL4A'),         // Отключено для yandex.fr
    generate_check(143, 154, 'YysBgJoA'),
    generate_check(190, 154, 'YysBgJoA'),
    # generate_check(190, 147, 'YysBgJMA'),         // Отключено для yandex.fr
    # generate_check(157, 147, 'YysBgJMA'),         // Отключено для yandex.fr
    generate_check(157, 190, 'YysBgL4A'),

    # Domain com, com.tr, com.ge, uz
    generate_check(110216, 87, 'YysBVwA='),
    generate_check(107762, 11503, 'YysBrO8A'),
    # generate_check(10284, 10277, 'YysBqCUA'),     // Отключено для yandex.fr
    # generate_check(10335, 10334, 'YysBqF4A'),     // Отключено для yandex.fr
]

"""
error

GET
{"params":id=969&retpath=https%3A%2F%2Fyandex.ru%2F" -H "Cookie: yandexuid=7630452101466268947"
    #error:bad_sk
{"params":id=969&retpath=https%3A%2F%2Fmail.ru%2F" -H "Cookie: yandexuid=7630452101466268947" -H
'sk-ok:y0d9ce139692fb126627d697010d1a74f'
    #error:bad_retpath

POST
curl -vLsk "https://www-rc.yandex.ru/portal/set/region/" -H "Cookie: yandexuid=4235693231476101041"
--data "id=969&sk=y96b0a98d9ba6b65f3588398de260b16c" --compressed -o /dev/null
    #error:bad_sk
curl -vLsk "https://www-rc.yandex.ru/portal/set/region/" -H "Cookie: yandexuid=4235693231476101041"
-H 'sk-ok:y96b0a98d9ba6b65f3588398de260b16c' --data
"id=969&sk=y96b0a98d9ba6b65f3588398de260b16c&retpath=https%3A%2F%2Fmail.ru%2F" --compressed -o /dev/null
    #error:bad_retpath


ПРОЧЕЕ - auto, no_location, name

success

все домены:
auto - флаг автоматического определения региона
{"params":auto=1
    yandex_gid=; Domain=.yandex.ru;
{"params":auto=1&id=2
    yandex_gid=; Domain=.yandex.ru;
{"params":auto=0&id=2
    yp=1506534890.ygu.0#1506534890.ygo.2:2; Domain=.yandex.ru;
    yandex_gid=2; Domain=.yandex.ru;
    my=YysBAgA=; Domain=.yandex.ru;

все домены:
no_location - флаг отказа уточения региона
{"params":no_location=1
    Set-Cookie: yp=1506525691.ygd.1; Domain=.yandex.ru;
{"params":no_location=0
    no ygd

{"params":id=969
    /#error:bad_retpath


name - название региона, может юзаться вместо id, сейчас не работает
{"params":name=%D0%9E%D0%BC%D1%81%D0%BA
err!!! - https://st.yandex-team.ru/HOME-33961

"""


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/region')
@pytest.mark.parametrize('method', ['GET', 'POST'])
@pytest.mark.parametrize('case', cases)
def test_set_region(method, case):
    """
    Пробуем установить куку. Отдельная функция нужна, чтобы правильно py.test генерил наборы параметров
    :param method: strign GET|POST
    :param case: dict Данные о куке - что ставим, как проверяем
    :return: None
    """

    client = MordaClient(mordas_for_domains[case['domain']])
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    result = client.set_region(secret_key, method, case['params'], retpath='https://yandex.ru/')
    result.send()
    for check in case['check']:
        if 'check' in check:
            client.test_cookie(check['cookie'], str(check['check']), check['domain'])
        elif 'check_re' in check:
            client.test_cookie_regex(check['cookie'], str(check['check_re']), check['domain'])


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/region')
@pytest.mark.parametrize('method', ['GET', 'POST'])
@pytest.mark.parametrize('case', cases[:1])
def test_set_region_bad_sk(method, case):

    client = MordaClient(mordas_for_domains[case['domain']])
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk'] + 'eughoegpoehge'

    result = client.set_region(secret_key, method, case['params'], retpath='https://yandex.ru/', allow_redirects=False)
    result = result.send()
    assert 'Location' in result.headers
    assert '#error:bad_sk' in result.headers['Location']
