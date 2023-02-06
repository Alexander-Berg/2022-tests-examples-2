# -*- coding: utf-8 -*-
import allure

from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, check_show, no_show, fetch_data, count_elements


BLOCK = 'Etrains'
DOMAIN_PREFIX = 'rasp.yandex.{domain}/thread'


@allure.feature('morda', 'Etrains')
class TestEtrainsTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_etrains_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Etrains_show(self):
        no_show(self.block)


@allure.feature('morda', 'Etrains')
class TestEtrainsTouchZheleznodorozhny(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ZHELEZNODOROZHNY), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_etrains_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_etrains_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_etrains_href_tab(self):
        count_elements(self.block.get('tctd'), 0)
        count_elements(self.block.get('fctd'), 0)

    @allure.story('url')
    def test_services_all_url(self):
        with allure.step('check url for tctd'):
            for element in self.block.get('tctd'):
                url = element.get('url')
                assert DOMAIN_PREFIX.format(domain=self.domain) in url, \
                    'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)
        with allure.step('check url for fctd'):
            for element in self.block.get('fctd'):
                url = element.get('url')
                assert DOMAIN_PREFIX.format(domain=self.domain) in url, \
                    'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)


@allure.feature('morda', 'services')
class TestEtrainsTouchAstana(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_etrains_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Etrains_show(self):
        no_show(self.block)


@allure.feature('morda', 'Etrains')
class TestEtrainsTouchMinsk(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_etrains_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Etrains_show(self):
        no_show(self.block)


# @allure.feature('morda', 'Etrains')
# class TestEtrainsTouchBobruisk(object):
#    def setup_class(cls):
#        data = fetch_data(TouchMain(region=Regions.BOBRUISK), [BLOCK])
#        cls.block = data.get(BLOCK)
#        cls.domain = 'by'
#
#    @allure.story('block exists')
#    def test_etrains_existance(self):
#        existance(self.block)
#
#    @allure.story('block show')
#    def test_etrains_show(self):
#        check_show(self.block)
#
#    @allure.story('count list')
#    def test_etrains_href_tab(self):
#        count_elements(self.block.get('tctd'), 0)
#        count_elements(self.block.get('fctd'), 0)
#
#    @allure.story('url')
#    def test_services_all_url(self):
#        with allure.step('check url for tctd'):
#            for element in self.block.get('tctd'):
#                url = element.get('url')
#                assert DOMAIN_PREFIX.format(domain=self.domain) in url, \
#                'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)
#        with allure.step('check url for fctd'):
#            for element in self.block.get('fctd'):
#                url = element.get('url')
#                assert DOMAIN_PREFIX.format(domain=self.domain) in url, \
#                    'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)
#

@allure.feature('morda', 'Etrains')
class TestEtrainsTouchTashkent(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_etrains_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Etrains_show(self):
        no_show(self.block)


@allure.feature('morda', 'Etrains')
class TestEtrainsDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_etrains_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Etrains_show(self):
        no_show(self.block)


@allure.feature('morda', 'Etrains')
class TestEtrainsDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_etrains_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Etrains_show(self):
        no_show(self.block)


@allure.feature('morda', 'Etrains')
class TestEtrainsDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_etrains_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Etrains_show(self):
        no_show(self.block)


@allure.feature('morda', 'Etrains')
class TestEtrainsDesktopTashkent(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_etrains_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Etrains_show(self):
        no_show(self.block)
