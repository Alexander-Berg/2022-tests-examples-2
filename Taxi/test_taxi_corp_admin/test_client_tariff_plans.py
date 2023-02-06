import datetime

import pytest
import pytz

NOW = datetime.datetime.utcnow().replace(microsecond=0, tzinfo=pytz.utc)
AVAILABLE_TARIFF_PLANS_TO_CHOOSE = {
    'rus': [
        {
            'name': 'main',
            'combination': [
                {
                    'tariff_plan_series_id': 'tariff_plan_series_id_1',
                    'description_key': 'tariff_plan_series_id_1',
                    'tags': ['fixed'],
                },
                {
                    'tariff_plan_series_id': 'tariff_plan_series_id_3',
                    'description_key': 'tariff_plan_series_id_2',
                    'tags': ['dynamic'],
                },
            ],
        },
    ],
}


def days(_days: int):
    return datetime.timedelta(_days)


@pytest.mark.now(NOW.isoformat())
async def test_get_list(taxi_corp_admin_client):
    response = await taxi_corp_admin_client.get(
        '/v1/client-tariff-plans',
        params={'client_id': 'client_id_1', 'service': 'taxi'},
    )
    from taxi_corp_admin.util import json_util

    assert response.status == 200
    assert await response.json() == {
        'items': [
            {
                'id': 'client_tariff_plan_id_3',
                'client_id': 'client_id_1',
                'service': 'taxi',
                'date_from': json_util.serialize(
                    NOW + datetime.timedelta(days=4),
                ),
                'date_to': None,
                'description': 'Начинает через 4 дня и навсегда',
                'tariff_plan_series_id': 'tariff_plan_series_id_3',
            },
            {
                'id': 'client_tariff_plan_id_2',
                'client_id': 'client_id_1',
                'service': 'taxi',
                'date_from': json_util.serialize(
                    NOW + datetime.timedelta(days=2),
                ),
                'date_to': json_util.serialize(
                    NOW + datetime.timedelta(days=3),
                ),
                'description': 'Начинает послезатра, действует 1 день',
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
            },
            {
                'id': 'client_tariff_plan_id_1',
                'client_id': 'client_id_1',
                'service': 'taxi',
                'date_from': json_util.serialize(
                    NOW - datetime.timedelta(days=1),
                ),
                'date_to': json_util.serialize(
                    NOW + datetime.timedelta(days=1),
                ),
                'description': 'От вчера до завтра',
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
            },
            {
                'id': 'client_tariff_plan_id_0',
                'client_id': 'client_id_1',
                'service': 'taxi',
                'date_from': json_util.serialize(
                    NOW - datetime.timedelta(days=2),
                ),
                'date_to': json_util.serialize(
                    NOW - datetime.timedelta(days=1),
                ),
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
            },
        ],
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE=AVAILABLE_TARIFF_PLANS_TO_CHOOSE,
    CORP_TARIFF_PLAN_CHANGE_COOLDOWN=7,
)
@pytest.mark.now(NOW.isoformat())
async def test_post_client_tariff_plan(
        db, monkeypatch, taxi_corp_admin_client,
):
    monkeypatch.setattr(
        'taxi_corp_admin.schemas.fields.UUID.default',
        'client_tariff_plan_id_new',
    )

    date_from = NOW

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans',
        json={
            'client_id': 'client_id_1',
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
        'is_updated_by_client': True,
        'client_id': 'client_id_1',
        'service': 'taxi',
        'description': 'Updated by client',
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
        'date_from': date_from.replace(tzinfo=None),
        'date_to': None,
        'created': NOW.replace(tzinfo=None),
        'updated': NOW.replace(tzinfo=None),
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE=AVAILABLE_TARIFF_PLANS_TO_CHOOSE,
    CORP_TARIFF_PLAN_CHANGE_COOLDOWN=7,
)
async def test_post_client_tariff_plan_tp_is_not_available(
        db, taxi_corp_admin_client,
):
    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans',
        json={
            'client_id': 'client_id_1',
            'tariff_plan_series_id': 'tariff_plan_series_id_2',
        },
    )
    assert response.status == 400
    assert await response.json() == {
        'status': 'error',
        'code': 'invalid-input',
        'message': (
            'tariff plan \'tariff_plan_series_id_2\''
            ' is not in the list of available tariff plans'
        ),
        'details': {},
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE=AVAILABLE_TARIFF_PLANS_TO_CHOOSE,
    CORP_TARIFF_PLAN_CHANGE_COOLDOWN=7,
)
async def test_post_client_tariff_plan_tp_was_updated_recently(
        db, taxi_corp_admin_client,
):
    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans',
        json={
            'client_id': 'client_id_1',
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
        },
    )

    data = await response.json()
    assert response.status == 200, data
    assert data == {}

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans',
        json={
            'client_id': 'client_id_1',
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
        },
    )

    assert response.status == 400
    assert await response.json() == {
        'status': 'error',
        'code': 'invalid-input',
        'message': 'client updated tariff plan within cooldown timeframe',
        'details': {},
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE={
        'rus': [
            {
                'name': 'main',
                'combination': [
                    {
                        'tariff_plan_series_id': 'tariff_plan_series_id_1',
                        'description_key': 'tariff_plan_series_id_1',
                        'tags': ['fixed'],
                    },
                ],
            },
        ],
    },
    CORP_TARIFF_PLAN_CHANGE_COOLDOWN=7,
)
async def test_post_client_tariff_plan_client_tp_not_in_combination(
        db, taxi_corp_admin_client,
):
    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans',
        json={
            'client_id': 'client_id_1',
            'tariff_plan_series_id': 'tariff_plan_series_id_2',
        },
    )
    assert response.status == 400
    assert await response.json() == {
        'status': 'error',
        'code': 'invalid-input',
        'message': 'this client cannot choose their tariff plan',
        'details': {},
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE={
        'rus': [
            {
                'name': 'main',
                'combination': [
                    {
                        'tariff_plan_series_id': 'tariff_plan_series_id_2',
                        'description_key': 'tariff_plan_series_id_2',
                        'tags': ['fixed'],
                    },
                ],
            },
        ],
    },
    CORP_TARIFF_PLAN_CHANGE_COOLDOWN=7,
)
async def test_post_client_tariff_plan_client_without_feature(
        db, taxi_corp_admin_client,
):
    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans',
        json={
            'client_id': 'client_id_2',
            'tariff_plan_series_id': 'tariff_plan_series_id_2',
        },
    )
    assert response.status == 400
    assert await response.json() == {
        'status': 'error',
        'code': 'invalid-input',
        'message': 'this client cannot choose their tariff plan',
        'details': {},
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
        '/v1/client-tariff-plans/assign',
        json={
            'client_id': 'client_id_2',
            'service': 'taxi',
            'description': 'text',
            'date_from': date_from.isoformat(),
            'date_to': date_to.isoformat(),
            'tariff_plan_series_id': 'tariff_plan_series_id_4',
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
        'client_id': 'client_id_2',
        'service': 'taxi',
        'description': 'text',
        'tariff_plan_series_id': 'tariff_plan_series_id_4',
        'date_from': date_from.replace(tzinfo=None),
        'date_to': date_to.replace(tzinfo=None),
        'created': NOW.replace(tzinfo=None),
        'updated': NOW.replace(tzinfo=None),
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'date_from, date_to, expected',
    [
        (
            None,
            None,
            [
                {
                    '_id': 'client_tariff_plan_id_5',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_6',
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
                    '_id': 'client_tariff_plan_id_5',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_6',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(2),
                    'date_to': NOW + days(7),
                },
                {
                    '_id': 'client_tariff_plan_id_8',
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
                    '_id': 'client_tariff_plan_id_5',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_6',
                    'date_from': NOW - days(1),
                    'date_to': NOW,
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW,
                    'date_to': NOW + days(5),
                },
                {
                    '_id': 'client_tariff_plan_id_7',
                    'date_from': NOW + days(5),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_8',
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
                    '_id': 'client_tariff_plan_id_5',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_6',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(1),
                    'date_to': NOW + days(4),
                },
                {
                    '_id': 'client_tariff_plan_id_7',
                    'date_from': NOW + days(4),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_8',
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
                    '_id': 'client_tariff_plan_id_5',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_6',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(4),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_8',
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
                    '_id': 'client_tariff_plan_id_5',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_6',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(4),
                    'date_to': NOW + days(5),
                },
                {
                    '_id': 'client_tariff_plan_id_7',
                    'date_from': NOW + days(5),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_8',
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
                    '_id': 'client_tariff_plan_id_5',
                    'date_from': NOW - days(2),
                    'date_to': NOW - days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_6',
                    'date_from': NOW - days(1),
                    'date_to': NOW + days(1),
                },
                {
                    '_id': 'client_tariff_plan_id_7',
                    'date_from': NOW + days(4),
                    'date_to': NOW + days(5),
                },
                {
                    '_id': 'client_tariff_plan_id_new',
                    'date_from': NOW + days(5),
                    'date_to': NOW + days(6),
                },
                {
                    '_id': 'client_tariff_plan_id_8',
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
    body = {
        'client_id': 'client_id_2',
        'service': 'taxi',
        'tariff_plan_series_id': 'tariff_plan_series_id_4',
    }
    if date_from:
        body['date_from'] = date_from.isoformat()
    if date_to:
        body['date_to'] = date_to.isoformat()

    response = await taxi_corp_admin_client.post(
        '/v1/client-tariff-plans/assign', json=body,
    )

    data = await response.json()

    assert response.status == 200, data
    assert data == {}

    client_tariff_plans = (
        await db.corp_client_tariff_plans.find(
            {'client_id': 'client_id_2', 'service': 'taxi'},
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
