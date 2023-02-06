import copy
import datetime
import json
import urllib

from bson import ObjectId
from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import dbh
from taxi_maintenance.stuff import admin_confirmations

import test_taxiadmin_api_views_commissions as test_commissions


@pytest.mark.parametrize('code,type,data,expected', [
    (
        200, 'tariffs', {'offset': 1, 'limit': 1}, [
            {
                'status': 'need_approval',
                'doc_type': 'tariffs',
                'updated': '2016-04-08T13:00:00+0300',
                'created': '2016-04-08T13:02:00+0300',
                'approvals': [],
                'operation_type': 'update',
                'created_by': 'dmkurilov',
                'version': 1,
                'request_id': 'test_request_id_3',
                'new_doc': {
                    'home_zone': 'cheboksary_2',
                    'categories': [
                        {
                            'waiting_included': 5,
                            'waiting_price': 4,
                            'tariff_id':
                                'd2063bfb1f144149b0e3cd47bf6d73d9',
                            'dayoff': False,
                            'paid_dispatch_distance_price_intervals': [],
                            'currency': 'RUB',
                            'time_price_intervals': [
                                {
                                    'price': 0,
                                    'begin': 10
                                }
                            ],
                            'category_name': 'econom',
                            'category_type': 'application',
                            'paid_cancel_fix': 0,
                            'add_minimal_to_paid_cancel': True
                        }
                    ]
                },
                'id': 'confirmation_id_2',
                'description': 'test_description',
                'comment': ['test_comment'],
                'run_manually': True
            },
        ]
    ),
    (
        200, 'tariffs', {'zone': 'cheboksary'}, [
            {
                'status': 'need_approval',
                'doc_type': 'tariffs',
                'updated': '2016-04-08T13:00:00+0300',
                'created': '2016-04-08T13:01:00+0300',
                'approvals': [],
                'created_by': 'dmkurilov',
                'version': 1,
                'operation_type': 'update',
                'request_id': 'test_request_id_2',
                'new_doc': {
                    'home_zone': 'cheboksary',
                    'categories': [
                        {
                            'waiting_included': 5,
                            'waiting_price': 4,
                            'tariff_id':
                                'd2063bfb1f144149b0e3cd47bf6d73d9',
                            'dayoff': False,
                            'paid_dispatch_distance_price_intervals': [],
                            'currency': 'RUB',
                            'time_price_intervals': [
                                {
                                    'price': 0,
                                    'begin': 10
                                }
                            ],
                            'category_name': 'econom',
                            'category_type': 'application',
                            'paid_cancel_fix': 50,
                            'add_minimal_to_paid_cancel': False
                        }
                    ]
                },
                'id': 'confirmation_id_1',
                'description': 'test_description',
                'comment': ['test_comment'],
                'run_manually': True
            },
        ]
    ),
    (
        200, 'commissions', None, [
            {
                'comment': [],
                'doc_type': 'commissions',
                'updated': '2016-04-08T13:00:00+0300',
                'created': '2016-04-08T13:03:00+0300',
                'approvals': [],
                'operation_type': 'update',
                'new_doc': {
                    'commissions': [
                        {
                            'cancel_percent': '0.09',
                            'branding_discounts': [
                                {
                                    'marketing_level': [
                                        'sticker', 'co_branding', 'lightbox'
                                    ], 'value': '0.05'
                                }
                            ],
                            'park_cancel_min_td': 420,
                            'expired_percent': '0.11',
                            'max_order_cost': '6000',
                            'id': 'some_fixed_percent_commission_contract_id2',
                            'end': '2016-12-31T00:00:00',
                            'taximeter_payment': '0.08',
                            'zone': 'moscow',
                            'percent': '0.03',
                            'has_fixed_cancel_percent': True,
                            'min_order_cost': '1',
                            'billable_cancel_distance': 300,
                            'type': 'fixed_percent',
                            'vat': '1.18',
                            'expired_cost': '800',
                            'begin': '2016-10-30T19:23:00',
                            'agent_percent': '0.0001',
                            'callcenter_commission_percent': '0',
                            'user_cancel_min_td': 120,
                            'acquiring_percent': '0.02',
                            'payment_type': 'card',
                            'user_cancel_max_td': 600,
                            'park_cancel_max_td': 600,
                            'tariff_class': None,
                            'tag': None,
                        },
                        {
                            'cancel_percent': '0.09',
                            'branding_discounts': [
                                {
                                    'marketing_level': [
                                        'sticker', 'co_branding', 'lightbox'
                                    ],
                                    'value': '0.05'
                                }
                            ],
                            'park_cancel_min_td': 420,
                            'expired_percent': '0.11',
                            'max_order_cost': '6000',
                            'id': 'some_fixed_percent_commission_contract_id2',
                            'end': '2016-12-31T00:00:00',
                            'taximeter_payment': '0.08',
                            'zone': 'moscow',
                            'percent': '0.03',
                            'has_fixed_cancel_percent': True,
                            'min_order_cost': '1',
                            'billable_cancel_distance': 300,
                            'type': 'fixed_percent',
                            'vat': '1.18',
                            'expired_cost': '800',
                            'begin': '2016-10-30T19:23:00',
                            'agent_percent': '0.0001',
                            'callcenter_commission_percent': '0',
                            'user_cancel_min_td': 120,
                            'acquiring_percent': '0.02',
                            'payment_type': 'cash',
                            'user_cancel_max_td': 600,
                            'park_cancel_max_td': 600,
                            'tariff_class': None,
                            'tag': None,
                        }
                    ]
                },
                'created_by': 'dmkurilov',
                'version': 1,
                'status': 'approved',
                'request_id': 'test_request_id_18',
                'description': 'test_description',
                'id': 'confirmation_id_12',
                'run_manually': True
            },
            {
                'comment': [],
                'doc_type': 'commissions',
                'updated': '2016-04-08T13:00:00+0300',
                'created': '2016-04-08T13:03:00+0300',
                'approvals': [],
                'operation_type': 'update',
                'new_doc': {
                    'cancel_percent': '0.09',
                    'branding_discounts': [
                        {
                            'marketing_level': [
                                'sticker',
                                'co_branding',
                                'lightbox'
                            ],
                            'value': '0.05'
                        }
                    ],
                    'acquiring_percent': '0.02',
                    'expired_percent': '0.11',
                    'max_order_cost': '6000',
                    'id': 'some_fixed_percent_commission_contract_id',
                    'end': '2016-12-31T00:00:00',
                    'taximeter_payment': '0.08',
                    'callcenter_commission_percent': '0',
                    'percent': '0.03',
                    'has_fixed_cancel_percent': True,
                    'zone': 'moscow',
                    'expired_cost': '800',
                    'billable_cancel_distance': 300,
                    'type': 'fixed_percent',
                    'vat': '1.18',
                    'min_order_cost': '1',
                    'begin': '2016-10-30T19:23:00',
                    'agent_percent': '0.0001',
                    'user_cancel_min_td': 120,
                    'park_cancel_min_td': 420,
                    'payment_type': 'card',
                    'user_cancel_max_td': 600,
                    'park_cancel_max_td': 600,
                    'tariff_class': None,
                    'tag': None,
                },
                'created_by': 'dmkurilov',
                'version': 1,
                'status': 'approved',
                'request_id': 'test_request_id_8',
                'description': 'test_description',
                'id': 'confirmation_id_6',
                'run_manually': True
            }
        ]
    ),
    (
        200, 'subventions', None, [
            {
                'id': 'confirmation_id_8',
                'new_doc': {
                    'branding_type': None,
                    'geoareas': None,
                    'tags': None,
                    'category': 'econom',
                    'dayofweek': '5-7',
                    'dayridecount': '1-7',
                    'dayridecount_days': 3,
                    'dayridecount_is_for_any_category': False,
                    'display_in_taximeter': True,
                    'end': '2020-05-14 00:00 +0300',
                    'group_id': '',
                    'has_fake_counterpart': False,
                    'close_previous_rules': False,
                    'hour': '0-3',
                    'is_active': True,
                    'is_bonus': False,
                    'is_fake': False,
                    'is_once': False,
                    'log_count': 0,
                    'not_editable': False,
                    'soon_to_end': False,
                    'soon_to_start': False,
                    'paymenttype': 'cash',
                    'rule_sum': 140.0,
                    'rule_type': 'guarantee',
                    'start': '2019-06-13 00:00 +0300',
                    'sub_commission': True,
                    'tariffzone': 'cheboksary',
                    'tariffzone_localized': 'cheboksary'
                },
                'operation_type': 'create',
                'doc_type': 'subventions',
                'description': 'test_description',
                'comment': [],
                'request_id': 'test_request_id_14',
                'run_manually': True,
                'approvals': [],
                'created': '2016-04-08T13:05:00+0300',
                'created_by': 'dmkurilov',
                'status': 'need_approval',
                'updated': '2016-04-08T13:00:00+0300',
                'version': 1
            },
            {
                'id': 'confirmation_id_7',
                'new_doc': {
                    'branding_type': None,
                    'rule_id': '5a572ade7795ae12616fc08d',
                    'geoareas': None,
                    'tags': None,
                    'dayofweek': '5-7',
                    'dayridecount': '1-7',
                    'dayridecount_days': 3,
                    'dayridecount_is_for_any_category': False,
                    'close_previous_rules': False,
                    'display_in_taximeter': True,
                    'end': '2020-05-14 00:00 +0300',
                    'group_id': '',
                    'has_fake_counterpart': False,
                    'hour': '0-4',
                    'is_active': True,
                    'is_bonus': False,
                    'is_fake': False,
                    'is_once': False,
                    'log_count': 0,
                    'not_editable': False,
                    'soon_to_end': False,
                    'soon_to_start': False,
                    'paymenttype': 'card',
                    'rule_sum': 140.0,
                    'rule_type': 'guarantee',
                    'start': '2019-06-13 00:00 +0300',
                    'sub_commission': True,
                    'tariffzone': 'cheboksary',
                    'tariffzone_localized': 'cheboksary'
                },
                'operation_type': 'update',
                'doc_type': 'subventions',
                'description': 'test_description',
                'comment': [],
                'request_id': 'test_request_id_13',
                'run_manually': True,
                'approvals': [],
                'created': '2016-04-08T13:04:00+0300',
                'created_by': 'dmkurilov',
                'status': 'need_approval',
                'updated': '2016-04-08T13:00:00+0300',
                'version': 1
            },
        ]
    ),
    (
        200, 'subventions_payments', {'operation_type': 'create'},
        [{
            'id': 'confirmation_id_9',
            'new_doc': {
                'clid': 'test_clid',
                'date_from': '2016-04-08',
                'date_to': '2016-04-09'
            },
            'operation_type': 'create',
            'doc_type': 'subventions_payments',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_15',
            'run_manually': True,
            'approvals': [],
            'created': '2016-04-08T13:06:00+0300',
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': '2016-04-08T13:00:00+0300',
            'version': 1
        }]
    ),
    (
        200, 'tariffs', {'status': 'approved'},
        [{
            'id': 'confirmation_id_10',
            'new_doc': {
                'home_zone': 'cheboksary_2',
                'categories': [
                    {
                        'waiting_included': 6,
                        'paid_dispatch_distance_price_intervals': [],
                        'waiting_price': 4,
                        'tariff_id': 'd2063bfb1f144149b0e3cd47bf6d73d9',
                        'currency': 'RUB',
                        'dayoff': False,
                        'time_price_intervals': [
                            {
                                'price': 0,
                                'begin': 10
                            }
                        ],
                        'category_name': 'econom',
                        'category_type': 'application',
                        'paid_cancel_fix': 0,
                        'add_minimal_to_paid_cancel': True
                    }
                ]
            },
            'operation_type': 'update',
            'description': 'test_description',
            'doc_type': 'tariffs',
            'comment': ['test_comment'],
            'request_id': 'test_request_id_16',
            'run_manually': True,
            'approvals': [],
            'created': '2016-04-08T13:07:00+0300',
            'created_by': 'dmkurilov',
            'status': 'approved',
            'updated': '2016-04-08T13:00:00+0300',
            'version': 1
        }]
    ),
    (
        200, 'subventions_payments', {'operation_type': 'bulk_create'},
        [{
            'id': 'confirmation_id_11',
            'new_doc': {
                'mds_file_id': 'test_mds_file_id',
                'mds_file_url': 'https://tc-tst.mobile.yandex.net/static/'
                                'test-images/test_mds_file_id',
                'planned_currency_sums': {
                    'RUB': '33.5566',
                    'AMD': '555.67688909'
                },
                'reason': 'covid-19_compensation',
            },
            'operation_type': 'bulk_create',
            'doc_type': 'subventions_payments',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_17',
            'run_manually': True,
            'approvals': [],
            'created': '2016-04-08T13:08:00+0300',
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': '2016-04-08T13:00:00+0300',
            'version': 1
        }]
    ),
    (
        200, 'subventions_payments', {'operation_type': 'bulk_create'},
        [{
            'id': 'confirmation_id_11',
            'new_doc': {
                'mds_file_id': 'test_mds_file_id',
                'mds_file_url': 'https://tc-tst.mobile.yandex.net/static/'
                                'test-images/test_mds_file_id',
                'planned_currency_sums': {
                    'RUB': '33.5566',
                    'AMD': '555.67688909'
                },
                'reason': 'covid-19_compensation',
            },
            'operation_type': 'bulk_create',
            'doc_type': 'subventions_payments',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_17',
            'run_manually': True,
            'approvals': [],
            'created': '2016-04-08T13:08:00+0300',
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': '2016-04-08T13:00:00+0300',
            'version': 1
        }]
    ),
])
@pytest.mark.config(
    IMAGES_URL_TEMPLATE='https://tc-tst.mobile.yandex.net'
                        '/static/test-images/{}')
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(admin_confirmations='get_list')
@pytest.mark.now('2020-01-01 03:00:00+03')
def test_get_confirmations_list(code, type, data, expected):
    if data:
        url = '/api/confirmations/list/?type=%s&%s' % (
            type, urllib.urlencode(data)
        )
    else:
        url = '/api/confirmations/list/?type=%s' % type
    response = django_test.Client().get(url)
    assert response.status_code == code
    if code == 200:
        response_data = json.loads(response.content)
        assert response_data == expected


BASE_DATA_FIELDS_1 = {
    'dayridecount': [[1, 7]],
    'is_once': False,
    'sub_commission': True,
    'is_bonus': False,
    'category': ['econom'],
    'dayridecount_is_for_any_category': False,
    'end': datetime.datetime(2017, 6, 13, 18, 0),
    'dayridecount_days': 3,
    'is_fake': False,
    'start': datetime.datetime(2017, 6, 12, 18, 0),
    'close_previous_rules': False,
    'branding_type': None,
    'ticket': 'TAXIRATE-ticket',
    'rule_type': 'guarantee',
    'has_fake_counterpart': False,
    'display_in_taximeter': True,
    'paymenttype': 'cash',
    'geoareas': [],
    'tags': [],
    'group_id': '',
    'currency': 'RUB',
}
BASE_DATA_FIELDS_2 = {
    'dayridecount': [],
    'is_once': False,
    'sub_commission': True,
    'is_bonus': False,
    'category': ['econom'],
    'end': datetime.datetime(2017, 6, 13, 18, 0),
    'is_fake': False,
    'start': datetime.datetime(2017, 6, 12, 18, 0),
    'close_previous_rules': False,
    'branding_type': None,
    'ticket': 'TAXIRATE-ticket',
    'rule_type': 'guarantee',
    'has_fake_counterpart': False,
    'display_in_taximeter': True,
    'paymenttype': 'cash',
    'geoareas': [],
    'tags': [],
    'group_id': '',
    'currency': 'RUB',
}
BASE_DATA_FIELDS_3 = {
    'dayridecount': [[1]],
    'is_once': False,
    'sub_commission': True,
    'is_bonus': False,
    'category': ['econom'],
    'dayridecount_is_for_any_category': False,
    'end': datetime.datetime(2017, 6, 13, 18, 0),
    'dayridecount_days': 3,
    'is_fake': False,
    'start': datetime.datetime(2017, 6, 12, 18, 0),
    'close_previous_rules': False,
    'branding_type': None,
    'ticket': 'TAXIRATE-ticket',
    'rule_type': 'guarantee',
    'has_fake_counterpart': False,
    'display_in_taximeter': True,
    'paymenttype': 'cash',
    'geoareas': [],
    'tags': [],
    'group_id': '',
    'currency': 'RUB',
}


def _make_subvention_expected_data(
        base_fields, categories, tariff_zones, date_info,
        geoareas_lists
):
    sub_rules = []
    for geoareas in geoareas_lists:
        for category in categories:
            for tariff_zone in tariff_zones:
                for item in date_info:
                    sub_data = copy.copy(base_fields)
                    sub_data['category'] = [category]
                    sub_data['tariffzone'] = [tariff_zone]
                    sub_data['dayofweek'] = item['dayofweek']
                    sub_data['hour'] = item['hour']
                    sub_data['geoareas'] = geoareas
                    sub_data['rule_sum'] = item['rule_sum']
                    sub_rules.append(sub_data)
    return {
        'subvention_rules': sub_rules,
        'ticket': base_fields['ticket']
    }


@pytest.mark.skipif(
    True,
    reason='Admin confirmations are obsolete, use approvals instead'
)
@pytest.mark.parametrize('data,code,expected', [
    (
        {'description': 'test_description'}, 400, None
    ),
    (
        {
            'new_doc': {
                'activation_zone': 'moscow',
                'home_zone': 'cheboksary',
                'categories': [
                    {
                        'category_name': 'vip',
                        'time_from': '00:00',
                        'time_to': '23:59',
                        'name_key': 'interval.24h',
                        'day_type': 2,
                        'currency': 'RUR',
                        'minimal': 42,
                        'waiting_price': 4,
                        'pddpi': [],
                        'name': 'econom',
                        'dayoff': False,
                        'tpi': [{'p': 0, 'b': 10}],
                        'waiting': 5,
                        'id': 'd2063bfb1f144149b0e3cd47bf6d73d9',
                        'paid_cancel_fix': 0,
                        'add_minimal_to_paid_cancel': True,
                    }
                ]
            },
            'operation_type': 'update',
            'doc_type': 'tariffs',
            'description': 'test_description',
            'request_id': 'test_request_id_1',
            'run_manually': True
        }, 409, None
    ),
    (
        {
            'new_doc': {
                'activation_zone': 'moscow',
                'home_zone': 'test_zone_id',
                'date_from': '2017-6-11T16:26:52.6',
                'categories': [
                    {
                        'category_name': 'vip',
                        'time_from': '00:00',
                        'time_to': '23:59',
                        'name_key': 'interval.24h',
                        'day_type': 2,
                        'currency': 'RUR',
                        'minimal': 42,
                        'waiting_price': 4,
                        'paid_dispatch_distance_price_intervals': [],
                        'dayoff': False,
                        'time_price_intervals': [{'price': 0, 'begin': 10}],
                        'waiting': 5,
                        'id': 'd2063bfb1f144149b0e3cd47bf6d73d9',
                        'paid_cancel_fix': 0,
                        'add_minimal_to_paid_cancel': True,
                    }
                ]
            },
            'operation_type': 'update',
            'doc_type': 'tariffs',
            'description': 'test_description',
            'request_id': 'test_request_id_1',
            'run_manually': True
        }, 200,
        {
            'new_doc': {
                'p': '__mrt',
                'activation_zone': 'moscow',
                'home_zone': 'test_zone_id',
                'date_from': '2017-6-11T16:26:52.6',
                'categories': [
                    {
                        'waiting_price': 4,
                        'name': 'vip',
                        'currency': 'RUR',
                        'to_time': '23:59',
                        'name_key': 'interval.24h',
                        'dt': 2,
                        'from_time': '00:00',
                        'minimal': 42,
                        'pddpi': [],
                        'tpi': [{'p': 0, 'b': 10}],
                        'paid_cancel_fix': 0,
                        'add_minimal_to_paid_cancel': True,
                    }
                ]
            },
            'operation_type': 'update',
            'change_doc_id': 'tariffs_test_zone_id',
            'doc_type': 'tariffs',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_1',
            'run_manually': True,
            'approvals': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'version': 1
        }
    ),
    (
        {
            'new_doc': {},
            'description': 'test_description',
            'request_id': 'test_request_id_1',
            'run_manually': True
        }, 400, None
    ),
    (
        {
            'new_doc': {
                'zone': 'moscow',
                'ticket': 'TAXIRATE-ticket',
                'begin': '2016-10-30T19:23:00',
                'agent_percent': '0.0001',
                'branding_discounts': [
                    {
                        'marketing_level': [
                            'lightbox', 'co_branding', 'sticker'
                        ],
                        'value': '0.05'
                    }
                ],
                'cancel_percent': '0.09',
                'acquiring_percent': '0.02',
                'expired_percent': '0.11',
                'expired_cost': '800',
                'max_order_cost': '6000',
                'end': '2016-12-31T00:00:00',
                'taximeter_payment': '0.08',
                'callcenter_commission_percent': '0',
                'percent': '0.03',
                'has_fixed_cancel_percent': True,
                'payment_type': 'card',
                'type': 'fixed_percent',
                'vat': '1.18',
                'min_order_cost': '1',
            },
            'via_taxirate': True,
            'doc_type': 'commissions',
            'operation_type': 'create',
            'description': 'test_description',
            'request_id': 'test_request_id_7',
            'run_manually': False
        }, 200,
        {
            'new_doc': {
                'document': {
                    'b': datetime.datetime(2016, 10, 30, 16, 23),
                    'bv': {
                        'bcd': 300,
                        'p_max': 600,
                        'p_min': 420,
                        'u_max': 600,
                        'u_min': 120
                    },
                    'cm': {
                        'acp': 200,
                        'agp': 1,
                        'bd': [
                            {
                                'marketing_level': [
                                    'lightbox', 'co_branding', 'sticker'
                                ],
                                'value': 500
                            }
                        ],
                        'cp': 900,
                        'd': {},
                        'ec': 8000000,
                        'ep': 1100,
                        'hacp': True,
                        'has_fixed_cancel_percent': True,
                        'hc': True,
                        'max': 60000000,
                        'min': 10000,
                        'p': 300,
                        't': 'fixed_percent',
                        'taximeter_payment': 800,
                        'callcenter_commission_percent': 0,
                        'vat': 11800,
                        'hiring': {
                            'extra_percent': 200,
                            'extra_percent_with_rent': 400,
                            'max_age_in_seconds': 15552000
                        }
                    },
                    'cn': {'p': 'card', 'z': 'moscow'},
                    'e': datetime.datetime(2016, 12, 30, 21, 0),
                    'updated': datetime.datetime(2016, 4, 8, 10, 0),
                },
                'ticket': 'TAXIRATE-ticket'
            },
            'via_taxirate': True,
            'doc_type': 'commissions',
            'operation_type': 'create',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_7',
            'run_manually': True,
            'approvals': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'created_by': 'dmkurilov',
            'status': 'approved',
            'updated': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'version': 1
        }
    ),
    (
        {
            'new_doc': {
                'id': 'some_fixed_percent_commission_contract_id'
            },
            'doc_type': 'commissions',
            'operation_type': 'delete',
            'description': 'test_description',
            'request_id': 'test_request_id_9',
            'run_manually': False
        }, 200,
        {
            'new_doc': {
                'b': datetime.datetime(2016, 12, 31, 21, 0, 0),
                'e': datetime.datetime(2017, 12, 31, 21, 0, 0),
                'cn': {
                    'p': 'cash',
                    'z': 'moscow'
                },
                'cm': {
                    'bd': [],
                    'has_fixed_cancel_percent': False,
                    'd': {},
                    'min': 0,
                    'max': 60000000,
                    'hacp': True,
                    'ec': 8000000,
                    'p': 1100,
                    'acp': 200,
                    't': 'fixed_percent',
                    'hc': True,
                    'cp': 1100,
                    'ep': 1100,
                    'vat': 11800,
                    'taximeter_payment': 10000,
                    'callcenter_commission_percent': 0,
                    'agp': 1,
                    'hiring': {
                        'extra_percent': 200,
                        'extra_percent_with_rent': 400,
                        'max_age_in_seconds': 15552000
                    }
                },
                'bv': {
                    'bcd': 300,
                    'u_min': 120,
                    'u_max': 600,
                    'p_min': 420,
                    'p_max': 600
                }
            },
            'change_doc_id': 'commissions_some_fixed_percent_commission_'
                             'contract_id_moscow_cash_all',
            'doc_type': 'commissions',
            'operation_type': 'delete',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_9',
            'run_manually': False,
            'approvals': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'version': 1
        }
    ),
    (
        {
            'new_doc': {
                'discounts': [
                    {
                        'num_rides_for_newbies': 1,
                        'round_digits': 2,
                        'final_min_value': 0.01,
                        'for': 'all',
                        'calculation_formula_v1_threshold': 600,
                        'newbie_max_coeff': 1.5,
                        'final_max_value': 0.99,
                        'max_value': 0.35,
                        'current_method': 'full-driver-less',
                        'enabled': True,
                        'min_value': 0.01,
                        'random_p': 0,
                        'random_time_threshold': 4,
                        'random_s': 0,
                        'payment_types': [
                            'card',
                            'applepay',
                            'googlepay',
                            'cash'
                        ],
                        'calculation_method': 'formula',
                        'calculation_formula_v1_p2': 35,
                        'calculation_formula_v1_a2': 0,
                        'calculation_formula_v1_a1': 0,
                        'calculation_formula_v1_c1': 100,
                        'calculation_formula_v1_c2': 100,
                        'classes': [
                            'econom'
                        ],
                        'newbie_num_coeff': 0.15,
                        'calculation_formula_v1_p1': 35,
                        'id': '000000000000000000000001'
                    }
                ],
                'enabled': True,
                'zone': 'cheboksary',
                'ticket': 'TAXIRATE-334'
            },
            'operation_type': 'create',
            'doc_type': 'user_discounts',
            'description': 'test_description',
            'request_id': 'test_request_id_fresh',
            'run_manually': True
        }, 200,
        {
            'new_doc': {
                'discounts':
                    [{
                        'classes': ['econom'],
                        'current_method': 'full-driver-less',
                        'enabled': True,
                        'final_max_value': 0.99,
                        'final_min_value': 0.01,
                        'for': 'all',
                        'calculation_method': 'formula',
                        'calculation_formula_v1_a1': 0,
                        'calculation_formula_v1_a2': 0,
                        'calculation_formula_v1_c1': 100,
                        'calculation_formula_v1_c2': 100,
                        'calculation_formula_v1_p1': 35,
                        'calculation_formula_v1_p2': 35,
                        'calculation_formula_v1_threshold': 600,
                        'max_value': 0.35,
                        'min_value': 0.01,
                        'newbie_max_coeff': 1.5,
                        'newbie_num_coeff': 0.15,
                        'num_rides_for_newbies': 1,
                        'payment_types': [
                            'card',
                            'applepay',
                            'googlepay',
                            'cash'
                        ],
                        'random_p': 0,
                        'random_s': 0,
                        'random_time_threshold': 4,
                        'round_digits': 2,
                        'id': '000000000000000000000001'
                    }],
                'enabled': True,
                'ticket': 'TAXIRATE-334'
            },
            'operation_type': 'create',
            'change_doc_id': 'user_discounts_cheboksary',
            'doc_type': 'user_discounts',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_fresh',
            'run_manually': True,
            'approvals': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'version': 1
        }
    ),
    (
        {
            'new_doc': {
                'zone': 'novocheboksarsk',
                'version': 1
            },
            'operation_type': 'delete',
            'doc_type': 'user_discounts',
            'description': 'test_description',
            'request_id': 'test_request_id_fresh',
            'run_manually': False
        }, 200,
        {
            'new_doc': {
                'version': 1
            },
            'operation_type': 'delete',
            'change_doc_id': 'user_discounts_novocheboksarsk',
            'doc_type': 'user_discounts',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_fresh',
            'run_manually': False,
            'approvals': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'version': 1
        }
    ),
    (
        {
            'new_doc': {
                'ticket': 'test_ticket',
                'dayofweek': '5,6,7',
                'dayridecount_days': 3,
                'geoareas': [],
                'tags': '',
                'category': 'econom',
                'start': '2017-6-12 21:00:00',
                'rule_type': 'guarantee',
                'rule_sum': 140.0,
                'tariffzone': 'cheboksary',
                'hour': '0-3',
                'dayridecount': '1-7',
                'paymenttype': 'cash',
                'is_fake': False,
                'has_fake_counterpart': False,
                'sub_commission': True,
                'is_bonus': False,
                'branding_type': None,
                'is_once': False
            },
            'operation_type': 'create',
            'doc_type': 'subventions',
            'description': 'test_description',
            'request_id': 'test_request_id_fresh',
            'run_manually': True
        }, 406, None
    ),
    (
        {
            'new_doc': {
                'ticket': 'test_ticket',
                'dayofweek': '5,6,7',
                'dayridecount_days': 3,
                'region': 'msc',
                'geoareas': [],
                'tags': '',
                'category': 'econom',
                'start': '2017-6-12 21:00:00',
                'rule_type': 'guarantee',
                'rule_sum': 140.0,
                'tariffzone': 'cheboksary',
                'hour': '0-3',
                'dayridecount': '1-',
                'paymenttype': 'cash',
                'is_fake': False,
                'has_fake_counterpart': False,
                'sub_commission': True,
                'is_bonus': False,
                'branding_type': None,
                'is_once': False
            },
            'operation_type': 'create',
            'doc_type': 'subventions',
            'description': 'test_description',
            'request_id': 'test_request_id_fresh',
            'run_manually': True
        }, 406, None
    ),
    (
        {
            'new_doc': {
                'ticket': 'test_ticket',
                'dayofweek': '5,6,7',
                'dayridecount_days': 3,
                'region': 'msc',
                'geoareas': [],
                'tags': '',
                'category': 'econom',
                'start': '2017-6-12 21:00:00',
                'end': '2017-6-13 21:00:00',
                'rule_type': 'guarantee',
                'rule_sum': 140.0,
                'tariffzone': 'cheboksary',
                'hour': '0-3',
                'dayridecount': '1-',
                'paymenttype': 'cash',
                'is_fake': False,
                'has_fake_counterpart': False,
                'sub_commission': True,
                'is_bonus': False,
                'branding_type': None,
                'is_once': False
            },
            'operation_type': 'create',
            'doc_type': 'subventions',
            'description': 'test_description',
            'request_id': 'test_request_id_fresh',
            'run_manually': True
        }, 200,
        {
            'new_doc': {
                'ticket': 'test_ticket',
                'branding_type': None,
                'category': ['econom'],
                'close_previous_rules': False,
                'currency': 'RUB',
                'dayofweek': [5, 6, 7],
                'dayridecount': [[1]],
                'dayridecount_days': 3,
                'dayridecount_is_for_any_category': False,
                'display_in_taximeter': True,
                'end': datetime.datetime(2017, 6, 13, 18, 0),
                'group_id': '',
                'has_fake_counterpart': False,
                'hour': [0, 1, 2, 3],
                'is_bonus': False,
                'is_fake': False,
                'is_once': False,
                'paymenttype': 'cash',
                'geoareas': [],
                'tags': [],
                'rule_sum': 140.0,
                'rule_type': 'guarantee',
                'start': datetime.datetime(2017, 6, 12, 18, 0),
                'sub_commission': True,
                'tariffzone': ['cheboksary']
            },
            'operation_type': 'create',
            'doc_type': 'subventions',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_fresh',
            'run_manually': True,
            'approvals': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'version': 1
        }
    ),
    (
        {
            'new_doc': {
                'ticket': 'test_ticket',
                'rule_id': '5a572ade7795ae12616fc08d',
                'dayofweek': '5,6,7',
                'dayridecount_days': 3,
                'start': '2017-6-12 21:00:00',
                'rule_type': 'guarantee',
                'rule_sum': 140.0,
                'tariffzone': 'cheboksary',
                'hour': '0-4',
                'dayridecount': '1-7',
                'paymenttype': 'card',
                'is_fake': False,
                'has_fake_counterpart': False,
                'sub_commission': True,
                'is_bonus': False,
                'branding_type': None,
                'is_once': False
            },
            'operation_type': 'update',
            'doc_type': 'subventions',
            'description': 'test_description',
            'request_id': 'test_request_id_13',
            'run_manually': True
        }, 406, None
    ),
    (
        {
            'new_doc': {
                'ticket': 'test_ticket',
                'rule_id': '5a572ade7795ae12616fc08d',
                'dayofweek': '5,6,7',
                'dayridecount_days': 3,
                'start': '2017-6-12 21:00:00',
                'end': '2017-6-13 21:00:00',
                'rule_type': 'guarantee',
                'rule_sum': 140.0,
                'tariffzone': 'cheboksary',
                'hour': '0-4',
                'dayridecount': '1-',
                'paymenttype': 'card',
                'is_fake': False,
                'has_fake_counterpart': False,
                'sub_commission': True,
                'is_bonus': False,
                'branding_type': None,
                'is_once': False
            },
            'operation_type': 'update',
            'doc_type': 'subventions',
            'description': 'test_description',
            'request_id': 'test_request_id_13',
            'run_manually': True
        }, 200,
        {
            'new_doc': {
                'cleaned_data': {
                    'rule_id': '5a572ade7795ae12616fc08d',
                    'category': ['econom'],
                    'currency': 'RUB',
                    'geoareas': [],
                    'tags': [],
                    'branding_type': None,
                    'close_previous_rules': False,
                    'dayofweek': [5, 6, 7],
                    'dayridecount': [[1]],
                    'dayridecount_days': 3,
                    'dayridecount_is_for_any_category': False,
                    'display_in_taximeter': True,
                    'end': datetime.datetime(2017, 6, 13, 18, 0),
                    'group_id': '',
                    'has_fake_counterpart': False,
                    'hour': [0, 1, 2, 3, 4],
                    'is_bonus': False,
                    'is_fake': False,
                    'is_once': False,
                    'paymenttype': 'card',
                    'ticket': 'test_ticket',
                    'rule_sum': 140.0,
                    'rule_type': 'guarantee',
                    'start': datetime.datetime(2017, 6, 12, 18, 0),
                    'sub_commission': True,
                    'tariffzone': ['cheboksary']
                },
                'rule': {
                    '_id': ObjectId('5a572ade7795ae12616fc08d'),
                    'branding_type': None,
                    'class': ['econom'],
                    'dayofweek': [5, 6, 7],
                    'dayridecount': [[1, 7]],
                    'dayridecount_days': 3,
                    'dayridecount_is_for_any_category': False,
                    'display_in_taximeter': True,
                    'end': datetime.datetime(2017, 6, 13, 18, 0),
                    'group_id': '',
                    'has_fake_counterpart': False,
                    'hour': [0, 1, 2, 3],
                    'is_bonus': False,
                    'is_fake': False,
                    'is_once': False,
                    'paymenttype': 'cash',
                    'geoareas': None,
                    'tags': None,
                    'sum': 140.0,
                    'type': 'guarantee',
                    'start': datetime.datetime(2017, 6, 12, 18, 0),
                    'sub_commission': True,
                    'tariffzone': ['cheboksary']
                },
                'skip_fields': [
                    'category',
                    'close_previous_rules',
                    'ticket',
                    'rule_id'
                ],
            },
            'operation_type': 'update',
            'doc_type': 'subventions',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_13',
            'run_manually': True,
            'approvals': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'version': 1
        }
    ),
    (
        {
            'new_doc': {
                'clid': 'park1',
                'date_from': '2016-04-08',
                'date_to': '2016-04-09'
            },
            'operation_type': 'create',
            'doc_type': 'subventions_payments',
            'description': 'test_description',
            'request_id': 'test_request_id_16',
            'run_manually': True
        }, 200,
        {
            'new_doc': {
                'clid': 'park1',
                'date_from': '2016-04-08',
                'date_to': '2016-04-09'
            },
            'operation_type': 'create',
            'change_doc_id': 'subvention_payments_park1',
            'doc_type': 'subventions_payments',
            'description': 'test_description',
            'comment': [],
            'request_id': 'test_request_id_16',
            'run_manually': True,
            'approvals': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': datetime.datetime(2016, 4, 8, 10, 0, 0),
            'version': 1
        }
    ),
    (
        {
            'new_doc': {
                'file_name': 'bulk_subventions_payments_data.csv'
            },
            'operation_type': 'bulk_create',
            'doc_type': 'subventions_payments',
            'description': 'test_description',
            'request_id': 'test_request_id_16',
            'run_manually': True
        }, 200,
        {
            'approvals': [],
            'comment': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0),
            'created_by': 'dmkurilov',
            'description': 'test_description',
            'doc_type': 'subventions_payments',
            'new_doc': {
                'mds_file_id': 'bulk_subventions_payments_data.csv',
                'planned_currency_sums': {
                    'RUB': '123',
                    'USD': '234324',
                    'AMD': '23321.69'
                }
            },
            'operation_type': 'bulk_create',
            'request_id': 'test_request_id_16',
            'run_manually': True,
            'status': 'need_approval',
            'updated': datetime.datetime(2016, 4, 8, 10, 0),
            'version': 1
        }
    ),
    (
        {
            'new_doc': {
                'tariff_zones': ['cheboksary', 'moscow'],
                'sums_by_days_hours': [
                    {
                        'days': '1-3,5',
                        'hours': '2-12,23',
                        'sum': 123
                    },
                    {
                        'days': '1-2,4-5',
                        'hours': '2-11,22-23',
                        'sum': 28
                    }
                ],
                'categories': ['econom', 'vip'],
                'geoareas_lists': [
                    ['shakhty'],
                    []
                ],
                'ticket': 'TAXIRATE-ticket',
                'dayridecount_days': 3,
                'region': 'msc',
                'geoareas': [],
                'tags': '',
                'category': 'econom',
                'start': '2017-6-12 21:00:00',
                'end': '2017-6-13 21:00:00',
                'rule_type': 'guarantee',
                'dayridecount': '',
                'paymenttype': 'cash',
                'is_fake': False,
                'has_fake_counterpart': False,
                'sub_commission': True,
                'is_bonus': False,
                'branding_type': None,
                'is_once': False,
            },
            'via_taxirate': True,
            'operation_type': 'bulk_create',
            'doc_type': 'subventions',
            'description': 'test_description',
            'request_id': 'test_request_id_16',
            'run_manually': True
        }, 200,
        {
            'approvals': [],
            'comment': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0),
            'created_by': 'dmkurilov',
            'description': 'test_description',
            'doc_type': 'subventions',
            'new_doc': _make_subvention_expected_data(
                BASE_DATA_FIELDS_2,
                ['econom', 'vip'],
                ['cheboksary', 'moscow'],
                [
                    {
                        'dayofweek': [1, 2, 3, 5],
                        'hour': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 23],
                        'rule_sum': 123
                    },
                    {
                        'dayofweek': [1, 2, 4, 5],
                        'hour': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 22, 23],
                        'rule_sum': 28
                    }
                ],
                [['shakhty'], []]
            ),
            'operation_type': 'bulk_create',
            'request_id': 'test_request_id_16',
            'run_manually': True,
            'via_taxirate': True,
            'status': 'approved',
            'updated': datetime.datetime(2016, 4, 8, 10, 0),
            'version': 1
        }
    ),
    (
        {
            "description": 'test_description',
            "via_taxirate": True,
            "operation_type": "create",
            "doc_type": "commissions",
            "run_manually": True,
            "new_doc": {
                "user_cancel_min_td": 120,
                "billable_cancel_distance": 300,
                "park_cancel_min_td": 420,
                "user_cancel_max_td": 600,
                "park_cancel_max_td": 600,
                "acquiring_percent": "0.02",
                "min_order_cost": "1",
                "max_order_cost": "6000",
                "agent_percent": "0.01",
                "zones": ["cheboksary", "moscow"],
                "cancel_percent": "0.09",
                "branding_discounts": [{
                    "marketing_level": ["sticker", "co_branding", "lightbox"],
                    "value":"0.03"
                }, {
                    "marketing_level": ["sticker", "lightbox"],
                    "value":"0.04"
                }],
                "expired_percent": "0.11",
                "end": "2020-11-02T00:00:00",
                "taximeter_payment": "0.08",
                "percent": "0.03",
                "has_fixed_cancel_percent": True,
                "type": "fixed_percent",
                "vat": "1.18",
                "expired_cost": "800",
                "begin": "2019-12-23T10:00:00",
                "callcenter_commission_percent": "0",
                "tariff_classes": [],
                "payment_types": ["card", "corp"],
                "ticket": "TAXIRATE-ticket"
            },
            "request_id":"test_request_id_7"
        }, 200,
        {
            'comment': [],
            'status': 'approved',
            'updated': datetime.datetime(2016, 4, 8, 10, 0),
            'description': 'test_description',
            'run_manually': True,
            'approvals': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0),
            'created_by': 'dmkurilov',
            'doc_type': 'commissions',
            'version': 1,
            'request_id': 'test_request_id_7',
            'operation_type': 'create',
            'new_doc': {
                'ticket': 'TAXIRATE-ticket',
                'document': [{
                    'updated': datetime.datetime(2016, 4, 8, 10, 0),
                    'b': datetime.datetime(2019, 12, 23, 7, 0),
                    'e': datetime.datetime(2020, 11, 1, 21, 0),
                    'cn': {'p': 'card', 'z': 'cheboksary'},
                    'cm': {
                        'bd': [{
                            'marketing_level': [
                                'sticker', 'co_branding', 'lightbox'
                            ],
                            'value': 300
                        }, {
                            'marketing_level': [
                                'sticker', 'lightbox'
                            ],
                            'value': 400
                        }],
                        'agp': 100,
                        'p': 300,
                        'd': {},
                        'min': 10000,
                        'max': 60000000,
                        'callcenter_commission_percent': 0,
                        'hacp': True,
                        'ec': 8000000,
                        't': 'fixed_percent',
                        'hiring': {
                            'max_age_in_seconds': 15552000,
                            'extra_percent': 200,
                            'extra_percent_with_rent': 400,
                        },
                        'acp': 200,
                        'has_fixed_cancel_percent': True,
                        'hc': True,
                        'cp': 900,
                        'ep': 1100,
                        'vat': 11800,
                        'taximeter_payment': 800
                    },
                    'bv': {
                        'bcd': 300,
                        'u_min': 120,
                        'p_min': 420,
                        'p_max': 600,
                        'u_max': 600
                    }
                }, {
                    'updated': datetime.datetime(2016, 4, 8, 10, 0),
                    'b': datetime.datetime(2019, 12, 23, 7, 0),
                    'e': datetime.datetime(2020, 11, 1, 21, 0),
                    'cn': {'p': 'card', 'z': 'moscow'},
                    'cm': {
                        'bd': [{
                            'marketing_level': [
                                'sticker', 'co_branding', 'lightbox'
                            ],
                            'value': 300
                        }, {
                            'marketing_level': [
                                'sticker', 'lightbox'
                            ],
                            'value': 400
                        }],
                        'agp': 100,
                        'p': 300,
                        'd': {},
                        'min': 10000,
                        'max': 60000000,
                        'callcenter_commission_percent': 0,
                        'hacp': True,
                        'ec': 8000000,
                        't': 'fixed_percent',
                        'hiring': {
                            'max_age_in_seconds': 15552000,
                            'extra_percent': 200,
                            'extra_percent_with_rent': 400,
                        },
                        'acp': 200,
                        'has_fixed_cancel_percent': True,
                        'hc': True,
                        'cp': 900,
                        'ep': 1100,
                        'vat': 11800,
                        'taximeter_payment': 800
                    },
                    'bv': {
                        'bcd': 300,
                        'u_min': 120,
                        'p_min': 420,
                        'p_max': 600,
                        'u_max': 600
                    }
                }, {
                    'updated': datetime.datetime(2016, 4, 8, 10, 0),
                    'b': datetime.datetime(2019, 12, 23, 7, 0),
                    'e': datetime.datetime(2020, 11, 1, 21, 0),
                    'cn': {'p': 'corp', 'z': 'cheboksary'},
                    'cm': {
                        'bd': [{
                            'marketing_level': [
                                'sticker', 'co_branding', 'lightbox'
                            ],
                            'value': 300
                        }, {
                            'marketing_level': [
                                'sticker', 'lightbox'
                            ],
                            'value': 400
                        }],
                        'agp': 100,
                        'p': 300,
                        'd': {},
                        'min': 10000,
                        'max': 60000000,
                        'callcenter_commission_percent': 0,
                        'hacp': True,
                        'ec': 8000000,
                        't': 'fixed_percent',
                        'hiring': {
                            'max_age_in_seconds': 15552000,
                            'extra_percent': 200,
                            'extra_percent_with_rent': 400,
                        },
                        'acp': 200,
                        'has_fixed_cancel_percent': True,
                        'hc': True,
                        'cp': 900,
                        'ep': 1100,
                        'vat': 11800,
                        'taximeter_payment': 800
                    },
                    'bv': {
                        'bcd': 300,
                        'u_min': 120,
                        'p_min': 420,
                        'p_max': 600,
                        'u_max': 600
                    }
                }, {
                    'updated': datetime.datetime(2016, 4, 8, 10, 0),
                    'b': datetime.datetime(2019, 12, 23, 7, 0),
                    'e': datetime.datetime(2020, 11, 1, 21, 0),
                    'cn': {'p': 'corp', 'z': 'moscow'},
                    'cm': {
                        'bd': [{
                            'marketing_level': [
                                'sticker', 'co_branding', 'lightbox'
                            ],
                            'value': 300
                        }, {
                            'marketing_level': [
                                'sticker', 'lightbox'
                            ],
                            'value': 400
                        }],
                        'agp': 100,
                        'p': 300,
                        'd': {},
                        'min': 10000,
                        'max': 60000000,
                        'callcenter_commission_percent': 0,
                        'hacp': True,
                        'ec': 8000000,
                        't': 'fixed_percent',
                        'hiring': {
                            'max_age_in_seconds': 15552000,
                            'extra_percent': 200,
                            'extra_percent_with_rent': 400,
                        },
                        'acp': 200,
                        'has_fixed_cancel_percent': True,
                        'hc': True,
                        'cp': 900,
                        'ep': 1100,
                        'vat': 11800,
                        'taximeter_payment': 800
                    },
                    'bv': {
                        'bcd': 300,
                        'u_min': 120,
                        'p_min': 420,
                        'p_max': 600,
                        'u_max': 600
                    }
                }]
            },
            'via_taxirate': True
        }
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-04-08 13:00:00+03')
@pytest.mark.config(
    COUNTRY_DATE_WITH_ONLY_AUTOMATE_DONATIONS={
        'rus': '2015-08-01'
    }
)
@pytest.inline_callbacks
def test_create_confirmation(open_file, data, code, expected, patch):
    @patch('taxiadmin.audit.check_ticket')
    @async.inline_callbacks
    def check_ticket(ticket_key, login, component=None, unique_ticket=False):
        yield

    @patch('taxiadmin.tariff_checks.check_tariff')
    @async.inline_callbacks
    def check_tariff(tariff, tariff_settings, log_extra=None):
        yield

    @patch('taxi.external.mds.upload')
    @async.inline_callbacks
    def upload(
        image_file, namespace=None, key_suffix=None,
        headers=None, retry_on_fails=True, log_extra=None
    ):
        yield
        async.return_value(file_name)

    @patch('taxi.external.mds.download')
    @async.inline_callbacks
    def download(
            path, range_start=None, range_end=None,
            namespace=None, log_extra=None
    ):
        yield
        with open_file(file_name) as fp:
            async.return_value(fp.read())

    @patch('taxi.internal.archive.get_many_orders')
    @async.inline_callbacks
    def get_many_orders(ids, log_extra=None):
        result = []
        for order_id in ids:
            if order_id in ['test_order_id_4', 'test_order_id_5']:
                result.append({
                    '_id': order_id,
                    'performer': {
                        'tariff': {
                            'currency': 'AMD'
                        }
                    }
                })
            else:
                result.append((yield db.orders.find_one({'_id': order_id})))
        async.return_value(result)

    @patch('taxi.internal.archive.get_order')
    @async.inline_callbacks
    def get_order(order_id, lookup_yt=True, log_extra=None):
        yield
        if order_id in ['test_order_id_4', 'test_order_id_5']:
            async.return_value({
                '_id': order_id,
                'performer': {
                    'tariff': {
                        'currency': 'AMD'
                    }
                }
            })
        else:
            async.return_value((yield db.orders.find_one({'_id': order_id})))

    @patch('taxi.internal.startrack.get_ticket_author_and_manager')
    @async.inline_callbacks
    def get_ticket_author_and_manager(ticket):
        yield async.return_value(('mvpetrov', 'chadeeva'))

    @patch('taxi.internal.startrack.create_comment')
    @async.inline_callbacks
    def create_comment(ticket, body, summonees=None):
        assert summonees == ['mvpetrov', 'chadeeva']
        yield

    @patch('taxi.external.startrack.get_ticket_info')
    @async.inline_callbacks
    def get_ticket_info(ticket):
        yield async.return_value({
            'status': {'key': 'approved'}
        })

    @patch('taxiadmin.audit.get_last_approver')
    @async.inline_callbacks
    def get_last_approver(ticket, approve_statuses):
        yield async.return_value(('mvpetrov', 'random_date'))

    confirmation_with_file = False
    if data.get('new_doc') and 'file_name' in data['new_doc']:
        file_name = data['new_doc'].pop('file_name')
        with open_file(file_name) as fp:
            response = django_test.Client().post(
                '/api/subventions/prepare_payments/', {'orders': fp}
            )
            data['new_doc']['mds_file_id'] = file_name
            response = django_test.Client().post(
                '/api/confirmations/create/', json.dumps(data),
                'application/json'
            )
        confirmation_with_file = True
    else:
        response = django_test.Client().post(
            '/api/confirmations/create/', json.dumps(data), 'application/json'
        )

    response_data = json.loads(response.content)

    assert response.status_code == code, response_data
    if code == 200:
        response_data = json.loads(response.content)
        result = yield db.admin_confirmations.find_one({
            '_id': response_data['id']})

        result.pop('_id')
        if data['doc_type'] == 'subventions' or confirmation_with_file:
            result.pop('change_doc_id')
        if (data['doc_type'] == 'commissions' and
                data['operation_type'] != 'delete'):
            result.pop('change_doc_id')
            result['new_doc'].pop('current_document')
            if isinstance(result['new_doc']['document'], dict):
                result['new_doc']['document'].pop('_id')
            else:
                for item in result['new_doc']['document']:
                    item.pop('_id')
        result['new_doc'].pop('_id', None)
        assert result == expected


@pytest.mark.parametrize('method,confirmation_id,code,expected', [
    (
        'GET', 'confirmation_id_1', 200,
        {
            'id': 'confirmation_id_1',
            'new_doc': {
                'home_zone': 'cheboksary',
                'categories': [
                    {
                        'waiting_included': 5,
                        'waiting_price': 4,
                        'tariff_id': 'd2063bfb1f144149b0e3cd47bf6d73d9',
                        'dayoff': False,
                        'paid_dispatch_distance_price_intervals': [],
                        'currency': 'RUB',
                        'time_price_intervals': [
                            {
                                'price': 0,
                                'begin': 10
                            }
                        ],
                        'category_name': 'econom',
                        'category_type': 'application',
                        'paid_cancel_fix': 50,
                        'add_minimal_to_paid_cancel': False,
                    }
                ]
            },
            'operation_type': 'update',
            'doc_type': 'tariffs',
            'request_id': 'test_request_id_2',
            'description': 'test_description',
            'comment': ['test_comment'],
            'run_manually': True,
            'approvals': [],
            'created': '2016-04-08T13:00:00+0300',
            'created_by': 'dmkurilov',
            'status': 'need_approval',
            'updated': '2016-04-08T13:00:00+0300',
            'version': 1
        }
    ),
    (
        'DELETE', 'confirmation_id_1', 200, None
    ),
    (
        'GET', 'confirmation_id_8', 200,
        {
            'id': 'confirmation_id_8',
            'operation_type': 'update',
            'new_doc': {
                'discounts': [
                    {
                        'num_rides_for_newbies': 1,
                        'round_digits': 2,
                        'final_min_value': 0.01,
                        'for': 'all',
                        'calculation_formula_v1_threshold': 600,
                        'newbie_max_coeff': 1.5,
                        'final_max_value': 0.99,
                        'max_value': 0.35,
                        'current_method': 'full-driver-less',
                        'enabled': True,
                        'min_value': 0.01,
                        'random_p': 0,
                        'random_time_threshold': 5,
                        'random_s': 0,
                        'payment_types': [
                            'card',
                            'applepay',
                            'googlepay',
                            'cash'
                        ],
                        'calculation_method': 'formula',
                        'calculation_formula_v1_p2': 35,
                        'calculation_formula_v1_a2': 0,
                        'calculation_formula_v1_a1': 0,
                        'calculation_formula_v1_c1': 100,
                        'calculation_formula_v1_c2': 100,
                        'classes': [
                            'econom'
                        ],
                        'newbie_num_coeff': 0.15,
                        'calculation_formula_v1_p1': 35,
                        'id': '000000000000000000000001'
                    }
                ],
                'version': 1,
                'enabled': True,
                'zone': 'novocheboksarsk',
                'zone_type': 'tariff_zone'
    },
            'doc_type': 'user_discounts',
            'request_id': 'test_request_id_11',
            'description': 'test_description',
            'comment': ['test_comment'],
            'run_manually': False,
            'approvals': [
                {
                    'login': 'test_name',
                    'created': '2016-04-08T13:00:00+0300',
                    'group': 'financier'
                }
            ],
            'created': '2016-04-08T13:00:00+0300',
            'created_by': 'asd',
            'status': 'need_approval',
            'updated': '2016-04-08T13:00:00+0300',
            'version': 1
        }
    ),
    (
        'GET', 'confirmation_id_9', 200,
        {
            'id': 'confirmation_id_9',
            'operation_type': 'delete',
            'new_doc': {
                'zone': 'novocheboksarsk',
                'zone_type': 'tariff_zone',
                'version': 1
            },
            'doc_type': 'user_discounts',
            'request_id': 'test_request_id_12',
            'description': 'test_description',
            'comment': ['test_comment'],
            'run_manually': False,
            'approvals': [
                {
                    'login': 'test_name',
                    'created': '2016-04-08T13:00:00+0300',
                    'group': 'manager'
                }
            ],
            'created': '2016-04-08T13:00:00+0300',
            'created_by': 'asd',
            'status': 'need_approval',
            'updated': '2016-04-08T13:00:00+0300',
            'version': 1
        }
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-04-08 13:00:00+03')
@pytest.inline_callbacks
def test_get_confirmation_or_delete(method, confirmation_id, code,
                                    expected):
    if method == 'DELETE':
        response = django_test.Client().delete(
            '/api/confirmations/%s/' % confirmation_id)
    else:
        response = django_test.Client().get(
            '/api/confirmations/%s/' % confirmation_id)

    assert response.status_code == code
    if method == 'GET':
        assert json.loads(response.content) == expected
    else:
        result = yield db.admin_confirmations.find_one(
            {'_id': confirmation_id})
        assert result is None


@pytest.inline_callbacks
def _check_tariffs(expected_doc):
    old_doc = yield db.tariffs.find_one({
        '_id': ObjectId('56d857346334f815640ab5ec')
    })
    assert old_doc['date_to'] == datetime.datetime(2016, 4, 8, 10)
    new_doc = yield db.tariffs.find_one({
        '_id': {'$ne': ObjectId('56d857346334f815640ab5ec')},
        'home_zone': expected_doc['home_zone']
    })
    new_doc.pop('_id')
    for category in new_doc['categories']:
        category.pop('id')
    assert new_doc == expected_doc


@pytest.inline_callbacks
def _check_user_discounts(expected_doc):
    new_doc = yield db.user_discounts.find_one({
        'zone_name': 'novocheboksarsk',
        'zone_type': 'tariff_zone'
    })
    assert new_doc == expected_doc


@pytest.mark.parametrize(
    'method,confirmation_id,code,check_method,expected_confirmation,'
    'expected_doc',
    [
        (
            'PUT', 'confirmation_id_2', 200, _check_tariffs,
            {
                '_id': 'confirmation_id_2',
                'request_id': 'test_request_id_3',
                'description': 'test_description',
                'run_manually': True,
                'new_doc': {
                    'home_zone': 'cheboksary'
                },
                'operation_type': 'update',
                'apply_time': datetime.datetime(2016, 4, 7, 13, 0),
                'approvals': [
                    {
                        'login': 'test_name',
                        'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
                        'group': 'financier'
                    },
                    {
                        'login': 'dmkurilov',
                        'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
                        'group': 'manager'
                    }
                ],
                'doc_type': 'tariffs',
                'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
                'created_by': 'asd',
                'comment': ['test_comment'],
                'status': 'approved',
                'updated': datetime.datetime(2016, 4, 8, 13, 0, 0),
                'version': 2
            }, None
        ),
        (
            'PUT', 'confirmation_id_3', 200, _check_tariffs,
            {
                '_id': 'confirmation_id_3',
                'comment': ['test_comment'],
                'request_id': 'test_request_id_4',
                'run_manually': False,
                'doc_type': 'tariffs',
                'description': 'test_description',
                'operation_type': 'update',
                'new_doc': {
                    'updated': datetime.datetime(
                        2017, 7, 11, 16, 26, 52, 600000),
                    'rz': ['cheboksary'],
                    'p': '__mrt',
                    'home_zone': 'cheboksary',
                    'categories': [
                        {
                            'waiting_price': 4,
                            'pddpi': [],
                            'name': 'econom',
                            'dayoff': False,
                            'tpi': [{'p': 0, 'b': 10}],
                            'currency': 'RUB',
                            'waiting': 5,
                            'id': 'e64420ac6e394df7950d433c9e12c692'
                        },
                        {
                            'waiting_price': 4,
                            'pddpi': [],
                            'name': 'vip',
                            'dayoff': False,
                            'tpi': [{'p': 0, 'b': 10}],
                            'currency': 'RUB',
                            'waiting': 5,
                            'id': 'b06176ca80984544b1efc13c91be07d1'
                        }
                    ]
                },
                'apply_time': datetime.datetime(2016, 4, 7, 13, 0),
                'approvals': [
                    {
                        'login': 'test_name',
                        'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
                        'group': 'financier'
                    },
                    {
                        'login': 'dmkurilov',
                        'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
                        'group': 'manager'
                    }
                ],
                'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
                'created_by': 'asd',
                'status': 'succeeded',
                'updated': datetime.datetime(2016, 4, 8, 13, 0, 0),
                'version': 4
            },
            {
                'updated': datetime.datetime(2016, 4, 8, 10, 0, 0),
                'date_from': datetime.datetime(2016, 4, 8, 10, 0, 0),
                'rz': ['cheboksary'],
                'p': '__mrt',
                'confirmation_id': 'confirmation_id_3',
                'home_zone': 'cheboksary',
                'categories': [
                    {
                        'waiting_price': 4,
                        'pddpi': [],
                        'name': 'econom',
                        'dayoff': False,
                        'tpi': [{'p': 0, 'b': 10}],
                        'currency': 'RUB',
                        'waiting': 5,
                        'category_type': 'application'
                    },
                    {
                        'waiting_price': 4,
                        'pddpi': [],
                        'name': 'vip',
                        'dayoff': False,
                        'tpi': [{'p': 0, 'b': 10}],
                        'currency': 'RUB',
                        'waiting': 5,
                        'category_type': 'application'
                    }
                ]
            }
        ),
        (
            'DELETE', 'confirmation_id_4', 200, None,
            {
                '_id': 'confirmation_id_4',
                'comment': ['test_comment'],
                'request_id': 'test_request_id_5',
                'run_manually': True,
                'description': 'test_description',
                'new_doc': {
                    'home_zone': 'cheboksary'
                },
                'operation_type': 'update',
                'approvals': [],
                'doc_type': 'tariffs',
                'created': datetime.datetime(2016, 4, 8, 10, 0, 0),
                'created_by': 'asd',
                'status': 'need_approval',
                'updated': datetime.datetime(2016, 4, 8, 13, 0, 0),
                'version': 2
            }, None
        ),
        (
            'PUT', 'confirmation_id_8', 200, _check_user_discounts,
            None,
            {
                'discounts': [
                    {
                        'num_rides_for_newbies': 1,
                        'round_digits': 2,
                        'final_min_value': 0.01,
                        'for': 'all',
                        'calculation_formula_v1_threshold': 600,
                        'newbie_max_coeff': 1.5,
                        'final_max_value': 0.99,
                        'max_value': 0.35,
                        'current_method': 'full-driver-less',
                        'enabled': True,
                        'min_value': 0.01,
                        'random_p': 0,
                        'random_time_threshold': 5,
                        'random_s': 0,
                        'payment_types': [
                            'card',
                            'applepay',
                            'googlepay',
                            'cash'
                        ],
                        'calculation_method': 'formula',
                        'calculation_formula_v1_p2': 35,
                        'calculation_formula_v1_a2': 0,
                        'calculation_formula_v1_a1': 0,
                        'calculation_formula_v1_c1': 100,
                        'calculation_formula_v1_c2': 100,
                        'classes': [
                            'econom'
                        ],
                        'history': [{
                            'login': 'asd',
                            'ticket': 'TAXIRATE-334',
                            'updated': datetime.datetime(2016, 4, 8, 10, 0)
                        }],
                        'newbie_num_coeff': 0.15,
                        'calculation_formula_v1_p1': 35,
                        'id': '000000000000000000000001'
                    }
                ],
                '_id': ObjectId('123456789012345678901234'),
                'zone_name': 'novocheboksarsk',
                'zone_type': 'tariff_zone',
                'enabled': True,
                'version': 2,
                'confirmation_id': 'confirmation_id_8'
            }
        )
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-04-08 13:00:00+03')
@pytest.mark.config(
    ADMIN_CONFIRMATIONS_NUM_APPROVALS=2,
)
@pytest.inline_callbacks
def test_approve_or_delete_approval(method, confirmation_id, code,
                                    check_method, expected_confirmation,
                                    expected_doc):
    if method == 'DELETE':
        response = django_test.Client().delete(
            '/api/confirmations/%s/approval/' % confirmation_id)
    else:
        response = django_test.Client().put(
            '/api/confirmations/%s/approval/' % confirmation_id)

    assert response.status_code == code
    yield db.admin_confirmations.update(
        {
            '_id': confirmation_id,
            dbh.admin_confirmations.Doc.status: 'approved'
        },
        {'$set': {
            dbh.admin_confirmations.Doc.apply_time:
                datetime.datetime(2016, 4, 7, 13, 0, 0)
        }}
    )
    yield admin_confirmations.do_stuff()
    result = yield db.admin_confirmations.find_one({'_id': confirmation_id})
    if expected_confirmation is not None:
        assert result == expected_confirmation
    if method == 'PUT':
        if not result['run_manually']:
            yield check_method(expected_doc)


@pytest.inline_callbacks
def _check_tariffs_manual(
        confirmation_id, json_response, expected, delete_ids
):
        confirmation_doc = yield db.admin_confirmations.find_one({
            '_id': confirmation_id})
        assert confirmation_doc['status'] == 'succeeded'

        assert db.tariffs.count().result == 3
        tariff_doc = yield db.tariffs.find_one({
            'home_zone': expected['home_zone'],
            'date_to': {'$exists': False}
        })
        tariff_doc.pop('_id')
        tariff_doc['categories'][0].pop('id')
        assert tariff_doc == expected


@pytest.inline_callbacks
def _check_commissions_manual(confirmation_id, json_response, id, delete_ids):
    confirmation_doc = yield db.admin_confirmations.find_one({
        '_id': confirmation_id})
    assert confirmation_doc['status'] == 'succeeded'

    if confirmation_doc['operation_type'] == 'update':
        expected = test_commissions._FIXED_PERCENT_DATA._replace(id=id)
        yield test_commissions.check_response(json_response, expected)
        commission_doc = yield db.commission_contracts.find_one({'_id': id})
        assert commission_doc['confirmation_id'] == confirmation_id + '_1'
    else:
        deleted_contract = yield db.commission_contracts.find_one({'_id': id})
        assert deleted_contract is None
        contract = yield dbh.commission_contracts.Doc.find_one_by_id(
            delete_ids[0])
        contract_2 = yield dbh.commission_contracts.Doc.find_one_by_id(
            delete_ids[1])
        assert contract.end == contract_2.begin


@pytest.inline_callbacks
def _check_subventions_manual(
        confirmation_id, json_response, expected, delete_ids
):
    confirmation_doc = yield db.admin_confirmations.find_one({
        '_id': confirmation_id})
    assert confirmation_doc['status'] == 'succeeded'
    if confirmation_doc['operation_type'] == 'update':
        updated_subvention = yield db.subvention_rules.find_one({
            '_id': ObjectId('5a572ade7795ae12616fc08d')
        })

        assert updated_subvention == expected
    else:
        created_subvention = yield db.subvention_rules.find_one({
            'paymenttype': 'card',
        })

        created_subvention.pop('_id')
        group_member_id = created_subvention.pop('group_member_id')
        assert group_member_id
        assert group_member_id == created_subvention['log'][-1].pop(
            'group_member_id')
        assert created_subvention == expected


@pytest.inline_callbacks
def _check_bulk_subventions_payments_manual(
        confirmation_id, json_response, expected, delete_ids
):
    conf = yield db.admin_confirmations.find_one({'_id': confirmation_id})
    reason = conf['new_doc'].get(
        'reason', dbh.subvention_reasons.BULK_BONUS_PAY_REASON
    )
    if len(expected['failed']) == 0:
        assert conf['status'] == dbh.admin_confirmations.SUCCEEDED_STATUS
    else:
        assert (
            conf['status'] ==
            dbh.admin_confirmations.PARTIALLY_SUCCEEDED_STATUS
        )
    for order_id in expected['succeed']:
        doc = yield db.orders.find_one({'_id': order_id})
        assert doc is not None
        doc = yield db.subvention_reasons.find_one({'order_id': order_id})
        assert doc is not None
        details = doc['subvention_bonus'][-1]['details']
        assert reason in details
        doc = yield db.mph_results.find_one({'_id': order_id})
        assert doc is None
    assert expected['failed_details'] == conf['new_doc']['failed_details']
    expected_texts = expected['text'].split('\n', 1)
    assert (expected_texts[0] == '%s;Subvention reason with order_id not found'
            % expected['failed'][0])
    assert (expected_texts[1] == '%s;Order is too old'
            % expected['failed'][1])


def _check_subvention(subvention):
    if dbh.subventions.Doc.comment in subvention:
        assert subvention.comment != {}
    if dbh.subventions.Doc.pool_subvention in subvention:
        assert subvention.pool_subvention != '{}'


def _bulk_bonus_test_case(confirmation_id):
    return (
        confirmation_id,
        200, _check_bulk_subventions_payments_manual,
        {
            'succeed': [
                'test_order_id_2',
                'test_order_id_4'
            ],
            'failed': [
                'test_order_id_5',
                'test_order_id_1',
            ],
            'failed_details': 'test_mds_id',
        }, None
    )


@pytest.mark.filldb(
    commission_contracts='for_delete',
)
@pytest.mark.parametrize(
    'confirmation_id,code,check_method,expected,delete_ids', [
        (
            'confirmation_id_5', 200,
            _check_tariffs_manual,
            {
                'updated': datetime.datetime(2016, 4, 8, 10),
                'date_from': datetime.datetime(2016, 4, 8, 10, 0),
                'rz': ['cheboksary'],
                'p': '__mrt',
                'confirmation_id': 'confirmation_id_5',
                'home_zone': 'cheboksary',
                'categories': [
                    {
                        'waiting_price': 4,
                        'pddpi': [],
                        'name': 'vip',
                        'dayoff': False,
                        'tpi': [{'p': 0, 'b': 10}],
                        'currency': 'RUB',
                        'waiting': 5,
                        'category_type': 'application',
                    }
                ]
            }, None
        ),
        (
            'confirmation_id_6', 200, _check_commissions_manual,
            'some_fixed_percent_commission_contract_id', None
        ),
        (
            'confirmation_id_7', 200, _check_commissions_manual,
            'contract_id_middle',
            ['contract_id_first', 'contract_id_last']
        ),
        (
            'confirmation_id_10', 200, _check_subventions_manual,
            {
                'confirmation_id': 'confirmation_id_10',
                'branding_type': None,
                'class': ['econom'],
                'dayofweek': [5, 6, 7],
                'dayridecount': [[1, 7]],
                'dayridecount_days': 3,
                'dayridecount_is_for_any_category': False,
                'display_in_taximeter': True,
                'end': datetime.datetime(2017, 6, 13, 18, 0),
                'group_id': 'cbe84b95f77d0c0c93967fce0a13a89cfb32e24a',
                'has_fake_counterpart': False,
                'hour': [0, 1, 2, 3],
                'log': [{
                    'branding_type': None,
                    'class': ['econom'],
                    'confirmation_id': 'confirmation_id_10',
                    'dayofweek': [5, 6, 7],
                    'dayridecount': [[1, 7]],
                    'dayridecount_days': 3,
                    'dayridecount_is_for_any_category': False,
                    'display_in_taximeter': True,
                    'end': datetime.datetime(2017, 6, 13, 18, 0),
                    'group_id': 'cbe84b95f77d0c0c93967fce0a13a89cfb32e24a',
                    'has_fake_counterpart': False,
                    'hour': [0, 1, 2, 3],
                    'is_bonus': False,
                    'is_fake': False,
                    'is_once': False,
                    'login': 'dmkurilov',
                    'paymenttype': 'card',
                    'geoareas': None,
                    'tags': None,
                    'start': datetime.datetime(2017, 6, 12, 18, 0),
                    'sub_commission': True,
                    'sum': 140.0,
                    'tariffzone': ['cheboksary'],
                    'ticket': 'test_ticket',
                    'type': 'guarantee',
                    'updated': datetime.datetime(2016, 4, 8, 10, 0)
                }],
                'is_bonus': False,
                'updated': datetime.datetime(2016, 4, 8, 13, 0),
                'is_fake': False,
                'is_once': False,
                'paymenttype': 'card',
                'geoareas': None,
                'tags': None,
                'sum': 140.0,
                'type': 'guarantee',
                'start': datetime.datetime(2017, 6, 12, 18, 0),
                'sub_commission': True,
                'tariffzone': ['cheboksary']
            }, None
        ),
        (
            'confirmation_id_11', 200, _check_subventions_manual,
            {
                '_id': ObjectId('5a572ade7795ae12616fc08d'),
                'confirmation_id': 'confirmation_id_11',
                'branding_type': None,
                'class': ['econom'],
                'dayofweek': [5, 6, 7],
                'dayridecount': [[1, 7]],
                'dayridecount_days': 3,
                'dayridecount_is_for_any_category': False,
                'display_in_taximeter': True,
                'end': datetime.datetime(2017, 6, 13, 18, 0),
                'group_id': '078196b13dc0ad1499215c7949f0fba0afdbd9f1',
                'group_member_id': '5a572ade7795ae12616fc08d',
                'has_fake_counterpart': False,
                'hour': [0, 1, 2, 3, 4],
                'log': [{
                    'branding_type': None,
                    'confirmation_id': 'confirmation_id_11',
                    'dayofweek': [5, 6, 7],
                    'dayridecount': [[1, 7]],
                    'dayridecount_days': 3,
                    'dayridecount_is_for_any_category': False,
                    'display_in_taximeter': True,
                    'end': datetime.datetime(2017, 6, 13, 18, 0),
                    'group_id': '078196b13dc0ad1499215c7949f0fba0afdbd9f1',
                    'group_member_id': '5a572ade7795ae12616fc08d',
                    'has_fake_counterpart': False,
                    'hour': [0, 1, 2, 3, 4],
                    'is_bonus': False,
                    'is_fake': False,
                    'is_once': False,
                    'ticket': 'test_ticket',
                    'login': 'dmkurilov',
                    'paymenttype': 'card',
                    'start': datetime.datetime(2017, 6, 12, 18, 0),
                    'sub_commission': True,
                    'sum': 140.0,
                    'tags': None,
                    'tariffzone': ['cheboksary'],
                    'type': 'guarantee',
                    'updated': datetime.datetime(2016, 4, 8, 10, 0)
                }],
                'is_bonus': False,
                'updated': datetime.datetime(2016, 4, 8, 13, 0),
                'is_fake': False,
                'is_once': False,
                'paymenttype': 'card',
                'geoareas': None,
                'tags': None,
                'sum': 140.0,
                'type': 'guarantee',
                'start': datetime.datetime(2017, 6, 12, 18, 0),
                'sub_commission': True,
                'tariffzone': ['cheboksary']
            }, None
        ),
        _bulk_bonus_test_case('confirmation_id_14'),
        _bulk_bonus_test_case('confirmation_id_17'),
        _bulk_bonus_test_case('confirmation_id_18'),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-04-08 13:00:00+03')
@pytest.mark.config(
    ADMIN_CONFIRMATIONS_NUM_APPROVALS=1,
    SUBVENTIONS_PAYMENTS_STEP=2,
    SUBVENTIONS_PAYMENTS_CREATE_NEW_DOC=True,
    BILLING_SUBVENTIONS_CHECK_MANUAL_SUBVENTION=True,
    MIN_DUE_TO_SEND_SUBVENTIONS_TO_BO='2016-02-01T00:00:00+00:00',
)
@pytest.inline_callbacks
def test_manual_apply(open_file, confirmation_id, code, check_method, expected,
                      delete_ids, patch):
    @patch('taxiadmin.audit.check_ticket')
    @async.inline_callbacks
    def check_ticket(ticket_key, login, component=None, unique_ticket=False):
        yield

    @patch('taxi.external.mds.download')
    @async.inline_callbacks
    def download(
        path, range_start=None, range_end=None, namespace=None, log_extra=None
    ):
        yield
        with open_file(path) as fp:
            async.return_value(fp.read())

    @patch('taxi.external.mds.upload')
    @async.inline_callbacks
    def upload(
            image_file, namespace=None, key_suffix=None,
            headers=None, retry_on_fails=True, log_extra=None
    ):
        yield
        expected['text'] = image_file
        async.return_value('test_mds_id')

    @patch('taxi.internal.archive.restore_many_orders')
    @async.inline_callbacks
    def restore_many_orders(order_ids, update=False, log_extra=None):
        yield db.orders.insert({
            '_id': order_ids[0],
            'performer': {
                'taxi_alias': {
                    'id': 'test_alias_id_%s' % order_ids[0].split('_')[-1]
                },
                'tariff': {
                    'currency': 'AMD'
                }
            }
        })
        async.return_value([])

    @patch('taxi.internal.archive.restore_many_subvention_reasons')
    @async.inline_callbacks
    def restore_many_subvention_reasons(orders_ids, update=False,
                                        log_extra=None):
        result = []
        for order_id in orders_ids:
            if order_id == 'test_order_id_5':
                result.append('test_order_id_5')
            yield db.subvention_reasons.insert({
                'order_id': order_id,
                'alias_id': 'test_alias_id_%s' % order_id.split('_')[-1],
                'subvention_bonus': [],
                'version': 1,
            })
        async.return_value(result)

    @patch('taxi.core.async.sleep')
    def sleep(seconds):
        pass

    @patch('taxi.internal.archive.restore_many_mph_results')
    @async.inline_callbacks
    def restore_many_mph_results(orders_ids, update=False, log_extra=None):
        for order_id in orders_ids:
            yield db.mph_results.insert({'_id': order_id})
        async.return_value([])

    @patch('taxi.external.billing_orders.send_doc')
    def send_doc(kind, external_obj_id, external_event_ref, event_at, data,
                 reason, **kwargs):
        return

    response = django_test.Client().post(
        '/api/confirmations/%s/manual_apply/' % confirmation_id,
        json.dumps({}), 'application/json'
    )

    assert response.status_code == code
    yield db.admin_confirmations.update(
        {
            '_id': confirmation_id,
            dbh.admin_confirmations.Doc.status: 'applying'
        },
        {'$set': {
            dbh.admin_confirmations.Doc.apply_time:
                datetime.datetime(2016, 4, 7, 13, 0, 0)
        }}
    )
    yield admin_confirmations.do_stuff()
    if code == 200:
        yield check_method(
            confirmation_id, json.loads(response.content), expected,
            delete_ids
        )
    assert not restore_many_mph_results.calls


@pytest.mark.parametrize('confirmation_id,data,code,expected', [
    (
        'confirmation_id_1', {
            'description': 'test_description',
            'doc_type': 'tariffs',
            'operation_type': 'update',
            'new_doc': {
                'activation_zone': 'moscow',
                'home_zone': 'cheboksary',
                'categories': [
                    {
                        'category_name': 'vip',
                        'time_from': '01:00',
                        'time_to': '13:59',
                        'name_key': 'interval.24h',
                        'day_type': 2,
                        'currency': 'RUR',
                        'minimal': 41,
                        'waiting_price': 43,
                        'paid_dispatch_distance_price_intervals': [],
                        'time_price_intervals': [
                            {'price': 10, 'begin': 110}
                        ],
                        'waiting_included': 5,
                        'paid_cancel_fix': 0,
                        'add_minimal_to_paid_cancel': True,
                    }
                ]
            },
            'request_id': 'test_request_id_113',
            'run_manually': False

        }, 200, {
            'comment': ['test_comment'],
            'run_manually': False,
            'doc_type': 'tariffs',
            'description': 'test_description',
            'updated': datetime.datetime(2016, 4, 7, 13, 0),
            'created': datetime.datetime(2016, 4, 8, 10, 0),
            'approvals': [],
            'created_by': 'dmkurilov',
            'version': 2,
            'operation_type': 'update',
            'change_doc_id': 'tariffs_cheboksary',
            'status': 'need_approval',
            'request_id': 'test_request_id_113',
            'new_doc': {
                'p': '__mrt',
                'activation_zone': 'moscow',
                'home_zone': 'cheboksary',
                'categories': [
                    {
                        'name': 'vip',
                        'from_time': '01:00',
                        'to_time': '13:59',
                        'name_key': 'interval.24h',
                        'dt': 2,
                        'currency': 'RUR',
                        'minimal': 41,
                        'waiting_price': 43,
                        'pddpi': [],
                        'tpi': [{'p': 10, 'b': 110}],
                        'waiting': 5,
                        'paid_cancel_fix': 0,
                        'add_minimal_to_paid_cancel': True,
                    }
                ]
            },
            '_id': 'confirmation_id_1'
        }
    ),
    (
        'confirmation_id_13', {
            'new_doc': {
                'clid': 'park1',
                'date_from': '2016-04-08',
                'date_to': '2016-04-13'
            },
            'operation_type': 'create',
            'doc_type': 'subventions_payments',
            'description': 'test_description',
            'request_id': 'test_request_id_19',
            'run_manually': True

        }, 200, {
            'comment': [],
            'run_manually': True,
            'operation_type': 'create',
            'doc_type': 'subventions_payments',
            'description': 'test_description',
            'updated': datetime.datetime(2016, 4, 7, 13, 0),
            'created': datetime.datetime(2016, 4, 8, 10, 0),
            'approvals': [],
            'created_by': 'dmkurilov',
            'version': 2,
            'change_doc_id': 'subvention_payments_park2',
            'status': 'need_approval',
            'request_id': 'test_request_id_19',
            'new_doc': {
                'clid': 'park1',
                'date_from': '2016-04-08',
                'date_to': '2016-04-13'
            },
            '_id': 'confirmation_id_13'
        }
    ),
    (
        'confirmation_id_15', {
            'new_doc': {
                'tariff_zones': ['cheboksary', 'moscow'],
                'sums_by_days_hours': [
                    {
                        'days': '1-3,5',
                        'hours': '2-12,23',
                        'sum': 123
                    },
                    {
                        'days': '1-2,4-5',
                        'hours': '2-11,22-23',
                        'sum': 28
                    }
                ],
                'geoareas_lists': [[]],
                'ticket': 'TAXIRATE-ticket',
                'dayridecount_days': 3,
                'region': 'msc',
                'geoareas': [],
                'tags': '',
                'categories': ['econom', 'vip'],
                'category': 'econom',
                'start': '2017-6-12 21:00:00',
                'rule_type': 'guarantee',
                'dayridecount': '1-7',
                'paymenttype': 'cash',
                'is_fake': False,
                'has_fake_counterpart': False,
                'sub_commission': True,
                'is_bonus': False,
                'branding_type': None,
                'is_once': False,
            },
            'request_id': 'test_request_id_22',
            'run_manually': True,
            'doc_type': 'subventions',
            'operation_type': 'bulk_create',
        }, 406, None
    ),
    (
        'confirmation_id_16', {
            'new_doc': {
                'tariff_zones': ['cheboksary', 'moscow'],
                'sums_by_days_hours': [
                    {
                        'days': '1-3,5',
                        'hours': '2-12,23',
                        'sum': 123
                    },
                    {
                        'days': '1-2,4-5',
                        'hours': '2-11,22-23',
                        'sum': 28
                    }
                ],
                'geoareas_lists': [[]],
                'ticket': 'TAXIRATE-ticket',
                'dayridecount_days': 3,
                'region': 'msc',
                'geoareas': [],
                'tags': '',
                'categories': ['econom', 'vip'],
                'category': 'econom',
                'start': '2017-6-12 21:00:00',
                'end': '2017-6-13 21:00:00',
                'rule_type': 'guarantee',
                'dayridecount': '1-',
                'paymenttype': 'cash',
                'is_fake': False,
                'has_fake_counterpart': False,
                'sub_commission': True,
                'is_bonus': False,
                'branding_type': None,
                'is_once': False,
            },
            'request_id': 'test_request_id_22',
            'run_manually': True,
            'doc_type': 'subventions',
            'operation_type': 'bulk_create',
        }, 200,
        {
            '_id': 'confirmation_id_16',
            'approvals': [],
            'comment': [],
            'created': datetime.datetime(2016, 4, 8, 10, 0),
            'created_by': 'dmkurilov',
            'description': '',
            'doc_type': 'subventions',
            'new_doc': _make_subvention_expected_data(
                BASE_DATA_FIELDS_3,
                ['econom', 'vip'],
                ['cheboksary', 'moscow'],
                [
                    {
                        'dayofweek': [1, 2, 3, 5],
                        'hour': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 23],
                        'rule_sum': 123
                    },
                    {
                        'dayofweek': [1, 2, 4, 5],
                        'hour': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 22, 23],
                        'rule_sum': 28
                    }
                ],
                [[]]
            ),
            'operation_type': 'bulk_create',
            'request_id': 'test_request_id_22',
            'run_manually': True,
            'via_taxirate': True,
            'change_doc_id': '6064646ce33047708a166412945bcbbd',
            'status': 'approved',
            'updated': datetime.datetime(2016, 4, 7, 13, 0),
            'version': 2
        }
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-04-07 13:00:00+03')
@pytest.mark.config(
    ADMIN_CONFIRMATIONS_NUM_APPROVALS=1,
    COUNTRY_DATE_WITH_ONLY_AUTOMATE_DONATIONS={
        'rus': '2015-08-01'
    }
)
@pytest.inline_callbacks
def test_edit_confiramtion(confirmation_id, data, code, expected, patch):
    @patch('taxiadmin.audit.check_ticket')
    @async.inline_callbacks
    def check_ticket(ticket_key, login, component=None, unique_ticket=False):
        yield

    @patch('taxiadmin.tariff_checks.check_tariff')
    @async.inline_callbacks
    def check_tariff(tariff, tariff_settings, log_extra=None):
        yield

    @patch('taxi.internal.startrack.create_comment')
    @async.inline_callbacks
    def create_comment(ticket, body, summonees=None):
        yield

    @patch('taxi.external.startrack.get_ticket_info')
    @async.inline_callbacks
    def get_ticket_info(ticket):
        yield async.return_value({
            'status': {'key': 'approved'},
            'createdBy': {'id': 'mvpetrov'},
            'manager': {}
        })

    @patch('taxiadmin.audit.get_last_approver')
    @async.inline_callbacks
    def get_last_approver(ticket, approve_statuses):
        yield async.return_value(('mvpetrov', 'random_date'))

    response = django_test.Client().post(
        '/api/confirmations/%s/edit/' % confirmation_id,
        json.dumps(data), 'application/json')

    assert response.status_code == code
    if code == 200:
        confirmation_doc = yield db.admin_confirmations.find_one({
            '_id': confirmation_id})

        assert confirmation_doc == expected


@pytest.mark.parametrize('confirmation_id,code,comment', [
    (
        'confirmation_id_5', 200, 'new_test_comment'
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-04-08 13:00:00+03')
@pytest.mark.config(
    ADMIN_CONFIRMATIONS_NUM_APPROVALS=1,
)
@pytest.inline_callbacks
def test_add_comment(confirmation_id, code, comment, patch):
    @patch('taxiadmin.audit.check_ticket')
    @async.inline_callbacks
    def check_ticket(ticket_key, login, component=None, unique_ticket=False):
        yield

    response = django_test.Client().post(
        '/api/confirmations/%s/comment/' % confirmation_id,
        json.dumps({'comment': comment}),
        'application/json')

    assert response.status_code == code
    if code == 200:
        confirmation_doc = yield db.admin_confirmations.find_one({
            '_id': confirmation_id})
        assert confirmation_doc['comment'] == [
            'test_comment', 'new_test_comment']


@pytest.mark.parametrize('confirmation_id,code,comment', [
    (
        'confirmation_id_13', 200, 'new_test_comment'
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-04-08 13:00:00+03')
@pytest.mark.config(
    ADMIN_CONFIRMATIONS_NUM_APPROVALS=1,
)
@pytest.inline_callbacks
def test_reject(confirmation_id, code, comment):
    response = django_test.Client().post(
        '/api/confirmations/%s/reject/' % confirmation_id,
        json.dumps({'comment': comment}),
        'application/json'
    )

    assert response.status_code == code
    rejected_confirmation = yield db.admin_confirmations.find_one({
        '_id': confirmation_id,
    })
    assert rejected_confirmation['status'] == 'rejected'
    assert rejected_confirmation['rejected_by'] == 'dmkurilov'


@pytest.mark.asyncenv('blocking')
def test_payments_prepare_invalid_status(open_file):
    with open_file("bulk_subventions_invalid_status.csv") as fp:
        response = django_test.Client().post(
            '/api/subventions/prepare_payments/', {'orders': fp}
        )

    assert response.status_code == 400
    assert json.loads(response.content) == {
        'status': 'error',
        'message': 'Order with id=test_order_id_4 '
                   'has invalid status: finished/expired',
        'code': 'invalid_order_status'
    }


@pytest.mark.asyncenv('blocking')
def test_prepare_payments_text_correct(open_file, patch):
    @patch('taxi.external.mds.upload')
    @async.inline_callbacks
    def upload(
            image_file, namespace=None, key_suffix=None,
            headers=None, retry_on_fails=True, log_extra=None
    ):
        assert "\r" not in image_file
        assert "\n\n" not in image_file
        async.return_value(image_file)

    @patch('taxi.internal.archive.get_many_orders')
    @async.inline_callbacks
    def get_many_orders(ids):
        result = yield db.orders.find({'_id': {'$in': ids}}).run()
        async.return_value(result)

    with open_file("test_prepare_payments_text_correct.csv") as fp:
        response = django_test.Client().post(
            '/api/subventions/prepare_payments/', {'orders': fp}
        )

    assert response.status_code == 200
