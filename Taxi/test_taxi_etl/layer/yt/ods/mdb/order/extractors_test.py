# coding: utf-8
from unittest import TestCase
import mock

from taxi_etl.layer.yt.ods.mdb.order.extractors import \
    order_proc_driver_tech_search_duration_sec_extractor, \
    get_fixed_price_order_flg, SuccessOrderFlgExtractor, SurgeValueExtractor, \
    BurntOrderFlgExtractor, ExpiredOrderFlgExtractor, Source, OrderBrandExtractor, \
    TaxiStatusParser, CostBeforeAntisurgeExtractor
from test_taxi_etl.layer.yt.ods.mdb.order.utils import create_order_proc, \
    create_user_status_update, create_data_for_cost_before_antisurge


class TestExtractors(TestCase):
    def test_order_proc_driver_tech_search_duration_sec_extractor(self):
        data = create_order_proc(type_='urgent')

        result = order_proc_driver_tech_search_duration_sec_extractor(data,
                                                                      None)
        self.assertIsNone(result)

        data = create_order_proc(type_='soon')
        result = order_proc_driver_tech_search_duration_sec_extractor(data,
                                                                      None)
        self.assertIsNone(result)

        status_updates = [
            create_user_status_update('2018-06-10 23:23:23.123000', 'pending'),
            create_user_status_update('2018-06-10 23:23:24.125000', None)
        ]
        data = create_order_proc(type_='urgent', status_updates=status_updates)

        result = order_proc_driver_tech_search_duration_sec_extractor(data,
                                                                      None)
        self.assertIsNone(result)

        data = create_order_proc(type_='soon', status_updates=status_updates)
        result = order_proc_driver_tech_search_duration_sec_extractor(data,
                                                                      None)
        self.assertEqual(1.002, result)


def test_fixed_price_order_flg():
    assert get_fixed_price_order_flg(dict()) is False

    doc = create_order_proc(calc_method=None)
    assert get_fixed_price_order_flg(doc) is False

    doc = create_order_proc(calc_method='taximeter')
    assert get_fixed_price_order_flg(doc) is False

    doc = create_order_proc(calc_method='fixed')
    assert get_fixed_price_order_flg(doc) is True


def test_success_order_flg_extractor():
    extract = SuccessOrderFlgExtractor(Source.ORDER_PROC)

    doc = dict()
    assert extract(doc, None) is False

    doc = create_order_proc(status='finished')
    assert extract(doc, None) is False

    doc = create_order_proc(taxi_status='complete')
    assert extract(doc, None) is False

    doc = create_order_proc(status='finished', taxi_status='complete')
    assert extract(doc, None) is True


def test_expired_order_flg_extractor():
    extract = ExpiredOrderFlgExtractor(Source.ORDER_PROC)

    doc = dict()
    assert extract(doc, None) is False

    doc = create_order_proc(taxi_status='complete')
    assert extract(doc, None) is False

    doc = create_order_proc(taxi_status='expired')
    assert extract(doc, None) is True


def test_burnt_order_flg_extractor():
    extract = BurntOrderFlgExtractor(Source.ORDER_PROC)

    doc = dict()
    assert extract(doc, None) is False

    doc = create_order_proc(type_='soon')
    assert extract(doc, None) is True

    doc = create_order_proc(type_='soon', driver_uuid='abc', clid='111')
    assert extract(doc, None) is False

    doc = create_order_proc(type_='soon',
                            driver_uuid='abc',
                            clid='111',
                            status='abc')
    assert extract(doc, None) is False

    doc = create_order_proc(type_='soon',
                            driver_uuid='abc',
                            clid='111',
                            status='cancelled',
                            created='2018-01-01 00:00:00',
                            status_updated='2018-01-01 00:00:55')
    assert extract(doc, None) is False

    doc = create_order_proc(type_='soon',
                            status='cancelled',
                            created='2018-01-01 00:00:00',
                            status_updated='2018-01-01 00:00:55')
    assert extract(doc, None) is True

    doc = create_order_proc(type_='soon',
                            status='cancelled',
                            created='2018-01-01 00:00:00.111111',
                            status_updated='2018-01-01 00:00:50.111112')
    assert extract(doc, None) is True

    doc = create_order_proc(type_='soon',
                            status='cancelled',
                            created='2018-01-01 00:00:00',
                            status_updated='2018-01-01 00:00:30')
    assert extract(doc, None) is False


def test_surge_value_extractor():
    extract = SurgeValueExtractor(Source.ORDERS)

    assert 1 == extract(dict(), None)
    assert 1 == extract(dict(request=dict()), None)
    assert 1 == extract(dict(request=dict(sp=None)), None)
    assert 1 == extract(dict(request=dict(sp=0)), None)
    assert 1 == extract(dict(request=dict(sp=0.5)), None)
    assert 1 == extract(dict(request=dict(sp=1)), None)
    assert 1.5 == extract(dict(request=dict(sp=1.5)), None)


def test_get_distance_in_transporting():
    extract_data = TaxiStatusParser(Source.ORDER_PROC)

    status_updates = dict(l=1000, t='complete', tl=2000)
    assert extract_data.get_status_update_distance(status_updates) == 2

    status_updates['tl'] = None
    assert extract_data.get_status_update_distance(status_updates) == 1

    status_updates['t'] = 'pending'
    assert extract_data.get_status_update_distance(status_updates) == 1


class TestOrderBrandExtractor(TestCase):
    YANGO = 'yango'
    YANDEX = 'yandex'
    CORP_CABINET = 'corp_cabinet'
    UBER = 'uber'

    def setUp(self):
        self.extract_order_proc_brand = OrderBrandExtractor(Source.ORDER_PROC)
        self.extract_order_brand = OrderBrandExtractor(Source.ORDERS)

    def test_order_proc_before_dateX_in_Helsinke__ret_yango(self):
        order = {'order': {'city': u'Хельсинки', 'created': '2018-11-12'}}
        brand = self.extract_order_proc_brand(order, '_')
        self.assertEqual(self.YANGO, brand)

    def test_order_proc_before_dateX_in_Abidjan__ret_yango(self):
        order = {'order': {'city': u'Абиджан', 'created': '2018-11-12'}}
        brand = self.extract_order_proc_brand(order, '_')
        self.assertEqual(self.YANGO, brand)

    def test_order_proc_after_dateX_in_Helsinke_wo_app__ret_not_yango(self):
        order = {'order': {'city': u'Хельсинки', 'created': '2018-11-14', 'application': None}}
        brand = self.extract_order_proc_brand(order, '_')
        self.assertNotEqual(self.YANGO, brand)

    def test_order_proc_equal_dateX_w_app_yango__ret_yango(self):
        order = {'order': {'created': '2018-11-13', 'application': 'yango_...'}}
        brand = self.extract_order_proc_brand(order, '_')
        self.assertEqual(self.YANGO, brand)

    def test_order_equal_dateX_w_app_yango__ret_yango(self):
        order = {'created': '2018-11-13', 'statistics': {'application': 'yango_...'}}
        brand = self.extract_order_brand(order, '_')
        self.assertEqual(self.YANGO, brand)

    @mock.patch('taxi_etl.layer.yt.ods.mdb.order.extractors_impl.OrderSourceExtractor.__call__', lambda *a: 'yandex')
    def test_order_w_order_source_yandex__ret_yandex(self):
        brand = self.extract_order_brand({}, '_')
        self.assertEqual(self.YANDEX, brand)

    @mock.patch('taxi_etl.layer.yt.ods.mdb.order.extractors_impl.OrderSourceExtractor.__call__', lambda *a: 'corp_cabinet')
    def test_order_w_order_source_corp_cabinet__ret_yandex(self):
        brand = self.extract_order_brand({}, '_')
        self.assertEqual(self.YANDEX, brand)

    @mock.patch('taxi_etl.layer.yt.ods.mdb.order.extractors_impl.OrderSourceExtractor.__call__', lambda *a: 'uber_old')
    def test_order_w_order_source_uber__ret_uber(self):
        brand = self.extract_order_brand({}, '_')
        self.assertEqual(brand, self.UBER)

    @mock.patch('taxi_etl.layer.yt.ods.mdb.order.extractors_impl.OrderSourceExtractor.__call__', lambda *a: 'new_unknown_source')
    def test_order_w_order_source_unknown__ret_None(self):
        brand = self.extract_order_proc_brand({}, '_')
        self.assertIsNone(brand)


def test_cost_before_antisurge():
    extract = CostBeforeAntisurgeExtractor(Source.ORDERS)
    created = '2016-01-01 22:00:12'
    doc = create_data_for_cost_before_antisurge(created=created)
    assert extract(doc, None) is None

    calc = dict()
    doc = create_data_for_cost_before_antisurge(created=created, calc=calc)
    assert extract(doc, None) is None

    calc = dict(alternative_type='not_explicit_antisurge')
    doc = create_data_for_cost_before_antisurge(created=created, calc=calc)
    assert extract(doc, None) is None

    created = '2019-01-01 22:00:12'
    calc = dict(alternative_type='explicit_antisurge')
    doc = create_data_for_cost_before_antisurge(created=created, calc=calc)
    assert extract(doc, None) is None

    allowed_tariffs = {
        "__park__": {
            "business": 3,
            "child_tariff": 2,
            "econom": 1,
        }
    }

    calc['allowed_tariffs'] = allowed_tariffs

    doc = create_data_for_cost_before_antisurge(created=created, calc=calc)
    assert extract(doc, None) is None

    driver_tariff = 'econom'
    doc = create_data_for_cost_before_antisurge(created=created, calc=calc, driver_tariff=driver_tariff)
    assert extract(doc, None) == 1

    driver_tariff = 'undefined'
    doc = create_data_for_cost_before_antisurge(created=created, calc=calc, driver_tariff=driver_tariff)
    assert extract(doc, None) is None

    request_class = ['undefined']
    doc = create_data_for_cost_before_antisurge(created=created, calc=calc, request_class=request_class)
    assert extract(doc, None) is None

    request_class = ['business']
    doc = create_data_for_cost_before_antisurge(created=created, calc=calc, request_class=request_class)
    assert extract(doc, None) == 3

    request_class = ['business']
    driver_tariff = 'econom'
    doc = create_data_for_cost_before_antisurge(
        created=created, calc=calc, request_class=request_class, driver_tariff=driver_tariff
    )
    assert extract(doc, None) == 1
