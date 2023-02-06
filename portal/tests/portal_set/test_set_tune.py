# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging
import allure
import pytest
import time

from common.client import MordaClient
from tests.portal_set.set_common import mordas_for_domains

logger = logging.getLogger(__name__)

"""
/set/tune/
выставляет значение в сабкуку yp и куку my
"""

set_tune_cookies = (
    {'name': 'mtd', 'value': '1', 'check': 'mtd.1'},
    {'name': 'ygd', 'value': '1', 'check': 'ygd.1'},
    {'name': 'self_window', 'value': '1', 'check': 'sp.tg:_sel'},
    {'name': 'family', 'value': '1', 'check': 'sp.family:2'},

    {'name': 'big_version', 'value': 1, 'check_my': 'YywBAQA='},
    {'name': 'no_interest_ad', 'value': 1, 'check_my': 'YyYBAQA='},
    {'name': 'no_main_banner', 'value': 1, 'check_my': 'Yy4BAQA='},
    {'name': 'no_geo_ad', 'value': 1, 'check_my': 'YzoBAQA='},
    {'name': 'no_app_by_links', 'value': 1, 'check_my': 'YzsBAQA='},
)
# Только POST куки
set_tune_post_cookies = (
    {'name': 'yes_interest_ad', 'value': 0, 'check_my': 'YyYBAQA='},
    {'name': 'yes_main_banner', 'value': 0, 'check_my': 'Yy4BAQA='},
    {'name': 'yes_geo_ad', 'value': 0, 'check_my': 'YzoBAQA='},
    {'name': 'mobile_version', 'value': 0, 'check_my': 'YywBAQA='},
    {'name': 'yes_app_by_links', 'value': 0, 'check_my': 'YzsBAQA='},
    {'name': 'new_window', 'value': 0, 'check': '.sp.tg:_self'},
    # Тест на то, что кука чиститься с протухшим временем
    {'name': 'family', 'value': None,
     'initial_cookie': ('yp', '1562295560.sp.family:2-lang:!ru!be:ajx:0'), 'check': None},
    # тест на чистку дефисов
    {'name': 'family', 'value': None,
     'initial_cookie': ('yp', '{time}.sp.family:2-lang:!ru!be:ajx:0'), 'check': '.sp.ajx:0:lang:!ru!be'},
    # тест на удаление дублей внутри куки
    {'name': 'family', 'value': 1,
     'initial_cookie': ('yp', '{time}.sp.ajx:0:family:0-family:2'), 'check': '.sp.ajx:0:family:2'},
    {'name': 'yes_mtd', 'value': 0, 'check': 'mtd.1'},
)


def try_set_tune(morda, method, cookie):
    """
    Пробуем установить куку. Отдельная функция нужна, чтобы правильно py.test генерил наборы параметров
    :param morda:
    :param method: str GET|POST
    :param cookie: dict Данные о куке - что ставим, как проверяем
    :return: None
    """
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    if 'initial_cookie' in cookie:
        ts = time.time() + 5000
        initial_cookie = list(cookie['initial_cookie'])
        initial_cookie[1] = initial_cookie[1].format(time=int(ts))
        client.set_cookie(*initial_cookie)

    result = client.set_tune(secret_key=secret_key, method=method, name=cookie['name'], value=cookie['value'],
                             retpath='https://yandex.ru/')
    result = result.send()
    assert 'Set-Cookie' in result.headers
    if 'check_my' in cookie:
        assert client.get_cookie_my() == cookie['check_my']
    elif 'check' in cookie:
        client.test_cookie_yp(cookie['check'])


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/tune')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('method', ['GET', 'POST'])
@pytest.mark.parametrize('cookie', set_tune_cookies)
def test_set_tune(morda, method, cookie):
    try_set_tune(morda, method, cookie)


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/tune')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('method', ['POST'])
@pytest.mark.parametrize('cookie', set_tune_post_cookies)
def test_set_tune_post(morda, method, cookie):
    try_set_tune(morda, method, cookie)


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/tune')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('method', ['GET', 'POST'])
@pytest.mark.parametrize('cookie', set_tune_cookies[:1])
def test_set_tune_bad_sk(morda, method, cookie):
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk'] + 'eughoegpoehge'

    result = client.set_tune(secret_key=secret_key, method=method, name=cookie['name'], value=cookie['value'],
                             retpath='https://yandex.ru/')
    result = result.send()
    assert 'Location' in result.headers
    assert '#error:bad_sk' in result.headers['Location']
