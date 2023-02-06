# coding: utf-8
from __future__ import unicode_literals

from datetime import datetime

import pytest

from taxi.util import dates
from taxi_maintenance.stuff.deptrans_report import OrdersMapper
from taxi_maintenance.stuff.deptrans_report import Reducer
from taxi.internal import dbh


def _cast_format(value):
    new_value = {}
    for key, subvalue in value.items():
        new_value[key] = dict(subvalue)
    for type, points in new_value['total_points'].items():
        new_value['total_points'][type] = list(points)
    return new_value


@pytest.mark.parametrize('input_row,output_row', [
    ({
        'calc_distance': 2.5,
        'nearest_zone': 'moscow',
        'created_order': dates.timestamp_us(datetime(2017, 8, 1)),
        'id': 1,
        'request_destinations': [{'geopoint': [55.72, 37.58]}],
        'request_due': dates.timestamp_us(datetime(2017, 8, 1, 0, 5)),
        'request_source': {'geopoint': [55.73, 37.59]},
        'statistics': {'travel_time': 600.0},
        'taxi_status': dbh.orders.TAXI_STATUS_COMPLETE,
    },
    {
        'travel_time': 600.0,
        'calc_distance': 2.5,
        'source_point': [55.73, 37.59],
        'destination_point': [55.72, 37.58],
        'request_due': dates.timestamp_us(datetime(2017, 8, 1, 0, 5)),
        'fake_to_reduce_by': 0,
    }),
    ({
        'id': 2,
        'nearest_zone': 'tumen',
        'created_order': dates.timestamp_us(datetime(2017, 8, 1, 0, 1)),
        'taxi_status': dbh.orders.TAXI_STATUS_COMPLETE,
    }, None),
    ({
        'id': 3,
        'nearest_zone': 'moscow',
        'created_order': dates.timestamp_us(datetime(2017, 8, 5)),
        'taxi_status': dbh.orders.TAXI_STATUS_COMPLETE,
    }, None),
    ({
        'id': 4,
        'calc_distance': 4.2,
        'nearest_zone': 'moscow',
        'created_order': dates.timestamp_us(datetime(2017, 8, 4, 23, 59, 59)),
        'request_destinations': [
            {'geopoint': [55.58, 37.67]},
            {'geopoint': [55.98, 37.43]},
        ],
        'request_due': dates.timestamp_us(datetime(2017, 8, 5)),
        'request_source': {'geopoint': [55.89, 37.54]},
        'statistics': {},
        'taxi_status': dbh.orders.TAXI_STATUS_COMPLETE,
    },
    {
        'travel_time': None,
        'calc_distance': 4.2,
        'source_point': [55.89, 37.54],
        'destination_point': [55.58, 37.67],
        'request_due': dates.timestamp_us(datetime(2017, 8, 5)),
        'fake_to_reduce_by': 0,
    }),
    ({
        'id': 5,
        'nearest_zone': 'moscow',
        'created_order': dates.timestamp_us(datetime(2017, 8, 1, 0, 1)),
        'taxi_status': dbh.orders.TAXI_STATUS_ACCEPT,
    }, None)
])
@pytest.mark.filldb(_fill=False)
def test_orders_mapper(input_row, output_row):
    from_date = dates.timestamp_us(datetime(2017, 8, 1))
    to_date = dates.timestamp_us(datetime(2017, 8, 5))
    mapper = OrdersMapper(from_date, to_date)
    yielded = list(mapper(input_row))
    if output_row is None:
        assert len(yielded) == 0
    else:
        assert len(yielded) == 1
        assert yielded[0] == output_row


@pytest.mark.parametrize('input_rows,output_expected', [
    ([
        {
            'travel_time': 600.0,
            'calc_distance': 3.2,
            'source_point': [55.3, 24.5],
            'destination_point': [34.6, 75.2],
            'request_due': dates.timestamp_us(datetime(2017, 8, 1, 10, 0)),
            'fake_to_reduce_by': 0,
        },
        {
            'travel_time': 800.0,
            'calc_distance': 7.2,
            'source_point': [51.3, 38.5],
            'destination_point': [76.6, 43.2],
            'request_due': dates.timestamp_us(datetime(2017, 8, 1, 23, 0)),
            'fake_to_reduce_by': 0,
        },
        {
            'travel_time': 1000.0,
            'calc_distance': 15.2,
            'source_point': [51.9, 38.9],
            'destination_point': [71.6, 47.2],
            'request_due': dates.timestamp_us(datetime(2017, 8, 5, 10, 0)),
            'fake_to_reduce_by': 0,
        },
    ],
    {
         'total_stats': {
             'travel_time': {
                 'count': 3,
                 'sum': 2400.0,
             },
             'distance': {
                 'count': 3,
                 'sum': 25.6,
             },
         },
         'total_points': {
             'day_from': [(24.5, 55.3)],
             'day_to': [(75.2, 34.6)],
             'night_from': [(38.5, 51.3), (38.9, 51.9)],
             'night_to': [(43.2, 76.6), (47.2, 71.6)],
         },
    })
])
@pytest.mark.filldb(_fill=False)
def test_reducer(input_rows, output_expected):
    reducer = Reducer()
    reduce_key = {'fake_to_reduce_by': 0}
    output_rows = list(reducer(reduce_key, input_rows))
    assert len(output_rows) == 1
    assert _cast_format(output_rows[0]) == output_expected
