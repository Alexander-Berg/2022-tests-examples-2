import pytest

from infranaim.models.configs import external_config


PERSONAL_ID_FIELDS = {
    "personal_phone_id": 'phone',
    "personal_license_id": 'driver_license',
}


@pytest.mark.parametrize(
    'show_personal',
    [1, 0]
)
def test_find_ticket(
        taxiparks_client_factory, get_mongo, show_personal,
):
    mongo = get_mongo
    configs = {
        'OKTELL_PERSONAL_DATA_SHOW': show_personal,
    }
    client = taxiparks_client_factory(mongo, configs=configs)
    user = {
        'login': 'root',
        'password': 'root_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=user)

    res = client.get('/oktell/find_ticket?ticket_id=1')
    assert res.status_code == 200
    ticket = res.json
    assert ticket
    for field in PERSONAL_ID_FIELDS.values():
        if show_personal:
            assert field in ticket
        else:
            assert field not in ticket


@pytest.mark.parametrize(
    'personal_response',
    ['valid', 'invalid']
)
@pytest.mark.parametrize(
    'store_personal',
    ['1', '0']
)
@pytest.mark.parametrize(
    'request_type',
    ['new_ticket', 'existing_ticket']
)
@pytest.mark.parametrize(
    'name',
    [
        'driver_simple',
        'driver_selfemployed_has_rides',
        'driver_selfemployed_no_rides',
        'courier_simple',
    ]
)
def test_submit(
        taxiparks_client_factory, load_json, get_mongo,
        patch, find_field,
        personal_check,
        personal,
        personal_response,
        store_personal,
        request_type,
        name
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
    client = taxiparks_client_factory(mongo)
    data = {
        'login': 'root',
        'password': 'root_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=data)
    request = load_json('requests.json')[request_type][name]
    request['csrf_token'] = client.get('/get_token').json['token']
    res = client.post('/oktell/submit', json=request)
    assert res.status_code == 200
    if request_type == 'new_ticket':
        queue = list(mongo.zendesk_tickets_to_create.find())
    else:
        queue = list(mongo.zendesk_tickets_to_update.find())
    if name != 'selfemployed_no_rides':
        assert len(queue) == 1
    else:
        assert len(queue) == 2

    for task in queue:
        if request_type == 'new_ticket':
            ticket = task['data']
        else:
            updates = task['upd_data']
            assert len(updates) == 1
            ticket = updates[0]['data']

        phone = find_field(ticket['custom_fields'], 30557445)
        pd_phone = find_field(ticket['custom_fields'], 360005536320)
        driver_license = find_field(ticket['custom_fields'], 30148269)
        pd_license = find_field(ticket['custom_fields'], 360005536340)

        if not store_personal and personal_response == 'valid':
            assert not phone
            if name != 'courier_simple':
                assert not driver_license
        else:
            assert phone['value']
            if name != 'courier_simple':
                assert driver_license['value']

        if personal_response == 'valid':
            assert pd_phone['value']
            if name != 'courier_simple':
                assert pd_license['value']
        else:
            assert not any([pd_license, pd_phone])

    stat = list(mongo.oktell_statistics.find())
    assert len(stat) == 1
    stat = stat[0]

    if not store_personal and personal_response == 'valid':
        assert 'phone' not in stat
        if name != 'courier_simple':
            assert 'driver_license' not in stat
    else:
        assert 'phone' in stat
        if name != 'courier_simple':
            assert 'driver_license' in stat

    if personal_response == 'valid':
        assert 'personal_phone_id' in stat
        if name != 'courier_simple':
            assert 'personal_license_id' in stat
    else:
        assert 'personal_phone_id' not in stat
        if name != 'courier_simple':
            assert 'personal_license_id' not in stat
