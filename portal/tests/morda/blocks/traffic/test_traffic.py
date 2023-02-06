# -*- coding: utf-8 -*-
import allure

from common import schema
from common.morda import DesktopMain, TouchMain
from common.geobase import Regions, ipByRegion
from common.blocks import existance, check_show, no_show, fetch_data


BLOCK = 'Traffic'
DOMAIN = 'yandex.{domain}/maps'
DOMAIN_TR = 'yandex.{domain}/harita'


@allure.feature('morda', 'traffic')
class TestTrafficTouchMoscow(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MOSCOW), [BLOCK], {'X-Forwarded-For': ipByRegion.MOSCOW})
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_Traffic_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Traffic_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_Traffic_href(self):
        domain = self.domain
        url = self.block.get('href')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_traffic_schema(self):
        schema.validate_schema_by_block(self.block, 'traffic', 'touch')


@allure.feature('morda', 'traffic')
class TestTrafficTouchAstana(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ASTANA), [BLOCK], {'X-Forwarded-For': ipByRegion.ASTANA})
        cls.block = data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_Traffic_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Traffic_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_Traffic_href(self):
        domain = self.domain
        url = self.block.get('href')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_traffic_schema(self):
        schema.validate_schema_by_block(self.block, 'traffic', 'touch')


@allure.feature('morda', 'traffic')
class TestTrafficTouchMinsk(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.MINSK), [BLOCK], {'X-Forwarded-For': ipByRegion.MINSK})
        cls.block = data.get(BLOCK)
        cls.domain = 'by'

    @allure.story('block exists')
    def test_Traffic_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Traffic_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_Traffic_href(self):
        domain = self.domain
        url = self.block.get('href')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_traffic_schema(self):
        schema.validate_schema_by_block(self.block, 'traffic', 'touch')


@allure.feature('morda', 'traffic')
class TestTrafficTouchIstambul(object):
    def setup_class(cls):
        data = fetch_data(TouchMain(region=Regions.ISTANBUL), [BLOCK], {'X-Forwarded-For': ipByRegion.ISTANBUL})
        cls.block = data.get(BLOCK)
        cls.domain = 'com.tr'

    @allure.story('block exists')
    def test_Traffic_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Traffic_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_Traffic_href(self):
        domain = self.domain
        url = self.block.get('href')
        assert (DOMAIN_TR.format(domain=domain) in url), 'Domain must be ' + DOMAIN_TR.format(domain=domain)

    @allure.story('schema')
    def test_traffic_schema(self):
        schema.validate_schema_by_block(self.block, 'traffic', 'touch')


@allure.feature('morda', 'traffic')
class TestTrafficDesktopMoscow(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK], {'X-Forwarded-For': ipByRegion.MOSCOW})
        cls.block = data.get(BLOCK)
        cls.domain = 'ru'

    @allure.story('block exists')
    def test_Traffic_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Traffic_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_Traffic_href(self):
        domain = self.domain
        url = self.block.get('href')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_traffic_schema(self):
        schema.validate_schema_by_block(self.block, 'traffic', 'desktop')


@allure.feature('morda', 'traffic')
class TestTrafficDesktopMinsk(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MINSK), [BLOCK], {'X-Forwarded-For': ipByRegion.MINSK})
        cls.block = data.get(BLOCK)
        cls.domain = 'by'

    @allure.story('block exists')
    def test_Traffic_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Traffic_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_Traffic_href(self):
        domain = self.domain
        url = self.block.get('href')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_traffic_schema(self):
        schema.validate_schema_by_block(self.block, 'traffic', 'desktop')


@allure.feature('morda', 'traffic')
class TestTrafficDesktopAstana(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.ASTANA), [BLOCK], {'X-Forwarded-For': ipByRegion.ASTANA})
        cls.block = data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_Traffic_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Traffic_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_Traffic_href(self):
        domain = self.domain
        url = self.block.get('href')
        assert (DOMAIN.format(domain=domain) in url), 'Domain must be ' + DOMAIN.format(domain=domain)

    @allure.story('schema')
    def test_traffic_schema(self):
        schema.validate_schema_by_block(self.block, 'traffic', 'desktop')


@allure.feature('morda', 'traffic')
class TestTrafficDesktopIstambul(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.ISTANBUL), [BLOCK], {'X-Forwarded-For': ipByRegion.ISTANBUL})
        cls.block = data.get(BLOCK)
        cls.domain = 'com.tr'

    @allure.story('block exists')
    def test_Traffic_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Traffic_show(self):
        check_show(self.block)

    @allure.story('localityURL')
    def test_Traffic_href(self):
        domain = self.domain
        url = self.block.get('href')
        assert (DOMAIN_TR.format(domain=domain) in url), 'Domain must be ' + DOMAIN_TR.format(domain=domain)

    @allure.story('schema')
    def test_traffic_schema(self):
        schema.validate_schema_by_block(self.block, 'traffic', 'desktop')


@allure.feature('morda', 'traffic')
class TestTrafficDesktopWashington(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.WASHINGTON), [BLOCK], {'X-Forwarded-For': ipByRegion.WASHINGTON})
        cls.block = data.get(BLOCK)
        cls.domain = 'kz'

    @allure.story('block exists')
    def test_Traffic_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_Traffic_show(self):
        no_show(self.block)
