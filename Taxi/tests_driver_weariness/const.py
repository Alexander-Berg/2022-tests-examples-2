DEFAULT_UDID_COUNT = 20
DEFAULT_DRIVER_PER_UDID = 2
DEFAULT_UNIQUE_DRIVERS = {
    'licenses_by_unique_drivers': {
        'last_revision': f'{DEFAULT_UDID_COUNT}_1',
        'items': (
            [
                {
                    'id': 'unique1',
                    'is_deleted': False,
                    'revision': '1_1',
                    'data': {
                        'license_ids': [
                            'license_1_1',
                            'license_1_2',
                            'license_1_3',
                        ],
                    },
                },
                {
                    'id': 'unique3',
                    'is_deleted': True,
                    'revision': '3_1',
                    'data': {'license_ids': ['license_3_1', 'license_5_5']},
                },
            ]
            + [
                {
                    'id': f'unique{i}',
                    'is_deleted': False,
                    'revision': f'{i}_1',
                    'data': {
                        'license_ids': [
                            f'license_{i}_{j}'
                            for j in range(0, DEFAULT_DRIVER_PER_UDID)
                        ],
                    },
                }
                for i in range(4, DEFAULT_UDID_COUNT + 1)
            ]
        ),
    },
    'license_by_driver_profile': {
        'last_revision': f'{DEFAULT_UDID_COUNT}_{DEFAULT_DRIVER_PER_UDID}',
        'items': (
            [
                {
                    'id': 'park1_driverSS1',
                    'is_deleted': False,
                    'revision': '1_1',
                    'data': {'license_id': 'license_1_1'},
                },
                {
                    'id': 'park1_driverSS2',
                    'is_deleted': False,
                    'revision': '2_1',
                    'data': {'license_id': 'license_2_1'},
                },
                {
                    'id': 'park2_driverSS3',
                    'is_deleted': False,
                    'revision': '3_1',
                    'data': {'license_id': 'license_5_5'},
                },
            ]
            + [
                {
                    'id': f'dbid_uuid{i}{j}',
                    'is_deleted': False,
                    'revision': f'{i}_{j}',
                    'data': {'license_id': f'license_{i}_{j}'},
                }
                for j in range(0, DEFAULT_DRIVER_PER_UDID)
                for i in range(4, DEFAULT_UDID_COUNT + 1)
            ]
        ),
    },
}

CSH_MARKER = 'csh_extended_events'
