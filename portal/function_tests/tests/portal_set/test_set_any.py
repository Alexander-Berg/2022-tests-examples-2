# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging
import allure
import pytest

from common.client import MordaClient
from tests.portal_set.set_common import mordas_for_domains

logger = logging.getLogger(__name__)

"""
/set/any
выставляет сабкуки в куку yp

//домены - ru, ua, by, kz
success:
"""
cases_mda = [
    {'params': {'mda': 0, 'empty': 1}, 'check': '0'},
]

cases = [
    {
        'params': {'af': 1, 'empty': 1},
        'check': '.af.1'
    },
    {
        'params': {'afn': 1, 'empty': 1},
        'check': '.afn.1'
    },
    {
        'params': {'beeb': 1, 'empty': 1},
        'check': '.beeb.1'
    },
    {
        'params': {'csc': 1, 'empty': 1},
        'check': '.csc.1'
    },
    {
        'params': {'hkd': 1, 'empty': 1},
        'check': '.hkd.1'
    },
    {
        'params': {'hwb': 1, 'empty': 1},
        'check': '.hwb.1'
    },
    {
        'params': {'msb': 1, 'empty': 1},
        'check': '.msb.1'
    },
    {
        'params': {'mtb': 1, 'empty': 1},
        'check': '.mtb.1'
    },
    {
        'params': {'mu': 1, 'empty': 1},
        'check': '.mu.1'
    },
    {
        'params': {'mv': 1, 'empty': 1},
        'check': '.mv.1'
    },
    {
        'params': {'obp': 1, 'empty': 1},
        'check': '.obp.1'
    },
    {
        'params': {'trf': 1, 'empty': 1},
        'check': '.trf.1'
    },
    {
        'params': {'vd': 1, 'empty': 1},
        'check': '.vd.1'
    },
    {
        'params': {'ybp': 1, 'empty': 1},
        'check': '.ybp.1'
    },
    {
        'params': {'ygp': 1, 'empty': 1},
        'check': '.ygp.1'
    },
    {
        'params': {'bdst': 1, 'empty': 1},
        'check': '.bdst.1'
    },
    {
        'params': {'ac': 1, 'empty': 1},
        'check': '.ac.1'
    },
    {
        'params': {'dq': 1, 'empty': 1},
        'check': '.dq.1'
    },
    {
        'params': {'cr': 'ua', 'empty': 1},
        'check': '.cr.ua'
    },
    {
        'params': {'clh': '234-567', 'empty': 1},
        'check': '.clh.234-567'
    },
    {
        'params': {'stst': 'min', 'empty': 1},
        'check': '.stst.min'
    },
    {
        'params': {'hk': 'm410316', 'empty': 1},
        'check': '.hk.m410316'
    },
    {
        'params': {'apps': 'mail-1', 'empty': 1},
        'check': '.apps.mail-1-0'
    },
    {
        'params': {'nt': 'culture', 'empty': 1},
        'check': '.nt.culture'
    },
    {
        'params': {'szm': '1:233x234:3432x23423', 'empty': 1},
        'check': '.szm.1:233x234:3432x23423'
    },
]


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/any')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('case', cases)
def test_set_any_yp(morda, case):
    """
    Пробуем установить куку.
    :param morda:
    :param case: dict Данные о куке - что ставим, как проверяем
    :return: None
    """
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    result = client.set_any(secret_key=secret_key, params=case['params'], retpath='https://yandex.ru/')
    result.send()

    client.test_cookie_yp(case['check'])


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/any')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('case', cases_mda)
def test_set_any_mda(morda, case):
    """
    Пробуем установить куку.
    :param morda:
    :param case: dict Данные о куке - что ставим, как проверяем
    :return: None
    """
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']

    result = client.set_any(secret_key=secret_key, params=case['params'], retpath='https://yandex.ru/')
    result.send()

    client.test_cookie('mda', case['check'])


"""
//домены - ru, ua, by, kz
    #error:bad_sk
"""


@pytest.mark.yasm
@allure.feature('portal_set')
@allure.story('set/my')
@pytest.mark.parametrize('morda', mordas_for_domains)
@pytest.mark.parametrize('case', cases[:1])
def test_set_any_bad_sk(morda, case):
    client = MordaClient(morda)
    secret_key = client.cleanvars(blocks=['sk']).send().json()['sk'] + 'eughoegpoehge'

    result = client.set_any(secret_key=secret_key, params=case['params'], retpath='https://yandex.ru/')
    result = result.send()
    assert 'Location' in result.headers
    assert '#error:bad_sk' in result.headers['Location']
