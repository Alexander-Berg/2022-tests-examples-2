ENDPOINT = '/internal-admin/signal-device-configs/v1/patch-presets/list'


async def test_ok(taxi_signal_device_configs):
    response = await taxi_signal_device_configs.post(ENDPOINT)
    assert response.status_code == 200, response.text
    assert response.json() == {
        'patches_list': [
            {
                'id': 'id-1',
                'patch': [
                    {'name': 'system.json', 'update': {'stream_meta': True}},
                ],
                'patch_name': 'Включить стрим мету',
            },
            {
                'id': 'id-2',
                'patch': [
                    {'name': 'system.json', 'update': {'stream_meta': False}},
                    {
                        'name': 'default.json',
                        'update': {'distraction': {'enabled': False}},
                    },
                ],
                'patch_name': 'Выключить фиксацию отвлечения',
            },
            {
                'id': 'id-3',
                'patch': [
                    {
                        'name': 'features.json',
                        'update': {
                            'drowsiness': {
                                'events': {'tired': {'enabled': False}},
                            },
                        },
                    },
                ],
                'patch_name': 'fixation of tired',
            },
            {
                'id': 'id-4',
                'patch': [
                    {
                        'name': 'features.json',
                        'update': {
                            'seatbelt': {
                                'events': {'seatbelt': {'enabled': False}},
                            },
                        },
                    },
                ],
                'patch_name': 'fixation of seatbelt',
            },
            {
                'id': 'id-5',
                'patch': [
                    {
                        'name': 'features.json',
                        'update': {
                            'smoking': {
                                'events': {'smoking': {'enabled': False}},
                            },
                        },
                    },
                ],
                'patch_name': 'fixation of smoking',
            },
            {
                'id': 'id-6',
                'patch': [
                    {
                        'name': 'features.json',
                        'update': {
                            'distraction': {
                                'events': {'distraction': {'enabled': False}},
                            },
                        },
                    },
                ],
                'patch_name': 'fixation of distraction',
            },
            {
                'id': 'id-7',
                'patch': [
                    {
                        'name': 'features.json',
                        'update': {
                            'general': {
                                'events': {
                                    'bad_camera_pose': {'enabled': False},
                                },
                            },
                        },
                    },
                ],
                'patch_name': 'fixation of bad_camera_pose',
            },
            {
                'id': 'id-8',
                'patch': [
                    {
                        'name': 'features.json',
                        'update': {
                            'general': {
                                'events': {'alarm': {'enabled': False}},
                            },
                        },
                    },
                ],
                'patch_name': 'fixation of alarm',
            },
            {
                'id': 'id-9',
                'patch': [
                    {'name': 'features.json', 'update': {'stream_meta': True}},
                ],
                'patch_name': 'Включить стрим мету, только теперь это фьючерс',
            },
        ],
    }
