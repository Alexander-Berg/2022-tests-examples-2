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
    response = await taxi_uapi_keys.post(
        ENDPOINT_URL,
        headers={
            **auth.DISPATCHER_HEADERS,
            'X-Park-Id': fleet_utils.PARK_ID,
            'X-YaTaxi-Fleet-Permissions': (
                fleet_utils.X_YATAXI_FLEET_PERMISSIONS
            ),
        },
        json={'comment': 'test', 'permission_ids': permission_ids},
    )

    assert response.status == 400
    assert response.json() == {'code': '400', 'message': message}


@pytest.mark.config(
    UAPI_KEYS_FLEET_API_AVAILABLE_PERMISSIONS={
        fleet_utils.PERMISSION_ID_1: [],
        fleet_utils.PERMISSION_ID_2: ['signalq_enabled', 'taxi_enabled'],
    },
    UAPI_KEYS_CONSUMERS=fleet_utils.UAPI_KEYS_CONSUMERS_MOCK,
)
@pytest.mark.parametrize('park_id, permission_ids', fleet_utils.OK_PARAMS)
async def test_ok(taxi_uapi_keys, pgsql, park_id, permission_ids):
    comment = 'test'
    response = await taxi_uapi_keys.post(
        ENDPOINT_URL,
        headers={
            **auth.DISPATCHER_HEADERS,
            'X-Park-Id': park_id,
            'X-YaTaxi-Fleet-Permissions': (
                fleet_utils.X_YATAXI_FLEET_PERMISSIONS
            ),
        },
        json={'comment': comment, 'permission_ids': permission_ids},
    )

    assert response.status == 200

    response_json = response.json()
    assert response_json['park_id'] == park_id
    assert response_json['client_id'] == 'taxi/park/' + park_id

    key_fields = [
        'is_enabled',
        'entity_id',
        'comment',
        'permission_ids',
        'created_at',
        'updated_at',
    ]
    assert (
        utils.check_created_at_after_creation(
            utils.select_keys(pgsql, key_fields),
        )
        == {
            'is_enabled': True,
            'entity_id': park_id,
            'comment': comment,
            'permission_ids': permission_ids,
        }
    )
