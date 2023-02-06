# -*- coding: utf-8 -*-
import allure

from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, fetch_data, check_show, count_elements, absence


BLOCK = 'Stream_now'
TABS_COUNT = 3
PROGRAMS_COUNT = 3


@allure.feature('morda', 'StreamNow')
class TestStreamNowBigMoscow(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK], cgi_params={'yandexuid': 572909971517226139})
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_StreamNow_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_StreamNow_show(self):
        check_show(self.block)

    @allure.story('tabs')
    def test_StreamNow_tabs(self):
        count_elements(self.block.get('tabs'), TABS_COUNT)

    @allure.story('programs')
    def test_StreamNow_programs(self):
        for tab in self.block.get('tabs'):
            count_elements(tab.get('programs'), PROGRAMS_COUNT)


@allure.feature('morda', 'StreamNow')
class TestStreamNowBigMinsk(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK], cgi_params={'yandexuid': 572909971517226139})
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_StreamNow_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_StreamNow_show(self):
        check_show(self.block)

    @allure.story('tabs')
    def test_StreamNow_tabs(self):
        count_elements(self.block.get('tabs'), TABS_COUNT)

    @allure.story('programs')
    def test_StreamNow_programs(self):
        for tab in self.block.get('tabs'):
            count_elements(tab.get('programs'), PROGRAMS_COUNT)


@allure.feature('morda', 'StreamNow')
class TestStreamNowBigAstana(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK], cgi_params={'yandexuid': 572909971517226139})
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_StreamNow_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_StreamNow_show(self):
        check_show(self.block)

    @allure.story('tabs')
    def test_StreamNow_tabs(self):
        count_elements(self.block.get('tabs'), TABS_COUNT)

    @allure.story('programs')
    def test_StreamNow_programs(self):
        for tab in self.block.get('tabs'):
            count_elements(tab.get('programs'), PROGRAMS_COUNT)


@allure.feature('morda', 'StreamNow')
class TestStreamNowTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK], cgi_params={'yandexuid': 572909971517226139})
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_StreamNow_absence(self):
        absence(self.block)
