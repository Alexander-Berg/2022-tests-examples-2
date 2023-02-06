import pytest

ENDPOINT = '/internal-admin/signal-device-configs/v1/patch-history'


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
async def test_ok(taxi_signal_device_configs):
    response = await taxi_signal_device_configs.get(
        ENDPOINT, params={'patch_id': '4'},
    )
    assert response.status_code, response.text
    assert response.json() == {
        'patch_history': [
            {
                'action_id': 'action-1',
                'patch_preset': {
                    'id': 'id-3',
                    'patch_name': 'Озвучка Алисы',
                    'patch': [
                        {
                            'name': 'system.json',
                            'update': {
                                'notify_manager_config': (
                                    '/etc/signalq/notify_manager-alisa.json'
                                ),
                            },
                        },
                    ],
                },
            },
            {
                'action_id': 'action-id33',
                'patch_preset': {
                    'id': 'id-2',
                    'patch_name': 'Выключить фиксацию отвлечения',
                    'patch': [
                        {
                            'name': 'system.json',
                            'update': {'stream_meta': False},
                        },
                        {
                            'name': 'default.json',
                            'update': {'distraction': {'enabled': False}},
                        },
                    ],
                },
            },
            {
                'action_id': 'action-2',
                'patch_preset': {
                    'id': 'id-1',
                    'patch_name': 'Включить стрим мету',
                    'patch': [
                        {
                            'name': 'system.json',
                            'update': {'stream_meta': True},
                        },
                    ],
                },
            },
        ],
    }


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
async def test_ok_no_action_history(taxi_signal_device_configs):
    response = await taxi_signal_device_configs.get(
        ENDPOINT, params={'patch_id': 1},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'patch_history': []}


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
async def test_errors(taxi_signal_device_configs):
    response = await taxi_signal_device_configs.get(
        ENDPOINT, params={'patch_id': 42},
    )
    assert response.status_code == 404, response.text

    assert response.json() == {
        'code': '404',
        'message': 'no patch with patch_id 42',
    }
