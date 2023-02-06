# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging
import allure
import pytest
from tests.portal_set.set_common import mordas_for_domains

from common.client import MordaClient

logger = logging.getLogger(__name__)

"""
/set/my
записывает значение в куку my
"""

# все домены - ru, ua, by, kz, com, com.tr, uz, com.ge
# success:
cases = [
    {'params': (('param', 2), ('block', '39')), 'check': 'YycBAgA='},
    {'params': (('param', 0), ('param', 2), ('block', '55')), 'check': 'YzcCAAIA'},
    {'params': (('param', ''), ('block', '39')), 'check': 'YwA='}
]

error_cases = [
    # все домены - ru, ua, by, kz, com, com.tr, uz
    # error:
    {'params': (('param', '2'), ('block', '')), 'check_error': '#error:no_block'},
    {'params': (('param', '3'),), 'check_error': '#error:no_block'},
    {'params': (('param', 'qqq'), ('block', 'aaa')), 'check_error': '#error:bad_block'},
]


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/my')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('case', cases)
def test_set_my(morda, case):
    """
    Пробуем установить куку. Отдельная функция нужна, чтобы правильно py.test генерил наборы параметров
    :param morda:
    :param case: dict Данные о куке - что ставим, как проверяем
    :return: None
    """
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    result = client.set_my(secret_key=secret_key, params=case['params'], retpath='https://yandex.ru/')
    result = result.send()
    # print('==========================')
    # print(json.dumps(dict(result.headers), indent=4))
    # print('==========================')

    if 'check' in case:
        assert case['check'] == client.get_cookie_my()


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/my')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('case', error_cases)
def test_set_my_errors(morda, case):
    """
    Пробуем установить куку. Отдельная функция нужна, чтобы правильно py.test генерил наборы параметров
    :param morda:
    :param case: dict Данные о куке - что ставим, как проверяем
    :return: None
    """
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    result = client.set_my(secret_key=secret_key, params=case['params'], retpath='https://yandex.ru/')
    result = result.send()
    # print('==========================')
    # print(json.dumps(dict(result.headers), indent=4))
    # print('==========================')

    assert 'Location' in result.headers
    assert case['check_error'] in result.headers['Location']


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/my')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('case', cases[:1])
def test_set_my_bad_sk(morda, case):
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk'] + 'eughoegpoehge'

    result = client.set_my(secret_key=secret_key, params=case['params'], retpath='https://yandex.ru/')
    result = result.send()
    assert 'Location' in result.headers
    assert '#error:bad_sk' in result.headers['Location']
