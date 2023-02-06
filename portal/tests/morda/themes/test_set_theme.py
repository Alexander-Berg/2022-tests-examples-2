# -*- coding: utf-8 -*-
import logging

import allure
import pytest

import themes
from common.client import MordaClient
from common.geobase import Regions
from common.morda import DesktopMain

logger = logging.getLogger(__name__)

parameters = [DesktopMain(language='ru', region=region) for region in [Regions.MOSCOW, Regions.KYIV,
                                                                       Regions.MINSK, Regions.ASTANA]]

ids = [str(p) for p in parameters]

theme1 = 'hots'
theme2 = 'depechemode'


@allure.feature('morda', 'skins')
@allure.story('big_skins')
@pytest.mark.parametrize('morda', parameters, ids=ids)
def test_set_theme(morda):
    client = MordaClient(morda)
    client.cleanvars().send()
    client.theme_set(theme1).send()
    dump = client.cleanvars().send().json()
    themes.should_see_theme(dump, theme1)


@allure.feature('morda', 'skins')
@allure.story('big_skins')
@pytest.mark.parametrize('morda', parameters, ids=ids)
def test_set_another_theme(morda):
    client = MordaClient(morda)
    client.cleanvars().send()
    client.theme_set(theme1).send()
    client.theme_set(theme2).send()
    dump = client.cleanvars().send().json()
    themes.should_see_theme(dump, theme2)


@allure.feature('morda', 'skins')
@allure.story('big_skins')
@pytest.mark.parametrize('morda', parameters, ids=ids)
def test_set_default_theme(morda):
    client = MordaClient(morda)
    client.cleanvars().send()
    client.theme_set(theme1).send()
    client.theme_set(themes.default_theme).send()
    dump = client.cleanvars().send().json()
    themes.should_see_default_theme(dump)


@allure.feature('morda', 'skins')
@allure.story('big_skins')
@pytest.mark.parametrize('morda', parameters, ids=ids)
def test_set_random_theme(morda):
    client = MordaClient(morda)
    client.cleanvars().send()
    client.theme_set(theme1).send()
    client.theme_set(themes.random_theme).send()
    dump = client.cleanvars().send().json()
    themes.should_see_random_theme(dump)
