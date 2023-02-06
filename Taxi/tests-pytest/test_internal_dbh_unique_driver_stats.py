# coding: utf-8

import datetime

import pytest

from taxi.internal import dbh
from taxi.core import db


@pytest.mark.filldb()
@pytest.mark.parametrize(
    ('unique_driver_id,'
     'midnight_datetime,'
     'order_id,'
     'brandings,'
     'tariff_class,'
     'city_id,'
     'geoareas,'
     'expected_num_orders,'
     'expected_num_sticker_orders,'
     'expected_num_full_branding_orders,'
     'expected_shallow_order_list,'), [
        # freshly inserted unique_driver_stat doc
        ('some_unique_driver_id',
         datetime.datetime(2016, 5, 16),
         'some_order_id',
         [],
         'econom',
         'Moscow',
         ['moscow', 'msk'],
         1,
         0,
         0,
         [
             {
                 'due': datetime.datetime(2016, 5, 16),
                 'order_id': 'some_order_id',
                 'geoareas': ['moscow', 'msk']
             },
         ],
         ),
        # inc in existing unique_driver_stat doc
        ('unique_driver_id_with_2_orders_in_moscow_econom',
         datetime.datetime(2016, 5, 16),
         'some_order_id',
         [],
         'econom',
         'Moscow',
         ['moscow'],
         3,
         0,
         0,
         [
             {
                 'due': datetime.datetime(2016, 5, 16),
                 'order_id': 'some_order_id',
                 'geoareas': ['moscow']
             },
         ],
         ),
        # inc in new unique_driver_stat doc
        ('unique_driver_id_with_2_orders_in_moscow_econom',
         datetime.datetime(2016, 5, 16),
         'some_order_id',
         [],
         'vip',
         'Moscow',
         ['moscow'],
         1,
         0,
         0,
         [
             {
                 'due': datetime.datetime(2016, 5, 16),
                 'order_id': 'some_order_id',
                 'geoareas': ['moscow']
             },
         ],
         ),
        # don't inc, because some_counted_order_id is already in orders
        ('unique_driver_id_with_1_orders_in_moscow_express',
         datetime.datetime(2016, 5, 16),
         'some_counted_order_id',
         [],
         'express',
         'Moscow',
         ['moscow'],
         1,
         0,
         0,
         [],
         ),
        #
        ('some_unique_driver_id',
         datetime.datetime(2016, 5, 16),
         'some_branded_order_id',
         ['full_branding', 'lightbox', 'sticker'],
         'express',
         'Moscow',
         None,
         1,
         1,
         1,
         [
             {
                 'due': datetime.datetime(2016, 5, 16),
                 'order_id': 'some_branded_order_id',
                 'has_lightbox': True,
                 'has_sticker': True,
             },
         ],
         ),
        ('with_shallow_order_list',
         datetime.datetime(2016, 5, 16),
         'some_branded_order_id',
         ['full_branding', 'lightbox', 'sticker'],
         'express',
         'Moscow',
         ['moscow'],
         2,
         1,
         1,
         [
             {
                 'due': datetime.datetime(2016, 5, 16, 3),
                 'order_id': 'id1',
                 'geoareas': ['moscow']
             },
             {
                 'due': datetime.datetime(2016, 5, 16),
                 'order_id': 'some_branded_order_id',
                 'has_lightbox': True,
                 'has_sticker': True,
                 'geoareas': ['moscow']
             },
         ],
         ),
    ])
@pytest.inline_callbacks
def test_count_order(
        unique_driver_id, midnight_datetime, order_id, brandings,
        tariff_class, city_id, geoareas, expected_num_orders,
        expected_num_sticker_orders, expected_num_full_branding_orders,
        expected_shallow_order_list):
    @pytest.inline_callbacks
    def _make_order_in_db():
        order = dbh.orders.Doc()
        order._id = order_id
        order.performer.tariff.cls = tariff_class
        order.request.due = midnight_datetime
        order.nearest_zone = city_id
        if 'lightbox' in brandings:
            order.performer.has_lightbox = True
        if 'sticker' in brandings:
            order.performer.has_sticker = True
        if geoareas:
            order.geoareas = geoareas
        yield db.orders.insert(order)
    yield _make_order_in_db()
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    proc = dbh.order_proc.Doc(_id=order.pk, order=order)

    unique_driver = dbh.unique_drivers.Doc()
    unique_driver._id = unique_driver_id

    yield dbh.unique_driver_zone_stats.Doc.count_order(
        proc=proc,
        brandings=brandings,
        unique_driver=unique_driver,
        midnight_datetime=midnight_datetime,
    )
    query = {
        dbh.unique_driver_zone_stats.Doc.unique_driver_id: unique_driver_id,
        dbh.unique_driver_zone_stats.Doc.midnight_datetime: midnight_datetime,
        dbh.unique_driver_zone_stats.Doc.tariff_class: tariff_class,
        dbh.unique_driver_zone_stats.Doc.area_id: city_id,
    }
    unique_driver_stat = yield dbh.unique_driver_zone_stats.Doc.find_one_or_not_found(
        query
    )
    assert unique_driver_stat.num_orders == expected_num_orders
    assert (unique_driver_stat.num_sticker_orders or 0) == expected_num_sticker_orders
    assert (unique_driver_stat.num_full_branding_orders or 0) == expected_num_full_branding_orders
    assert unique_driver_stat.shallow_order_list == expected_shallow_order_list
