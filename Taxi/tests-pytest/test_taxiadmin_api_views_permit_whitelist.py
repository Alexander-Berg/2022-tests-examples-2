# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django import test as django_test
import pytest

from taxi.util import helpers


@pytest.mark.now('2018-02-06T00:00:00+0300')
@pytest.mark.asyncenv('blocking')
def test_permit_whitelist():
    data = {
        'car_numbers': ['AB001', 'AB002'],
        'till': '2018-03-06T00:00:00+0300'
    }
    add_response = django_test.Client().post(
        '/api/permits/whitelist/insert/',
        json.dumps(data),
        'application/json'
    )
    assert add_response.status_code == 200
    clean_numbers = [helpers.clean_number(car_number)
                     for car_number in data['car_numbers']]
    details_response = django_test.Client().get(
        '/api/permits/whitelist/?skip=0&limit=2'
    )
    details = json.loads(details_response.content)
    assert len(details['items']) == details['total'] == 2
    for item in details['items']:
        assert item['login'] == 'dmkurilov'
        assert item['till'] == '2018-03-06T00:00:00+0300'
        assert item['added'] == '2018-02-06T00:00:00+0300'
    car_numbers = [item['car_number'] for item in details['items']]
    assert sorted(car_numbers) == sorted(clean_numbers)
    data = {
        'car_numbers': ['AB001'],
    }
    remove_response = django_test.Client().post(
        '/api/permits/whitelist/delete/',
        json.dumps(data),
        'application/json'
    )
    assert remove_response.status_code == 200
    clean_number = helpers.clean_number(data['car_numbers'][0])
    details_response = django_test.Client().get(
        '/api/permits/whitelist/?skip=0&limit=2'
    )
    details = json.loads(details_response.content)
    assert len(details['items']) == details['total'] == 1
    car_numbers = [item['car_number'] for item in details['items']]
    assert clean_number not in car_numbers
