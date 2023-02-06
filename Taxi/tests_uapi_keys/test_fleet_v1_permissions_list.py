import pytest

from tests_uapi_keys import auth


ENDPOINT_URL = '/fleet/uapi-keys/v1/permissions/list'


def make_response(permissions):
    return {'permissions': permissions}


TRANSLATIONS = {
    'FleetAPI_V1UsersListPOST': {
        'en': 'List users',
        'ru': 'Список пользователей',
    },
    'FleetAPI_V2ParksTransactionsListPOST': {
        'en': 'List park\'s transactions',
        'ru': 'Список транзакций парка',
    },
}


PARAMS_200 = [
    (
        'en',
        [
            {
                'permission_id': 'fleet-api:v1-users-list:POST',
                'description': 'List users',
            },
            {
                'permission_id': 'fleet-api:v2-parks-transactions-list:POST',
                'description': 'List park\'s transactions',
            },
            {
                'permission_id': 'fleet-api:v1-parks-cars-list:POST',
                'description': '[fallback] List cars',
            },
        ],
        ['1_enabled', '2_enabled'],
    ),
    (
        'ru',
        [
            {
                'permission_id': 'fleet-api:v1-users-list:POST',
                'description': 'Список пользователей',
            },
            {
                'permission_id': 'fleet-api:v2-parks-transactions-list:POST',
                'description': 'Список транзакций парка',
            },
            {
                'permission_id': 'fleet-api:v1-parks-cars-list:POST',
                'description': '[fallback] List cars',
            },
        ],
        ['1_enabled', '2_enabled'],
    ),
    (
        'de',
        [
            {
                'permission_id': 'fleet-api:v1-users-list:POST',
                'description': '[fallback] List users',
            },
            {
                'permission_id': 'fleet-api:v2-parks-transactions-list:POST',
                'description': '[fallback] List park\'s transactions',
            },
            {
                'permission_id': 'fleet-api:v1-parks-cars-list:POST',
                'description': '[fallback] List cars',
            },
        ],
        ['1_enabled', '2_enabled'],
    ),
    (
        'en',
        [
            {
                'permission_id': 'fleet-api:v1-users-list:POST',
                'description': 'List users',
            },
            {
                'permission_id': 'fleet-api:v1-parks-cars-list:POST',
                'description': '[fallback] List cars',
            },
        ],
        ['1_enabled'],
    ),
    (
        'ru',
        [
            {
                'permission_id': 'fleet-api:v2-parks-transactions-list:POST',
                'description': 'Список транзакций парка',
            },
            {
                'permission_id': 'fleet-api:v1-parks-cars-list:POST',
                'description': '[fallback] List cars',
            },
        ],
        ['2_enabled'],
    ),
    ('en', [], ['3_enabled']),
    ('ru', [], []),
]


@pytest.mark.parametrize('locale, permissions, tags', PARAMS_200)
@pytest.mark.translations(uapi_keys=TRANSLATIONS)
async def test_200(taxi_uapi_keys, locale, permissions, tags):
    response = await taxi_uapi_keys.get(
        ENDPOINT_URL,
        headers={
            **auth.DISPATCHER_HEADERS,
            'Accept-Language': locale,
            'X-Park-Id': 'park_id',
            'X-YaTaxi-Fleet-Permissions': ','.join(tags),
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == make_response(permissions)


@pytest.mark.config(
    UAPI_KEYS_FLEET_API_AVAILABLE_PERMISSIONS={
        'fleet-api:v1-parks-cars-list:POST': ['1_enabled', '2_enabled'],
    },
    UAPI_KEYS_CONSUMERS={
        'not-fleet-api': {
            'permissions': {
                'fleet-api:v1-parks-cars-list:POST': {
                    'description': '[fallback] List cars',
                },
            },
        },
    },
)
@pytest.mark.translations(uapi_keys=TRANSLATIONS)
async def test_no_fleet_api_in_config(taxi_uapi_keys):
    response = await taxi_uapi_keys.get(
        ENDPOINT_URL,
        headers={
            **auth.DISPATCHER_HEADERS,
            'Accept-Language': 'ru',
            'X-Park-Id': 'park_id',
            'X-YaTaxi-Fleet-Permissions': '1_enabled,2_enabled',
        },
    )
    assert response.status_code == 500, response.text
