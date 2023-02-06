import datetime

import pytest


@pytest.mark.parametrize(
    ['client_id', 'service', 'expected_data'],
    [
        pytest.param(
            'client_id_1',
            'taxi',
            {
                'client_id': 'client_id_1',
                'categories': [{'name': 'econom'}, {'name': 'vip'}],
                'default_category': None,
                'service': 'taxi',
            },
        ),
    ],
)
async def test_get(taxi_corp_admin_client, client_id, service, expected_data):
    response = await taxi_corp_admin_client.get(
        '/v1/client-categories',
        params={'client_id': client_id, 'service': service},
    )

    assert response.status == 200
    assert await response.json() == expected_data


@pytest.mark.parametrize(
    ['client_id', 'service'],
    [pytest.param('client_id_2', 'taxi'), pytest.param('client_id_3', 'taxi')],
)
async def test_get_empty(taxi_corp_admin_client, client_id, service):
    response = await taxi_corp_admin_client.get(
        '/v1/client-categories',
        params={'client_id': client_id, 'service': service},
    )

    assert response.status == 200
    assert await response.json() == {
        'client_id': client_id,
        'categories': None,
        'default_category': None,
        'service': service,
    }


@pytest.mark.parametrize(
    ['post_data', 'expected_db'],
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'categories': [{'name': 'vip'}, {'name': 'comfortplus'}],
                'default_category': None,
                'service': 'taxi',
            },
            {
                'client_id': 'client_id_1',
                'categories': [{'name': 'vip'}, {'name': 'comfortplus'}],
                'default_category': None,
                'service': 'taxi',
            },
            id='not null db - set category',
        ),
        pytest.param(
            {
                'client_id': 'client_id_4',
                'categories': [{'name': 'vip'}, {'name': 'comfortplus'}],
                'default_category': None,
                'service': 'taxi',
            },
            {
                'client_id': 'client_id_4',
                'categories': [{'name': 'vip'}, {'name': 'comfortplus'}],
                'default_category': None,
                'service': 'taxi',
            },
            id='set category and drop default_category',
        ),
        pytest.param(
            {
                'client_id': 'client_id_3',
                'categories': [{'name': 'vip'}, {'name': 'comfortplus'}],
                'default_category': None,
                'service': 'taxi',
            },
            {
                'client_id': 'client_id_3',
                'categories': [{'name': 'vip'}, {'name': 'comfortplus'}],
                'default_category': None,
                'service': 'taxi',
            },
            id='null category in db - set category',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'categories': [{'name': 'vip'}, {'name': 'comfortplus'}],
                'default_category': 'vip',
                'service': 'taxi',
            },
            {
                'client_id': 'client_id_1',
                'categories': [{'name': 'vip'}, {'name': 'comfortplus'}],
                'default_category': 'vip',
                'service': 'taxi',
            },
            id='set category and default_category',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'categories': None,
                'default_category': None,
                'service': 'taxi',
            },
            {
                'client_id': 'client_id_1',
                'categories': None,
                'default_category': None,
                'service': 'taxi',
            },
            id='set category and default_category to default',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'categories': None,
                'default_category': 'business',
                'service': 'taxi',
            },
            {
                'client_id': 'client_id_1',
                'categories': None,
                'default_category': 'business',
                'service': 'taxi',
            },
            id='set category and default_category to default',
        ),
    ],
)
@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {
            'econom': 'name.econom',
            'vip': 'name.vip',
            'business': 'name.business',
            'comfortplus': 'name.comfortplus',
        },
    },
)
async def test_change(taxi_corp_admin_client, db, post_data, expected_db):
    response = await taxi_corp_admin_client.post(
        '/v1/client-categories', json=post_data,
    )

    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {}

    client_id = post_data['client_id']
    service = post_data['service']
    db_categories = await db.corp_client_categories.find_one(
        {'client_id': client_id, 'service': service},
    )
    db_categories.pop('_id')

    updated = db_categories.pop('updated', None)
    assert isinstance(updated, datetime.datetime)

    assert db_categories == expected_db


async def test_change_update_to_default(taxi_corp_admin_client, db):
    data = {
        'client_id': 'client_id_1',
        'categories': None,
        'default_category': None,
        'service': 'taxi',
    }

    response = await taxi_corp_admin_client.post(
        '/v1/client-categories', json=data,
    )

    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {}

    db_categories = await db.corp_client_categories.find_one(
        {'client_id': 'client_id_1', 'service': 'taxi'},
    )

    updated = db_categories.pop('updated', None)
    assert isinstance(updated, datetime.datetime)

    assert db_categories == {
        '_id': 'client_categories_1',
        'client_id': 'client_id_1',
        'categories': None,
        'default_category': None,
        'service': 'taxi',
    }


@pytest.mark.parametrize(
    ['post_data', 'expected_db'],
    [
        pytest.param(
            {
                'client_id': 'client_id_2',
                'categories': [{'name': 'econom'}, {'name': 'vip'}],
                'default_category': 'vip',
                'service': 'taxi',
            },
            {
                '_id': 'client_categories_new',
                'client_id': 'client_id_2',
                'categories': [{'name': 'econom'}, {'name': 'vip'}],
                'default_category': 'vip',
                'service': 'taxi',
            },
            id='set category and default_category',
        ),
    ],
)
async def test_change_create(
        taxi_corp_admin_client, db, monkeypatch, post_data, expected_db,
):
    monkeypatch.setattr(
        'taxi_corp_admin.api.common.categories_helper.'
        'create_client_categories_id',
        lambda: 'client_categories_new',
    )

    response = await taxi_corp_admin_client.post(
        '/v1/client-categories', json=post_data,
    )

    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {}

    db_categories = await db.corp_client_categories.find_one(
        {'client_id': 'client_id_2', 'service': 'taxi'},
    )

    updated = db_categories.pop('updated', None)
    assert isinstance(updated, datetime.datetime)

    assert db_categories == expected_db


@pytest.mark.config(CORP_CATEGORIES={'__default__': {'econom': 'name.econom'}})
async def test_change_category_failed(taxi_corp_admin_client):
    data = {
        'client_id': 'client_id_1',
        'service': 'taxi',
        'categories': [
            {'name': 'econom'},
            {'name': 'vip'},
            {'name': 'comfortplus'},
        ],
        'default_category': None,
    }

    response = await taxi_corp_admin_client.post(
        f'/v1/client-categories', json=data,
    )

    response_json = await response.json()

    assert response.status == 400, response_json
    assert response_json == {
        'status': 'error',
        'code': 'invalid-input',
        'message': 'Invalid input',
        'details': {
            'categories.name': [
                'vip is not allowed',
                'comfortplus is not allowed',
            ],
        },
    }


@pytest.mark.parametrize(
    ['post_data', 'expected_response'],
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'service': 'taxi',
                'categories': [{'name': 'econom'}, {'name': 'vip'}],
                'default_category': 'comfortplus',
            },
            {
                'status': 'error',
                'code': 'invalid-input',
                'message': 'Invalid input',
                'details': {
                    'default_category': ['comfortplus is not allowed'],
                },
            },
            id='unknown category',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'categories': None,
                'default_category': 'business',
                'service': 'taxi',
            },
            {
                'status': 'error',
                'code': 'invalid-input',
                'message': 'Invalid input',
                'details': {'default_category': ['business is not allowed']},
            },
            id='unknown category - defaults',
        ),
    ],
)
@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {
            'econom': 'name.econom',
            'vip': 'name.vip',
            'comfortplus': 'name.comfortplus',
        },
    },
)
async def test_change_default_category_failed(
        taxi_corp_admin_client, post_data, expected_response,
):

    response = await taxi_corp_admin_client.post(
        f'/v1/client-categories', json=post_data,
    )

    response_json = await response.json()

    assert response.status == 400, response_json
    assert response_json == expected_response
