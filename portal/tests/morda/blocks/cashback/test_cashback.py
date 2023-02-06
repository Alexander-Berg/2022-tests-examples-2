# -*- coding: utf-8 -*-
import allure

from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, fetch_data, check_show, count_elements, absence


BLOCK = 'Cashback'
TABS_COUNT = 1
ELEMENTS_COUNT = 30


@allure.feature('morda', 'Cashback')
class TestCashbackBigMoscow(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_Cashback_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Cashback_show(self):
        check_show(self.block)

    @allure.story('tabs')
    def test_Cashback_tabs(self):
        count_elements(self.block.get('tabs'), TABS_COUNT)

    @allure.story('elements')
    def test_Cashback_elements(self):
        for tab in self.block.get('tabs'):
            count_elements(tab.get('elements'), ELEMENTS_COUNT)


@allure.feature('morda', 'Cashback')
class TestCashbackBigMinsk(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_Cashback_absence(self):
        absence(self.block)


@allure.feature('morda', 'Cashback')
class TestCashbackBigAstana(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_Cashback_absence(self):
        absence(self.block)


@allure.feature('morda', 'Cashback')
class TestCashbackTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_Cashback_absence(self):
        absence(self.block)
