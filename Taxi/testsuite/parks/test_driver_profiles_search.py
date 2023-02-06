# encoding=utf-8
import json

import pytest

from taxi_tests.utils import ordered_object


TESTPARAMS_OK = [
    # 0
    (
        {'query': {'park': {'id': ['222333']}}, 'fields': {'park': ['_id']}},
        {
            'profiles': [
                {'driver': {'id': 'driverSS10'}, 'park': {'id': '222333'}},
                {'driver': {'id': 'absent-car'}, 'park': {'id': '222333'}},
                {'driver': {'id': 'superDriver'}, 'park': {'id': '222333'}},
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 1
    (
        {
            'query': {'park': {'id': ['222333']}},
            'fields': {'driver': ['_id', 'park_id', 'balance', 'driver_id']},
        },
        {
            'profiles': [
                {'driver': {'id': 'driverSS10'}, 'park': {'id': '222333'}},
                {'driver': {'id': 'absent-car'}, 'park': {'id': '222333'}},
                {'driver': {'id': 'superDriver'}, 'park': {'id': '222333'}},
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 2
    (
        {
            'query': {'park': {'id': ['222333']}},
            'fields': {
                'park': ['_id'],
                'driver': ['_id', 'park_id', 'balance', 'driver_id'],
            },
        },
        {
            'profiles': [
                {'driver': {'id': 'driverSS10'}, 'park': {'id': '222333'}},
                {'driver': {'id': 'absent-car'}, 'park': {'id': '222333'}},
                {'driver': {'id': 'superDriver'}, 'park': {'id': '222333'}},
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 3
    (
        {
            'query': {'park': {'id': ['222333']}},
            'fields': {
                'park': ['abrakadabra#I'],
                'driver': ['abrakadabra#1', 'abrakadabra#2'],
                'account': ['abrakadabra#X'],
            },
        },
        {
            'profiles': [
                {
                    'driver': {'id': 'driverSS10'},
                    'park': {'id': '222333'},
                    'accounts': [{}],
                },
                {
                    'driver': {'id': 'absent-car'},
                    'park': {'id': '222333'},
                    'accounts': [{}],
                },
                {
                    'driver': {'id': 'superDriver'},
                    'park': {'id': '222333'},
                    'accounts': [{}],
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 4
    (
        {
            'query': {'park': {'id': ['222333']}},
            'fields': {'driver': ['id', 'first_name']},
        },
        {
            'profiles': [
                {
                    'driver': {'id': 'superDriver', 'first_name': 'Антон'},
                    'park': {'id': '222333'},
                },
                {
                    'driver': {'id': 'absent-car', 'first_name': 'Anton'},
                    'park': {'id': '222333'},
                },
                {
                    'driver': {'id': 'driverSS10', 'first_name': 'Андрей'},
                    'park': {'id': '222333'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 5
    (
        {
            'query': {'driver': {'id': ['superDriver']}},
            'fields': {
                'park': ['id', 'city', 'created_date'],
                'driver': ['id', 'last_name', 'birth_date'],
                'account': ['id', 'type', 'balance', 'currency'],
            },
        },
        {
            'profiles': [
                {
                    'park': {
                        'id': '222333',
                        'city': 'Париж',
                        'created_date': '2018-08-29T08:04:14.517+0000',
                    },
                    'driver': {
                        'id': 'superDriver',
                        'last_name': 'Тодуа',
                        'birth_date': '1994-01-01T07:15:13+0000',
                    },
                    'accounts': [
                        {
                            'id': 'superDriver',
                            'type': 'current',
                            'balance': '13.7200',
                            'currency': 'EUR',
                        },
                    ],
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 6
    (
        {
            'query': {'driver': {'phone': ['+79104607457', '+79575775757']}},
            'fields': {
                'park': ['id', 'city', 'created_date'],
                'driver': ['id', 'last_name', 'phones'],
                'account': ['id', 'type', 'balance', 'currency'],
            },
        },
        {
            'profiles': [
                {
                    'park': {
                        'id': '222333',
                        'city': 'Париж',
                        'created_date': '2018-08-29T08:04:14.517+0000',
                    },
                    'driver': {
                        'id': 'superDriver',
                        'last_name': 'Тодуа',
                        'phones': ['+79104607457', '+79575775757'],
                    },
                    'accounts': [
                        {
                            'id': 'superDriver',
                            'type': 'current',
                            'balance': '13.7200',
                            'currency': 'EUR',
                        },
                    ],
                },
            ],
        },
        {'retrieve': 2, 'find': 1},
    ),
    # 7
    (
        {
            'query': {'driver': {'license': ['7211050505']}},
            'fields': {
                'park': ['id', 'city', 'created_date'],
                'driver': ['id', 'last_name'],
                'account': ['id', 'type', 'balance', 'currency'],
            },
        },
        {
            'profiles': [
                {
                    'park': {
                        'id': '222333',
                        'city': 'Париж',
                        'created_date': '2018-08-29T08:04:14.517+0000',
                    },
                    'driver': {'id': 'superDriver', 'last_name': 'Тодуа'},
                    'accounts': [
                        {
                            'id': 'superDriver',
                            'type': 'current',
                            'balance': '13.7200',
                            'currency': 'EUR',
                        },
                    ],
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 8
    (
        {
            'query': {'account': {'id': ['superDriver']}},
            'fields': {
                'park': ['id', 'city', 'created_date'],
                'driver': ['id', 'last_name', 'affiliation'],
                'account': ['id', 'type', 'balance', 'currency'],
            },
        },
        {
            'profiles': [
                {
                    'park': {
                        'id': '222333',
                        'city': 'Париж',
                        'created_date': '2018-08-29T08:04:14.517+0000',
                    },
                    'driver': {'id': 'superDriver', 'last_name': 'Тодуа'},
                    'accounts': [
                        {
                            'id': 'superDriver',
                            'type': 'current',
                            'balance': '13.7200',
                            'currency': 'EUR',
                        },
                    ],
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 9
    (
        {
            'query': {
                'driver': {'id': ['superDriver']},
                'account': {'id': ['superDriver']},
            },
            'fields': {
                'park': ['id', 'city', 'created_date'],
                'driver': ['id', 'last_name', 'affiliation'],
                'account': ['id', 'type', 'balance', 'currency'],
            },
        },
        {
            'profiles': [
                {
                    'park': {
                        'id': '222333',
                        'city': 'Париж',
                        'created_date': '2018-08-29T08:04:14.517+0000',
                    },
                    'driver': {'id': 'superDriver', 'last_name': 'Тодуа'},
                    'accounts': [
                        {
                            'id': 'superDriver',
                            'type': 'current',
                            'balance': '13.7200',
                            'currency': 'EUR',
                        },
                    ],
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 10
    (
        {
            'query': {
                'driver': {'id': ['driverSS10']},
                'account': {'id': ['superDriver']},
            },
            'fields': {
                'park': ['id', 'city', 'created_date'],
                'driver': ['id', 'last_name', 'affiliation'],
                'account': ['id', 'type', 'balance', 'currency'],
            },
        },
        {'profiles': []},
        {'retrieve': 1, 'find': 0},
    ),
    # 11
    (
        {
            'query': {'driver': {'id': ['driverSS10', 'superDriver']}},
            'fields': {'account': ['id', 'balance']},
        },
        {
            'profiles': [
                {
                    'driver': {'id': 'superDriver'},
                    'park': {'id': '222333'},
                    'accounts': [{'id': 'superDriver', 'balance': '13.7200'}],
                },
                {
                    'driver': {'id': 'driverSS10'},
                    'park': {'id': '222333'},
                    'accounts': [{'id': 'driverSS10', 'balance': '501.0000'}],
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 12
    (
        {
            'query': {'driver': {'car_id': ['Gelendewagen', 'ХУ23423O']}},
            'fields': {'account': ['id', 'balance']},
        },
        {
            'profiles': [
                {
                    'accounts': [{'balance': '13.7200', 'id': 'superDriver'}],
                    'driver': {'id': 'superDriver'},
                    'park': {'id': '222333'},
                },
                {
                    'accounts': [{'balance': '987.0000', 'id': 'driverSS'}],
                    'driver': {'id': 'driverSS'},
                    'park': {'id': '1488'},
                },
                {
                    'accounts': [
                        {
                            'balance': '100.0000',
                            'id': 'driver_se_1_affiliation',
                        },
                    ],
                    'affiliation': {
                        'partner_source': 'self_employed',
                        'state': 'accepted',
                    },
                    'driver': {'id': 'driver_se_1_affiliation'},
                    'park': {'id': '1488'},
                },
                {
                    'accounts': [
                        {'balance': '100.0000', 'id': 'driver_se_2_original'},
                    ],
                    'driver': {'id': 'driver_se_2_original'},
                    'park': {'id': 'park_se_1'},
                },
                {
                    'accounts': [
                        {'balance': '100.0000', 'id': 'driver_ie_1_original'},
                    ],
                    'driver': {'id': 'driver_ie_1_original'},
                    'park': {'id': 'park_ie_1'},
                },
                {
                    'accounts': [{'balance': '100.0000', 'id': 'driver'}],
                    'driver': {'id': 'driver'},
                    'park': {'id': '1488'},
                },
                {
                    'accounts': [
                        {
                            'balance': '100.0000',
                            'id': 'driver_ie_1_affiliation',
                        },
                    ],
                    'affiliation': {
                        'partner_source': 'individual_entrepreneur',
                        'state': 'active',
                    },
                    'driver': {'id': 'driver_ie_1_affiliation'},
                    'park': {'id': '1488'},
                },
                {
                    'accounts': [
                        {'balance': '100.0000', 'id': 'driver_ie_2_original'},
                    ],
                    'driver': {'id': 'driver_ie_2_original'},
                    'park': {'id': 'park_ie_2'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 13
    (
        {
            'query': {'park': {'id': ['1488']}},
            'fields': {'driver': ['id']},
            'limit': 1,
        },
        {
            'has_more': True,
            'profiles': [{'driver': {'id': 'Low'}, 'park': {'id': '1488'}}],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 14
    (
        {
            'query': {'park': {'id': ['1488']}},
            'fields': {'driver': ['id']},
            'offset': 2,
            'limit': 2,
        },
        {
            'has_more': True,
            'profiles': [
                {'driver': {'id': 'NoLimit'}, 'park': {'id': '1488'}},
                {'driver': {'id': 'driverSS9'}, 'park': {'id': '1488'}},
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 15
    (
        {
            'query': {'park': {'id': ['1488']}},
            'fields': {'driver': ['id']},
            'offset': 9,
            'limit': 3,
        },
        {
            'has_more': True,
            'profiles': [
                {'driver': {'id': 'driverSS3'}, 'park': {'id': '1488'}},
                {'driver': {'id': 'driverSS2'}, 'park': {'id': '1488'}},
                {'driver': {'id': 'driverSS1'}, 'park': {'id': '1488'}},
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 16
    (
        {
            'query': {'park': {'id': ['1488']}},
            'fields': {'driver': ['id']},
            'offset': 13,
        },
        {
            'profiles': [
                {'driver': {'id': 'driver'}, 'park': {'id': '1488'}},
                {
                    'affiliation': {
                        'partner_source': 'self_employed',
                        'state': 'new',
                    },
                    'driver': {'id': 'driver_se_2_affiliation'},
                    'park': {'id': '1488'},
                },
                {
                    'affiliation': {
                        'partner_source': 'individual_entrepreneur',
                        'state': 'active',
                    },
                    'driver': {'id': 'driver_ie_2_affiliation'},
                    'park': {'id': '1488'},
                },
                {
                    'affiliation': {
                        'partner_source': 'self_employed',
                        'state': 'accepted',
                    },
                    'driver': {'id': 'driver_se_1_affiliation'},
                    'park': {'id': '1488'},
                },
                {
                    'affiliation': {
                        'partner_source': 'individual_entrepreneur',
                        'state': 'active',
                    },
                    'driver': {'id': 'driver_ie_1_affiliation'},
                    'park': {'id': '1488'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 17
    (
        {
            'query': {'park': {'id': ['1488']}},
            'fields': {'driver': ['id']},
            'offset': 18,
        },
        {'profiles': []},
        {'retrieve': 1, 'find': 0},
    ),
    # 18
    (
        {
            'query': {'park': {'id': ['1488']}},
            'fields': {'driver': ['id']},
            'offset': 999,
            'limit': 500,
        },
        {'has_more': False, 'profiles': []},
        {'retrieve': 1, 'find': 0},
    ),
    # 19
    (
        {
            'query': {'park': {'id': ['222333']}},
            'fields': {'driver': ['self_employment_request_date']},
        },
        {
            'profiles': [
                {
                    'driver': {
                        'id': 'driverSS10',
                        'self_employment_request_date': (
                            '2019-02-11T10:00:00.123+0000'
                        ),
                    },
                    'park': {'id': '222333'},
                },
                {
                    'driver': {
                        'id': 'superDriver',
                        'self_employment_request_date': (
                            '2019-03-11T10:00:00.999+0000'
                        ),
                    },
                    'park': {'id': '222333'},
                },
                {'driver': {'id': 'absent-car'}, 'park': {'id': '222333'}},
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 20
    (
        {
            'query': {'park': {'id': ['222333']}},
            'fields': {'driver': ['id', 'additional_experiments']},
        },
        {
            'profiles': [
                {
                    'driver': {
                        'id': 'driverSS10',
                        'additional_experiments': [
                            'experimentOne',
                            'experimentTwo',
                        ],
                    },
                    'park': {'id': '222333'},
                },
                {
                    'driver': {
                        'id': 'superDriver',
                        'additional_experiments': [],
                    },
                    'park': {'id': '222333'},
                },
                {'driver': {'id': 'absent-car'}, 'park': {'id': '222333'}},
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 21
    (
        {
            'query': {'park': {'id': ['222777']}},
            'fields': {
                'driver': [
                    'id',
                    'self_employment_request_date',
                    'additional_experiments',
                ],
            },
        },
        {
            'profiles': [
                {'driver': {'id': '1234abcd'}, 'park': {'id': '222777'}},
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 22
    (
        {
            'query': {'driver': {'license_normalized': ['1234451451']}},
            'fields': {'driver': ['id', 'license', 'license_normalized']},
        },
        {
            'profiles': [
                {
                    'driver': {
                        'id': '1234abcd',
                        'license': '1234451451',
                        'license_normalized': '1234451451',
                    },
                    'park': {'id': '222777'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 23
    (
        {
            'query': {'driver': {'platform_uid': ['driverSS3_uid']}},
            'fields': {
                'park': ['id', 'city', 'created_date'],
                'driver': ['id', 'last_name'],
                'account': ['id', 'type', 'balance', 'currency'],
            },
        },
        {
            'profiles': [
                {
                    'accounts': [
                        {
                            'balance': '1000.0000',
                            'currency': 'RUB',
                            'id': 'driverSS3',
                            'type': 'current',
                        },
                    ],
                    'driver': {'id': 'driverSS3', 'last_name': 'Мироненко'},
                    'park': {'city': 'Москва', 'id': '1488'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 24
    (
        {
            'query': {'driver': {'platform_uid': ['uid_ie_se']}},
            'fields': {'park': ['id'], 'driver': ['id']},
        },
        {
            'profiles': [
                {
                    'driver': {'id': 'driver_ie_1_original'},
                    'park': {'id': 'park_ie_1'},
                },
                {
                    'affiliation': {
                        'partner_source': 'individual_entrepreneur',
                        'state': 'active',
                    },
                    'driver': {'id': 'driver_ie_1_affiliation'},
                    'park': {'id': '1488'},
                },
                {
                    'driver': {'id': 'driver_ie_2_original'},
                    'park': {'id': 'park_ie_2'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 25
    (
        {
            'query': {
                'driver': {
                    'platform_uid': ['uid_ie_se'],
                    'rule_id': ['rule_two'],
                },
            },
            'fields': {'park': ['id'], 'driver': ['id']},
        },
        {
            'profiles': [
                {
                    'driver': {'id': 'driver_ie_2_original'},
                    'park': {'id': 'park_ie_2'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 26
    (
        {
            'query': {
                'driver': {
                    'platform_uid': ['uid_ie_se'],
                    'license_normalized': ['AA285554488'],
                },
            },
            'fields': {'park': ['id'], 'driver': ['id']},
        },
        {
            'profiles': [
                {
                    'affiliation': {
                        'partner_source': 'individual_entrepreneur',
                        'state': 'active',
                    },
                    'driver': {'id': 'driver_ie_1_affiliation'},
                    'park': {'id': '1488'},
                },
                {
                    'driver': {'id': 'driver_ie_1_original'},
                    'park': {'id': 'park_ie_1'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 27
    (
        {
            'query': {'driver': {'license_normalized': ['AA285554432']}},
            'fields': {'driver': ['id', 'affiliation']},
        },
        {
            'profiles': [
                {
                    'driver': {'id': 'driver_ie_2_original'},
                    'park': {'id': 'park_ie_2'},
                },
                {
                    'affiliation': {
                        'partner_source': 'individual_entrepreneur',
                        'state': 'active',
                    },
                    'driver': {'id': 'driver_ie_2_affiliation'},
                    'park': {'id': '1488'},
                },
                {
                    'affiliation': {
                        'partner_source': 'self_employed',
                        'state': 'accepted',
                    },
                    'driver': {'id': 'driver_se_1_affiliation'},
                    'park': {'id': '1488'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 28
    (
        {
            'query': {
                'park': {'id': ['1488']},
                'driver': {'car_id': ['ХУ234239']},
            },
            'fields': {'driver': ['id', 'affiliation']},
        },
        {
            'profiles': [
                {
                    'affiliation': {
                        'partner_source': 'individual_entrepreneur',
                        'state': 'active',
                    },
                    'driver': {'id': 'driver_ie_2_affiliation'},
                    'park': {'id': '1488'},
                },
            ],
        },
        {'retrieve': 1, 'find': 0},
    ),
    # 29
    (
        {
            'query': {'driver': {'phone': ['+70004607457']}},
            'fields': {
                'park': ['id', 'city', 'created_date'],
                'driver': ['id', 'last_name'],
                'account': ['id', 'type', 'balance', 'currency'],
            },
        },
        {'profiles': []},
        {'retrieve': 1, 'find': 1},
    ),
]


@pytest.mark.parametrize(
    'request_json,expected_response,mock_calls', TESTPARAMS_OK,
)
def test_ok(
        taxi_parks,
        request_json,
        expected_response,
        mock_calls,
        personal_phones_bulk_find,
        personal_phones_bulk_retrieve,
):
    response = taxi_parks.post(
        '/driver-profiles/search', data=json.dumps(request_json),
    )

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_response, ['profiles'])

    assert personal_phones_bulk_find.times_called == mock_calls['find']
    assert personal_phones_bulk_retrieve.times_called == mock_calls['retrieve']


TESTPARAMS_400 = [
    ({}, {'error': {'text': 'object query must be present'}}),
    ({'query': []}, {'error': {'text': 'object query must be present'}}),
    (
        {'query': {'park': []}},
        {'error': {'text': 'query.park must have an object type'}},
    ),
    (
        {'query': {'park': {'id': 7}}},
        {
            'error': {
                'text': 'query.park.id must have an array of strings type',
            },
        },
    ),
    (
        {'query': {'park': {'id': '777'}}},
        {
            'error': {
                'text': 'query.park.id must have an array of strings type',
            },
        },
    ),
    (
        {
            'query': {
                'park': {'abra': 1.13},
                'driver': {'kadabra': 'abc'},
                'account': {'city': []},
                'profile': 14,
            },
        },
        {
            'error': {
                'text': (
                    'at least one of park.id, driver.id, driver.car_id,'
                    ' driver.rule_id, driver.phone, driver.platform_uid,'
                    ' driver.license, driver.license_normalized,'
                    ' driver.last_name, driver.work_status,'
                    ' account.id must be present in query'
                ),
            },
        },
    ),
    (
        {'query': {'driver': {'phone': ['+79104607457']}}},
        {'error': {'text': 'object fields must be present'}},
    ),
    (
        {'query': {'driver': {'phone': ['+79104607457']}}, 'fields': []},
        {'error': {'text': 'object fields must be present'}},
    ),
    (
        {
            'query': {'driver': {'phone': ['+79104607457']}},
            'fields': {'account': {}},
        },
        {'error': {'text': 'fields.account must have an array type'}},
    ),
    (
        {
            'query': {'driver': {'phone': ['+79104607457']}},
            'fields': {'driver': [1]},
        },
        {'error': {'text': 'fields.driver element must have a string type'}},
    ),
    (
        {
            'query': {'driver': {'phone': ['+79104607457']}},
            'fields': {'driver': ['id', 'id']},
        },
        {
            'error': {
                'text': (
                    'fields.driver must contain unique non-empty values'
                    ' (error at `id`)'
                ),
            },
        },
    ),
    (
        {'query': {'driver': {'phone': ['+79104607457']}}, 'fields': {}},
        {
            'error': {
                'text': (
                    'at least one field of park, driver, account '
                    'must be present in fields'
                ),
            },
        },
    ),
    (
        {
            'query': {'driver': {'phone': ['+79104607457']}},
            'fields': {'park': [], 'driver': [], 'account': []},
        },
        {
            'error': {
                'text': (
                    'at least one field of park, driver, account '
                    'must be present in fields'
                ),
            },
        },
    ),
    (
        {
            'query': {'driver': {'phone': ['+79104607457']}},
            'fields': {'park': ['id']},
            'limit': 'a',
        },
        {'error': {'text': 'limit must have integer value between 1 and 500'}},
    ),
    (
        {
            'query': {'driver': {'phone': ['+79104607457']}},
            'fields': {'park': ['id']},
            'limit': 0,
        },
        {'error': {'text': 'limit must have integer value between 1 and 500'}},
    ),
    (
        {
            'query': {'driver': {'phone': ['+79104607457']}},
            'fields': {'park': ['id']},
            'limit': 501,
        },
        {'error': {'text': 'limit must have integer value between 1 and 500'}},
    ),
    (
        {
            'query': {'driver': {'phone': ['+79104607457']}},
            'fields': {'park': ['id']},
            'offset': 'a',
        },
        {
            'error': {
                'text': (
                    'offset must have integer value'
                    ' between 0 and 2147483647'
                ),
            },
        },
    ),
    (
        {
            'query': {'driver': {'phone': ['+79104607457']}},
            'fields': {'park': ['id']},
            'offset': -1,
        },
        {
            'error': {
                'text': (
                    'offset must have integer value'
                    ' between 0 and 2147483647'
                ),
            },
        },
    ),
]


@pytest.mark.parametrize('request_json,expected_response', TESTPARAMS_400)
def test_bad_request(taxi_parks, request_json, expected_response):
    response = taxi_parks.post(
        '/driver-profiles/search', data=json.dumps(request_json),
    )

    assert response.status_code == 400
    assert response.json() == expected_response


TEST_USE_PD_PHONES_PARAMS = [
    (
        {
            'query': {'driver': {'phone': ['89031237321']}},
            'fields': {'driver': ['id', 'phones']},
        },
        {
            'profiles': [
                {
                    'driver': {
                        'id': 'NoPhonesDriver',
                        'phones': ['+79211237321', '89031237321'],
                    },
                    'park': {'id': '222333badpd'},
                },
            ],
        },
    ),
    (
        {
            'query': {'driver': {'id': ['NoPhonesDriver']}},
            'fields': {'driver': ['id', 'phones']},
        },
        {
            'profiles': [
                {
                    'driver': {
                        'id': 'NoPhonesDriver',
                        'phones': ['+79211237321', '89031237321'],
                    },
                    'park': {'id': '222333badpd'},
                },
            ],
        },
    ),
]


@pytest.mark.parametrize(
    'request_json, expected_response', TEST_USE_PD_PHONES_PARAMS,
)
def test_use_pd_phones(
        taxi_parks, request_json, expected_response, mock_personal_data,
):
    response = taxi_parks.post(
        '/driver-profiles/search', data=json.dumps(request_json),
    )

    assert response.status_code == 200
    assert response.json() == expected_response
