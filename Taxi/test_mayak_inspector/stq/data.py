import typing as tp


JSON = tp.Dict[str, tp.Any]

SIMPLE_PROFILES: JSON = {
    '123': {
        'driver_license_pd_id': '123',
        'car_id': '123',
        'last_login_at': '2022-05-05T00:00:00+00:00',
    },
}
SIMPLE_ENTITY: JSON = {
    'park_driver_profile_ids': {'123': '123'},
    'driver_profiles': SIMPLE_PROFILES,
}
EMPTY_ENTITY: JSON = {
    'park_driver_profile_ids': dict(),
    'driver_profiles': dict(),
}
MOCK_ENTITY: JSON = {
    'driver_profiles': {
        'park_mock_entity': {
            'driver_license_pd_id': 'pd_id_park_mock_entity',
            'car_id': 'car_id_park_mock_entity',
            'last_login_at': '2022-04-01T00:00:00',
        },
    },
    'park_driver_profile_ids': {'park_mock_entity': 'park'},
    'prefix_tags': [],
}
MOCK_ENTITY_EXP: JSON = {
    **MOCK_ENTITY,
    'prefix_tags': ['experiment::test_experiment'],
}
WRONG_ENTITY = {
    'driver_profiles': {},
    'park_driver_profile_ids': {'park_wrong_udid': 'park'},
    'prefix_tags': [],
}
