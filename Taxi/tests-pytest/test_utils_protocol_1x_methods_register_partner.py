import json

import pytest

import mocks
from taxi.core import async
from taxi.internal.dbh import partners
from utils.protocol_1x.methods import register_partner


@pytest.inline_callbacks
def test_set_partner_no_req_fields():
    content = {}
    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert response == {
        'errors': [
            {
                'field': 'park-name',
                'error': 'missing or invalid type',
            },
        ]
    }
    assert request.response_code == 400


@pytest.inline_callbacks
def test_set_partner_field_invalid_value():
    content = {
        'park-name': 'pname',
        'is-individual-entrepreneur': 'a',
    }
    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert response == {
        'errors': [
            {
                'field': 'is-individual-entrepreneur',
                'error': 'invalid value',
            }
        ]
    }
    assert request.response_code == 400


@pytest.inline_callbacks
def test_set_partner_ok():
    content = {
        'park-name': 'pname',
        'id': 'm-id',
        'user-fathername': 'FN',
        'user-secondname': 'LN',
        'is-individual-entrepreneur': 'yes',
    }

    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert request.response_code is None, response

    partners_created = yield partners.Doc.find_many()
    assert len(partners_created) == 1
    partner = partners_created[0]
    assert partner.client_ip == '1.2.3.4'
    assert partner.client_ua == 'User-Agent'
    assert partner.registration_form.park_name == 'pname'
    assert partner.registration_form.user_middlename == 'FN'
    assert partner.registration_form.user_lastname == 'LN'
    assert partner.registration_form.is_individual_entrepreneur == 'yes'


@pytest.inline_callbacks
def test_set_partner_ok_indiv_enterpern_default_value():
    content = {
        'park-name': 'pname',
        'id': 'm-id',
        'user-fathername': 'FN',
        'user-secondname': 'LN',
    }

    request = mocks.FakeRequest(content=json.dumps(content))
    response = yield _get_response(request)
    assert request.response_code is None, response

    partners_created = yield partners.Doc.find_many()
    assert len(partners_created) == 1
    partner = partners_created[0]
    assert partner.client_ip == '1.2.3.4'
    assert partner.client_ua == 'User-Agent'
    assert partner.registration_form.park_name == 'pname'
    assert partner.registration_form.user_middlename == 'FN'
    assert partner.registration_form.user_lastname == 'LN'
    assert partner.registration_form.is_individual_entrepreneur == 'no'


@async.inline_callbacks
def _get_response(request):
    method = register_partner.Method()
    method.user_ip = '1.2.3.4'
    method.user_agent = 'User-Agent'

    response = yield method.POST(request)
    async.return_value(response)
