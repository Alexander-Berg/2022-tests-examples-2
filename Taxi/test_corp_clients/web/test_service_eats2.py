import datetime

import pytest

from taxi.util import dates as dates_utils

from corp_clients.utils import json_util
from test_corp_clients.web import test_utils

NOW = datetime.datetime.utcnow().replace(microsecond=0)


def iso_localize(data: datetime.datetime) -> str:
    return dates_utils.localize(data).isoformat()


def timedelta_dec(**kwargs) -> datetime.datetime:
    return NOW - datetime.timedelta(**kwargs)


def timedelta_inc(**kwargs) -> datetime.datetime:
    return NOW + datetime.timedelta(**kwargs)


async def test_service_eats2_get_404(web_app_client):
    response = await web_app_client.get(
        '/v1/services/eats2', params={'client_id': 'unknown'},
    )
    response_json = await response.json()

    assert response.status == 404, response_json
    assert response_json == {
        'code': 'NOT_FOUND',
        'details': {'reason': 'Service eats2 for client unknown not found'},
        'message': 'Not found',
    }


@pytest.mark.now(NOW.isoformat())
async def test_service_eats2_get(web_app_client):
    response = await web_app_client.get(
        '/v1/services/eats2', params={'client_id': 'client_id_1'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {'is_active': True, 'is_visible': True}


@pytest.mark.now(NOW.isoformat())
async def test_service_eats2_update(web_app_client, db, corp_billing_mock):
    data = {
        'is_active': False,
        'is_visible': False,
        'is_test': True,
        'deactivate_threshold_ride': 1,
        'deactivate_threshold_date': timedelta_inc(days=1),
    }

    old_client = await db.secondary.corp_clients.find_one(
        {'_id': 'client_id_1'},
    )

    expected_client = old_client
    expected_client['services']['eats2'] = data

    response = await web_app_client.patch(
        '/v1/services/eats2',
        params={'client_id': 'client_id_1'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_1'})

    for key in ['created', 'updated', 'updated_at']:
        expected_client.pop(key, None)
        client.pop(key, None)

    assert client == expected_client


@pytest.mark.translations(**test_utils.TRANSLATIONS)
async def test_service_eats2_default_limit(web_app_client, db, drive_mock):
    data: dict = {'is_active': True, 'is_visible': True}

    response = await web_app_client.patch(
        '/v1/services/eats2',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    eats2_limit = await db.corp_limits.find_one(
        {'client_id': 'client_id_2', 'service': 'eats2'},
        projection={'_id': False, 'created': False, 'updated': False},
    )
    assert eats2_limit == {
        'client_id': 'client_id_2',
        'title': 'Регулярные заказы',
        'name': 'Регулярные заказы',
        'department_id': None,
        'service': 'eats2',
        'is_default': True,
        'limits': {'orders_cost': None, 'orders_amount': None},
    }
