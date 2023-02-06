# -*- coding: utf-8 -*-
import logging
import allure
import pytest

from common.morda import DesktopMain, DesktopCom, DesktopComTr, TouchMain, TouchCom, TouchComTr
from common.client import MordaClient
from common.geobase import Regions

logger = logging.getLogger(__name__)

"""
HOME-37221
Проверяет работу блока Котировки
Бывший https://github.yandex-team.ru/portal/morda-backend/...
...tree/master/morda-backend-tests/src/main/java/ru/yandex/autotests/mordabackend/stocks
"""

BLOCK = 'Topnews'
SUBBLOCK = 'topnews_stocks'
DOMAIN_PREFIX = 'yandex.{domain}/news'

YASM_SIGNAL_NAME = 'morda_stocks_{}_tttt'


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopMoscow(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW))
        self.block = self.data.get(BLOCK).get(SUBBLOCK)

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self)

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {1, 23, 1006}, {2000, 2002, 1006})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, 'ru')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopKyiv(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.KYIV))
        self.block = self.data.get(BLOCK).get(SUBBLOCK)

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self)

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {40043, 40042})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, 'ua')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopMinsk(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.MINSK))
        self.block = self.data.get(BLOCK).get(SUBBLOCK)

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self)

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {4011, 4010, 4020})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, 'by')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopAstana(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.ASTANA))
        self.block = self.data.get(BLOCK).get(SUBBLOCK)

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self)

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {5000, 5001, 5002})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, 'kz')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopCom(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopCom())

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'stocks_in_topnews')
class TestStocksDesktopComTr(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopComTr())

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchMoscow(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW))
        self.block = self.data.get(BLOCK).get(SUBBLOCK)

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self)

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {1, 23, 1006}, {2000, 2002, 1006})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, 'ru')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchKyiv(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.KYIV))
        self.block = self.data.get(BLOCK).get(SUBBLOCK)

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self)

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {40043, 40042})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, 'ua')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchMinsk(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.MINSK))
        self.block = self.data.get(BLOCK).get(SUBBLOCK)

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self)

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {4011, 4010, 4020})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, 'by')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchAstana(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.ASTANA))
        self.block = self.data.get(BLOCK).get(SUBBLOCK)

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self)

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {5000, 5001, 5002})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, 'kz')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks_in_topnews')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchCom(object):
    def setup_class(self):
        self.data = _fetch_data(TouchCom())

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'stocks_in_topnews')
class TestStocksTouchComTr(object):
    def setup_class(self):
        self.data = _fetch_data(TouchComTr())

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'

# ==============================


def _test_existance(test_case):
    with allure.step('Test if block exists'):
        assert test_case.data[BLOCK][SUBBLOCK], 'Failed to get block'


def _test_stocks_set(test_case, stocks_set, secondary_stocks_set=None):
    with allure.step('Test if normal set of stocks presented'):
        income_set = {int(el['id']) for el in test_case.block}
        if secondary_stocks_set is not None:
            assert stocks_set == income_set or secondary_stocks_set == income_set, 'Failed to check stocks set'
        else:
            assert stocks_set == income_set, 'Failed to check stocks set'


def _test_stocks_values(test_case):
    with allure.step('Test if non zero values exists'):
        for s in test_case.block:
            val = s['value'].replace(',', '.')
            assert float(val) > 0, 'Failed to check value'


def _test_stocks_href(test_case, domain, path=None):
    _domain = path if path else DOMAIN_PREFIX.format(domain=domain)
    with allure.step('Check href'):
        for s in test_case.block:
            s_href = s.get('href')
            assert s_href.index(_domain), 'Domain must be '+_domain


def _test_stocks_xiva(test_case):
    with allure.step('Check xiva'):
        for s in test_case.block:
            xiva_key = s.get('Xivadata')['key']
            assert xiva_key, 'Xiva key must be presented'


def _fetch_data(morda, **kwargs):
    client = MordaClient(morda)
    response = client.cleanvars([BLOCK], **kwargs).send()
    with allure.step('Fetch data'):
        assert response.is_ok(), 'Failed to get cleanvars'
    return response.json()
