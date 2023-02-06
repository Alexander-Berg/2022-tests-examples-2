DEFAULT_UNIQUE_DRIVERS = {
    'licenses_by_unique_drivers': {
        'last_revision': '111112_1',
        'items': [
            {
                'id': 'udid1',
                'is_deleted': False,
                'revision': '111111_1',
                'data': {'license_ids': ['license_1_1']},
            },
            {
                'id': 'uuid2',
                'is_deleted': False,
                'revision': '111112_1',
                'data': {'license_ids': ['license_2_1']},
            },
            {
                'id': 'dummy_uuid',
                'is_deleted': False,
                'revision': '111113_1',
                'data': {'license_ids': ['license_dummy_1']},
            },
        ],
    },
    'license_by_driver_profile': {
        'last_revision': '779_2',
        'items': [
            {
                'id': 'dbid1_uuid1',
                'is_deleted': False,
                'revision': '778_1',
                'data': {'license_id': 'license_1_1'},
            },
            {
                'id': 'dbid1_uuid2',
                'is_deleted': False,
                'revision': '779_2',
                'data': {'license_id': 'license_2_1'},
            },
            {
                'id': 'dbid1_uuid3',
                'is_deleted': False,
                'revision': '779_3',
                'data': {'license_id': 'license_3_1'},
            },
            {
                'id': 'dummy_dbid_uuid',
                'is_deleted': False,
                'revision': '779_4',
                'data': {'license_id': 'license_dummy_1'},
            },
        ],
    },
}
