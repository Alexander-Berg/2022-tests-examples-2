PARK_ID = '7ad36bc7560449998acbe2c57a75c293'
PARK_ID_NOT_EXISTED = '7ad36bc7560449998acbe2c57a75c294'

KEY_ID = '1'
BAD_KEY_ID = '2'
KEY_ID_NOT_EXISTED = '3'

PERMISSION_ID_1 = 'fleet-api:v1-parks-cars-list:POST'
PERMISSION_ID_2 = 'fleet-api:v1-signalq-list:POST'
PERMISSION_ID_3 = 'fleet-api:v1-parks-driver-profiles-list:POST'
PERMISSION_ID_NOT_ALLOWED = 'fleet-api:v1-users-list:POST'

X_YATAXI_FLEET_PERMISSIONS = 'some_permission,taxi_enabled'

BAD_PARAMS = [
    (
        [PERMISSION_ID_NOT_ALLOWED],
        f'permission with id `{PERMISSION_ID_NOT_ALLOWED}` does not exist',
    ),
    (
        [PERMISSION_ID_1, PERMISSION_ID_1],
        f'permission with id `{PERMISSION_ID_1}` is duplicated',
    ),
    (
        [PERMISSION_ID_3],
        f'permission with id `{PERMISSION_ID_3}` does not exist',
    ),
]

OK_PARAMS = [
    (PARK_ID_NOT_EXISTED, [PERMISSION_ID_1]),
    (PARK_ID, [PERMISSION_ID_1, PERMISSION_ID_2]),
]

UAPI_KEYS_CONSUMERS_MOCK = {
    'fleet-api': {
        'permissions': {
            PERMISSION_ID_1: {'description': 'API7 parks cars list'},
            PERMISSION_ID_2: {'description': 'API7 signalq events list'},
            PERMISSION_ID_NOT_ALLOWED: {'description': 'API7 users list'},
        },
    },
}
