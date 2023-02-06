import uuid

import pytest

HEADERS = {
    'Content-Type': 'application/json',
    'X-Idempotency-Token': 'token',
    'X-Yandex-Login': 'jorka',
    'X-Yandex-UID': 'user777',
}

SPACE_MECHANICS = 'space mechanics'
WRONG_SYMBOL_MECHANICS = 'wrong_symbol_!_mechanics'
UPPER_CASE_MECHANICS = 'Uppercase_mechanics'
CORRECT_MECHANICS = 'correct_mechanics'
MECHANICS_SETTINGS = {
    CORRECT_MECHANICS: {
        'reasons': {'22222222-2222-2222-2222-222222222222': ['block_key_1']},
    },
}


async def test_ok(pgsql, taxi_blocklist, add_request):
    add_request['mechanics'] = 'qc_dkvu'
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['data'] == add_request

    cursor = pgsql['blocklist'].cursor()
    cursor.execute('SELECT COUNT(*) FROM blocklist.blocks')
    assert not next(cursor)[0]


async def test_default_mechanics_ok(pgsql, taxi_blocklist, add_request):
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 200
    data = response.json()['data']
    assert data.pop('mechanics') == 'taximeter'
    assert data == add_request


async def test_mechanics_not_supported(taxi_blocklist, add_request):
    add_request['mechanics'] = 'not_allowed'
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'MECHANICS_NOT_FOUND'


@pytest.mark.config(BLOCKLIST_MECHANICS_SETTINGS=MECHANICS_SETTINGS)
async def test_mechanics_format(taxi_blocklist, add_request):
    add_request['mechanics'] = UPPER_CASE_MECHANICS
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'MECHANICS_NOT_FOUND'

    add_request['mechanics'] = WRONG_SYMBOL_MECHANICS
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'MECHANICS_NOT_FOUND'

    add_request['mechanics'] = SPACE_MECHANICS
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'MECHANICS_NOT_FOUND'

    add_request['mechanics'] = CORRECT_MECHANICS
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 200


async def test_predicate_not_found(taxi_blocklist, add_request):
    add_request['predicate_id'] = str(uuid.uuid4())
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'PREDICATE_NOT_FOUND'


async def test_predicate_not_allowed(taxi_blocklist, add_request):
    add_request['predicate_id'] = '44444444-4444-4444-4444-444444444444'
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'PREDICATE_NOT_ALLOWED'


async def test_kwargs_does_not_match(taxi_blocklist, add_request):
    add_request['kwargs'].pop('park_id')
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'KWARGS_DOES_NOT_MATCH_PREDICATE'


async def test_kwargs_are_missing(taxi_blocklist, add_request):
    add_request['kwargs'] = dict(
        park_id=add_request['kwargs']['park_id'],
        license_id=add_request['kwargs']['car_number'],
    )
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 400
    body = response.json()
    assert body['code'] == 'KWARGS_ARE_MISSING'
    assert 'car_number' in body['message']


async def test_reason_is_empty(taxi_blocklist, add_request):
    add_request['reason'] = {}
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'REASON_IS_EMPTY'


async def test_reason_not_allowed(taxi_blocklist, add_request):
    add_request['reason'] = dict(key='not_allowed_reason')
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/add/check', json=add_request, headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'REASON_NOT_ALLOWED'
