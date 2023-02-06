import typing

import pytest

from infranaim.models.configs import external_config
from scouts.app import constants

ROUTE_AGENT = '/agent'
ROUTE_CSRF = '/get_token'
ROUTE_LOGIN = '/login'
ROUTE_TAXIPARK_INFO = '/data/taxipark_info'
ROUTE_TICKET = '/get_ticket'
ROUTE_TICKETS = '/tickets'


@pytest.fixture
def check_agent_surveys(personal_check):
    def _wrapper(
            surveys: typing.List[dict],
            personal_response: str,
            store_personal: int,
    ):
        for survey in surveys:
            if personal_response == 'valid':
                assert survey['personal_phone_id'] == personal_check(
                    'personal_phone_id')
                assert survey['personal_license_id'] == personal_check(
                    'personal_license_id')
                if store_personal:
                    assert survey['phone'] == personal_check('phone')
                    assert survey['driver_license'] == personal_check(
                        'driver_license')
                else:
                    assert survey['phone'] == ''
                    assert survey['driver_license'] == ''
            elif personal_response == 'invalid_incoming_data':
                assert not survey.get('personal_phone_id')
                assert not survey.get('personal_license_id')
                assert survey['phone'] == personal_check('phone')
                assert survey['driver_license'] == personal_check(
                    'driver_license'
                )
    return _wrapper


@pytest.fixture
def check_agent_tickets(find_field, personal_check):
    def _wrapper(
            docs: typing.List[dict],
            personal_response: str,
            store_personal: int,
    ):
        lead_count = 0
        not_lead_count = 0
        status_double = constants.ZENDESK['STATUSES']['AGENT_DOUBLE']
        reason_double = constants.ZENDESK['REJECT_REASONS']['AGENT_DOUBLE']
        for doc in docs:
            custom_fields = doc['data']['custom_fields']
            assert len(custom_fields) > 6
            personal_phone = find_field(custom_fields, 360005536320)
            phone = find_field(custom_fields, 30557445)
            personal_license = find_field(custom_fields, 360005536340)
            driver_license = find_field(custom_fields, 30148269)
            deaf_candidate = find_field(custom_fields, 89)
            city_of_activation = find_field(custom_fields, 90)
            status = find_field(custom_fields, 230)
            reject_reason = find_field(custom_fields, 231)
            assert deaf_candidate
            assert not city_of_activation
            if (
                status['value'] == status_double
                and reject_reason['value'] == reason_double
            ):
                not_lead_count += 1
            elif (
                status['value'] != status_double
                and not reject_reason
            ):
                lead_count += 1

            if personal_response == 'valid':
                if store_personal:
                    assert all(
                        [personal_phone, personal_license,
                         phone, driver_license])
                    assert phone['value'] == personal_check('phone')
                    assert driver_license['value'] == personal_check(
                        'driver_license')
                else:
                    assert all([personal_phone, personal_license])
                    assert not any([phone, driver_license])

                assert personal_license['value'] == personal_check(
                    'personal_license_id')
                assert personal_phone['value'] == personal_check(
                    'personal_phone_id')

            elif personal_response == 'invalid_incoming_data':
                assert not any([personal_phone, personal_license])
                assert phone['value'] == personal_check('phone')
                assert driver_license['value'] == personal_check('driver_license')

        if personal_response == 'valid':
            assert lead_count == 1
            assert not_lead_count == 1
        else:
            assert lead_count == 1
            assert not_lead_count == 0
    return _wrapper


@pytest.mark.parametrize(
    'request_name, status_code',
    [
        ('bad_name', 400),
        ('bad_csrf_token', 403),
    ]
)
def test_agent_error(flask_client, log_user_in, load_json, csrf_token_session,
                request_name, status_code):
    data = {
        'login': 'agent',
        'password': 'agent_pass'
    }
    res = log_user_in(data)
    assert res.status_code == 200
    request_data = {'csrf_token': csrf_token_session()}
    request_data.update(load_json('post_data.json')[request_name])
    response = flask_client.post(ROUTE_AGENT, json=request_data)
    assert response.status_code == status_code


def test_no_auth(flask_client, load_json):
    response = flask_client.post(
        ROUTE_AGENT,
        json=load_json('post_data.json')['default'],
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    'personal_response, store_personal',
    [
        ('valid', 1),
        ('valid', 0),
        ('invalid_incoming_data', 1),
        ('invalid_incoming_data', 0),
    ]
)
def test_personal_data(
        flask_client_factory, load_json,
        get_mongo, patch,
        find_documents_in_scouts_agents,
        find_documents_in_create_queue,
        personal_check,
        personal,
        find_field,
        check_agent_tickets,
        check_agent_surveys,
        personal_response,
        store_personal,
):
    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
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

    mongo = get_mongo

    client = flask_client_factory(mongo)
    data = {
        'login': 'agent',
        'password': 'agent_pass',
        'csrf_token': client.get(ROUTE_CSRF).json['token']
    }
    client.post(ROUTE_LOGIN, json=data)
    request = load_json('personal_data.json')
    request['csrf_token'] = client.get(ROUTE_CSRF).json['token']
    for i in range(2):
        res = client.post(ROUTE_AGENT, json=request)
        assert res.status_code == 200

    surveys = find_documents_in_scouts_agents(mongo)
    assert len(surveys) == 2
    docs = find_documents_in_create_queue(mongo)
    if personal_response == 'valid':
        assert len(docs) == 2
    else:
        assert len(docs) == 1
    check_agent_surveys(surveys, personal_response, store_personal)
    check_agent_tickets(docs,personal_response, store_personal)


def test_park_info(
        flask_client, log_user_in, load_json,
        csrf_token_session,
):
    data = {
        'login': 'agent',
        'password': 'agent_pass'
    }
    log_user_in(data)
    park = flask_client.get(ROUTE_TAXIPARK_INFO + '?park_id=MONGO_ID1').json
    assert 'deaf_relation' in park


def test_pedestrian(
        flask_client_factory, load_json, get_mongo, find_field,
        patch, personal, find_documents_in_create_queue,
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

    mongo = get_mongo

    client = flask_client_factory(mongo)
    auth = {
        'login': 'agent',
        'password': 'agent_pass',
        'csrf_token': client.get(ROUTE_CSRF).json['token']
    }
    client.post(ROUTE_LOGIN, json=auth)
    request = load_json('post_data.json')['pedestrian_courier']
    request['csrf_token'] = client.get(ROUTE_CSRF).json['token']
    response = client.post(ROUTE_AGENT, json=request)
    assert response.status_code == 200
    docs = find_documents_in_create_queue(mongo)
    assert len(docs) == 1
    doc = docs[0]
    custom_fields = doc['data']['custom_fields']
    status = find_field(custom_fields, 230)
    assert status['value'] == 'become_delivery_walking_courier'
