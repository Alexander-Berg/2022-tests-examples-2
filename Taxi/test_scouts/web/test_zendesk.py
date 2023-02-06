import json

import freezegun
import pytest
import requests

from infranaim.models.configs import external_config


FIELDS_MAPPING = {
    'phone': 'personal_phone_id',
    'driver_license': 'personal_license_id',
}


def assert_personal_in_data(document, invert=False):
    for field in FIELDS_MAPPING.keys():
        if invert:
            assert not document[field]
        else:
            assert document[field]


def assert_personal_ids_in_data(document, invert=False):
    for field in FIELDS_MAPPING.values():
        if invert:
            assert field not in document
        else:
            assert field in document


@freezegun.freeze_time('2019-10-04T14:00:00Z')
@pytest.mark.parametrize(
    'data_type, vacancy, name, status_code, '
    'personal_response, store_personal',
    [
        (
            'valid', 'driver',
            'russia_moscow_default_vacancy_default_workflow', 200,
            'valid', 1,
        ),
        (
            'valid', 'driver',
            'russia_kazan', 200,
            'valid', 1,
        ),
        (
            'valid', 'driver',
            'kazakhstan_self_employed', 200,
            'valid', 1,
        ),
        (
            'valid', 'driver',
            'active_checked', 200,
            'valid', 1,
        ),
        (
            'valid', 'driver',
            'active_not_checked', 200,
            'valid', 1,
        ),
        (
            'valid', 'courier',
            'active', 200,
            'valid', 1,
        ),
        (
            'valid', 'courier',
            'not_active', 200,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'invalid_phone_empty', 200,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'invalid_phone_string', 200,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'invalid_phone_bad_format', 200,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'invalid_phone_unparsable', 200,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'missing_phone', 400,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'invalid_ticket_id', 400,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'missing_ticket_id', 400,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'missing_s_code', 400,
            'valid', 1,
        ),
        (
            'invalid', 'courier',
            'invalid_phone_empty', 200,
            'valid', 1,
        ),
        (
            'invalid', 'courier',
            'invalid_phone_string', 200,
            'valid', 1,
        ),
        (
            'invalid', 'courier',
            'invalid_phone_bad_format', 200,
            'valid', 1,
        ),
        (
            'invalid', 'courier',
            'invalid_phone_unparsable', 200,
            'valid', 1,
        ),
        (
            'valid', 'driver',
            'russia_moscow_valid_personal_no_store', 200,
            'valid', 0,
        ),
        (
            'valid', 'driver',
            'russia_moscow_invalid_personal_store', 200,
            'invalid', 1,
        ),
        (
            'valid', 'driver',
            'russia_moscow_invalid_personal_no_store', 200,
            'invalid', 0,
        ),
    ]
)
def test_precheck_phone(
        flask_client_factory, get_mongo, load_json,
        patch, find_documents_in_update_queue, personal, personal_imitation,
        data_type, vacancy, name, status_code,
        personal_response, store_personal
):
    @patch('infranaim.helper._find_valid_token')
    def _getenv(*args, **kwargs):
        return 'TOKEN'

    @patch('infranaim.helper._is_equal_b64')
    def _token(*args, **kwargs):
        return True

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

    @patch('infranaim.clients.courier_eda.EdaClient._post')
    def _request(_name, _data):
        incoming_phone = _data['phones']
        if incoming_phone == ['79689540576']:
            status = 'notLead'
        else:
            status = 'lead'
        result = {
            'info': [
                {
                    'phone': incoming_phone[0],
                    'status': status
                }
            ]
        }
        return result

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    mongo = get_mongo
    configs = {
        'USE_EXPERIMENTS3': False,
    }
    flask_client = flask_client_factory(mongo, configs=configs)

    filepath = load_json('requests_precheck_phone.json')[data_type][vacancy][name]
    data = filepath['request']
    if name != 'missing_s_code':
        data['s_code'] = 'TOKEN'
    res = flask_client.post('/zendesk/precheck_phone', json=data)
    assert res.status_code == status_code

    docs = find_documents_in_update_queue(mongo)
    if status_code != 200:
        assert not docs
        return

    assert docs
    assert len(docs) == 1
    tickets = docs[0]['upd_data']
    assert len(tickets) == 1

    ticket = tickets[0]['data']
    expected = filepath['expected']

    assert ticket['id'] == expected['id']
    for line in expected['comment']['body'].split('\n\n'):
        assert line in ticket['comment']['body']
    for field in expected['custom_fields']:
        ticket_field = next(
            (
                item
                for item in ticket['custom_fields']
                if item['id'] == field['id']
            ),
            None
        )
        assert ticket_field
        assert field['value'] == ticket_field['value']
        ticket['custom_fields'].remove(ticket_field)
    assert not ticket['custom_fields']


@pytest.mark.parametrize(
    'store_personal, personal_response',
    [
        (1, 'valid'),
        (0, 'valid'),
        (1, 'invalid'),
        (0, 'invalid'),
    ]
)
def test_add_deaf_drivers(
        flask_client_factory, get_mongo, load_json, patch,
        store_personal, personal_response,
        personal, personal_imitation,
):
    @patch('infranaim.helper._find_valid_token')
    def _getenv(*args, **kwargs):
        return 'TOKEN'

    @patch('infranaim.helper._is_equal_b64')
    def _token(*args, **kwargs):
        return True

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

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    mongo = get_mongo
    client = flask_client_factory(mongo)

    request = load_json('requests_add_deaf_drivers.json')
    res = client.post('/zendesk/deaf_drivers_to_add', json=request)
    _check_personal(
        mongo.deaf_drivers_to_add, personal_response, res, store_personal
    )


@pytest.mark.parametrize(
    'store_personal, personal_response',
    [
        (1, 'valid'),
        (0, 'valid'),
        (1, 'invalid'),
        (0, 'invalid'),
    ]
)
def test_add_drivers(
        flask_client_factory, get_mongo, load_json, patch,
        store_personal, personal_response,
        personal, personal_imitation,
):
    @patch('infranaim.helper._find_valid_token')
    def _getenv(*args, **kwargs):
        return 'TOKEN'

    @patch('infranaim.helper._is_equal_b64')
    def _token(*args, **kwargs):
        return True

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

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    mongo = get_mongo
    client = flask_client_factory(mongo)

    request = load_json('requests_add_drivers.json')
    res = client.post('/zendesk/drivers_to_add', json=request)
    _check_personal(
        mongo.drivers_to_add, personal_response, res, store_personal
    )


def _check_personal(collection, personal_response, res, store_personal):
    assert res.status_code == 200
    docs = list(collection.find())
    assert len(docs) == 1
    doc = docs[0]
    if personal_response == 'valid':
        assert_personal_ids_in_data(doc)
    if store_personal:
        assert_personal_in_data(doc)
        if personal_response != 'valid':
            assert_personal_ids_in_data(doc, True)
    else:
        if personal_response == 'valid':
            assert_personal_in_data(doc, True)
        else:
            assert_personal_in_data(doc)


@freezegun.freeze_time('2019-10-04T14:00:00Z')
@pytest.mark.parametrize(
    'data_type, name, status_code, '
    'personal_response, store_personal',
    [
        (
            'valid',
            'russia_moscow_valid_personal_store_active', 200,
            'valid', 1,
        ),
        (
            'valid',
            'russia_moscow_valid_personal_store', 200,
            'valid', 1,
        ),
        (
            'valid',
            'russia_moscow_valid_personal_no_store', 200,
            'valid', 0,
        ),
        (
            'valid',
            'russia_moscow_invalid_personal_store', 200,
            'invalid', 1,
        ),
        (
            'valid',
            'russia_moscow_invalid_personal_no_store', 200,
            'invalid', 0,
        ),
    ]
)
def test_precheck_license(
        flask_client_factory, get_mongo, load_json,
        patch, find_documents_in_update_queue, personal, personal_imitation,
        data_type, name, status_code, personal_response, store_personal
):
    @patch('infranaim.helper._find_valid_token')
    def _getenv(*args, **kwargs):
        return 'TOKEN'

    @patch('infranaim.helper._is_equal_b64')
    def _token(*args, **kwargs):
        return True

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

    @patch('infranaim.clients.courier_eda.EdaClient._post')
    def _request(_name, _data):
        incoming_phone = _data['phones']
        if incoming_phone == ['79689540576']:
            status = 'notLead'
        else:
            status = 'lead'
        result = {
            'info': [
                {
                    'phone': incoming_phone[0],
                    'status': status
                }
            ]
        }
        return result

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    mongo = get_mongo
    configs = {
        'USE_EXPERIMENTS3': False,
    }
    flask_client = flask_client_factory(mongo, configs=configs)

    filepath = load_json('requests_precheck_license.json')[data_type][name]
    data = filepath['request']
    if name != 'missing_s_code':
        data['s_code'] = 'TOKEN'
    res = flask_client.post('/zendesk/precheck_license', json=data)
    assert res.status_code == status_code

    docs = find_documents_in_update_queue(mongo)
    if status_code != 200:
        assert not docs
        return

    assert docs
    assert len(docs) == 1
    tickets = docs[0]['upd_data']
    assert len(tickets) == 1

    ticket = tickets[0]['data']
    expected = filepath['expected']

    assert ticket['id'] == expected['id']
    for line in expected['comment']['body'].split('\n\n'):
        assert line in ticket['comment']['body']
    for field in expected['custom_fields']:
        ticket_field = next(
            (
                item
                for item in ticket['custom_fields']
                if item['id'] == field['id']
            ),
            None
        )
        assert ticket_field
        assert field['value'] == ticket_field['value']
        ticket['custom_fields'].remove(ticket_field)
    assert not ticket['custom_fields']


@pytest.mark.parametrize(
    'case',
    ['valid', 'invalid_name', 'duplicate_phone']
)
def test_add_delivery_courier(
        flask_client_factory, get_mongo, patch, load_json,
        find_documents_in_update_queue, case,
):
    @patch('infranaim.helper._find_valid_token')
    def _getenv(*args, **kwargs):
        return 'TOKEN'

    @patch('infranaim.helper._is_equal_b64')
    def _token(*args, **kwargs):
        return True

    @patch('infranaim.clients.cargo_misc.add_delivery_courier')
    def _cargo_misc(*args, **kwargs):
        status_code = 200
        body = {
            "success": True
        }
        if case == 'duplicate_phone':
            status_code = 400
            body = {
                "code": "duplicate_phone",
                "message": "duplicate_phone"
            }
        result = requests.Response()
        result._content = bytes(json.dumps(body), encoding='utf8')
        result.status_code = status_code
        return result

    mongo = get_mongo
    flask_client = flask_client_factory(mongo)
    request = load_json('requests_add_delivery.json')[case]
    response = flask_client.post(
        '/zendesk/add_delivery_courier',
        json=request,
    )
    assert response.status_code == 200
    updates = find_documents_in_update_queue(mongo)
    if case == 'valid':
        assert not updates
        return
    assert len(updates) == 1
