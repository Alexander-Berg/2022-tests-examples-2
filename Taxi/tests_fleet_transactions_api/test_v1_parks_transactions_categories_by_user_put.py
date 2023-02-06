# encoding=utf-8
import pytest

from tests_fleet_transactions_api import utils


ENDPOINT_URL = 'v1/parks/transactions/categories/by-user'
PARK_ID = 'park_id_test'


def make_params(park_id, category_id):
    return {'park_id': park_id, 'category_id': category_id}


def make_request(name, is_enabled=True):
    return {'name': name, 'is_enabled': is_enabled}


@pytest.mark.parametrize(
    'category_id, category_index, new_name, is_enabled',
    [
        ('partner_service_manual_1', 1, 'x', True),
        ('partner_service_manual_1', 1, 'Новое имя', False),
        ('partner_service_manual_2', 2, 'y', False),
        ('partner_service_manual_2', 2, 'Новое имя (2)', True),
    ],
)
async def test_ok_and_limit(
        taxi_fleet_transactions_api,
        dispatcher_access_control,
        pgsql,
        category_id,
        category_index,
        new_name,
        is_enabled,
):
    response = await taxi_fleet_transactions_api.put(
        ENDPOINT_URL,
        headers=utils.DISPATCHER_HEADERS,
        params=make_params(PARK_ID, category_id),
        json=make_request(new_name, is_enabled=is_enabled),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'id': category_id,
        'is_enabled': is_enabled,
        'name': new_name,
    }

    db_category = utils.select_park_category(pgsql, PARK_ID, category_index)
    assert db_category.get('is_enabled') == is_enabled
    assert db_category.get('category_name') == new_name


@pytest.mark.parametrize(
    'name, message',
    [
        ('_', 'category name must be non-empty'),
        ('   ', 'category name must be non-empty'),
        # ('\x03', 'category name must be printable utf-8'),
        # Uncomment after fix tier-0 tests
    ],
)
async def test_bad_request(
        taxi_fleet_transactions_api, dispatcher_access_control, name, message,
):
    response = await taxi_fleet_transactions_api.put(
        ENDPOINT_URL,
        headers=utils.DISPATCHER_HEADERS,
        params=make_params(PARK_ID, 'partner_service_manual_1'),
        json=make_request(name),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': message}


@pytest.mark.parametrize(
    'park_id, category_id',
    [
        ('park_not_found', 'partner_service_manual_1'),
        ('park_test', 'partner_service_manual_1_'),
        ('park_test', 'partner_service_manual1'),
        ('park_test', 'partner_service_manual_0'),
        ('park_test', 'partner_service_manual_3'),
        ('park_test', 'partner_service_manual_-124'),
    ],
)
async def test_not_found(
        taxi_fleet_transactions_api,
        dispatcher_access_control,
        park_id,
        category_id,
):
    response = await taxi_fleet_transactions_api.put(
        ENDPOINT_URL,
        headers=utils.DISPATCHER_HEADERS,
        params=make_params(park_id, category_id),
        json=make_request('любое имя'),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': '404',
        'message': f'category id `{category_id}` not found',
    }


@pytest.mark.parametrize(
    'category_id, name',
    [
        ('partner_service_manual_1', 'по расписанию'),
        ('partner_service_manual_2', 'штрафы'),
    ],
)
async def test_already_exists(
        taxi_fleet_transactions_api,
        dispatcher_access_control,
        category_id,
        name,
):
    response = await taxi_fleet_transactions_api.put(
        ENDPOINT_URL,
        headers=utils.DISPATCHER_HEADERS,
        params=make_params(PARK_ID, category_id),
        json=make_request(name),
    )

    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': 'already_exists',
        'message': f'category `{name}` already exists',
    }


async def test_forbidden(taxi_fleet_transactions_api, mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def dispatcher_access_control(request):
        request.get_data()
        return {'users': []}

    response = await taxi_fleet_transactions_api.put(
        ENDPOINT_URL,
        headers=utils.DISPATCHER_HEADERS,
        params=make_params('park_id_forbidden', 'partner_service_manual_1'),
        json=make_request('Запреты'),
    )

    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'dispatcher does not exist or deactivated',
    }
    assert dispatcher_access_control.times_called >= 1
