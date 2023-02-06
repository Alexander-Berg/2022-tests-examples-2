# -*- coding: utf-8 -*-
import allure

from common import schema
from common.morda import DesktopMain, TouchMain
from common.geobase import Regions
from common.blocks import existance, check_show, fetch_data, count_elements


BLOCK = 'Services'
DOMAIN_PREFIX = 'yandex.{domain}/all'


@allure.feature('morda', 'services')
class TestServicesTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_services_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_services_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_services_count_elements(self):
        with allure.step('exists keys'):
            assert self.block.get('hash').keys()
        for key in self.block.get('hash').keys():
            count_elements(self.block.get('hash').get(key), 0)

    @allure.story('url all')
    def test_services_all_url(self):
        all_url = self.block.get('all_url')
        assert DOMAIN_PREFIX.format(domain=self.domain) in all_url, \
            'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)

    @allure.story('schema')
    def test_services_schema(self):
        schema.validate_schema_by_block(self.block, 'services', 'touch')


# @allure.feature('morda', 'services')
# class TestServicesTouchAstana(object):
#     def setup_class(cls):
#         data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK])
#         cls.block = data.get(BLOCK)
#         cls.domain = 'kz'
#
#     @allure.story('block exists')
#     def test_services_existance(self):
#         existance(self.block)
#
#     @allure.story('block show')
#     def test_services_show(self):
#         check_show(self.block)
#
#     @allure.story('count list')
#     def test_services_count_elements(self):
#         with allure.step('exists keys'):
#             assert self.block.get('hash').keys()
#         for key in self.block.get('hash').keys():
#             count_elements(self.block.get('hash').get(key), 0)
#
#     @allure.story('url all')
#     def test_services_all_url(self):
#         all_url = self.block.get('all_url')
#         assert DOMAIN_PREFIX.format(domain=self.domain) in all_url, \
#             'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)

#    @allure.story('schema')
#    def test_services_schema(self):
#        schema.validate_schema_by_block(self.block, 'services', 'touch')


# @allure.feature('morda', 'services')
# class TestServicesTouchMinsk(object):
#     def setup_class(cls):
#         data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK])
#         cls.block = data.get(BLOCK)
#         cls.domain = 'by'
#
#     @allure.story('block exists')
#     def test_services_existance(self):
#         existance(self.block)
#
#     @allure.story('block show')
#     def test_services_show(self):
#         check_show(self.block)
#
#     @allure.story('count list')
#     def test_services_count_elements(self):
#         with allure.step('exists keys'):
#             assert self.block.get('hash').keys()
#         for key in self.block.get('hash').keys():
#             count_elements(self.block.get('hash').get(key), 0)
#
#     @allure.story('url all')
#     def test_services_all_url(self):
#         all_url = self.block.get('all_url')
#         assert DOMAIN_PREFIX.format(domain=self.domain) in all_url, \
#             'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)
#
#    @allure.story('schema')
#    def test_services_schema(self):
#        schema.validate_schema_by_block(self.block, 'services', 'touch')


@allure.feature('morda', 'services')
class TestServicesTouchTashkent(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'uz'

    @allure.story('block exists')
    def test_services_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_services_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_services_count_elements(self):
        with allure.step('exists keys'):
            assert self.block.get('hash').keys()
        for key in self.block.get('hash').keys():
            count_elements(self.block.get('hash').get(key), 0)

    @allure.story('url all')
    def test_services_all_url(self):
        all_url = self.block.get('all_url')
        assert DOMAIN_PREFIX.format(domain=self.domain) in all_url, \
            'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)

    @allure.story('schema')
    def test_services_schema(self):
        schema.validate_schema_by_block(self.block, 'services', 'touch')


@allure.feature('morda', 'services')
class TestServicesDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_services_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_services_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_services_count_elements(self):
        with allure.step('exists keys'):
            assert self.block.get('hash').keys()
        for key in self.block.get('hash').keys():
            count_elements(self.block.get('hash').get(key), 0)

    @allure.story('url all')
    def test_services_all_url(self):
        all_url = self.block.get('all_url')
        assert DOMAIN_PREFIX.format(domain=self.domain) in all_url, \
            'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)

    @allure.story('schema')
    def test_services_schema(self):
        schema.validate_schema_by_block(self.block, 'services', 'desktop')


@allure.feature('morda', 'services')
class TestServicesDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'by'

    @allure.story('block exists')
    def test_services_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_services_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_services_count_elements(self):
        with allure.step('exists keys'):
            assert self.block.get('hash').keys()
        for key in self.block.get('hash').keys():
            count_elements(self.block.get('hash').get(key), 0)

    @allure.story('url all')
    def test_services_all_url(self):
        all_url = self.block.get('all_url')
        assert DOMAIN_PREFIX.format(domain=self.domain) in all_url, \
            'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)

    @allure.story('schema')
    def test_services_schema(self):
        schema.validate_schema_by_block(self.block, 'services', 'desktop')


@allure.feature('morda', 'services')
class TestServicesDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_services_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_services_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_services_count_elements(self):
        with allure.step('exists keys'):
            assert self.block.get('hash').keys()
        for key in self.block.get('hash').keys():
            count_elements(self.block.get('hash').get(key), 0)

    @allure.story('url all')
    def test_services_all_url(self):
        all_url = self.block.get('all_url')
        assert DOMAIN_PREFIX.format(domain=self.domain) in all_url, \
            'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)

    @allure.story('schema')
    def test_services_schema(self):
        schema.validate_schema_by_block(self.block, 'services', 'desktop')


@allure.feature('morda', 'services')
class TestServicesDesktopTashkent(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'uz'

    @allure.story('block exists')
    def test_services_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_services_show(self):
        check_show(self.block)

    @allure.story('count list')
    def test_services_count_elements(self):
        with allure.step('exists keys'):
            assert self.block.get('hash').keys()
        for key in self.block.get('hash').keys():
            count_elements(self.block.get('hash').get(key), 0)

    @allure.story('url all')
    def test_services_all_url(self):
        all_url = self.block.get('all_url')
        assert DOMAIN_PREFIX.format(domain=self.domain) in all_url, \
            'Domain must be ' + DOMAIN_PREFIX.format(domain=self.domain)

    @allure.story('schema')
    def test_services_schema(self):
        schema.validate_schema_by_block(self.block, 'services', 'desktop')
