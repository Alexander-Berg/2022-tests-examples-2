# -*- coding: utf-8 -*-

import datetime
import json

import pytest

from taxi.internal.corp_kit import corp_manager
from taxi.internal import dbh


@pytest.mark.parametrize(
    'order_id, expected_result, pd_phone_retrieve_calls',
    [
        (
            '9313c8dcef3243e7a36ae826e71dcc66',
            {
                '_id': '9313c8dcef3243e7a36ae826e71dcc66',
                'status': 'finished',
                'taxi_status': 'complete',
                '_type': 'soon',
                'waiting': {
                    'waiting_cost': 1784.7999999999997,
                    'waiting_time': 8924,
                    'waiting_in_depart_time': 100,
                    'waiting_in_transit_time': 2812
                },
                'city': u'Москва',
                'nearest_zone': u'moscow',
                'created_date': datetime.datetime(2016, 3, 24, 21, 27, 17),
                'due_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'started_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'finished_date': datetime.datetime(2016, 3, 24, 21, 47, 17),
                'performer': {
                    'car': u'Volkswagen Caravelle коричневый КС67477',
                    'fullname': u'Гарольд',
                    'vehicle': {'color_code': u'коричневый', 'model': u'Volkswagen Caravelle', 'number': u'КС67477'},
                },
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'destination': {
                    'geopoint': [
                        37.600296,
                        55.750379
                    ]
                },
                'source': {
                    'geopoint': [
                        37.58878761211858,
                        55.73414175200699
                    ],
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16'
                },
                'user_to_pay': {'ride': 6372000},
                'without_vat_to_pay': {'ride': 5400000},
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'class': 'comfort',
                'order_updated': datetime.datetime(2016, 3, 24, 21, 47, 17),
                'distance': 3100.,
                'cost_center': {
                    'user': u'старый ЦЗ',
                },
                'cost_centers': {
                    'user': [
                        {
                            'id': 'cost_center',
                            'title': u'Центр затрат',
                            'value': u'командировка',
                        },
                    ],
                },
                'combo_order': {
                    'delivery_id': 'delivery1',
                },
            },
            1,
        ),
        (
            'f4b0704ac74d47cbb6193175d6a50ec6',
            {
                '_id': 'f4b0704ac74d47cbb6193175d6a50ec6',
                'status': 'finished',
                'taxi_status': 'complete',
                '_type': 'soon',
                'city': u'Москва',
                'created_date': datetime.datetime(2016, 3, 24, 21, 27, 17),
                'due_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'started_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'finished_date': datetime.datetime(2016, 3, 24, 21, 47, 17),
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'source': {
                    'geopoint': [
                        37.58878761211858,
                        55.73414175200699
                    ],
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16'
                },
                'waiting': {
                    'waiting_in_depart_time': 100
                },
                'user_to_pay': {'ride': 6372000},
                'without_vat_to_pay': {'ride': 5400000},
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'class': 'econom',
                'performer': {},
                'order_updated': datetime.datetime(2016, 3, 24, 21, 47, 17),
            },
            0,
        ),
        (
            '6d6d90f169364806bf8bed8ac085fb63',
            {
                '_id': '6d6d90f169364806bf8bed8ac085fb63',
                'status': 'pending',
                'taxi_status': None,
                '_type': 'soon',
                'city': u'Москва',
                'created_date': datetime.datetime(2016, 3, 24, 21, 27, 17),
                'due_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'source': {
                    'geopoint': [
                        37.58878761211858,
                        55.73414175200699
                    ],
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16'
                },
                'waiting': {
                    'waiting_in_transit_time': 100
                },
                'class': 'econom',
                'performer': {},
                'order_updated': datetime.datetime(2016, 3, 24, 21, 47, 17),
                'cost_center': {
                    'user': u'ЦЗ по умолчанию',
                },
            },
            0,
        ),
        (
            '11abc876f33f46e0bf1c756780241f21',
            {
                '_id': '11abc876f33f46e0bf1c756780241f21',
                'status': 'assigned',
                '_type': 'soon',
                'taxi_status': 'transporting',
                'city': u'Москва',
                'created_date': datetime.datetime(2016, 3, 24, 21, 27, 17),
                'due_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'started_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'source': {
                    'geopoint': [
                        37.58878761211858,
                        55.73414175200699
                    ],
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16'
                },
                'performer': {
                    'car': u'Volkswagen Caravelle коричневый КС67477',
                    'fullname': u'Гарольд',
                    'vehicle': {'color_code': u'коричневый', 'model': u'Volkswagen Caravelle', 'number': u'КС67477'},
                },
                'class': 'econom',
                'order_updated': datetime.datetime(2016, 3, 24, 21, 37, 17),
            },
            1,
        ),
        (
            '1d8dd28d64bd4c29bf9d2e8fc125e037',
            {
                '_id': '1d8dd28d64bd4c29bf9d2e8fc125e037',
                'status': 'finished',
                'taxi_status': 'complete',
                '_type': 'soon',
                'user_to_pay': {'ride': 6372000},
                'without_vat_to_pay': {'ride': 5400000},
                'city': u'Москва',
                'created_date': datetime.datetime(2016, 3, 24, 21, 27, 17),
                'due_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'started_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'finished_date': datetime.datetime(2016, 3, 24, 21, 47, 17),
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'source': {
                    'geopoint': [
                        37.58878761211858,
                        55.73414175200699
                    ],
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16'
                },
                'destination': {
                    'geopoint': [
                        37.600296,
                        55.750379
                    ],
                },
                'distance': 7500.,
                'performer': {
                    'car': u'Volkswagen Caravelle коричневый КС67477',
                    'fullname': u'Гарольд',
                    'vehicle': {'color_code': u'коричневый', 'model': u'Volkswagen Caravelle', 'number': u'КС67477'},
                },
                'class': 'econom',
                'order_updated': datetime.datetime(2016, 3, 24, 21, 47, 17),
            },
            1,
        ),
        (
            'eb30cfe96cef481ea1c11d4e40d756d5',
            {
                '_id': 'eb30cfe96cef481ea1c11d4e40d756d5',
                'status': 'reordered',
                'taxi_status': None,
                '_type': 'soon',
                'city': u'Москва',
                'created_date': datetime.datetime(2016, 3, 24, 21, 27, 17),
                'due_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'source': {
                    'geopoint': [
                        37.58878761211858,
                        55.73414175200699
                    ],
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16'
                },
                'class': 'vip',
                'performer': {},
                'order_updated': datetime.datetime(2016, 3, 24, 21, 37, 17),
            },
            0,
        ),
        (
            'gagacfe96cef481ea1c11d4e40d756d5',
            {
                '_id': 'gagacfe96cef481ea1c11d4e40d756d5',
                'status': 'reordered',
                'taxi_status': None,
                '_type': 'soon',
                'city': u'Москва',
                'created_date': datetime.datetime(2016, 3, 24, 21, 27, 17),
                'due_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'source': {
                    'geopoint': [
                        37.58878761211858,
                        55.73414175200699
                    ],
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16'
                },
                'class': 'vip',
                'performer': {},
                'order_updated': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'cost_center': {
                    'user': u'ЦЗ по умолчанию',
                },
            },
            0,
        ),
        (
            'dadacfe96cef481ea1c11d4e40d756d5',
            {
                '_id': 'dadacfe96cef481ea1c11d4e40d756d5',
                'status': 'reordered',
                'taxi_status': None,
                '_type': 'soon',
                'city': u'Москва',
                'created_date': datetime.datetime(2016, 3, 24, 21, 27, 17),
                'due_date': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'source': {
                    'geopoint': [
                        37.58878761211858,
                        55.73414175200699
                    ],
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16'
                },
                'class': 'vip',
                'performer': {},
                'order_updated': datetime.datetime(2016, 3, 24, 21, 37, 17),
                'cost_center': {
                    'user': u'ЦЗ по умолчанию',
                },
            },
            0,
        ),
        (
            '53f23cf186b34e31b571ce9554b56675',
            {
                '_id': '53f23cf186b34e31b571ce9554b56675',
                'status': 'finished',
                'taxi_status': 'complete',
                '_type': 'soon',
                'city': u'Москва',
                'created_date': datetime.datetime(2017, 12, 21, 12, 14, 42),
                'order_updated': datetime.datetime(2017, 12, 21, 13, 03, 18),
                'finished_date': datetime.datetime(2017, 12, 21, 12, 32, 49),
                'due_date': datetime.datetime(2017, 12, 21, 12, 28, 00),
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'class': 'econom',
                'performer': {},
                'source': {
                    'geopoint': [37.58878761211858, 55.73414175200699],
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16'
                },
                'destination': {
                    'fullname': u'Россия, Москва, Большая Никитская улица, 13',
                    'geopoint': [37.600296, 55.750379]
                },
                'interim_destinations': [
                    {
                        'fullname': (
                            u'Россия, Москва, Садовническая улица, 84с7'
                        ),
                        'geopoint': [33.6, 55.1]
                    },
                    {
                        'fullname': (
                            u'Россия, Москва, Малая Никитская улица, 43'
                        ),
                        'geopoint': [37.6, 55.7]
                    }
                ],
                'user_to_pay': {'ride': 6616378},
                'without_vat_to_pay': {'ride': 5607100},
            },
            0,
        ),
        (
            'c5e8d0e99eb542e2b58ac13e918c4717',
            None,
            0,
        ),
        (
            'bfe801920d36410dacb8e3aaece5ece0',
            {
                '_id': 'bfe801920d36410dacb8e3aaece5ece0',
                'status': 'finished',
                'taxi_status': 'complete',
                '_type': 'soon',
                'city': u'Москва',
                'created_date': datetime.datetime(2020, 02, 21, 13, 40, 00),
                'order_updated': datetime.datetime(2020, 02, 21, 16, 00, 00),
                'finished_date': datetime.datetime(2020, 02, 21, 16, 00, 00),
                'due_date': datetime.datetime(2020, 02, 21, 16, 00, 00),
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'class': 'express',
                'cost_center': {
                    'user': u'старый ЦЗ',
                },
                'cost_centers': {
                    'user': [
                        {
                            'id': 'cost_center',
                            'title': u'Центр затрат',
                            'value': u'командировка',
                        },
                    ],
                },
                'performer': {},
                'requirements': {
                    "door_to_door": True,
                },
                'source': {
                    'extra_data': {
                        'apartment': '5',
                        'contact_phone_id': 'da4498c23324495790d49bee7dade66d',
                        'comment': 'source comment',
                        'floor': '3'
                    },
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16',
                    'geopoint': [37.58878761211858, 55.73414175200699],
                    'porchnumber': '1',
                },
                'destination': {
                    'extra_data': {
                        'apartment': '1',
                        'contact_phone_id': '73ac6747b2fa4e37a58caf19cba38c78',
                        'comment': 'destination comment',
                        'floor': '2'
                    },
                    'fullname': u'Россия, Москва, Большая Никитская улица, 13',
                    'geopoint': [37.600296, 55.750379],
                    'porchnumber': '1',
                },
                'interim_destinations': [
                    {
                        'fullname': (
                            u'Россия, Москва, Садовническая улица, 84с7'
                        ),
                        'geopoint': [33.6, 55.1]
                    },
                    {
                        'fullname': (
                            u'Россия, Москва, Малая Никитская улица, 43'
                        ),
                        'geopoint': [37.6, 55.7]
                    }
                ],
                'user_to_pay': {'ride': 9870000},
                'without_vat_to_pay': {'ride': 7459000},
            },
            0,
        ),
        (
            'be923a51bf4944aba33793b3025d5e58',
            {
                '_id': 'be923a51bf4944aba33793b3025d5e58',
                'status': 'finished',
                'taxi_status': 'complete',
                '_type': 'soon',
                'city': u'Москва',
                'created_date': datetime.datetime(2020, 02, 21, 13, 40, 00),
                'order_updated': datetime.datetime(2020, 02, 21, 16, 00, 00),
                'finished_date': datetime.datetime(2020, 02, 21, 16, 00, 00),
                'due_date': datetime.datetime(2020, 02, 21, 16, 00, 00),
                'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                'corp_user': {
                    'user_id': '88eaf8ef4d8b4d8384f6064da13a1680',
                    'department_id': 'e408b7e62a964cedb677952f600d5b08',
                },
                'class': 'express',
                'performer': {},
                'requirements': {
                    "door_to_door": True,
                },
                'source': {
                    'extra_data': {
                        'contact_phone_id': 'da4498c23324495790d49bee7dade66d',
                    },
                    'fullname': u'Россия, Москва, улица Льва Толстого, 16',
                    'geopoint': [37.58878761211858, 55.73414175200699],
                },
                'destination': {
                    'extra_data': {
                        'contact_phone_id': '73ac6747b2fa4e37a58caf19cba38c78',
                    },
                    'fullname': u'Россия, Москва, Большая Никитская улица, 13',
                    'geopoint': [37.600296, 55.750379],
                },
                'interim_destinations': [
                    {
                        'fullname': (
                            u'Россия, Москва, Садовническая улица, 84с7'
                        ),
                        'geopoint': [33.6, 55.1]
                    },
                    {
                        'fullname': (
                            u'Россия, Москва, Малая Никитская улица, 43'
                        ),
                        'geopoint': [37.6, 55.7]
                    }
                ],
                'user_to_pay': {'ride': 9870000},
                'without_vat_to_pay': {'ride': 7459000},
                'cost_center': {
                    'user': u'ЦЗ по умолчанию',
                },
            },
            0,
        ),
    ]
)
@pytest.mark.asyncenv('async')
@pytest.mark.config(CORP_SOURCES_NO_USER=['cargo'])
@pytest.mark.config(CORP_TAXI_PROCESSING_SETTINGS={})
@pytest.mark.filldb()
@pytest.inlineCallbacks
def test_sync_corp_order(order_id, expected_result, pd_phone_retrieve_calls,
                         patch, areq_request):
    @patch('taxi.external.cars_catalog.get_color')
    def mock_get_color(raw_color):
        return {'normalized_color': raw_color, 'color_code': raw_color}

    @patch('taxi.external.cars_catalog.get_brand_model')
    def mock_brand_model(brand, model):
        return {'corrected_model': brand + ' ' + model}

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    @patch('taxi.external.corp_users.v2_users_get')
    def _mock_v2_users_get(user_id, fields=None, log_extra=None, **kwargs):
        return {
            "id": "88eaf8ef4d8b4d8384f6064da13a1680",
            "cost_center": "ЦЗ по умолчанию",
            "department_id": "e408b7e62a964cedb677952f600d5b08",
        }
    yield corp_manager.corp_sync_order_stq(order_id)

    result = yield dbh.corp_orders.Doc._find_one({
        dbh.corp_orders.Doc.order_id: order_id
    })
    if expected_result:
        assert result.pop('updated', None) is not None
        assert dict(result) == expected_result
    else:
        assert not result

    assert len(requests_request.calls) == pd_phone_retrieve_calls
