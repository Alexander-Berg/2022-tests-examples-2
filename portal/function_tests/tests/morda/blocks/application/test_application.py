# -*- coding: utf-8 -*-
import allure

from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, check_show, fetch_data, count_elements, absence


BLOCK = 'Application'


@allure.feature('morda', 'application')
class TestApplicationTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_rasp_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_rasp_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_rasp_href_tab(self):
        count_elements(self.block.get('list'), 0)


@allure.feature('morda', 'application')
class TestRaspTouchSaintPetersburg(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.SAINT_PETERSBURG), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_rasp_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_rasp_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_rasp_href_tab(self):
        count_elements(self.block.get('list'), 0)


@allure.feature('morda', 'application')
class TestRaspTouchAstana(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_rasp_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_rasp_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_rasp_href_tab(self):
        count_elements(self.block.get('list'), 0)


@allure.feature('morda', 'application')
class TestRaspTouchMinsk(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'by'
        cls.domain_avia = 'ru'

    @allure.story('block exists')
    def test_rasp_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_rasp_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_rasp_href_tab(self):
        count_elements(self.block.get('list'), 0)


@allure.feature('morda', 'application')
class TestRaspTouchTashkent(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'uz'
        cls.domain_avia = 'ru'

    @allure.story('block exists')
    def test_rasp_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_rasp_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_rasp_href_tab(self):
        count_elements(self.block.get('list'), 0)


@allure.feature('morda', 'application')
class TestRaspDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_rasp_existance(self):
        absence(self.block)


@allure.feature('morda', 'application')
class TestRaspDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_rasp_existance(self):
        absence(self.block)


@allure.feature('morda', 'application')
class TestRaspDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_rasp_existance(self):
        absence(self.block)


@allure.feature('morda', 'application')
class TestRaspDesktopTashkent(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_rasp_existance(self):
        absence(self.block)
