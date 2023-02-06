# -*- coding: utf-8 -*-
import logging
import allure
import pytest

from common.morda import DesktopMain
from common.client import MordaClient
from common.geobase import Regions

logger = logging.getLogger(__name__)

'''
HOME-74865
Проверяет соответствие котировок контракту

Котировок нет в регионах: [162, 163, 149, 20729, 164, 159, 143, 144, 157, 10334, 10335, 187, 171, 154]
'''

BLOCK = 'Stocks'

YASM_SIGNAL_NAME = 'morda_stocks_{}_tttt'

REGIONS_WITHOUT_STOCKS = [162, 163, 149, 20729, 164, 159, 143, 144, 157, 10334, 10335, 187, 171, 154]


def get_regions():
    regions = dir(Regions)
    regions = regions[:len(regions) - 18]
    regions = [getattr(Regions, region) for region in regions]
    return list(set(regions) - set(REGIONS_WITHOUT_STOCKS))


def gen_params():
    regions = get_regions()
    params = [dict(cleanvars=1, ab_flags='zen_informer_down', geo=region) for region in regions]
    return params


@allure.feature('function_tests_stable')
@allure.feature('morda', 'stocks')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
@pytest.mark.parametrize('params', gen_params())
def test_stocks_contract(params):
    params = {'params': params}
    client = MordaClient(morda=DesktopMain(region=Regions.MOSCOW))
    url = client.make_url('{}')
    response = client.request(url=url, **params).send()
    assert response, 'Failed to get cleanvars'
    json = response.json()
    assert len(json) != 0, "Empty response"
    _test_json_match(json)


#Проверка на то, что возвращаются только Stocks, и Stocks соответствуют формату
def _test_json_match(json):
    assert json.get("Stocks") is not None, "Missed stocks"
    json = json["Stocks"]
    assert json.get("processed") is not None, "Missed processed"
    assert json.get("show") is not None, "Missed show"
    assert json.get("title") is not None, "Missed title"
    assert json.get("url") is not None, "Missed url"
    assert json.get("rows") is not None, "Missed rows"
    for items in json['rows']:
        _test_rows_match(items)


def _test_rows_match(row):
    assert _test_rows_format_with_graph(row) or _test_rows_format_buy_sale(row), "Rows wrong format"


#Формат 1 (с графиком и без графика)
def _test_rows_format_with_graph(row):
    return all([sum( list(map(int, [row.get('title') is not None, 
                row.get('subtitle') is not None, 
                row.get('value') is not None,
                row.get('delta') is not None,
                row.get('is_today') is not None,
                row.get('url') is not None,
                row.get('chart_icon') is not None]))) == len(row),
                row.get('title') is not None,
                row.get('value') is not None,
                row.get('url') is not None])


#Формат 2 (без графика, покупка/продажа)
def _test_rows_format_buy_sale(row):
    return all([sum( list(map(int, [row.get('title') is not None, 
                row.get('subtitle1') is not None, 
                row.get('value1') is not None,
                row.get('subtitle2') is not None, 
                row.get('value2') is not None,
                row.get('delta') is not None,
                row.get('is_today') is not None,
                row.get('url') is not None]))) == len(row),
                row.get('title') is not None,
                row.get('value1') is not None,
                row.get('value2') is not None,
                row.get('url') is not None])
