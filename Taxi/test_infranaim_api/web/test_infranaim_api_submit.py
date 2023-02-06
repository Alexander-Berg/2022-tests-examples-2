import json

import freezegun
import pytest

from infranaim.models.configs import external_config

ROUTE_SIMPLE = '/v1/submit/create'
ROUTE_LOW_PRIORITY = '/v1/submit/low_priority'
PHONE_CHECK_REQUESTS = 'requests_precheck_phone.json'
SIMPLE_REQUESTS = 'requests.json'
HEADERS = {
    'Content-Type': 'application/json',
    'token': 'aERiVVNRNTV1RGRYd1BMMmtmbXV0UFc1TjRIb3dHQTdBTjlhZzdQT29G'
}


@pytest.mark.parametrize('store_personal', [1, 0])
@pytest.mark.parametrize('personal_response', ['valid', 'invalid'])
@pytest.mark.parametrize(
    ('doc_name', 'route', 'priority'),
    [
        ('personal_and_values', ROUTE_SIMPLE, 0),
        ('personal_and_values', ROUTE_LOW_PRIORITY, 10),
        ('only_values', ROUTE_SIMPLE, 0),
        ('only_personal', ROUTE_SIMPLE, 0),
        ('invalid', ROUTE_SIMPLE, 0),
    ]
)
def test_infranaim_submit(
        infranaim_client_factory, load_json, get_mongo,
        patch, personal, check_creates_or_updates, check_personal_dict,
        store_personal, personal_response, doc_name, route, priority,
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

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    mongo = get_mongo

    client = infranaim_client_factory(mongo)
    request_data = load_json('requests.json')[doc_name]
    res = client.post(
        route,
        headers=HEADERS,
        json=request_data
    )

    idempotent = list(mongo.idempotent_requests.find())
    if doc_name == 'invalid':
        assert res.status_code == 422
        assert not idempotent
        return
    else:
        assert res.status_code == 200
        assert idempotent

    for doc in idempotent:
        data = doc['request'].replace("'", '"')
        data = json.loads(data)
        check_personal_dict(
            data, store_personal, personal_response, doc_name,
        )

    docs = list(mongo.zendesk_tickets_to_create.find())
    assert docs
    for doc in docs:
        assert doc['priority'] == priority
        ticket = doc['data']
        assert ticket
        custom_fields = {
            item['id']: item
            for item in ticket['custom_fields']
        }
        phone = custom_fields.get(30557445, {})
        pd_phone = custom_fields.get(360005536320, {})
        driver_license = custom_fields.get(30148269, {})
        pd_license = custom_fields.get(360005536340, {})

        if personal_response == 'valid':
            assert pd_phone['value'] and pd_license['value']
            if store_personal:
                assert phone['value'] and driver_license['value']
            else:
                assert not phone and not driver_license
        else:
            assert phone.get('value') or pd_phone.get('value')
            assert driver_license.get('value') or pd_license.get('value')

    double_res = client.post(
        route,
        headers=HEADERS,
        json=request_data
    )
    assert double_res.status_code == 409
    assert mongo.idempotent_requests.count_documents({}) == len(idempotent)
    assert mongo.zendesk_tickets_to_create.count_documents({}) == len(docs)


@freezegun.freeze_time('2019-12-04T14:00:00Z')
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
            'invalid_phone_empty', 422,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'invalid_phone_string', 422,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'invalid_phone_bad_format', 200,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'invalid_phone_unparsable', 400,
            'valid', 1,
        ),
        (
            'invalid', 'driver',
            'missing_phone', 422,
            'valid', 1,
        ),
        (
            'invalid', 'courier',
            'invalid_phone_empty', 422,
            'valid', 1,
        ),
        (
            'invalid', 'courier',
            'invalid_phone_string', 422,
            'valid', 1,
        ),
        (
            'invalid', 'courier',
            'invalid_phone_bad_format', 200,
            'valid', 1,
        ),
        (
            'invalid', 'courier',
            'invalid_phone_unparsable', 400,
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
def test_precheck_phone_on_submit(
        infranaim_client_factory,
        load_json,
        get_mongo,
        patch,
        personal,
        check_creates_or_updates,
        check_personal_dict,
        data_type,
        vacancy,
        name,
        status_code,
        personal_response,
        store_personal,
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
    external_config.HIRING_INFRANAIM_PHONE_CHECK_ON_SUBMIT = True

    mongo = get_mongo
    flask_client = infranaim_client_factory(mongo)
    filepath = load_json(PHONE_CHECK_REQUESTS)[data_type][vacancy][name]
    data = {'params': filepath['request']}
    res = flask_client.post(ROUTE_SIMPLE, json=data, headers=HEADERS)
    assert res.status_code == status_code

    docs = list(mongo.zendesk_tickets_to_create.find())
    if status_code != 200:
        assert not docs
        return

    assert docs
    assert len(docs) == 1
    ticket = docs[0]['data']
    expected = filepath['expected']

    for line in expected['comment']['body'].split('\n\n'):
        assert line in ticket['comment']['body']
    assert 'Водитель с этим номером телефона' not in ticket['comment']['body']
    ticket_custom_fields = {
        item['id']: item
        for item in ticket['custom_fields']
    }
    for field in expected['custom_fields']:
        ticket_field = ticket_custom_fields.get(field['id'])
        assert ticket_field
        assert field['value'] == ticket_field['value']
        del ticket_custom_fields[field['id']]
    assert not ticket_custom_fields
