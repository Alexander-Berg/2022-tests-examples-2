# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import namedtuple

from django import test as django_test
import pytest


@pytest.fixture
def ticket_check_is_successful(patch):
    @patch('taxiadmin.audit.check_ticket')
    def check_ticket(ticket, login):
        return


@pytest.mark.asyncenv('blocking')
@pytest.mark.load_data(_load=False)
@pytest.mark.config(
    ADMIN_REQUIRE_TICKET_TO_EDIT_COUNTRY_MONEY_FIELDS=True,
)
def test_get_list(ticket_check_is_successful, load):
    doc = json.loads(load('get_list_data.json'))
    request_data = dict(doc)
    request_data['ticket'] = 'TAXIRATE-10'
    response = django_test.Client().post(
        '/api/countries/save/', json.dumps(request_data), 'application/json'
    )
    assert response.status_code == 200, response.content
    assert json.loads(response.content) == {}

    response = django_test.Client().get('/api/countries/list/')
    assert response.status_code == 200
    assert json.loads(response.content) == {'items': [doc]}

    del doc['vat']
    del doc['min_hold_amount']
    del doc['hide_check_contracts']
    del doc['carrier_enabled']
    del doc['antifraud_paid_count']
    del doc['currency']
    del doc['promocode_max_value']
    del doc['currency_rules']
    request_data = dict(doc)
    request_data['ticket'] = 'TAXIRATE-10'

    response = django_test.Client().post(
        '/api/countries/save/', json.dumps(request_data), 'application/json'
    )
    assert response.status_code == 200, response.content
    assert json.loads(response.content) == {}

    response = django_test.Client().get('/api/countries/list/')
    assert response.status_code == 200
    assert json.loads(response.content) == {'items': [doc]}


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
@pytest.mark.disable_territories_api_mock
def test_get_list_x_ya_request_id(areq_request, patch):
    uuid = 'test_uuid'

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = namedtuple('uuid4', 'hex')
        return uuid4_(uuid)

    @areq_request
    def countries(*args, **kwargs):
        assert kwargs['headers']['X-YaRequestId'] == uuid
        return areq_request.response(200, body=json.dumps({'countries': []}))

    response = django_test.Client().get('/api/countries/list/')
    assert response.status_code == 200
    assert countries.call


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('suffix,expected_code', [
    (None, 200),
    ('', 200),
    ('armeny', 200),
    ('yerevan', 400),
])
@pytest.mark.translations([
    (
        'taximeter_messages', 'subventions_feed.bonus_title_armeny', 'ru',
        'text'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_title_armeny', 'ru',
        'text'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_text_armeny', 'ru',
        'text'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_text_sms_armeny',
        'ru', 'text'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_armeny', 'ru',
        'text'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_sms_armeny', 'ru',
        'text'
    ),
])
@pytest.mark.config(
    ADMIN_REQUIRE_TICKET_TO_EDIT_COUNTRY_MONEY_FIELDS=True,
)
def test_subventions_text_suffix(ticket_check_is_successful, suffix,
                                 expected_code):
    doc = {
        'id': 'rus',
        'code2': 'RU',
        'currency': 'RUB',
        'eng': 'Russia',
        'hide_check_contracts': True,
        'lang': 'ru',
        'min_hold_amount': '1',
        'name': 'Россия',
        'national_access_code': '8',
        'phone_code': '7',
        'phone_max_length': 11,
        'phone_min_length': 11,
        'promocode_max_value': 2500,
        'region_id': 225,
        'vat': 11800,
        'antifraud_paid_count': 3,
        'ticket': 'TAXIRATE-10',
    }
    if suffix is not None:
        doc['subventions_text_suffix'] = suffix
    response = django_test.Client().post(
        '/api/countries/save/', json.dumps(doc), 'application/json'
    )
    assert response.status_code == expected_code, response.content


@pytest.mark.parametrize('request_data,expected_code', [
    (
        # New country with money fields
        {
            'id': 'rus',
            'code2': 'RU',
            'currency': 'RUB',
            'eng': 'Russia',
            'hide_check_contracts': True,
            'lang': 'ru',
            'min_hold_amount': '1',
            'name': 'Россия',
            'national_access_code': '8',
            'phone_code': '7',
            'phone_max_length': 11,
            'phone_min_length': 11,
            'promocode_max_value': 2500,
            'region_id': 225,
            'vat': 11800,
            'antifraud_paid_count': 3,
        },
        400,
    ),
    (
        # New country without money fields
        {
            'id': 'rus',
            'code2': 'RU',
            'eng': 'Russia',
            'hide_check_contracts': True,
            'lang': 'ru',
            'name': 'Россия',
            'national_access_code': '8',
            'phone_code': '7',
            'phone_max_length': 11,
            'phone_min_length': 11,
            'region_id': 225,
        },
        200,
    ),
    (
        # Existing country with money fields changed
        {
            'id': 'uus',
            'code2': 'RU',
            'currency': 'RUB',
            'eng': 'Russia',
            'hide_check_contracts': True,
            'lang': 'ru',
            'min_hold_amount': '12',
            'name': 'Россия',
            'national_access_code': '8',
            'phone_code': '7',
            'phone_max_length': 11,
            'phone_min_length': 11,
            'promocode_max_value': 2500,
            'region_id': 225,
            'vat': 11800,
            'antifraud_paid_count': 3,
        },
        400,
    ),
    (
        # Existing country with money field being deleted
        {
            'id': 'uus',
            'code2': 'RU',
            'currency': 'RUB',
            'eng': 'Russia',
            'hide_check_contracts': True,
            'lang': 'ru',
            'name': 'Россия',
            'national_access_code': '8',
            'phone_code': '7',
            'phone_max_length': 11,
            'phone_min_length': 11,
            'promocode_max_value': 2500,
            'region_id': 225,
            'vat': 11800,
            'antifraud_paid_count': 3,
        },
        400,
    ),
    (
        # Existing country with money field being added
        {
            'id': 'qus',
            'code2': 'RU',
            'currency': 'RUB',
            'eng': 'Russia',
            'hide_check_contracts': True,
            'lang': 'ru',
            'min_hold_amount': '12',
            'name': 'Россия',
            'national_access_code': '8',
            'phone_code': '7',
            'phone_max_length': 11,
            'phone_min_length': 11,
            'promocode_max_value': 2500,
            'region_id': 225,
            'vat': 11800,
            'antifraud_paid_count': 3,
        },
        400,
    ),
    (
        # New country with weekends
        {
            'id': 'rus',
            'code2': 'RU',
            'eng': 'Russia',
            'hide_check_contracts': True,
            'lang': 'ru',
            'name': 'Россия',
            'national_access_code': '8',
            'phone_code': '7',
            'phone_max_length': 11,
            'phone_min_length': 11,
            'region_id': 225,
            'weekends': ['monday', 'tuesday', 'wednesday', 'thursday',
                         'friday', 'saturday', 'sunday']
        },
        200,
    ),
    (
        # New country without weekends
        {
            'id': 'rus',
            'code2': 'RU',
            'eng': 'Russia',
            'hide_check_contracts': True,
            'lang': 'ru',
            'name': 'Россия',
            'national_access_code': '8',
            'phone_code': '7',
            'phone_max_length': 11,
            'phone_min_length': 11,
            'region_id': 225,
            'weekends': []
        },
        200,
    ),
    (
        # New country with bad weekends
        {
            'id': 'rus',
            'code2': 'RU',
            'eng': 'Russia',
            'hide_check_contracts': True,
            'lang': 'ru',
            'name': 'Россия',
            'national_access_code': '8',
            'phone_code': '7',
            'phone_max_length': 11,
            'phone_min_length': 11,
            'region_id': 225,
            'weekends': ['newday']
        },
        400,
    ),
])
@pytest.mark.config(
    ADMIN_REQUIRE_TICKET_TO_EDIT_COUNTRY_MONEY_FIELDS=True,
)
@pytest.mark.load_data(
    countries='test_modifying_money_fields_requires_ticket'
)
@pytest.mark.asyncenv('blocking')
def test_modifying_money_fields_requires_ticket(request_data, expected_code):
    response = django_test.Client().post(
        '/api/countries/save/', json.dumps(request_data), 'application/json'
    )
    assert response.status_code == expected_code, response.content
