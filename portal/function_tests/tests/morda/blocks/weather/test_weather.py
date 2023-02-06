# -*- coding: utf-8 -*-
import allure

from common import schema
from common.morda import DesktopMain, TouchMain, DesktopComTr
from common.geobase import Regions
from common.blocks import existance, check_show, fetch_data


BLOCK = 'Weather'
DOMAIN = 'yandex.{domain}/pogoda'
DOMAIN_TR = 'yandex.{domain}/hava'


@allure.feature('morda', 'weather')
class TestWeatherTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_weather_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_weather_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_weather_href(self):
        domain = self.domain
        url = self.block.get('url')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_weather_schema(self):
        schema.validate_schema_by_block(self.block, 'weather', 'touch')


@allure.feature('morda', 'weather')
class TestWeatherTouchAstana(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_weather_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_weather_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_weather_href(self):
        domain = self.domain
        url = self.block.get('url')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_weather_schema(self):
        schema.validate_schema_by_block(self.block, 'weather', 'touch')


@allure.feature('morda', 'weather')
class TestWeatherTouchMinsk(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'by'

    @allure.story('block exists')
    def test_weather_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_weather_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_weather_href(self):
        domain = self.domain
        url = self.block.get('url')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_weather_schema(self):
        schema.validate_schema_by_block(self.block, 'weather', 'touch')


@allure.feature('morda', 'weather')
class TestweatherDesktopMoscow(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_weather_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_weather_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_weather_href(self):
        domain = self.domain
        url = self.block.get('url')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_weather_schema(self):
        schema.validate_schema_by_block(self.block, 'weather', 'touch')


@allure.feature('morda', 'weather')
class TestWeatherDesktopMinsk(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'by'

    @allure.story('block exists')
    def test_weather_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_weather_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_weather_href(self):
        domain = self.domain
        url = self.block.get('url')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_weather_schema(self):
        schema.validate_schema_by_block(self.block, 'weather', 'desktop')


@allure.feature('morda', 'weather')
class TestWeatherDesktopAstana(object):
    def setup_class(cls):
        cls.data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK])
        cls.block = cls.data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_weather_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_weather_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_weather_href(self):
        domain = self.domain
        url = self.block.get('url')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_weather_schema(self):
        schema.validate_schema_by_block(self.block, 'weather', 'desktop')


@allure.feature('morda', 'weather')
class TestWeatherDesktopIstambul(object):
    def setup_class(cls):
        data = fetch_data(DesktopComTr(region=Regions.ISTANBUL), [BLOCK])
        cls.block = data.get(BLOCK)
        cls.domain = 'com.tr'

    @allure.story('block exists')
    def test_Weather_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Weather_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_Weather_href(self):
        domain = self.domain
        url = self.block.get('url')
        assert (DOMAIN_TR.format(domain=domain) in url), 'Domain must be ' + DOMAIN_TR.format(domain=domain)

    @allure.story('schema')
    def test_weather_schema(self):
        schema.validate_schema_by_block(self.block, 'weather', 'desktop')
