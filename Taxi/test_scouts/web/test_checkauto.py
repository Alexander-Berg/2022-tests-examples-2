import datetime
import random

import freezegun
import pytest

from infranaim.app import ErrorResponses
from infranaim.models.configs import external_config
from infranaim.utils import validation_utils

ROUTE = '/enter_number'
ROUTE_CSRF = '/get_token'
ROUTE_USER_DATA = '/get_user_data'


def assert_checks(message, not_new):
    assert message
    if not_new:
        assert 'Отменяй' in message
    else:
        assert 'Берем' in message


@pytest.mark.parametrize(
    'role, status_code',
    [
        ('agent', 400),
        ('scout', 400),
    ]
)
def test_check_error(
        flask_client, log_user_role, load_json,
        csrf_token_session, role,
        status_code,
):
    log_user_role(role)

    requests = load_json('requests.json')['invalid']
    for name, data in requests.items():
        data['csrf_token'] = csrf_token_session()
        response = flask_client.post(ROUTE, json=data)
        assert response.status_code == status_code


@pytest.mark.parametrize(
    'role, personal_response',
    [
        ('agent', 'valid'),
        ('agent', 'invalid'),
        ('scout', 'valid'),
        ('scout', 'invalid'),
    ]
)
def test_check_valid(
        flask_client, load_json, get_mongo, patch,
        personal, personal_imitation, log_user_role, role,
        personal_response,
):
    @patch('infranaim.clients.personal.PreparedRequestMain._generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal(personal_response, *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    client = flask_client
    mongo = get_mongo
    log_user_role(role)

    phone_code = client.get(ROUTE_USER_DATA).json['country_phone_code']
    requests = load_json('requests.json')['valid']

    for name, data in requests.items():
        data['csrf_token'] = client.get(ROUTE_CSRF).json['token']
        res = client.post(ROUTE, json=data)
        assert res.status_code == 200
        query = {'check_type': data['type']}
        not_new = not name.endswith('_new')
        assert_checks(res.json['message'], not_new)
        query['check_result'] = not_new
        doc = mongo.check_table.find_one(query)
        assert doc
        if data['type'] in ['phone_number', 'license_number']:
            value = data['number']
            if data['type'] == 'phone_number':
                value = '{}{}'.format(phone_code, data['number'])
                value = validation_utils.fix_phone(value)
            else:
                value = validation_utils.fix_license(value)
            if personal_response == 'valid':
                assert doc['check_data'] == personal_imitation(value)
            else:
                assert not doc['check_data']
        else:
            assert doc['check_data'] == validation_utils.fix_car_plate(
                data['number'])


@pytest.mark.parametrize('role', ['agent', 'scout'])
def test_check_valid_candidates(
        flask_client, load_json, get_mongo, patch,
        personal, personal_imitation, log_user_role, role,
):
    @patch('infranaim.clients.personal.PreparedRequestMain._generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal('valid', *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    @patch('infranaim.clients.hiring_candidates.Candidates._make_request')
    def _candidates(route, payload, log_extra=None):
        assert payload['days'] == 45
        response = {'is_active': False}
        if route == 'CHECK_PHONE':
            phone_id = payload['personal_phone_id']
            if phone_id == '1136c6d5c4a9432d96323a0a56e89ef0':
                response['is_active'] = True
        else:
            license_id = payload['personal_license_id']
            if license_id == '0acdfcc640054eeaa7ae282cfc81e628':
                response['is_active'] = True
        return response

    external_config.HIRING_INFRANAIM_ENABLE_CANDIDATES = True
    client = flask_client
    mongo = get_mongo
    log_user_role(role)

    phone_code = client.get(ROUTE_USER_DATA).json['country_phone_code']
    requests = load_json('requests.json')['valid_candidates']

    for name, data in requests.items():
        data['csrf_token'] = client.get(ROUTE_CSRF).json['token']
        res = client.post(ROUTE, json=data)
        assert res.status_code == 200
        query = {'check_type': data['type']}
        not_new = not name.endswith('_new')
        assert_checks(res.json['message'], not_new)
        query['check_result'] = not_new
        doc = mongo.check_table.find_one(query)
        assert doc
        if data['type'] in ['phone_number', 'license_number']:
            value = data['number']
            if data['type'] == 'phone_number':
                value = '{}{}'.format(phone_code, data['number'])
                value = validation_utils.fix_phone(value)
            else:
                value = validation_utils.fix_license(value)
            assert doc['check_data'] == personal_imitation(value)
        else:
            assert doc['check_data'] == validation_utils.fix_car_plate(
                data['number'])
    external_config.HIRING_INFRANAIM_ENABLE_CANDIDATES = False


@pytest.mark.parametrize(
    'timestr, result',
    [
        ('2020-03-17T12:00:00Z', True),
        ('2020-06-17T12:00:00Z', False),
    ]
)
def test_check_phone_experiment(
        flask_client, log_user_role, patch, personal, timestr, result
):
    @patch('infranaim.clients.personal.PreparedRequestMain._generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal('valid', *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    with freezegun.freeze_time(timestr):
        client = flask_client
        log_user_role('agent')
        data = {
            'type': 'phone_number',
            'number': '7014567503',
            'csrf_token': client.get('/get_token').json['token']
        }
        res = client.post(ROUTE, json=data)
        assert res.status_code == 200
        assert_checks(res.json['message'], result)
