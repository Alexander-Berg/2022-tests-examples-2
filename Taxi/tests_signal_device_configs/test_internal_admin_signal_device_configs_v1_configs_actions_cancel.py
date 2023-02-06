import pytest

from tests_signal_device_configs import utils
from tests_signal_device_configs import web_common

ENDPOINT = '/internal-admin/signal-device-configs/v1/configs/actions/cancel'

PATCH_1 = {'distraction': True}  # 0598a7e7-dd77-4fa2-813a-1e13ab3afda7
PATCH_2 = {
    'stream_meta': {'enabled': False},
}  # 51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7 p1
PATCH_3 = {
    'mqtt': {'enabled': False, 'timeout': 0.5},
    'fallback': 'NULL',
}  # 1bf10f86-1913-48b9-b4ab-ee35ccdde491 serial1
PATCH_4 = {
    'some_old_event': {'enabled': False},
}  # 6fe8bba9-3e72-41e2-adf4-59e382a5a967 0.0.0-1


async def check_db(db, select_cond, patch_expected, action_history_expected):
    db.execute(
        f"""
        SELECT patch_id from signal_device_configs.device_patches
        {select_cond}
        """,
    )
    patch_id = list(db)[0][0]
    db.execute(
        f"""
        SELECT patch, action_history FROM signal_device_configs.patches
        WHERE id = {patch_id}
        """,
    )
    db_result = list(db)
    patch = db_result[0][0]
    action_history = db_result[0][1]
    assert patch == patch_expected
    assert action_history == action_history_expected


@pytest.mark.parametrize(
    'action_id, serial_numbers, expected_code, expected_message',
    [
        ('not_exist', None, 404, 'No action with id : not_exist'),
        (
            '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
            ['not_exist'],
            400,
            'No serial_number not_exist in action with id : 0598a7e7-dd77-4fa2-813a-1e13ab3afda7',  # noqa E501
        ),
    ],
)
@pytest.mark.pgsql('signal_device_configs', files=['test_data.sql'])
async def test_errors(
        taxi_signal_device_configs,
        action_id,
        serial_numbers,
        expected_code,
        expected_message,
):
    body = {}
    body['action_id'] = action_id
    if serial_numbers is not None:
        body['serial_numbers'] = serial_numbers

    response = await taxi_signal_device_configs.post(
        ENDPOINT, json=body, headers={**web_common.YA_TEAM_HEADERS},
    )
    assert response.status_code == expected_code
    assert response.json()['message'] == expected_message


@pytest.mark.parametrize(
    'action_id, serial_numbers, device_patch_ids, '
    'device_patch_id_to_new_patch, device_patch_id_to_new_action_history',
    [
        (
            '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
            ['serial1'],
            [1, 3, 5, 7, 8],
            {
                1: PATCH_1,
                3: PATCH_1,
                5: utils.deep_merge_dicts(PATCH_1, PATCH_2),
                7: utils.deep_merge_dicts(PATCH_1, PATCH_4),
                8: utils.deep_merge_dicts(
                    utils.deep_merge_dicts(PATCH_1, PATCH_2), PATCH_4,
                ),
            },
            {
                1: ['0598a7e7-dd77-4fa2-813a-1e13ab3afda7'],
                3: ['0598a7e7-dd77-4fa2-813a-1e13ab3afda7'],
                5: [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                ],
                7: [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '6fe8bba9-3e72-41e2-adf4-59e382a5a967',
                ],
                8: [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                    '6fe8bba9-3e72-41e2-adf4-59e382a5a967',
                ],
            },
        ),
        (
            '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
            None,
            [1, 2, 3, 4, 5, 6, 7, 8],
            {
                1: {},
                2: PATCH_2,
                3: PATCH_3,
                4: PATCH_4,
                5: utils.deep_merge_dicts(PATCH_2, PATCH_3),
                6: utils.deep_merge_dicts(PATCH_2, PATCH_4),
                7: utils.deep_merge_dicts(PATCH_3, PATCH_4),
                8: utils.deep_merge_dicts(
                    utils.deep_merge_dicts(PATCH_2, PATCH_3), PATCH_4,
                ),
            },
            {
                1: [],
                2: ['51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7'],
                3: ['1bf10f86-1913-48b9-b4ab-ee35ccdde491'],
                4: ['6fe8bba9-3e72-41e2-adf4-59e382a5a967'],
                5: [
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                    '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
                ],
                6: [
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                    '6fe8bba9-3e72-41e2-adf4-59e382a5a967',
                ],
                7: [
                    '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
                    '6fe8bba9-3e72-41e2-adf4-59e382a5a967',
                ],
                8: [
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                    '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
                    '6fe8bba9-3e72-41e2-adf4-59e382a5a967',
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('signal_device_configs', files=['test_data.sql'])
async def test_ok(
        taxi_signal_device_configs,
        action_id,
        serial_numbers,
        device_patch_ids,
        device_patch_id_to_new_patch,
        device_patch_id_to_new_action_history,
        pgsql,
):
    body = {}
    body['action_id'] = action_id
    if serial_numbers is not None:
        body['serial_numbers'] = serial_numbers

    await taxi_signal_device_configs.post(
        ENDPOINT, json=body, headers={**web_common.YA_TEAM_HEADERS},
    )
    db = pgsql['signal_device_configs'].cursor()
    for device_patch_id in device_patch_ids:
        await check_db(
            db,
            f'WHERE id = {device_patch_id}',
            device_patch_id_to_new_patch[device_patch_id],
            device_patch_id_to_new_action_history[device_patch_id],
        )


PRESET_PATCH_1 = {'preset_number': 1, 'pervoe_pole': True}
PRESET_PATCH_2 = {'preset_number': 228, 'vtoroe_pole': True}
PRESET_PATCH_3 = {'preset_number': 322, 'third_pole': True}
APPLY_ENDPOINT = '/internal-admin/signal-device-configs/v1/patch-presets/apply'


@pytest.mark.parametrize(
    'action_id, serial_numbers, device_serial_number_to_new_patch, '
    'device_serial_number_to_new_action_history',
    [
        (
            '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
            ['serial2', 'serial3'],
            {
                'serial1': utils.deep_merge_dicts(
                    utils.deep_merge_dicts(PRESET_PATCH_1, PRESET_PATCH_2),
                    PRESET_PATCH_3,
                ),
                'serial2': PRESET_PATCH_2,
                'serial3': PRESET_PATCH_3,
            },
            {
                'serial1': [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                    '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
                ],
                'serial2': ['51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7'],
                'serial3': ['1bf10f86-1913-48b9-b4ab-ee35ccdde491'],
            },
        ),
        (
            '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
            ['serial1'],
            {
                'serial1': utils.deep_merge_dicts(
                    PRESET_PATCH_1, PRESET_PATCH_3,
                ),
                'serial2': utils.deep_merge_dicts(
                    PRESET_PATCH_1, PRESET_PATCH_2,
                ),
                'serial3': utils.deep_merge_dicts(
                    PRESET_PATCH_1, PRESET_PATCH_3,
                ),
            },
            {
                'serial1': [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
                ],
                'serial2': [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                ],
                'serial3': [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
                ],
            },
        ),
        (
            '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
            ['serial1', 'serial3'],
            {
                'serial1': utils.deep_merge_dicts(
                    PRESET_PATCH_1, PRESET_PATCH_2,
                ),
                'serial2': utils.deep_merge_dicts(
                    PRESET_PATCH_1, PRESET_PATCH_2,
                ),
                'serial3': PRESET_PATCH_1,
            },
            {
                'serial1': [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                ],
                'serial2': [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                ],
                'serial3': ['0598a7e7-dd77-4fa2-813a-1e13ab3afda7'],
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'signal_device_configs', files=['test_data_sub_serial_numbers.sql'],
)
async def test_ok_sub_serial_numbers(
        taxi_signal_device_configs,
        action_id,
        serial_numbers,
        device_serial_number_to_new_patch,
        device_serial_number_to_new_action_history,
        pgsql,
):
    body = {}
    body['preset_patch_id'] = 'id-1'
    body['preset_filter'] = {}
    body['preset_filter']['serial_numbers'] = ['serial1', 'serial2', 'serial3']
    await taxi_signal_device_configs.post(
        APPLY_ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': '0598a7e7-dd77-4fa2-813a-1e13ab3afda7'},
    )
    body['preset_patch_id'] = 'id-2'
    body['preset_filter']['serial_numbers'] = ['serial1', 'serial2']
    await taxi_signal_device_configs.post(
        APPLY_ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7'},
    )
    body['preset_patch_id'] = 'id-3'
    body['preset_filter']['serial_numbers'] = ['serial1', 'serial3']
    await taxi_signal_device_configs.post(
        APPLY_ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': '1bf10f86-1913-48b9-b4ab-ee35ccdde491'},
    )

    device_serial_number_to_patch = {
        'serial1': utils.deep_merge_dicts(
            utils.deep_merge_dicts(PRESET_PATCH_1, PRESET_PATCH_2),
            PRESET_PATCH_3,
        ),
        'serial2': utils.deep_merge_dicts(PRESET_PATCH_1, PRESET_PATCH_2),
        'serial3': utils.deep_merge_dicts(PRESET_PATCH_1, PRESET_PATCH_3),
    }
    device_serial_number_to_action_history = {  # pylint: disable=C0103
        'serial1': [
            '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
            '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
            '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
        ],
        'serial2': [
            '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
            '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
        ],
        'serial3': [
            '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
            '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
        ],
    }

    db = pgsql['signal_device_configs'].cursor()
    for serial_number in ['serial1', 'serial2', 'serial3']:
        await check_db(
            db,
            f'WHERE serial_number = \'{serial_number}\'',
            device_serial_number_to_patch[serial_number],
            device_serial_number_to_action_history[serial_number],
        )

    body = {}
    body['action_id'] = action_id
    body['serial_numbers'] = serial_numbers
    await taxi_signal_device_configs.post(
        ENDPOINT, json=body, headers={**web_common.YA_TEAM_HEADERS},
    )
    for serial_number in ['serial1', 'serial2', 'serial3']:
        await check_db(
            db,
            f'WHERE serial_number = \'{serial_number}\'',
            device_serial_number_to_new_patch[serial_number],
            device_serial_number_to_new_action_history[serial_number],
        )


COMPOSITE_PRESET_PATCH_1 = {
    'preset_number': 1,
    'pervoe_pole': True,
}  # system.json
COMPOSITE_PRESET_PATCH_2 = {
    'preset_number': 2,
    'vtoroe_pole': True,
}  # default.json
COMPOSITE_PRESET_PATCH_3_SYSTEM = {'preset_number': 3, 'third_pole': True}
COMPOSITE_PRESET_PATCH_3_DEFAULT = {'preset_number': 3, 'third_pole': True}


@pytest.mark.parametrize(
    'action_id, new_patches, new_action_history',
    [
        (
            '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
            [COMPOSITE_PRESET_PATCH_1, COMPOSITE_PRESET_PATCH_2],
            [
                ['0598a7e7-dd77-4fa2-813a-1e13ab3afda7'],
                ['51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7'],
            ],
        ),
        (
            '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
            [
                COMPOSITE_PRESET_PATCH_3_SYSTEM,
                utils.deep_merge_dicts(
                    COMPOSITE_PRESET_PATCH_2, COMPOSITE_PRESET_PATCH_3_DEFAULT,
                ),
            ],
            [
                ['1bf10f86-1913-48b9-b4ab-ee35ccdde491'],
                [
                    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
                    '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
                ],
            ],
        ),
        (
            '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
            [
                utils.deep_merge_dicts(
                    COMPOSITE_PRESET_PATCH_1, COMPOSITE_PRESET_PATCH_3_DEFAULT,
                ),
                COMPOSITE_PRESET_PATCH_3_SYSTEM,
            ],
            [
                [
                    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
                    '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
                ],
                ['1bf10f86-1913-48b9-b4ab-ee35ccdde491'],
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'signal_device_configs', files=['test_data_composite_preset.sql'],
)
async def test_ok_composite_preset(
        taxi_signal_device_configs,
        pgsql,
        action_id,
        new_patches,
        new_action_history,
):
    body = {}
    body['preset_patch_id'] = 'id-1'
    body['preset_filter'] = {}
    body['preset_filter']['serial_numbers'] = ['serial1']
    await taxi_signal_device_configs.post(
        APPLY_ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': '0598a7e7-dd77-4fa2-813a-1e13ab3afda7'},
    )
    body['preset_patch_id'] = 'id-2'
    body['preset_filter']['serial_numbers'] = ['serial1']
    await taxi_signal_device_configs.post(
        APPLY_ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7'},
    )

    db = pgsql['signal_device_configs'].cursor()
    await check_db(
        db,
        'WHERE serial_number = \'serial1\' and config_name = \'system.json\'',
        COMPOSITE_PRESET_PATCH_1,
        ['0598a7e7-dd77-4fa2-813a-1e13ab3afda7'],
    )
    await check_db(
        db,
        'WHERE serial_number = \'serial1\' and config_name = \'default.json\'',
        COMPOSITE_PRESET_PATCH_2,
        ['51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7'],
    )

    body['preset_patch_id'] = 'id-3'
    body['preset_filter']['serial_numbers'] = ['serial1']
    await taxi_signal_device_configs.post(
        APPLY_ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': '1bf10f86-1913-48b9-b4ab-ee35ccdde491'},
    )

    await check_db(
        db,
        'WHERE serial_number = \'serial1\' and config_name = \'system.json\'',
        utils.deep_merge_dicts(
            COMPOSITE_PRESET_PATCH_1, COMPOSITE_PRESET_PATCH_3_DEFAULT,
        ),
        [
            '0598a7e7-dd77-4fa2-813a-1e13ab3afda7',
            '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
        ],
    )
    await check_db(
        db,
        'WHERE serial_number = \'serial1\' and config_name = \'default.json\'',
        utils.deep_merge_dicts(
            COMPOSITE_PRESET_PATCH_2, COMPOSITE_PRESET_PATCH_3_DEFAULT,
        ),
        [
            '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7',
            '1bf10f86-1913-48b9-b4ab-ee35ccdde491',
        ],
    )

    body = {}
    body['action_id'] = action_id
    await taxi_signal_device_configs.post(
        ENDPOINT, json=body, headers={**web_common.YA_TEAM_HEADERS},
    )

    await check_db(
        db,
        'WHERE serial_number = \'serial1\' and config_name = \'system.json\'',
        new_patches[0],
        new_action_history[0],
    )
    await check_db(
        db,
        'WHERE serial_number = \'serial1\' and config_name = \'default.json\'',
        new_patches[1],
        new_action_history[1],
    )
