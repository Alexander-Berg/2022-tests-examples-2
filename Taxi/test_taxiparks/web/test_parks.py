import csv
import typing

import pytest

from infranaim.models.configs import external_config


PERSONAL_ID_FIELDS = {
    "personal_contact_phone_id": 'contact_phone',
    "personal_dispatch_phone_id": 'dispatch_phone',
    "personal_email_ids": 'email',
    "personal_whatsapp_contact_id": 'whatsapp_contact'
}


@pytest.mark.parametrize(
    'show_personal',
    [1, 0],
)
def test_table(
        taxiparks_client_factory, get_mongo, show_personal,
):
    """
    + get park
    + get park history
    """
    mongo = get_mongo
    configs = {
        'TAXIPARKS_PERSONAL_DATA_SHOW': show_personal,
    }
    client = taxiparks_client_factory(mongo, configs=configs)
    user = {
        'login': 'root',
        'password': 'root_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=user)

    res = client.get('/parks_table_dyn')
    assert res.status_code == 200
    parks = res.json['data']
    assert parks
    for park_table in parks:
        park = client.get('/v2/taxiparks/show?_id={}'.format(
            park_table['_id'])).json
        assert park
        park_history = client.get(
            '/v2/taxiparks/history?taxipark_id={}'.format(
                park_table['_id'])).json[0]
        assert park_history

        parks_to_check = [park_table, park, park_history]
        for item in parks_to_check:
            assert 'fleet_type' in item

        for field in PERSONAL_ID_FIELDS.values():
            if show_personal:
                for unit in parks_to_check:
                    assert field in unit
            else:
                for unit in parks_to_check:
                    assert field not in unit


@pytest.mark.parametrize(
    'filters',
    [
        {'city': 'Москва'},
        {'workflow_groups': 'all_drivers'},
        {'city': 'Москва', 'workflow_groups': 'all_drivers'},
        {'city': 'Казань', 'workflow_groups': 'all_drivers'},
    ]
)
@pytest.mark.usefixtures('log_in')
def test_table_filters(taxiparks_client, filters):
    def check_filter(value, expected):
        if isinstance(value, list):
            assert expected in value
        else:
            assert expected == value

    params = {}
    for k, v in filters.items():
        params['filter[{}]'.format(k)] = v

    res = taxiparks_client.get('/parks_table_dyn', query_string=params)
    assert res.status_code == 200

    for park in res.json:
        for k, v in filters.items():
            if k not in park:
                continue
            check_filter(park[k], v)


def _check_location(acquisition):
    fields = ['lat', 'lon']
    for acq in acquisition:
        location = acq['location']
        if location is None:
            return
        for field in fields:
            assert field in location
            assert isinstance(location[field], float)


def _check_parks(
        park: dict,
        park_history: dict,
        request_data: dict,
        store_personal: int,
        personal_response: str,
):
    for key in ['_id', 'taxipark_id', 'action_type']:
        park.pop(key, None)
        park_history.pop(key)
    assert park == park_history
    _check_location(park['acquisition'])
    for doc in [park, park_history]:
        for field, real_field in PERSONAL_ID_FIELDS.items():
            if personal_response == 'valid':
                assert field in doc
                if doc[real_field]:
                    assert doc[field]
            else:
                assert not doc[field]

        if store_personal:
            assert doc['contact_phone'] == request_data['contact_phone']
            assert doc['email'] == request_data['email']
            assert doc['dispatch_phone'] == request_data['dispatch_phone']
            assert doc['whatsapp_contact'] == request_data['whatsapp_contact']
        else:
            for field in PERSONAL_ID_FIELDS.values():
                if personal_response == 'valid':
                    assert not doc[field]
                else:
                    if request_data.get(field):
                        assert doc[field]


def _check_eq_or_ne(
        eq: bool,
        data: dict,
        simple_str: typing.List[str],
        list_of_str: typing.Optional[typing.List[str]] = None,
):
    for field in simple_str:
        if eq:
            assert data[field].strip() == data[field]
        else:
            assert data[field].strip() != data[field]
    if list_of_str:
        for field in list_of_str:
            for item in data[field]:
                if eq:
                    assert item.strip() == item
                else:
                    assert item.strip() != item


def _check_untrimmed(
        data: dict,
        simple_str: typing.List[str],
        list_of_str: typing.Optional[typing.List[str]] = None,
):
    _check_eq_or_ne(False, data, simple_str, list_of_str)


def _check_trimmed(
        data: dict,
        simple_str: typing.List[str],
        list_of_str: typing.Optional[typing.List[str]] = None,
):
    _check_eq_or_ne(True, data, simple_str, list_of_str)


@pytest.mark.parametrize(
    'store_personal, personal_response',
    [
        (1, 'valid'),
        (0, 'valid'),
        (1, 'invalid'),
        (0, 'invalid'),
    ]
)
def test_create_park(
        taxiparks_client_factory, get_mongo, load_json, personal,
        personal_imitation, patch,
        store_personal, personal_response,
):
    # + ensure proper history
    @patch('infranaim.helper.park_exists_in_taximeter')
    def _exists(*args, **kwargs):
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

    client = taxiparks_client_factory(mongo)
    user = {
        'login': 'root',
        'password': 'root_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=user)
    request_data = {
        'csrf_token': client.get('/get_token').json['token']
    }
    request_data.update(load_json('create_park_template.json'))

    untrimmed_fields_str = ['taximeter_name', 'db_uuid']
    untrimmed_fields_list_of_str = ['workflow_groups']
    _check_untrimmed(
        request_data,
        untrimmed_fields_str,
        untrimmed_fields_list_of_str,
    )
    res = client.post('/v2/taxiparks/create', json=request_data)
    assert res.status_code == 200

    query = {'db_uuid': request_data['db_uuid'].strip()}
    park = mongo.taxiparks.find_one(query)
    park_history = mongo.history_taxiparks.find_one(query)
    assert park and park_history

    _check_trimmed(
        park,
        untrimmed_fields_str,
        untrimmed_fields_list_of_str,
    )
    _check_trimmed(
        park_history,
        untrimmed_fields_str,
        untrimmed_fields_list_of_str,
    )
    _check_parks(
        park, park_history, request_data, store_personal, personal_response)


@pytest.mark.parametrize(
    'data, status_code, store_personal, personal_response, pop_item',
    [
        ({}, 200, 1, 'valid', []),
        (
            {
                'rent': 1,
                'contact_phone': '+79989774443',
                'is_paid_acquisition': False,

            }, 200, 1, 'valid', []
        ),
        ({'email': ['good@email.com', 'good2@email.com']}, 200, 1, 'valid', []),
        ({'email': ['good@email.com', 'bad_email.com']}, 400, 1, 'valid', []),
        ({'email': ['good@email.com', '.bad@email.com']}, 400, 1, 'valid', []),
        ({'email': ['плохой@email.com']}, 400, 1, 'valid', []),
        ({'email': ['плохой@email.com']}, 400, 1, 'valid', []),
        ({'email': ['good@email.com', '.bad@email.com']}, 400, 1, 'valid', []),
        ({'email': ['good@email.com', 'bad@email']}, 400, 1, 'valid', []),
        ({'email': ['']}, 400, 1, 'valid', []),
        ({"whatsapp_contact": "+79998887766", "deaf_relation": "only_deaf"},
         200, 1, 'valid', []),
        ({"whatsapp_contact": "abc", "deaf_relation": "only_deaf"},
         400, 1, 'valid', []),
        ({"whatsapp_contact": "abc123", "deaf_relation": "only_deaf"},
         400, 1, 'valid', []),
        ({"whatsapp_contact": "", "deaf_relation": "only_deaf"},
         400, 1, 'valid', []),
        ({"whatsapp_contact": "", "deaf_relation": "only_not_deaf"},
         200, 1, 'valid', []),
        ({"whatsapp_contact": None, "deaf_relation": "only_not_deaf"},
         400, 1, 'valid', []),
        ({}, 200, 1, 'invalid', []),
        ({}, 200, 0, 'valid', []),
        ({}, 200, 0, 'invalid', []),
        ({}, 200, 0, 'valid', ['contact_phone', 'dispatch_phone', 'email']),
    ],
)
def test_edit_park(
        taxiparks_client_factory, get_mongo, load_json, personal,
        personal_imitation, patch, data, status_code, store_personal,
        personal_response, pop_item,
):
    # + ensure proper history

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
    user = {
        'login': 'root',
        'password': 'root_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=user)

    request_data = {
        'csrf_token': client.get('/get_token').json['token']
    }
    request_data.update(load_json('edit_park_template.json'))
    request_data.update(data)

    untrimmed_fields_str = ['responsible_manager', 'city']
    _check_untrimmed(request_data, untrimmed_fields_str)

    for item in pop_item:
        request_data.pop(item, None)
    response = client.post('/v2/taxiparks/update', json=request_data)
    assert response.status_code == status_code
    if status_code != 200:
        return

    park = mongo.taxiparks.find_one(request_data['_id'])
    park_history = mongo.history_taxiparks.find_one(
        {
            'db_uuid': park['db_uuid'],
            'action_type': 'edit'
        }
    )

    _check_trimmed(park, untrimmed_fields_str)
    _check_trimmed(park_history, untrimmed_fields_str)

    assert park['rent'] == bool(request_data['rent'])
    assert park['is_paid_acquisition'] == bool(request_data['is_paid_acquisition'])
    general_park = park['general_info']
    general_request = park['general_info']
    assert (
        general_park['driver_citizenship'] == general_request['driver_citizenship']
    )

    _check_parks(
        park, park_history, request_data, store_personal, personal_response
    )


@pytest.mark.parametrize(
    'show_personal',
    [1, 0]
)
def test_parks_csv(get_mongo, taxiparks_client_factory, show_personal):
    mongo = get_mongo
    configs = {
        'TAXIPARKS_PERSONAL_DATA_SHOW': show_personal,
    }
    client = taxiparks_client_factory(mongo, configs=configs)
    user = {
        'login': 'root',
        'password': 'root_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=user)

    request = {
        'csrf_token': client.get('/get_token').json['token'],
        'filters': {},
        'sort': {},
        'columns': {
            'clid': 'clid',
            'contact_phone': 'contact_phone',
            'dispatch_phone': 'dispatch_phone',
            'email': 'email',
            'whatsapp_contact': 'whatsapp_contact',
        }
    }

    res = client.post('/parks_to_csv', json=request)
    assert res.status_code == 200

    text = [
        line.strip()
        for line in res.data.decode('utf8').split('\n')
    ]
    fieldnames = text.pop(0).split(';')
    reader = csv.DictReader(text, fieldnames, delimiter=';')
    for i, line in enumerate(reader):
        for personal_field, field in PERSONAL_ID_FIELDS.items():
            assert personal_field not in line
            if show_personal:
                assert field in line
            else:
                assert field not in line
    assert i


@pytest.mark.usefixtures('log_user_in')
def test_gambler_handler(taxiparks_client):
    data = taxiparks_client.get('/taxiparks/gambling').json
    assert data
