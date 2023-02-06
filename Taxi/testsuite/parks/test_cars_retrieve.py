# encoding=utf-8
import json

import pytest


ENDPOINT_URL = '/cars/retrieve'

OK_PARAMS = [
    (
        {
            'query': {'park': {'id': '222333', 'car': {'id': 'Gelendewagen'}}},
            'fields': {
                'car': [
                    'brand',
                    'model',
                    'callsign',
                    'normalized_number',
                    'category',
                    'fuel_type',
                    'rental',
                    'rental_status',
                    'leasing_company',
                    'leasing_start_date',
                    'leasing_term',
                    'leasing_monthly_payment',
                    'leasing_interest_rate',
                ],
            },
        },
        {
            'car': {
                'brand': 'Mercedes-Benz',
                'model': 'AMG G63',
                'callsign': 'гелик',
                'normalized_number': 'B7770P77',
                'category': ['business', 'mkk'],
                'fuel_type': 'petrol',
                'rental': True,
                'rental_status': 'leasing',
                'leasing_company': 'sber',
                'leasing_interest_rate': 4.6,
                'leasing_monthly_payment': 50000,
                'leasing_start_date': '2018-01-01T00:00:00+0000',
                'leasing_term': 1000,
            },
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'car': {
                        'id': 'Gelendewagen',
                        'categories_filter': ['business', 'mkk', 'maybach'],
                    },
                },
            },
            'fields': {'car': ['category']},
        },
        {'car': {'category': ['business', 'mkk']}},
    ),
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'car': {
                        'id': 'Gelendewagen',
                        'categories_filter': ['business', 'maybach'],
                    },
                },
            },
            'fields': {
                'car': [
                    'category',
                    'carrying_capacity',
                    'body_number',
                    'cargo_hold_dimensions',
                ],
            },
        },
        {
            'car': {
                'category': ['business'],
                'carrying_capacity': 10,
                'body_number': '09876543211234567',
                'cargo_hold_dimensions': {
                    'length': 11,
                    'width': 12,
                    'height': 13,
                },
            },
        },
    ),
    (
        {
            'query': {
                'park': {'id': '222666', 'car': {'id': 'Gelendewagen2'}},
            },
            'fields': {'car': ['registration_cert_verified']},
        },
        {'car': {'registration_cert_verified': False}},
    ),
    (
        {
            'query': {
                'park': {'id': '222666', 'car': {'id': 'Gelendewagen2'}},
            },
            'fields': {'car': ['cert_verification']},
        },
        {'car': {}},
    ),
    # is_readonly
    (
        {
            'query': {
                'park': {'id': '222666', 'car': {'id': 'Gelendewagen2'}},
            },
            'fields': {'car': ['is_readonly']},
        },
        {'car': {'is_readonly': False}},
    ),
    (
        {
            'query': {
                'park': {'id': 'couriers_park', 'car': {'id': 'fake_car'}},
            },
            'fields': {'car': ['id', 'is_readonly']},
        },
        {'car': {'id': 'fake_car', 'is_readonly': True}},
    ),
    # digital_lightbox
    (
        {
            'query': {
                'park': {'id': 'digital_lightbox_park', 'car': {'id': 'car1'}},
            },
            'fields': {'car': ['amenities']},
        },
        {'car': {'amenities': ['digital_lightbox']}},
    ),
]


@pytest.mark.parametrize('request_json,expected_response', OK_PARAMS)
def test_ok(taxi_parks, request_json, expected_response):
    response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(request_json))

    assert response.status_code == 200
    assert response.json() == expected_response


BAD_REQUEST_PARAMS = [
    ({}, 'query must be present'),
    ({'query': {}}, 'query.park must be present'),
    ({'query': {'park': {}}}, 'query.park.id must be present'),
    (
        {'query': {'park': {'id': ''}}},
        'query.park.id must be a non-empty utf-8 string without BOM',
    ),
    ({'query': {'park': {'id': 'x'}}}, 'query.park.car must be present'),
    (
        {'query': {'park': {'id': 'x', 'car': {}}}},
        'query.park.car.id must be present',
    ),
    (
        {'query': {'park': {'id': 'x', 'car': {'id': ''}}}},
        'query.park.car.id must be a non-empty utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': 'x', 'car': {'id': 'y'}}}},
        'fields must be present',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'car': {'id': 'y'}}},
            'fields': {'car': ['a', 'number', 'c', 'number']},
        },
        'fields.car must contain unique strings (error at `number`)',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'car': {'id': 'y'}}},
            'fields': {'car': []},
        },
        'fields must contain at least one field',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'car': {'id': 'yyy', 'categories_filter': ['abra']},
                },
            },
        },
        'query.park.car.categories_filter each element must be one of: '
        '`business`, `cargo`, `child_tariff`, `comfort`, `comfort_plus`, '
        '`courier`, `demostand`, `econom`, `eda`, `express`, `lavka`, '
        '`limousine`, `maybach`, `minibus`, `minivan`, `mkk`, '
        '`mkk_antifraud`, `night`, `personal_driver`, `pool`, `premium_suv`, '
        '`premium_van`, `promo`, `selfdriving`, `standart`, `start`, '
        '`suv`, `trucking`, `ultimate`, `vip`, `wagon`',
    ),
]


@pytest.mark.parametrize('request_json,error_text', BAD_REQUEST_PARAMS)
def test_bad_request(taxi_parks, request_json, error_text):
    response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(request_json))

    assert response.status_code == 400
    assert response.json() == {'error': {'text': error_text}}


def test_car_not_found(taxi_parks):
    response = taxi_parks.post(
        ENDPOINT_URL,
        data=json.dumps(
            {
                'query': {
                    'park': {'id': '1499', 'car': {'id': 'Gelendewagen'}},
                },
                'fields': {'car': ['id']},
            },
        ),
    )

    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'car not found'}}
