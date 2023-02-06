# -*- coding: utf-8 -*-
import allure

from common import schema
from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, check_show, count_elements, check_href_host, fetch_data, count_elements_range,\
        empty_elements


BLOCK = 'TV'
DOMAIN_PREFIX = 'tv.yandex.'
DEFAULT_TOUCH_TABS_NUM = 2
DEFAULT_TOUCH_PROGRAMMS_MAX = 10
DEFAULT_TOUCH_PROGRAMMS_MIN = 1
DEFAULT_DESKTOP_PROGRAMMS_NUM = 3


@allure.feature('morda', 'tv')
class TestTvTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_tv_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_tv_show(self):
        check_show(self.block)

    @allure.story('tabs')
    def test_tv_tabs(self):
        count_elements(self.block.get('tabs'), DEFAULT_TOUCH_TABS_NUM)

    @allure.story('programms')
    def test_tv_programs(self):
        for tab in self.block.get('tabs'):
            if tab.get('type') != 'channel':
                count_elements_range(tab.get('programms'), DEFAULT_TOUCH_PROGRAMMS_MIN, DEFAULT_TOUCH_PROGRAMMS_MAX)
            else:
                empty_elements(tab.get('programms'))

    @allure.story('href')
    def test_tv_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('href tab')
    def test_tv_href_tab(self):
        for tab in self.block.get('tabs'):
            check_href_host(tab, DOMAIN_PREFIX + self.domain)

    @allure.story('href programm')
    def test_tv_href_program(self):
        for tab in self.block.get('tabs'):
            for program in tab.get('programms'):
                check_href_host(program, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_tv_schema(self):
        schema.validate_schema_by_block(self.block, 'tv', 'touch')


class TestTvTouchAstana(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_tv_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_tv_show(self):
        check_show(self.block)

    @allure.story('tabs')
    def test_tv_tabs(self):
        count_elements(self.block.get('tabs'), DEFAULT_TOUCH_TABS_NUM)

    @allure.story('programms')
    def test_tv_programs(self):
        for tab in self.block.get('tabs'):
            if tab.get('type') != 'channel':
                count_elements_range(tab.get('programms'), DEFAULT_TOUCH_PROGRAMMS_MIN, DEFAULT_TOUCH_PROGRAMMS_MAX)
            else:
                empty_elements(tab.get('programms'))

    @allure.story('href')
    def test_tv_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('href tab')
    def test_tv_href_tab(self):
        for tab in self.block.get('tabs'):
            check_href_host(tab, DOMAIN_PREFIX + self.domain)

    @allure.story('href programm')
    def test_tv_href_program(self):
        for tab in self.block.get('tabs'):
            for program in tab.get('programms'):
                check_href_host(program, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_tv_schema(self):
        schema.validate_schema_by_block(self.block, 'tv', 'touch')


class TestTvTouchMinsk(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'by'

    @allure.story('block exists')
    def test_tv_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_tv_show(self):
        check_show(self.block)

    @allure.story('tabs')
    def test_tv_tabs(self):
        count_elements(self.block.get('tabs'), DEFAULT_TOUCH_TABS_NUM)

    @allure.story('programms')
    def test_tv_programs(self):
        for tab in self.block.get('tabs'):
            if tab.get('type') != 'channel':
                count_elements_range(tab.get('programms'), DEFAULT_TOUCH_PROGRAMMS_MIN, DEFAULT_TOUCH_PROGRAMMS_MAX)
            else:
                empty_elements(tab.get('programms'))

    @allure.story('href')
    def test_tv_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('href tab')
    def test_tv_href_tab(self):
        for tab in self.block.get('tabs'):
            check_href_host(tab, DOMAIN_PREFIX + self.domain)

    @allure.story('href programm')
    def test_tv_href_program(self):
        for tab in self.block.get('tabs'):
            for program in tab.get('programms'):
                check_href_host(program, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_tv_schema(self):
        schema.validate_schema_by_block(self.block, 'tv', 'touch')


class TestTvTouchTashkent(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'uz'

    @allure.story('block exists')
    def test_tv_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_tv_show(self):
        check_show(self.block)

    @allure.story('tabs')
    def test_tv_tabs(self):
        count_elements(self.block.get('tabs'), DEFAULT_TOUCH_TABS_NUM)

    @allure.story('programs')
    def test_tv_programs(self):
        for tab in self.block.get('tabs'):
            if tab.get('type') != 'channel':
                count_elements_range(tab.get('programms'), DEFAULT_TOUCH_PROGRAMMS_MIN, DEFAULT_TOUCH_PROGRAMMS_MAX)
            else:
                empty_elements(tab.get('programms'))

    @allure.story('href')
    def test_tv_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('href tab')
    def test_tv_href_tab(self):
        for tab in self.block.get('tabs'):
            check_href_host(tab, DOMAIN_PREFIX + self.domain)

    @allure.story('href programm')
    def test_tv_href_program(self):
        for tab in self.block.get('tabs'):
            for program in tab.get('programms'):
                check_href_host(program, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_tv_schema(self):
        schema.validate_schema_by_block(self.block, 'tv', 'touch')


class TestTvDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_tv_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_tv_show(self):
        check_show(self.block)

    @allure.story('programs')
    def test_tv_programs(self):
        count_elements(self.block.get('programms'), DEFAULT_DESKTOP_PROGRAMMS_NUM)

    @allure.story('href')
    def test_tv_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('href program')
    def test_tv_href_tab(self):
        for program in self.block.get('programms'):
            check_href_host(program, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_tv_schema(self):
        schema.validate_schema_by_block(self.block, 'tv', 'desktop')


class TestTvDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'by'

    @allure.story('block exists')
    def test_tv_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_tv_show(self):
        check_show(self.block)

    @allure.story('programs')
    def test_tv_programs(self):
        count_elements(self.block.get('programms'), DEFAULT_DESKTOP_PROGRAMMS_NUM)

    @allure.story('href')
    def test_tv_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('href program')
    def test_tv_href_tab(self):
        for program in self.block.get('programms'):
            check_href_host(program, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_tv_schema(self):
        schema.validate_schema_by_block(self.block, 'tv', 'desktop')


class TestTvDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_tv_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_tv_show(self):
        check_show(self.block)

    @allure.story('programs')
    def test_tv_programs(self):
        count_elements(self.block.get('programms'), DEFAULT_DESKTOP_PROGRAMMS_NUM)

    @allure.story('href')
    def test_tv_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('href program')
    def test_tv_href_tab(self):
        for program in self.block.get('programms'):
            check_href_host(program, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_tv_schema(self):
        schema.validate_schema_by_block(self.block, 'tv', 'desktop')


class TestTvDesktopTashkent(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'uz'

    @allure.story('block exists')
    def test_tv_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_tv_show(self):
        check_show(self.block)

    @allure.story('programs')
    def test_tv_programs(self):
        count_elements(self.block.get('programms'), DEFAULT_DESKTOP_PROGRAMMS_NUM)

    @allure.story('href')
    def test_tv_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('href program')
    def test_tv_href_tab(self):
        for program in self.block.get('programms'):
            check_href_host(program, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_tv_schema(self):
        schema.validate_schema_by_block(self.block, 'tv', 'desktop')
