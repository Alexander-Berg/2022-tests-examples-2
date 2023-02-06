import time

import freezegun
import pymongo
import pytest


FIELDS_TO_APPEAR = [
    'personal_phone_id', 'personal_license_id', 'deaf_candidate',
    'city_of_activation',
]


def test_get_ticket_non_existent(
        log_in, find_ticket):
    res = find_ticket(123)
    assert res.status_code == 404


def test_get_ticket_insufficient_permissions(
        log_in, find_ticket):
    res = find_ticket(7371442)
    assert res.status_code == 404


@freezegun.freeze_time('2019-9-10T14:00:00')
@pytest.mark.parametrize(
    'show_personal',
    [
        1,
        0
    ]
)
def test_get_ticket_pd_not_hidden(
        flask_client_factory, get_mongo, find_pd_fields,
        show_personal,
):
    mongo = get_mongo
    configs = {
        'PERSONAL_DATA_SHOW': show_personal
    }
    client = flask_client_factory(mongo, configs=configs)
    data = {
        'login': 'scout',
        'password': 'scout_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=data)
    res = client.get('/get_ticket?ticket_id=7371443')
    assert res.status_code == 200
    assert 'personal_phone_id' in res.json
    assert 'personal_license_id' in res.json
    for field in find_pd_fields:
        if show_personal:
            assert '*' not in str(res.json[field])
        else:
            assert field not in res.json


@pytest.mark.parametrize(
    'ids, show_personal',
    [
        ([7371439, 7371440, 7371441], 1),
        ([7371439, 7371440, 7371441], 0),
    ]
)
def test_get_ticket_pd_hidden(
        flask_client_factory, get_mongo, find_pd_fields,
        ids, show_personal,
):
    mongo = get_mongo
    configs = {
        'PERSONAL_DATA_SHOW': show_personal
    }
    client = flask_client_factory(mongo, configs=configs)
    data = {
        'login': 'scout',
        'password': 'scout_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=data)

    for ticket_id in ids:
        ticket = client.get(
            '/get_ticket?ticket_id={}'.format(ticket_id)).json
        assert ticket
        for name in FIELDS_TO_APPEAR:
            assert name in ticket
        for field in find_pd_fields:
            if show_personal:
                assert '*' in str(ticket[field])
            else:
                assert field not in ticket


@pytest.fixture
def generate_tickets(mongodb, load_json):
    template = load_json('ticket_template.json')
    start_id = template['_id']

    def func(tickets_to_insert_count: int):
        operations = []
        for i in range(tickets_to_insert_count):
            new_id = start_id + i
            new_doc = {**template, "_id": new_id, "id": str(new_id)}
            operations.append(pymongo.InsertOne(new_doc))
            if len(operations) == 1000:
                mongodb.tickets.bulk_write(operations, ordered=False)
                operations = []
        total_documents = mongodb.tickets.estimated_document_count()
        assert tickets_to_insert_count < total_documents
    return func


@pytest.mark.parametrize(
    'show_personal',
    [
        0,
        1
    ]
)
def test_tickets_personal(
        flask_client_factory, get_mongo, find_pd_fields,
        show_personal,
):
    mongo = get_mongo
    configs = {
        'PERSONAL_DATA_SHOW': show_personal
    }
    client = flask_client_factory(mongo, configs=configs)
    data = {
        'login': 'scout',
        'password': 'scout_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=data)
    tickets = client.get('/tickets').json['data']
    assert tickets
    for ticket in tickets:
        for name in FIELDS_TO_APPEAR:
            assert name in ticket
        for field in find_pd_fields:
            if show_personal:
                assert field in ticket
            else:
                assert field not in ticket


@pytest.mark.usefixtures('log_in')
def test_plenty_of_tickets(tickets, generate_tickets):
    quantity = 10**5
    max_allowed_time = 0.5
    requests_quantity = 100

    params = {
        "start": 0,
        "count": 30,
        "continue": True,
    }

    generate_tickets(quantity)

    durations = []
    for i in range(requests_quantity):
        start = time.time()
        params['start'] = i*30
        response = tickets(params=params)
        assert response.status_code == 200
        assert len(response.json['data']) == 30
        durations.append(time.time() - start)
    assert min(durations) > 0
    assert max(durations) <= max_allowed_time


@pytest.mark.parametrize(
    'params',
    [
        {},
        {'filter[status_tag]': 'заведен_в_таксометр'},
        {'filter[status_tag]': 'активен_100_зак'},
    ],
)
def test_agent_legal_entity_tickets(
        log_user_role, tickets, params
):
    log_user_role('agent_legal_entity')

    response = tickets(params=params)
    data = response.json['data']
    assert len(data) > 0

    organizations = {d['organization'] for d in data}
    assert len(organizations) == 1 and next(iter(organizations))


@pytest.mark.parametrize(
    'params, role, code, rows_count',
    [
        ({'created_from': '2019-09-01', 'created_to': '2019-10-01'}, 'agent', 200, 1),
        ({'created_from': '2019-09-01', 'created_to': '2019-10-01'}, 'agent_legal_entity', 200, 4),
        ({'created_from': '2019-08-11', 'created_to': '2019-10-01'}, 'agent_legal_entity', 200, 5),
        ({'created_from': '2017-09-08', 'created_to': '2019-10-01'}, 'agent_legal_entity', 400, None),
        ({'created_from': '2019-09-01', 'created_to': '2019-10-01'}, 'scout', 403, None),
    ],
)
def test_download_tickets(
        log_user_role, download, csrf_token_session, load_json,
        params, role, code, rows_count
):
    log_user_role(role)
    req_params = load_json('requests_download.json')['default']
    req_params['filters'].update(params)
    req_params['csrf_token'] = csrf_token_session()

    result = download(params=req_params)
    assert result.status_code == code

    if code != 200:
        return

    text = result.data.decode('utf8')
    nlines = len(text.splitlines())
    assert rows_count == nlines


@pytest.mark.parametrize(
    'role, ticket_id',
    [
        ('agent', 8772905)
    ],
)
def test_ticket_response_integrity(
        log_user_role, find_ticket, load_json,
        role, ticket_id
):
    log_user_role(role)
    ticket = find_ticket(ticket_id).json

    projection = load_json('expected_fields.json')[role]
    for field in projection:
        assert field in ticket
        ticket.pop(field)
    assert not ticket
