# -- coding: utf8 --

from __future__ import unicode_literals

import datetime
import json

from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db


@pytest.mark.parametrize('method, data, code', [
    ('get', {}, 200),
    ('get', {'a': 'b'}, 400),
    ('post', {}, 405),
])
@pytest.mark.asyncenv('blocking')
def test_get_cities(method, data, code):
    method = getattr(django_test.Client(), method)
    response = method('/api/get_cities/', data)
    assert response.status_code == code
    if code == 200:
        response = json.loads(response.content)
        assert len(response) == 1
        response = response['items']

        assert {'id': 'moscow', 'center_tab': False} in response
        assert {'id': 'city2', 'center_tab': False} in response
        assert {'id': 'city1', 'center_tab': True} in response


@pytest.mark.parametrize('method, data, code, expected_response', [
    ('post', {'city_id': 'moscow', 'center_tab': False}, 200, {}),
    ('post', {'city_id': 'moscow', 'center_tab': True}, 200, {}),
    ('post', {'city_id': 'moscow', 'center_tab': 1}, 400, None),
    ('post', {'city_id': 'ekb', 'center_tab': True}, 404, None),
    ('post', {'city_id': 'moscow'}, 400, None),
    ('get', {}, 405, None),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_city_center_tab(method, data, code, expected_response):
    client = django_test.Client()
    if method == 'post':
        response = client.post('/api/set_city_center_tab/', json.dumps(data),
                               'application/json')
    else:
        response = client.get('/api/set_city_center_tab/', data)
    assert response.status_code == code, response.content
    if expected_response is not None:
        assert json.loads(response.content) == expected_response
        city = yield db.cities.find_one(data['city_id'])
        assert data['center_tab'] == city['center_tab']


@pytest.mark.parametrize('method, data, code, expected_response', [
    ('get', {'city_id': 'moscow'}, 200, {}),
    ('get', {'city_id': 'city1'}, 200, {
        'max_refund': 100000,
        'max_manual_charge': 200000
    }),
    ('get', {'city_id': 'city2'}, 200, {
        'max_refund': 100000,
        'max_compensation': 200000,
        'max_manual_charge': 300000
    }),
    ('get', {'city_id': 'undefined'}, 404, None),
    ('post', {}, 405, None),
])
@pytest.mark.asyncenv('blocking')
def test_get_city_refund_settings(method, data, code, expected_response):
    client = django_test.Client()
    if method == 'post':
        response = client.post('/api/get_city_refund_settings/', json.dumps(data),
                               'application/json')
    else:
        response = client.get('/api/get_city_refund_settings/', data)
    assert response.status_code == code, response.content
    if expected_response is not None:
        assert json.loads(response.content) == expected_response


@pytest.mark.parametrize('method, data, code, expected_response', [
    ('post', {'city_id': 'moscow',
              'max_refund': 400000,
              'max_compensation': 500000}, 200, {}),
    ('post', {'city_id': 'moscow',
              'max_refund': 600000,
              'max_compensation': 700000,
              'max_manual_charge': 800000}, 200, {}),
    ('post', {}, 400, None),
    ('post', {'city_id': 'undefined'}, 404, None),
    ('get', {}, 405, None),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_city_refund_settings(method, data, code, expected_response):
    client = django_test.Client()
    if method == 'post':
        response = client.post('/api/set_city_refund_settings/', json.dumps(data),
                               'application/json')
    else:
        response = client.get('/api/set_city_refund_settings/', data)
    assert response.status_code == code, response.content
    if expected_response is not None:
        assert json.loads(response.content) == expected_response
        city = yield db.cities.find_one(data.pop('city_id'))
        assert data == city['card_payment_settings']


# Load cities list with extended data
@pytest.mark.asyncenv('blocking')
def test_api_cities_list():
    response = django_test.Client().post(
        '/api/cities/list/',
        json.dumps({}),
        'application/json',
    )
    assert response.status_code == 405

    response = django_test.Client().get('/api/cities/list/')
    assert response.status_code == 200

    response = json.loads(response.content)

    almaty, = [city for city in response['cities'] if city['id'] == 'Алматы']

    assert almaty['eng'] == 'almaty'
    assert almaty['country'] == 'kaz'
    assert almaty['transfer_zones_count'] == 3
    assert almaty['geocoder_objects_count'] == 0
    assert almaty['exam_link'] == 'https://exam.ru/'
    assert almaty['center_tab'] is False


# Load specified citiy
@pytest.mark.asyncenv('blocking')
def test_api_load_city():
    response = django_test.Client().post(
        '/api/cities/list/',
        json.dumps({'id': 'Алматы'}),
        'application/json',
    )
    assert response.status_code == 405

    response = django_test.Client().get('/api/cities/list/', {'id': 'Алматы'})
    assert response.status_code == 200

    response = json.loads(response.content)

    city = response['cities'][0]

    assert city['eng'] == 'almaty'
    assert city['country'] == 'kaz'
    assert city['transfer_zones_count'] == 3
    assert city['geocoder_objects_count'] == 0
    assert city['exam_link'] == 'https://exam.ru/'
    assert city['center_tab'] is False


@pytest.mark.parametrize('update_data, status_code', [
    ({'id': 1}, 400),
    ({'disabled': 'true'}, 400),
    ({'country': 111}, 400),
    ({'eng': 123}, 400),
    ({'tl': [28.746]}, 400),
    ({'tl': [28.746, 'str']}, 400),
    ({'tl': []}, 400),
    ({'tl': [28.746, 33.567, 11.123]}, 400),
    ({'br': [28.746]}, 400),
    ({'br': [28.746, 'str']}, 400),
    ({'br': []}, 400),
    ({'br': [28.746, 33.567, 11.123]}, 400),
    ({'tz': None}, 400),
    ({'tz': ''}, 400),
    ({'tz': 'SomeNonExistingTimeZone'}, 400),
    ({'support_phone': None}, 400),
    ({'app_download_short_link': None}, 400),
    ({'max_card_payment': -1}, 400),
    ({'max_corp_payment': -1}, 400),
    ({'donate_multiplier': '1.3'}, 400),
    ({'donate_multiplier': ''}, 400),
    ({'req_destination': 'aaa'}, 400),
    ({'req_destination_rules': {'min_timedelta': -1}}, 400),
    ({'req_destination_rules': '1231234'}, 400),
    ({'precalc_cost': 33}, 400),
    ({'exact_orders': '123'}, 400),
    ({'waves_distance': [{'wave': 'common', 'max_distance': 100}]}, 400),
    ({'reorder_suggestion_interval': -1}, 400),
    ({'estimated_waiting_power_coef': -1}, 400),
    ({'check_contracts': -1}, 400),
    ({'accepted_permit_issuers': [-1, 3]}, 400),
    ({'center_tab': -1}, 400),
    ({'exam_link': 'http://ya.ru/'}, 400),
    ({'exam_link': 123}, 400),
    ({'donate_multiplier': '1.01'}, 400),
    ({'donate_discounts_multiplier': '1.01'}, 400),
    ({'donate_multiplier': '1.01', 'ticket': 'TAXIRATE-1'}, 200),
    ({'donate_discounts_multiplier': '1.01', 'ticket': 'TAXIRATE-1'}, 200),
    ({}, 200),
    ({
        'max_card_payment': None,
        'max_corp_payment': None,
        'req_destination': None,
        'req_destination_rules': None,
        'precalc_cost': None,
        'exact_orders': None,
        'waves_distance': None,
        'reorder_suggestion_interval': None,
        'estimated_waiting_power_coef': None,
        'check_contracts': None,
        'accepted_permit_issuers': None,
        'center_tab': None,
        'exam_link': None
    }, 200)
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_api_cities_save_validator(patch, update_data, status_code):

    @patch('taxiadmin.audit.check_taxirate')
    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        yield async.return_value()

    data = {
        'id': 'Кишинев',
        'disabled': False,
        'country': 'mda',
        'eng': 'chisinau',
        'tl': [28.746126, 47.080211],
        'br': [28.969972, 46.923788],
        'tz': 'Europe/Chisinau',
        'support_phone': '+74957058888',
        'donate_multiplier': '1.00',
        'donate_discounts_multiplier': '1.00',
        'app_download_short_link': '_link',
        'max_card_payment': 3200,
        'max_corp_payment': 20000,
        'req_destination': True,
        'req_destination_rules': {
            'min_timedelta': 100
        },
        'exact_orders': False,
        'precalc_cost': True,
        'waves_distance': [
            {'wave': 'default', 'max_distance': 1},
            {'wave': 0, 'max_distance': 1000}
        ],
        'reorder_suggestion_interval': 120,
        'estimated_waiting_power_coef': 0.8,
        'check_contracts': False,
        'accepted_permit_issuers': ['moscow'],
        'center_tab': True,
        'exam_link': 'https://exam.ru'
    }

    data.update(update_data)

    response = django_test.Client().post(
        '/api/cities/save/',
        json.dumps(data),
        'application/json'
    )
    assert response.status_code == status_code


# Add new city
@pytest.mark.parametrize('data, expected_filename', [
    (
        {
            'id': 'Кишинев',
            'disabled': False,
            'country': 'mda',
            'eng': 'chisinau',
            'tl': [28.746126, 47.080211],
            'br': [28.969972, 46.923788],
            'tz': 'Europe/Chisinau  ',
            'donate_multiplier': '1.00',
            'donate_discounts_multiplier': '1.00',
            'support_phone': '+74957058888',
            'max_card_payment': 3200,
            'max_corp_payment': 20000,
            'app_download_short_link': '_link',
            'reorder_suggestion_interval': 120,
            'estimated_waiting_power_coef': 0.8,
            'check_contracts': False,
            'accepted_permit_issuers': ['moscow'],
            'exam_link': 'https://exam2.ru/',
            'center_tab': True
        },
        'default_create.json'
    ),
    (
        {
            'id': 'Кишинев',
            'disabled': False,
            'country': 'mda',
            'eng': 'chisinau',
            'tl': [28.746126, 47.080211],
            'br': [28.969972, 46.923788],
            'tz': 'Europe/Chisinau  ',
            'donate_multiplier': '1.00',
            'donate_discounts_multiplier': '1.00',
            'support_phone': '+74957058888',
            'max_card_payment': 3200,
            'max_corp_payment': 20000,
            'app_download_short_link': '_link',
            'reorder_suggestion_interval': 120,
            'estimated_waiting_power_coef': 0.8,
            'check_contracts': False,
            'accepted_permit_issuers': ['moscow'],
            'exam_link': 'https://exam2.ru/',
            'center_tab': True,
            'promocode_subvention_state': True,
        },
        'promo_state_on_create.json'
    ),
])
@pytest.mark.now('2019-10-07T00:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_api_cities_create(load, data, expected_filename):
    response = django_test.Client().get('/api/cities/save/')
    assert response.status_code == 405

    response = django_test.Client().post(
        '/api/cities/save/',
        json.dumps(data),
        'application/json',
    )
    assert response.status_code == 200

    response = json.loads(response.content)
    inserted_city = yield db.cities.find_one({'_id': response['id']})
    expected = json.loads(load(expected_filename))
    expected['updated'] = datetime.datetime(*expected['updated'])
    expected['promocode_subvention_periods'] = [
        [
            datetime.datetime(
                *expected['promocode_subvention_periods'][0][0]
            ),
            datetime.datetime(
                *expected['promocode_subvention_periods'][0][1]
            ),
        ]
    ]
    assert inserted_city == expected


# Modify existing city
@pytest.mark.now('2019-10-07T00:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_api_cities_save():
    response = django_test.Client().get('/api/cities/save/')
    assert response.status_code == 405

    almaty = {
        'id': 'Алматы',
        'disabled': False,
        'country': 'kaz',
        'eng': 'alma-ata',
        'tl': [76.721583, 43.430484],
        'br': [77.169417, 43.046116],
        'tz': 'Asia/Almaty',
        'support_phone': '+74957058888',
        'max_card_payment': 3200,
        'max_corp_payment': 20000,
        'donate_multiplier': '1.06',
        'app_download_short_link': '_link',
        'reorder_suggestion_interval': 120,
        'estimated_waiting_power_coef': 0.8,
        'check_contracts': False,
        'accepted_permit_issuers': ['moscow'],
        'exam_link': 'https://exam2.ru/',
        'center_tab': True,
        'promocode_subvention_state': False,
    }

    response = django_test.Client().post(
        '/api/cities/save/',
        json.dumps(almaty),
        'application/json',
    )
    assert response.status_code == 200

    response = json.loads(response.content)
    updated_city = yield db.cities.find_one({'_id': response['id']})

    assert updated_city['eng'] == 'alma-ata'
    assert updated_city['accepted_permit_issuers'] == ['moscow']
    assert updated_city['areas']['airport']['geometry'] == [
        [
            [
              77.0099,
              43.3451
            ],
            [
              77.0084,
              43.3474
            ],
            [
              77.0118,
              43.3487
            ],
            [
              77.0132,
              43.3457
            ],
            [
              77.0099,
              43.3451
            ]
        ]
    ]
    assert updated_city['exam_link'] == 'https://exam2.ru/'
    assert updated_city['center_tab'] is True
    assert updated_city['promocode_subvention_periods'] == [
        [
            datetime.datetime.min,
            datetime.datetime(2018, 12, 31, 23, 59, 59)
        ],
        [
            datetime.datetime.now(),
            datetime.datetime(9999, 12, 31, 23, 59, 59, 999000)
        ]
    ]


@pytest.mark.parametrize('params, expected_data', [
    (
        {'city_id': 'moscow'},
        {
            'items': [
                {
                    'id': 'another_city_zone_id',
                    'object': {
                        'full_text': 'Another City Zone',
                        'short_text': 'Another',
                        'country': 'Russia',
                        'city': 'Moscow',
                        'point': [37, 55],
                        'type': 'organization',
                        'object_type': 'some_object_type',
                    },
                    'object_locale': {},
                    'geometry': [
                        [[37, 55], [38, 55], [38, 56], [37, 56]],
                    ],
                },
                {
                    'id': 'existing_city_zone_id',
                    'object': {
                        'full_text': 'Existing City Zone',
                        'short_text': 'Existing',
                        'country': 'Russia',
                        'city': 'Moscow',
                        'point': [37, 55],
                        'type': 'organization',
                        'object_type': 'some_object_type',
                    },
                    'object_locale': {
                        'ru': {
                            'full_text': 'Existing City Zone',
                            'short_text': 'Existing',
                            'country': 'Russia',
                        }
                    },
                    'geometry': [
                        [[37, 55], [38, 55], [38, 56], [37, 56]],
                    ],
                },
            ],
        }
    ),
    (
        {
            'city_id': 'moscow',
            'limit': 1,
        },
        {
            'items': [
                {
                    'id': 'another_city_zone_id',
                    'object': {
                        'full_text': 'Another City Zone',
                        'short_text': 'Another',
                        'country': 'Russia',
                        'city': 'Moscow',
                        'point': [37, 55],
                        'type': 'organization',
                        'object_type': 'some_object_type',
                    },
                    'object_locale': {},
                    'geometry': [
                        [[37, 55], [38, 55], [38, 56], [37, 56]],
                    ],
                },
            ],
        }
    ),
    (
        {
            'city_id': 'moscow',
            'offset': 1,
        },
        {
            'items': [

                {
                    'id': 'existing_city_zone_id',
                    'object': {
                        'full_text': 'Existing City Zone',
                        'short_text': 'Existing',
                        'country': 'Russia',
                        'city': 'Moscow',
                        'point': [37, 55],
                        'type': 'organization',
                        'object_type': 'some_object_type',
                    },
                    'object_locale': {
                        'ru': {
                            'full_text': 'Existing City Zone',
                            'short_text': 'Existing',
                            'country': 'Russia',
                        }
                    },
                    'geometry': [
                        [[37, 55], [38, 55], [38, 56], [37, 56]],
                    ],
                },
            ],
        }
    ),
])
@pytest.mark.asyncenv('blocking')
def test_get_city_zones(params, expected_data):
    response = django_test.Client().get(
        '/api/cities/city_zones/list/',
        params,
    )
    assert response.status_code == 200
    assert json.loads(response.content) == expected_data


@pytest.mark.parametrize('method, params, expected_code', [
    ('post', {'city_id': 'moscow'}, 405),
    ('get', {}, 406),
    ('get', {'city_id': 'missing city'}, 404),
])
@pytest.mark.asyncenv('blocking')
def test_get_city_zones_fail(method, params, expected_code):
    assert method in ['get', 'post']

    if method == 'get':
        response = django_test.Client().get(
            '/api/cities/city_zones/list/',
            params,
        )
    elif method == 'post':
        response = django_test.Client().post(
            '/api/cities/city_zones/list/',
            json.dumps(params),
            'application/json',
        )

    assert response.status_code == expected_code


@pytest.mark.parametrize('params', [
    {
        'city_id': 'moscow',
        'object': {
            'full_text': 'New City Zone',
            'short_text': 'New',
            'country': 'Russia',
            'city': 'Moscow',
            'street': 'Red Square',
            'house': '1',
            'point': [37, 55],
            'type': 'organization',
            'object_type': 'some_object_type',
            'description': 'some description',
            'exact': True,
            'oid': 0,
            'accepts_exact5': True,
        },
        'object_locale': {
            'ru': {
                'full_text': 'New City Zone',
                'short_text': 'New',
                'country': 'Russia',
                'city': 'Moscow',
                'street': 'Red Square',
                'house': '1',
                'description': 'some description',
            }
        },
        'geometry': [
            [[37, 55], [38, 55], [38, 56], [37, 56]],
        ],
    },
])
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_post_city_zone(params):
    response = django_test.Client().post(
        '/api/cities/city_zones/create/',
        json.dumps(params),
        'application/json',
    )
    assert response.status_code == 200

    city = yield db.cities.find_one({'_id': params['city_id']})
    assert city
    assert 'geocoder_objects' in city

    params.pop('city_id')
    for obj in city['geocoder_objects']:
        obj.pop('id')
    assert params in city['geocoder_objects']


@pytest.mark.parametrize('params, expected_code', [
    (
        {
            'city_id': 'missing city',
            'object': {
                'full_text': 'New City Zone',
                'short_text': 'New',
                'country': 'Russia',
                'city': 'Moscow',
                'street': 'Red Square',
                'house': '1',
                'point': [37, 55],
                'type': 'organization',
                'object_type': 'some_object_type',
                'description': 'some description',
                'exact': True,
                'oid': 0,
                'accepts_exact5': True,
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
        },
        406,
    ),
    (
        {
            'city_id': 'moscow',
            'object': {
                'full_text': 'New City Zone',
                'country': 'Russia',
                'city': 'Moscow',
                'street': 'Red Square',
                'house': '1',
                'point': [37, 55],
                'type': 'organization',
                'object_type': 'some_object_type',
                'description': 'some description',
                'exact': True,
                'oid': 0,
                'accepts_exact5': True,
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
        },
        406,
    ),
    (
        {
            'city_id': 'moscow',
            'object': {
                'full_text': 'New City Zone',
                'short_text': 'New',
                'country': 'Russia',
                'city': 'Moscow',
                'street': 'Red Square',
                'house': '1',
                'type': 'organization',
                'object_type': 'some_object_type',
                'description': 'some description',
                'exact': True,
                'oid': 0,
                'accepts_exact5': True,
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
        },
        406,
    ),
])
@pytest.mark.asyncenv('blocking')
def test_post_city_zone_fail(params, expected_code):
    response = django_test.Client().post(
        '/api/cities/city_zones/create/',
        json.dumps(params),
        'application/json',
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize('city_zone_id, params', [
    (
        'existing_city_zone_id',
        {
            'city_id': 'moscow',
            'object': {
                'full_text': 'Renamed City Zone',
                'short_text': 'Renamed',
                'country': 'Russia',
                'city': 'Moscow',
                'point': [37, 55],
                'type': 'organization',
                'object_type': 'some_object_type',
            },
            'object_locale': {
                'ru': {
                    'full_text': 'Existing City Zone',
                    'short_text': 'Existing',
                    'country': 'Russia',
                }
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
        }
    ),
])
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_put_city_zone(city_zone_id, params):
    response = django_test.Client().put(
        '/api/cities/city_zones/{}/'.format(city_zone_id),
        json.dumps(params),
        'application/json',
    )
    assert response.status_code == 200

    city = yield db.cities.find_one({'_id': params['city_id']})
    assert city
    assert 'geocoder_objects' in city

    params.pop('city_id')
    for obj in city['geocoder_objects']:
        obj.pop('id')
    assert params in city['geocoder_objects']


@pytest.mark.parametrize('city_zone_id, params, expected_code', [
    (
        'existing_city_zone_id',
        {
            'city_id': 'missing city',
            'object': {
                'full_text': 'Renamed City Zone',
                'short_text': 'Renamed',
                'country': 'Russia',
                'city': 'Moscow',
                'street': 'Red Square',
                'house': '1',
                'point': [37, 55],
                'type': 'organization',
                'object_type': 'some_object_type',
                'description': 'some description',
                'exact': True,
                'oid': 0,
                'accepts_exact5': True,
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
        },
        406,
    ),
    (
        'existing_city_zone_id',
        {
            'city_id': 'moscow',
            'object': {
                'full_text': 'Renamed City Zone',
                'country': 'Russia',
                'city': 'Moscow',
                'street': 'Red Square',
                'house': '1',
                'point': [37, 55],
                'type': 'organization',
                'object_type': 'some_object_type',
                'description': 'some description',
                'exact': True,
                'oid': 0,
                'accepts_exact5': True,
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
        },
        406,
    ),
    (
        'existing_city_zone_id',
        {
            'city_id': 'moscow',
            'object': {
                'full_text': 'Renamed City Zone',
                'short_text': 'Renamed',
                'country': 'Russia',
                'city': 'Moscow',
                'street': 'Red Square',
                'house': '1',
                'type': 'organization',
                'object_type': 'some_object_type',
                'description': 'some description',
                'exact': True,
                'oid': 0,
                'accepts_exact5': True,
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
        },
        406,
    ),
    (
        'missing_city_zone_id',
        {
            'city_id': 'moscow',
            'object': {
                'full_text': 'Renamed City Zone',
                'short_text': 'Renamed',
                'country': 'Russia',
                'city': 'Moscow',
                'street': 'Red Square',
                'house': '1',
                'point': [37, 55],
                'type': 'organization',
                'object_type': 'some_object_type',
                'description': 'some description',
                'exact': True,
                'oid': 0,
                'accepts_exact5': True,
            },
            'object_locale': {
                'ru': {
                    'full_text': 'New City Zone',
                    'short_text': 'New',
                    'country': 'Russia',
                    'city': 'Moscow',
                    'street': 'Red Square',
                    'house': '1',
                    'description': 'some description',
                }
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
        },
        406,
    ),
])
@pytest.mark.asyncenv('blocking')
def test_put_city_zone_fail(city_zone_id, params, expected_code):
    response = django_test.Client().put(
        '/api/cities/city_zones/{}/'.format(city_zone_id),
        json.dumps(params),
        'application/json',
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize('city_zone_id', [
    ('existing_city_zone_id'),
])
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_delete_city_zone(city_zone_id):
    response = django_test.Client().delete(
        '/api/cities/city_zones/{}/'.format(city_zone_id),
    )
    assert response.status_code == 200

    city = yield db.cities.find_one({'geocoder_objects.id': city_zone_id})
    assert city is None


@pytest.mark.parametrize('city_zone_id, expected_code', [
    (
        'missing_city_zone_id',
        406,
    ),
])
@pytest.mark.asyncenv('blocking')
def test_delete_city_zone_fail(city_zone_id, expected_code):
    response = django_test.Client().delete(
        '/api/cities/city_zones/{}/'.format(city_zone_id),
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize('params, expected_data', [
    (
        {'city_id': 'moscow'},
        {
            'items': [
                {
                    'id': 'another_transfer_zone_id',
                    'name': {
                        'en': 'Another Transfer Zone',
                        'ru': 'Another Transfer Zone',
                        'ru_from': 'From Another Transfer Zone',
                        'ru_to': 'To Another Transfer Zone',
                    },
                    'geometry': [
                        [[37, 55], [38, 55], [38, 56], [37, 56]],
                    ],
                    'type': 'other',
                    'priority': 5,
                    'scope': {
                        'transfer': True,
                        'taximeter': True,
                    },
                },
                {
                    'id': 'existing_transfer_zone_id',
                    'name': {
                        'en': 'Existing Transfer Zone',
                        'ru': 'Existing Transfer Zone',
                        'ru_from': 'From Existing Transfer Zone',
                        'ru_to': 'To Existing Transfer Zone',
                    },
                    'geometry': [
                        [[37, 55], [38, 55], [38, 56], [37, 56]],
                    ],
                    'type': 'other',
                    'priority': 4,
                    'scope': {
                        'transfer': True,
                        'taximeter': True,
                    },
                },
                {
                    'id': 'suburb',
                    'name': {
                        'en': 'Suburb',
                        'ru': 'Suburb',
                        'ru_from': 'From suburb',
                        'ru_to': 'To suburb',
                    },
                    'geometry': [
                        [[37, 55], [38, 55], [38, 56], [37, 56]],
                    ],
                    'type': 'airport',
                    'priority': 3,
                    'scope': {
                        'transfer': True,
                        'taximeter': True,
                    },
                },
            ],
        }
    ),
])
@pytest.mark.asyncenv('blocking')
def test_get_transfer_zones(params, expected_data):
    response = django_test.Client().get(
        '/api/cities/transfer_zones/list/',
        params,
    )
    assert response.status_code == 200
    assert json.loads(response.content) == expected_data


@pytest.mark.parametrize('method, params, expected_code', [
    ('post', {'city_id': 'moscow'}, 405),
    ('get', {}, 406),
    ('get', {'city_id': 'missing city'}, 404),
])
@pytest.mark.asyncenv('blocking')
def test_get_transfer_zones_fail(method, params, expected_code):
    assert method in ['get', 'post']

    if method == 'get':
        response = django_test.Client().get(
            '/api/cities/transfer_zones/list/',
            params,
        )
    elif method == 'post':
        response = django_test.Client().post(
            '/api/cities/transfer_zones/list/',
            json.dumps(params),
            'application/json',
        )

    assert response.status_code == expected_code


@pytest.mark.parametrize('params', [
    {
        'city_id': 'moscow',
        'name': {
            'en': 'New Transfer Zone',
            'ru': 'New Transfer Zone',
            'ru_from': 'From New Transfer Zone',
            'ru_to': 'To New Transfer Zone',
        },
        'geometry': [
            [[37, 55], [38, 55], [38, 56], [37, 56]],
        ],
        'type': 'other',
        'priority': 9,
        'scope': {
            'transfer': True,
            'taximeter': True,
        },
    },
])
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_post_transfer_zone(params):
    response = django_test.Client().post(
        '/api/cities/transfer_zones/create/',
        json.dumps(params),
        'application/json',
    )
    assert response.status_code == 200
    content = json.loads(response.content)
    transfer_zone_id = content['id']

    city = yield db.cities.find_one({'_id': params['city_id']})
    assert city
    assert transfer_zone_id in city['areas']

    params.pop('city_id')
    assert params == city['areas'][transfer_zone_id]


@pytest.mark.parametrize('params, expected_code', [
    (
        {
            'city_id': 'missing_city_id',  # city does not exist
            'name': {
                'en': 'New Transfer Zone',
                'ru': 'New Transfer Zone',
                'ru_from': 'From New Transfer Zone',
                'ru_to': 'To New Transfer Zone',
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'other',
            'priority': 5,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        # name.ru_from not set
        {
            'city_id': 'moscow',
            'name': {
                'en': 'New Transfer Zone',
                'ru': 'New Transfer Zone',
                'ru_to': 'To New Transfer Zone',
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'other',
            'priority': 5,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        # geometry not set
        {
            'city_id': 'moscow',
            'name': {
                'en': 'New Transfer Zone',
                'ru': 'New Transfer Zone',
                'ru_from': 'From New Transfer Zone',
                'ru_to': 'To New Transfer Zone',
            },
            'type': 'airport',
            'priority': 5,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        # type not set
        {
            'city_id': 'moscow',
            'name': {
                'en': 'New Transfer Zone',
                'ru': 'New Transfer Zone',
                'ru_from': 'From New Transfer Zone',
                'ru_to': 'To New Transfer Zone',
            },
            'priority': 5,
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        {
            'city_id': 'moscow',
            'name': {
                'en': 'New Transfer Zone',
                'ru': 'New Transfer Zone',
                'ru_from': 'From New Transfer Zone',
                'ru_to': 'To New Transfer Zone',
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'bad_type',  # not in ['airport', 'other']
            'priority': 5,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        {
            'city_id': 'moscow',
            'name': {
                'en': 'New Transfer Zone',
                'ru': 'New Transfer Zone',
                'ru_from': 'From New Transfer Zone',
                'ru_to': 'To New Transfer Zone',
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'other',
            'priority': 15,  # greater than 9
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        {
            'city_id': 'moscow',
            'name': {
                'en': 'New Transfer Zone',
                'ru': 'New Transfer Zone',
                'ru_from': 'From New Transfer Zone',
                'ru_to': 'To New Transfer Zone',
            },
            'geometry': [
                [[33, 55], [38, 55], [38, 56], [37, 56]],  # exceeds tl,br
            ],
            'type': 'other',
            'priority': 9,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
])
@pytest.mark.asyncenv('blocking')
def test_post_transfer_zone_fail(params, expected_code):
    response = django_test.Client().post(
        '/api/cities/transfer_zones/create/',
        json.dumps(params),
        'application/json',
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize('transfer_zone_id, params', [
    (
        'existing_transfer_zone_id',
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Renamed Transfer Zone',
                'ru': 'Renamed Transfer Zone',
                'ru_from': 'From Renamed Transfer Zone',
                'ru_to': 'To Renamed Transfer Zone',
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'other',
            'priority': 5,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
    ),
])
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_put_transfer_zone(transfer_zone_id, params):
    response = django_test.Client().put(
        '/api/cities/transfer_zones/{}/'.format(transfer_zone_id),
        json.dumps(params),
        'application/json',
    )
    assert response.status_code == 200

    city = yield db.cities.find_one({'_id': params['city_id']})
    assert city
    assert transfer_zone_id in city['areas']

    params.pop('city_id')
    assert params == city['areas'][transfer_zone_id]


@pytest.mark.parametrize('transfer_zone_id, params, expected_code', [
    (
        'existing_transfer_zone_id',
        {
            'city_id': 'missing_city_id',  # city does not exist
            'name': {
                'en': 'Renamed Transfer Zone',
                'ru': 'Renamed Transfer Zone',
                'ru_from': 'From Renamed Transfer Zone',
                'ru_to': 'To Renamed Transfer Zone',
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'other',
            'priority': 5,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        # name.ru_from not set
        'existing_transfer_zone_id',
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Renamed Transfer Zone',
                'ru': 'Renamed Transfer Zone',
                'ru_to': 'To Renamed Transfer Zone',
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'other',
            'priority': 5,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        # geometry not set
        'existing_transfer_zone_id',
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Renamed Transfer Zone',
                'ru': 'Renamed Transfer Zone',
                'ru_from': 'From Renamed Transfer Zone',
                'ru_to': 'To Renamed Transfer Zone',
            },
            'type': 'airport',
            'priority': 5,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        # type not set
        'existing_transfer_zone_id',
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Renamed Transfer Zone',
                'ru': 'Renamed Transfer Zone',
                'ru_from': 'From Renamed Transfer Zone',
                'ru_to': 'To Renamed Transfer Zone',
            },
            'priority': 5,
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        'existing_transfer_zone_id',
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Renamed Transfer Zone',
                'ru': 'Renamed Transfer Zone',
                'ru_from': 'From Renamed Transfer Zone',
                'ru_to': 'To Renamed Transfer Zone',
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'bad_type',  # not in ['airport', 'other']
            'priority': 5,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        'existing_transfer_zone_id',
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Renamed Transfer Zone',
                'ru': 'Renamed Transfer Zone',
                'ru_from': 'From Renamed Transfer Zone',
                'ru_to': 'To Renamed Transfer Zone',
            },
            'object_locale': {},
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'other',
            'priority': 15,  # greater than 9
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        'existing_transfer_zone_id',
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Renamed Transfer Zone',
                'ru': 'Renamed Transfer Zone',
                'ru_from': 'From Renamed Transfer Zone',
                'ru_to': 'To Renamed Transfer Zone',
            },
            'geometry': [
                [[33, 55], [38, 55], [38, 56], [37, 56]],  # exceeds tl,br
            ],
            'type': 'other',
            'priority': 9,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        'suburb',
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Suburb',
                'ru': 'Suburb',
                'ru_from': 'From suburb',
                'ru_to': 'To suburb',
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'other',  # cannot be changed
            'priority': 3,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
    (
        'suburb',
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Suburb',
                'ru': 'Suburb',
                'ru_from': 'From suburb',
                'ru_to': 'To suburb',
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'airport',
            'priority': 3,
            'scope': {
                'transfer': False,  # cannot be changed
                'taximeter': True,
            },
        },
        406,
    ),
    (
        'missing_transfer_zone_id',  # must exist in city.areas
        {
            'city_id': 'moscow',
            'name': {
                'en': 'Renamed Transfer Zone',
                'ru': 'Renamed Transfer Zone',
                'ru_from': 'From Renamed Transfer Zone',
                'ru_to': 'To Renamed Transfer Zone',
            },
            'geometry': [
                [[37, 55], [38, 55], [38, 56], [37, 56]],
            ],
            'type': 'other',
            'priority': 9,
            'scope': {
                'transfer': True,
                'taximeter': True,
            },
        },
        406,
    ),
])
@pytest.mark.asyncenv('blocking')
def test_put_transfer_zone_fail(transfer_zone_id, params, expected_code):
    response = django_test.Client().put(
        '/api/cities/transfer_zones/{}/'.format(transfer_zone_id),
        json.dumps(params),
        'application/json',
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize('transfer_zone_id, params, expected_tl, expected_br',
    [
        (
            'existing_transfer_zone_id',
            {
                'city_id': 'moscow',
                'name': {
                    'en': 'Renamed Transfer Zone',
                    'ru': 'Renamed Transfer Zone',
                    'ru_from': 'From Renamed Transfer Zone',
                    'ru_to': 'To Renamed Transfer Zone',
                },
                'geometry': [
                    [[37.2, 55.2], [37.8, 55.2], [37.8, 55.8], [37.2, 55.8]],
                ],
                'type': 'other',
                'priority': 5,
                'scope': {
                    'transfer': True,
                    'taximeter': True,
                },
                'extend_tlbr': True,
            },
            [37, 56],
            [38, 55],
        ),
    ],
)
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_extend_tlbr(transfer_zone_id, params, expected_tl, expected_br):
    response = django_test.Client().put(
        '/api/cities/transfer_zones/{}/'.format(transfer_zone_id),
        json.dumps(params),
        'application/json',
    )
    assert response.status_code == 200

    city = yield db.cities.find_one({'_id': params['city_id']})
    assert city
    assert city['tl'] == expected_tl
    assert city['br'] == expected_br


@pytest.mark.parametrize('transfer_zone_id', [
    ('existing_transfer_zone_id'),
])
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_delete_transfer_zone(transfer_zone_id):
    response = django_test.Client().delete(
        '/api/cities/transfer_zones/{}/'.format(transfer_zone_id),
    )
    assert response.status_code == 200

    city = yield db.cities.find_one(
        {
            'areas.{}'.format(transfer_zone_id): {
                '$exists': True,
            },
        },
    )
    assert city is None


@pytest.mark.parametrize('transfer_zone_id, expected_code', [
    (
        'missing_transfer_zone_id',
        406,
    ),
])
@pytest.mark.asyncenv('blocking')
def test_delete_transfer_zone_fail(transfer_zone_id, expected_code):
    response = django_test.Client().delete(
        '/api/cities/transfer_zones/{}/'.format(transfer_zone_id),
    )
    assert response.status_code == expected_code
