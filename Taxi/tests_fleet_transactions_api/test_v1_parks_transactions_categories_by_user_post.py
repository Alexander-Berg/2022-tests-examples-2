# encoding=utf-8
import pytest

from tests_fleet_transactions_api import utils


ENDPOINT_URL = 'v1/parks/transactions/categories/by-user'


def make_headers(idempotency_token):
    return {
        **utils.DISPATCHER_HEADERS,
        'X-Idempotency-Token': idempotency_token,
    }


def make_params(park_id):
    return {'park_id': park_id}


def make_request(name):
    return {'name': name}


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_PARK_CATEGORIES_LIMIT={
        '__default__': 3,
        'park_id_big': 5,
        'park_id_small': 1,
        'park_id_disabled': 0,
    },
)
@pytest.mark.parametrize(
    'park_id, limit, name',
    [
        ('park_id_any', 3, 'Название на Русском'),
        ('park_id_big', 5, 'English name'),
        ('park_id_small', 1, '---'),
        ('park_id_disabled', 0, 'UnknOwn'),
    ],
)
async def test_ok_and_limit(
        taxi_fleet_transactions_api,
        dispatcher_access_control,
        pgsql,
        park_id,
        limit,
        name,
):
    for i in range(1, limit + 1):
        category_name = name + f' {i}'
        idempotency_token = f'a1b2c3d4e5f6g7h8_{i}'

        response = await taxi_fleet_transactions_api.post(
            ENDPOINT_URL,
            headers=make_headers(idempotency_token),
            params=make_params(park_id),
            json=make_request(category_name),
        )

        assert response.status_code == 200, response.text
        assert response.json() == {
            'id': f'partner_service_manual_{i}',
            'is_enabled': True,
            'name': category_name,
        }

        db_category = utils.select_park_category(pgsql, park_id, i)
        assert db_category == {
            'category_name': category_name,
            'idempotency_token': idempotency_token,
            'is_enabled': True,
        }

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL,
        headers=make_headers('a1b2c3d4e5f6g7h8'),
        params=make_params(park_id),
        json=make_request(name),
    )

    assert response.status_code == 409, response.text
    if limit == 0:
        assert response.json() == {
            'code': 'restricted',
            'message': 'park transaction categories is restricted',
        }
    else:
        assert response.json() == {
            'code': 'limit_exceeded',
            'message': f'exceeded limit of {limit} categories',
        }


@pytest.mark.parametrize(
    'name, idempotency_token, db_index, db_is_enabled, db_name',
    [
        ('Штрафы', 'abcd1234cdef5678', 1, True, 'Штрафы'),
        ('   штрафы', 'abcd1234cdef5678', 1, True, 'Штрафы'),
        ('штрафы   ', 'abcd1234cdef5678', 1, True, 'Штрафы'),
        ('  ШТРАФЫ ', 'abcd1234cdef5678', 1, True, 'Штрафы'),
        ('штрАфы___', 'abcd1234cdef5678', 1, True, 'Штрафы'),
        ('по Расписанию', 'zyx9876543210cba', 2, False, 'по Расписанию'),
        ('_ По _ распиСАнию  ', 'zyx9876543210cba', 2, False, 'по Расписанию'),
    ],
)
async def test_idempotency(
        taxi_fleet_transactions_api,
        dispatcher_access_control,
        name,
        idempotency_token,
        db_index,
        db_is_enabled,
        db_name,
):
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL,
        headers=make_headers(idempotency_token),
        params=make_params('park_id_test'),
        json=make_request(name),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'id': f'partner_service_manual_{db_index}',
        'is_enabled': db_is_enabled,
        'name': db_name,
    }


@pytest.mark.parametrize(
    'idempotency_token', ['abcd1234cdef5678', 'zyx9876543210cba'],
)
async def test_idempotency_error(
        taxi_fleet_transactions_api,
        dispatcher_access_control,
        idempotency_token,
):
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL,
        headers=make_headers(idempotency_token),
        params=make_params('park_id_test'),
        json=make_request('Others'),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'idempotency token duplicate',
    }


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
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL,
        headers=make_headers('aaa' * 12),
        params=make_params('park_id_test'),
        json=make_request(name),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': message}


@pytest.mark.parametrize(
    'name, normalized_name',
    [
        ('Штрафы', 'Штрафы'),
        ('   штрафы', 'штрафы'),
        ('штрафы   ', 'штрафы'),
        ('  ШТРАФЫ ', 'ШТРАФЫ'),
        ('штрАфы___', 'штрАфы'),
        ('по Расписанию', 'по Расписанию'),
        ('_ По _ _ распиСАнию  ', 'По распиСАнию'),
    ],
)
async def test_already_exists(
        taxi_fleet_transactions_api,
        dispatcher_access_control,
        name,
        normalized_name,
):
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL,
        headers=make_headers('xyzw' * 4),
        params=make_params('park_id_test'),
        json=make_request(name),
    )

    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': 'already_exists',
        'message': f'category `{normalized_name}` already exists',
    }


async def test_forbidden(taxi_fleet_transactions_api, mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def dispatcher_access_control(request):
        request.get_data()
        return {'users': []}

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL,
        headers=make_headers('f' * 16),
        params=make_params('park_id_forbidden'),
        json=make_request('Запреты'),
    )

    assert dispatcher_access_control.times_called >= 1
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'dispatcher does not exist or deactivated',
    }
