# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging
import allure
import pytest
from tests.portal_set.set_common import mordas_for_domains
from common.cookies.my import CookieMy
from common.morda import DesktopMain
from common.geobase import Regions


from common.client import MordaClient

logger = logging.getLogger(__name__)

"""
 /set/lang
 Выставляет куку my, блок 39, на тот домен? с которого запрос
"""

# //все домены - ru, ua, by, kz, com, com.tr, uz
# success:
lang_codes = {
    'ru': 1,
    'uk': 2,
    'en': 3,
    'kk': 4,
    'be': 5,
    'tt': 6,
    'az': 7,
    'tr': 8,
    'hy': 9,
    'ka': 10,
    'ro': 11,
    'de': 12,
    'id': 13,
    # 'zh': 14,         # Языки пока не поддерживаются мордой
    # 'es': 15,
    # 'pt': 16,
    # 'fr': 17,
    # 'it': 18,
    # 'ja': 19,
    # 'br': 20,
    # 'cs': 21,
    # 'fi': 22,
    'uz': 23
}


def make_my_cookie_with_lang(lang_name):
    """
    Генерация референсного значения куки My с блоком языка
    https://wiki.yandex-team.ru/mycookie/
    :param lang_name:
    :return:
    """
    cookie = CookieMy()
    cookie.set_lang(lang_name)
    return cookie.to_string()


cases = [{'params': {'intl': lang}, 'check': make_my_cookie_with_lang(lang)} for lang in lang_codes.keys()]

"""
Дополнительные случаи для проверки реакции на ошибки:
"""
error_cases = [
    {
        'params': {'intl': 'gfds'},
        'check_error': '/#error:bad_lang'
    },
    {
        'params': {'intl': ''},
        'check_error': '/#error:bad_lang'
    },
    {
        'params': {'intl': 'uk', 'retpath': 'https://mail.ru'},
        'check_error': '/#error:bad_retpath'
    },
]


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/my')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('case', cases)
def test_set_lang(morda, case):
    """
    :param morda:
    :param case: dict Данные о куке - что ставим, как проверяем
    :return: None
    """
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    result = client.set_lang(secret_key=secret_key, params=case['params'])
    result = result.send()
    # print('==========================')
    # print(json.dumps(dict(result.headers), indent=4))
    # print('==========================')

    assert case['check'] == client.get_cookie_my()


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/my')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('case', error_cases)
def test_set_lang_errors(morda, case):
    """
    :param morda:
    :param case: dict Данные о куке - что ставим, как проверяем
    :return: None
    """
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']
    result = client.set_lang(secret_key=secret_key, params=case['params'])
    result = result.send()

    assert 'Location' in result.headers
    assert case['check_error'] in result.headers['Location']


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/my')
@pytest.mark.parametrize('case', cases[:1])
def test_set_lang_bad_sk(case):

    client = MordaClient(DesktopMain(Regions.MOSCOW))
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk'] + 'eughoegpoehge'

    result = client.set_lang(secret_key=secret_key, params=case['params'])
    result = result.send()
    assert 'Location' in result.headers
    assert '#error:bad_sk' in result.headers['Location']
