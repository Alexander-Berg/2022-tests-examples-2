# -*- coding: utf-8 -*-
import allure
import pytest

from common import schema
from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, check_show, no_show, count_elements, check_href_host, fetch_data


BLOCK = 'Afisha'
BLOCKS = ['Afisha', 'Stream']  # На десктопе есть зависимость от стрима
DOMAIN_PREFIX = 'afisha.yandex.'
DEFAULT_TOUCH_EVENTS_NUM = 10


@pytest.mark.skip(reason="Блок афиши отключен")
@allure.feature('morda', 'afisha')
class TestAfishaTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_afisha_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_afisha_show(self):
        check_show(self.block)

    @allure.story('events')
    def test_afisha_events(self):
        count_elements(self.block.get('events'), DEFAULT_TOUCH_EVENTS_NUM)

    @allure.story('href')
    def test_afisha_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_afisha_schema(self):
        schema.validate_schema_by_block(self.block, 'afisha', 'touch')


@pytest.mark.skip(reason="Блок афиши отключен")
@allure.feature('morda', 'afisha')
class TestAfishaTouchAstana(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_afisha_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_afisha_show(self):
        check_show(self.block)

    @allure.story('events')
    def test_afisha_events(self):
        count_elements(self.block.get('events'), DEFAULT_TOUCH_EVENTS_NUM)

    @allure.story('href')
    def test_afisha_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @pytest.mark.skip(reason="HOME-57672")
    @allure.story('schema')
    def test_afisha_schema(self):
        schema.validate_schema_by_block(self.block, 'afisha', 'touch')


@pytest.mark.skip(reason="Блок афиши отключен")
@allure.feature('morda', 'afisha')
class TestAfishaTouchMinsk(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'by'

    @allure.story('block exists')
    def test_afisha_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_afisha_show(self):
        check_show(self.block)

    @allure.story('events')
    def test_afisha_events(self):
        count_elements(self.block.get('events'), DEFAULT_TOUCH_EVENTS_NUM)

    @allure.story('href')
    def test_afisha_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain)

    @allure.story('schema')
    def test_afisha_schema(self):
        schema.validate_schema_by_block(self.block, 'afisha', 'touch')


@pytest.mark.skip(reason="Блок афиши отключен")
@allure.feature('morda', 'afisha')
class TestAfishaDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), BLOCKS)
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_afisha_existance(self):
        existance(self.block)

    @allure.story('block does not exist')
    def test_afisha_no_show(self):
        if (self.data.get('Stream') and self.data.get('Stream').get('show')):
            no_show(self.block)
        else:
            check_show(self.block)


@pytest.mark.skip(reason="Блок афиши отключен")
@allure.feature('morda', 'afisha')
class TestAfishaDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MINSK), BLOCKS)
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_afisha_existance(self):
        existance(self.block)

    @allure.story('block does not exist')
    def test_afisha_no_show(self):
        if (self.data.get('Stream') and self.data.get('Stream').get('show')):
            no_show(self.block)
        else:
            check_show(self.block)


@pytest.mark.skip(reason="Блок афиши отключен")
@allure.feature('morda', 'afisha')
class TestAfishaDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), BLOCKS)
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_afisha_existance(self):
        existance(self.block)

    @allure.story('block does not exist')
    def test_afisha_no_show(self):
        if (self.data.get('Stream') and self.data.get('Stream').get('show')):
            no_show(self.block)
        else:
            check_show(self.block)
