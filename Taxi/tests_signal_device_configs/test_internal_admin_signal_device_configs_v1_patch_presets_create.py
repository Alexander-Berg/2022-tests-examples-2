ENDPOINT = '/internal-admin/signal-device-configs/v1/patch-presets/create'

PATCH_NAME_1 = 'Выключить фиксацию отвлечения'
PATCH_1 = [
    {'name': 'system.json', 'update': {'stream_meta': False}},
    {'name': 'default.json', 'update': {'distraction': {'enabled': False}}},
]

PATCH_NAME_2 = 'Включить стрим мету'
PATCH_2 = [{'name': 'system.json', 'update': {'stream_meta': True}}]


async def test_ok(taxi_signal_device_configs, pgsql):
    db = pgsql['signal_device_configs'].cursor()
    db.execute(
        """
        DELETE FROM signal_device_configs.patch_presets
        """,
    )
    body = {}
    body['patch_presets'] = [
        {'patch': PATCH_1, 'patch_name': PATCH_NAME_1},
        {'patch': PATCH_2, 'patch_name': PATCH_NAME_2},
    ]
    response = await taxi_signal_device_configs.post(ENDPOINT, json=body)
    assert response.status_code == 200, response.text
    db.execute(
        """
        SELECT patch, patch_name
        FROM signal_device_configs.patch_presets
        ORDER BY patch_name
        """,
    )
    assert list(db) == [(PATCH_2, PATCH_NAME_2), (PATCH_1, PATCH_NAME_1)]


async def test_already_exist(taxi_signal_device_configs, pgsql):
    db = pgsql['signal_device_configs'].cursor()
    db.execute(
        """
        DELETE FROM signal_device_configs.patch_presets
        """,
    )
    body = {}
    body['patch_presets'] = [{'patch': PATCH_1, 'patch_name': PATCH_NAME_1}]
    response = await taxi_signal_device_configs.post(ENDPOINT, json=body)
    assert response.status_code == 200, response.text
    response = await taxi_signal_device_configs.post(ENDPOINT, json=body)
    assert response.status_code == 409
    assert (
        response.json()['message']
        == f'Preset patch with name = \'{PATCH_NAME_1}\' already exists'
    )
