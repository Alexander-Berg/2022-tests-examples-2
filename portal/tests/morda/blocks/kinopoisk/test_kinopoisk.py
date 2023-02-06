# -*- coding: utf-8 -*-
import allure

from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, fetch_data, check_show, no_show, count_elements, absence


BLOCK = 'Kinopoisk'
GROUP_COUNT = 7
FILM_COUNT = 10


@allure.feature('morda', 'kinopoisk')
class TestKinopoiskBigMoscow(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_kinopoisk_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_kinopoisk_show(self):
        check_show(self.block)

    @allure.story('groups')
    def test_kinopoisk_tabs(self):
        count_elements(self.block.get('groups'), GROUP_COUNT)

    @allure.story('elements')
    def test_kinopoisk_elements(self):
        count_elements(self.block.get('groups')[0].get('films'), FILM_COUNT)


@allure.feature('morda', 'kinopoisk')
class TestKinopoiskBigMinsk(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_kinopoisk_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_kinopoisk_show(self):
        check_show(self.block)

    @allure.story('groups')
    def test_kinopoisk_tabs(self):
        count_elements(self.block.get('groups'), GROUP_COUNT)

    @allure.story('elements')
    def test_kinopoisk_elements(self):
        count_elements(self.block.get('groups')[0].get('films'), FILM_COUNT)


@allure.feature('morda', 'kinopoisk')
class TestKinopoiskBigAstana(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_kinopoisk_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_kinopoisk_show(self):
        check_show(self.block)

    @allure.story('groups')
    def test_kinopoisk_tabs(self):
        count_elements(self.block.get('groups'), GROUP_COUNT)

    @allure.story('elements')
    def test_kinopoisk_elements(self):
        count_elements(self.block.get('groups')[0].get('films'), FILM_COUNT)


@allure.feature('morda', 'kinopoisk')
class TestKinopoiskBigTashkent(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_kinopoisk_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_kinopoisk_show(self):
        no_show(self.block)


@allure.feature('morda', 'kinopoisk')
class TestKinopoiskTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_kinopoisk_absence(self):
        absence(self.block)


@allure.feature('morda', 'kinopoisk')
class TestKinopoiskTouchMinsk(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_kinopoisk_absence(self):
        absence(self.block)


@allure.feature('morda', 'kinopoisk')
class TestKinopoiskTouchAstana(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_kinopoisk_absence(self):
        absence(self.block)


@allure.feature('morda', 'kinopoisk')
class TestKinopoiskTouchTashkent(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_kinopoisk_absence(self):
        absence(self.block)
