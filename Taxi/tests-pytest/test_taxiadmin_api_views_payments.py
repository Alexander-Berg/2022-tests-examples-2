# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import urlparse

import pytest

from django import test as django_test

from taxi import config
from taxi.conf import settings
from taxi.core import arequests
from taxi.core import async
from taxi.core import db
from taxi.external import experiments3
from taxi.external import transactions
from taxi.internal import archive
from taxi.internal import dbh
from taxi.internal.payment_kit import invoices
from taxi.internal.payment_kit import rebill
from taxi.util import dates
from taxi.util import evlog

from taxiadmin.api.views import payments
import taxiadmin.payments

from cardstorage_mock import mock_cardstorage

import helpers


PHONE_IDS_BY_PHONE = {
    'test_phone_1': ['592d51042f5c50410d821782', '5a09b034d1fe05d21a2c5735'],
    'test_phone_2': ['362564184864438b2c3a7a5c', 'e2653e6116a6001e671f718d'],
    '+71115556677': ['5587d1254794b3f8d9cb87a5'],
    '+98798777777': [],
}


@pytest.fixture
def search_orders_mock(areq_request):
    @areq_request
    def request(method, url, data, **kwargs):
        data = json.loads(data)

        assert method == arequests.METHOD_POST
        parse_result = urlparse.urlparse(url)

        assert parse_result.netloc == urlparse.urlparse(
            settings.API_ADMIN_URL).netloc

        path_components = list(filter(None, parse_result.path.split('/')))
        assert path_components[0: 3] == [
            'taxi_admin_personal', 'order', 'search'
        ]

        if not data:
            return areq_request.response(
                406, body=json.dumps({'message': 'Missing search params'})
            )

        assert data.keys() == ['user_phone']
        phone_ids = PHONE_IDS_BY_PHONE.get(data['user_phone'], [])

        return areq_request.response(
            200, body=json.dumps({
                'users': [
                    {'phone_id': phone_id} for phone_id in phone_ids
                ]
            })
        )


def _experiments3_mock(patch, restrict=None, last_orders=2, last_days=1):

    @patch('taxi.external.experiments3.get_config_values')
    @async.inline_callbacks
    def _get_experiments(*args, **kwargs):
        yield
        if restrict:
            restriction = {}
            if last_orders is not None:
                restriction['last_orders'] = last_orders
            if last_days is not None:
                restriction['last_days'] = last_days
            resp = [
                experiments3.ExperimentsValue(
                    'admin_restrictions',
                    {
                        '/payments/orders_info/': restriction,
                    },
                ),
            ]
        else:
            resp = []
        async.return_value(resp)


def mock_invoice_not_found(patch):
    @patch('taxi.external.transactions.v2_invoice_retrieve')
    @async.inline_callbacks
    def v2_invoice_retrieve(
            id_, prefer_transactions_data, tvm_src_service, log_extra=None,
    ):
        raise transactions.NotFoundError('Invoice not found')


def _mock_cargo_orders(patch, is_phoenix=False):
    @patch('taxi.external.cargo_orders.phoenix_bulk_traits')
    @async.inline_callbacks
    def cargo_orders_phoenix_bulk_traits(request, log_extra=None):
        response = {'orders': []}
        for cargo_ref_id in request.cargo_ref_ids:
            response_json = {
                'cargo_ref_id': cargo_ref_id,
                'is_phoenix_flow': is_phoenix
            }
            if is_phoenix:
                response_json['claim_id'] = 'claim_id'
            response['orders'].append(response_json)
        yield async.return_value(response)


@pytest.fixture
def mock_invoice(patch, data):
    @patch('taxi.external.transactions.v2_invoice_retrieve')
    @async.inline_callbacks
    def v2_invoice_retrieve(
            id_, prefer_transactions_data, tvm_src_service, log_extra=None,
    ):
        yield
        async.return_value(data)


@pytest.mark.asyncenv('blocking')
def test_get_fiscal_receipt_urls(replication_map_data):
    replication_map_data('order1')
    response = django_test.Client().get('/api/payments/order1/')
    assert response.status_code == 200

    data = json.loads(response.content)
    assert data == {
        'transactions': [
            {
                'receipt': {
                    'urls': {
                        'html': 'http://trust/fiscal1?mode=html',
                        'mobile': 'http://trust/fiscal1?mode=mobile',
                        'pdf': 'http://trust/fiscal1?mode=pdf'
                    }
                },
                'refunds': [
                    {
                        'urls': {
                            'html': 'http://trust/refund?mode=html',
                            'mobile': 'http://trust/refund?mode=mobile',
                            'pdf': 'http://trust/refund?mode=pdf'
                        }
                    }
                ],
                'reversal_receipt': {
                    'urls': {
                        'html': 'http://trust/reversal/?mode=html',
                        'mobile': 'http://trust/reversal/?mode=mobile',
                        'pdf': 'http://trust/reversal/?mode=pdf'
                    }
                }
            }
        ]
    }


@pytest.mark.asyncenv('blocking')
def test_get_reason_codes():
    response = django_test.Client().get('/api/payments/reason_codes/')
    assert response.status_code == 200


@pytest.mark.asyncenv('blocking')
def test_get_new_sum_reason_codes():
    response = django_test.Client().get('/api/payments/new_sum_reason_codes/')
    assert response.status_code == 200


@pytest.mark.parametrize(
    'order_id, expected_code, expected_order, permissions, '
    'experiments_restrict',
    [
        (
            'order2',
            200,
            {
                'disp_cost': {
                    'operator_login': 'Техподдержка',
                    'taximeter_cost': 236.0,
                    'disp_cost': 300.0,
                    'driver_cost': None,
                },
                'user_id': '30f0d7da8c864b06951e0e3ab4c405d3',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': True,
                'need_driver_accept': False,
                'driver_clid': 'clid',
                'driver_uuid': 'driverid',
                'compensations': [{
                    'full_sum': {'ride': 49.0},
                    'status': 'compensation_success',
                    'sum': {'ride': 49.0},
                    'trust_payment_id': 'compensation-trust-payment-id-1',
                    'updated': '2018-02-02T13:16:45+0300',
                    'refunds': [{
                        'status': 'refund_success',
                        'sum': {'ride': 10.0},
                        'updated': '2018-01-11T17:00:00+0300',
                        'trust_refund_id': 'refund_1'
                    }]
                }],
                'coupon_value': 10,
                'driver_info': {
                    'driver_exam_score': 4,
                    'driver_name': 'Driver',
                    'driver_rating': 0.8,
                    'is_driver_gold': False
                },
                'order_source': None,
                'subventions': None,
                'calc_price': 982.33,
                'is_decoupling': True,
                'driver_ride_sum_to_pay': 1.1
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            'order3',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            '     order3  ',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            'decoupling1',
            200,
            {
                'driver_info': None,
                'compensations': None,
                'transactions': [
                    {
                        'billing_service_id': '650',
                        'card': None,
                        'payment_type': 'corp',
                        'persistent_id': None,
                        'purchase_token': 'some_purchase_token',
                        'status': 'clear_success',
                        'sum': {'ride': 236.0},
                        'trust_payment_id': '',
                        'updated': '2018-05-17T18:45:34+0300'},
                    {
                        'billing_service_id': '651',
                        'card': None,
                        'payment_type': 'corp',
                        'persistent_id': None,
                        'status': 'clear_success',
                        'sum': {'ride': 236.0},
                        'trust_payment_id': '',
                        'updated': '2018-05-17T18:45:34+0300'
                    }
                ],
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            '       ',
            400,
            {},
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            'order3',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33
            },
            {
                'view_orders_limited': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            'order3',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            True,
        ),
        (
            'order_with_cost_includes_coupon',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 400.0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33,
                'default_compensation_sum': 636.0
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            True,
        ),
        (
            'order_with_cost_includes_coupon_no_cost',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 400.0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33,
                'default_compensation_sum': 400.0
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            True,
        ),
    ]
)
@pytest.mark.filldb(
    order_proc='test_get_orders_info',
    orders='test_get_orders_info',
    cities='test_get_orders_info',
)
@pytest.mark.translations([
    ('tariff', 'econom', 'ru', 'Эконом'),
    ('geoareas', 'moscow', 'ru', 'Москва'),
    ('order', 'payment.type.card', 'ru', 'Банковская карта'),
    ('order', 'subvention_rule.type.discount_payback', 'ru', 'Выплата скидки'),
    ('order', 'subvention_rule.type.bonus', 'ru', 'Бонус')
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ORDERS_INFO_SHOW_PERSONAL_DATA=True)
def test_get_orders_info(patch, order_id, expected_code, expected_order,
                         permissions, experiments_restrict):
    _test_get_orders_info(patch, order_id, expected_code, expected_order,
                          permissions, experiments_restrict)


@pytest.mark.parametrize(
    'order_id, expected_code, expected_order, permissions, '
    'experiments_restrict',
    [
        (
            'order2',
            200,
            {
                'disp_cost': {
                    'operator_login': 'Техподдержка',
                    'taximeter_cost': 236.0,
                    'disp_cost': 300.0,
                    'driver_cost': None,
                },
                'user_id': '30f0d7da8c864b06951e0e3ab4c405d3',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': True,
                'need_driver_accept': False,
                'driver_clid': 'clid',
                'driver_uuid': 'driverid',
                'compensations': [{
                    'full_sum': {'ride': 49.0},
                    'status': 'compensation_success',
                    'sum': {'ride': 49.0},
                    'trust_payment_id': 'compensation-trust-payment-id-1',
                    'updated': '2018-02-02T13:16:45+0300',
                    'refunds': [{
                        'status': 'refund_success',
                        'sum': {'ride': 10.0},
                        'updated': '2018-01-11T17:00:00+0300',
                        'trust_refund_id': 'refund_1'
                    }]
                }],
                'coupon_value': 10,
                'driver_info': {
                    'driver_exam_score': 4,
                    'driver_name': 'Driver',
                    'driver_rating': 0.8,
                    'is_driver_gold': False
                },
                'order_source': None,
                'subventions': None,
                'calc_price': 982.33,
                'is_decoupling': True,
                'driver_ride_sum_to_pay': 1.1
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            'order3',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            '     order3  ',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            'decoupling1',
            200,
            {
                'driver_info': None,
                'compensations': None,
                'transactions': [
                    {
                        'billing_service_id': '650',
                        'card': None,
                        'payment_type': 'corp',
                        'persistent_id': None,
                        'purchase_token': 'some_purchase_token',
                        'status': 'clear_success',
                        'sum': {'ride': 236.0},
                        'trust_payment_id': '',
                        'updated': '2018-05-17T18:45:34+0300'},
                    {
                        'billing_service_id': '651',
                        'card': None,
                        'payment_type': 'corp',
                        'persistent_id': None,
                        'status': 'clear_success',
                        'sum': {'ride': 236.0},
                        'trust_payment_id': '',
                        'updated': '2018-05-17T18:45:34+0300'
                    }
                ],
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            '       ',
            400,
            {},
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            'order3',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33
            },
            {
                'view_orders_limited': {'mode': 'unrestricted'},
            },
            False,
        ),
        (
            'order3',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            True,
        ),
        (
            'order_with_cost_includes_coupon',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 400.0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33,
                'default_compensation_sum': 636.0
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            True,
        ),
        (
            'order_with_cost_includes_coupon_no_cost',
            200,
            {
                'disp_cost': {
                    'operator_login': None,
                    'taximeter_cost': 236.0,
                    'disp_cost': None,
                    'driver_cost': 300.0
                },
                'user_id': '6e1efa5653d4484aa360f9d4b05feafd',
                'status': 'finished',
                'taxi_status': 'complete',
                'need_dispatch_accept': False,
                'need_driver_accept': True,
                'driver_clid': None,
                'driver_uuid': None,
                'compensations': None,
                'coupon_value': 400.0,
                'driver_info': None,
                'order_source': 'uber',
                'subventions': None,
                'calc_price': 859.33,
                'default_compensation_sum': 400.0
            },
            {
                'accept_card_orders': {'mode': 'unrestricted'},
            },
            True,
        ),
    ]
)
@pytest.mark.filldb(
    order_proc='test_get_orders_info',
    orders='test_get_orders_info',
    cities='test_get_orders_info',
)
@pytest.mark.translations([
    ('tariff', 'econom', 'ru', 'Эконом'),
    ('geoareas', 'moscow', 'ru', 'Москва'),
    ('order', 'payment.type.card', 'ru', 'Банковская карта'),
    ('order', 'subvention_rule.type.discount_payback', 'ru', 'Выплата скидки'),
    ('order', 'subvention_rule.type.bonus', 'ru', 'Бонус')
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(ORDERS_INFO_SHOW_PERSONAL_DATA=False)
def test_get_orders_info_without_user_phone(patch, order_id, expected_code, expected_order,
                         permissions, experiments_restrict):
    _test_get_orders_info(patch, order_id, expected_code, expected_order,
                          permissions, experiments_restrict, check_user_personal_data=True)


@pytest.inline_callbacks
def _test_get_orders_info(patch, order_id, expected_code, expected_order,
                         permissions, experiments_restrict, check_user_personal_data=False):
    mock_cardstorage(patch)

    @patch('taxiadmin.permissions.get_user_permissions')
    @async.inline_callbacks
    def get_user_permissions(request):
        request.permissions = permissions
        yield
        async.return_value(permissions)

    _experiments3_mock(patch, experiments_restrict)

    request_data = {
        'limit': 1,
        'order_id': order_id,
    }
    if experiments_restrict:
        request_data['last_days'] = 1
        request_data['last_orders'] = 2
    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.time_storage = evlog.new_time_storage('')
    request.superuser = False
    request.groups = []
    request.login = 'test_login'
    response = yield payments.get_orders_info(request)
    assert response.status_code == expected_code
    if expected_code == 200:
        response_data = json.loads(response.content)
        assert len(response_data['orders']) == 1
        order = response_data['orders'][0]

        if order['payment_type'] == 'corp':
            assert order['payment_type_label'] == 'Корпоративный'
        else:
            assert order['payment_type_label'] == 'Банковская карта'

        driver_check_fields = [
            'driver_name', 'driver_exam_score',
            'driver_rating', 'is_driver_gold'
        ]

        driver_info = expected_order.pop('driver_info')
        if driver_info:
            for field in driver_check_fields:
                assert order[field] == driver_info[field]
        else:
            for field in driver_check_fields:
                assert field not in order

        compensations = expected_order.pop('compensations')
        if compensations:
            assert order['compensations'] == compensations
        else:
            assert 'compensations' not in order

        if 'transactions' in expected_order:
            assert order['transactions'] == expected_order['transactions']

        for key, expected_value in expected_order.items():
            assert order.get(key) == expected_value, key

        if check_user_personal_data:
            assert 'user_phone' not in order or not order['user_phone']


@pytest.mark.parametrize(
    'restrict,need_accept,need_dispatch_accept,permission_limit,limit,'
    'offset,expected_ids', [
        # no offset & no limit - no new logic
        (
            False,
            False,
            False,
            None,
            None,
            None,
            ['order3', 'order2'],
        ),
        # no offset & no limit, need_accept - no new logic, found, limit
        # ignored in accept
        (
            False,
            True,
            False,
            None,
            1,
            None,
            ['order3', 'order2'],
        ),
        # no offset, need_dispatch_accept - no new logic, found, limit
        # ignored in disp_accept
        (
            False,
            False,
            True,
            None,
            1,
            None,
            ['order3', 'order2'],
        ),
        # offset & limit - new logic
        (
            False,
            False,
            False,
            None,
            1,
            0,
            ['order3'],
        ),
        # offset & limit - new logic
        (
            False,
            False,
            False,
            None,
            1,
            1,
            ['order2'],
        ),
        # new logic respects permission restrictions
        (
            True,
            False,
            False,
            1,
            2,
            0,
            ['order3'],
        ),
        # no offset - no new logic
        (
            False,
            False,
            False,
            None,
            1,
            None,
            ['order3', 'order2'],
        ),
])
@pytest.mark.filldb(
    order_proc='test_get_orders_info',
    orders='test_get_orders_info',
    cities='test_get_orders_info',
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_orders_info_by_card(
        patch, restrict, need_accept, need_dispatch_accept,
        permission_limit, limit, offset, expected_ids
):
    @patch('taxiadmin.permissions.get_user_permissions')
    @async.inline_callbacks
    def get_user_permissions(request):
        permissions = {
            'accept_card_orders': {'mode': 'unrestricted'},
            'search_payment_by_card': {'mode': 'unrestricted'},
        }
        request.permissions = permissions
        yield
        async.return_value(permissions)

    @patch('taxiadmin.payments.get_orders_by_card_number')
    @async.inline_callbacks
    def get_orders_by_card_number(card_number, filters=None, log_extra=None):
        orders = yield db.orders.find(
            {'_id': {'$in': ['order2', 'order3']}}
        ).run()
        async.return_value(orders)

    mock_cardstorage(patch)
    _experiments3_mock(
        patch,
        restrict=restrict,
        last_orders=permission_limit,
        last_days=None,
    )
    request_data = {
        'card': '1111****2222',
    }
    if need_accept:
        request_data['need_accept'] = True
    if need_dispatch_accept:
        request_data['need_dispatch_accept'] = True
    if limit is not None:
        request_data['limit'] = limit
    if offset is not None:
        request_data['offset'] = offset
    if permission_limit is not None:
        request_data['last_orders'] = permission_limit
    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.time_storage = evlog.new_time_storage('')
    request.superuser = False
    request.groups = []
    request.login = 'test_login'
    response = yield payments.get_orders_info(request)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    actual_ids = [an_order['id'] for an_order in response_data['orders']]
    assert actual_ids == expected_ids


@pytest.mark.config(
    ADMIN_PAYMENTS_ARCHIVE_CHUNK_SIZE=1,
)
@pytest.inline_callbacks
def test_merge_mongo_and_yt_orders(patch):
    @patch('taxi.internal.archive.get_many_orders')
    @async.inline_callbacks
    def get_many_orders(
        ids, lookup_yt=True, src_tvm_service=None, log_extra=None
    ):
        async.return_value([])
        yield
    merged = yield taxiadmin.payments._merge_mongo_and_yt_orders(
        mongo_orders=[],
        yt_orders_ids=['first_id', 'second_id']
    )
    assert merged == []
    calls = get_many_orders.calls
    assert len(calls) == 2
    assert calls[0]['args'] == (['first_id'],)
    assert calls[1]['args'] == (['second_id'],)


case = helpers.case_getter(
    'request_data initial_idempotency_token via_transactions '
    'has_billing_error billing_do_refund_responses permissions config_data '
    'expected_code expected_response expected_last_decision expected_refunds',
    via_transactions=False,
    has_billing_error=False,
    billing_do_refund_responses=[{'status': 'success'}],
    expected_code=200,
    expected_response={},
    expected_last_decision=None,
    config_data={},
    permissions={
        'refund_compensations': {'mode': 'unrestricted'},
    }
)
case_400_error = case.partial(
    expected_code=400,
    billing_do_refund_responses=[],
    expected_refunds=[],
)
case_409_error = case_400_error.partial(
    expected_code=409,
    expected_response={
        'status': 'error',
        'message': 'refresh the page and try again',
        'code': 'race_condition',
    },
)
CONFIG_DATA_ALLOWS_AUTO = {
    'allow_autocompensations': True,
}
CONFIG_DATA_ALLOWS_REFUNDS = {
    'allow_partially_refunded': True,
}
CONFIG_DATA_ALLOWS_UNPAID = {
    'allow_unpaid_rides': True,
}


@pytest.mark.config(
    REFUND_COMPENSATIONS_SINCE='2016-01-01T00:00:00+00:00'
)
@pytest.mark.parametrize(
    case.params,
    [
        # 0: successful refund
        case(
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-2',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_refunds=[
                {   # one refund made just now (see @pytest.mark.now below)
                    'billing_response': {
                        # see do_refund patch in the test function
                        'status': 'success',
                    },
                    'created': datetime.datetime(2019, 5, 20, 10, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 390000},
                    'trust_refund_id': 'compensation-trust-payment-id-2_refund',
                    'updated': datetime.datetime(2019, 5, 20, 10, 0),
                    'refund_made_at': datetime.datetime(2019, 5, 20, 10, 0),
                }
            ],
        ),
        # 1: successful refund for old order without compensations.refunds field
        case(
            request_data={
                'order_id': 'order4',
                'payment_id': 'compensation-trust-payment-id-6',
                'sum': 6,
                'zendesk_ticket': 'some_other_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 10,
            },
            expected_refunds=[
                {   # one refund made just now (see @pytest.mark.now below)
                    'billing_response': {
                        # see do_refund patch in the test function
                        'status': 'success',
                    },
                    'created': datetime.datetime(2019, 5, 20, 10, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 60000},
                    'trust_refund_id': 'compensation-trust-payment-id-6_refund',
                    'updated': datetime.datetime(2019, 5, 20, 10, 0),
                    'refund_made_at': datetime.datetime(2019, 5, 20, 10, 0),
                }
            ],
        ),
        # 2: sum too big -> error 400 (and no refund appeared in the compensation)
        case_400_error(
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-2',
                'sum': 390,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_response={
                'code': 'refund_sum_too_big',
                'message': 'Refund sum cannot be more than 39.0',
                'status': 'error',
            },
        ),
        # 3: compensation has refunds, so it cannot be refunded
        case_400_error(
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-1',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_response={
                'code': 'cannot_refund_compensation',
                'message': 'Cannot refund compensation',
                'status': 'error',
            },
            expected_refunds=[
                # just old refund in the order.billing_tech.compensations
                {
                    'billing_response': {'status': 'success'},
                    'created': datetime.datetime(2018, 1, 11, 13, 0),
                    'data': None,
                    'refund_made_at': datetime.datetime(2018, 1, 11, 14, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 100000},
                    'trust_refund_id': 'refund_1',
                    'updated': datetime.datetime(2018, 1, 11, 14, 0),
                }
            ],
        ),
        # 4: payment_id is absent in order - 404
        case_400_error(
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-non-existent',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_code=404,
            expected_response={
                'code': 'compensation_not_found',
                'message': 'Compensation not found',
                'status': 'error',
            },
            expected_refunds=None,
        ),
        # 5: payment_id fits automatic compens (which should not be refunded according to config - 400 (?) 409/406 (?)
        # no refund appeared in the compensation
        case_400_error(
            request_data={
                'order_id': 'order3',
                'payment_id': 'compensation-trust-payment-id-4',
                'sum': 49,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_response={
                'code': 'cannot_refund_compensation',
                'message': 'Cannot refund compensation',
                'status': 'error',
            },
        ),
        # 6: payment_id fits failed compensation
        case_400_error(
            request_data={
                'order_id': 'order4',
                'payment_id': 'compensation-trust-payment-id-5',
                'sum': 49,
                'zendesk_ticket': 'some_other_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 10,
            },
            expected_response={
                'code': 'cannot_refund_compensation',
                'message': 'Cannot refund compensation',
                'status': 'error',
            },
        ),
        # 7: billing refused to refund - 40X with error text (?) for duty developer
        case_400_error(
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-2',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            has_billing_error=True,
            expected_response={
                'status': 'error',
                'message': '''Billing responded {u'status': u'some_error'}''',
                'code': 'billing_error',
            },
        ),
        # 8: check what happens when billing responds wait_for_notification
        case(
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-2',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            billing_do_refund_responses=[
                {
                    'status': 'wait_for_notification',
                    'status_desc': 'refund is in queue',
                },
                {
                    'status': 'wait_for_notification',
                    'status_desc': 'refund is in queue',
                },
                {
                    'status': 'success',
                    'status_desc': 'refund sent to payment system',
                },
            ],
            expected_refunds=[
                {
                    'billing_response': {
                        'status': 'success',
                        'status_desc': 'refund sent to payment system',
                    },
                    'created': datetime.datetime(2019, 5, 20, 10, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 390000},
                    'trust_refund_id': 'compensation-trust-payment-id-2_refund',
                    'updated': datetime.datetime(2019, 5, 20, 10, 0),
                    'refund_made_at': datetime.datetime(2019, 5, 20, 10, 0),
                }
            ],
        ),
        # 9: idempotency token is different, refund successful
        case(
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-2',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            initial_idempotency_token='previous_idempotency_token',
            expected_refunds=[
                {   # one refund made just now (see @pytest.mark.now below)
                    'billing_response': {
                        # see do_refund patch in the test function
                        'status': 'success',
                    },
                    'created': datetime.datetime(2019, 5, 20, 10, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 390000},
                    'trust_refund_id': 'compensation-trust-payment-id-2_refund',
                    'updated': datetime.datetime(2019, 5, 20, 10, 0),
                    'refund_made_at': datetime.datetime(2019, 5, 20, 10, 0),
                }
            ],
        ),
        # 10: idempotency token is same, no refund
        case_409_error(
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-2',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'same_idempotency_token',
                'version': 11,
            },
            initial_idempotency_token='same_idempotency_token',
        ),
        # 11: billing.version is different
        case_409_error(
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-2',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 12,
            },
        ),
        # 12: payment_id fits automatic compens and config allows refunding it
        # refund appears as for manual compensations
        case(
            config_data=CONFIG_DATA_ALLOWS_AUTO,
            request_data={
                'order_id': 'order3',
                'payment_id': 'compensation-trust-payment-id-4',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_refunds=[
                {
                    'billing_response': {
                        'status': 'success',
                    },
                    'created': datetime.datetime(2019, 5, 20, 10, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 390000},
                    'trust_refund_id': 'compensation-trust-payment-id-4_refund',
                    'updated': datetime.datetime(2019, 5, 20, 10, 0),
                    'refund_made_at': datetime.datetime(2019, 5, 20, 10, 0),
                }
            ],
        ),
        # 12.5: refund unpaid ride
        # refund appears as for manual compensations
        case(
            config_data=CONFIG_DATA_ALLOWS_UNPAID,
            request_data={
                'order_id': 'unpaid_order',
                'payment_id': 'compensation-trust-payment-id-2',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_refunds=[
                {
                    'billing_response': {
                        'status': 'success',
                    },
                    'created': datetime.datetime(2019, 5, 20, 10, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 390000},
                    'trust_refund_id': 'compensation-trust-payment-id-2_refund',
                    'updated': datetime.datetime(2019, 5, 20, 10, 0),
                    'refund_made_at': datetime.datetime(2019, 5, 20, 10, 0),
                }
            ],
        ),
        # 13: sum too big (because compens is partially refunded) -> error 400
        case_400_error(
            config_data=CONFIG_DATA_ALLOWS_REFUNDS,
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-1',
                'sum': 40,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_response={
                'code': 'refund_sum_too_big',
                'message': 'Refund sum cannot be more than 39.0',
                'status': 'error',
            },
            expected_refunds=[
                # just old refund in the order.billing_tech.compensations
                {
                    'billing_response': {'status': 'success'},
                    'created': datetime.datetime(2018, 1, 11, 13, 0),
                    'data': None,
                    'refund_made_at': datetime.datetime(2018, 1, 11, 14, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 100000},
                    'trust_refund_id': 'refund_1',
                    'updated': datetime.datetime(2018, 1, 11, 14, 0),
                }
            ],
        ),
        # 14: has refund yet can be refunded by the rest of sum (if config allows)
        case(
            config_data=CONFIG_DATA_ALLOWS_REFUNDS,
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-1',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_refunds=[
                # just old refund in the order.billing_tech.compensations
                {
                    'billing_response': {'status': 'success'},
                    'created': datetime.datetime(2018, 1, 11, 13, 0),
                    'data': None,
                    'refund_made_at': datetime.datetime(2018, 1, 11, 14, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 100000},
                    'trust_refund_id': 'refund_1',
                    'updated': datetime.datetime(2018, 1, 11, 14, 0),
                },
                {
                    'billing_response': {'status': 'success'},
                    'created': datetime.datetime(2019, 5, 20, 10, 0),
                    # 'data': None,
                    'refund_made_at': datetime.datetime(2019, 5, 20, 10, 0),
                    'status': 'refund_success',
                    'sum': {'ride': 390000},
                    'trust_refund_id': 'compensation-trust-payment-id-1_refund',
                    'updated': datetime.datetime(2019, 5, 20, 10, 0),
                }

            ],
        ),
        # 15: refund via transactions
        case(
            via_transactions=True,
            request_data={
                'order_id': 'order2',
                'payment_id': 'compensation-trust-payment-id-2',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_refunds=[],
            billing_do_refund_responses=[],
            expected_last_decision={
                    'created': datetime.datetime(2019, 5, 20, 10),
                    'operator_login': 'test_login',
                    'otrs_ticket': 'some_ticket',
                    'decision': 'compensation_refund',
                    'compensation_refund_sum': {'ride': 39},
                    'transactions_params': {
                        'operation_id': 'compensation/refund/abc',
                        'trust_payment_id': 'compensation-trust-payment-id-2',
                        'net_amount': '39',

                }
            }
        ),
        # 16: compensation too old to refund
        case_400_error(
            request_data={
                'order_id': 'order5',
                'payment_id': 'compensation-trust-payment-id-1',
                'sum': 39,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_response={
                'code': 'cannot_refund_compensation',
                'message': 'Compensation is too old to refund',
                'status': 'error',
            },
        ),
        # 17: too small compensation sum
        case_400_error(
            request_data={
                'order_id': 'order6',
                'payment_id': 'compensation-trust-payment-id-1',
                'sum': 4.4408920985e-16,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_response={
                'code': 'general',
                'message': (
                    'Request error: 4.4408920985e-16 is less than the minimum '
                    'of 1\n\nFailed validating \'minimum\' in '
                    'schema[\'properties\'][\'sum\']:\n    {\'minimum\': 1, '
                    '\'type\': \'number\'}\n\nOn instance[\'sum\']:\n    '
                    '4.4408920985e-16'
                ),
                'status': 'error',
            },
        ),
        # 18: there is an active compensation operation
        case_400_error(
            request_data={
                'order_id': 'order7',
                'payment_id': 'compensation-trust-payment-id-1',
                'sum': 1337,
                'zendesk_ticket': 'some_ticket',
                'idempotency_token': 'some_idempotency_token',
                'version': 11,
            },
            expected_response={
                'code': 'there_is_active_compensation_operation',
                'message': 'There is already an active compensation operation',
                'status': 'error',
            },
        ),
    ]
)
@pytest.mark.filldb(
    orders='test_orders_info_compensations',
    order_proc='test_get_orders_info',
    cities='test_get_orders_info',
)
@pytest.mark.now('2019-05-20 10:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_refund_compensation(patch,
                             request_data, initial_idempotency_token,
                             via_transactions,
                             has_billing_error, billing_do_refund_responses,
                             permissions, config_data,
                             expected_code, expected_response,
                             expected_last_decision, expected_refunds):
    _patch_try_process_invoice(patch, via_transactions)
    _patch_uuid4(patch)

    if config_data:
        yield config.ADMIN_COMPENSATION_REFUND_RULES.save(config_data)

    do_refund_calls = []
    do_refund_calls_expected = [
        response for response in billing_do_refund_responses
    ]
    payment_id = request_data['payment_id']
    order_id = request_data['order_id']

    if initial_idempotency_token is not None:
        idempotency_field = 'idempotency_keys.{}'.format(
            'taxi_admin_views_payments_refund_compensation'
        )
        yield db.orders.update(
            {'_id': order_id},
            {'$set': {idempotency_field: initial_idempotency_token}}
        )

    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    @patch('taxiadmin.audit.log_action')
    @async.inline_callbacks
    def log_action(*args, **kwargs):
        yield
        async.return_value('some_bson_doc_id')

    @patch('taxi.external.billing._call_simple')
    @async.inline_callbacks
    def billing_call_simple(billing_service, method, params, timeout=None,
                            log_extra=None):
        yield
        if has_billing_error:
            call_response = {'status': 'some_error'}
        else:
            if method == 'CreateRefund':
                call_response = {
                    'status': 'success',
                    'trust_refund_id': request_data['payment_id'] + '_refund',
                }
            elif method == 'DoRefund':
                call_response = billing_do_refund_responses.pop(0)
                do_refund_calls.append(call_response)
            elif method == 'CheckBasket':
                call_response = {'status': 'success'}
            else:
                raise ValueError('unmocked method: {}'.format(method))
        async.return_value(call_response)

    @patch('taxi.core.async.sleep')
    @async.inline_callbacks
    def sleep(seconds):
        yield

    request = yield helpers.TaxiAdminRequest(permissions=permissions).json(
        data=request_data
    )
    response = payments.refund_compensation(request)
    assert response.status_code == expected_code
    response_data = json.loads(response.content)
    assert expected_response == response_data
    order_doc = yield db.orders.find_one(order_id)
    try:
        refunds = next(
            comp['refunds']
            for comp in order_doc['billing_tech']['compensations']
            if comp['trust_payment_id'] == payment_id
        )
    except StopIteration:
        refunds = None
    assert do_refund_calls == do_refund_calls_expected
    assert refunds == expected_refunds
    if expected_last_decision is not None:
        actual_last_decision = order_doc['payment_tech']['history'][-1]
        assert actual_last_decision == expected_last_decision


def _patch_try_process_invoice(patch, via_transactions):
    @patch('taxi.internal.payment_kit.invoices.try_process_invoice')
    @async.inline_callbacks
    def try_process_invoice(payable_order, log_extra=None):
        async.return_value(invoices.Processing(via_transactions, None))
        yield


def _patch_uuid4(patch):
    class Mock(object):
        def __init__(self, hex):
            self.hex = hex

    @patch('uuid.uuid4')
    def uuid4():
        return Mock('abc')


case = helpers.case_getter(
    'order_id expected_code compensations config_data',
    expected_code=200,
)
case_allowed_unpaid = case.partial(
    config_data=CONFIG_DATA_ALLOWS_UNPAID,
)
case_allowed_auto = case.partial(
    config_data=CONFIG_DATA_ALLOWS_AUTO,
)
case_allowed_refund = case.partial(
    config_data=CONFIG_DATA_ALLOWS_REFUNDS,
)
COMPENSATIONS_UNPAID_RIDE = [
    {   # this compensation is refundable
        'full_sum': {'ride': 39.0},
        'status': 'compensation_success',
        'sum': {'ride': 39.0},
        'trust_payment_id': 'compensation-trust-payment-id-2',
        'updated': '2018-02-02T22:26:45+0300',
        'is_refundable': True,
        'max_refund_sum': 39,
    }
]
COMPENSATIONS_WITH_REFUND = [
    {   # first compensation is refunded, has no is_refundable flag
        'full_sum': {'ride': 49.0},
        'status': 'compensation_success',
        'sum': {'ride': 49.0},
        'trust_payment_id': 'compensation-trust-payment-id-1',
        'updated': '2018-02-02T13:16:45+0300',
        'refunds': [{
            'status': 'refund_success',
            'sum': {'ride': 10.0},
            'updated': '2018-01-11T17:00:00+0300',
            'trust_refund_id': 'refund_1'
        }]
    },
    {   # this compensation is refundable
        'full_sum': {'ride': 39.0},
        'status': 'compensation_success',
        'sum': {'ride': 39.0},
        'trust_payment_id': 'compensation-trust-payment-id-2',
        'updated': '2018-02-02T22:26:45+0300',
        'is_refundable': True,
        'max_refund_sum': 39,
    },
]
COMPENSATIONS_WITH_REFUND_REFUNDABLE = [
    dict(COMPENSATIONS_WITH_REFUND[0], is_refundable=True, max_refund_sum=39),
    COMPENSATIONS_WITH_REFUND[1],
]
COMPENSATIONS_WITH_AUTO = [
    {
        'full_sum': {'ride': 49.0},
        'status': 'compensation_success',
        'sum': {'ride': 49.0},
        'trust_payment_id': 'compensation-trust-payment-id-3',
        'updated': '2018-02-02T13:16:45+0300',
        'is_refundable': True,
        'max_refund_sum': 49,
    },
    {
        'full_sum': {'ride': 39.0},
        'status': 'compensation_success',
        'sum': {'ride': 39.0},
        'trust_payment_id': 'compensation-trust-payment-id-4',
        'updated': '2018-02-02T22:26:45+0300',
    },
]
COMPENSATIONS_WITH_AUTO_REFUNDABLE = [
    COMPENSATIONS_WITH_AUTO[0],
    dict(COMPENSATIONS_WITH_AUTO[1], is_refundable=True, max_refund_sum=39),
]
COMPENSATIONS_WITH_FAILED = [
    {
        'full_sum': {'ride': 49.0},
        'status': 'compensation_fail',
        'sum': {'ride': 49.0},
        'trust_payment_id': 'compensation-trust-payment-id-5',
        'updated': '2018-02-02T13:16:45+0300',
    },
    {
        'full_sum': {'ride': 9.0},
        'status': 'compensation_success',
        'sum': {'ride': 9.0},
        'trust_payment_id': 'compensation-trust-payment-id-6',
        'updated': '2018-02-02T13:16:46+0300',
        'is_refundable': True,
        'max_refund_sum': 9,
    },
]


@pytest.mark.parametrize(
    case.params,
    [
        case(
            order_id='order2',
            compensations=COMPENSATIONS_WITH_REFUND,
        ),
        case_allowed_unpaid(
            order_id='unpaid_order',
            compensations=COMPENSATIONS_UNPAID_RIDE,
        ),
        # allowing autocompensations does not affect refunded compensations
        case_allowed_auto(
            order_id='order2',
            compensations=COMPENSATIONS_WITH_REFUND,
        ),
        # allowing refund does affect refunded compensations
        case_allowed_refund(
            order_id='order2',
            compensations=COMPENSATIONS_WITH_REFUND_REFUNDABLE,
        ),
        case(
            order_id='order3',
            compensations=COMPENSATIONS_WITH_AUTO,
        ),
        case_allowed_auto(
            order_id='order3',
            compensations=COMPENSATIONS_WITH_AUTO_REFUNDABLE,
        ),
        case(
            order_id='order4',
            compensations=COMPENSATIONS_WITH_FAILED,
        ),
        # allowing autocompensations does not affect failed compensations
        case_allowed_auto(
            order_id='order4',
            compensations=COMPENSATIONS_WITH_FAILED,
        ),
        # allowing refunds does not affect failed compensations
        case_allowed_refund(
            order_id='order4',
            compensations=COMPENSATIONS_WITH_FAILED,
        ),
        # wrong order_id
        case(
            order_id='       ',
            expected_code=400,
        ),
    ]
)
@pytest.mark.filldb(
    orders='test_orders_info_compensations',
    order_proc='test_get_orders_info',
    cities='test_get_orders_info',
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_orders_info_compensations(order_id, expected_code, compensations,
                                   config_data, patch):

    mock_cardstorage(patch)
    _experiments3_mock(patch)
    if config_data:
        yield config.ADMIN_COMPENSATION_REFUND_RULES.save(config_data)

    request = helpers.TaxiAdminRequest(superuser=True).json(
        data={
            'limit': 1,
            'order_id': order_id,
        },
    )
    response = yield payments.get_orders_info(request)
    assert response.status_code == expected_code
    if expected_code == 200:
        response_data = json.loads(response.content)
        assert len(response_data['orders']) == 1
        order = response_data['orders'][0]

        if compensations:
            assert order['compensations'] == compensations
        else:
            assert 'compensations' not in order


@pytest.mark.parametrize(
    'query,expected_code,expected_count',
    [
        (
            {'limit': 1},
            400,
            None
        ),
        (
            {
                'limit': 1,
                'order_id': 'order3',
                'phone': 'test_phone_1'
            },
            200,
            1
        ),
        (
            {
                'limit': 1,
                'order_id': 'order3',
                'phone': 'test_phone_2'
            },
            200,
            0
        ),
        (
            {
                'limit': 10,
                'order_id': 'order3',
                'phone': '+71115556677'
            },
            200,
            0
        ),
        (
            {
                'limit': 1,
                'order_id': 'order3',
                'phone': '+98798777777'
            },
            200,
            0
        ),
    ]
)
@pytest.mark.filldb(
    orders='test_get_orders_info',
    cities='test_get_orders_info',
    user_phones='test_get_orders_info',
)
@pytest.mark.usefixtures('search_orders_mock')
@pytest.mark.asyncenv('blocking')
def test_get_orders_info_with_multiple_parameters(
        patch, query, expected_code, expected_count):
    mock_cardstorage(patch)
    _experiments3_mock(patch)

    @patch('taxi.internal.archive.get_many_order_proc_by_ids')
    @async.inline_callbacks
    def get_many_order_proc_by_ids(ids, **kwargs):
        yield async.return_value([])

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    def fake_clean_international_phone(phone, *args, **kwargs):
        return phone

    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps(query),
        content_type='application/json'
    )
    request.time_storage = evlog.new_time_storage('')
    request.login = 'some_login'
    request.superuser = True
    request.groups = []
    response = payments.get_orders_info(request)
    assert response.status_code == expected_code
    if response.status_code == 200:
        response_data = json.loads(response.content)
        assert len(response_data['orders']) == expected_count


@pytest.mark.filldb(
    orders='test_get_orders_info',
    cities='test_get_orders_info',
    user_phones='test_get_orders_info',
)
@pytest.mark.usefixtures('search_orders_mock')
@pytest.mark.asyncenv('blocking')
def test_get_orders_info_with_just_partner_payments(
        patch):
    mock_cardstorage(patch)
    _experiments3_mock(patch)

    @patch('taxi.internal.archive.get_many_order_proc_by_ids')
    @async.inline_callbacks
    def get_many_order_proc_by_ids(ids, **kwargs):
        yield async.return_value([])

    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps({'order_id': 'order3'}),
        content_type='application/json'
    )
    request.time_storage = evlog.new_time_storage('')
    request.login = 'some_login'
    request.superuser = True
    request.groups = []
    response = payments.get_orders_info(request)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data['orders']) == 1
    response_order_info = response_data['orders'][0]
    assert response_order_info['just_partner_payments']
    assert response_order_info['cargo_ref_id'] == 'some_awesome_cargo_id'


@pytest.mark.config(ORDERS_INFO_GET_PHOENIX_TRAITS={'behaviour': 'enabled'})
@pytest.mark.filldb(
    orders='test_get_orders_info',
    cities='test_get_orders_info',
    user_phones='test_get_orders_info',
)
@pytest.mark.usefixtures('search_orders_mock')
@pytest.mark.asyncenv('blocking')
def test_get_orders_info_is_phoenix_flow(
        patch):
    mock_cardstorage(patch)
    _experiments3_mock(patch)
    _mock_cargo_orders(patch, is_phoenix=True)

    @patch('taxi.internal.archive.get_many_order_proc_by_ids')
    @async.inline_callbacks
    def get_many_order_proc_by_ids(ids, **kwargs):
        yield async.return_value([])

    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps({'order_id': 'order3'}),
        content_type='application/json'
    )
    request.time_storage = evlog.new_time_storage('')
    request.login = 'some_login'
    request.superuser = True
    request.groups = []
    response = payments.get_orders_info(request)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data['orders']) == 1
    response_order_info = response_data['orders'][0]
    assert response_order_info['cargo_ref_id'] == 'some_awesome_cargo_id'
    assert response_order_info['delivery_payments'] == {
        'flow': 'claims',
        'entity_id': 'claim_id'
    }


@pytest.mark.config(PAYMENTS_ACCESS_BY_COUNTRY=True)
@pytest.mark.parametrize(
    'permissions, query, expected_code, expected',
    [
        (
            {},
            {'limit': 1, 'order_id': 'id1'},
            403,
            None,
        ),
        (
            {
                'accept_card_orders': {
                    'mode': 'countries_filter',
                    'countries_filter': {'ukr'}
                }
            },
            {'limit': 1, 'order_id': 'id1'},
            200,
            [],
        ),
        (
            {
                'accept_card_orders': {
                    'mode': 'countries_filter',
                    'countries_filter': {'rus'}
                }
            },
            {'limit': 1, 'order_id': 'id1'},
            200,
            {
                'id': 'id1'
            },
        )
    ]
)
@pytest.mark.filldb(
    orders='test_access',
    order_proc='test_access',
    cities='test_get_orders_info',
)
@pytest.mark.asyncenv('blocking')
def test_get_orders_info_by_countries(
        patch, load, permissions, query, expected_code, expected,
):
    mock_cardstorage(patch)

    @patch('taxi.internal.archive.get_many_order_proc_by_ids')
    @async.inline_callbacks
    def get_many_order_proc_by_ids(ids, **kwargs):
        yield async.return_value([])

    @patch('taxi.external.archive.get_order_by_id_or_alias')
    @async.inline_callbacks
    def get_order_by_id_or_alias(order_id, lookup_yt=True,
                                 src_tvm_service=None, log_extra=None):
        doc = yield db.orders.find_one({'_id': order_id})
        async.return_value({'doc': doc})

    @patch('taxi.internal.dbh.admin_groups.Doc.get_groups_permissions')
    @async.inline_callbacks
    def get_groups_permissions(groups):
        yield
        async.return_value(
            permissions
        )

    _experiments3_mock(patch, False)

    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps(query),
        content_type='application/json'
    )
    request.time_storage = evlog.new_time_storage('')
    request.superuser = False
    request.groups = []
    request.login = 'test_login'
    response = payments.get_orders_info(request)
    assert response.status_code == expected_code, 'Response {}'.format(response.content)
    if response.status_code == 200:
        response_data = json.loads(response.content)
        if isinstance(expected, list):
            assert response_data['orders'] == expected
        else:
            response_data['orders'][0]['id'] = expected['id']


@pytest.mark.parametrize(
    'query,expected_code',
    [
        (
            {
                'order_id': 'order3',
                'zendesk_ticket': '123',
            },
            200
        ),
        (
            {
                'order_id': 'order4',
                'zendesk_ticket': '1234',
                'ticket_type': 'chatterbox'
            },
            200
        ),
        (
            {
                'order_id': 'order4',
                'zendesk_ticket': '123',
                'ticket_type': 'chatterbox'
            },
            400
        )
    ]
)
@pytest.mark.filldb(
    order_proc='test_unbind_ticket_new',
    finance_tickets_zendesk='test_unbind_ticket_new',
    tariff_settings='unbind_new'
)
@pytest.mark.asyncenv('blocking')
def test_unbind_ticket_new_mode(patch, query, expected_code):

    @patch('taxi.external.archive.get_order_proc_by_id')
    @async.inline_callbacks
    def get_order_proc_by_id(order_id, **kwargs):
        yield async.return_value({'doc': {}})

    response = django_test.Client().post(
        path='/api/payments/unbind_zendesk_ticket/',
        data=json.dumps(query),
        content_type='application/json'
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        query = {
            '_id': query['zendesk_ticket'],
            'order_id': query['order_id'],
        }
        tickets_count = db.finance_tickets_zendesk._collection.count(query)
        assert tickets_count == 0


@pytest.mark.now('2018-11-16 13:00:00+03')
@pytest.mark.filldb(parks='compensate_park')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_compensate_park(patch, load):
    @patch('taxi.internal.archive.restore_many_orders')
    @async.inline_callbacks
    def restore_orders(orders_ids, update=False, src_tvm_service=None,
                       log_extra=None):
        yield db.orders.insert(
            json.loads(
                load('restore_order.json'),
                object_hook=helpers.bson_object_hook
            )
        )

    @patch('taxi.internal.archive.restore_many_subvention_reasons')
    @async.inline_callbacks
    def restore_subvention_reasons(orders_ids, update=False,
                                   src_tvm_service=None, log_extra=None):
        reasons = json.loads(load('restore_subvention_reason.json'))
        reasons['due'] = dates.parse_timestring(reasons['due'])
        yield db.subvention_reasons.insert(reasons)

    @patch('taxi.internal.archive.restore_many_mph_results')
    @async.inline_callbacks
    def restore_mph_results(orders_ids, update=False, src_tvm_service=None,
                            log_extra=None):
        yield db.mph_results.insert({'_id': 'compensate_order'})

    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    @patch('taxi.internal.park_manager.get_trust_status')
    @async.inline_callbacks
    def patch_donations(*args, **kwargs):
        yield
        async.return_value('init')

    @patch('taxi_stq.client.order_billing')
    def order_billing_task(order_id, reason, **kwargs):
        assert order_id == 'compensate_order'
        assert reason == 'dryclean'

    @patch('taxi.external.billing_orders.send_doc')
    def send_doc(kind, external_obj_id, external_event_ref, event_at, data,
                 reason, **kwargs):
        expected_doc = json.loads(load('expected_manual_subvention_doc.json'))
        assert kind == expected_doc['kind']
        assert external_obj_id == expected_doc['external_obj_id']
        assert external_event_ref == expected_doc['external_event_ref']
        assert event_at == expected_doc['event_at']

        expected_data = expected_doc['data']

        assert data['billing_contract_is_set'] == (
               expected_data['billing_contract_is_set'])

        if data['billing_contract_is_set']:
            assert sorted(data['billing_contract'].items()) == (
                sorted(expected_data['billing_contract'].items()))
            data.pop('billing_contract')
            expected_data.pop('billing_contract')

        assert sorted(data.items()) == sorted(expected_data.items())
        assert reason == expected_doc['reason']

    response = django_test.Client().post(
        '/api/payments/compensate_park/',
        data=json.dumps({
            'order_id': 'compensate_order',
            'sum': 100,
            'reason': 'dryclean',
            'version': 1,
            'zendesk_ticket': ' 100001\n\t',
        }),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert json.loads(response.content) == {}

    subvention_reason = yield db.subvention_reasons.find_one(
        {'order_id': 'compensate_order'}
    )

    assert subvention_reason['subvention_bonus'][-1] == {
        'value': '223.5',
        'details': {
            'dryclean': '100',
            'test_reason_1': '123.5'
        },
        'created': datetime.datetime(2018, 11, 16, 10, 0)
    }

    assert send_doc.call
    assert not restore_mph_results.calls


@pytest.mark.now('2020-11-16 13:00:00+03')
@pytest.mark.filldb(parks='compensate_park')
@pytest.mark.config(BILLING_SUBVENTIONS_CHECK_MANUAL_SUBVENTION=True)
@pytest.mark.asyncenv('blocking')
def test_old_order_compensate_park(patch, load):
    @patch('taxi.internal.archive.restore_many_orders')
    @async.inline_callbacks
    def restore_orders(orders_ids, update=False, src_tvm_service=None,
                       log_extra=None):
        yield db.orders.insert(
            json.loads(
                load('restore_order.json'),
                object_hook=helpers.bson_object_hook
            )
        )

    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    response = django_test.Client().post(
        '/api/payments/compensate_park/',
        data=json.dumps({
            'order_id': 'compensate_order',
            'sum': 100,
            'reason': 'dryclean',
            'version': 1,
            'zendesk_ticket': '100001',
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
    response_content = json.loads(response.content)
    assert response_content['status'] == 'error'
    assert response_content['code'] == 'bad_request'
    assert response_content['message'] == 'Order is too old'


@pytest.mark.now('2018-11-16 13:00:00+03')
@pytest.mark.filldb(parks='compensate_park')
@pytest.mark.asyncenv('blocking')
def test_not_finished_order_error_compensate_park(patch, load):
    @patch('taxi.internal.archive.restore_many_orders')
    @async.inline_callbacks
    def restore_orders(orders_ids, update=False, src_tvm_service=None,
                       log_extra=None):
        yield db.orders.insert(
            json.loads(load('restore_not_finished_order.json'))
        )

    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    @patch('taxi.internal.park_manager.get_trust_status')
    @async.inline_callbacks
    def patch_donations(*args, **kwargs):
        yield
        async.return_value('init')

    response = django_test.Client().post(
        '/api/payments/compensate_park/',
        data=json.dumps({
            'order_id': 'compensate_not_finished_order',
            'sum': 100,
            'reason': 'dryclean',
            'version': 1,
            'zendesk_ticket': '100001',
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
    response_content = json.loads(response.content)
    assert response_content['status'] == 'error'
    assert response_content['code'] == 'order_must_be_finished'


@pytest.mark.config(
    BILLING_SUBVENTIONS_DISABLE_SUBVENTION_REASONS=True,
    MIN_DUE_TO_SEND_SUBVENTIONS_TO_BO='2016-02-01T00:00:00+00:00'
)
@pytest.mark.now('2018-11-16 13:00:00+03')
@pytest.mark.filldb(parks='compensate_park')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_compensate_park_without_subvention_reasons(patch, load):
    @patch('taxi.internal.archive.restore_many_orders')
    @async.inline_callbacks
    def restore_orders(orders_ids, update=False, src_tvm_service=None,
                       log_extra=None):
        yield db.orders.insert(
            json.loads(
                load('restore_order.json'),
                object_hook=helpers.bson_object_hook
            )
        )

    @patch('taxi.internal.archive.restore_many_mph_results')
    @async.inline_callbacks
    def restore_mph_results(orders_ids, update=False, src_tvm_service=None,
                            log_extra=None):
        yield db.mph_results.insert({'_id': 'compensate_order'})

    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    @patch('taxi.internal.park_manager.get_trust_status')
    @async.inline_callbacks
    def patch_donations(*args, **kwargs):
        yield
        async.return_value('init')

    @patch('taxi_stq.client.order_billing')
    def order_billing_task(order_id, reason, **kwargs):
        assert order_id == 'compensate_order'
        assert reason == 'dryclean'

    @patch('taxi.external.billing_orders.send_doc')
    def send_doc(kind, external_obj_id, external_event_ref, event_at, data,
                 reason, **kwargs):
        expected_doc = json.loads(load('expected_manual_subvention_doc_wo_sybvention_reasons.json'))
        assert kind == expected_doc['kind']
        assert external_obj_id == expected_doc['external_obj_id']
        assert external_event_ref == expected_doc['external_event_ref']
        assert event_at == expected_doc['event_at']

        expected_data = expected_doc['data']

        assert data['billing_contract_is_set'] == (
               expected_data['billing_contract_is_set'])

        if data['billing_contract_is_set']:
            assert sorted(data['billing_contract'].items()) == (
                sorted(expected_data['billing_contract'].items()))
            data.pop('billing_contract')
            expected_data.pop('billing_contract')

        assert sorted(data.items()) == sorted(expected_data.items())
        assert reason == expected_doc['reason']

    response = django_test.Client().post(
        '/api/payments/compensate_park/',
        data=json.dumps({
            'order_id': 'compensate_order',
            'sum': 100,
            'reason': 'dryclean',
            'version': 1,
            'zendesk_ticket': ' 100001\n\t',
        }),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert json.loads(response.content) == {}

    subvention_reason = yield db.subvention_reasons.find_one(
        {'order_id': 'compensate_order'}
    )

    assert not subvention_reason

    assert send_doc.call
    assert not restore_mph_results.calls


@pytest.mark.parametrize(
    'rebill_result,ticket_type,expected_status_code,expected_response', [
        (
            999,
            'chatterbox',
            200,
            {'doc': {'id': 999}}
        ),
        (
            999,
            'startrack',
            200,
            {'doc': {'id': 999}}
        ),
        (
            rebill.UnsupportedOrderError('some_code', 'some message'),
            'chatterbox',
            400,
            {
                'status': 'error',
                'code': 'some_code',
                'message': 'some message',
            }
        ),
        (
            rebill.NotFoundError(),
            'chatterbox',
            404,
            {
                'status': 'error',
                'code': 'not_found',
                'message': 'order with id some_order_id not found',
            }
        ),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_rebill_order(
        rebill_result,
        ticket_type,
        expected_status_code, expected_response,
        patch, load):
    @patch('taxi.internal.payment_kit.rebill.change_cost_and_rebill')
    def change_cost_and_rebill(
            order_id, cost_for_driver, ticket_type, ticket_id, log_extra=None):
        if isinstance(rebill_result, Exception):
            raise rebill_result
        return rebill_result

    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    response = django_test.Client().post(
        '/api/payments/rebill_order/',
        data=json.dumps({
            'order_id': 'some_order_id',
            'cost_for_driver': '300',
            'zendesk_ticket': '100001',
            'ticket_type': ticket_type,
        }),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code
    response_content = json.loads(response.content)
    assert response_content == expected_response


@pytest.mark.translations([
    ('order', 'subvention_bonus_reason.dryclean', 'ru', 'Химчистка'),
    ('order', 'subvention_bonus_reason.cashrunner', 'ru', 'Сбежал'),
])
@pytest.mark.asyncenv('blocking')
def test_compensation_reasons():
    response = django_test.Client().get('/api/payments/compensation_reasons/')
    assert response.status_code == 200
    assert json.loads(response.content) == {
        'reasons': [
            {'code': 'cashrunner', 'name': 'Сбежал'},
            {'code': 'dryclean', 'name': 'Химчистка'}
        ]
    }


@pytest.mark.filldb(
    orders='cardlocks',
    users='cardlocks',
    cards='cardlocks',
    user_phones='cardlocks',
    phonelocks='cardlocks',
    cardlocks='cardlocks',
    devicelocks='cardlocks',
)
@pytest.mark.parametrize('query_string,expected_code,expected_result', [
    ('', 400, None),
    ('?phone=%2B71112223344', 200, 'expected_cardlocks_1.json'),
    ('?yandex_uid=123456', 200, 'expected_cardlocks_1.json'),
    ('?yandex_uid=100000', 200, 'expected_cardlocks_2.json'),
    ('?phone=%2B79159801902', 200, 'expected_cardlocks_3.json')
])
@pytest.mark.asyncenv('blocking')
def test_get_lock_reasons(patch, load, query_string, expected_code, expected_result):
    _patch_cardlocks(patch)
    mock_cardstorage(patch)
    response = django_test.Client().get(
        '/api/payments/lock_reasons/{}'.format(query_string)
    )
    assert response.status_code == expected_code

    result = json.loads(response.content)
    if expected_code == 200:
        assert result == json.loads(load(expected_result))


@pytest.mark.filldb(
    orders='cardlocks',
    users='cardlocks',
    cards='cardlocks',
    user_phones='cardlocks',
    phonelocks='cardlocks',
    cardlocks='cardlocks',
    devicelocks='cardlocks',
)
@pytest.mark.asyncenv('blocking')
def test_unmark_user_as_debtor(patch):
    mock_cardstorage(patch)

    @patch('taxi.internal.archive.get_order_by_id_or_alias')
    @async.inline_callbacks
    def get_order_by_id_or_alias(id_or_alias, as_dbh=False, **kwargs):
        if id_or_alias == 'order_id_4':
            raise archive.NotFound
        doc = yield db.orders.find_one(id_or_alias)
        if as_dbh:
            doc = dbh.order_proc.Doc(doc)
        async.return_value(doc)

    _patch_cardlocks(patch)
    response = django_test.Client().post(
        '/api/payments/unmark_debtor/',
        json.dumps({
            'order_id': 'order_id_1'
        }),
        'application/json',
    )
    assert response.status_code == 200

    response = django_test.Client().post(
        '/api/payments/unmark_debtor/',
        json.dumps({
            'order_id': 'order_id_2'
        }),
        'application/json',
    )
    assert response.status_code == 200

    response = django_test.Client().post(
        '/api/payments/unmark_debtor/',
        json.dumps({
            'order_id': 'order_id_3'
        }),
        'application/json',
    )
    assert response.status_code == 200

    response = django_test.Client().post(
        '/api/payments/unmark_debtor/',
        json.dumps({
            'order_id': 'order_id_4'
        }),
        'application/json',
    )
    assert response.status_code == 200

    response = django_test.Client().post(
        '/api/payments/unmark_debtor/',
        json.dumps({
            'order_id': 'order_id_5'
        }),
        'application/json',
    )
    assert response.status_code == 200

    response = django_test.Client().get(
        '/api/payments/lock_reasons/?phone=%2B71112223344'
    )
    assert response.status_code == 200
    assert len(json.loads(response.content)['orders_info']) == 1


@pytest.mark.filldb(
    orders='cardlocks',
    users='cardlocks',
    cards='cardlocks',
    user_phones='cardlocks',
    phonelocks='cardlocks',
    cardlocks='cardlocks',
    devicelocks='cardlocks',
)
@pytest.mark.asyncenv('blocking')
def test_unmark_user_as_debtor_batch(patch):
    mock_cardstorage(patch)

    @patch('taxi.internal.archive.get_order_by_id_or_alias')
    @async.inline_callbacks
    def get_order_by_id_or_alias(id_or_alias, as_dbh=False, **kwargs):
        if id_or_alias == 'order_id_4':
            raise archive.NotFound
        doc = yield db.orders.find_one(id_or_alias)
        if as_dbh:
            doc = dbh.order_proc.Doc(doc)
        async.return_value(doc)

    _patch_cardlocks(patch)

    response = django_test.Client().post(
        '/api/payments/unmark_debtor/',
        json.dumps({
            'order_id': 'order_id_1',
            'order_id_list': [
                'order_id_2',
                'order_id_3',
            ]
        }),
        'application/json',
    )
    assert response.status_code == 200

    response = django_test.Client().post(
        '/api/payments/unmark_debtor/',
        json.dumps({
            'order_id_list': [
                'order_id_4',
                'order_id_5',
            ]
        }),
        'application/json',
    )
    assert response.status_code == 200

    response = django_test.Client().get(
        '/api/payments/lock_reasons/?phone=%2B71112223344'
    )
    assert response.status_code == 200
    assert len(json.loads(response.content)['orders_info']) == 1


@pytest.mark.parametrize('get_invoices_enabled,invoice_found', [
    (False, True),
    (True, False),
])
@pytest.mark.filldb(
    orders='test_get_orders_info',
    cities='test_get_orders_info',
    user_phones='test_get_orders_info',
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_no_is_refundable_flag(
        patch, get_invoices_enabled, invoice_found,
):
    yield config.ADMIN_GET_INVOICES.save(get_invoices_enabled)
    mock_cardstorage(patch)
    _experiments3_mock(patch)

    if not invoice_found:
        mock_invoice_not_found(patch)

    @patch('taxi.internal.archive.get_many_order_proc_by_ids')
    @async.inline_callbacks
    def get_many_order_proc_by_ids(ids, **kwargs):
        yield async.return_value([])

    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps({'order_id': 'order3'}),
        content_type='application/json'
    )
    request.time_storage = evlog.new_time_storage('')
    request.login = 'some_login'
    request.superuser = True
    request.groups = []
    response = payments.get_orders_info(request)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data['orders']) == 1
    response_order_info = response_data['orders'][0]
    assert 'is_refundable' not in response_order_info


@pytest.mark.parametrize('is_refundable', [
    False,
    True,
])
@pytest.mark.config(ADMIN_GET_INVOICES=True)
@pytest.mark.filldb(
    orders='test_get_orders_info',
    cities='test_get_orders_info',
    user_phones='test_get_orders_info',
)
@pytest.mark.usefixtures('search_orders_mock')
@pytest.mark.asyncenv('blocking')
def test_is_refundable_flag(patch, is_refundable):
    mock_cardstorage(patch)
    _experiments3_mock(patch)

    mock_invoice(patch, {'is_refundable': is_refundable})

    @patch('taxi.internal.archive.get_many_order_proc_by_ids')
    @async.inline_callbacks
    def get_many_order_proc_by_ids(ids, **kwargs):
        yield async.return_value([])

    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps({'order_id': 'order3'}),
        content_type='application/json'
    )
    request.time_storage = evlog.new_time_storage('')
    request.login = 'some_login'
    request.superuser = True
    request.groups = []
    response = payments.get_orders_info(request)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data['orders']) == 1
    response_order_info = response_data['orders'][0]
    assert response_order_info['is_refundable'] == is_refundable


@pytest.mark.now('2018-11-16 13:00:00+03')
@pytest.mark.filldb(
    parks='compensate_park',
    orders='test_cash_compensate_park',
    tariff_settings='test_cash_compensate_park',
)
@pytest.mark.config(BILLING_SUBVENTIONS_CHECK_MANUAL_SUBVENTION=True)
@pytest.mark.config(USE_TARIFF_SETTINGS_PAYMENT_LIMITS=True)
@pytest.mark.asyncenv('blocking')
def test_cash_compensate_park(patch, load):
    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield async.return_value((True, 'zendesk'))

    response = django_test.Client().post(
        '/api/payments/compensate_park/',
        data=json.dumps({
            'order_id': 'some_order_id',
            'sum': 101,
            'version': 1,
            'zendesk_ticket': '100001',
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
    response_content = json.loads(response.content)
    assert response_content['status'] == 'error'
    assert response_content['code'] == 'cash_compensation_forbidden'
    assert response_content['message'] == (
        'Cannot compensate ride for cash paid orders'
    )


@pytest.mark.now('2018-11-16 13:00:00+03')
@pytest.mark.filldb(
    parks='compensate_park',
    orders='test_too_small_compensation',
    tariff_settings='test_too_small_compensation',
)
@pytest.mark.config(BILLING_SUBVENTIONS_CHECK_MANUAL_SUBVENTION=True)
@pytest.mark.config(USE_TARIFF_SETTINGS_PAYMENT_LIMITS=True)
@pytest.mark.asyncenv('blocking')
def test_too_small_compensation(patch, load):
    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    response = django_test.Client().post(
        '/api/payments/compensate_park/',
        data=json.dumps({
            'order_id': 'some_order_id',
            'sum': 1.1,
            'version': 1,
            'zendesk_ticket': '100001',
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
    response_content = json.loads(response.content)
    assert response_content['status'] == 'error'
    assert response_content['code'] == 'invalid_compensation_sum'
    assert response_content['message'] == (
        'invalid compensation sum: net sum 0.0011 is effectively 0'
    )


@pytest.mark.now('2018-11-16 13:00:00+03')
@pytest.mark.filldb(
    parks='compensate_park',
    orders='test_bonus_limit',
    tariff_settings='test_too_small_compensation',
)
@pytest.mark.config(BILLING_SUBVENTIONS_CHECK_MANUAL_SUBVENTION=True)
@pytest.mark.config(USE_TARIFF_SETTINGS_PAYMENT_LIMITS=True)
@pytest.mark.config(MAX_SUBVENTION_BONUS_VALUE_BY_CURRENCY={'RUB': 10000})
@pytest.mark.asyncenv('blocking')
def test_raises_when_bonus_exceeds_limit(patch, load):
    @patch('taxi.internal.archive.restore_many_orders')
    @async.inline_callbacks
    def restore_orders(orders_ids, update=False, src_tvm_service=None,
                       log_extra=None):
        yield db.orders.insert(
            json.loads(
                load('restore_order.json'),
                object_hook=helpers.bson_object_hook
            )
        )

    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    response = django_test.Client().post(
        '/api/payments/compensate_park/',
        data=json.dumps({
            'order_id': 'some_order_id',
            'sum': 10000.1,
            'version': 1,
            'zendesk_ticket': '100001',
            'reason': 'dryclean',
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
    response_content = json.loads(response.content)
    assert response_content['status'] == 'error'
    assert response_content['code'] == 'invalid_bonus_value'
    assert response_content['message'] == 'Bonus value exceeds the limit'


@pytest.mark.now('2018-11-16 13:00:00+03')
@pytest.mark.filldb(
    parks='compensate_park',
    orders='test_bonus_limit',
    tariff_settings='test_too_small_compensation',
)
@pytest.mark.config(BILLING_SUBVENTIONS_CHECK_MANUAL_SUBVENTION=True)
@pytest.mark.config(USE_TARIFF_SETTINGS_PAYMENT_LIMITS=True)
@pytest.mark.config(MAX_SUBVENTION_BONUS_VALUE_BY_CURRENCY={})
@pytest.mark.asyncenv('blocking')
def test_raises_when_no_value_for_currency_is_set(patch, load):
    @patch('taxi.internal.archive.restore_many_orders')
    @async.inline_callbacks
    def restore_orders(orders_ids, update=False, src_tvm_service=None,
                       log_extra=None):
        yield db.orders.insert(
            json.loads(
                load('restore_order.json'),
                object_hook=helpers.bson_object_hook
            )
        )

    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    response = django_test.Client().post(
        '/api/payments/compensate_park/',
        data=json.dumps({
            'order_id': 'some_order_id',
            'sum': 10000.1,
            'version': 1,
            'zendesk_ticket': '100001',
            'reason': 'dryclean',
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
    response_content = json.loads(response.content)
    assert response_content['status'] == 'error'
    assert response_content['code'] == 'no_limit_for_currency'
    assert response_content['message'] == (
        'Limit for currency RUB is not set in config '
        'MAX_SUBVENTION_BONUS_VALUE_BY_CURRENCY'
    )


def _patch_cardlocks(patch):
    @patch('taxi.internal.archive.get_many_orders')
    @async.inline_callbacks
    def get_many_orders(ids, **kwargs):
        orders = yield db.orders.find({'_id': {'$in': ids}}).run()
        async.return_value(orders)

    @patch('taxi.internal.archive.get_many_order_proc_by_ids')
    @async.inline_callbacks
    def get_many_order_proc_by_ids(ids, as_dbh=False, **kwargs):
        yield
        docs = [{'_id': 'order_id_5'}]
        if as_dbh:
            docs = [dbh.order_proc.Doc(doc) for doc in docs]
        async.return_value(docs)

    @patch('taxi.internal.order_kit.payment_handler.is_nothing_to_hold_order')
    def is_nothing_to_hold_order(order):
        return order.pk not in ('order_id_5', 'order_id_6')


@pytest.mark.filldb(orders='back_to_card')
@pytest.mark.asyncenv('blocking')
def test_back_to_card(patch, monkeypatch, mock_send_event):

    @patch('taxiadmin.views.common.check_zendesk_ticket')
    @async.inline_callbacks
    def check_zendesk_ticket(*args, **kwargs):
        yield
        async.return_value((True, 'zendesk'))

    mock_cardstorage(patch)

    result = {}
    from taxi.core.db import classes as db_classes
    old_find_and_modify = db_classes.BaseCollectionWrapper.find_and_modify

    def mock_find_and_modify(self, query, update, *args, **kwargs):
        if self._collection_name == 'order_proc':
            result['query'] = query
            result['update'] = update
            return {'_id': 'order1'}
        else:
            return old_find_and_modify(self, query, update, *args, **kwargs)

    monkeypatch.setattr(
        db_classes.BaseCollectionWrapper, 'find_and_modify', mock_find_and_modify
    )

    response = django_test.Client().post(
        '/api/payments/back_to_card/',
        json.dumps({
            'order_id': 'order1',
            'zendesk_ticket': 'zd',
            'ticket_type': 'chatterbox',
        }),
        'application/json',
    )
    assert response.status_code == 200, response.content

    assert result['query'] == {
        '_id': 'order1',
        '_shard_id': 0,
        'order_info.statistics.status_updates': {
            '$not': {'$elemMatch': {'h': True, 'q': 'back_to_card'}}
        }
    }
    su = result['update']['$push']['order_info.statistics.status_updates']
    assert su.pop('x-idempotency-token') is not None
    assert result['update'] == {
        '$currentDate': {u'updated': True},
        '$inc': {'order.version': 1, 'processing.version': 1},
        '$push': {u'order_info.statistics.status_updates': {
            'a': {'card_info': {
                'main_card_billing_id': u'x1234',
                'main_card_payment_id': u'card-x1234',
                'main_card_persistent_id': u'deadbeef',
                'main_card_possible_moneyless': None}
            },
            'c': datetime.datetime.utcnow(),
            'h': True,
            'q': 'back_to_card'}
        },
        '$set': {
            'processing.need_start': True}
    }
