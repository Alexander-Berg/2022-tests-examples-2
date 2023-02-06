import pytest


ENDPOINT_URL = '/v2/permissions/list'


def make_request(consumer_id):
    return {'query': {'consumer_id': consumer_id}}


def make_response(permissions):
    return {'permissions': permissions}


OK_HEADERS = {'Accept-Language': 'ru'}
OK_PARAMS = [
    (
        'fleet-api',
        [
            {
                'description': '[fallback] List cars',
                'permission_id': 'fleet-api:v1-parks-cars-list:POST',
            },
            {
                'description': '[fallback] List users',
                'permission_id': 'fleet-api:v1-users-list:POST',
            },
            {
                'description': '[fallback] List park\'s transactions',
                'permission_id': 'fleet-api:v2-parks-transactions-list:POST',
            },
        ],
    ),
    (
        'fleet-api-internal',
        [
            {
                'description': 'List users',
                'permission_id': 'fleet-api:v1-users-list:POST',
            },
        ],
    ),
    ('routeinfo', []),
]


@pytest.mark.parametrize('consumer_id, permissions', OK_PARAMS)
async def test_ok(taxi_uapi_keys, consumer_id, permissions):
    response = await taxi_uapi_keys.post(
        ENDPOINT_URL, headers=OK_HEADERS, json=make_request(consumer_id),
    )
    assert response.status_code == 200, response.text
    assert response.json() == make_response(permissions)


async def test_consumer_not_found(taxi_uapi_keys):
    consumer_id = 'trash'
    response = await taxi_uapi_keys.post(
        ENDPOINT_URL, headers=OK_HEADERS, json=make_request(consumer_id),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'consumer_not_found',
        'message': f'consumer with id `{consumer_id}` was not found',
    }
