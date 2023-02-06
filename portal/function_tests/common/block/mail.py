# -*- coding: utf-8 -*-
import allure
from hamcrest import equal_to

from common.utils import get_field, check_field


@allure.step('Should see mail popup')
def check_mail_popup_is_visible(cleanvars):
    check_field(cleanvars, 'Mail.visible', equal_to(1))


@allure.step('Should not see mail popup')
def check_mail_popup_is_not_visible(cleanvars):
    check_field(cleanvars, 'Mail.visible', equal_to(0))


@allure.step('Close popup')
def close_popup(client, cleanvars):
    close_url = get_field(cleanvars, 'Mail.visible_set_off')
    return client.request(url=close_url).send()


@allure.step('Open popup')
def open_popup(client, cleanvars):
    open_url = get_field(cleanvars, 'Mail.visible_set_on')
    return client.request(url=open_url).send()


@allure.step('Login as {2}')
def login(client, cleanvars, login, password):
    passport_host = get_field(cleanvars, 'Mail.auth_host')
    return client.login(passport_host=passport_host, login=login, password=password).send()


@allure.step('Logout')
def logout(client, cleanvars):
    passport_host = get_field(cleanvars, 'Mail.auth_host')
    return client.logout(passport_host=passport_host).send()
