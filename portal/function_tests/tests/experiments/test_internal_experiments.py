# -*- coding: utf-8 -*-
import allure
import pytest

from common.client import MordaClient

LOGINS = {
    None: None,
    'mordadisk': {'password': 'aaaaaa', 'is_staff': 1},
    'mordanodisk': {'password': 'b1b2b3', 'is_staff': 0}
}
EXPERIMENT_NAME = 'yandex_internal_test'
EXP_STATES = {
    1: 'on',
    0: 'off'
}


@allure.step('Check is valid experiment state')
def check_state(response, expected_exp_on, flags=None):
    fact_exp_on = 0
    exps = response['exp']
    if EXPERIMENT_NAME in exps:
        exp = exps[EXPERIMENT_NAME]
        if 'on' in exp:
            fact_exp_on = 1 if exp['on'] else 0
        if flags:
            for flag in flags:
                assert exp['flags'][flag] == 1, 'Expect flag {} is 1'.format(flag)
    assert expected_exp_on == fact_exp_on, 'Expect experiment is {}, really is {}'.format(
                                   EXP_STATES[expected_exp_on], EXP_STATES[fact_exp_on]
                               )


@pytest.mark.skipif('True')
@allure.feature('morda', 'experiments')
@allure.story('experiment_yandex')
@pytest.mark.parametrize('login', LOGINS.keys())
@pytest.mark.parametrize('yandex', [0, 1])
def test_is_valid_internal_experiments(login, yandex):
    client = MordaClient()
    is_staff = 0
    if login:
        passport_host = client.cleanvars(blocks=['Mail']).send().json()['Mail']['auth_host']
        is_staff = LOGINS[login]['is_staff']
        client.login(passport_host, login, LOGINS[login]['password']).send()
    is_exp_on = is_staff or yandex
    kwargs = {'params': {'yandex': yandex, 'staff_login': is_staff}}
    kwargs['headers'] = {'X-Yandex-Autotests': '1'}
    response = client.cleanvars_data(blocks=['exp'], **kwargs)
    flags = []
    if is_staff:
        flags.append('yandex_669')
    if yandex:
        flags.append('yandex')
    check_state(response, is_exp_on, flags=flags)
