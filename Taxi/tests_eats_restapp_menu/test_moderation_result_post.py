import json

import pytest

PLACE_ID = 109151
REVISION = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'
TASK_ID = 'task123'


@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.parametrize(
    ('status', 'file_expected'),
    [
        pytest.param('approved', 'expected_images.json', id='approve'),
        pytest.param('rejected', 'expected_rejected_images.json', id='reject'),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_post_basic(
        taxi_eats_restapp_menu,
        pg_get_menu_content,
        pg_get_pictures,
        load_json,
        status,
        file_expected,
):

    response = await taxi_eats_restapp_menu.post(
        '/v1/moderation/result',
        json={
            'task_id': TASK_ID,
            'context': {'place_id': str(PLACE_ID)},
            'queue': 'restapp_moderation_menu',
            'status': status,
            'actual_payload': {},
            'payload': {
                'id': '1234595',
                'identity': '1368744/9d2253f1d40f86ff4e525e998f49dfca',
                'revision': REVISION,
            },
        },
    )

    assert response.status_code == 200

    db_data = pg_get_pictures()
    assert len(db_data) == 3
    assert (
        db_data[0]['status'] == status
        and db_data[1]['status'] == 'moderation'
        and db_data[2]['status'] == 'approved'
    )

    assert json.loads(pg_get_menu_content()[0]['menu_json']) == load_json(
        file_expected,
    )


@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_post_invalid(taxi_eats_restapp_menu):

    response = await taxi_eats_restapp_menu.post(
        '/v1/moderation/result',
        json={
            'task_id': TASK_ID,
            'context': {'place_id': str(PLACE_ID)},
            'queue': 'restapp_moderation_menu',
            'status': 'rejected',
            'actual_payload': {},
            'payload': {
                'id': 'UNKNOWN',
                'identity': '1368744/9d2253f1d40f86ff4e525e998f49dfca',
                'revision': REVISION,
            },
        },
    )

    assert response.status_code == 404


@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_post_400(taxi_eats_restapp_menu):

    response = await taxi_eats_restapp_menu.post(
        '/v1/moderation/result',
        json={
            'task_id': TASK_ID,
            'context': {'place_id': str(PLACE_ID)},
            'queue': 'UNKNOWN_QUEUE',
            'status': 'rejected',
            'actual_payload': {},
            'payload': {
                'id': '1234595',
                'identity': '1368744/9d2253f1d40f86ff4e525e998f49dfca',
                'revision': REVISION,
            },
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    ('status', 'file_expected'),
    [
        pytest.param('approved', 'expected_config.json', id='approve'),
        pytest.param('rejected', 'expected_rejected_config.json', id='reject'),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_post_config(
        taxi_eats_restapp_menu,
        pg_get_menu_content,
        pg_get_revisions,
        load_json,
        status,
        file_expected,
        get_parametrized_config,
):
    response = await taxi_eats_restapp_menu.post(
        '/v1/moderation/result',
        json={
            'task_id': TASK_ID,
            'context': {'place_id': str(PLACE_ID)},
            'queue': 'restapp_moderation_item',
            'reasons': get_parametrized_config['reasons'],
            'status': status,
            'actual_payload': {},
            'payload': {
                'id': '1234595',
                'identity': '1368744/9d2253f1d40f86ff4e525e998f49dfca',
                'revision': REVISION,
            },
        },
    )

    assert response.status_code == 200

    db_data = pg_get_revisions()
    assert len(db_data) == 2
    assert (
        db_data[0]['origin'] == 'moderation'
        and db_data[1]['origin'] == 'user_generated'
    )
    assert (
        json.loads(db_data[0]['errors_json'])
        == get_parametrized_config['expected']
    )

    db_content = pg_get_menu_content()
    assert db_content[0]['menu_hash'] == db_data[0]['menu_hash']
    assert json.loads(db_content[0]['menu_json']) == load_json(file_expected)


@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_post_change_data(
        taxi_eats_restapp_menu,
        pg_get_revisions,
        pg_get_menu_content,
        load_json,
):

    response = await taxi_eats_restapp_menu.post(
        '/v1/moderation/result',
        json={
            'task_id': TASK_ID,
            'context': {'place_id': str(PLACE_ID)},
            'queue': 'restapp_moderation_item',
            'status': 'approved',
            'actual_payload': {},
            'payload': {
                'id': '1234595',
                'revision': REVISION,
                'value': '{"name": "Поправили имя"}',
            },
        },
    )

    assert response.status_code == 200

    db_revisions = pg_get_revisions()
    assert len(db_revisions) == 2
    assert (
        db_revisions[0]['origin'] == 'moderation'
        and db_revisions[0]['status'] == 'processing'
        and db_revisions[1]['origin'] == 'user_generated'
        and db_revisions[1]['status'] == 'applied'
    )

    db_content = pg_get_menu_content()
    assert db_content[0]['menu_hash'] == db_revisions[0]['menu_hash']
    assert json.loads(db_content[0]['menu_json']) == load_json(
        'expected_change_data.json',
    )


@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
    },
)
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_post_change_options(
        taxi_eats_restapp_menu,
        pg_get_revisions,
        pg_get_menu_content,
        load_json,
):

    response = await taxi_eats_restapp_menu.post(
        '/v1/moderation/result',
        json={
            'task_id': TASK_ID,
            'context': {'place_id': str(PLACE_ID)},
            'queue': 'restapp_moderation_item',
            'status': 'approved',
            'actual_payload': {},
            'payload': {
                'id': '1234595',
                'revision': REVISION,
                'value': (
                    '{"name": "Сметана 20%", "modifierGroups": [{"id":'
                    ' "123", "name": "unknown"}, {"id": "kzgxvz3g-lses'
                    'vny8wc-lrf53ugye5", "name": "Поправили группу", "'
                    'modifiers": [{"id": "321", "name": "unknown_optio'
                    'ns"},{"id": "kzgxw3uo-bjjsuf6o7tc-guo5kqc3f4o", "'
                    'name": "Поправили опцию"}]}]}'
                ),
            },
        },
    )

    assert response.status_code == 200

    db_revisions = pg_get_revisions()
    assert len(db_revisions) == 2
    assert (
        db_revisions[0]['origin'] == 'moderation'
        and db_revisions[0]['status'] == 'processing'
        and db_revisions[1]['origin'] == 'user_generated'
        and db_revisions[1]['status'] == 'applied'
    )

    db_content = pg_get_menu_content()
    assert db_content[0]['menu_hash'] == db_revisions[0]['menu_hash']
    assert json.loads(db_content[0]['menu_json']) == load_json(
        'expected_change_options.json',
    )
