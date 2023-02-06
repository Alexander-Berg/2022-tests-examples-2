import pytest

from tests_uapi_keys import auth
from tests_uapi_keys import fleet_utils
from tests_uapi_keys import utils

ENDPOINT_URL = '/fleet/uapi-keys/v1/keys'


@pytest.mark.config(
    UAPI_KEYS_FLEET_API_AVAILABLE_PERMISSIONS={
        fleet_utils.PERMISSION_ID_1: ['taxi_enabled', 'signalq_enabled'],
        fleet_utils.PERMISSION_ID_NOT_ALLOWED: ['non_existent_permission'],
    },
    UAPI_KEYS_CONSUMERS=fleet_utils.UAPI_KEYS_CONSUMERS_MOCK,
)
@pytest.mark.parametrize('permission_ids, message', fleet_utils.BAD_PARAMS)
async def test_bad(taxi_uapi_keys, permission_ids, message):
    response = await taxi_uapi_keys.put(
        ENDPOINT_URL,
        headers={
            **auth.DISPATCHER_HEADERS,
            'X-Park-Id': fleet_utils.PARK_ID,
            'X-YaTaxi-Fleet-Permissions': (
                fleet_utils.X_YATAXI_FLEET_PERMISSIONS
            ),
        },
        params={'key_id': fleet_utils.KEY_ID},
        json={
            'is_enabled': True,
            'comment': 'test',
            'permission_ids': permission_ids,
        },
    )

    assert response.status == 400, response.text
    assert response.json() == {'code': '400', 'message': message}


@pytest.mark.parametrize(
    'park_id, key_id',
    (
        (fleet_utils.PARK_ID_NOT_EXISTED, fleet_utils.KEY_ID),
        (fleet_utils.PARK_ID, fleet_utils.BAD_KEY_ID),
        (fleet_utils.PARK_ID, fleet_utils.KEY_ID_NOT_EXISTED),
    ),
)
async def test_key_not_found(taxi_uapi_keys, park_id, key_id):
    response = await taxi_uapi_keys.put(
        ENDPOINT_URL,
        headers={
            **auth.DISPATCHER_HEADERS,
            'X-Park-Id': park_id,
            'X-YaTaxi-Fleet-Permissions': (
                fleet_utils.X_YATAXI_FLEET_PERMISSIONS
            ),
        },
        params={'key_id': key_id},
        json={'is_enabled': True, 'comment': 'test', 'permission_ids': []},
    )

    assert response.status == 404, response.text
    assert response.json() == {'code': '404', 'message': 'key not found'}


@pytest.mark.config(
    UAPI_KEYS_FLEET_API_AVAILABLE_PERMISSIONS={
        fleet_utils.PERMISSION_ID_1: [],
        fleet_utils.PERMISSION_ID_2: ['signalq_enabled', 'taxi_enabled'],
    },
    UAPI_KEYS_CONSUMERS=fleet_utils.UAPI_KEYS_CONSUMERS_MOCK,
)
@pytest.mark.parametrize('is_enabled', [True, False])
async def test_ok(taxi_uapi_keys, pgsql, is_enabled):
    comment = 'test'
    permission_ids = [fleet_utils.PERMISSION_ID_1, fleet_utils.PERMISSION_ID_2]

    response = await taxi_uapi_keys.put(
        ENDPOINT_URL,
        headers={
            **auth.DISPATCHER_HEADERS,
            'X-Park-Id': fleet_utils.PARK_ID,
            'X-YaTaxi-Fleet-Permissions': (
                fleet_utils.X_YATAXI_FLEET_PERMISSIONS
            ),
        },
        params={'key_id': fleet_utils.KEY_ID},
        json={
            'is_enabled': is_enabled,
            'comment': comment,
            'permission_ids': permission_ids,
        },
    )
    assert response.status == 204, response.text

    key_fields = [
        'id',
        'is_enabled',
        'comment',
        'permission_ids',
        'updated_at',
    ]
    assert (
        utils.check_updated_at_after_update(
            utils.select_keys(pgsql, key_fields, fleet_utils.KEY_ID),
        )
        == {
            'id': int(fleet_utils.KEY_ID),
            'is_enabled': is_enabled,
            'comment': comment,
            'permission_ids': permission_ids,
        }
    )
