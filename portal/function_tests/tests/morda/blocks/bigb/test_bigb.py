# -*- coding: utf-8 -*-
import allure

from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, fetch_data
import re


BLOCK = 'TargetingInfo'


@allure.feature('morda', 'bigb')
class TestBigBDesktop(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MOSCOW), [], cgi_params={'yandexuid': 572909971517226139, 'req': 'TargetingInfo'})
        cls.block = data.get('data')

    @allure.story('block exists')
    def test_block_existance(self):
        existance(self.block)

    @allure.story('promo-groups')
    def test_bigb_promo_groups(self):
        promo_groups = self.block.get('promo-groups')

        with allure.step('Test if promo-groups exists'):
            assert promo_groups, 'Show must be promo-groups in TargetingInfo'

        with allure.step('Test keywords in promo-groups'):
            for keyword, value in promo_groups.items():
                assert re.compile(r'^\d+:\d+$').match(keyword)
                assert value == 1, 'value must be 1'

    @allure.story('other_keys')
    def test_bigb_other_keys(self):
        with allure.step('Test check keys'):
            for key in ['cryptaid2', 'gender', 'age']:
                assert key in self.block.keys(), key + ' must exists'


@allure.feature('morda', 'bigb')
class TestBigBTouch(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MOSCOW), [], cgi_params={'yandexuid': 572909971517226139, 'req': 'TargetingInfo'})
        cls.block = data.get('data')

    @allure.story('block exists')
    def test_block_existance(self):
        existance(self.block)

    @allure.story('promo-groups')
    def test_bigb_promo_groups(self):
        promo_groups = self.block.get('promo-groups')

        with allure.step('Test if promo-groups exists'):
            assert promo_groups, 'Show must be promo-groups in TargetingInfo'

        with allure.step('Test keywords in promo-groups'):
            for keyword, value in promo_groups.items():
                assert re.compile(r'^\d+:\d+$').match(keyword)
                assert value == 1, 'value must be 1'

    @allure.story('other_keys')
    def test_bigb_other_keys(self):
        with allure.step('Test check keys'):
            for key in ['cryptaid2', 'gender', 'age']:
                assert key in self.block.keys(), key + ' must exists'
