# encoding=utf-8
import json

import pytest

from taxi_tests.utils import ordered_object


ENDPOINT = '/cars/list'
ORDER_FIELDS = [
    'cars.category',
    'cars.amenities',
    'cars.chairs',
    'cars.chairs.categories',
    'cars.confirmed_chairs',
    'cars.confirmed_chairs.categories',
    'cars.confirmed_chairs.confirmed_categories',
    'cars.tags',
]

DEFAULT_FIELDS = [
    'amenities',
    'booster_count',
    'brand',
    'callsign',
    'cargo_loaders',
    'carrier_permit_owner_id',
    'category',
    'chairs',
    'charge_confirmed',
    'color',
    'confirmed_boosters',
    'confirmed_chairs',
    'created_date',
    'description',
    'euro_car_segment',
    'id',
    'kasko_date',
    'lightbox_confirmed',
    'mileage',
    'model',
    'modified_date',
    'normalized_number',
    'number',
    'onlycard',
    'osago_date',
    'osago_number',
    'park_id',
    'permit_doc',
    'permit_num',
    'permit_series',
    'registration_cert',
    'registration_cert_verified',
    'rental',
    'rug_confirmed',
    'service_date',
    'status',
    'sticker_confirmed',
    'tags',
    'tariffs',
    'transmission',
    'vin',
    'year',
    'fuel_type',
    'rental_status',
    'leasing_company',
    'leasing_start_date',
    'leasing_term',
    'leasing_monthly_payment',
    'leasing_interest_rate',
]


def check_offset_limit(response_json, request_json):
    if 'offset' in request_json:
        assert response_json.pop('offset') == request_json['offset']
    else:
        assert response_json.pop('offset') == 0
    if 'limit' in request_json:
        assert response_json.pop('limit') == request_json['limit']
    else:
        assert 'limit' not in response_json


@pytest.mark.parametrize(
    'request_json,expected_response',
    [
        (
            {
                'query': {'park': {'id': 'net_takogo'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_empty.json',
        ),
        (
            {
                'query': {'park': {'id': '1234abc'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_ok.json',
        ),
        (
            {
                'query': {
                    'park': {
                        'id': '1234abc',
                        'car': {
                            'id': [
                                '00033693fa67429588f09de95f4aaa9c',
                                '005c49c5f2fb4075a3fbd015ebace10e',
                            ],
                        },
                    },
                },
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_ok.json',
        ),
        (
            {
                'query': {'park': {'id': 'chair_yandex_brand'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_chair_yandex_brand.json',
        ),
        (
            {
                'query': {'park': {'id': 'chair_empty_brand'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_chair_empty_brand.json',
        ),
        (
            {
                'query': {'park': {'id': 'chair_isofix'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_chair_isofix.json',
        ),
        (
            {
                'offset': 2,
                'query': {'park': {'id': '1234abc'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_offset_too_large.json',
        ),
        (
            {
                'limit': 10,
                'offset': 2,
                'query': {'park': {'id': '1234abc'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_offset_too_large.json',
        ),
        (
            {
                'limit': 10,
                'offset': 10,
                'query': {'park': {'id': '1234abc'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_offset_too_large.json',
        ),
        (
            {
                'limit': 1,
                'offset': 0,
                'query': {'park': {'id': '1234abc'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_ok_005.json',
        ),
        (
            {
                'limit': 1,
                'offset': 1,
                'query': {'park': {'id': '1234abc'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_ok_00033.json',
        ),
        (
            {
                'limit': 10,
                'offset': 1,
                'query': {'park': {'id': '1234abc'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_ok_00033.json',
        ),
        (
            {
                'limit': 2,
                'offset': 0,
                'query': {'park': {'id': '1234abc'}},
                'fields': {'car': DEFAULT_FIELDS},
            },
            'response_ok.json',
        ),
    ],
)
def test_old_functionality_ok(
        taxi_parks, load_json, request_json, expected_response,
):
    response = taxi_parks.post(ENDPOINT, data=json.dumps(request_json))

    assert response.status_code == 200, response.text
    response_json = response.json()
    check_offset_limit(response_json, request_json)
    assert ordered_object.order(
        response_json, ORDER_FIELDS,
    ) == ordered_object.order(load_json(expected_response), ORDER_FIELDS)


TEST_PARAMS_OK = [
    (
        {
            'query': {'park': {'id': 'test_search'}, 'text': ''},
            'fields': {'car': DEFAULT_FIELDS},
        },
        'response_test_search_all.json',
    ),
    (
        {
            'query': {
                'park': {'id': 'test_search', 'car': {'id': ['3', '1', '2']}},
                'text': '',
            },
            'fields': {'car': DEFAULT_FIELDS},
        },
        'response_test_search_all.json',
    ),
    (
        {
            'query': {'park': {'id': 'test_search'}, 'text': 'AA77'},
            'fields': {'car': DEFAULT_FIELDS},
        },
        'response_test_search_number.json',
    ),
    (
        {
            'query': {
                'park': {'id': 'test_search', 'car': {'id': ['3', '1', '2']}},
                'text': 'AA77',
            },
            'fields': {'car': DEFAULT_FIELDS},
        },
        'response_test_search_number.json',
    ),
    (
        {
            'query': {
                'park': {'id': 'test_search', 'car': {'id': ['1', '2']}},
                'text': 'AA77',
            },
            'fields': {'car': DEFAULT_FIELDS},
        },
        'response_test_search_number.json',
    ),
    (
        {
            'query': {
                'park': {'id': 'test_search', 'car': {'id': ['1', '2']}},
                'text': '  AA77 ',
            },
            'fields': {'car': DEFAULT_FIELDS},
        },
        'response_test_search_number.json',
    ),
    (
        {
            'query': {
                'park': {'id': 'test_search', 'car': {'id': ['1', '2']}},
                'text': '  AA77 ',
            },
            'fields': {'car': DEFAULT_FIELDS},
        },
        'response_test_search_number.json',
    ),
    (
        {
            'query': {
                'park': {'id': 'test_search', 'car': {'id': ['1', '2']}},
                'text': '  aa7 ',
            },
            'fields': {'car': DEFAULT_FIELDS},
        },
        'response_test_search_number.json',
    ),
    (
        {'query': {'park': {'id': 'test_search'}, 'text': '  a77 '}},
        'response_test_fields1.json',
    ),
    (
        {'query': {'park': {'id': 'test_search'}, 'text': '  77 '}},
        'response_test_fields1.json',
    ),
    (
        {
            'query': {'park': {'id': 'test_search'}, 'text': '  aa77 '},
            'fields': {'car': ['id', 'park_id', 'vin']},
        },
        'response_test_fields2.json',
    ),
    (
        {
            'query': {'park': {'id': 'test_search2', 'car': {'id': ['4']}}},
            'fields': {'car': ['id', 'park_id', 'registration_cert_verified']},
        },
        'response_test_cert_verification.json',
    ),
]


@pytest.mark.parametrize('request_json,expected_response', TEST_PARAMS_OK)
def test_ok(taxi_parks, load_json, request_json, expected_response):
    response = taxi_parks.post(ENDPOINT, data=json.dumps(request_json))

    assert response.status_code == 200, response.text
    response_json = response.json()
    check_offset_limit(response_json, request_json)
    assert ordered_object.order(
        response_json, ORDER_FIELDS,
    ) == ordered_object.order(load_json(expected_response), ORDER_FIELDS)


def test_unprintable_search_request(taxi_parks):
    response = taxi_parks.post(
        ENDPOINT,
        data=b'{"query": {"park": { "id": "1" }, "text": "\x80  aa 77 " }}',
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'error': {'text': 'query.text must be an utf-8 string without BOM'},
    }


TEST_QUERY_PARAMS_OK = [
    # query park car status
    (
        {
            'query': {
                'park': {
                    'id': 'test_search',
                    'car': {'status': ['abra', 'kadabra']},
                },
            },
        },
        {'cars': [], 'offset': 0, 'total': 0},
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'test_search',
                    'car': {'status': ['not_working']},
                },
            },
        },
        {'cars': [{'id': '1'}], 'offset': 0, 'total': 1},
    ),
    (
        {
            'query': {
                'park': {'id': 'test_search', 'car': {'status': ['working']}},
            },
        },
        {'cars': [{'id': '2'}, {'id': '3'}], 'offset': 0, 'total': 2},
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'test_search',
                    'car': {'status': ['working', 'not_working']},
                },
            },
        },
        {
            'cars': [{'id': '2'}, {'id': '1'}, {'id': '3'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # query park car amenities
    (
        {
            'query': {
                'park': {'id': '222333', 'car': {'amenities': ['wifi']}},
            },
            'fields': {'car': ['normalized_number']},
        },
        {
            'cars': [{'id': 'Gelendewagen', 'normalized_number': 'B7770P77'}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {'park': {'id': '1488', 'car': {'amenities': ['wifi']}}},
            'fields': {'car': ['normalized_number']},
        },
        {
            'cars': [
                {
                    'id': '11133693fa67429588f09de95f4aaa9c',
                    'normalized_number': 'HB9999',
                },
                {'id': 'Gelendewagen', 'normalized_number': 'B7770P77'},
            ],
            'offset': 0,
            'total': 2,
        },
    ),
    (
        {
            'query': {'park': {'id': '1488', 'car': {'amenities': ['wifi']}}},
            'fields': {
                'car': [
                    'service_check_expiration_date',
                    'car_insurance_expiration_date',
                    'car_authorization_expiration_date',
                    'insurance_for_goods_and_passengers_expiration_date',
                    'badge_for_alternative_transport_expiration_date',
                ],
            },
        },
        {
            'cars': [
                {'id': '11133693fa67429588f09de95f4aaa9c'},
                {
                    'id': 'Gelendewagen',
                    'service_check_expiration_date': '2019-12-27T00:00:00.00Z',
                    'car_insurance_expiration_date': '2019-12-27T00:00:00.00Z',
                    'car_authorization_expiration_date': (
                        '2019-12-27T00:00:00.00Z'
                    ),
                    'insurance_for_goods_and_passengers_expiration_date': (
                        '2019-12-27T00:00:00.00Z'
                    ),
                    'badge_for_alternative_transport_expiration_date': (
                        '2019-12-27T00:00:00.00Z'
                    ),
                },
            ],
            'offset': 0,
            'total': 2,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'car': {'amenities': ['wifi', 'smoking']},
                },
            },
            'fields': {'car': ['normalized_number']},
        },
        {
            'cars': [{'id': 'Gelendewagen', 'normalized_number': 'B7770P77'}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'Kindergarten',
                    'car': {'amenities': ['booster']},
                },
            },
            'fields': {'car': ['amenities']},
        },
        {
            'cars': [
                {
                    'id': '3_one_booster_amenity_false',
                    'amenities': ['wifi', 'booster', 'rug'],
                },
                {
                    'id': '4_two_booster_amenity_true',
                    'amenities': ['wifi', 'booster', 'rug'],
                },
                {
                    'id': '9_three_boosters_one_chair',
                    'amenities': ['pos', 'booster', 'child_seat', 'rug'],
                },
            ],
            'offset': 0,
            'total': 3,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'Kindergarten',
                    'car': {'amenities': ['child_seat']},
                },
            },
            'fields': {'car': ['amenities']},
        },
        {
            'cars': [
                {
                    'id': '7_one_chair_amenity_false',
                    'amenities': ['animals', 'child_seat', 'rug'],
                },
                {
                    'id': '8_two_chairs_amenity_true',
                    'amenities': ['animals', 'child_seat', 'rug'],
                },
                {
                    'id': '9_three_boosters_one_chair',
                    'amenities': ['pos', 'booster', 'child_seat', 'rug'],
                },
            ],
            'offset': 0,
            'total': 3,
        },
    ),
    # query park car categories
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'car': {'categories': ['maybach', 'econom']},
                },
            },
            'fields': {'car': ['normalized_number']},
        },
        {'cars': [], 'offset': 0, 'total': 0},
    ),
    (
        {
            'query': {
                'park': {'id': '222333', 'car': {'categories': ['business']}},
            },
            'fields': {'car': ['normalized_number']},
        },
        {
            'cars': [{'id': 'Gelendewagen', 'normalized_number': 'B7770P77'}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {'park': {'id': '1488', 'car': {'categories': ['vip']}}},
            'fields': {'car': ['normalized_number']},
        },
        {
            'cars': [
                {
                    'id': '11133693fa67429588f09de95f4aaa9c',
                    'normalized_number': 'HB9999',
                },
                {'id': 'Gelendewagen', 'normalized_number': 'B7770P77'},
            ],
            'offset': 0,
            'total': 2,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'car': {'categories': ['econom', 'vip']},
                },
            },
            'fields': {'car': ['normalized_number']},
        },
        {
            'cars': [
                {
                    'id': '11133693fa67429588f09de95f4aaa9c',
                    'normalized_number': 'HB9999',
                },
            ],
            'offset': 0,
            'total': 1,
        },
    ),
    # query park car amenities + categories
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'car': {'amenities': ['wifi'], 'categories': ['vip']},
                },
            },
            'fields': {'car': ['normalized_number']},
        },
        {
            'cars': [
                {
                    'id': '11133693fa67429588f09de95f4aaa9c',
                    'normalized_number': 'HB9999',
                },
                {'id': 'Gelendewagen', 'normalized_number': 'B7770P77'},
            ],
            'offset': 0,
            'total': 2,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'car': {'amenities': ['smoking'], 'categories': ['vip']},
                },
            },
            'fields': {'car': ['normalized_number']},
        },
        {
            'cars': [{'id': 'Gelendewagen', 'normalized_number': 'B7770P77'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # categories_filter
    (
        {
            'query': {
                'park': {'id': '222333', 'car': {'id': ['Gelendewagen']}},
            },
            'fields': {'car': ['category']},
        },
        {
            'cars': [{'id': 'Gelendewagen', 'category': ['mkk', 'business']}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'car': {'id': ['Gelendewagen'], 'categories_filter': []},
                },
            },
            'fields': {'car': ['category']},
        },
        {
            'cars': [{'id': 'Gelendewagen', 'category': ['business', 'mkk']}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'car': {
                        'id': ['Gelendewagen'],
                        'categories_filter': ['business', 'maybach'],
                    },
                },
            },
            'fields': {'car': ['category']},
        },
        {
            'cars': [{'id': 'Gelendewagen', 'category': ['business']}],
            'offset': 0,
            'total': 1,
        },
    ),
    # test amenities
    (
        {
            'query': {'park': {'id': 'Kindergarten'}},
            'fields': {'car': ['amenities']},
        },
        {
            'cars': [
                {'id': '0_bad_boosters_count_and_chairs', 'amenities': []},
                {
                    'id': '1_no_boosters_amenity_false',
                    'amenities': ['wifi', 'rug'],
                },
                {
                    'id': '2_no_booster_amenity_true',
                    'amenities': ['wifi', 'rug'],
                },
                {
                    'id': '3_one_booster_amenity_false',
                    'amenities': ['wifi', 'booster', 'rug'],
                },
                {
                    'id': '4_two_booster_amenity_true',
                    'amenities': ['wifi', 'booster', 'rug'],
                },
                {
                    'id': '5_no_chairs_amenity_false',
                    'amenities': ['animals', 'rug'],
                },
                {
                    'id': '6_no_chairs_amenity_true',
                    'amenities': ['animals', 'rug'],
                },
                {
                    'id': '7_one_chair_amenity_false',
                    'amenities': ['animals', 'child_seat', 'rug'],
                },
                {
                    'id': '8_two_chairs_amenity_true',
                    'amenities': ['animals', 'child_seat', 'rug'],
                },
                {
                    'id': '9_three_boosters_one_chair',
                    'amenities': ['pos', 'booster', 'child_seat', 'rug'],
                },
            ],
            'offset': 0,
            'total': 10,
        },
    ),
    # is_rental filter
    (
        {
            'query': {
                'park': {'id': 'rental_cars_park', 'car': {'is_rental': True}},
            },
        },
        {
            'cars': [{'id': 'rental_car1'}, {'id': 'rental_car2'}],
            'offset': 0,
            'total': 2,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'rental_cars_park',
                    'car': {'is_rental': False},
                },
            },
        },
        {
            'cars': [{'id': 'non_rental_car1'}, {'id': 'non_rental_car2'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # is_rental + categories
    (
        {
            'query': {
                'park': {
                    'id': 'rental_cars_park',
                    'car': {'is_rental': True, 'categories': ['business']},
                },
            },
        },
        {'cars': [{'id': 'rental_car1'}], 'offset': 0, 'total': 1},
    ),
    # is_readonly
    (
        {
            'query': {
                'park': {
                    'id': 'rental_cars_park',
                    'car': {'id': ['rental_car1']},
                },
            },
            'fields': {'car': ['is_readonly']},
        },
        {
            'cars': [{'id': 'rental_car1', 'is_readonly': False}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {'park': {'id': 'couriers_park'}},
            'fields': {'car': ['is_readonly']},
        },
        {
            'cars': [{'id': 'fake_car', 'is_readonly': True}],
            'offset': 0,
            'total': 1,
        },
    ),
    # digital_lightbox
    (
        {
            'query': {'park': {'id': 'digital_lightbox_park'}},
            'fields': {'car': ['amenities']},
        },
        {
            'cars': [{'id': 'car1', 'amenities': ['digital_lightbox']}],
            'offset': 0,
            'total': 1,
        },
    ),
]


@pytest.mark.parametrize(
    'request_json,expected_response', TEST_QUERY_PARAMS_OK,
)
def test_query_ok(taxi_parks, request_json, expected_response):
    response = taxi_parks.post(ENDPOINT, data=json.dumps(request_json))

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['cars.category'],
    )


QUERY_TEXT_PARAMS = [
    # id
    'pagani_huayra_car_id',
    # vin
    'АККК0123456789ВВВ',
    'AKKK0123456789ВВВ   ',
    ' AKKK0123456789BBB',
    '     0123456789',
    # brand
    'pagani',
    'PAGANI',
    'pAGAni',
    'pAGAn ',
    # model
    'huayra',
    'HUAYRA',
    'huayRA',
    'huay',
    'hu',
    # number
    ' X077AM77',
    '     AM77',
    'х077ам  ',
    'Х077аМ7',
    '  077',
    # call sign
    'хуара',
    'хуа  ',
    # permit doc
    'QI7   ',
    'QI7978',
    # permit num
    '344',
    '3443',
    # permit series
    'МСК',
    # registration cert
    '2525     ',
    '    69996',
    '252569996',
]


@pytest.mark.parametrize('query_text', QUERY_TEXT_PARAMS)
def test_query_text(taxi_parks, query_text):
    response = taxi_parks.post(
        ENDPOINT,
        data=json.dumps(
            {
                'query': {
                    'park': {'id': 'sport_cars_park_id'},
                    'text': query_text,
                },
                'fields': {'car': ['park_id']},
            },
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'offset': 0,
        'total': 1,
        'cars': [
            {'id': 'pagani_huayra_car_id', 'park_id': 'sport_cars_park_id'},
        ],
    }


SORT_ORDER_PARAMS = [
    ([], ['2', '1', '3']),
    ([{'field': 'car.created_date', 'direction': 'asc'}], ['3', '1', '2']),
    ([{'field': 'car.modified_date', 'direction': 'asc'}], ['1', '2', '3']),
    ([{'field': 'car.modified_date', 'direction': 'desc'}], ['3', '2', '1']),
    ([{'field': 'car.created_date', 'direction': 'desc'}], ['2', '1', '3']),
    ([{'field': 'car.call_sign', 'direction': 'asc'}], ['1', '3', '2']),
    ([{'field': 'car.call_sign', 'direction': 'desc'}], ['2', '3', '1']),
    (
        [{'field': 'car.normalized_number', 'direction': 'asc'}],
        ['3', '1', '2'],
    ),
    (
        [{'field': 'car.normalized_number', 'direction': 'desc'}],
        ['2', '1', '3'],
    ),
]


@pytest.mark.parametrize('sort_order,expected_ids', SORT_ORDER_PARAMS)
def test_sort_order(taxi_parks, sort_order, expected_ids):
    response = taxi_parks.post(
        ENDPOINT,
        data=json.dumps(
            {
                'query': {'park': {'id': 'test_search'}},
                'sort_order': sort_order,
            },
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'offset': 0,
        'total': 3,
        'cars': list(map(lambda id: {'id': id}, expected_ids)),
    }
