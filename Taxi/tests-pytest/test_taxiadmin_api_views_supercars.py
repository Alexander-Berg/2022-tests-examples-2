# coding: utf8

from __future__ import unicode_literals

import json
import StringIO

from django import test as django_test
import pytest

from taxi.util import helpers
from taxi.core import async
from taxi.internal import dbh


@pytest.mark.parametrize('method, params, expected_code, expected_response', [
    ('post', '', 405, None),
    (
        'get', '', 200,
        [
            {
                'clid': '*',
                'car_number': u'7АМР77777',
                'model': 'Mercedes Benz S-classe',
                'age': 2016,
                'added': '2018-01-03T03:00:00+0300',
                'added_by': 'dummy_man',
            },
            {
                'clid': 'fourth_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Fourth Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
            },
            {
                'clid': 'some_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Some Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
            {
                'clid': 'third_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Third Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
            {
                'clid': 'third_park_id',
                'car_number': 'QWЕ456',
                'park_name': 'Third Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-02T03:00:00+0300',
                'added_by': 'anybody',

            },
            {
                'clid': 'another_park_id',
                'car_number': 'QWЕ789',
                'park_name': 'Another Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-03T03:00:00+0300',
                'added_by': 'nobody',
            },
            {
                'clid': 'some_park_id',
                'car_number': 'ZХС789',
                'park_name': 'Some Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'BMW X5',
                'age': 2005,
                'added': '2018-01-03T03:00:00+0300',
                'added_by': 'nobody',
            },
            {
                'clid': 'another_park_id',
                'car_number': 'АSD123',
                'park_name': 'Another Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Toyota Corolla',
                'age': 2012,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
            {
                'clid': 'another_park_id',
                'car_number': 'АSD456',
                'park_name': 'Another Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Toyota Corolla',
                'age': 2012,
                'added': '2018-01-02T03:00:00+0300',
                'added_by': 'anybody',
            },
            {
                'clid': 'some_park_id',
                'car_number': 'АSD456',
                'park_name': 'Some Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Toyota Corolla',
                'age': 2012,
                'added': '2018-01-02T03:00:00+0300',
                'added_by': 'anybody',
            },
            {
                'clid': 'third_park_id',
                'car_number': 'АSD789',
                'park_name': 'Third Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Toyota Corolla',
                'age': 2012,
                'added': '2018-01-03T03:00:00+0300',
                'added_by': 'nobody',
            },
        ]
    ),
    (
        'get', '?offset=3&limit=3', 200,
        [
            {
                'clid': 'third_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Third Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
            {
                'clid': 'third_park_id',
                'car_number': 'QWЕ456',
                'park_name': 'Third Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-02T03:00:00+0300',
                'added_by': 'anybody',

            },
            {
                'clid': 'another_park_id',
                'car_number': 'QWЕ789',
                'park_name': 'Another Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-03T03:00:00+0300',
                'added_by': 'nobody',
            },
        ]
    ),
    (
        'get', '?clid=another_park_id', 200,
        [
            {
                'clid': 'another_park_id',
                'car_number': 'QWЕ789',
                'park_name': 'Another Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-03T03:00:00+0300',
                'added_by': 'nobody',
            },
            {
                'clid': 'another_park_id',
                'car_number': 'АSD123',
                'park_name': 'Another Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Toyota Corolla',
                'age': 2012,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
            {
                'clid': 'another_park_id',
                'car_number': 'АSD456',
                'park_name': 'Another Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Toyota Corolla',
                'age': 2012,
                'added': '2018-01-02T03:00:00+0300',
                'added_by': 'anybody',
            },
        ]
    ),
    (
        'get', '?car_number=qwe123', 200,
        [
            {
                'clid': 'fourth_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Fourth Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
            },
            {
                'clid': 'some_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Some Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
            {
                'clid': 'third_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Third Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
        ]
    ),
    (
        'get', '?car_number=123', 200,
        [
            {
                'clid': 'fourth_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Fourth Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
            },
            {
                'clid': 'some_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Some Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
            {
                'clid': 'third_park_id',
                'car_number': 'QWЕ123',
                'park_name': 'Third Park',
                'city': 'spb',
                'country': 'Россия',
                'model': 'Ford Focus',
                'age': 2000,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
            {
                'clid': 'another_park_id',
                'car_number': 'АSD123',
                'park_name': 'Another Park',
                'city': 'moscow',
                'country': 'Россия',
                'model': 'Toyota Corolla',
                'age': 2012,
                'added': '2018-01-01T03:00:00+0300',
                'added_by': 'somebody',
            },
        ]
    ),
    (
        'get', '?car_number=777', 200,
        [
            {
                'clid': '*',
                'car_number': u'7АМР77777',
                'model': 'Mercedes Benz S-classe',
                'age': 2016,
                'added': '2018-01-03T03:00:00+0300',
                'added_by': 'dummy_man',
            }
        ]
    ),
    (
        'get', '?clid=*', 200,
        [
            {
                'clid': '*',
                'car_number': u'7АМР77777',
                'model': 'Mercedes Benz S-classe',
                'age': 2016,
                'added': '2018-01-03T03:00:00+0300',
                'added_by': 'dummy_man',
            },
        ]
    )
])
@pytest.mark.asyncenv('blocking')
def test_list(method, params, expected_code, expected_response, patch):
    @patch('taxi.internal.driver_manager._set_brand_model')
    @async.inline_callbacks
    def _set_brand_model(brand, model, car_doc):
        yield
        car_doc['model'] = model

    args = ['/api/supercars/list/' + params]
    if method == 'post':
        args += [{'some_param': 'some_value'}, 'application/json']

    method = getattr(django_test.Client(), method)
    http_response = method(*args)

    assert http_response.status_code == expected_code

    if expected_code == 200:
        response = json.loads(http_response.content)
        assert response == expected_response


@pytest.mark.parametrize('action, method, data, expected_code', [
    ('bulk_add', 'get', {}, 405),
    (
        'bulk_add', 'post',
        {
            'items': [
                {'clid': 'some_park_id', 'car_number': 'abc000'},
                {'clid': 'some_park_id', 'car_number': 'авс001'},
                {'clid': 'another_park_id', 'car_number': 'ABC002'},
            ],
            'ticket': 'TAXIRATE-111',
        },
        200,
    ),
    ('bulk_add', 'get', {}, 405),
    (
        'bulk_add', 'post',
        {
            'items': [
                {'clid': 'another_park_id', 'car_number': 'АSD123'},
                {'clid': 'third_park_id', 'car_number': 'QWЕ123'},
            ],
            'ticket': 'TAXIRATE-222',
        },
        200,
    ),
    ('bulk_add', 'get', {}, 405),
    (
        'bulk_add', 'post',
        {
            'items': [
                {'clid': 'another_park_id', 'car_number': 'АSD123'},
                {'clid': '*', 'car_number': 'ASD123'},
            ],
            'ticket': 'TAXIRATE-222',
        },
        200,
    ),
    ('bulk_add', 'get', {}, 405),
    (
            'bulk_add', 'post',
            {
                'items': [
                    {'clid': '*', 'car_number': 'АSD123'},
                    {'clid': '*', 'car_number': 'QWЕ123'},
                ],
                'ticket': 'TAXIRATE-222',
            },
            200,
    ),
    ('clear_park', 'get', {}, 405),
    (
        'clear_park', 'post',
        {
            'clid': '*',
            'ticket': 'TAXIRATE-333',
        },
        406,
    ),
    (
        'clear_park', 'post',
        {
            'clid': 'some_park_id',
            'ticket': 'TAXIRATE-333',
        },
        200,
    ),
    (
        'clear_park', 'post',
        {
            'clid': 'third_park_id',
            'ticket': 'TAXIRATE-333',
        },
        200,
    ),
    (
        'bulk_remove', 'post',
        {
            'ticket': 'TAXIRATE-333',
            'items': [
                {
                    'clid': 'strange_park_id',
                    'car_number': 'АSD123'
                }
            ]
        },
        406
    ),
    (
        'bulk_remove', 'post',
        {
            'ticket': 'TAXIRATE-333',
            'items': [
                {
                    'clid': '*',
                    'car_number': 'АSD123'
                }
            ]
        },
        200
    ),
    (
        'bulk_remove', 'post',
        {
            'ticket': 'TAXIRATE-333',
            'items': [
                {
                    'clid': 'strange_id',
                    'car_number': 'АSD123'
                }
            ]
        },
        406
    ),
    (
        'bulk_remove', 'post',
        {
            'ticket': 'TAXIRATE-333',
            'items': [
                {
                    'clid': 'another_park_id',
                    'car_number': 'АSD123'
                }
            ]
        },
        200
    )
])
@pytest.mark.config(ADMIN_AUDIT_TICKET_CONFIG={'enabled': False})
@pytest.mark.config(ADMIN_AUDIT_TICKET_ENABLE_COMMENT=False)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_modify(action, method, data, expected_code):
    args = ['/api/supercars/{}/'.format(action)]
    if method == 'post':
        args += [json.dumps(data), 'application/json']

    method = getattr(django_test.Client(), method)
    http_response = method(*args)

    assert http_response.status_code == expected_code

    if expected_code == 200:
        if 'items' in data:
            items = data['items']
        else:
            items = [data]

        supercars = yield dbh.supercars.Doc.find_many()
        supercars = dbh.supercars.Doc.group_by_id(supercars)

        for item in items:
            if action == 'bulk_add':
                car_number = helpers.clean_number(item['car_number'])
                assert car_number in supercars
                doc = supercars[car_number]
                assert doc.satisfies_conditions(item['clid'])
            elif action == 'bulk_remove':
                assert item['car_number'] not in supercars
            elif action == 'clear_park':
                for id, supercar in supercars.iteritems():
                    parks = supercar.get_condition_parks_in()
                    clid = data['clid']

                    if clid in parks:
                        assert supercars == {}

                    assert clid not in parks


@pytest.mark.parametrize('method, ticket, csv_data, expected_code', [
    (
        'post',

        'TAXIRATE-333',

        'clid,car_number\n'
        'some_park_id,abc000\n'
        'some_park_id,авс001\n'
        'another_park_id,ABC002\n',

        200,
    ),
    (
            'post',

            None,

            'clid,car_number\n'
            'some_park_id,abc000\n'
            'some_park_id,авс001\n'
            'another_park_id,ABC002\n',

            400,
    ),
])
@pytest.mark.config(ADMIN_AUDIT_TICKET_CONFIG={'enabled': False})
@pytest.mark.config(ADMIN_AUDIT_TICKET_ENABLE_COMMENT=False)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_csv_import(method, ticket, csv_data, expected_code):
    args = ['/api/supercars/csv_import/']
    if method == 'post':
        csv_fh = StringIO.StringIO(csv_data.encode('utf8'))
        csv_fh.name = 'test.csv'

        data = {
            'filename': csv_fh,
        }
        if ticket:
            data['ticket'] = ticket

        args.append(data)

    method = getattr(django_test.Client(), method)
    http_response = method(*args)
    assert http_response.status_code == expected_code

    if expected_code == 200:
        supercars = yield dbh.supercars.Doc.find_many()
        supercars = dbh.supercars.Doc.group_by_id(supercars)

        first_line = True
        for line in csv_data.split('\n'):
            if first_line:
                first_line = False
                continue
            if line == '':
                continue
            columns = line.split(',')
            assert len(columns) == 2
            clid, car_number = columns
            car_number = helpers.clean_number(car_number)

            assert car_number in supercars
