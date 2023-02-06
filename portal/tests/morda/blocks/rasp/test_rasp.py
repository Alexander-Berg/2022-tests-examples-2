# -*- coding: utf-8 -*-
import allure

from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, check_show, absence, check_href_host, fetch_data


BLOCK = 'Rasp'

dict_domain_prefix = {
    'plane': 'avia.yandex.',
    'train': 'travel.yandex.',
    'bus': 't.rasp.yandex.',
    'suburban': 't.rasp.yandex.',
    'water': 't.rasp.yandex.'
}

dict_ids = {
    'bus': 'bus',
    'plane': 'aero',
    'suburban': 'el',
    'water': 'ship',
    'train': 'train'
}


@allure.feature('morda', 'rasp')
class TestRaspTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_rasp_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_rasp_show(self):
        check_show(self.block)

    @allure.story('url list')
    def test_rasp_href_tab(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            check_href_host(tab, dict_domain_prefix.get(tab_id) + self.domain, key_url='url')

    @allure.story('flags mutch with list')
    def test_rasp_flags(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            alias = dict_ids.get(tab_id)
            assert self.block.get(alias), 'flag ' + str(alias) + ' must be 1'


@allure.feature('morda', 'rasp')
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

    @allure.story('url list')
    def test_rasp_href_tab(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            check_href_host(tab, dict_domain_prefix.get(tab_id) + self.domain, key_url='url')

    @allure.story('flags mutch with list')
    def test_rasp_flags(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            alias = dict_ids.get(tab_id)
            print alias
            assert self.block.get(alias), 'flag ' + str(alias) + ' must be 1'


@allure.feature('morda', 'rasp')
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

    @allure.story('url list')
    def test_rasp_href_tab(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            if tab_id not in ['train', 'bus', 'suburban']:          # Always t.rasp.yandex.RU
                check_href_host(tab, dict_domain_prefix.get(tab_id) + self.domain, key_url='url')

    @allure.story('flags mutch with list')
    def test_rasp_flags(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            alias = dict_ids.get(tab_id)
            assert self.block.get(alias), 'flag ' + str(alias) + ' must be 1'


@allure.feature('morda', 'rasp')
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

    @allure.story('url list')
    def test_rasp_href_tab(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            domain = self.domain
            if (tab_id == 'plane'):
                domain = self.domain_avia
            if tab_id not in ['train', 'bus', 'suburban']:
                check_href_host(tab, dict_domain_prefix.get(tab_id) + domain, key_url='url')

    @allure.story('flags mutch with list')
    def test_rasp_flags(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            alias = dict_ids.get(tab_id)
            assert self.block.get(alias), 'flag ' + str(alias) + ' must be 1'


@allure.feature('morda', 'rasp')
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

    @allure.story('url list')
    def test_rasp_href_tab(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            domain = self.domain
            if (tab_id == 'plane'):
                domain = self.domain_avia
            if tab_id not in ['train', 'bus', 'suburban']:
                check_href_host(tab, dict_domain_prefix.get(tab_id) + domain, key_url='url')

    @allure.story('flags mutch with list')
    def test_rasp_flags(self):
        for tab in self.block.get('list'):
            tab_id = tab.get('id')
            alias = dict_ids.get(tab_id)
            assert self.block.get(alias), 'flag ' + str(alias) + ' must be 1'


@allure.feature('morda', 'rasp')
class TestRaspDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_rasp_existance(self):
        absence(self.block)


@allure.feature('morda', 'rasp')
class TestRaspDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_rasp_existance(self):
        absence(self.block)


@allure.feature('morda', 'rasp')
class TestRaspDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_rasp_existance(self):
        absence(self.block)


@allure.feature('morda', 'rasp')
class TestRaspDesktopTashkent(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('block exists')
    def test_rasp_existance(self):
        absence(self.block)
