# coding: utf-8
from taxi_etl.layer.yt.ods.mdb.common.impl import (
    get_order_brand,
    get_order_request_class,
    get_order_tariff_class,
    get_order_source,
    get_burnt_order_flg,
    get_distance_length,
)


def test_get_order_request_class():
    assert get_order_request_class(['vip']) == ['vip']
    assert get_order_request_class(['vip', 'econom']) == ['vip', 'econom']
    assert get_order_request_class([]) == []
    assert get_order_request_class(['']) == ['']
    assert get_order_request_class([None]) == [None]
    assert get_order_request_class(None) == []


def test_get_order_tariff_class():
    assert get_order_tariff_class('vip', ['econom', 'business']) == 'vip'
    assert get_order_tariff_class('', ['econom', 'business']) == ''
    assert get_order_tariff_class(None, ['econom', 'business']) == 'econom'
    assert get_order_tariff_class(None, ['']) == ''
    assert get_order_tariff_class(None, []) is None
    assert get_order_tariff_class(None, [None, 'business']) is None
    assert get_order_tariff_class(None, [None]) is None
    assert get_order_tariff_class(None, None) is None


def test_get_order_source():
    assert get_order_source('2018-01-01', 'uber', 'vip') == 'uber'
    assert get_order_source('2018-01-01', None, 'vip') == 'yandex'
    assert get_order_source('2018-01-01', 'yaber', 'vip') == 'yaber'
    assert get_order_source('2018-03-03', 'yaber', 'ubervip') == 'uber'
    assert get_order_source('2018-03-03', None, 'ubervip') == 'uber'
    assert get_order_source('2018-03-03', None, 'vip') == 'yandex'
    assert get_order_source('2018-03-03', None, None) == 'yandex'


def test_get_order_brand():
    assert get_order_brand('2018-11-05', 'iphone', u'Хельсинки', 'yandex') == 'yango'
    assert get_order_brand('2018-11-05', 'iphone', u'Москва', 'yandex') == 'yandex'
    assert get_order_brand('2018-11-05', 'yango', u'Москва', 'yandex') == 'yango'
    assert get_order_brand('2018-11-05', 'iphone', u'', 'yandex') == 'yandex'
    assert get_order_brand('2018-11-05', 'iphone', None, 'uber') == 'uber'
    assert get_order_brand('2018-12-15', 'iphone', u'Москва', 'yandex') == 'yandex'
    assert get_order_brand('2018-12-15', 'yango', u'Москва', 'yandex') == 'yango'
    assert get_order_brand('2018-12-15', 'iphone', u'Москва', 'uber') == 'uber'
    assert get_order_brand('2018-12-15', 'iphone', u'Москва', 'unexpected_brand') is None
    assert get_order_brand('2018-12-15', 'turboapp', 'any', 'any') == 'yandex'
    assert get_order_brand('2018-12-15', 'cargo', 'any', 'any') == 'yandex'
    assert get_order_brand('2020-02-01', 'vezetmini_call_center', 'any', 'call_center') == 'vezet'
    assert get_order_brand('2020-02-01', 'vezet_call_center', 'any', 'call_center') == 'vezet'
    assert get_order_brand('2020-02-01', 'saturn_call_center', 'any', 'call_center') == 'saturn'
    assert get_order_brand('2020-02-01', 'redtaxi_call_center', 'any', 'call_center') == 'redtaxi'


def call_get_burnt_order_flg(order_type=None, driver_id=None, status=None,
                             status_updated_dttm=None, utc_order_created_dttm=None):
    return get_burnt_order_flg(order_type, driver_id, status, status_updated_dttm, utc_order_created_dttm)


def test_get_burnt_order_flg():
    assert call_get_burnt_order_flg(order_type='soon', driver_id='123_456') == False
    assert call_get_burnt_order_flg(order_type='soon') == True
    assert call_get_burnt_order_flg(order_type='not so soon', driver_id='123_456') == False
    assert call_get_burnt_order_flg(order_type='not so soon') == False
    assert call_get_burnt_order_flg(order_type='soon', status='done') == True
    assert call_get_burnt_order_flg(order_type='soon', status='cancelled',
                                    utc_order_created_dttm='2019-07-01 00:00:00',
                                    status_updated_dttm='2019-07-01 00:00:10') == False
    assert call_get_burnt_order_flg(order_type='soon', status='cancelled',
                                    utc_order_created_dttm='2019-07-01 00:00:00',
                                    status_updated_dttm='2019-07-01 00:01:00') == True


def test_get_distance_length():
    assert get_distance_length(status='complete', distance_length=None, total_distance_length=None) is None
    assert get_distance_length(status='complete', distance_length=1, total_distance_length=2) == 2
    assert get_distance_length(status='complete', distance_length=1, total_distance_length=None) == 1
    assert get_distance_length(status='pending', distance_length=1, total_distance_length=2) == 1
