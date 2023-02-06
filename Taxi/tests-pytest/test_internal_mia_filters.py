# coding: utf-8
from __future__ import unicode_literals

import datetime

import pytest

from taxi.internal.mia import filters
from taxi.internal.mia import utils
from taxi.util import dates


def _datetime_ts(*args, **kwargs):
    return dates.timestamp_us(datetime.datetime(*args, **kwargs))


@pytest.mark.parametrize('filter_name,operator,regex_or_exact,input_row,'
                         'raised_exc,expected_result', [
    (
        'driver_name', 'falls_inside', 'test', None,
        filters.IncompatibleOperatorError, None,
    ),
    (
        'driver_name',
        'eq',
        'Test Name',
        {
            'candidates': [
                {'name': 'Test Name'}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        True,
    ),
    (
        'driver_name',
        'eq',
        'Test Name',
        {
            'candidates': [
                {'name': 'Test Name Not Exact'}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        False,
    ),
    (
        'driver_name', 'regex', 'f8(', None,
        filters.InvalidReferenceValueError, None,
    ),
    (
        'driver_name',
        'regex',
        'Test.*Name',
        {
            'candidates': [
                {'name': 'Test Name'}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        True,
    ),
    (
        'driver_name',
        'regex',
        'Test.*Name',
        {
            'candidates': [
                {'name': 'Test NotExact Name'}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        True,
    ),
    (
        'driver_name',
        'regex',
        'Test.*Name',
        {
            'candidates': [
                {'name': 'Test Another'}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        False,
    ),
    (
        'source_address', 'eq', 'Тестовый адрес',
        {'request_source': {
            'fullname': 'Тестовый адрес'.encode('utf-8')
        }},
        None, True,
    ),
    (
        'any_destination_address', 'eq', 'Тестовый адрес',
        {
            'request_destinations': [
                {'fullname': 'Тестовый адрес'.encode('utf-8')},
                {'fullname': 'Неподходящая конечная точка'.encode('utf-8')},
            ]
        },
        None,
        True,
    ),
    (
        'any_destination_address', 'regex', 'Тестовый адрес',
        {
            'request_destinations': [
                {'fullname': 'Тестовый адрес'.encode('utf-8')},
                {'fullname': 'Неподходящая конечная точка'.encode('utf-8')},
            ]
        },
        None,
        True,
    ),
    (
        'final_destination_address', 'regex', 'Тестовый адрес',
        {
            'request_destinations': [
                {'fullname': 'Неподходящая конечная точка'.encode('utf-8')},
                {'fullname': 'Тестовый адрес'.encode('utf-8')},
            ]
        },
        None,
        True,
    ),
    (
        'final_destination_address', 'eq', 'Тестовый адрес',
        {
            'request_destinations': [
                {'fullname': 'Тестовый адрес'.encode('utf-8')},
                {'fullname': 'Неподходящая конечная точка'.encode('utf-8')},
            ]
        },
        None,
        False,
    ),
    (
        'driver_license',
        'eq',
        '458365455',
        {
            'candidates': [
                {'driver_license': '458365455'}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        True,
    ),
    (
        'driver_license',
        'eq',
        '458АВ5455',
        {
            'candidates': [
                {'driver_license': '458AB5455'}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        True,
    ),
    (
        'driver_license',
        'regex',
        '^АВ.*5$',
        {
            'candidates': [
                {'driver_license': 'AB767436535'}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        True,
    ),
    (
        'license_plates',
        'regex',
        'AB0.*C77',
        {
            'candidates': [
                {'car_number': 'АВ076С77'.encode('utf-8')}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        True,
    ),
    (
        'license_plates',
        'eq',
        'AB076C77',
        {
            'candidates': [
                {'car_number': 'АВ076С77'.encode('utf-8')}
            ],
            'order_events': [
                {
                    'name': 'status_update',
                    'value': {
                        'candidate_index': 0,
                        'status': 'assigned'
                    }
                }
            ],
        },
        None,
        True,
    ),
    (
        'card_number', 'regex', '45744444.*9432',
        {'creditcard_credentials_card_number': '4574444476219432'},
        None, True,
    ),
    (
        'source_location', 'falls_inside',
        '37.535249,55.670616,37.731630,55.836160',
        {'request_source': {'geopoint': (37.616960, 55.754928)}},
        None, True,
    ),
    (
        'source_location', 'falls_inside',
        '37.535249,55.670616,37.731630', None,
        filters.InvalidReferenceValueError, None,
    ),
    (
        'source_location', 'falls_inside',
        'a,b,c,d', None,
        filters.InvalidReferenceValueError, None,
    ),
    (
        'source_location', 'regex', None, None,
        filters.IncompatibleOperatorError, None,
    ),
    (
        'any_destination_location', 'falls_inside',
        '37.535249,55.670616,37.731630,55.836160',
        {'request_destinations': [{'geopoint': (37.616960, 55.754928)}]},
        None, True,
    ),
    (
        'final_destination_location', 'falls_inside',
        '37.535249,55.670616,37.731630,55.836160',
        {
            'request_destinations': [
                {'geopoint': (37.616960, 55.754928)},
                {'geopoint': (38.616960, 55.754928)},
            ]
        },
        None, False,
    ),
    (
        'request_due', 'regex', None, None,
        filters.IncompatibleOperatorError, None,
    ),
    (
        'request_due', 'falls_inside',
        '2017-08-10T10:00:00Z,2017-08-11T10:00:00Z', None,
        filters.InvalidReferenceValueError, None,
    ),
    (
        'request_due', 'falls_inside',
        '10.00 28.10.2017/14.00 28.10.2017', None,
        filters.InvalidReferenceValueError, None,
    ),
    (
        'request_due', 'falls_inside',
        '2017-08-10T10:00:00Z/2017-08-11T10:00:00Z',
        {'request_due': _datetime_ts(2017, 8, 10, 10)}, None, True,
    ),
    (
        'request_due', 'falls_inside',
        '2017-08-10T10:00:00Z/2017-08-11T10:00:00Z',
        {'request_due': _datetime_ts(2017, 8, 10, 9)}, None, False,
    ),
    (
        'created', 'falls_inside',
        '2017-08-10T10:00:00Z/2017-08-11T10:00:00Z',
        {'created_order': _datetime_ts(2017, 8, 10, 16)}, None, True,
    ),
    (
        'user_phone', 'eq', '89992221122', None,
        filters.InvalidReferenceValueError, None,
    ),
    (
        'user_phone', 'eq', '+79992221122',
        {'user_phone': '+79992221122'}, None, True,
    ),
    (
        'user_phone', 'regex', None, None,
        filters.IncompatibleOperatorError, None,
    ),
    (
        'driver_phone', 'eq', '+79992221122',
        {'candidates_extra': [{'driver_phone': '+79992221122'}]}, None, True,
    ),
    ('order_id', 'eq', 'test_id', {'order_id': 'test_id'}, None, True),
    ('order_id', 'eq', 'test_id', {'order_id': 'not_test_id'}, None, False),
    (
        'order_id', 'eq', 'test_id', {
            'order_id': 'not_test_id',
            'performer_taxi_alias_id': 'test_id',
        }, None, True,
    ),
    (
        'order_id', 'eq', 'test_id', {
            'order_id': 'not_test_id',
            'performer_taxi_alias_id': 'not_test_id',
            'candidates': [
                {'alias_id': 'not_test_id'}, {'alias_id': 'test_id'},
            ],
        }, None, True,
    ),
])
@pytest.mark.asyncenv('blocking')
def test_filters(filter_name, operator, regex_or_exact,
                 input_row, raised_exc, expected_result):
    all_filters = filters.all_filters
    if not raised_exc:
        f = all_filters[filter_name](operator, regex_or_exact)
        result = f.is_suitable(input_row)
        assert result == expected_result
    else:
        with pytest.raises(raised_exc):
            all_filters[filter_name](operator, regex_or_exact)


@pytest.mark.parametrize('conditions,operator,rows_and_results', [
    (
        [
            {
                'expression': {
                    'field': 'user_phone',
                    'operator': 'eq',
                    'reference_value': '+79222222222',
                }
            },
            {
                'sub_conditions': [
                    {
                        'expression': {
                            'field': 'request_due',
                            'operator': 'falls_inside',
                            'reference_value':
                                '2017-08-10T10:00:00Z/2017-08-11T10:00:00Z',
                        },
                    },
                    {
                        'expression': {
                            'field': 'request_due',
                            'operator': 'falls_inside',
                            'reference_value':
                                '2017-08-22T10:00:00Z/2017-08-23T10:00:00Z',
                        },
                    }
                ],
                'operator': 'or',
            }
        ],
        'and',
        [
            (
                {
                    'user_phone': '+79222222222',
                    'request_due': _datetime_ts(2017, 8, 10, 15),
                },
                True,
            ),
            (
                {
                    'user_phone': '+79222222222',
                    'request_due': _datetime_ts(2017, 8, 22, 15),
                },
                True,
            ),
            (
                {
                    'user_phone': '+79222222221',
                    'request_due': _datetime_ts(2017, 8, 10, 15),
                },
                False,
            ),
            (
                {
                    'user_phone': '+79222222222',
                    'request_due': _datetime_ts(2017, 8, 16),
                },
                False,
            ),
        ]
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
@pytest.mark.now('2018-05-19 13:00:00+03')
def test_filter_query(conditions, operator, rows_and_results):
    filters_parsed = filters.parse_filters(conditions, operator)
    for row, expected_result in rows_and_results:
        result = utils.is_suitable(row, filters_parsed.filter_query)
        assert result == expected_result
