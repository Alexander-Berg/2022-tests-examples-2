# encoding=utf-8
import json

import pytest


def get_personal_caches_mock_response_for_test_ok(park_id, text):
    if text == '':
        return {'driver_profile_items': [], 'filter_status': 'empty'}

    if park_id == '1488':
        if text == 'ал +7 брандашмыг ив ни':
            return {'driver_profile_items': [], 'filter_status': 'filled'}
        if text == '3936525':
            return {
                'driver_profile_items': [{'driver_id': 'Low', 'rank': 4}],
                'filter_status': 'filled',
            }
        if text == 'Мироненко Андрей Иванович 89031234568 foo 289':
            return {'driver_profile_items': [], 'filter_status': 'filled'}
        if text == 'Мироненко Андрей Иванович 89031234568 м82о9289 foo':
            return {
                'driver_profile_items': [
                    {'driver_id': 'driverSS9', 'rank': 36},
                ],
                'filter_status': 'filled',
            }
        if text == 'AA285554433':
            return {
                'driver_profile_items': [{'driver_id': 'driver', 'rank': 10}],
                'filter_status': 'filled',
            }
        if text == 'андрЕй':
            return {
                'driver_profile_items': [
                    {'driver_id': 'driverSS3', 'rank': 4},
                    {'driver_id': 'driverSS9', 'rank': 4},
                    {'driver_id': 'driverSS2', 'rank': 4},
                    {'driver_id': 'driverSS', 'rank': 4},
                    {'driver_id': 'driverSS6', 'rank': 4},
                ],
                'filter_status': 'filled',
            }
        if text == 'андрЕй аЛЕкС':
            return {
                'driver_profile_items': [
                    {'driver_id': 'driverSS', 'rank': 5},
                    {'driver_id': 'driverSS2', 'rank': 5},
                    {'driver_id': 'driverSS6', 'rank': 5},
                ],
                'filter_status': 'filled',
            }
        if text == 'low +79163936525':
            return {
                'driver_profile_items': [{'driver_id': 'Low', 'rank': 1010}],
                'filter_status': 'filled',
            }
        if text == 'Николай Алекса':
            return {
                'driver_profile_items': [
                    {'driver_id': 'driverSS5', 'rank': 5},
                ],
                'filter_status': 'filled',
            }
        if text == 'a':
            return {
                'driver_profile_items': [
                    {'driver_id': 'driver', 'rank': 10},
                    {'driver_id': 'driver_ie_1_affiliation', 'rank': 10},
                    {'driver_id': 'driver_ie_2_affiliation', 'rank': 10},
                    {'driver_id': 'driver_se_1_affiliation', 'rank': 10},
                    {'driver_id': 'driver_se_2_affiliation', 'rank': 10},
                ],
                'filter_status': 'filled',
            }

    if park_id == '222333':
        if text == 'романОВИЧ':
            return {
                'driver_profile_items': [
                    {'driver_id': 'superDriver', 'rank': 5},
                ],
                'filter_status': 'filled',
            }
        if text == '77':
            return {
                'driver_profile_items': [
                    {'driver_id': 'superDriver', 'rank': 2},
                ],
                'filter_status': 'filled',
            }
        if text == 'гелик':
            return {
                'driver_profile_items': [
                    {'driver_id': 'superDriver', 'rank': 10},
                ],
                'filter_status': 'filled',
            }
        if text == 'в777ор77':
            return {
                'driver_profile_items': [
                    {'driver_id': 'superDriver', 'rank': 10},
                ],
                'filter_status': 'filled',
            }
        if text == '+7':
            return {'driver_profile_items': [], 'filter_status': 'filled'}

    if park_id == 'only_signalq_park1':
        if text == 'SIGNALQ1':
            return {
                'driver_profile_items': [
                    {'driver_id': 'signalq_0', 'rank': 10},
                ],
                'filter_status': 'filled',
            }
    assert False  # should mock response with test park_id and text


OK_PARAMS = [
    # limit, offset test
    # 1
    (
        {'query': {'park': {'id': '222333'}}, 'limit': 1},
        {
            'driver_profiles': [{'driver_profile': {'id': 'superDriver'}}],
            'parks': [{'id': '222333'}],
            'limit': 1,
            'offset': 0,
            'total': 3,
        },
    ),
    # 2
    (
        {'query': {'park': {'id': '222333'}}, 'limit': 1, 'offset': 1},
        {
            'driver_profiles': [{'driver_profile': {'id': 'absent-car'}}],
            'parks': [{'id': '222333'}],
            'limit': 1,
            'offset': 1,
            'total': 3,
        },
    ),
    # 3
    (
        {'query': {'park': {'id': '222333'}}, 'offset': 1},
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'absent-car'}},
                {'driver_profile': {'id': 'driverSS10'}},
            ],
            'parks': [{'id': '222333'}],
            'offset': 1,
            'total': 3,
        },
    ),
    # 4
    (
        {'query': {'park': {'id': '222333'}}, 'limit': 1, 'offset': 3},
        {
            'driver_profiles': [],
            'parks': [{'id': '222333'}],
            'limit': 1,
            'offset': 3,
            'total': 3,
        },
    ),
    # 5
    (
        {'query': {'park': {'id': '222333'}}, 'offset': 1534},
        {
            'driver_profiles': [],
            'parks': [{'id': '222333'}],
            'offset': 1534,
            'total': 3,
        },
    ),
    # 6
    # sort_order test
    (
        {'query': {'park': {'id': '222333'}}},
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'superDriver'}},
                {'driver_profile': {'id': 'absent-car'}},
                {'driver_profile': {'id': 'driverSS10'}},
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 7
    (
        {
            'query': {'park': {'id': '222333'}},
            'sort_order': [
                {'direction': 'asc', 'field': 'driver_profile.created_date'},
            ],
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'superDriver'}},
                {'driver_profile': {'id': 'absent-car'}},
                {'driver_profile': {'id': 'driverSS10'}},
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 8
    (
        {
            'query': {'park': {'id': '222333'}},
            'sort_order': [
                {'direction': 'asc', 'field': 'driver_profile.modified_date'},
            ],
            'fields': {'driver_profile': ['modified_date']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'absent-car',
                        'modified_date': '2018-11-01T11:04:14.517+0000',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'superDriver',
                        'modified_date': '2018-11-02T11:04:14.517+0000',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'driverSS10',
                        'modified_date': '2018-11-03T11:04:14.517+0000',
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 9
    (
        {
            'query': {'park': {'id': '222333'}},
            'sort_order': [
                {'direction': 'desc', 'field': 'driver_profile.modified_date'},
            ],
            'fields': {'driver_profile': ['modified_date']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'driverSS10',
                        'modified_date': '2018-11-03T11:04:14.517+0000',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'superDriver',
                        'modified_date': '2018-11-02T11:04:14.517+0000',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'absent-car',
                        'modified_date': '2018-11-01T11:04:14.517+0000',
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 10
    (
        {
            'query': {'park': {'id': '222333'}},
            'sort_order': [
                {'direction': 'desc', 'field': 'driver_profile.created_date'},
            ],
            'fields': {'driver_profile': ['created_date']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'driverSS10',
                        'created_date': '2018-11-20T02:04:14.517+0000',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'absent-car',
                        'created_date': '2018-11-19T11:04:14.517+0000',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'superDriver',
                        'created_date': '2018-11-19T10:04:14.517+0000',
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 11
    (
        {
            'query': {'park': {'id': '222333'}},
            'sort_order': [
                {'direction': 'desc', 'field': 'driver_profile.first_name'},
                {'direction': 'desc', 'field': 'driver_profile.created_date'},
            ],
            'fields': {'parks': [], 'driver_profile': [], 'account': []},
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'superDriver'}},
                {'driver_profile': {'id': 'driverSS10'}},
                {'driver_profile': {'id': 'absent-car'}},
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 12
    (
        {
            'query': {'park': {'id': '1488'}},
            'sort_order': [
                {'direction': 'asc', 'field': 'driver_profile.last_name'},
                {'direction': 'asc', 'field': 'driver_profile.first_name'},
                {'direction': 'desc', 'field': 'driver_profile.middle_name'},
                {'direction': 'desc', 'field': 'account.current.balance'},
                {'direction': 'desc', 'field': 'driver_profile.created_date'},
            ],
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver'}},
                {'driver_profile': {'id': 'driver_ie_1_affiliation'}},
                {'driver_profile': {'id': 'driver_ie_2_affiliation'}},
                {'driver_profile': {'id': 'driver_se_1_affiliation'}},
                {'driver_profile': {'id': 'driver_se_2_affiliation'}},
                {'driver_profile': {'id': 'NoLimit'}},
                {'driver_profile': {'id': 'Low'}},
                {'driver_profile': {'id': 'NulLimit'}},
                {'driver_profile': {'id': 'driverSS1'}},
                {'driver_profile': {'id': 'driverSS8'}},
                {'driver_profile': {'id': 'driverSS3'}},
                {'driver_profile': {'id': 'driverSS9'}},
                {'driver_profile': {'id': 'driverSS'}},
                {'driver_profile': {'id': 'driverSS6'}},
                {'driver_profile': {'id': 'driverSS2'}},
                {'driver_profile': {'id': 'driverSS7'}},
                {'driver_profile': {'id': 'driverSS4'}},
                {'driver_profile': {'id': 'driverSS5'}},
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 18,
        },
    ),
    # 13
    (
        {'query': {'park': {'id': 'test_search'}}, 'fields': {'car': ['id']}},
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'test_search_XX'},
                    'car': {'id': '1'},
                },
                {'driver_profile': {'id': 'test_search_YY'}},
                {
                    'driver_profile': {'id': 'test_search_ZZ'},
                    'car': {'id': '2'},
                },
            ],
            'parks': [{'id': 'test_search'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 14
    (
        {
            'query': {'park': {'id': 'test_search'}},
            'fields': {'car': ['id']},
            'sort_order': [{'direction': 'asc', 'field': 'car.call_sign'}],
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'test_search_XX'},
                    'car': {'id': '1'},
                },
                {
                    'driver_profile': {'id': 'test_search_ZZ'},
                    'car': {'id': '2'},
                },
                {'driver_profile': {'id': 'test_search_YY'}},
            ],
            'parks': [{'id': 'test_search'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 15
    (
        {
            'query': {'park': {'id': 'test_search'}},
            'fields': {'car': ['id']},
            'sort_order': [{'direction': 'desc', 'field': 'car.call_sign'}],
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'test_search_ZZ'},
                    'car': {'id': '2'},
                },
                {
                    'driver_profile': {'id': 'test_search_XX'},
                    'car': {'id': '1'},
                },
                {'driver_profile': {'id': 'test_search_YY'}},
            ],
            'parks': [{'id': 'test_search'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 16
    (
        {
            'query': {'park': {'id': 'test_search'}},
            'sort_order': [
                {'direction': 'asc', 'field': 'driver_profile.hire_date'},
            ],
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'test_search_ZZ'}},
                {'driver_profile': {'id': 'test_search_XX'}},
                {'driver_profile': {'id': 'test_search_YY'}},
            ],
            'parks': [{'id': 'test_search'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 17
    (
        {
            'query': {'park': {'id': 'test_search'}},
            'sort_order': [
                {'direction': 'desc', 'field': 'driver_profile.hire_date'},
            ],
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'test_search_YY'}},
                {'driver_profile': {'id': 'test_search_XX'}},
                {'driver_profile': {'id': 'test_search_ZZ'}},
            ],
            'parks': [{'id': 'test_search'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 18
    # fields test
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                },
            },
            'fields': {
                'park': ['id', 'name'],
                'driver_profile': [],
                'account': [],
            },
        },
        {
            'driver_profiles': [{'driver_profile': {'id': 'superDriver'}}],
            'parks': [{'id': '222333', 'name': 'Taxi71'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 19
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                },
            },
            'fields': {
                'driver_profile': ['_id', 'driver_id', 'park_id', 'balance'],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'superDriver', 'park_id': '222333'}},
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 20
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                },
            },
            'fields': {
                'park': ['id', 'name'],
                'driver_profile': ['license', 'car_id'],
                'account': ['id', 'type', 'balance', 'currency'],
                'car': [
                    '_id',
                    'amenities',
                    'brand',
                    'car_id',
                    'color',
                    'model',
                    'normalized_number',
                    'number',
                    'number_normalized',
                    'service',
                ],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'superDriver',
                        'license': {
                            'birth_date': '1994-01-01T07:15:13+0000',
                            'normalized_number': '7211050505',
                            'number': '7211050505',
                        },
                        'car_id': 'Gelendewagen',
                    },
                    'accounts': [
                        {
                            'id': 'superDriver',
                            'type': 'current',
                            'balance': '13.7200',
                            'currency': 'EUR',
                        },
                    ],
                    'car': {
                        'id': 'Gelendewagen',
                        'model': 'AMG G63',
                        'brand': 'Mercedes-Benz',
                        'color': 'Black',
                        'number': 'В777ОР77',
                        'normalized_number': 'B7770P77',
                        'amenities': ['wifi'],
                    },
                },
            ],
            'parks': [{'id': '222333', 'name': 'Taxi71'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 21
    # query test
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {'id': ['abra', 'ka', 'dabra']},
                },
            },
        },
        {
            'driver_profiles': [],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # 22
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {'work_rule_id': ['abra', 'kadabra']},
                },
            },
        },
        {
            'driver_profiles': [],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # 23
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {'work_status': ['abrakadabra']},
                },
            },
        },
        {
            'driver_profiles': [],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # 24
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'id': ['driver', 'driverSS', 'driverSSS'],
                    },
                },
            },
            'fields': {
                'driver_profile': [
                    'driver_license',
                    'license',
                    'license_country',
                    'license_driver_birth_date',
                    'license_expire_date',
                    'license_issue_date',
                    'license_normalized',
                ],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'driver_license': {
                            'birth_date': '1939-09-01T00:00:07+0000',
                            'country': 'rus',
                            'expiration_date': '2028-11-20T08:11:11+0000',
                            'issue_date': '2018-11-20T08:11:11+0000',
                            'normalized_number': 'xyz',
                            'number': 'М8-2О9/289',
                        },
                        'id': 'driverSS',
                        'license': {
                            'birth_date': '1939-09-01T00:00:07+0000',
                            'country': 'rus',
                            'expiration_date': '2028-11-20T08:11:11+0000',
                            'issue_date': '2018-11-20T08:11:11+0000',
                            'normalized_number': 'xyz',
                            'number': 'М8-2О9/289',
                        },
                    },
                },
                {
                    'driver_profile': {
                        'driver_license': {
                            'normalized_number': 'AA285554433',
                            'number': 'М8-2О9/289',
                        },
                        'id': 'driver',
                        'license': {
                            'normalized_number': 'AA285554433',
                            'number': 'М8-2О9/289',
                        },
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # 25
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'id': ['driverSS1', 'driverSS', 'driverSSS'],
                        'work_status': ['working'],
                    },
                },
            },
        },
        {
            'driver_profiles': [{'driver_profile': {'id': 'driverSS1'}}],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 26
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'id': ['driverSS1', 'driverSS', 'driverSSS'],
                        'work_status': ['working', 'fired'],
                    },
                },
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driverSS1'}},
                {'driver_profile': {'id': 'driverSS'}},
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # 27
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'work_rule_id': ['rule_one', 'rule_two', 'rule_three'],
                        'work_status': ['working'],
                    },
                },
            },
            'fields': {'driver_profile': ['work_status', 'work_rule_id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'NoLimit',
                        'work_rule_id': 'rule_one',
                        'work_status': 'working',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'driverSS9',
                        'work_rule_id': 'rule_two',
                        'work_status': 'working',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'driverSS7',
                        'work_rule_id': 'rule_two',
                        'work_status': 'working',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'driverSS6',
                        'work_rule_id': 'rule_three',
                        'work_status': 'working',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'driverSS1',
                        'work_rule_id': 'rule_one',
                        'work_status': 'working',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'driver',
                        'work_rule_id': 'rule_one',
                        'work_status': 'working',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'driver_ie_1_affiliation',
                        'work_rule_id': 'rule_one',
                        'work_status': 'working',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'driver_se_1_affiliation',
                        'work_rule_id': 'rule_three',
                        'work_status': 'working',
                    },
                },
                {
                    'driver_profile': {
                        'id': 'driver_se_2_affiliation',
                        'work_rule_id': 'rule_three',
                        'work_status': 'working',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 9,
        },
    ),
    # 28
    # query text tests
    (
        {'query': {'park': {'id': '1488'}, 'text': 'ал +7 брандашмыг ив ни'}},
        {
            'driver_profiles': [],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 0,
        },
    ),
    # 29
    (
        {'query': {'park': {'id': '1488'}, 'text': '3936525'}},
        {
            'driver_profiles': [{'driver_profile': {'id': 'Low'}}],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 1,
        },
    ),
    # 30
    (
        {
            'query': {
                'park': {'id': '1488'},
                'text': 'Мироненко Андрей Иванович 89031234568 foo 289',
            },
        },
        {
            'driver_profiles': [],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 0,
        },
    ),
    # 31
    (
        {
            'query': {
                'park': {'id': '1488'},
                'text': 'Мироненко Андрей Иванович 89031234568 м82о9289 foo',
            },
        },
        {
            'driver_profiles': [{'driver_profile': {'id': 'driverSS9'}}],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 1,
        },
    ),
    # 32
    (
        {'query': {'park': {'id': '1488'}, 'text': 'AA285554433'}},
        {
            'driver_profiles': [{'driver_profile': {'id': 'driver'}}],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 1,
        },
    ),
    # 33
    (
        {'query': {'park': {'id': '1488'}, 'text': 'андрЕй'}},
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driverSS9'}},
                {'driver_profile': {'id': 'driverSS6'}},
                {'driver_profile': {'id': 'driverSS3'}},
                {'driver_profile': {'id': 'driverSS2'}},
                {'driver_profile': {'id': 'driverSS'}},
            ],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 5,
        },
    ),
    # 34
    (
        {'query': {'park': {'id': '1488'}, 'text': 'андрЕй аЛЕкС'}},
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driverSS6'}},
                {'driver_profile': {'id': 'driverSS2'}},
                {'driver_profile': {'id': 'driverSS'}},
            ],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 3,
        },
    ),
    # 35
    (
        {'query': {'park': {'id': '1488'}, 'text': 'low +79163936525'}},
        {
            'driver_profiles': [{'driver_profile': {'id': 'Low'}}],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 1,
        },
    ),
    # 36
    (
        {'query': {'park': {'id': '1488'}, 'text': 'Николай Алекса'}},
        {
            'driver_profiles': [{'driver_profile': {'id': 'driverSS5'}}],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 1,
        },
    ),
    # 37
    (
        {'query': {'park': {'id': '222333'}, 'text': 'романОВИЧ'}},
        {
            'driver_profiles': [{'driver_profile': {'id': 'superDriver'}}],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 38
    (
        {'query': {'park': {'id': '222333'}, 'text': '77'}},
        {
            'driver_profiles': [{'driver_profile': {'id': 'superDriver'}}],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 39
    (
        {
            'query': {'park': {'id': '222333'}, 'text': 'гелик'},
            'fields': {'car': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'superDriver'},
                    'car': {'id': 'Gelendewagen'},
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 40
    (
        {
            'query': {'park': {'id': '222333'}, 'text': 'в777ор77'},
            'fields': {'car': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'superDriver'},
                    'car': {'id': 'Gelendewagen'},
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # random tests
    # 41
    (
        {
            'query': {'park': {'id': '1488'}},
            'fields': {
                'driver_profile': ['created_date'],
                'account': ['balance'],
            },
            'sort_order': [
                {'direction': 'desc', 'field': 'account.current.balance'},
                {'direction': 'asc', 'field': 'driver_profile.first_name'},
            ],
            'limit': 5,
            'offset': 3,
        },
        {
            'driver_profiles': [
                {
                    'accounts': [{'balance': '1000.0000', 'id': 'driverSS7'}],
                    'driver_profile': {
                        'created_date': '2018-11-20T05:04:14.517+0000',
                        'id': 'driverSS7',
                    },
                },
                {
                    'accounts': [{'balance': '987.0000', 'id': 'driverSS'}],
                    'driver_profile': {
                        'created_date': '2018-11-20T13:04:14.517+0000',
                        'id': 'driverSS',
                    },
                },
                {
                    'accounts': [{'balance': '888.0000', 'id': 'driverSS1'}],
                    'driver_profile': {
                        'created_date': '2018-11-20T11:04:14.517+0000',
                        'id': 'driverSS1',
                    },
                },
                {
                    'accounts': [{'balance': '807.0000', 'id': 'driverSS4'}],
                    'driver_profile': {
                        'created_date': '2018-11-20T08:04:14.517+0000',
                        'id': 'driverSS4',
                    },
                },
                {
                    'accounts': [{'balance': '708.0000', 'id': 'driverSS5'}],
                    'driver_profile': {
                        'created_date': '2018-11-20T07:04:14.517+0000',
                        'id': 'driverSS5',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'limit': 5,
            'offset': 3,
            'total': 18,
        },
    ),
    # 42
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'work_rule_id': ['rulez'],
                        'work_status': ['working'],
                    },
                },
            },
            'fields': {
                'driver_profile': ['created_date'],
                'account': ['balance'],
            },
            'sort_order': [
                {'direction': 'desc', 'field': 'account.current.balance'},
                {'direction': 'asc', 'field': 'driver_profile.first_name'},
            ],
        },
        {
            'driver_profiles': [
                {
                    'accounts': [{'id': 'driverSS4', 'balance': '807.0000'}],
                    'driver_profile': {
                        'created_date': '2018-11-20T08:04:14.517+0000',
                        'id': 'driverSS4',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 43
    (
        {'query': {'park': {'id': '666'}}, 'fields': {'park': ['id', 'name']}},
        {
            'driver_profiles': [],
            'parks': [{'id': '666', 'name': 'Taxi666'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # no car test
    # 44
    (
        {
            'query': {
                'park': {'id': '777', 'driver_profile': {'id': ['Vasya']}},
            },
            'fields': {'car': ['brand'], 'driver_profile': ['car_id']},
        },
        {
            'driver_profiles': [{'driver_profile': {'id': 'Vasya'}}],
            'parks': [{'id': '777'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 45
    # car required test
    (
        {
            'query': {'park': {'id': '222333'}},
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
            'required': ['car'],
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'superDriver'},
                    'car': {
                        'id': 'Gelendewagen',
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # query park car amenities test
    # 46
    (
        {
            'query': {
                'park': {'id': '222333', 'car': {'amenities': ['wifi']}},
            },
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'superDriver'},
                    'car': {
                        'id': 'Gelendewagen',
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 47
    (
        {
            'query': {'park': {'id': '1488', 'car': {'amenities': ['wifi']}}},
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driverSS5'},
                    'car': {
                        'id': '11133693fa67429588f09de95f4aaa9c',
                        'normalized_number': 'HB9999',
                    },
                },
                {
                    'driver_profile': {'id': 'driverSS'},
                    'car': {
                        'id': 'Gelendewagen',
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # 48
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'car': {'amenities': ['wifi', 'smoking']},
                },
            },
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driverSS'},
                    'car': {
                        'id': 'Gelendewagen',
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 49
    # query park car categories test
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'car': {'categories': ['maybach', 'econom']},
                },
            },
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # 50
    (
        {
            'query': {
                'park': {'id': '222333', 'car': {'categories': ['business']}},
            },
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'superDriver'},
                    'car': {
                        'id': 'Gelendewagen',
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 51
    (
        {
            'query': {'park': {'id': '1488', 'car': {'categories': ['vip']}}},
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driverSS5'},
                    'car': {
                        'id': '11133693fa67429588f09de95f4aaa9c',
                        'normalized_number': 'HB9999',
                    },
                },
                {
                    'driver_profile': {'id': 'driverSS'},
                    'car': {
                        'id': 'Gelendewagen',
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # 52
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'car': {'categories': ['econom', 'vip']},
                },
            },
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driverSS5'},
                    'car': {
                        'id': '11133693fa67429588f09de95f4aaa9c',
                        'normalized_number': 'HB9999',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 53
    # query park car amenities + categories test
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'car': {'amenities': ['wifi'], 'categories': ['vip']},
                },
            },
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driverSS5'},
                    'car': {
                        'id': '11133693fa67429588f09de95f4aaa9c',
                        'normalized_number': 'HB9999',
                    },
                },
                {
                    'driver_profile': {'id': 'driverSS'},
                    'car': {
                        'id': 'Gelendewagen',
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # 54
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'car': {'amenities': ['smoking'], 'categories': ['vip']},
                },
            },
            'fields': {'car': ['normalized_number'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driverSS'},
                    'car': {
                        'id': 'Gelendewagen',
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # aggregate account test
    # 55
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'id': [
                            'driver',
                            'driverSS',
                            'NoLimit',
                            'NulLimit',
                            'Low',
                        ],
                    },
                },
            },
            'fields': {
                'aggregate': {
                    'account': [
                        'positive_balance_sum',
                        'negative_balance_sum',
                        'balance_limit_sum',
                    ],
                },
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'Low'}},
                {'driver_profile': {'id': 'NulLimit'}},
                {'driver_profile': {'id': 'NoLimit'}},
                {'driver_profile': {'id': 'driverSS'}},
                {'driver_profile': {'id': 'driver'}},
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 5,
            'aggregate': {
                'account': {
                    'positive_balance_sum': '1087.0000',
                    'negative_balance_sum': '-153.0000',
                    'balance_limit_sum': '80.0000',
                },
            },
        },
    ),
    # 56
    # categories_filter
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                },
            },
            'fields': {'car': ['category']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'superDriver'},
                    'car': {
                        'id': 'Gelendewagen',
                        'category': ['business', 'mkk'],
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 57
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                    'car': {'categories_filter': []},
                },
            },
            'fields': {'car': ['category']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'superDriver'},
                    'car': {
                        'id': 'Gelendewagen',
                        'category': ['business', 'mkk'],
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 58
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                    'car': {'categories_filter': ['business', 'maybach']},
                },
            },
            'fields': {'car': ['category']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'superDriver'},
                    'car': {'id': 'Gelendewagen', 'category': ['business']},
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # payment_service_id field
    # 59
    (
        {
            'query': {
                'park': {'id': '1488', 'driver_profile': {'id': ['driverSS']}},
            },
            'fields': {'driver_profile': ['payment_service_id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'driverSS',
                        'payment_service_id': '123456',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 60
    (
        {
            'query': {
                'park': {'id': '1488', 'driver_profile': {'id': ['driverSS']}},
            },
            'fields': {'driver_profile': ['password']},
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driverSS', 'password': '123456'}},
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 61
    (
        {
            'query': {
                'park': {'id': '1488', 'driver_profile': {'id': ['driverSS']}},
            },
            'fields': {'driver_profile': ['payment_service_id', 'password']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'driverSS',
                        'payment_service_id': '123456',
                        'password': '123456',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # current status test
    # ids is not provided
    # 62
    (
        {
            'query': {'park': {'id': 'status_park'}},
            'fields': {
                'park': ['id'],
                'driver_profile': [],
                'account': [],
                'current_status': ['status', 'status_updated_at'],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driver1'},
                    'current_status': {'status': 'offline'},
                },
                {
                    'driver_profile': {'id': 'driver2'},
                    'current_status': {'status': 'busy'},
                },
                {
                    'driver_profile': {'id': 'driver3'},
                    'current_status': {
                        'status': 'free',
                        'status_updated_at': '2018-12-17T00:00:02+0000',
                    },
                },
            ],
            'parks': [{'id': 'status_park'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 63
    (
        {
            'query': {
                'park': {
                    'id': 'status_park',
                    'current_status': {'status': ['free']},
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': [],
                'account': [],
                'current_status': ['status_updated_at'],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driver3'},
                    'current_status': {
                        'status_updated_at': '2018-12-17T00:00:02+0000',
                    },
                },
            ],
            'parks': [{'id': 'status_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 64
    (
        {
            'query': {
                'park': {
                    'id': 'status_park',
                    'current_status': {'status': ['free']},
                },
            },
            'fields': {'park': ['id'], 'driver_profile': [], 'account': []},
        },
        {
            'driver_profiles': [{'driver_profile': {'id': 'driver3'}}],
            'parks': [{'id': 'status_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 65
    (
        {
            'query': {
                'park': {
                    'id': 'status_park',
                    'current_status': {'status': ['busy']},
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': [],
                'account': [],
                'current_status': ['status_updated_at'],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver2'}, 'current_status': {}},
            ],
            'parks': [{'id': 'status_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # current status test
    # ids provided
    # 66
    (
        {
            'query': {
                'park': {
                    'id': 'status_park',
                    'driver_profile': {'id': ['driver1']},
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': [],
                'account': [],
                'current_status': ['status', 'status_updated_at'],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driver1'},
                    'current_status': {'status': 'offline'},
                },
            ],
            'parks': [{'id': 'status_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 67
    (
        {
            'query': {
                'park': {
                    'id': 'status_park',
                    'driver_profile': {'id': ['driver1']},
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': [],
                'account': [],
                'current_status': ['status_updated_at'],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver1'}, 'current_status': {}},
            ],
            'parks': [{'id': 'status_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 68
    (
        {
            'query': {
                'park': {
                    'id': 'status_park',
                    'driver_profile': {'id': ['driver2']},
                    'current_status': {'status': ['busy']},
                },
            },
            'fields': {'park': ['id'], 'driver_profile': [], 'account': []},
        },
        {
            'driver_profiles': [{'driver_profile': {'id': 'driver2'}}],
            'parks': [{'id': 'status_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 69
    (
        {
            'query': {
                'park': {
                    'id': 'status_park',
                    'driver_profile': {'id': ['driver3']},
                    'current_status': {'status': ['busy']},
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['affiliation'],
                'account': [],
            },
        },
        {
            'driver_profiles': [],
            'parks': [{'id': 'status_park'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # get park country_id
    # 70
    (
        {
            'query': {'park': {'id': '666'}},
            'fields': {'park': ['id', 'country_id']},
        },
        {
            'driver_profiles': [],
            'parks': [{'id': '666', 'country_id': 'rus'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # city without country_id
    # 71
    (
        {
            'query': {'park': {'id': 'park_with_city_without_country_id'}},
            'fields': {'park': ['id', 'country_id']},
        },
        {
            'driver_profiles': [],
            'parks': [{'id': 'park_with_city_without_country_id'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # park without city
    # 72
    (
        {
            'query': {'park': {'id': 'park_without_city'}},
            'fields': {'park': ['id', 'country_id']},
        },
        {
            'driver_profiles': [],
            'parks': [{'id': 'park_without_city'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # get drivers by car_id
    # 73
    (
        {
            'query': {
                'park': {
                    'id': '2_car_park',
                    'driver_profile': {'work_status': ['working']},
                    'car': {'id': ['Car01', 'Car02']},
                },
            },
            'fields': {'driver_profile': ['car_id']},
        },
        {
            'driver_profiles': [
                {'driver_profile': {'car_id': 'Car01', 'id': 'driver01'}},
                {'driver_profile': {'car_id': 'Car01', 'id': 'driver02'}},
                {'driver_profile': {'car_id': 'Car02', 'id': 'driver03'}},
            ],
            'offset': 0,
            'parks': [{'id': '2_car_park'}],
            'total': 3,
        },
    ),
    # 74
    (
        {
            'query': {
                'park': {'id': '222333', 'car': {'categories': ['business']}},
            },
            'fields': {
                'car': ['is_readonly', 'normalized_number'],
                'driver_profile': ['id', 'is_readonly', 'license_experience'],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'superDriver',
                        'license_experience': {'total_since': '2019-12-27'},
                        'is_readonly': True,
                    },
                    'car': {
                        'id': 'Gelendewagen',
                        'is_readonly': False,
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # Romania fields test
    # 75
    (
        {
            'query': {
                'park': {'id': '222333', 'car': {'categories': ['business']}},
            },
            'fields': {
                'car': ['is_readonly', 'normalized_number'],
                'driver_profile': [
                    'id',
                    'affiliation',
                    'is_readonly',
                    'professional_certificate_expiration_date',
                    'road_penalties_record_issue_date',
                    'background_criminal_record_issue_date',
                ],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'superDriver',
                        'professional_certificate_expiration_date': (
                            '2019-12-27T00:00:00+0000'
                        ),
                        'road_penalties_record_issue_date': (
                            '2019-12-27T00:00:00+0000'
                        ),
                        'background_criminal_record_issue_date': (
                            '2019-12-27T00:00:00+0000'
                        ),
                        'is_readonly': True,
                    },
                    'car': {
                        'id': 'Gelendewagen',
                        'is_readonly': False,
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # sex
    # 76
    (
        {
            'query': {
                'park': {'id': '222333', 'car': {'categories': ['business']}},
            },
            'fields': {
                'car': ['is_readonly', 'normalized_number'],
                'driver_profile': ['id', 'is_readonly', 'sex'],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'superDriver',
                        'sex': 'male',
                        'is_readonly': True,
                    },
                    'car': {
                        'id': 'Gelendewagen',
                        'is_readonly': False,
                        'normalized_number': 'B7770P77',
                    },
                },
            ],
            'parks': [{'id': '222333'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # courier
    # 77
    (
        {
            'query': {'park': {'id': 'couriers_park'}},
            'fields': {
                'car': ['id', 'is_readonly'],
                'driver_profile': ['id', 'courier_type', 'driver_license'],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'courier_xxx',
                        'courier_type': 'walking_courier',
                        'driver_license': {
                            'birth_date': '1994-01-01T07:15:13+0000',
                            'normalized_number': 'COURIER123',
                            'number': 'COURIER123',
                            'country': 'rus',
                        },
                    },
                    'car': {'id': 'fake_car', 'is_readonly': True},
                },
            ],
            'parks': [{'id': 'couriers_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # treat null value as absent field
    # 78
    (
        {
            'query': {
                'park': {
                    'id': 'park_with_nulls',
                    'driver_profile': {'id': ['driver_with_null_rule_id']},
                },
            },
            'fields': {'driver_profile': ['id', 'last_name', 'work_rule_id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'driver_with_null_rule_id',
                        'last_name': 'Нулевой',
                    },
                },
            ],
            'parks': [{'id': 'park_with_nulls'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # digital_lightbox
    # 79
    (
        {
            'query': {'park': {'id': 'digital_lightbox_park'}},
            'fields': {'car': ['amenities'], 'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driver1'},
                    'car': {'id': 'car1', 'amenities': ['digital_lightbox']},
                },
            ],
            'parks': [{'id': 'digital_lightbox_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 80
    (
        {
            'query': {'park': {'id': '1488'}, 'text': '3936525'},
            'fields': {'driver_profile': ['id', 'phones', 'created_date']},
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'created_date': '2018-11-19T21:04:14.517+0000',
                        'id': 'Low',
                        'phones': ['+79163936525'],
                    },
                },
            ],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 1,
        },
    ),
    # 81, text test with short text
    (
        {
            'query': {'park': {'id': '1488'}, 'text': 'a'},
            'fields': {'driver_profile': ['id']},
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver'}},
                {'driver_profile': {'id': 'driver_ie_1_affiliation'}},
                {'driver_profile': {'id': 'driver_ie_2_affiliation'}},
                {'driver_profile': {'id': 'driver_se_1_affiliation'}},
                {'driver_profile': {'id': 'driver_se_2_affiliation'}},
            ],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 5,
        },
    ),
    # 82, signalq driver
    (
        {
            'query': {
                'park': {'id': 'only_signalq_park1'},
                'text': 'SIGNALQ1',
            },
            'fields': {'driver_profile': ['id']},
        },
        {
            'driver_profiles': [{'driver_profile': {'id': 'signalq_0'}}],
            'offset': 0,
            'parks': [{'id': 'only_signalq_park1'}],
            'total': 1,
        },
    ),
    # 83, signalq driver with empty phone in response
    (
        {
            'query': {
                'park': {'id': 'only_signalq_park1'},
                'text': 'SIGNALQ1',
            },
            'fields': {'driver_profile': ['id', 'phones']},
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'signalq_0', 'phones': []}},
            ],
            'offset': 0,
            'parks': [{'id': 'only_signalq_park1'}],
            'total': 1,
        },
    ),
    # 84, is_rental = None
    (
        {
            'query': {'park': {'id': 'rental_cars_park'}},
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': [],
                'current_status': [],
                'car': ['rental'],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'rental_driver1'},
                    'car': {'id': 'rental_car1', 'rental': True},
                },
                {
                    'driver_profile': {'id': 'rental_driver2'},
                    'car': {'id': 'non_rental_car1', 'rental': False},
                },
            ],
            'parks': [{'id': 'rental_cars_park'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # 85, is_rental = True
    (
        {
            'query': {
                'park': {'id': 'rental_cars_park', 'car': {'is_rental': True}},
            },
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': [],
                'current_status': [],
                'car': ['rental'],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'rental_driver1'},
                    'car': {'id': 'rental_car1', 'rental': True},
                },
            ],
            'parks': [{'id': 'rental_cars_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 86, is_rental = False
    (
        {
            'query': {
                'park': {
                    'id': 'rental_cars_park',
                    'car': {'is_rental': False},
                },
            },
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': [],
                'current_status': [],
                'car': ['rental'],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'rental_driver2'},
                    'car': {'id': 'non_rental_car1', 'rental': False},
                },
            ],
            'parks': [{'id': 'rental_cars_park'}],
            'offset': 0,
            'total': 1,
        },
    ),
]


@pytest.mark.redis_store(
    ['hset', 'status_park:STATUS_DRIVERS', 'driver2', 1],
    ['hset', 'status_park:STATUS_DRIVERS', 'driver3', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:status_park',
        'driver3',
        '"2018-12-17T00:00:02.00000Z"',
    ],
)
@pytest.mark.parametrize('request_json,expected_response', OK_PARAMS)
@pytest.mark.parametrize('use_personal_caches', [True, False])
@pytest.mark.parametrize(
    'personal_caches_enable_settings',
    [
        'turned_off',
        'fully_turned_on',
        'fully_turned_on_with_check',
        'turned_on_for_check_equality',
    ],
)
def test_ok(
        taxi_parks,
        mockserver,
        redis_store,
        request_json,
        expected_response,
        use_personal_caches,
        personal_caches_enable_settings,
        config,
):
    config.set_values(dict(PARKS_USE_PERSONAL_CACHES=use_personal_caches))
    config.set_values(
        dict(
            PARKS_PERSONAL_CACHES_ENABLE_SETTINGS={
                'active_status': personal_caches_enable_settings,
            },
        ),
    )

    @mockserver.json_handler('/personal_caches/v1/parks/drivers-lookup')
    def mock_personal_caches(request):
        input_json = json.loads(request.get_data())
        park_id = input_json['park_id']
        text = input_json['text']
        return get_personal_caches_mock_response_for_test_ok(park_id, text)

    response = taxi_parks.post(
        '/driver-profiles/list', data=json.dumps(request_json),
    )

    assert response.status_code == 200
    assert response.json() == expected_response


LAST_TRANSACTION_TEST_PARAMS = [
    # filter out without last_transaction_date
    # 1
    (
        {
            'query': {
                'park': {
                    'id': 'last_transaction_park1',
                    'account': {
                        'last_transaction_date': {
                            'from': '2018-12-17T00:00:02.00000Z',
                        },
                    },
                },
            },
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [],
            'parks': [{'id': 'last_transaction_park1'}],
            'offset': 0,
            'total': 0,
        },
    ),
    # from filter
    (
        {
            'query': {
                'park': {
                    'id': 'last_transaction_park2',
                    'account': {
                        'last_transaction_date': {
                            'from': '2015-01-01T10:00:00.00000Z',
                        },
                    },
                },
            },
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver2'}},
                {'driver_profile': {'id': 'driver3'}},
            ],
            'parks': [{'id': 'last_transaction_park2'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # to filter
    (
        {
            'query': {
                'park': {
                    'id': 'last_transaction_park2',
                    'account': {
                        'last_transaction_date': {
                            'to': '2015-01-01T11:00:00.00000Z',
                        },
                    },
                },
            },
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver1'}},
                {'driver_profile': {'id': 'driver3'}},
            ],
            'parks': [{'id': 'last_transaction_park2'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # from and to filter
    (
        {
            'query': {
                'park': {
                    'id': 'last_transaction_park2',
                    'account': {
                        'last_transaction_date': {
                            'from': '2000-01-01T10:00:00.00000Z',
                            'to': '2015-01-01T11:00:00.00000Z',
                        },
                    },
                },
            },
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver1'}},
                {'driver_profile': {'id': 'driver3'}},
            ],
            'parks': [{'id': 'last_transaction_park2'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # work_status filter intersection
    (
        {
            'query': {
                'park': {
                    'id': 'last_transaction_park2',
                    'account': {
                        'last_transaction_date': {
                            'from': '2000-01-01T10:00:00.00000Z',
                        },
                    },
                    'driver_profile': {'work_status': ['working']},
                },
            },
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver2'}},
                {'driver_profile': {'id': 'driver3'}},
            ],
            'parks': [{'id': 'last_transaction_park2'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # sorted in balance order
    (
        {
            'query': {
                'park': {
                    'id': 'last_transaction_park2',
                    'account': {
                        'last_transaction_date': {
                            'from': '2015-01-01T10:00:00.00000Z',
                        },
                    },
                },
            },
            'sort_order': [
                {'direction': 'desc', 'field': 'account.current.balance'},
            ],
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver3'}},
                {'driver_profile': {'id': 'driver2'}},
            ],
            'parks': [{'id': 'last_transaction_park2'}],
            'offset': 0,
            'total': 2,
        },
    ),
    # last_transaction_date in returned fields
    (
        {
            'query': {
                'park': {
                    'id': 'last_transaction_park2',
                    'account': {
                        'last_transaction_date': {
                            'from': '2015-01-01T10:00:00.00000Z',
                            'to': '2015-01-01T11:00:00.00000Z',
                        },
                    },
                },
            },
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': ['last_transaction_date'],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driver3'},
                    'accounts': [
                        {
                            'id': 'driver3',
                            'last_transaction_date': (
                                '2015-01-01T10:00:00+0000'
                            ),
                        },
                    ],
                },
            ],
            'parks': [{'id': 'last_transaction_park2'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # last_transaction_date is required but it is not in the document
    (
        {
            'query': {
                'park': {
                    'id': 'last_transaction_park2',
                    'driver_profile': {'id': ['driver4']},
                },
            },
            'fields': {
                'park': [],
                'driver_profile': [],
                'account': ['last_transaction_date'],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {'id': 'driver4'},
                    'accounts': [{'id': 'driver4'}],
                },
            ],
            'parks': [{'id': 'last_transaction_park2'}],
            'offset': 0,
            'total': 1,
        },
    ),
]


@pytest.mark.parametrize(
    'request_json,expected_response', LAST_TRANSACTION_TEST_PARAMS,
)
@pytest.mark.parametrize('use_personal_caches', [True, False])
def test_last_transaction_date(
        taxi_parks,
        request_json,
        expected_response,
        use_personal_caches,
        config,
):
    config.set_values(dict(PARKS_USE_PERSONAL_CACHES=use_personal_caches))

    response = taxi_parks.post(
        '/driver-profiles/list', data=json.dumps(request_json),
    )

    assert response.status_code == 200
    assert response.json() == expected_response


DRIVER_AFFILIATION_PARAMS = [
    # 1
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'work_rule_id': ['rule_one'],
                        'affiliation_partner_sources': [
                            'individual_entrepreneur',
                        ],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['affiliation'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'affiliation': {
                            'id': 'f0201c13b0274180900025559b3d2cf8',
                            'original_driver_id': 'driver_ie_1_original',
                            'original_park_id': 'park_ie_1',
                            'partner_source': 'individual_entrepreneur',
                            'state': 'active',
                        },
                        'id': 'driver_ie_1_affiliation',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 2
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'work_status': ['fired'],
                        'affiliation_partner_sources': [
                            'individual_entrepreneur',
                        ],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver_ie_2_affiliation'}},
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 3
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'work_status': ['working'],
                        'affiliation_partner_sources': ['self_employed'],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id', 'affiliation'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'affiliation': {
                            'id': '22d4b27fb0fa4fdeb1f676a63343754e',
                            'original_driver_id': 'driver_se_1_original',
                            'original_park_id': 'park_se_1',
                            'partner_source': 'self_employed',
                            'state': 'accepted',
                        },
                        'id': 'driver_se_1_affiliation',
                    },
                },
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 4
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'work_status': ['working', 'fired'],
                        'affiliation_partner_sources': [
                            'self_employed',
                            'individual_entrepreneur',
                        ],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver_ie_1_affiliation'}},
                {'driver_profile': {'id': 'driver_ie_2_affiliation'}},
                {'driver_profile': {'id': 'driver_se_1_affiliation'}},
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 5
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'affiliation_partner_sources': [
                            'self_employed',
                            'individual_entrepreneur',
                        ],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'driver_ie_1_affiliation'}},
                {'driver_profile': {'id': 'driver_ie_2_affiliation'}},
                {'driver_profile': {'id': 'driver_se_1_affiliation'}},
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 3,
        },
    ),
    # 6
    (
        {
            'query': {
                'park': {
                    'id': '1489',
                    'driver_profile': {
                        'affiliation_partner_sources': ['self_employed'],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id', 'is_selfemployed'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'driver_selfemployed_fns',
                        'is_selfemployed': True,
                    },
                },
            ],
            'parks': [{'id': '1489'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 7
    (
        {
            'query': {
                'park': {
                    'id': '1489',
                    'driver_profile': {
                        'affiliation_partner_sources': ['none'],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id', 'is_selfemployed'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': 'driverSSS',
                        'is_selfemployed': False,
                    },
                },
            ],
            'parks': [{'id': '1489'}],
            'offset': 0,
            'total': 1,
        },
    ),
    # 8
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'affiliation_partner_sources': ['none'],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'Low'}},
                {'driver_profile': {'id': 'NulLimit'}},
                {'driver_profile': {'id': 'NoLimit'}},
                {'driver_profile': {'id': 'driverSS9'}},
                {'driver_profile': {'id': 'driverSS8'}},
                {'driver_profile': {'id': 'driverSS7'}},
                {'driver_profile': {'id': 'driverSS6'}},
                {'driver_profile': {'id': 'driverSS5'}},
                {'driver_profile': {'id': 'driverSS4'}},
                {'driver_profile': {'id': 'driverSS3'}},
                {'driver_profile': {'id': 'driverSS2'}},
                {'driver_profile': {'id': 'driverSS1'}},
                {'driver_profile': {'id': 'driverSS'}},
                {'driver_profile': {'id': 'driver'}},
                {'driver_profile': {'id': 'driver_se_2_affiliation'}},
            ],
            'parks': [{'id': '1488'}],
            'offset': 0,
            'total': 15,
        },
    ),
    # 9
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'affiliation_partner_sources': [
                            'none',
                            'self_employed',
                        ],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'Low'}},
                {'driver_profile': {'id': 'NulLimit'}},
                {'driver_profile': {'id': 'NoLimit'}},
                {'driver_profile': {'id': 'driverSS9'}},
                {'driver_profile': {'id': 'driverSS8'}},
                {'driver_profile': {'id': 'driverSS7'}},
                {'driver_profile': {'id': 'driverSS6'}},
                {'driver_profile': {'id': 'driverSS5'}},
                {'driver_profile': {'id': 'driverSS4'}},
                {'driver_profile': {'id': 'driverSS3'}},
                {'driver_profile': {'id': 'driverSS2'}},
                {'driver_profile': {'id': 'driverSS1'}},
                {'driver_profile': {'id': 'driverSS'}},
                {'driver_profile': {'id': 'driver'}},
                {'driver_profile': {'id': 'driver_se_1_affiliation'}},
                {'driver_profile': {'id': 'driver_se_2_affiliation'}},
            ],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 16,
        },
    ),
    # 10
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'affiliation_partner_sources': [
                            'none',
                            'self_employed',
                            'individual_entrepreneur',
                        ],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'Low'}},
                {'driver_profile': {'id': 'NulLimit'}},
                {'driver_profile': {'id': 'NoLimit'}},
                {'driver_profile': {'id': 'driverSS9'}},
                {'driver_profile': {'id': 'driverSS8'}},
                {'driver_profile': {'id': 'driverSS7'}},
                {'driver_profile': {'id': 'driverSS6'}},
                {'driver_profile': {'id': 'driverSS5'}},
                {'driver_profile': {'id': 'driverSS4'}},
                {'driver_profile': {'id': 'driverSS3'}},
                {'driver_profile': {'id': 'driverSS2'}},
                {'driver_profile': {'id': 'driverSS1'}},
                {'driver_profile': {'id': 'driverSS'}},
                {'driver_profile': {'id': 'driver'}},
                {'driver_profile': {'id': 'driver_ie_1_affiliation'}},
                {'driver_profile': {'id': 'driver_ie_2_affiliation'}},
                {'driver_profile': {'id': 'driver_se_1_affiliation'}},
                {'driver_profile': {'id': 'driver_se_2_affiliation'}},
            ],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 18,
        },
    ),
    # 11
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'affiliation_partner_sources': [
                            'none',
                            'individual_entrepreneur',
                        ],
                    },
                },
            },
            'fields': {
                'park': ['id'],
                'driver_profile': ['id', 'affiliation'],
                'account': [],
                'current_status': [],
            },
        },
        {
            'driver_profiles': [
                {'driver_profile': {'id': 'Low'}},
                {'driver_profile': {'id': 'NulLimit'}},
                {'driver_profile': {'id': 'NoLimit'}},
                {'driver_profile': {'id': 'driverSS9'}},
                {'driver_profile': {'id': 'driverSS8'}},
                {'driver_profile': {'id': 'driverSS7'}},
                {'driver_profile': {'id': 'driverSS6'}},
                {'driver_profile': {'id': 'driverSS5'}},
                {'driver_profile': {'id': 'driverSS4'}},
                {'driver_profile': {'id': 'driverSS3'}},
                {'driver_profile': {'id': 'driverSS2'}},
                {'driver_profile': {'id': 'driverSS1'}},
                {'driver_profile': {'id': 'driverSS'}},
                {'driver_profile': {'id': 'driver'}},
                {
                    'driver_profile': {
                        'affiliation': {
                            'id': 'f0201c13b0274180900025559b3d2cf8',
                            'original_driver_id': 'driver_ie_1_original',
                            'original_park_id': 'park_ie_1',
                            'partner_source': 'individual_entrepreneur',
                            'state': 'active',
                        },
                        'id': 'driver_ie_1_affiliation',
                    },
                },
                {
                    'driver_profile': {
                        'affiliation': {
                            'id': '22d4b27fb0fa4fdeb1f676a63343754b',
                            'original_driver_id': 'driver_ie_2_original',
                            'original_park_id': 'park_ie_2',
                            'partner_source': 'individual_entrepreneur',
                            'state': 'active',
                        },
                        'id': 'driver_ie_2_affiliation',
                    },
                },
                {
                    'driver_profile': {
                        'affiliation': {
                            'id': '22d4b27fb0fa4fdeb1f676a64343754e',
                            'original_driver_id': 'driver_se_2_original',
                            'original_park_id': 'park_se_1',
                            'partner_source': 'self_employed',
                            'state': 'new',
                        },
                        'id': 'driver_se_2_affiliation',
                    },
                },
            ],
            'offset': 0,
            'parks': [{'id': '1488'}],
            'total': 17,
        },
    ),
]


@pytest.mark.parametrize(
    'request_json,expected_response', DRIVER_AFFILIATION_PARAMS,
)
@pytest.mark.parametrize('use_personal_caches', [True, False])
def test_driver_affiliation(
        taxi_parks,
        request_json,
        expected_response,
        use_personal_caches,
        config,
):
    config.set_values(dict(PARKS_USE_PERSONAL_CACHES=use_personal_caches))

    response = taxi_parks.post(
        '/driver-profiles/list', data=json.dumps(request_json),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


DEPTRANS_PARAMS = [
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                },
            },
            'fields': {
                'park': ['id', 'name'],
                'driver_profile': [],
                'account': [],
                'deptrans': ['status'],
            },
        },
        {
            'driver_profiles': [
                {
                    'deptrans': {'status': 'approved'},
                    'driver_profile': {'id': 'superDriver'},
                },
            ],
            'parks': [{'id': '222333', 'name': 'Taxi71'}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                },
            },
            'fields': {
                'park': ['id', 'name'],
                'driver_profile': [],
                'account': [],
                'deptrans': ['status', 'updated_at'],
            },
        },
        {
            'driver_profiles': [
                {
                    'deptrans': {
                        'status': 'approved',
                        'updated_at': '2020-12-30T11:00:00+0000',
                    },
                    'driver_profile': {'id': 'superDriver'},
                },
            ],
            'parks': [{'id': '222333', 'name': 'Taxi71'}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                },
            },
            'fields': {
                'park': ['id', 'name'],
                'driver_profile': [],
                'account': [],
                'deptrans': ['id', 'status', 'updated_at'],
            },
        },
        {
            'driver_profiles': [
                {
                    'deptrans': {
                        'id': 'valid_deptrans_id',
                        'status': 'approved',
                        'updated_at': '2020-12-30T11:00:00+0000',
                    },
                    'driver_profile': {'id': 'superDriver'},
                },
            ],
            'parks': [{'id': '222333', 'name': 'Taxi71'}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                    'deptrans': {'statuses': ['approved']},
                },
            },
            'fields': {
                'park': ['id', 'name'],
                'driver_profile': [],
                'account': [],
                'deptrans': ['id', 'status', 'updated_at'],
            },
        },
        {
            'driver_profiles': [
                {
                    'deptrans': {
                        'id': 'valid_deptrans_id',
                        'status': 'approved',
                        'updated_at': '2020-12-30T11:00:00+0000',
                    },
                    'driver_profile': {'id': 'superDriver'},
                },
            ],
            'parks': [{'id': '222333', 'name': 'Taxi71'}],
            'offset': 0,
            'total': 1,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': ['superDriver']},
                    'deptrans': {'statuses': ['not_needed']},
                },
            },
            'fields': {
                'park': ['id', 'name'],
                'driver_profile': [],
                'account': [],
                'deptrans': ['id', 'status', 'updated_at'],
            },
        },
        {
            'driver_profiles': [],
            'parks': [{'id': '222333', 'name': 'Taxi71'}],
            'offset': 0,
            'total': 0,
        },
    ),
]


@pytest.mark.parametrize('request_json,expected_response', DEPTRANS_PARAMS)
@pytest.mark.parametrize('use_personal_caches', [True, False])
def test_deptrans(
        taxi_parks,
        mockserver,
        request_json,
        expected_response,
        use_personal_caches,
        config,
):
    config.set_values(dict(PARKS_USE_PERSONAL_CACHES=use_personal_caches))

    response = taxi_parks.post(
        '/driver-profiles/list', data=json.dumps(request_json),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


BAD_PARAMS = [
    ({}, 'query must be present'),
    ({'query': {}}, 'query.park must be present'),
    ({'query': []}, 'query must be an object'),
    ({'query': {'park': []}}, 'query.park must be an object'),
    (
        {'query': {'park': {'some_field': 'some_value'}}},
        'query.park.id must be present',
    ),
    (
        {'query': {'park': {'id': 7}}},
        'query.park.id must be a non-empty utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': ''}}},
        'query.park.id must be a non-empty utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': 'xxx'}, 'text': 13.72}},
        'query.text must be an utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': 'xxx', 'driver_profile': {'id': 'yyy'}}}},
        'query.park.driver_profile.id must be an array',
    ),
    (
        {
            'query': {
                'park': {'id': 'xxx', 'driver_profile': {'id': ['yyy', 13]}},
            },
        },
        'query.park.driver_profile.id[1] '
        'must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'driver_profile': {'id': ['yyy', 'zzz', 'yyy']},
                },
            },
        },
        'query.park.driver_profile.id must contain unique strings'
        ' (error at `yyy`)',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'driver_profile': {'work_rule_id': 'yyy'},
                },
            },
        },
        'query.park.driver_profile.work_rule_id must be an array',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'driver_profile': {'work_rule_id': ['yyy', 'zzz', '']},
                },
            },
        },
        'query.park.driver_profile.work_rule_id[2] must be'
        ' a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'driver_profile': {'work_rule_id': ['yyy', 'zzz', 'yyy']},
                },
            },
        },
        'query.park.driver_profile.work_rule_id must contain unique strings'
        ' (error at `yyy`)',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'driver_profile': {'work_status': 'yyy'},
                },
            },
        },
        'query.park.driver_profile.work_status must be an array',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'driver_profile': {'work_status': [True]},
                },
            },
        },
        'query.park.driver_profile.work_status[0] must be'
        ' a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'driver_profile': {
                        'work_status': ['yyy', 'zzz', 'yy', 'aa', 'zzz'],
                    },
                },
            },
        },
        'query.park.driver_profile.work_status must contain unique strings'
        ' (error at `zzz`)',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'limit': 'abc'},
        'limit must be a non-negative integer',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'limit': -1},
        'limit must be a non-negative integer',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'limit': 0},
        'limit must be greater than or equal to 1',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'offset': -1},
        'offset must be a non-negative integer',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'offset': 'abc'},
        'offset must be a non-negative integer',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'sort_order': {}},
        'sort_order must be an array',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'sort_order': ['abc']},
        'sort_order[0] must be an object',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'sort_order': [{}]},
        'sort_order[0].field must be present',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [{'direction': 'asc'}],
        },
        'sort_order[0].field must be present',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [{'direction': 'asc', 'field': ['xxx']}],
        },
        'sort_order[0].field must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [{'direction': 'asc', 'field': ''}],
        },
        'sort_order[0].field must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [
                {'direction': 'asc', 'field': 'account.current.balance'},
                {'direction': 'desc', 'field': 'driver_profile.created_date'},
                {'direction': 'asc', 'field': 'driver_profile.first_name'},
                {'direction': 'desc', 'field': 'driver_profile.last_name'},
                {'direction': 'asc', 'field': 'driver_profile.middle_name'},
                {'direction': 'asc', 'field': 'driver_profile.some'},
            ],
        },
        'sort_order[5].field must be one of: `account.current.balance`, '
        '`car.call_sign`, `driver_profile.created_date`, '
        '`driver_profile.modified_date`, `driver_profile.hire_date`, '
        '`driver_profile.last_name`, `driver_profile.first_name`, '
        '`driver_profile.middle_name`',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [
                {'direction': 'asc', 'field': 'driver_profile.first_name'},
                {'direction': 'asc', 'field': 'driver_profile.first_name'},
            ],
        },
        'sort_order[1] must not contain a field'
        ' that has been previously selected',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [
                {'direction': 'asc', 'field': 'account.current.balance'},
                {'direction': 'desc', 'field': 'driver_profile.created_date'},
                {'direction': 'asc', 'field': 'driver_profile.first_name'},
                {'direction': 'asc', 'field': 'driver_profile.created_date'},
            ],
        },
        'sort_order[3] must not contain a field'
        ' that has been previously selected',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [{'field': 'car.call_sign'}],
        },
        'sort_order[0].direction must be present',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [{'field': 'car.call_sign', 'direction': 17.14}],
        },
        'sort_order[0].direction must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [{'field': 'car.call_sign', 'direction': ''}],
        },
        'sort_order[0].direction must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'sort_order': [{'field': 'car.call_sign', 'direction': 'what'}],
        },
        'sort_order[0].direction must be one of: `asc`, `desc`',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'fields': {'park': {}}},
        'fields.park must be an array',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'fields': {'park': [True]}},
        'fields.park[0] must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'fields': {'park': ['abc', 'xyz', 'abc']},
        },
        'fields.park must contain unique strings (error at `abc`)',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'fields': {'driver_profile': {}},
        },
        'fields.driver_profile must be an array',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'fields': {'driver_profile': [True]},
        },
        'fields.driver_profile[0] '
        'must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'fields': {'driver_profile': ['abc', 'xyz', 'abc']},
        },
        'fields.driver_profile must contain unique strings (error at `abc`)',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'fields': {'account': {}}},
        'fields.account must be an array',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'fields': {'account': [True]}},
        'fields.account[0] must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'fields': {'account': ['abc', 'xyz', 'abc']},
        },
        'fields.account must contain unique strings (error at `abc`)',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'fields': {'car': {}}},
        'fields.car must be an array',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'fields': {'car': [True]}},
        'fields.car[0] must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'fields': {'car': ['123', '345', '567', '345']},
        },
        'fields.car must contain unique strings (error at `345`)',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'fields': {'car': {}}},
        'fields.car must be an array',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'fields': {'car': [True]}},
        'fields.car[0] must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {'park': {'id': 'qwerty'}},
            'fields': {'car': ['123', '345', '567', '345']},
        },
        'fields.car must contain unique strings (error at `345`)',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'required': 'car'},
        'required must be an array',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'required': ['car', '']},
        'required[1] must be a non-empty utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'required': ['var', 'var']},
        'required must contain unique strings (error at `var`)',
    ),
    (
        {'query': {'park': {'id': 'qwerty'}}, 'required': ['var']},
        'required must not contain any string, except `car`',
    ),
    (
        {'query': {'park': {'id': 'xxx', 'car': {'amenities': 'yyy'}}}},
        'query.park.car.amenities must be an array',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'car': {'amenities': ['wifi', 'ski', '']},
                },
            },
        },
        'query.park.car.amenities[2] '
        'must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'car': {'amenities': ['wifi', 'ski', 'wifi']},
                },
            },
        },
        'query.park.car.amenities must contain unique values',
    ),
    (
        {'query': {'park': {'id': 'xxx', 'car': {'amenities': ['abra']}}}},
        'query.park.car.amenities[0] must be one of: `animals`, `bicycle`,'
        ' `conditioner`, `delivery`, `extra_seats`, `pos`, `print_bill`,'
        ' `ski`, `smoking`, `vip_event`, `wifi`, `wagon`, `woman_driver`,'
        ' `yandex_money`, `booster`, `child_seat`, `charge`, `franchise`,'
        ' `lightbox`, `digital_lightbox`, `rug`, `sticker`, `cargo_clean`,'
        ' `cargo_packing`, `rigging_equipment`',
    ),
    (
        {
            'query': {
                'park': {'id': 'xxx', 'car': {'categories_filter': ['abra']}},
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
    (
        {'query': {'park': {'id': 'xxx', 'car': {'categories': 'yyy'}}}},
        'query.park.car.categories must be an array',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'car': {'categories': ['vip', 'econom', '']},
                },
            },
        },
        'query.park.car.categories[2] '
        'must be a non-empty utf-8 string without BOM',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'car': {'categories': ['vip', 'econom', 'vip']},
                },
            },
        },
        'query.park.car.categories must contain unique values',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'car': {
                        'categories_filter': ['maybach', 'ultimate'],
                        'categories': ['vip'],
                    },
                },
            },
        },
        'query.park.car.categories each element must be one of: `maybach`, '
        '`ultimate`',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'account': {'last_transaction_date': {}},
                },
            },
        },
        'query.park.account.last_transaction_date :'
        ' either `from` or `to` must be specified',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'account': {'last_transaction_date': ''},
                },
            },
        },
        'query.park.account.last_transaction_date ' 'must be an object',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'account': {
                        'last_transaction_date': {
                            'from': '2016-01-01T10:00:00.00000Z',
                            'to': '2015-01-01T10:00:00.00000Z',
                        },
                    },
                },
            },
        },
        'query.park.account.last_transaction_date :'
        ' `from` must be earlier than `to`',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'xxx',
                    'account': {
                        'last_transaction_date': {
                            'from': '2015-01-01T10:00:00.00000Z',
                            'to': '2015-01-01T10:00:00.00000Z',
                        },
                    },
                },
            },
        },
        'query.park.account.last_transaction_date :'
        ' `from` must be earlier than `to`',
    ),
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {
                        'affiliation_partner_sources': [
                            'self_employed',
                            'self_employed',
                            'individual_entrepreneur',
                        ],
                    },
                },
            },
        },
        'query.park.driver_profile.affiliation_partner_sources'
        ' must contain unique values',
    ),
]


@pytest.mark.parametrize('request_json,error_text', BAD_PARAMS)
@pytest.mark.parametrize('use_personal_caches', [True, False])
def test_bad_request(
        taxi_parks, request_json, error_text, use_personal_caches, config,
):
    config.set_values(dict(PARKS_USE_PERSONAL_CACHES=use_personal_caches))

    response = taxi_parks.post(
        '/driver-profiles/list', data=json.dumps(request_json),
    )

    assert response.status_code == 400
    assert response.json() == {'error': {'text': error_text}}


@pytest.mark.parametrize('use_personal_caches', [True, False])
def test_not_found(taxi_parks, use_personal_caches, config):
    config.set_values(dict(PARKS_USE_PERSONAL_CACHES=use_personal_caches))
    response = taxi_parks.post(
        '/driver-profiles/list',
        data=json.dumps({'query': {'park': {'id': 'qwerty'}}}),
    )

    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'park with id `qwerty` not found'},
    }
