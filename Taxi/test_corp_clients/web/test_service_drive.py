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


async def test_service_drive_get_404(web_app_client):
    response = await web_app_client.get(
        '/v1/services/drive', params={'client_id': 'unknown'},
    )
    response_json = await response.json()

    assert response.status == 404, response_json
    assert response_json == {
        'code': 'NOT_FOUND',
        'details': {'reason': 'Service drive for client unknown not found'},
        'message': 'Not found',
    }


@pytest.mark.now(NOW.isoformat())
async def test_service_drive_get(web_app_client):
    response = await web_app_client.get(
        '/v1/services/drive', params={'client_id': 'client_id_1'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {
        'is_active': True,
        'is_visible': True,
        'parent_id': 12345,
    }


@pytest.mark.now(NOW.isoformat())
async def test_service_drive_update(web_app_client, db):
    data = {
        'is_active': False,
        'is_visible': False,
        'is_test': True,
        'deactivate_threshold_ride': 1,
        'deactivate_threshold_date': timedelta_inc(days=1),
        'parent_id': 12345,
    }

    old_client = await db.secondary.corp_clients.find_one(
        {'_id': 'client_id_1'},
    )

    expected_client = old_client
    expected_client['services']['drive'] = data

    response = await web_app_client.patch(
        '/v1/services/drive',
        params={'client_id': 'client_id_1'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_1'})

    for key in ['created', 'updated', 'updated_at']:
        expected_client.pop(key, None)
        client.pop(key, None)

    assert client == expected_client


# activate service drive for client without parent_id
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations(**test_utils.TRANSLATIONS)
async def test_service_drive_new_parent_id(web_app_client, db, drive_mock):
    data: dict = {'is_active': True, 'is_visible': True}

    old_client = await db.secondary.corp_clients.find_one(
        {'_id': 'client_id_2'},
    )

    expected_client = old_client
    expected_client['services']['drive'] = dict(
        data, parent_id=drive_mock.new_account_id,
    )

    response = await web_app_client.patch(
        '/v1/services/drive',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_2'})

    for key in ['created', 'updated', 'updated_at']:
        expected_client.pop(key, None)
        client.pop(key, None)

    assert client == expected_client

    # check drive calls
    assert drive_mock.create_organization.next_call()['request'].json == {
        'account_meta': {
            'comment': 'corp_client_2',
            'company': 'corp_client_2',
        },
        'active_flag': True,
        'default_description': {
            'hard_limit': 100000,
            'meta': {
                'hr_name': 'corp_client_2',
                'is_personal': True,
                'max_links': 1,
                'offers_filter': 'corporate*rus',
                'refresh_policy': 'month',
                'selectable': True,
            },
            'name': 'corp_yataxi_client_id_2_default',
            'soft_limit': 100000,
            'type': 'wallet',
        },
        'name': 'corp_yataxi',
    }
    assert not drive_mock.create_organization.has_calls


@pytest.mark.translations(**test_utils.TRANSLATIONS)
async def test_service_drive_default_limit(web_app_client, db, drive_mock):
    data: dict = {'is_active': True, 'is_visible': True}

    response = await web_app_client.patch(
        '/v1/services/drive',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    drive_limit = await db.corp_limits.find_one(
        {'client_id': 'client_id_2', 'service': 'drive'},
        projection={'_id': False, 'created': False, 'updated': False},
    )
    assert drive_limit == {
        'client_id': 'client_id_2',
        'title': 'Регулярные поездки',
        'name': 'Регулярные поездки',
        'department_id': None,
        'service': 'drive',
        'is_default': True,
        'limits': {
            'orders_cost': {'value': '10000', 'period': 'month'},
            'orders_amount': None,
        },
    }
