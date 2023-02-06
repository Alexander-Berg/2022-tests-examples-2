import pytest

from infranaim.models.configs import external_config


ROUTE = '/questionnaire'


@pytest.mark.parametrize(
    'request_name, status_code',
    [
        ('bad_name', 400),
        ('bad_csrf_token', 403),
    ]
)
@pytest.mark.usefixtures('log_in')
def test_questionnaire(flask_client, load_json, csrf_token_session,
                       request_name, status_code):
    request_data = {'csrf_token': csrf_token_session()}
    request_data.update(load_json('post_data.json')[request_name])
    response = flask_client.post(ROUTE, json=request_data)
    assert response.status_code == status_code


def test_no_auth(flask_client, load_json):
    response = flask_client.post(
        ROUTE,
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
        flask_client_factory, load_json, get_mongo, patch,
        find_documents_in_scouts_agents,
        find_documents_in_create_queue,
        personal_check,
        personal,
        find_field,
        personal_response,
        store_personal,
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

    client = flask_client_factory(mongo)
    data = {
        'login': 'scout',
        'password': 'scout_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=data)
    request = load_json('personal_data.json')
    request['csrf_token'] = client.get('/get_token').json['token']
    res = client.post(ROUTE, json=request)
    assert res.status_code == 200

    docs = find_documents_in_scouts_agents(mongo)
    assert len(docs) == 1
    doc = docs[0]
    if personal_response == 'valid':
        assert doc['personal_phone_id'] == personal_check(
            'personal_phone_id')
        assert doc['personal_license_id'] == personal_check(
            'personal_license_id')
        if store_personal:
            assert doc['phone'] == personal_check('phone')
            assert doc['driver_license'] == personal_check(
                'driver_license')
        else:
            assert doc['phone'] == ''
            assert doc['driver_license'] == ''
    else:
        assert not doc.get('personal_phone_id')
        assert not doc.get('personal_license_id')
        assert doc['phone'] == personal_check('phone')
        assert doc['driver_license'] == personal_check('driver_license')

    docs = find_documents_in_create_queue(mongo)
    assert len(docs) == 1

    doc = docs[0]
    custom_fields = doc['data']['custom_fields']
    assert len(custom_fields) > 6
    personal_phone = find_field(custom_fields, 360005536320)
    phone = find_field(custom_fields, 30557445)
    personal_license = find_field(custom_fields, 360005536340)
    driver_license = find_field(custom_fields, 30148269)

    deaf_candidate = find_field(custom_fields, 89)
    city_of_activation = find_field(custom_fields, 90)
    assert deaf_candidate
    assert not city_of_activation

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

    else:
        assert not any([personal_phone, personal_license])
        assert phone['value'] == personal_check('phone')
        assert driver_license['value'] == personal_check('driver_license')

