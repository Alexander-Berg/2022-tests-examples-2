# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import pytest
from django import test as django_test


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb
@pytest.mark.parametrize('country,expected_code', [
    ('rus', 200),
    ('bel', 404),
])
def test_list_modifiers(country, expected_code):
    client = django_test.Client()
    response = client.post(
        '/api/price_modifiers/list/', json.dumps({'country': country}),
        'application/json'
    )
    assert response.status_code == expected_code, 'Got {}'.format(response.content)
    data = json.loads(response.content)
    if expected_code == 200:
        assert data == {
            'country': 'rus',
            'modifiers': [
                {
                    'id': 'ya_plus',
                    'type': 'multiplier',
                    'value': '0.9',
                    'tariff_categories': ['econom'],
                    'is_enabled': True,
                    'pay_subventions': False
                },
                {
                    'id': 'ya_plus_cashback',
                    'type': 'cashback',
                    'value': '0.9',
                    'tariff_categories': ['econom', 'business'],
                    'is_enabled': True,
                    'pay_subventions': False
                },
            ]
        }


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb
@pytest.mark.parametrize('country,classes,type,ticket,expected_code', [
    # update
    ('rus', ['business', 'vip'], 'multiplier', 'TAXIRATE-123', 200),
    # create
    ('arm', ['business', 'vip'], 'multiplier', 'TAXIRATE-123', 200),
    # type cashback
    ('arm', ['business', 'vip'], 'cashback', 'TAXIRATE-123', 200),
    # no ticket
    ('rus', ['business', 'vip'], 'multiplier', '', 406),
    # wrong country
    ('xxx', ['business'], 'multiplier', 'TAXIRATE-123', 400),
    # wrong tariff
    ('rus', ['cheap_trip'], 'multiplier', 'TAXIRATE-123', 400),
    # wrong type
    ('rus', ['business'], 'some-other-type', 'TAXIRATE-123', 400)
    ], ids=[
        'update',
        'create',
        'cashback',
        'no-ticket',
        'wrong-country',
        'wrong-tariff',
        'wrong-type',
    ]
)
def test_save_modifiers(country, classes, type, ticket, expected_code):
    doc = {
        'country': country,
        'modifiers': [{
            'is_enabled': True,
            'type': type,
            'id': 'ya_plus',
            'value': '0.9',
            'tariff_categories': classes,
            'pay_subventions': True
        }],
        'ticket': ticket,
    }
    response = django_test.Client().post(
        '/api/price_modifiers/save/', json.dumps(doc), 'application/json'
    )
    assert response.status_code == expected_code, response.content
