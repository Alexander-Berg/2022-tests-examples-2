# -*- coding: utf-8 -*-
import allure

from common import schema
from common.morda import DesktopMain
from common.geobase import Regions
from common.blocks import fetch_data


BLOCK = 'Geo'


class TestGeoDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('schema')
    def test_geo_schema(self):
        schema.validate_schema_by_block(self.block, 'geo', 'desktop')


class TestGeoDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('schema')
    def test_geo_schema(self):
        schema.validate_schema_by_block(self.block, 'geo', 'desktop')


class TestGeoDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('schema')
    def test_geo_schema(self):
        schema.validate_schema_by_block(self.block, 'geo', 'desktop')


class TestGeoDesktopTashkent(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.TASHKENT), [BLOCK])
        cls.block = cls.data.get(BLOCK)

    @allure.story('schema')
    def test_geo_schema(self):
        schema.validate_schema_by_block(self.block, 'geo', 'desktop')
