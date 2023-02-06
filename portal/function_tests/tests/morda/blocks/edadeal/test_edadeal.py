# -*- coding: utf-8 -*-
import allure
import pytest

from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, check_show, no_show, count_elements, check_href_host, fetch_data
from common.utils import get_field


BLOCK = 'Edadeal'
BLOCK_DESKTOP = 'EdadealInserts'
DOMAIN_PREFIX = 'edadeal.'
DEFAULT_TOUCH_RETAILERS_NUM = 10
DEFAULT_DESKTOP_RETAILERS_NUM_TOP = 10


@pytest.mark.skip(reason="Блок edadeal отключен")
@allure.feature('morda', 'edadeal')
class TestEdadealTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_edadeal_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_edadeal_show(self):
        check_show(self.block)

    @allure.story('retailers')
    def test_edadeal_events(self):
        count_elements(self.block.get('retailers'), DEFAULT_TOUCH_RETAILERS_NUM)

    @allure.story('localityURL')
    def test_edadeal_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain, 'localityURL')


@pytest.mark.skip(reason="Блок edadeal отключен")
@allure.feature('morda', 'edadeal')
class TestEdadealTouchAstana(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_edadeal_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_edadeal_show(self):
        no_show(self.block)


@pytest.mark.skip(reason="Блок edadeal отключен")
@allure.feature('morda', 'edadeal')
class TestEdadealTouchMinsk(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_edadeal_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_edadeal_show(self):
        no_show(self.block)


@pytest.mark.skip(reason="Блок edadeal отключен")
@allure.feature('morda', 'edadeal')
class TestEdadealDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK_DESKTOP])
        cls.block = cls.data.get(BLOCK_DESKTOP)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_edadeal_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_edadeal_show(self):
        check_show(self.block)

    @allure.story('data.top')
    def test_edadeal_events(self):
        count_elements(get_field(self.block, 'data.top'), DEFAULT_DESKTOP_RETAILERS_NUM_TOP)

    @allure.story('url')
    def test_edadeal_href(self):
        check_href_host(self.block, DOMAIN_PREFIX + self.domain, 'data.url')


@pytest.mark.skip(reason="Блок edadeal отключен")
@allure.feature('morda', 'edadeal')
class TestAfishaDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK_DESKTOP])
        cls.block = cls.data.get(BLOCK_DESKTOP)

    @allure.story('block exists')
    def test_edadeal_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_edadeal_show(self):
        no_show(self.block)


@pytest.mark.skip(reason="Блок edadeal отключен")
@allure.feature('morda', 'edadeal')
class TestAfishaDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK_DESKTOP])
        cls.block = cls.data.get(BLOCK_DESKTOP)

    @allure.story('block exists')
    def test_edadeal_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_edadeal_show(self):
        no_show(self.block)
