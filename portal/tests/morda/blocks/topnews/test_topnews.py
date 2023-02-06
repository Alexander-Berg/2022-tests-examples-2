# -*- coding: utf-8 -*-
import logging
import allure
import pytest

from common import schema
from common.morda import DesktopMain, DesktopCom, DesktopComTr, TouchMain, TouchCom, TouchComTr
from common.client import MordaClient
from common.geobase import Regions

logger = logging.getLogger(__name__)

"""
HOME-37220
Проверяет работу блока Новости
Бывший mordabackend/topnews/TopnewsBlockTest.java
"""

BLOCK = 'Topnews'
DOMAIN_PREFIX = 'news.yandex.'
DOMAIN_PREFIX_SPORT = 'yandex.{domain}/sport'

DEFAULT_DESKTOP_TABS_NUM_GE = 2
DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE = 5

DEFAULT_TOUCH_TABS_NUM_GE = 10
DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE = 5

YASM_SIGNAL_NAME = 'morda_topnews_{}_tttt'


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsDesktopMoscow(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW))
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsDesktopKyiv(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.KYIV))
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ua'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsDesktopMinsk(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.MINSK))
        self.block = self.data.get(BLOCK)
        self.href_domain = 'by'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsDesktopAstana(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.ASTANA))
        self.block = self.data.get(BLOCK)
        self.href_domain = 'kz'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsDesktopCom(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopCom())

    @allure.story('block does not exist')
    def test_topnews_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


# TODO: cleanup when experiment is finished
@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsDesktopComTrOld(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopComTr(params=dict(ab_flags='comtr_standart=0')))

    @allure.story('block does not exist')
    def test_topnews_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsDesktopComTr(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopComTr(params=dict(ab_flags='comtr_standart=1')))    # TODO: cleanup when experiment is finished
        self.block = self.data.get(BLOCK)

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsTouchMoscow(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW))
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEFAULT_TOUCH_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsTouchKyiv(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.KYIV))
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ua'
        self.tabs_num_ge = DEFAULT_TOUCH_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsTouchMinsk(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.MINSK))
        self.block = self.data.get(BLOCK)
        self.href_domain = 'by'
        self.tabs_num_ge = DEFAULT_TOUCH_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsTouchAstana(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.ASTANA))
        self.block = self.data.get(BLOCK)
        self.href_domain = 'kz'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsTouchCom(object):
    def setup_class(self):
        self.data = _fetch_data(TouchCom())

    @allure.story('block does not exist')
    def test_topnews_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


# TODO: cleanup when experiment is finished
@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsTouchComTrOld(object):
    def setup_class(self):
        self.data = _fetch_data(TouchComTr(params=dict(ab_flags='comtr_standart=0')))

    @allure.story('block does not exist')
    def test_topnews_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'

@allure.feature('morda', 'topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsTouchComTr(object):
    def setup_class(self):
        self.data = _fetch_data(TouchComTr(params=dict(ab_flags='comtr_standart=1')))    # TODO: cleanup when experiment is finished
        self.block = self.data.get(BLOCK)

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)


# ==============================


def _fetch_data(morda, **kwargs):
    client = MordaClient(morda)
    response = client.cleanvars([BLOCK], **kwargs).send()
    with allure.step('Fetch data'):
        assert response.is_ok(), 'Failed to get cleanvars'
    return response.json()


def _test_existance(test_case):
    with allure.step('Test if block exists'):
        assert test_case.data[BLOCK], 'Failed to get block'


def _test_common(test_case):
    with allure.step('Test if block shows'):
        assert test_case.block['show'], 'Show must be 1'


def _test_date(test_case):
    with allure.step('Test if date ok'):
        assert test_case.block['BigDay'], 'BigDay was not found'
        assert test_case.block['BigMonth'], 'BigMonth was not found'
        assert test_case.block['BigWday'], 'BigWday was not found'


def _test_tabs(test_case):
    with allure.step('Check tabs'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        assert len(test_case.block['tabs']) >= test_case.tabs_num_ge, (
                'Tabs num: must be more than '+str(test_case.tabs_num_ge))
        for tab in test_case.block['tabs']:
            assert len(tab.get('news')) >= test_case.news_in_tabs_num_ge, (
                    'News num in tab: must be more than '+str(test_case.news_in_tabs_num_ge))
        first_tab = test_case.block['tabs'][0]
        assert first_tab.get('default'), 'First tab must have default flag'


def _test_href(test_case):
    with allure.step('Check main href'):
        block = test_case.block
        domain = test_case.href_domain
        main_href = block.get('href')
        assert main_href.index(DOMAIN_PREFIX+domain), 'Domain must be '+DOMAIN_PREFIX+domain

    with allure.step('Check special href'):
        if 'special' in block:
            special_href = block.get('special').get('href')
            assert(DOMAIN_PREFIX+domain in special_href or DOMAIN_PREFIX_SPORT.format(domain=domain) in special_href),\
                'Domain must be '+DOMAIN_PREFIX+domain + ' or ' + DOMAIN_PREFIX_SPORT.format(domain=domain)

    with allure.step('Check news and tabs href'):
        for tab in block.get('tabs'):
            tab_href = tab.get('href')
            assert tab_href.index(DOMAIN_PREFIX+domain), 'Domain must be '+DOMAIN_PREFIX+domain
            for n in tab.get('news'):
                n_href = n.get('href')
                assert n_href.index(DOMAIN_PREFIX+domain), 'Domain must be '+DOMAIN_PREFIX+domain
