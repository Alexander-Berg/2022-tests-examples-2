# -- coding: utf8 --

from __future__ import unicode_literals
from taxi.core import db
from django import test as django_test
import pytest
import json


@pytest.mark.asyncenv('blocking')
def test_delete():
    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 2

    client = django_test.Client()
    client.post('/api/classifier/exceptions/delete/', json.dumps({
        'car_number': 'В444ВВ',
        'rule_ids': [
            '1', '2'
        ]
    }), 'application/json')

    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 0


@pytest.mark.asyncenv('blocking')
def test_add():
    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 2

    client = django_test.Client()
    client.post('/api/classifier/exceptions/add/', json.dumps({
        'car_number': 'В444ВВ',
        'rules': [
            {
                'categories': ['econom'],
                "zones": ["moscow"],
                'end': '22/11/2019',
            },
        ],
    }), 'application/json')

    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 3


@pytest.mark.asyncenv('blocking')
def test_update():
    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 2

    client = django_test.Client()
    client.post('/api/classifier/exceptions/update/', json.dumps({
        'car_number': 'В444ВВ',
        'rules': [
            {
                'categories': ['econom'],
                "zones": ["moscow"],
                'end': '22/11/2019',
            },
        ],
    }), 'application/json')

    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 3


@pytest.mark.asyncenv('blocking')
def test_delete_bulk(open_file):
    result = db.cars.find_one({'_id': 'В444ВА'}).result
    assert len(result['classifier_exceptions']) == 2

    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 2

    client = django_test.Client()
    with open_file('delete_bulk.csv') as f:
        client.post(
            '/api/classifier/exceptions/delete_bulk/',
            {'exceptions': f}
        )

    result = db.cars.find_one({'_id': 'В444ВА'}).result
    assert len(result['classifier_exceptions']) == 1

    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 1


@pytest.mark.asyncenv('blocking')
def test_add_bulk(open_file):
    result = db.cars.find_one({'_id': 'В444ВА'}).result
    assert len(result['classifier_exceptions']) == 2

    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 2

    client = django_test.Client()
    with open_file('add_bulk.csv') as f:
        client.post(
            '/api/classifier/exceptions/add_bulk/',
            {'exceptions': f}
        )

    result = db.cars.find_one({'_id': 'В444ВА'}).result
    assert len(result['classifier_exceptions']) == 3

    result = db.cars.find_one({'_id': 'В444ВВ'}).result
    assert len(result['classifier_exceptions']) == 3


@pytest.mark.asyncenv('blocking')
def test_delete_bulk_malformed(open_file):
    client = django_test.Client()
    with open_file('delete_bulk_malformed.csv') as f:
        response = client.post(
            '/api/classifier/exceptions/delete_bulk/',
            {'exceptions': f}
        )
        response_json = json.loads(response.content)
        assert response_json.get('status') == 'error'
        assert response_json.get('code') == 'BAD_LINE'
