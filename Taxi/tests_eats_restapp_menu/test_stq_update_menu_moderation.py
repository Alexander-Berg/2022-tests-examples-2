import json

import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
MENU_REVISION = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'
MENU_REVISION_STQ = 'MS4xNjI4NDI0MDAwMDAwLmJDb012aVBoQW1Db2hUUGhubmZxLXc'
MENU_REVISION_WITH_VALIDATION = (
    'MS4xNjI4NDI0MDAwMDAwLlZjR2ZibE1pMHhVY2k1SVpZNXYzdXc'
)
MENU_REVISION_FOR_MERGE = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFlu'
MENU_REVISION_DERIVED = 'MS4xNjI4NDI0MDAwMDAwLlVMbERWdDczaWdqWXc5MnNlSy1jbkE'
MENU_REVISION_DERIVED_OPTIONS = (
    'MS4xNjI4NDI0MDAwMDAwLlJjc0JNeUN4UDl4bDcybjFYeWQzOWc'
)
MENU_REVISION_NEW_BASE = 'MS4xNjA5NDU5MjAwMDAwLndpZEpzLTB5dzVnWmt5VVlUcXRlRWc'
MENU_REVISION_BASE = 'base_revision_hash'
UPDATE_JOB_ID = '86fde2da-3c74-4408-909c-985a8b3c3bc1'


@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.parametrize(
    (
        'merge_called',
        'result_revision',
        'revisions_count',
        'sent_menu',
        'validations_count',
        'merging_revision',
        'moderation_tasks_count',
        'moderation_file',
    ),
    [
        pytest.param(
            1,
            MENU_REVISION_STQ,
            4,
            'sent_menu.json',
            0,
            MENU_REVISION,
            6,
            'moderation_success_1.json',
            id='merging config',
        ),
        pytest.param(
            1,
            MENU_REVISION_WITH_VALIDATION,
            4,
            'sent_menu_validation.json',
            1,
            MENU_REVISION_WITH_VALIDATION,
            6,
            'moderation_success_2.json',
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_MENU_VALIDATION={'enabled': True},
                ),
            ],
            id='merging and validation config',
        ),
    ],
)
@pytest.mark.experiments3(filename='moderation_flow_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_stq_update_menu_moderation_success(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        load_json,
        testpoint,
        merge_called,
        result_revision,
        revisions_count,
        sent_menu,
        validations_count,
        merging_revision,
        mock_eats_catalog_storage,
        moderation_tasks_count,
        moderation_file,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        req_json = request.json
        del req_json['lastChange']
        assert request.query['place_id'] == PLACE_ID
        assert req_json == load_json(sent_menu)
        return {'jobId': UPDATE_JOB_ID, 'isNewJob': True}

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data_empty.json')

    @mockserver.json_handler(
        f'/eats-core-restapp/v1/eats-restapp-menu/validate',
    )
    def mock_validate_menu(request):
        return load_json('validated_menu.json')

    @testpoint('MergeMenu')
    def merge_menu(arg):
        assert arg == {
            'revision': merging_revision,
            'base_revision': MENU_REVISION_BASE,
        }

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION,
        kwargs={'place_id': int(PLACE_ID), 'revision': MENU_REVISION},
        expect_fail=False,
    )

    assert mock_validate_menu.times_called == validations_count
    assert mock_place_menu.times_called == merge_called
    assert core_menu_update.times_called == 1
    assert merge_menu.times_called == merge_called
    assert stq.eats_restapp_menu_update_menu_status.times_called == 1
    assert (
        stq.eats_restapp_menu_moderate_menu.times_called
        == moderation_tasks_count
    )

    expected = (
        load_json(moderation_file) if moderation_file is not None else []
    )
    for i in range(moderation_tasks_count):
        req_data = stq.eats_restapp_menu_moderate_menu.next_call()['kwargs']
        req_data['context'] = json.loads(req_data['context'])
        req_data['payload'] = json.loads(req_data['payload'])
        if 'value' in req_data['payload']:
            req_data['payload']['value'] = json.loads(
                req_data['payload']['value'],
            )
        assert {
            'context': req_data['context'],
            'payload': req_data['payload'],
            'queue': req_data['queue'],
            'scope': req_data['scope'],
        } == expected[i]

    stq_args = stq.eats_restapp_menu_update_menu_status.next_call()['kwargs']
    del stq_args['log_extra']
    assert stq_args == {
        'place_id': int(PLACE_ID),
        'revision': result_revision,
        'job_id': UPDATE_JOB_ID,
    }

    db_data = pg_get_revisions()
    assert len(db_data) == revisions_count


@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data_merging.sql',))
@pytest.mark.experiments3(filename='moderation_flow_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
async def test_stq_update_menu_moderation_success_merging(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        load_json,
        testpoint,
        mock_eats_catalog_storage,
        mock_eats_moderation,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def core_menu_get(request):
        return load_json('base_data_merging.json')

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        expected = load_json('sent_menu_merging.json')
        req_json = request.json
        req_json['lastChange'] = expected['lastChange']
        assert request.query['place_id'] == PLACE_ID
        assert req_json == expected
        return {'jobId': UPDATE_JOB_ID, 'isNewJob': True}

    @testpoint('MergeMenu')
    def merge_menu(arg):
        assert arg == {
            'revision': MENU_REVISION_FOR_MERGE,
            'base_revision': MENU_REVISION,
        }

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION_FOR_MERGE,
        kwargs={
            'place_id': int(PLACE_ID),
            'revision': MENU_REVISION_FOR_MERGE,
        },
        expect_fail=False,
    )

    assert core_menu_get.times_called == 1
    assert core_menu_update.times_called == 1
    assert merge_menu.times_called == 1
    assert stq.eats_restapp_menu_update_menu_status.times_called == 1

    stq_args = stq.eats_restapp_menu_update_menu_status.next_call()['kwargs']
    del stq_args['log_extra']
    assert stq_args == {
        'place_id': int(PLACE_ID),
        'revision': MENU_REVISION_DERIVED,
        'job_id': UPDATE_JOB_ID,
    }

    assert stq.eats_restapp_menu_moderate_menu.times_called == 2

    req_data = stq.eats_restapp_menu_moderate_menu.next_call()['kwargs']
    req_data['context'] = json.loads(req_data['context'])
    req_data['payload'] = json.loads(req_data['payload'])
    req_data['payload']['value'] = json.loads(req_data['payload']['value'])
    req_data['payload']['modified_value'] = json.loads(
        req_data['payload']['modified_value'],
    )
    assert (
        {
            'context': req_data['context'],
            'payload': req_data['payload'],
            'queue': req_data['queue'],
            'scope': req_data['scope'],
        }
        == {
            'context': {
                'city': 'Москва',
                'origin_id': '1234595',
                'partner_id': '765',
                'place_id': '109151',
            },
            'payload': {
                'id': '1234595',
                'modified_value': {
                    'changed': {
                        'available': False,
                        'reactivatedAt': '2021-09-02T21:00:00+00:00',
                        'description': 'Добавили описание',
                    },
                    'id': '1234595',
                    'op': 'Mod',
                },
                'revision': (
                    'MS4xNjI4NDI0MDAwMDAwLlVMbERWdDczaWdqWXc5MnNlSy1jbkE'
                ),
                'value': {
                    'available': False,
                    'categoryId': '103263',
                    'description': 'Добавили описание',
                    'id': '1234595',
                    'images': [
                        {
                            'approved': True,
                            'url': (
                                'https://testing.eda.tst.yandex.net/'
                                'images/1368744/'
                                '9d2253f1d40f86ff4e525e998f49dfca.jpg'
                            ),
                        },
                    ],
                    'measure': 50,
                    'measureUnit': 'г',
                    'menuItemId': 37660168,
                    'modifierGroups': [],
                    'name': 'Сметана 20%',
                    'price': 100,
                    'reactivatedAt': '2021-09-02T21:00:00+00:00',
                    'sortOrder': 100,
                    'thumbnails': [
                        {
                            'url': (
                                'https://testing.eda.tst.yandex.net/'
                                'images/1368744/'
                                '9d2253f1d40f86ff4e525e998f49dfca-80x80.jpg'
                            ),
                        },
                    ],
                    'vat': 0,
                },
            },
            'queue': 'restapp_moderation_item',
            'scope': 'eda',
        }
    )

    req_data = stq.eats_restapp_menu_moderate_menu.next_call()['kwargs']
    req_data['context'] = json.loads(req_data['context'])
    req_data['payload'] = json.loads(req_data['payload'])
    req_data['payload']['value'] = json.loads(req_data['payload']['value'])
    assert (
        {
            'context': req_data['context'],
            'payload': req_data['payload'],
            'queue': req_data['queue'],
            'scope': req_data['scope'],
        }
        == {
            'context': {
                'place_id': '109151',
                'partner_id': '765',
                'city': 'Москва',
                'origin_id': '103265',
            },
            'scope': 'eda',
            'queue': 'restapp_moderation_category',
            'payload': {
                'value': {
                    'id': '103265',
                    'sortOrder': 160,
                    'available': True,
                    'name': 'Закуски и прочее',
                    'parentId': None,
                    'reactivatedAt': None,
                },
                'id': '103265',
                'revision': (
                    'MS4xNjI4NDI0MDAwMDAwLlVMbERWdDczaWdqWXc5MnNlSy1jbkE'
                ),
            },
        }
    )

    db_data = pg_get_revisions()
    assert (
        len(db_data) == 4
        and db_data[0]['revision'] == MENU_REVISION_NEW_BASE
        and db_data[0]['origin'] == 'external'
        and db_data[0]['status'] == 'not_applicable'
        and db_data[1]['revision'] == MENU_REVISION_DERIVED
        and db_data[1]['origin'] == 'derived'
        and db_data[1]['status'] == 'updating'
        and db_data[2]['revision'] == MENU_REVISION
        and db_data[2]['origin'] == 'external'
        and db_data[2]['status'] == 'not_applicable'
        and db_data[3]['revision'] == MENU_REVISION_FOR_MERGE
        and db_data[3]['origin'] == 'user_generated'
        and db_data[3]['status'] == 'updating'
    )


@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data_conflict.sql',))
@pytest.mark.experiments3(filename='moderation_flow_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
async def test_stq_update_menu_moderation_success_conflict(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        load_json,
        testpoint,
        mock_eats_catalog_storage,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def core_menu_get(request):
        return load_json('base_data_conflict.json')

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        expected = load_json('sent_menu_conflict.json')
        req_json = request.json
        req_json['lastChange'] = expected['lastChange']
        assert request.query['place_id'] == PLACE_ID
        assert req_json == expected
        return {'jobId': UPDATE_JOB_ID, 'isNewJob': True}

    @testpoint('MergeMenu')
    def merge_menu(arg):
        assert arg == {
            'revision': MENU_REVISION_FOR_MERGE,
            'base_revision': MENU_REVISION,
        }

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION_FOR_MERGE,
        kwargs={
            'place_id': int(PLACE_ID),
            'revision': MENU_REVISION_FOR_MERGE,
        },
        expect_fail=False,
    )

    assert core_menu_get.times_called == 1
    assert core_menu_update.times_called == 1
    assert merge_menu.times_called == 1
    assert stq.eats_restapp_menu_update_menu_status.times_called == 1

    stq_args = stq.eats_restapp_menu_update_menu_status.next_call()['kwargs']
    assert (
        stq_args['place_id'] == int(PLACE_ID)
        and stq_args['job_id'] == UPDATE_JOB_ID
    )

    assert stq.eats_restapp_menu_moderate_menu.times_called == 3
    req_data = stq.eats_restapp_menu_moderate_menu.next_call()['kwargs']
    req_data['context'] = json.loads(req_data['context'])
    req_data['payload'] = json.loads(req_data['payload'])
    req_data['payload']['value'] = json.loads(req_data['payload']['value'])
    req_data['payload']['modified_value'] = json.loads(
        req_data['payload']['modified_value'],
    )
    assert {
        'context': req_data['context'],
        'payload': req_data['payload'],
        'queue': req_data['queue'],
        'scope': req_data['scope'],
    } == load_json('moderation_success_conflict_2.json')

    req_data = stq.eats_restapp_menu_moderate_menu.next_call()['kwargs']
    req_data['context'] = json.loads(req_data['context'])
    req_data['payload'] = json.loads(req_data['payload'])
    req_data['payload']['value'] = json.loads(req_data['payload']['value'])
    req_data['payload']['modified_value'] = json.loads(
        req_data['payload']['modified_value'],
    )
    assert {
        'context': req_data['context'],
        'payload': req_data['payload'],
        'queue': req_data['queue'],
        'scope': req_data['scope'],
    } == load_json('moderation_success_conflict_1.json')

    req_data = stq.eats_restapp_menu_moderate_menu.next_call()['kwargs']
    req_data['context'] = json.loads(req_data['context'])
    req_data['payload'] = json.loads(req_data['payload'])
    req_data['payload']['value'] = json.loads(req_data['payload']['value'])
    assert (
        {
            'context': req_data['context'],
            'payload': req_data['payload'],
            'queue': req_data['queue'],
            'scope': req_data['scope'],
        }
        == {
            'context': {
                'place_id': '109151',
                'partner_id': '765',
                'origin_id': '103263',
                'city': 'Москва',
            },
            'scope': 'eda',
            'queue': 'restapp_moderation_category',
            'payload': {
                'revision': (
                    'MS4xNjI4NDI0MDAwMDAwLklEMldfWU9sVWZHUlhiemNDUUJWaGc'
                ),
                'value': {
                    'id': '103263',
                    'sortOrder': 130,
                    'available': True,
                    'name': 'Завтрак (изменен)',
                    'parentId': None,
                    'reactivatedAt': None,
                },
                'id': '103263',
            },
        }
    )

    db_data = pg_get_revisions()
    assert len(db_data) == 4


@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.experiments3(filename='moderation_flow_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': False,
    },
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_stq_update_menu_moderation_images_remove(
        stq_runner,
        mockserver,
        stq,
        testpoint,
        pg_get_revisions,
        load_json,
        mock_eats_catalog_storage,
        mock_eats_moderation,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        req_json = request.json
        del req_json['lastChange']
        assert request.query['place_id'] == PLACE_ID
        assert req_json == {
            'categories': [
                {
                    'id': '103263',
                    'name': 'Завтрак',
                    'sortOrder': 130,
                    'available': True,
                },
                {
                    'id': '103265',
                    'name': 'Закуски',
                    'sortOrder': 160,
                    'available': True,
                },
            ],
            'items': [
                {
                    'id': '1234583',
                    'categoryId': '103263',
                    'name': 'Сухофрукты',
                    'description': '',
                    'price': 100.0,
                    'vat': 0,
                    'measure': 35.0,
                    'measureUnit': 'г',
                    'sortOrder': 100,
                    'modifierGroups': [],
                    'images': [],
                    'thumbnails': [],
                    'available': False,
                    'menuItemId': 37660163,
                },
                {
                    'id': '1234595',
                    'categoryId': '103263',
                    'name': 'Сметана 20%',
                    'description': '',
                    'price': 100.0,
                    'vat': 0,
                    'measure': 50.0,
                    'measureUnit': 'г',
                    'sortOrder': 100,
                    'modifierGroups': [],
                    'images': [
                        {
                            'url': (
                                'https://testing.eda.tst.yandex.net/'
                                'images/OLD/OLDOLDOLD.jpg'
                            ),
                            'avatarnicaIdentity': 'OLD/OLDOLDOLD',
                        },
                    ],
                    'thumbnails': [],
                    'available': False,
                    'menuItemId': 37660168,
                },
            ],
        }
        return {'jobId': UPDATE_JOB_ID, 'isNewJob': True}

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data_images.json')

    @testpoint('MergeMenu')
    def merge_menu(arg):
        assert arg == {
            'revision': MENU_REVISION,
            'base_revision': MENU_REVISION_BASE,
        }

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION,
        kwargs={'place_id': int(PLACE_ID), 'revision': MENU_REVISION},
        expect_fail=False,
    )

    assert mock_place_menu.times_called == 1
    assert core_menu_update.times_called == 1
    assert merge_menu.times_called == 1
    assert stq.eats_restapp_menu_update_menu_status.times_called == 1
    assert stq.eats_restapp_menu_moderate_menu.times_called == 2

    expected = [
        {
            'context': {
                'place_id': '109151',
                'origin_id': '1234595',
                'partner_id': 'system',
                'city': 'Москва',
            },
            'scope': 'eda',
            'queue': 'restapp_moderation_menu',
            'payload': {
                'identity': '1368744/9d2253f1d40f86ff4e525e998f49dfca',
                'photo_url': (
                    'https://testing.eda.tst.yandex.net/images/'
                    '1368744/9d2253f1d40f86ff4e525e998f49dfca.jpg'
                ),
                'id': '1234595',
                'revision': (
                    'MS4xNjI4NDI0MDAwMDAwLmJDb012aVBoQW1Db2hUUGhubmZxLXc'
                ),
            },
        },
        {
            'context': {
                'place_id': '109151',
                'origin_id': '1234583',
                'partner_id': 'system',
                'city': 'Москва',
            },
            'scope': 'eda',
            'queue': 'restapp_moderation_menu',
            'payload': {
                'identity': '1370147/36ca994761eb1fd00066ac634c96e0d9',
                'photo_url': (
                    'https://testing.eda.tst.yandex.net/images/'
                    '1370147/36ca994761eb1fd00066ac634c96e0d9.jpg'
                ),
                'id': '1234583',
                'revision': (
                    'MS4xNjI4NDI0MDAwMDAwLmJDb012aVBoQW1Db2hUUGhubmZxLXc'
                ),
            },
        },
    ]

    for i in range(2):
        req_data = stq.eats_restapp_menu_moderate_menu.next_call()['kwargs']
        req_data['context'] = json.loads(req_data['context'])
        req_data['payload'] = json.loads(req_data['payload'])
        if 'value' in req_data['payload']:
            req_data['payload']['value'] = json.loads(
                req_data['payload']['value'],
            )
        assert {
            'context': req_data['context'],
            'payload': req_data['payload'],
            'queue': req_data['queue'],
            'scope': req_data['scope'],
        } == expected[i]

    stq_args = stq.eats_restapp_menu_update_menu_status.next_call()['kwargs']
    del stq_args['log_extra']
    assert stq_args == {
        'place_id': int(PLACE_ID),
        'revision': MENU_REVISION_STQ,
        'job_id': UPDATE_JOB_ID,
    }

    db_data = pg_get_revisions()
    assert len(db_data) == 4


@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.pgsql(
    'eats_restapp_menu', files=('fill_data_merging_options.sql',),
)
@pytest.mark.experiments3(filename='moderation_flow_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': False,
    },
)
async def test_stq_update_menu_moderation_success_options(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        load_json,
        testpoint,
        mock_eats_catalog_storage,
        mock_eats_moderation,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def core_menu_get(request):
        return load_json('base_data_merging.json')

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        expected = load_json('sent_menu_merging_options.json')
        req_json = request.json
        req_json['lastChange'] = expected['lastChange']
        assert request.query['place_id'] == PLACE_ID
        assert req_json == expected
        return {'jobId': UPDATE_JOB_ID, 'isNewJob': True}

    @testpoint('MergeMenu')
    def merge_menu(arg):
        assert arg == {
            'revision': MENU_REVISION_FOR_MERGE,
            'base_revision': MENU_REVISION,
        }

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION_FOR_MERGE,
        kwargs={
            'place_id': int(PLACE_ID),
            'revision': MENU_REVISION_FOR_MERGE,
        },
        expect_fail=False,
    )

    assert core_menu_get.times_called == 1
    assert core_menu_update.times_called == 1
    assert merge_menu.times_called == 1
    assert stq.eats_restapp_menu_update_menu_status.times_called == 1

    stq_args = stq.eats_restapp_menu_update_menu_status.next_call()['kwargs']
    del stq_args['log_extra']
    assert stq_args == {
        'place_id': int(PLACE_ID),
        'revision': MENU_REVISION_DERIVED_OPTIONS,
        'job_id': UPDATE_JOB_ID,
    }

    assert stq.eats_restapp_menu_moderate_menu.times_called == 1

    req_data = stq.eats_restapp_menu_moderate_menu.next_call()['kwargs']
    req_data['context'] = json.loads(req_data['context'])
    req_data['payload'] = json.loads(req_data['payload'])
    req_data['payload']['value'] = json.loads(req_data['payload']['value'])
    req_data['payload']['modified_value'] = json.loads(
        req_data['payload']['modified_value'],
    )
    assert (
        {
            'context': req_data['context'],
            'payload': req_data['payload'],
            'queue': req_data['queue'],
            'scope': req_data['scope'],
        }
        == {
            'context': {
                'city': 'Москва',
                'origin_id': '1234595',
                'partner_id': '765',
                'place_id': '109151',
            },
            'payload': {
                'modified_value': {
                    'op': 'Mod',
                    'id': '1234595',
                    'changed': {
                        'modifierGroups': [
                            {
                                'id': '2716078',
                                'maxSelectedModifiers': 6,
                                'menuItemOptionGroupId': 21171787,
                                'minSelectedModifiers': 0,
                                'modifiers': [
                                    {
                                        'available': True,
                                        'id': '26778790',
                                        'maxAmount': 1,
                                        'menuItemOptionId': 172641802,
                                        'minAmount': 0,
                                        'name': 'Малина протертая с сахаром',
                                        'price': 100.0,
                                    },
                                    {
                                        'available': True,
                                        'id': '26778793',
                                        'maxAmount': 1,
                                        'menuItemOptionId': 172641807,
                                        'minAmount': 0,
                                        'name': 'Клубника протертая с сахаром',
                                        'price': 100.0,
                                    },
                                ],
                                'name': 'Дополнительные ингредиенты',
                                'sortOrder': 100,
                            },
                        ],
                    },
                },
                'value': {
                    'id': '1234595',
                    'categoryId': '103263',
                    'name': 'Сметана 20%',
                    'description': '',
                    'price': 100,
                    'vat': 0,
                    'measure': 50,
                    'measureUnit': 'г',
                    'sortOrder': 100,
                    'available': True,
                    'menuItemId': 37660168,
                    'modifierGroups': [
                        {
                            'id': '2716078',
                            'maxSelectedModifiers': 6,
                            'menuItemOptionGroupId': 21171787,
                            'minSelectedModifiers': 0,
                            'modifiers': [
                                {
                                    'available': True,
                                    'id': '26778790',
                                    'maxAmount': 1,
                                    'menuItemOptionId': 172641802,
                                    'minAmount': 0,
                                    'name': 'Малина протертая с сахаром',
                                    'price': 100.0,
                                },
                                {
                                    'available': True,
                                    'id': '26778793',
                                    'maxAmount': 1,
                                    'menuItemOptionId': 172641807,
                                    'minAmount': 0,
                                    'name': 'Клубника протертая с сахаром',
                                    'price': 100.0,
                                },
                            ],
                            'name': 'Дополнительные ингредиенты',
                            'sortOrder': 100,
                        },
                    ],
                    'images': [
                        {
                            'url': (
                                'https://testing.eda.tst.yandex.net/images/'
                                '1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg'
                            ),
                        },
                    ],
                    'thumbnails': [
                        {
                            'url': (
                                'https://testing.eda.tst.yandex.net/images/'
                                '1368744/9d2253f1d40f86ff4e525e998f49dfca-8'
                                '0x80.jpeg'
                            ),
                        },
                    ],
                },
                'id': '1234595',
                'revision': (
                    'MS4xNjI4NDI0MDAwMDAwLlJjc0JNeUN4UDl4bDcybjFYeWQzOWc'
                ),
            },
            'queue': 'restapp_moderation_item',
            'scope': 'eda',
        }
    )

    db_data = pg_get_revisions()
    assert len(db_data) == 4
    assert (
        db_data[0]['revision']
        == 'MS4xNjA5NDU5MjAwMDAwLlFEcURLUjlERm15bEN2bGtSQVBLUXc'
        and db_data[0]['origin'] == 'external'
        and db_data[0]['status'] == 'not_applicable'
    )
    assert (
        db_data[1]['revision']
        == 'MS4xNjI4NDI0MDAwMDAwLlJjc0JNeUN4UDl4bDcybjFYeWQzOWc'
        and db_data[1]['origin'] == 'derived'
        and db_data[1]['status'] == 'updating'
    )
    assert (
        db_data[2]['revision'] == MENU_REVISION
        and db_data[2]['origin'] == 'external'
        and db_data[2]['status'] == 'not_applicable'
    )
    assert (
        db_data[3]['revision'] == MENU_REVISION_FOR_MERGE
        and db_data[3]['origin'] == 'user_generated'
        and db_data[3]['status'] == 'updating'
    )
