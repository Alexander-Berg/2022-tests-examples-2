# -*- coding: utf-8 -*-

import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi.internal.order_kit import positions_handler


@pytest.mark.filldb()
@pytest.mark.parametrize('order_id,expected', [
    # Incomplete order
    ('order_1', None,),

    # Original destination is real
    (
        'order_good_dest',
        {
            'geopoint': [37.71707, 55.605714],
            'locality': u'Москва'
        },
    ),

    # Original destination has changed
    (
        'order_wrong_dest',
        {
            'geopoint': [37.71813, 55.605902],
        },
    ),

    # No original destination
    (
        'order_no_dest',
        {
            'geopoint': [37.71813, 55.605902],
        },
    ),

    # No positions were stored (partner's bug, forgive for now)
    (
        'order_no_pos',
        {
            'geopoint': [37.71707, 55.605714],
            'locality': u'Москва'
        },
    ),

    # Unknown destination
    ('order_nothing_at_all', None,),
])
@pytest.inline_callbacks
def test_compute_real_destination(order_id, expected):
    order_proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    dest = yield positions_handler.compute_real_destination(order_proc)
    assert dest == expected


@pytest.mark.parametrize('order_id,expected', [
    # Incomplete order
    ('order_1', (None, None, None, None)),
    # Original destination is real. Dont use geocoder.
    (
        'order_22',
        (
            [37.71707, 55.605714], u'ул. Льва Толстого, 16',
            u'Россия, Москва, ул. Льва Толстого, 16', None
        ),
    ),
    # Original destination has changed. Using geocoder.
    (
        'order_wrong_dest',
        (
            [37.71813, 55.605902], 'Butyrskaya, 28',
            'Moskva, Butyrskaya, 28',
            ['ymapsbm1://geo?ll=37.71813%2C55.605902&text=%D0'],
        ),
    ),
    # Unknown destination
    ('order_nothing_at_all', (None, None, None, None)),
])
@pytest.inline_callbacks
def test_destinations_preparing(order_id, expected, patch):

    @patch('taxi.external.taxi_protocol.localize_geo_objects')
    @async.inline_callbacks
    def localize_geo_objects(orderid, locale, route_objects, log_extra=None):
        assert len(route_objects) == 1
        yield
        async.return_value({
            'addresses': [{
                'fullname': 'Moskva, Butyrskaya, 28',
                'short_text': 'Butyrskaya, 28',
                'geopoint': [37.71813, 55.605902],
                'uris': ['ymapsbm1://geo?ll=37.71813%2C55.605902&text=%D0']
            }]
        })

    order_proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    dest = yield positions_handler.get_destination_address(
        order_proc, locale='en',
    )
    assert dest == expected


@pytest.inline_callbacks
def test_destinations_preparing_broken_localizeaddress(patch):

    @patch('taxi.external.taxi_protocol.localize_geo_objects')
    @async.inline_callbacks
    def localize_geo_objects(orderid, locale, route_objects, log_extra=None):
        assert len(route_objects) == 1
        yield
        async.return_value({'addresses': []})

    order_proc = yield dbh.order_proc.Doc.find_one_by_id('order_wrong_dest')
    dest = yield positions_handler.get_destination_address(
        order_proc, locale='en',
    )
    assert dest == ([37.71813, 55.605902], None, None, None)
