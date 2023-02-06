import datetime

import pytest
import pytz

NOW = datetime.datetime.utcnow().replace(microsecond=0, tzinfo=pytz.utc)


def days(_days: int):
    return datetime.timedelta(_days)


@pytest.mark.now(NOW.isoformat())
async def test_check_create(taxi_corp_admin_client, monkeypatch):
    monkeypatch.setattr('taxi_corp_admin.schemas.fields.UUID.default', 'id1')

    date_from = NOW + days(1)
    date_to = NOW + days(2)

    data = {
        'client_id': 'client_id_1',
        'description': 'text',
        'date_from': date_from.isoformat(),
        'date_to': date_to.isoformat(),
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
    }

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/draft/check', json=data,
    )

    assert response.status == 200
    assert await response.json() == {
        'data': data,
        'change_doc_id': 'corp_client_tariff_plan_client_id_1',
    }


@pytest.mark.now(NOW.isoformat())
async def test_check_update(taxi_corp_admin_client):
    date_from = NOW - days(1)
    date_to = NOW + days(2)

    data = {
        'id': 'client_tariff_plan_id_1',
        'client_id': 'client_id_1',
        'description': 'text',
        'date_from': date_from.isoformat(),
        'date_to': date_to.isoformat(),
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
    }

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/draft/check', json=data,
    )

    assert response.status == 200
    assert await response.json() == {
        'data': data,
        'change_doc_id': 'corp_client_tariff_plan_client_id_1',
    }


@pytest.mark.now(NOW.isoformat())
async def test_apply_create(db, monkeypatch, taxi_corp_admin_client):
    monkeypatch.setattr(
        'taxi_corp_admin.schemas.fields.UUID.default',
        'client_tariff_plan_id_new',
    )

    date_from = NOW + days(1)
    date_to = NOW + days(2)

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/draft/apply',
        json={
            'client_id': 'client_id_1',
            'service': 'taxi',
            'description': 'text',
            'date_from': date_from.isoformat(),
            'date_to': date_to.isoformat(),
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
        },
    )

    data = await response.json()

    assert response.status == 200, data
    assert data == {}

    new_client_plan = await db.corp_client_tariff_plans.find_one(
        {'_id': 'client_tariff_plan_id_new'},
    )

    assert new_client_plan == {
        '_id': 'client_tariff_plan_id_new',
        'client_id': 'client_id_1',
        'service': 'taxi',
        'description': 'text',
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
        'date_from': date_from.replace(tzinfo=None),
        'date_to': date_to.replace(tzinfo=None),
        'created': NOW.replace(tzinfo=None),
        'updated': NOW.replace(tzinfo=None),
    }


@pytest.mark.now(NOW.isoformat())
async def test_apply_update(db, taxi_corp_admin_client):
    date_from = NOW - days(1)
    date_to = NOW + days(2)

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/draft/apply',
        json={
            'id': 'client_tariff_plan_id_1',
            'client_id': 'client_id_1',
            'service': 'cargo',
            'description': 'text',
            'date_from': date_from.isoformat(),
            'date_to': date_to.isoformat(),
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
        },
    )

    data = await response.json()

    assert response.status == 200, data
    assert data == {}

    new_client_plan = await db.corp_client_tariff_plans.find_one(
        {'_id': 'client_tariff_plan_id_1'}, projection={'updated': False},
    )

    assert new_client_plan == {
        '_id': 'client_tariff_plan_id_1',
        'client_id': 'client_id_1',
        'service': 'cargo',
        'description': 'text',
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
        'date_from': date_from.replace(tzinfo=None),
        'date_to': date_to.replace(tzinfo=None),
        'created': (NOW - datetime.timedelta(days=1)).replace(tzinfo=None),
    }


@pytest.mark.now(NOW.isoformat())
async def test_remove_check(taxi_corp_admin_client):
    data = {'id': 'client_tariff_plan_id_2'}

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/remove/draft/check', json=data,
    )

    response_data = await response.json()

    assert response.status == 200, response_data
    assert response_data == {
        'data': {'id': 'client_tariff_plan_id_2'},
        'change_doc_id': 'corp_client_tariff_plan_client_id_1',
    }


@pytest.mark.now(NOW.isoformat())
async def test_remove_apply(db, taxi_corp_admin_client):
    data = {'id': 'client_tariff_plan_id_2'}

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/remove/draft/apply', json=data,
    )

    response_data = await response.json()

    assert response.status == 200, response_data
    assert response_data == {}

    cl_tariff_plans = db.secondary.corp_client_tariff_plans.find(
        {'client_id': 'client_id_1', 'service': 'taxi'}, projection=['_id'],
    )
    ids = sorted([ctp['_id'] async for ctp in cl_tariff_plans])
    assert ids == [
        'client_tariff_plan_id_0',
        'client_tariff_plan_id_1',
        'client_tariff_plan_id_3',
    ]


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'date_from, date_to, expected',
    [
        (
            None,
            None,
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': NOW,
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW,
                    'date_to': None,
                },
            ],
        ),
        (
            NOW + days(2),
            NOW + days(7),
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(2),
                    'date_to': NOW + days(7),
                },
                {
                    '_id': 'client_tariff_plan_id_3',
                    'date_from': NOW + days(8),
                    'date_to': None,
                },
            ],
        ),
        (
            NOW,
            NOW + days(5),
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': NOW,
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW,
                    'date_to': NOW + days(5),
                },
                {
                    '_id': 'client_tariff_plan_id_2',
                    'date_from': NOW + days(5),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_3',
                    'date_from': NOW + days(8),
                    'date_to': None,
                },
            ],
        ),
        (
            NOW + days(1),
            NOW + days(4),
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(1),
                    'date_to': NOW + days(4),
                },
                {
                    '_id': 'client_tariff_plan_id_2',
                    'date_from': NOW + days(4),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_3',
                    'date_from': NOW + days(8),
                    'date_to': None,
                },
            ],
        ),
        (
            NOW + days(4),
            NOW + days(6),
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(4),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_3',
                    'date_from': NOW + days(8),
                    'date_to': None,
                },
            ],
        ),
        (
            NOW + days(4),
            NOW + days(5),
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(4),
                    'date_to': NOW + days(5),
                },
                {
                    '_id': 'client_tariff_plan_id_2',
                    'date_from': NOW + days(5),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_3',
                    'date_from': NOW + days(8),
                    'date_to': None,
                },
            ],
        ),
        (
            NOW + days(5),
            NOW + days(6),
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_2',
                    'date_from': NOW + days(4),
                    'date_to': NOW + days(5),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(5),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_3',
                    'date_from': NOW + days(8),
                    'date_to': None,
                },
            ],
        ),
    ],
)
async def test_move_plans_on_create(
        db, taxi_corp_admin_client, monkeypatch, date_from, date_to, expected,
):
    monkeypatch.setattr(
        'taxi_corp_admin.schemas.fields.UUID.default',
        'client_tariff_plan_id_new',
    )

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/draft/apply',
        json={
            'client_id': 'client_id_1',
            'service': 'taxi',
            'date_from': date_from.isoformat() if date_from else None,
            'date_to': date_to.isoformat() if date_to else None,
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
        },
    )

    data = await response.json()

    assert response.status == 200, data
    assert data == {}

    client_tariff_plans = (
        await db.corp_client_tariff_plans.find(
            {'client_id': 'client_id_1', 'service': 'taxi'},
            projection=['date_from', 'date_from', 'date_to'],
        )
        .sort([('date_from', 1)])
        .to_list(None)
    )

    for ctp in expected:
        if ctp['date_from']:
            ctp['date_from'] = ctp['date_from'].replace(tzinfo=None)
        if ctp['date_to']:
            ctp['date_to'] = ctp['date_to'].replace(tzinfo=None)

    assert client_tariff_plans == expected


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '_id, date_from, date_to, expected',
    [
        (
            'client_tariff_plan_id_1',
            NOW - days(1),
            None,
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': None,
                },
            ],
        ),
        (
            'client_tariff_plan_id_2',
            None,
            None,
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': NOW,
                },
                {
                    '_id': 'client_tariff_plan_id_2',
                    'date_from': NOW,
                    'date_to': None,
                },
            ],
        ),
        (
            'client_tariff_plan_id_2',
            NOW + days(1),
            NOW + days(8),
            [
                {
                    '_id': 'client_tariff_plan_id_0',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_1',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_2',
                    'date_from': NOW + days(1),
                    'date_to': NOW + days(8),
                },
                {
                    '_id': 'client_tariff_plan_id_3',
                    'date_from': NOW + days(8),
                    'date_to': None,
                },
            ],
        ),
    ],
)
async def test_move_plans_on_update(
        db,
        taxi_corp_admin_client,
        monkeypatch,
        _id,
        date_from,
        date_to,
        expected,
):
    monkeypatch.setattr(
        'taxi_corp_admin.schemas.fields.UUID.default',
        'client_tariff_plan_id_new',
    )

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/draft/apply',
        json={
            'id': _id,
            'client_id': 'client_id_1',
            'service': 'taxi',
            'date_from': date_from.isoformat() if date_from else None,
            'date_to': date_to.isoformat() if date_to else None,
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
        },
    )

    data = await response.json()

    assert response.status == 200, data
    assert data == {}

    client_tariff_plans = (
        await db.corp_client_tariff_plans.find(
            {'client_id': 'client_id_1', 'service': 'taxi'},
            projection=['date_from', 'date_from', 'date_to'],
        )
        .sort([('date_from', 1)])
        .to_list(None)
    )

    for ctp in expected:
        if ctp['date_from']:
            ctp['date_from'] = ctp['date_from'].replace(tzinfo=None)
        if ctp['date_to']:
            ctp['date_to'] = ctp['date_to'].replace(tzinfo=None)

    assert client_tariff_plans == expected


@pytest.mark.now(NOW.isoformat())
async def test_bulk_check_create(db, taxi_corp_admin_client):
    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/bulk/draft/check',
        json={
            'tariff_plan_series_id': 'series_1',
            'service': 'taxi',
            'since': '2021-10-04T10:50:37+00:00',
            'idempotency_token': 'token_1',
            'client_ids': ['client_2'],
        },
    )

    assert response.status == 200
    assert await response.json() == {
        'change_doc_id': 'bulk_corp_tariff_plan_series_1',
        'data': {
            'tariff_plan_series_id': 'series_1',
            'service': 'taxi',
            'since': '2021-10-04T10:50:37+00:00',
            'idempotency_token': 'token_1',
            'client_ids': ['client_2'],
        },
    }
    client_tariff_plans_count = await db.corp_client_tariff_plans.count(
        {'client_id': 'client_id_2'},
    )
    assert client_tariff_plans_count == 0


@pytest.mark.now(NOW.isoformat())
async def test_bulk_apply_create_success(db, taxi_corp_admin_client, patch):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    data = {
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
        'service': 'taxi',
        'since': '2021-10-04T10:50:37+00:00',
        'idempotency_token': 'token_1',
        'client_ids': ['client_id_2'],
    }

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/bulk/draft/apply', json=data,
    )

    assert response.status == 200
    assert await response.json() == {'status': 'applying'}

    long_task = await db.corp_long_tasks.find_one(
        {'idempotency_token': 'token_1'}, projection={'_id': False},
    )

    assert long_task == {
        'idempotency_token': 'token_1',
        'task_name': 'corp_bulk_assign_tariff_plan',
        'task_args': {},
        'status': 'running',
        'exec_tries': 0,
        'created_at': NOW.replace(tzinfo=None),
    }


@pytest.mark.now(NOW.isoformat())
async def test_bulk_apply_create_fail(db, taxi_corp_admin_client, patch):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    data = {
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
        'service': 'taxi',
        'since': '2021-10-04T10:50:37+00:00',
        'idempotency_token': 'token_2',
        'client_ids': ['client_id_2'],
    }

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/bulk/draft/apply', json=data,
    )
    assert response.status == 400
    assert await response.json() == {
        'status': 'error',
        'code': 'invalid-input',
        'message': 'Invalid input',
        'details': {'validation_error': ['non existent client_tariff_plan']},
    }
