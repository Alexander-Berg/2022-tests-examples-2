import pytest

from tests_signal_device_configs import utils
from tests_signal_device_configs import web_common

ENDPOINT = '/internal-admin/signal-device-configs/v1/patch-presets/apply'

PATCH_0 = {'distraction': True}
PATCH_1 = {'stream_meta': {'enabled': False}}  # p1
PATCH_2 = {
    'mqtt': {'enabled': False, 'timeout': 0.5},
    'fallback': 'NULL',
}  # serial1
PATCH_3 = {'some_old_event': {'enabled': False}}  # 0.0.0-1

PATCH_SERIAL_1_SOFT_1 = utils.deep_merge_dicts(
    utils.deep_merge_dicts(PATCH_0, PATCH_2), PATCH_3,
)

ALL_PATCH = utils.deep_merge_dicts(
    utils.deep_merge_dicts(utils.deep_merge_dicts(PATCH_0, PATCH_1), PATCH_2),
    PATCH_3,
)

PATCH_MQTT = {'mqtt': {'enabled': True}, 'fallback': 'some_conf'}
PATCH_ID_1 = {'mqtt': 'NULL'}
PATCH_ID_2 = {'distraction': {'enabled': True}}
PATCH_ID_3 = {'new_field': {'enabled': True}}
PATCH_ID_4 = {'stream_meta': False}
PATCH_ID_5 = {'stream_meta': True}
PATCH_DEFULT_JSON = {'distraction': {'enabled': False}}


@pytest.mark.pgsql('signal_device_configs', files=['test_data.sql'])
async def test_invalid_preset(taxi_signal_device_configs):
    body = {}
    body['preset_patch_id'] = 'id_not_exist'
    body['preset_filter'] = {}
    body['preset_filter']['serial_numbers'] = 'All'
    response = await taxi_signal_device_configs.post(
        ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': 'ed2037d3-9f6d-4312-8962-d2c53ed6df01'},
    )
    assert response.status_code == 404
    assert (
        response.json()['message'] == 'No preset patch with id : id_not_exist'
    )


@pytest.mark.parametrize(
    'park_id, serial_numbers, software_version, '
    'device_patches_updated_or_created',
    [
        (None, 'All', None, 8),
        ('p1', 'All', None, 4),
        (None, ['serial1'], None, 4),
        (None, 'All', '0.0.0-1', 4),
        ('p1', ['serial1'], None, 2),
        (None, ['serial1'], '0.0.0-1', 2),
        ('p1', 'All', '0.0.0-1', 2),
        ('p1', ['serial1'], '0.0.0-1', 1),
        ('p2', 'All', None, 4),
        (None, ['serial2'], None, 4),
        (None, 'All', '0.0.0-2', 4),
        ('p2', 'All', '0.0.0-1', 2),
        (None, ['serial2'], '0.0.0-1', 2),
        ('p1', ['serial2'], None, 2),
        ('p2', ['serial1'], '0.0.0-1', 1),
        ('p1', ['serial1'], '0.0.0-2', 1),
        (None, ['serial1', 'serial2'], '0.0.0-1', 4),
        (None, ['serial2'], '0.0.0-2', 2),
        ('p2', ['serial2'], None, 2),
        (None, ['serial6', 'serial5', 'serial4'], '0.0.0-1', 6),
    ],
)
@pytest.mark.pgsql('signal_device_configs', files=['test_data.sql'])
async def test_filter_ok(
        taxi_signal_device_configs,
        pgsql,
        park_id,
        serial_numbers,
        software_version,
        device_patches_updated_or_created,
):
    body = {}
    body['preset_patch_id'] = 'id-3'
    body['preset_filter'] = {}
    body['preset_filter']['serial_numbers'] = serial_numbers
    if park_id is not None:
        body['preset_filter']['park_id'] = park_id
    if software_version is not None:
        body['preset_filter']['software_version'] = software_version
    response = await taxi_signal_device_configs.post(
        ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': 'ed2037d3-9f6d-4312-8962-d2c53ed6df01'},
    )
    assert response.status_code, response.text
    db = pgsql['signal_device_configs'].cursor()
    db.execute(
        f"""
        SELECT TRUE FROM signal_device_configs.device_patches
        WHERE updated_at > NOW() - INTERVAL '5 MINUTE'
        """,
    )
    assert len(list(db)) == device_patches_updated_or_created


@pytest.mark.parametrize(
    'preset_id, park_id, expected_patch, name',
    [
        (
            'id-mqtt',
            'p1',
            utils.deep_merge_dicts(ALL_PATCH, PATCH_MQTT),
            'system.json',
        ),
        (
            'id-1',
            'p1',
            utils.deep_merge_dicts(ALL_PATCH, PATCH_ID_1),
            'system.json',
        ),
        (
            'id-2',
            'p1',
            utils.deep_merge_dicts(ALL_PATCH, PATCH_ID_2),
            'system.json',
        ),
        (
            'id-3',
            'p1',
            utils.deep_merge_dicts(ALL_PATCH, PATCH_ID_3),
            'system.json',
        ),
        (
            'id-mqtt',
            'p2',
            utils.deep_merge_dicts(PATCH_SERIAL_1_SOFT_1, PATCH_MQTT),
            'system.json',
        ),
        (
            'id-4',
            'p2',
            utils.deep_merge_dicts(PATCH_SERIAL_1_SOFT_1, PATCH_ID_4),
            'system.json',
        ),
        ('id-4', 'p2', PATCH_DEFULT_JSON, 'default.json'),
    ],
)
@pytest.mark.pgsql('signal_device_configs', files=['test_data.sql'])
async def test_merge_json(
        taxi_signal_device_configs,
        pgsql,
        preset_id,
        park_id,
        expected_patch,
        name,
):
    body = {}
    body['preset_patch_id'] = preset_id
    body['preset_filter'] = {}
    body['preset_filter']['park_id'] = park_id
    body['preset_filter']['serial_numbers'] = ['serial1']
    body['preset_filter']['software_version'] = '0.0.0-1'
    response = await taxi_signal_device_configs.post(
        ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': 'ed2037d3-9f6d-4312-8962-d2c53ed6df01'},
    )
    assert response.status_code, response.text
    db = pgsql['signal_device_configs'].cursor()
    db.execute(
        f"""
        SELECT patch_id FROM signal_device_configs.device_patches
        WHERE config_name = '{name}' AND park_id = '{park_id}'
        AND serial_number = 'serial1'
        AND canonized_software_version =
        '{utils.get_canonized_software_version('0.0.0-1')}'
        """,
    )
    patch_id = list(db)[0][0]
    db.execute(
        f"""
        SELECT patch FROM signal_device_configs.patches
        WHERE id = {patch_id}
        """,
    )
    patch = list(db)[0][0]
    assert patch == expected_patch


@pytest.mark.parametrize(
    'action_ids, expected_code, expected_message',
    [
        (
            [
                'ed2037d3-9f6d-4312-8962-d2c53ed6df01',
                '7e712270-ad55-457c-8c4d-7c65fa2149a9',
                '6099c348-2366-4b89-a672-047bf22ae981',
            ],
            200,
            None,
        ),
        (
            ['f37a495c-d7a2-488f-b7da-93dd2fa3bdcd', 'action1', 'action1'],
            409,
            'Action with id = f37a495c-d7a2-488f-b7da-93dd2fa3bdcd already exists',  # noqa E501
        ),
    ],
)
@pytest.mark.pgsql('signal_device_configs', files=['test_data.sql'])
async def test_action_history(
        taxi_signal_device_configs,
        pgsql,
        action_ids,
        expected_code,
        expected_message,
):
    body = {}
    preset_ids = ['id-mqtt', 'id-3', 'id-2']
    body['preset_filter'] = {}
    body['preset_filter']['park_id'] = 'p1'
    body['preset_filter']['serial_numbers'] = ['serial1']
    body['preset_filter']['software_version'] = '0.0.0-1'
    for action_id, preset_id in zip(action_ids, preset_ids):
        body['preset_patch_id'] = preset_id
        response = await taxi_signal_device_configs.post(
            ENDPOINT,
            json=body,
            headers={**web_common.YA_TEAM_HEADERS},
            params={'action_id': action_id},
        )
        assert response.status_code == expected_code
        if expected_code == 409:
            assert response.json()['message'] == expected_message
            return

    db = pgsql['signal_device_configs'].cursor()
    db.execute(
        f"""
        SELECT patch_id FROM signal_device_configs.device_patches
        WHERE config_name = 'system.json' AND park_id = 'p1'
        AND serial_number = 'serial1'
        AND canonized_software_version =
        '{utils.get_canonized_software_version('0.0.0-1')}'
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

    assert patch == utils.deep_merge_dicts(
        utils.deep_merge_dicts(
            utils.deep_merge_dicts(ALL_PATCH, PATCH_MQTT), PATCH_ID_3,
        ),
        PATCH_ID_2,
    )
    assert action_history == action_ids

    for action_id, preset_id in zip(action_ids, preset_ids):
        db.execute(
            f"""
            SELECT * FROM signal_device_configs.actions
            WHERE id = '{action_id}'
            """,
        )
        db_result = list(db)
        assert db_result[0][1] == preset_id
        assert db_result[0][2] == 'p1'
        assert db_result[0][3] == ['serial1']
        assert db_result[0][4] == utils.get_canonized_software_version(
            '0.0.0-1',
        )


@pytest.mark.pgsql('signal_device_configs', files=['test_empty.sql'])
async def test_empty(taxi_signal_device_configs, pgsql):
    body = {}
    body['preset_patch_id'] = 'id-1'
    body['preset_filter'] = {}
    body['preset_filter']['serial_numbers'] = ['serial1']
    response = await taxi_signal_device_configs.post(
        ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': 'ed2037d3-9f6d-4312-8962-d2c53ed6df01'},
    )
    assert response.status_code, response.text

    db = pgsql['signal_device_configs'].cursor()
    db.execute(
        f"""
        SELECT patch_id from signal_device_configs.device_patches
        WHERE serial_number = 'serial1'
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
    assert patch == PATCH_ID_1


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
async def test_features_empty_history(taxi_signal_device_configs, pgsql):
    park_id = 'p11'
    body = {}
    body['preset_patch_id'] = 'id-9'
    body['preset_filter'] = {}
    body['preset_filter']['park_id'] = park_id
    body['preset_filter']['serial_numbers'] = 'All'
    response = await taxi_signal_device_configs.post(
        ENDPOINT,
        json=body,
        headers={**web_common.YA_TEAM_HEADERS},
        params={'action_id': '2f217357-4160-41be-bbcd-c7d87232383d'},
    )
    assert response.status_code, response.text

    db = pgsql['signal_device_configs'].cursor()
    db.execute(
        f"""
        SELECT patch_id
        FROM signal_device_configs.device_patches
        WHERE park_id = '{park_id}'
        AND canonized_software_version = ''
        AND serial_number = ''
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
    assert patch == PATCH_ID_5
