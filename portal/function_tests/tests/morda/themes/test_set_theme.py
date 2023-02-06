import logging

import allure
import pytest

import themes
from common.client import MordaClient
from common.geobase import Regions
from common.morda import DesktopMain


theme1 = {
    'name': 'hots',
    'color': 'night',
}

theme2 = {
    'name': 'weather',
    'color': 'night',
}


@allure.feature('morda', 'skins')
class TestSkinsBigMoscowBlack(object):
    def setup_class(cls):
        client = MordaClient(DesktopMain(region=Regions.MOSCOW))
        client.cleanvars().send()
        client.theme_set(theme1.get('name')).send()
        dump = client.cleanvars().send().json()
        # the first time the topic sometimes is not set
        for i in range(10):
            if dump['Skin'] is not None:
                break

            client.theme_set(theme1.get('name')).send()
            dump = client.cleanvars().send().json()

        cls.dump = dump
        cls.theme = theme1

    @allure.story('big_skins')
    def test_set_theme(self):
        theme = self.theme
        assert self.dump['Skin'] == theme.get('color'), 'Invalid "Skin"'
        assert self.dump['Themes']['current']['id'] == theme.get('color'), 'Invalid "Themes.current.id"'
        assert self.dump['WPSettings']['defskin'] == theme.get('name'), 'Invalid "WPSettings.defskin"'

class TestSkinsBigMoscowWhite(object):
    def setup_class(cls):
        client = MordaClient(DesktopMain(region=Regions.MOSCOW))
        client.cleanvars().send()
        client.theme_set(theme2.get('name')).send()
        dump = client.cleanvars().send().json()
        cls.dump = dump
        cls.theme = theme2

    @allure.story('big_skins')
    def test_set_theme(self):
        theme = self.theme
        assert self.dump['Skin'] is None, 'Invalid "Skin"'
        assert self.dump['WPSettings']['defskin'] == theme.get('name'), 'Invalid "WPSettings.defskin"'



@allure.feature('morda', 'skins')
class TestSkinsBigAstana(object):
    def setup_class(cls):
        client = MordaClient(DesktopMain(region=Regions.ASTANA))
        client.cleanvars().send()
        client.theme_set(theme1.get('name')).send()
        dump = client.cleanvars().send().json()
        # the first time the topic sometimes is not set
        for i in range(10):
            if dump['Skin'] is not None:
                break

            client.theme_set(theme1.get('name')).send()
            dump = client.cleanvars().send().json()
        cls.dump = dump
        cls.theme = theme1

    @allure.story('big_skins')
    def test_set_theme(self):
        theme = self.theme
        assert self.dump['Skin'] == theme.get('name'), 'Invalid "Skin"'
        assert self.dump['Themes']['current']['id'] == theme.get('name'), 'Invalid "Themes.current.id"'
        assert self.dump['WPSettings']['defskin'] == theme.get('name'), 'Invalid "WPSettings.defskin"'



