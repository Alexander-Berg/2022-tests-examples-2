import datetime

import pytest

from corp_clients.utils import json_util
from test_corp_clients.web import test_utils

NOW = datetime.datetime.utcnow().replace(microsecond=0)


def timedelta_inc(**kwargs) -> datetime.datetime:
    return NOW + datetime.timedelta(**kwargs)


@pytest.mark.now(NOW.isoformat())
async def test_service_tanker_update(web_app_client, db, corp_billing_mock):
    data = {
        'is_active': False,
        'is_visible': False,
        'is_test': True,
        'deactivate_threshold_ride': 1,
        'deactivate_threshold_date': timedelta_inc(days=1),
        'payment_method': 'card',
    }

    old_client = await db.secondary.corp_clients.find_one(
        {'_id': 'client_id_1'},
    )

    expected_client = old_client
    expected_client['services']['tanker'] = data

    response = await web_app_client.patch(
        '/v1/services/tanker',
        params={'client_id': 'client_id_1'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_1'})

    for key in ['created', 'updated', 'updated_at']:
        expected_client.pop(key, None)
        client.pop(key, None)

    assert client == expected_client


@pytest.mark.config(
    CORP_DEFAULT_LIMITS_SETTINGS={
        'tanker': {'tanker_key': 'limits.default_tanker_name'},
    },
)
@pytest.mark.translations(**test_utils.TRANSLATIONS)
async def test_service_tanker_default_limit(web_app_client, db, drive_mock):
    data: dict = {'is_active': True, 'is_visible': True}

    response = await web_app_client.patch(
        '/v1/services/tanker',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    tanker_limit = await db.corp_limits.find_one(
        {'client_id': 'client_id_2', 'service': 'tanker'},
        projection={'_id': False, 'created': False, 'updated': False},
    )
    assert tanker_limit == {
        'client_id': 'client_id_2',
        'title': 'Регулярные заправки',
        'name': 'Регулярные заправки',
        'department_id': None,
        'service': 'tanker',
        'is_default': True,
        'fuel_types': [],
        'limits': {'orders_cost': None},
    }
