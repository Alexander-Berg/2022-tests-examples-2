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

BLOCK = 'Stocks'
DOMAIN_PREFIX = 'news.yandex.'

YASM_SIGNAL_NAME = 'morda_stocks_{}_tttt'


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopMoscow(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW))
        self.block = self.data.get(BLOCK)

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopKyiv(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.KYIV))
        self.block = self.data.get(BLOCK)

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopMinsk(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.MINSK))
        self.block = self.data.get(BLOCK)

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopAstana(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.ASTANA))
        self.block = self.data.get(BLOCK)

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopCom(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopCom())

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


# TODO: cleanup when experiment is finished
@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopComTrOld(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopComTr(params=dict(ab_flags='comtr_standart=0')))
        self.block = self.data.get(BLOCK)['lite']

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self, 'lite')

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {40052, 40053})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, None, 'yandex.com.tr/search')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksDesktopComTr(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopComTr(params=dict(ab_flags='comtr_standart=1')))   # TODO: cleanup when experiment is finished

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchMoscow(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW))
        self.block = self.data.get(BLOCK)['blocks']

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self, 'blocks')

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_touch_set(self, {1, 23, 2002, 2000, 1006})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_touch_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_touch_href(self, None, 'ru')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_touch_xiva(self)


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchKyiv(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.KYIV))
        self.block = self.data.get(BLOCK)['blocks']

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self, 'blocks')

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_touch_set(self, {40043, 40042, 40010, 3005, 3027, 3015})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_touch_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_touch_href(self, None, 'ua')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_touch_xiva(self)


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchMinsk(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.MINSK))
        self.block = self.data.get(BLOCK)['blocks']

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self, 'blocks')

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_touch_set(self, {40090, 40091, 40092, 4011, 4010, 4020})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_touch_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_touch_href(self, None, 'by')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_touch_xiva(self)


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchAstana(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.ASTANA))
        self.block = self.data.get(BLOCK)['blocks']

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self, 'blocks')

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_touch_set(self, {5000, 5001, 5002, 71001, 71000, 71002})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_touch_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_touch_href(self, None, 'kz')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_touch_xiva(self)


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchCom(object):
    def setup_class(self):
        self.data = _fetch_data(TouchCom())

    @allure.story('block does not exist')
    def test_stocks_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


# TODO: cleanup when experiment is finished
@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchComTrOld(object):
    def setup_class(self):
        self.data = _fetch_data(TouchComTr(params=dict(ab_flags='comtr_standart=0')))
        self.block = self.data.get(BLOCK)['lite']

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self, 'lite')

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_set(self, {40052, 40053})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_href(self, None, 'yandex.com.tr/search')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_xiva(self)


@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestStocksTouchComTr(object):
    def setup_class(self):
        self.data = _fetch_data(TouchComTr(params=dict(ab_flags='comtr_standart=1')))   # TODO: cleanup when experiment is finished
        self.block = self.data.get(BLOCK)['blocks']

    @allure.story('block exists')
    def test_stocks_existance(self):
        _test_existance(self, 'blocks')

    @allure.story('stocks set')
    def test_stocks_set(self):
        _test_stocks_touch_set(self, {40052, 40053})

    @allure.story('values')
    def test_stocks_values(self):
        _test_stocks_touch_values(self)

    @allure.story('href')
    def test_stocks_href(self):
        _test_stocks_touch_href(self, None, 'yandex.com.tr/search')

    @allure.story('xiva')
    def test_stocks_xiva(self):
        _test_stocks_touch_xiva(self)


# ==============================


def _test_existance(test_case, subblock):
    with allure.step('Test if block exists'):
        assert test_case.data[BLOCK][subblock], 'Failed to get block'


def _test_stocks_set(test_case, stocks_set):
    with allure.step('Test if normal set of stocks presented'):
        income_set = {int(el['id']) for el in test_case.block}
        assert stocks_set == income_set, 'Failed to check stocks set'


def _test_stocks_touch_set(test_case, stocks_set):
    with allure.step('Test if normal set of stocks presented'):
        income_set = set()
        for block in test_case.block:
            for stock in block['rows']:
                income_set.add(int(stock['id']))
    assert stocks_set == income_set, 'Failed to check stocks set'


def _test_stocks_values(test_case):
    with allure.step('Test if non zero values exists'):
        for s in test_case.block:
            val = s['value'].replace(',', '.')
            assert float(val) > 0, 'Failed to check value'


def _test_stocks_touch_values(test_case):
    with allure.step('Test if non zero values exists'):
        for block in test_case.block:
            for stock in block['rows']:
                for val in stock['data']:
                    val = val['value'].replace(',', '.')
                    assert float(val) > 0, 'Failed to check value'


def _test_stocks_href(test_case, domain, path):
    _domain = path if path else DOMAIN_PREFIX+domain
    with allure.step('Check href'):
        for s in test_case.block:
            s_href = s.get('href')
            assert s_href.index(_domain), 'Domain must be '+_domain


def _test_stocks_touch_href(test_case, domain, path):
    _domain = path if path else DOMAIN_PREFIX+domain
    with allure.step('Check href'):
        for block in test_case.block:
            for stock in block['rows']:
                s_href = stock.get('href')
                assert s_href.index(_domain), 'Domain must be '+_domain


def _test_stocks_xiva(test_case):
    with allure.step('Check xiva'):
        for s in test_case.block:
            xiva_key = s.get('Xivadata')['key']
            assert xiva_key, 'Xiva key must be presented'


def _test_stocks_touch_xiva(test_case):
    with allure.step('Check xiva'):
        for s in test_case.data['Stocks']['Xivadata']:
            assert s['key'], 'Xivadata.key key must be presented'
        for s in test_case.data['Stocks']['Xivas']:
            assert s['key'], 'Xivas.key key must be presented'


def _fetch_data(morda, **kwargs):
    client = MordaClient(morda)
    response = client.cleanvars([BLOCK], **kwargs).send(**kwargs)
    with allure.step('Fetch data'):
        assert response.is_ok(), 'Failed to get cleanvars'
    return response.json()
