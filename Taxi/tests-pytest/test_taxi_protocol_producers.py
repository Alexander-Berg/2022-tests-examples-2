# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import re

from lxml import etree

import pytest

from taxi import config
from taxi.core import async
from taxi.internal import dbh
from taxi.internal.city_kit import country_manager
from taxi.internal.order_kit import order_helpers
from taxi.internal.order_kit import pool
from taxi.taxi_protocol.protocol_1x import producers
import helpers


def test_updaterequest():
    to_send = order_helpers.make_updaterequest_notification(
        warn_no_card=False,
        wait_payment_complete=True,
        paid_by_card=False,
        version=1,
    )
    order_data = {
        'performer': {
            'clid': 'some_clid',
            'taxi_alias': {
                'id': 'some_taxi_alias_id'
            }

        },
        'request': {
            'payment': {
                'type': dbh.orders.PAYMENT_TYPE_CASH
            }
        }
    }
    order_proc = dbh.order_proc.Doc(
        candidates=[{
            dbh.order_proc.Doc.candidates.acceptance_rate.key: 0.9,
            dbh.order_proc.Doc.candidates.completed_rate.key: 0.9,
            dbh.order_proc.Doc.candidates.alias_id.key: 0,
        }],
        aliases=[
            {'id': 0, 'due': datetime.datetime.utcnow()}
        ]
    )
    order_proc.performer.candidate_index = -1
    order_proc.order = dbh.orders.Doc(order_data)
    updaterequest_body = producers.build_updaterequest(
        order_proc, to_send, 'cash')
    parsed = etree.fromstring(updaterequest_body)
    assert parsed.xpath('//Requirements/Require/text()')[0] == 'no'
    assert len(parsed.xpath('//Change/Id/text()')) == 1
    assert parsed.xpath('//Change/Type/text()')[0] == 'payment'
    assert parsed.xpath('//Change/Version/text()')[0] == '1'


BUILD_TARIFF_DECOUPLING_DATA = {
    'user_price_info': {
        'category_id': 'corp:c_id',
        'tariff_id': 'abc-def-ghi',
    },
    'driver_price_info': {
        'category_id': 'c_id',
        'tariff_id': 'jkl-mno-pqr',
    },
}
BUILD_TARIFF_CASE_SET_1 = [param.replace((None, None,) + param.values) for param in [
    helpers.Param(
        None, None, None, None, True, 'time-dist', None, None, True, {},
        'c_id',
        'c_id',
        id='no surge: simple tariff id'
    ),
    helpers.Param(
        1.0, None, None, None, True, 'time-dist', None, None, True, {},
        'c_id',
        'c_id',
        id='identity surge: simple tariff id'
    ),
    helpers.Param(
        2.0, None, None, None, True, 'time-dist', None, None, True, {},
        'surge--c_id--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        'surge--c_id--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        id='surge: modifiers tariff id'
    ),
    helpers.Param(
        2.0, None, None, None, False, 'time-dist', None, None, True, {},
        'c_id',
        'c_id',
        id='not synchronizable tariff: simple tariff id'
    ),
    helpers.Param(
        0.5, None, None, None, True, 'time-dist', None, None, True, {},
        'surge--c_id--minimal_1.0-distance_0.5-time_0.5-hidden_0',
        'surge--c_id--minimal_1.0-distance_0.5-time_0.5-hidden_0',
        id='case 1'
    ),
    helpers.Param(
        0.5, None, None, None, True, 'full', None, None, True, {},
        'surge--c_id--minimal_0.5-distance_0.5-time_0.5-hidden_0',
        'surge--c_id--minimal_0.5-distance_0.5-time_0.5-hidden_0',
        id='case 2'
    ),
    helpers.Param(
        0.5, None, None, None, True, 'time-dist', None, None, False, {},
        'c_id',
        'c_id',
        id='case 3'
    ),
    helpers.Param(
        0.5, None, None, None, True, 'full', None, None, False, {},
        'c_id',
        'c_id',
        id='case 4'
    ),
    helpers.Param(
        0.5, 2.0, None, None, True, 'full', None, None, False, {},
        'c_id',
        'c_id',
        id='case 5'
    ),
    helpers.Param(
        0.5, 1.5, 0.25, None, True, 'full', None, None, False, {},
        'c_id',
        'c_id',
        id='case 6'
    ),
    helpers.Param(
        0.4, 2.0, None, None, True, 'full', None, None, False, {},
        'c_id',
        'c_id',
        id='case 7'
    ),
    helpers.Param(
        0.4, 1.5, 0.25, None, True, 'full', None, None, False, {},
        'c_id',
        'c_id',
        id='case 8'
    ),
    helpers.Param(
        0.4, 2.0, None, None, True, 'full', None, None, True, {},
        'surge--c_id--minimal_0.8-distance_0.8-time_0.8-hidden_0',
        'surge--c_id--minimal_0.8-distance_0.8-time_0.8-hidden_0',
        id='case 9'
    ),
    helpers.Param(
        0.4, 1.5, 0.25, None, True, 'full', None, None, True, {},
        'surge--c_id--minimal_0.85-distance_0.85-time_0.85-hidden_0',
        'surge--c_id--minimal_0.85-distance_0.85-time_0.85-hidden_0',
        id='case 10'
    ),
    helpers.Param(
        0.6, 1.5, 0.25, None, True, 'full', None, None, False, {},
        'surge--c_id--minimal_1.15-distance_1.15-time_1.15-hidden_0',
        'surge--c_id--minimal_1.15-distance_1.15-time_1.15-hidden_0',
        id='case 11'
    ),
    helpers.Param(
        2.0, None, None, None, True, 'time-dist', None, None, True, {},
        'surge--c_id--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        'surge--c_id--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        id='case 12'
    ),
    helpers.Param(
        2.0, None, None, None, True, 'full', None, None, True, {},
        'surge--c_id--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        'surge--c_id--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        id='case 13'
    ),
    helpers.Param(
        1.0, 0.0, 1.0, 100.0, True, 'time-dist', None, None, True, {},
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-surcharge_100.0',
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-surcharge_100.0',
        id='case 14'
    ),
    helpers.Param(
        2.0, 0.7, 0.3, 100.0, True, 'time-dist', None, None, True, {},
        'surge--c_id--minimal_1.7-distance_1.7-time_1.7-hidden_0-surcharge_30.0',
        'surge--c_id--minimal_1.7-distance_1.7-time_1.7-hidden_0-surcharge_30.0',
        id='surge: modifiers tariff id'
    ),
    helpers.Param(
        0.5, 0.8, 0.2, 100.0, True, 'time-dist', None, None, False, {},
        'c_id',
        'c_id',
        id='case 15'
    ),
    helpers.Param(
        0.5, 0.8, 0.2, 100.0, True, 'full', None, None, False, {},
        'c_id',
        'c_id',
        id='case 16'
    ),
    helpers.Param(
        0.5, 0.8, 0.2, 100.0, True, 'time-dist', None, None, True, {},
        'surge--c_id--minimal_1.0-distance_0.6-time_0.6-hidden_0',
        'surge--c_id--minimal_1.0-distance_0.6-time_0.6-hidden_0',
        id='case 17'
    ),
    helpers.Param(
        0.5, 0.8, 0.2, 100.0, True, 'full', None, None, True, {},
        'surge--c_id--minimal_0.6-distance_0.6-time_0.6-hidden_0-surcharge_20.0',
        'surge--c_id--minimal_0.6-distance_0.6-time_0.6-hidden_0-surcharge_20.0',
        id='case 18'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', None, None, True, {},
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='case 19'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', None, None, True, {},
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='case 20'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2, None, True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='case 21'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2, None, True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='case 22'
    ),
    helpers.Param(
        None, None, None, None, True, 'time-dist', None,
        [('ya_plus', 0.9, False)], True, {},
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        id='no surge + ya_plus'
    ),
    helpers.Param(
        None, None, None, None, True, 'time-dist', None,
        [('ya_plus', 0.9, False)], True, {},
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        id='case 23'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2, [('ya_plus', 0.9, False)],
        True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_0.9',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        id='surge + discount + ya_plus'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2,
        [('personal_wallet', 0.9, False)], True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_0.9',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        id='surge + discount + personal_wallet'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2,
        [('ya_plus', 0.9, False), ('personal_wallet', 0.9, False)],
        True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_0.81',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.81',
        id='surge + discount + ya_plus + personal_wallet'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2,
        [('ya_plus', 0.9, True), ('personal_wallet', 0.9, False)],
        True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_0.81',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        id='surge + discount + ya_plus(paid) + personal_wallet(unpaid)'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2,
        [('ya_plus', 0.9, True), ('personal_wallet', 0.9, True)],
        True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_0.81',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='surge + discount + ya_plus(paid) + personal_wallet(paid)'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2,
        [('call_center', 1.1, True)], True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_1.1',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_1.1',
        id='surge + discount + call_center'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2,
        [('call_center', 1.1, False)], True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_1.1',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_1.1',
        id='surge + discount + call_center'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2, [('ya_plus', 0.9, True)],
        True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_0.9',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='case 24'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2,
        [('ya_plus', 0.9, False),
         ('personal_wallet', 0.9, False),
         ('call_center', 1.1, True),
         ('requirements', 1.3, False)], True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_1.1583',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_1.1583',
        id='decoupling surge + discount + call_center + requirements + discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'full', 0.2,
        [('ya_plus', 0.9, False),
         ('personal_wallet', 0.9, False),
         ('call_center', 1.1, True),
         ('requirements', 0.9, False)], True, {},
        'surge--c_id--minimal_1.28-distance_1.28-time_1.28-hidden_0-surcharge_32.0-multiplier_0.8019',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.8019',
        id='decoupling surge + discount + call_center + requirements + discount_val no effect'
    ),
]]
BUILD_TARIFF_CASE_SET_2 = [param.replace((None, BUILD_TARIFF_DECOUPLING_DATA,) + param.values) for param in [
    helpers.Param(
        None, None, None, None, True, 'time-dist', None, None, True, {},
        'corp:c_id:abc-def-ghi',
        'c_id',
        id='decoupling no surge: simple tariff id'
    ),
    helpers.Param(
        1.0, None, None, None, True, 'time-dist', None, None, True, {},
        'corp:c_id:abc-def-ghi',
        'c_id',
        id='decoupling identity surge: simple tariff id'
    ),
    helpers.Param(
        2.0, None, None, None, True, 'time-dist', None, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        'surge--c_id--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        id='decoupling surge: modifiers tariff id'
    ),
    helpers.Param(
        2.0, None, None, None, False, 'time-dist', None, None, True, {},
        'corp:c_id:abc-def-ghi',
        'surge--c_id--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        id='decoupling not synchronizable tariff: simple tariff id'
    ),
    helpers.Param(
        0.5, None, None, None, True, 'time-dist', None, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.0-distance_0.5-time_0.5-hidden_0',
        'surge--c_id--minimal_1.0-distance_0.5-time_0.5-hidden_0',
        id='decoupling case 1'
    ),
    helpers.Param(
        0.5, None, None, None, True, 'time-dist', None, None, False, {},
        'corp:c_id:abc-def-ghi',
        'c_id',
        id='decoupling case 3'
    ),
    helpers.Param(
        0.5, 2.0, None, None, True, 'time-dist', None, None, False, {},
        'corp:c_id:abc-def-ghi',
        'c_id',
        id='decoupling case 5'
    ),
    helpers.Param(
        0.5, 1.5, 0.25, None, True, 'time-dist', None, None, False, {},
        'corp:c_id:abc-def-ghi',
        'c_id',
        id='decoupling case 6'
    ),
    helpers.Param(
        0.4, 2.0, None, None, True, 'time-dist', None, None, False, {},
        'corp:c_id:abc-def-ghi',
        'c_id',
        id='decoupling case 7'
    ),
    helpers.Param(
        0.4, 1.5, 0.25, None, True, 'time-dist', None, None, False, {},
        'corp:c_id:abc-def-ghi',
        'c_id',
        id='decoupling case 8'
    ),
    helpers.Param(
        0.4, 2.0, None, None, True, 'time-dist', None, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.0-distance_0.8-time_0.8-hidden_0',
        'surge--c_id--minimal_1.0-distance_0.8-time_0.8-hidden_0',
        id='decoupling case 9'
    ),
    helpers.Param(
        0.4, 1.5, 0.25, None, True, 'time-dist', None, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.0-distance_0.85-time_0.85-hidden_0',
        'surge--c_id--minimal_1.0-distance_0.85-time_0.85-hidden_0',
        id='decoupling case 10'
    ),
    helpers.Param(
        0.6, 1.5, 0.25, None, True, 'time-dist', None, None, False, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.15-distance_1.15-time_1.15-hidden_0',
        'surge--c_id--minimal_1.15-distance_1.15-time_1.15-hidden_0',
        id='decoupling case 11'
    ),
    helpers.Param(
        2.0, None, None, None, True, 'time-dist', None, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        'surge--c_id--minimal_2.0-distance_2.0-time_2.0-hidden_0',
        id='decoupling case 12'
    ),
    helpers.Param(
        1.0, 0.0, 1.0, 100.0, True, 'time-dist', None, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.0-distance_1.0-time_1.0-hidden_0-surcharge_100.0',
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-surcharge_100.0',
        id='decoupling case 14'
    ),
    helpers.Param(
        2.0, 0.7, 0.3, 100.0, True, 'time-dist', None, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.7-distance_1.7-time_1.7-hidden_0-surcharge_30.0',
        'surge--c_id--minimal_1.7-distance_1.7-time_1.7-hidden_0-surcharge_30.0',
        id='decoupling surge: modifiers tariff id'
    ),
    helpers.Param(
        0.5, 0.8, 0.2, 100.0, True, 'time-dist', None, None, False, {},
        'corp:c_id:abc-def-ghi',
        'c_id',
        id='decoupling case 15'
    ),
    helpers.Param(
        0.5, 0.8, 0.2, 100.0, True, 'time-dist', None, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.0-distance_0.6-time_0.6-hidden_0',
        'surge--c_id--minimal_1.0-distance_0.6-time_0.6-hidden_0',
        id='decoupling case 17'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', None, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='decoupling case 19'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='decoupling case 21 discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2, None, True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='decoupling case 22 discount_val no effect'
    ),
    helpers.Param(
        None, None, None, None, True, 'time-dist', None,
        [('ya_plus', 0.9, False)], True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        id='decoupling no surge + ya_plus'
    ),
    helpers.Param(
        None, None, None, None, True, 'time-dist', None,
        [('requirements', 1.3, False)], True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_1.3',
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_1.3',
        id='decoupling no surge + requirements'
    ),
    helpers.Param(
        None, None, None, None, True, 'time-dist', None,
        [('requirements', 1.3, False)], True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_1.3',
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_1.3',
        id='decoupling no surge + requirements + driver tariff'
    ),
    helpers.Param(
        None, None, None, None, True, 'time-dist', None,
        [('ya_plus', 0.9, False)], True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        id='decoupling case 23'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2, [('ya_plus', 0.9, False)],
        True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        id='decoupling surge + discount + ya_plus discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2,
        [('personal_wallet', 0.9, False)], True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        id='decoupling surge + discount + personal_wallet discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2,
        [('ya_plus', 0.9, False), ('personal_wallet', 0.9, False)],
        True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.81',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.81',
        id='decoupling surge + discount + ya_plus + personal_wallet discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2,
        [('ya_plus', 0.9, True), ('personal_wallet', 0.9, False)],
        True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.81',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        id='decoupling surge + discount + ya_plus(paid) + personal_wallet(unpaid) discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2,
        [('ya_plus', 0.9, True), ('personal_wallet', 0.9, True)],
        True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.81',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='decoupling surge + discount + ya_plus(paid) + personal_wallet(paid) discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2,
        [('call_center', 1.1, True)], True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_1.1',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_1.1',
        id='decoupling surge + discount + call_center discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2,
        [('call_center', 1.1, False)], True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_1.1',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_1.1',
        id='decoupling surge + discount + call_center discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2, [('ya_plus', 0.9, True)],
        True, {},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='decoupling case 24 discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2, [('ya_plus', 0.9, True)],
        True, {'yellowcarnumber': True},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='decoupling case 24 discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2, [('ya_plus', 0.9, True)],
        True, {'hourly_rental': 1},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9'
        '-requirement_hourly_rental.1hours',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-requirement_hourly_rental.1hours',
        id='decoupling case 24 discount_val no effect'
    ),
    helpers.Param(
        2.0, 0.6, 0.4, 100.0, True, 'time-dist', 0.2, [('ya_plus', 0.9, True)],
        True, {'hourly_rental': 2},
        'surge--corp:c_id:abc-def-ghi--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0-multiplier_0.9',
        'surge--c_id--minimal_1.6-distance_1.6-time_1.6-hidden_0-surcharge_40.0',
        id='decoupling case 24 discount_val no effect'
    ),
]]

BUILD_TARIFF_CASE_SET_3 = [
    helpers.Param(
        None,
        {
            'user_price_info': {
                'category_id': 'corp:c_id',
                'tariff_id': 'abc-def-ghi',
                'surge_price': 1.0,
                'surcharge': None,
                'surcharge_alpha': None,
                'surcharge_beta': None,
            },
            'driver_price_info': {
                'category_id': 'c_id',
                'tariff_id': 'jkl-mno-pqr',
                'surge_price': 0.7,
                'surcharge': None,
                'surcharge_alpha': None,
                'surcharge_beta': None,
            },
        },
        None, None, None, None, True, 'time-dist', None, None, True, {},
        'corp:c_id:abc-def-ghi',
        'surge--c_id--minimal_1.0-distance_0.7-time_0.7-hidden_0',
        id='decoupling surge only for driver'
    ),
]

BUILD_TARIFF_CASE_SET_4 = [
    helpers.Param(
        {
            "cashback_calc_coeff": 0.11111111111111108,
            "cashback_tariff_multiplier": 0.9,
        },
        None,
        None, None, None, None, True, 'time-dist', None, None, True, {},
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        'surge--c_id--minimal_1.0-distance_1.0-time_1.0-hidden_0-multiplier_0.9',
        id='cashback for plus new pricing'
    ),
helpers.Param(
        {
            "cashback_rate": 0.1,
        },
        None,
        None, None, None, None, True, 'time-dist', None, None, True, {},
        'c_id',
        'c_id',
        id='no cashback for plus new pricing'
    ),
]


@pytest.mark.parametrize('order_doc,proc_doc,umbrella_proc_doc,'
                         'expected_value',
[
    (
        # Test 1.
        {
            'status': 'finished',
            'taxi_status': 'complete',
            'cost': 99.5,
            'driver_cost': {
                'cost': 110.56
            },
            'request': {
                'payment': {
                    'type': dbh.orders.PAYMENT_TYPE_CARD
                }
            },
            'performer': {
                'tariff': {
                    'class': 'econom'
                }
            },
            'payment_tech': {
                'type': 'card',
                'notifications': {
                    'payment': {
                        'to_send': {
                            'updated': datetime.datetime(2016, 9, 23, 22, 13),
                            'ride_sum': 99.5,
                            'tips_sum': 9.5,
                        }
                    }
                }
            },
            'price_modifiers': {
                'items': [
                    {
                        'type': 'multiplier',
                        'reason': 'ya_plus',
                        'value': 0.9,
                        'tariff_categories': ['econom']
                    }
                ]
            },
        },
        {
            'candidates': [
                {
                    'driver_id': 'parkid_driverid',
                    'alias_id': 'alias1',
                    'ci': 'c_id',
                }
            ],
            'aliases': [{'id': 'alias1'}],
            'performer': {
                'park_id': 'parkid',
                'uuid': 'driverid',
                'candidate_index': 0,
            }
        },
        {},
        # Subvention = 110.56 - 99.50 = 11.06
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Order>'
        '<Orderid>alias1</Orderid>'
        '<Cars><Car><Uuid>driverid</Uuid><Clid>parkid</Clid><DBId/></Car></Cars>'
        '<Payments>'
        '<Payment Currency="RUB" Sum="99.50" Type="ride" Time="2016-09-24T01:13:00+0300"/>'
        '<Payment Currency="RUB" Sum="9.50" Type="tips" Time="2016-09-24T01:13:00+0300"/>'
        '<Payment Currency="RUB" Sum="11.06" Type="subvention" Time="2016-09-24T01:13:00+0300"/>'
        '</Payments><PaymentMethod type="card"/>'
        '</Order>'
    ),
    (
        # Test 2.
        {
            'status': 'finished',
            'taxi_status': 'complete',
            'request': {
                'requirements': {},
                'payment': {
                    'type': dbh.orders.PAYMENT_TYPE_CASH
                }
            },
            'payment_tech': {
                'type': 'cash',
                'notifications': {
                    'payment': {
                        'to_send': {
                            'updated': datetime.datetime(2016, 9, 23, 22, 13),
                            'ride_sum': 99.5,
                            'tips_sum': 9.5,
                        }
                    }
                }
            }
        },
        {
            'candidates': [
                {
                    'driver_id': 'parkid_driverid',
                    'alias_id': 'alias2',
                }
            ],
            'aliases': [{'id': 'alias2'}],
            'performer': {
                'park_id': 'parkid',
                'uuid': 'driverid',
                'candidate_index': 0,
            }
        },
        {},
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Order>'
        '<Orderid>alias2</Orderid>'
        '<Cars><Car><Uuid>driverid</Uuid><Clid>parkid</Clid><DBId/></Car></Cars>'
        '<Payments>'
        '<Payment Currency="RUB" Sum="99.50" Type="ride" Time="2016-09-24T01:13:00+0300"/>'
        '<Payment Currency="RUB" Sum="9.50" Type="tips" Time="2016-09-24T01:13:00+0300"/>'
        '</Payments><PaymentMethod type="cash"/>'
        '</Order>'
    ),
    (
        # Test 3: with db_id set
        {
            'status': 'finished',
            'taxi_status': 'complete',
            'request': {
                'requirements': {},
                'payment': {
                    'type': dbh.orders.PAYMENT_TYPE_CASH
                }
            },
            'payment_tech': {
                'type': 'cash',
                'notifications': {
                    'payment': {
                        'to_send': {
                            'updated': datetime.datetime(2016, 9, 23, 22, 13),
                            'ride_sum': 99.5,
                            'tips_sum': 9.5,
                        }
                    }
                }
            }
        },
        {
            'candidates': [
                {
                    'driver_id': 'parkid_driverid',
                    'db_id': 'dbid',
                    'alias_id': 'alias3',
                }
            ],
            'aliases': [{'id': 'alias3'}],
            'performer': {
                'park_id': 'parkid',
                'uuid': 'driverid',
                'candidate_index': 0,
            }
        },
        {},
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Order>'
        '<Orderid>alias3</Orderid>'
        '<Cars><Car><Uuid>driverid</Uuid><Clid>parkid</Clid><DBId>dbid</DBId></Car></Cars>'
        '<Payments>'
        '<Payment Currency="RUB" Sum="99.50" Type="ride" Time="2016-09-24T01:13:00+0300"/>'
        '<Payment Currency="RUB" Sum="9.50" Type="tips" Time="2016-09-24T01:13:00+0300"/>'
        '</Payments><PaymentMethod type="cash"/>'
        '</Order>'
    ),
    (
        # Test 4. test inverting payment logic for umbrella orders.
        {   # order_doc
            'status': 'finished',
            'taxi_status': 'complete',
            'request': {
                'payment': {
                    'type': dbh.orders.PAYMENT_TYPE_CARD
                }
            },
            'performer': {
                'taxi_alias': {
                    'id': 'alias',
                },
            },
            'payment_tech': {
                'type': 'card',
                'notifications': {
                    'payment': {
                        'to_send': {
                            'updated': datetime.datetime(2016, 9, 23, 22, 13),
                            'ride_sum': 99.5,
                            'tips_sum': 9.5,
                        }
                    }
                }
            }
        },
        {   # proc_doc
            'candidates': [
                {
                },
                {
                    'driver_id': 'parkid_driverid',
                    'db_id': 'dbid',
                    'alias_id': 'alias',
                    dbh.order_proc.Doc.candidates.key: [
                        {
                            dbh.order_proc.Doc.candidates.pool.key: {
                                dbh.order_proc.Doc.candidates.pool.
                                    umbrella_order_id.key: 'umbr',
                            },
                        }
                    ]
                }
            ],
            'performer': {
                'park_id': 'parkid',
                'uuid': 'driverid',
                'candidate_index': 1,
            }
        },
        {   # umbrella_proc_doc
            '_id': 'umbr',
            'candidates': [
                {
                    'driver_id': 'parkid_driverid',
                    'db_id': 'dbid',
                    dbh.order_proc.Doc.candidates.alias_id.key: 'txals',
                }
            ],
            'performer': {
                'park_id': 'parkid',
                'uuid': 'driverid',
                'candidate_index': 0,
            }
        },
        """
        <?xml version="1.0" encoding="utf-8"?>
        <Order>
            <Orderid>alias</Orderid>
            <UmbrellaOrderId>txals</UmbrellaOrderId>
            <Cars>
                <Car>
                    <Uuid>driverid</Uuid>
                    <Clid>parkid</Clid>
                    <DBId>dbid</DBId>
                </Car>
            </Cars>
            <Payments>
                <Payment Currency="RUB" Sum="99.50" Type="ride" Time="2016-09-24T01:13:00+0300"/>
                <Payment Currency="RUB" Sum="9.50" Type="tips" Time="2016-09-24T01:13:00+0300"/>
            </Payments>
            <PaymentMethod type="card"/>
        </Order>
        """
    ),
    (
        {
            'status': 'finished',
            'taxi_status': 'complete',
            'cost': 99.5,
            'driver_cost': {
                'cost': 110.56
            },
            'request': {
                'payment': {
                    'type': dbh.orders.PAYMENT_TYPE_AGENT
                }
            },
            'performer': {
                'tariff': {
                    'class': 'econom'
                }
            },
            'payment_tech': {
                'type': 'agent',
                'main_card_payment_id': 'agent_007',
                'notifications': {
                    'payment': {
                        'to_send': {
                            'updated': datetime.datetime(2016, 9, 23, 22, 13),
                            'ride_sum': 99.5,
                            'tips_sum': 9.5,
                        }
                    }
                }
            },
            'price_modifiers': {
                'items': [
                    {
                        'type': 'multiplier',
                        'reason': 'ya_plus',
                        'value': 0.9,
                        'tariff_categories': ['econom']
                    }
                ]
            },
        },
        {
            'candidates': [
                {
                    'driver_id': 'parkid_driverid',
                    'alias_id': 'alias1',
                    'ci': 'c_id',
                }
            ],
            'aliases': [{'id': 'alias1'}],
            'performer': {
                'park_id': 'parkid',
                'uuid': 'driverid',
                'candidate_index': 0,
            }
        },
        {},
        # Subvention = 110.56 - 99.50 = 11.06
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Order>'
        '<Orderid>alias1</Orderid>'
        '<Cars><Car><Uuid>driverid</Uuid><Clid>parkid</Clid><DBId/></Car></Cars>'
        '<Payments>'
        '<Payment Currency="RUB" Sum="99.50" Type="ride" Time="2016-09-24T01:13:00+0300"/>'
        '<Payment Currency="RUB" Sum="9.50" Type="tips" Time="2016-09-24T01:13:00+0300"/>'
        '<Payment Currency="RUB" Sum="11.06" Type="subvention" Time="2016-09-24T01:13:00+0300"/>'
        '</Payments><PaymentMethod type="card"/>'
        '</Order>'
    ),
])
@pytest.inline_callbacks
def test_build_payment(order_doc, proc_doc, umbrella_proc_doc,
                       expected_value):
    order_proc = dbh.order_proc.Doc(proc_doc)
    order_proc.order = dbh.orders.Doc(order_doc)
    umbrella_proc_doc = (
        dbh.order_proc.Doc(umbrella_proc_doc) if umbrella_proc_doc else None
    )
    value = yield producers.build_payment(
        order_proc,
        order_doc['payment_tech']['notifications']['payment'],
        order_doc['payment_tech']['type'],
        umbrella_proc_doc=umbrella_proc_doc
    )
    assert value == re.sub(r'\n\s*', '', expected_value)


@pytest.inline_callbacks
def test_localize_addresses(patch):
    @patch('taxi.external.taxi_protocol.localize_geo_objects')
    @async.inline_callbacks
    def localize_geo_objects(orderid, locale, route_objects, log_extra=None):
        yield
        if len(route_objects) > 1 and route_objects[1].type == 'organization':
            async.return_value({
                'addresses': [{'fullname': 'Moskva',
                               'title': 'Yandex',
                               'short_text': 'Leo Tolstoy, 16'}
                              for _ in range(len(route_objects))]
            })
        if locale == 'ru':
            async.return_value({
                'addresses': [{'fullname': 'Moskva'}
                              for _ in range(len(route_objects))]
            })
        else:
            async.return_value({
                'addresses': [{'fullname': 'Moscow'}
                              for _ in range(len(route_objects))]
            })

    @patch('taxi.internal.driver_manager.get_driver_by_clid_uuid')
    @async.inline_callbacks
    def get_driver_by_clid_uuid(*args, **kwargs):
        yield
        async.return_value(dict(locale='ru'))

    assert (None, None, []) == (
        yield producers.localize_addresses(
            country_id=None,
            order_id='', driver_id='1', user_locale='ru', driver_position=None,
            source=None, destinations=[], log_extra=None)
    )

    class Address(object):
        def __init__(self, point, type='address'):
            self.point = point
            self.type = type

        def get(self, key, default=None):
            extra = dict(
                porchnumber='21',
                extra_data=dict(
                    floor='2',
                    apartment='42',
                    comment='kek',
                    doorphone_number='10#123'
                )
            )
            return extra.get(key, default)

    address = Address([1, 2])
    # No translations
    assert (None, address, [address]) == (
        yield producers.localize_addresses(
            country_id=None,
            order_id='', driver_id='1', user_locale='ru',
            source=address,
            destinations=[address],
            log_extra=None)
    )

    # A translation to ru (driver locale)
    EXPECTED_EXTRA_DATA = dict(
        porchnumber='21',
        extra_data=dict(
            floor='2',
            apartment='42',
            comment='kek',
            doorphone_number='10#123',
        )
    )
    expected_address = dict(
        fullname='Moskva',
    )
    expected_address.update(**EXPECTED_EXTRA_DATA)
    assert (None, expected_address, [expected_address]) == (
        yield producers.localize_addresses(
            country_id=None,
            order_id='', driver_id='1', user_locale='en',
            source=address,
            destinations=[address],
            log_extra=None)
    )

    org = Address([1, 2], 'organization')
    expected_address = dict(
        fullname='Moskva',
        title='Yandex',
        short_text='Leo Tolstoy, 16',
    )
    expected_address.update(**EXPECTED_EXTRA_DATA)
    # A translation to ru (driver locale) orgs
    assert (None, expected_address, [expected_address]) == (
        yield producers.localize_addresses(
            country_id=None,
            order_id='', driver_id='1', user_locale='en',
            source=org,
            destinations=[org],
            log_extra=None)
    )

    # Localized driver position
    assert (dict(fullname='Moskva'), address, [address]) == (
        yield producers.localize_addresses(
            country_id=None,
            order_id='', driver_id='1', user_locale='ru',
            driver_position=[1, 2],
            source=address,
            destinations=[address],
            log_extra=None)
    )

    # No destinations
    assert (dict(fullname='Moskva'), address, None) == (
        yield producers.localize_addresses(
            country_id=None,
            order_id='', driver_id='1', user_locale='ru',
            driver_position=[1, 2],
            source=address,
            log_extra=None)
    )


def test_request_attributes():
    order_proc = dbh.order_proc.Doc()
    order_proc.order = dbh.orders.Doc()
    print producers._build_request_attrs(order_proc, None)
    attrs = {}
    attrs['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    assert attrs == (
        producers._build_request_attrs(order_proc, None)
    )


def test_request_attributes_pool__exists():
    order_proc = dbh.order_proc.Doc()
    order_proc.order = dbh.orders.Doc()
    # https://wiki.yandex-team.ru/taxi/backend/pool/taximeter-protocol
    attrs = {}
    attrs['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    attrs['pool'] = 'yes'
    assert attrs == producers._build_request_attrs(
        order_proc, pool.PoolInfo(orders=[], route=[], driver_address=None,
                                  close_point_order_ids=[],
                                  previous_close_point_order_ids=[],
                                  experiments=[],
                                  changed_pickups_order_id=None))


@pytest.mark.parametrize('use_default_on_error,country_id,country_lang,'
                         'driver_lang,config_value,expected_result',
    [
        # have driver and locale
        (False, 'en', {'taximeter_lang': 'en'}, {'locale': 'kz'},
            ['en', 'ru', 'kz'], 'kz'),
        # have driver but no locale
        (False, 'en', {'taximeter_lang': 'en'}, {}, ['en', 'ru', 'kz'], 'en'),
        # have driver but no locale and no country_id
        (False, None, {'taximeter_lang': 'en'}, {}, ['en', 'ru', 'kz'], 'ru'),
        # have driver but no locale and no taximeter_lang
        (False, 'en', {}, {}, ['en', 'ru', 'kz'], 'ru'),
        # have driver but no locale and no country info
        (False, 'en', None, {}, ['en', 'ru', 'kz'], 'ru'),
        # no driver and do not use default
        (False, 'en', {'taximeter_lang': 'en'}, None, ['en', 'ru', 'kz'], None),
        # no driver and use default
        (True, 'en', {'taximeter_lang': 'en'}, None, ['en', 'ru', 'kz'], 'en'),
        # have driver but no locale and taximeter_lang not in config
        (False, 'en', {'taximeter_lang': 'en'}, {}, ['ru', 'kz'], 'ru'),
        # have driver but locale not in config
        (False, 'en', {'taximeter_lang': 'en'}, {'locale': 'kz'},
            ['en', 'ru'], 'ru')
    ]
)
@pytest.inline_callbacks
def test_get_driver_locale_default_lang_by_country(
    patch,
    use_default_on_error,
    country_id,
    country_lang,
    driver_lang,
    config_value,
    expected_result
):
    config.LOCALES_SUPPORTED.save(config_value)

    @patch('taxi.internal.city_kit.country_manager.get_doc')
    @async.inline_callbacks
    def get_doc(*args, **kwargs):
        yield
        if country_lang is None:
            raise country_manager.NotFoundError('error')
        async.return_value(country_lang)

    @patch('taxi.internal.driver_manager.get_driver_by_clid_uuid')
    @async.inline_callbacks
    def get_driver_by_clid_uuid(*args, **kwargs):
        yield
        if driver_lang is None:
            raise dbh.drivers.NotFound('error')
        async.return_value(driver_lang)

    result = yield producers.get_driver_locale(
        country_id,
        'some_driver_id',
        'ru',
        'ru' if use_default_on_error else None,
    )

    assert result == expected_result
