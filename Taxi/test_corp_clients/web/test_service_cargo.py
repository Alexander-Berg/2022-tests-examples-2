import datetime

import pytest

from taxi.util import dates as dates_utils

from corp_clients.utils import json_util

NOW = datetime.datetime.utcnow().replace(microsecond=0)


def iso_localize(data: datetime.datetime) -> str:
    return dates_utils.localize(data).isoformat()


def timedelta_dec(**kwargs) -> datetime.datetime:
    return NOW - datetime.timedelta(**kwargs)


def timedelta_inc(**kwargs) -> datetime.datetime:
    return NOW + datetime.timedelta(**kwargs)


async def test_service_cargo_get_404(web_app_client):
    response = await web_app_client.get(
        '/v1/services/cargo', params={'client_id': 'unknown'},
    )
    response_json = await response.json()

    assert response.status == 404, response_json
    assert response_json == {
        'code': 'NOT_FOUND',
        'details': {'reason': 'Service cargo for client unknown not found'},
        'message': 'Not found',
    }


@pytest.mark.now(NOW.isoformat())
async def test_service_cargo_get(web_app_client):
    response = await web_app_client.get(
        '/v1/services/cargo', params={'client_id': 'client_id_1'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {
        'is_active': True,
        'is_visible': True,
        'next_day_delivery': True,
    }


@pytest.mark.now(NOW.isoformat())
async def test_service_cargo_update(web_app_client, db):
    data = {
        'is_active': False,
        'is_visible': False,
        'is_test': True,
        'deactivate_threshold_ride': 1,
        'deactivate_threshold_date': timedelta_inc(days=1),
        'next_day_delivery': False,
    }

    old_client = await db.secondary.corp_clients.find_one(
        {'_id': 'client_id_1'},
    )

    expected_client = old_client
    expected_client['services']['cargo'] = data

    response = await web_app_client.patch(
        '/v1/services/cargo',
        params={'client_id': 'client_id_1'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_1'})

    for key in ['created', 'updated', 'updated_at']:
        expected_client.pop(key, None)
        client.pop(key, None)

    assert client == expected_client


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_CARGO_DEFAULT_TARIFF_PLANS={
        'rus': {'tariff_plan_series_id': 'tariff_plan_default'},
    },
)
async def test_service_cargo_update_assign_tariff_plans(db, web_app_client):
    data = {'is_active': True}

    response = await web_app_client.patch(
        '/v1/services/cargo',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )
    response_json = await response.json()
    assert response.status == 200, response_json

    client_tariff_plans = (
        await db.secondary.corp_client_tariff_plans.find(
            {'client_id': 'client_id_2'},
        )
        .sort('date_from')
        .to_list(None)
    )

    for client_tariff_plan in client_tariff_plans:
        assert client_tariff_plan.pop('_id')
        assert client_tariff_plan.pop('created')
        assert client_tariff_plan.pop('updated')
        assert client_tariff_plan.pop('client_id') == 'client_id_2'
        assert client_tariff_plan.pop('service') == 'cargo'

    assert client_tariff_plans == [
        {
            'tariff_plan_series_id': 'tariff_plan_default',
            'date_from': NOW,
            'date_to': None,
        },
    ]


@pytest.mark.now(NOW.isoformat())
async def test_service_cargo_update_assign_default_category(
        db, web_app_client,
):
    data = {'is_active': True}

    response = await web_app_client.patch(
        '/v1/services/cargo',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )
    response_json = await response.json()
    assert response.status == 200, response_json

    client_categories = await db.secondary.corp_client_categories.find(
        {'client_id': 'client_id_2'},
    ).to_list(None)

    for client_category in client_categories:
        assert client_category.pop('_id')
        assert client_category.pop('client_id') == 'client_id_2'
        assert client_category.pop('service') == 'cargo'
        updated = client_category.pop('updated', None)
        assert isinstance(updated, datetime.datetime)

    assert client_categories == [
        {'categories': None, 'default_category': None},
    ]
