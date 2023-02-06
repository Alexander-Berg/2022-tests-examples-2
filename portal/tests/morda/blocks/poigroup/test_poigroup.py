# -*- coding: utf-8 -*-
import allure

from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, check_show, absence, fetch_data, count_elements


BLOCK = 'PoiGroups'


@allure.feature('morda', 'poigroups')
class TestPoiGroupsTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_poigroup_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_poigroup_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_poigroup_count_list(self):
        count_elements(self.block.get('list'), 0)


@allure.feature('morda', 'poigroups')
class TestPoiGroupsTouchAstana(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_poigroup_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_poigroup_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_poigroup_count_list(self):
        count_elements(self.block.get('list'), 0)


@allure.feature('morda', 'poigroups')
class TestPoiGroupsTouchMinsk(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_poigroup_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_poigroup_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_poigroup_count_list(self):
        count_elements(self.block.get('list'), 0)


@allure.feature('morda', 'poigroups')
class TestPoiGroupsTouchTashkent(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_poigroups_existance(self):
        absence(self.block)


@allure.feature('morda', 'poigroups')
class TestPoiGroupsDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_poigroups_existance(self):
        absence(self.block)


@allure.feature('morda', 'poigroups')
class TestPoiGroupsDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_poigroups_existance(self):
        absence(self.block)


@allure.feature('morda', 'poigroups')
class TestPoiGroupsDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_poigroups_existance(self):
        absence(self.block)


@allure.feature('morda', 'poigroups')
class TestPoiGroupsDesktopTashkent(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_poigroups_existance(self):
        absence(self.block)
