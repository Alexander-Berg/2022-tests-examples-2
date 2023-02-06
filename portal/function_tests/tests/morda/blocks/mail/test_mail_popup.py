# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from common.block.mail import check_mail_popup_is_visible, check_mail_popup_is_not_visible, close_popup, open_popup, \
    login, logout
from common.client import MordaClient
from common.geobase import Regions
from common.morda import DesktopMain
from common.users import User

logger = logging.getLogger(__name__)

_BLOCKS = ['Mail']


def get_mordas():
    result = []
    for region in [Regions.MOSCOW, Regions.KYIV, Regions.MINSK, Regions.ASTANA]:
        result.append(DesktopMain(region=region))
    return result


def ids(value):
    return str(value)


@allure.feature('morda', 'mail')
@allure.story('mail_popup')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_popup_is_visible_by_default(morda):
    client = MordaClient(morda=morda)
    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()

    check_mail_popup_is_visible(cleanvars)


@allure.feature('morda', 'mail')
@allure.story('mail_popup')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_popup_can_be_closed(morda):
    client = MordaClient(morda=morda)

    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
    close_popup(client, cleanvars)

    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
    check_mail_popup_is_not_visible(cleanvars)


@allure.feature('morda', 'mail')
@allure.story('mail_popup')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_popup_can_be_reopened(morda):
    client = MordaClient(morda=morda)

    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
    close_popup(client, cleanvars)
    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
    open_popup(client, cleanvars)
    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()

    check_mail_popup_is_visible(cleanvars)


@allure.feature('morda', 'mail')
@allure.story('mail_popup')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_popup_is_visible_logged(morda):
    client = MordaClient(morda=morda)
    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()

    with User() as user:
        login(client, cleanvars, user['login'], user['password'])
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        check_mail_popup_is_visible(cleanvars)


@allure.feature('morda', 'mail')
@allure.story('mail_popup')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_popup_becomes_visible_after_login(morda):
    client = MordaClient(morda=morda)

    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
    close_popup(client, cleanvars)
    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()

    with User() as user:
        login(client, cleanvars, user['login'], user['password'])
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        check_mail_popup_is_visible(cleanvars)


@allure.feature('morda', 'mail')
@allure.story('mail_popup')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_popup_can_be_closed_login(morda):
    client = MordaClient(morda=morda)

    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()

    with User() as user:
        login(client, cleanvars, user['login'], user['password'])
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        close_popup(client, cleanvars)
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        check_mail_popup_is_not_visible(cleanvars)


@allure.feature('morda', 'mail')
@allure.story('mail_popup')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_popup_can_be_reopened_login(morda):
    client = MordaClient(morda=morda)

    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()

    with User() as user:
        login(client, cleanvars, user['login'], user['password'])
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        close_popup(client, cleanvars)
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        open_popup(client, cleanvars)
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        check_mail_popup_is_visible(cleanvars)


@allure.feature('morda', 'mail')
@allure.story('mail_popup')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_popup_stays_invisible_after_logout(morda):
    client = MordaClient(morda=morda)

    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
    close_popup(client, cleanvars)
    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()

    with User() as user:
        login(client, cleanvars, user['login'], user['password'])
        logout(client, cleanvars)
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        check_mail_popup_is_not_visible(cleanvars)


@allure.feature('morda', 'mail')
@allure.story('mail_popup')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_popup_stays_visible_after_logout(morda):
    client = MordaClient(morda=morda)

    cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()

    with User() as user:
        login(client, cleanvars, user['login'], user['password'])
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        close_popup(client, cleanvars)
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        logout(client, cleanvars)
        cleanvars = client.cleanvars(blocks=_BLOCKS).send().json()
        check_mail_popup_is_visible(cleanvars)
