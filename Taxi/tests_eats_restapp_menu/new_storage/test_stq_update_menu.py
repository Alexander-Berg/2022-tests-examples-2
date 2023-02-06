import pytest


PLACE_ID = '109151'
MENU_REVISION = 'Mi4y'
MENU_REVISION_STQ = 'Mi40'
MENU_REVISION_WITH_VALIDATION = 'Mi41'
UPDATE_JOB_ID = '86fde2da-3c74-4408-909c-985a8b3c3bc1'


@pytest.mark.experiments3(filename='transitional_settings.json')
@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.parametrize(
    (
        'merge_called',
        'result_revision',
        'sent_menu',
        'validations_count',
        'merged_id',
        'db_state_file',
        'moderation_called',
    ),
    [
        pytest.param(
            1,
            MENU_REVISION_STQ,
            'sent_menu.json',
            0,
            2,
            'db_state1.json',
            0,
            id='merging config',
        ),
        pytest.param(
            1,
            MENU_REVISION_WITH_VALIDATION,
            'sent_menu_validation.json',
            1,
            3,
            'db_state2.json',
            2,
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_MENU_VALIDATION={'enabled': True},
                ),
                pytest.mark.experiments3(
                    filename='moderation_settings_no_images.json',
                ),
            ],
            id='merging and validation config',
        ),
    ],
)
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
async def test_ns_stq_update_menu_success(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        load_json,
        testpoint,
        merge_called,
        result_revision,
        sent_menu,
        validations_count,
        db_state_file,
        merged_id,
        pg_get_items,
        pg_get_categories,
        pg_get_menus,
        mock_eats_catalog_storage,
        moderation_called,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        expected = load_json(sent_menu)
        req_json = request.json
        req_json['categories'] = sorted(
            req_json['categories'], key=lambda x: x['id'],
        )
        req_json['items'] = sorted(req_json['items'], key=lambda x: x['id'])
        del req_json['lastChange']
        assert request.query['place_id'] == PLACE_ID
        assert req_json == expected
        return {'jobId': UPDATE_JOB_ID, 'isNewJob': True}

    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data_empty.json')

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def mock_place_menu_new(request):
        return load_json('base_data_empty.json')

    @mockserver.json_handler(
        f'/eats-core-restapp/v1/eats-restapp-menu/validate',
    )
    def mock_validate_menu(request):
        return load_json('validated_menu.json')

    @testpoint('MergeMenuNew')
    def merge_menu(arg):
        assert arg == {'menu_id': merged_id, 'base_id': 1}

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION,
        kwargs={'place_id': int(PLACE_ID), 'revision': MENU_REVISION},
        expect_fail=False,
    )

    assert mock_validate_menu.times_called == validations_count
    assert merge_called in (
        mock_place_menu.times_called,
        mock_place_menu_new.times_called,
    )
    assert (
        stq.eats_restapp_menu_moderate_menu.times_called == moderation_called
    )
    assert core_menu_update.times_called == 1
    assert merge_menu.times_called == merge_called
    assert stq.eats_restapp_menu_update_menu_status.times_called == 1

    stq_args = stq.eats_restapp_menu_update_menu_status.next_call()['kwargs']
    del stq_args['log_extra']
    assert stq_args == {
        'place_id': int(PLACE_ID),
        'revision': result_revision,
        'job_id': UPDATE_JOB_ID,
    }

    assert len(pg_get_revisions()) == 2

    db_data = load_json(db_state_file)

    dic = {}
    dic['items'] = pg_get_items()
    dic['categories'] = pg_get_categories()
    dic['menus'] = [
        [
            it['id'],
            it['base_id'],
            it['place_id'],
            it['author_id'],
            it['categories_hash'],
            it['items_hash'],
            it['origin'],
            it['status'],
            it['errors_json'],
            it['sent_external'],
        ]
        for it in pg_get_menus()
    ]

    assert dic == db_data


@pytest.mark.experiments3(filename='transitional_settings.json')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_restapp_menu_erms_integration',
    consumers=['eats-restapp-menu/transitional_settings'],
    clauses=[],
    default_value={'update_enabled': True, 'get_enabled': True},
    is_config=True,
)
@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.parametrize(
    (
        'merge_called',
        'result_revision',
        'sent_menu',
        'sent_menu_erms',
        'validations_count',
        'merged_id',
        'db_state_file',
        'moderation_called',
    ),
    [
        pytest.param(
            1,
            MENU_REVISION_STQ,
            'sent_menu.json',
            'sent_menu_erms.json',
            0,
            2,
            'db_state1.json',
            0,
            id='merging config',
        ),
        pytest.param(
            1,
            MENU_REVISION_WITH_VALIDATION,
            'sent_menu_validation.json',
            'sent_menu_validation_erms.json',
            1,
            3,
            'db_state2.json',
            2,
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_MENU_VALIDATION={'enabled': True},
                ),
                pytest.mark.experiments3(
                    filename='moderation_settings_no_images.json',
                ),
            ],
            id='merging and validation config',
        ),
    ],
)
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
async def test_ns_stq_update_menu_erms_success(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        load_json,
        testpoint,
        merge_called,
        result_revision,
        sent_menu,
        sent_menu_erms,
        validations_count,
        db_state_file,
        merged_id,
        pg_get_items,
        pg_get_categories,
        pg_get_menus,
        mock_eats_catalog_storage,
        moderation_called,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        expected = load_json(sent_menu)
        req_json = request.json
        req_json['categories'] = sorted(
            req_json['categories'], key=lambda x: x['id'],
        )
        req_json['items'] = sorted(req_json['items'], key=lambda x: x['id'])
        del req_json['lastChange']
        assert request.query['place_id'] == PLACE_ID
        assert req_json == expected
        return {'jobId': UPDATE_JOB_ID, 'isNewJob': True}

    @mockserver.json_handler('/eats-rest-menu-storage/internal/v1/update/menu')
    def erms_menu_update(request):
        expected = load_json(sent_menu_erms)
        req_json = request.json
        req_json['categories'] = sorted(
            req_json['categories'], key=lambda x: x['origin_id'],
        )
        req_json['items'] = sorted(
            req_json['items'], key=lambda x: x['origin_id'],
        )
        assert req_json == expected
        return {}

    @mockserver.json_handler('/eats-rest-menu-storage/internal/v1/menu')
    def mock_place_menu(request):
        return load_json('base_data_empty.json')

    @mockserver.json_handler(
        f'/eats-core-restapp/v1/eats-restapp-menu/validate',
    )
    def mock_validate_menu(request):
        return load_json('validated_menu.json')

    @testpoint('MergeMenuNew')
    def merge_menu(arg):
        assert arg == {'menu_id': merged_id, 'base_id': 1}

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION,
        kwargs={'place_id': int(PLACE_ID), 'revision': MENU_REVISION},
        expect_fail=False,
    )

    assert mock_validate_menu.times_called == validations_count
    assert merge_called == mock_place_menu.times_called
    assert (
        stq.eats_restapp_menu_moderate_menu.times_called == moderation_called
    )
    assert core_menu_update.times_called == 1
    assert erms_menu_update.times_called == 1
    assert merge_menu.times_called == merge_called
    assert stq.eats_restapp_menu_update_menu_status.times_called == 1

    stq_args = stq.eats_restapp_menu_update_menu_status.next_call()['kwargs']
    del stq_args['log_extra']
    assert stq_args == {
        'place_id': int(PLACE_ID),
        'revision': result_revision,
        'job_id': UPDATE_JOB_ID,
    }

    assert len(pg_get_revisions()) == 2

    db_data = load_json(db_state_file)

    dic = {}
    dic['items'] = pg_get_items()
    dic['categories'] = pg_get_categories()
    dic['menus'] = [
        [
            it['id'],
            it['base_id'],
            it['place_id'],
            it['author_id'],
            it['categories_hash'],
            it['items_hash'],
            it['origin'],
            it['status'],
            it['errors_json'],
            it['sent_external'],
        ]
        for it in pg_get_menus()
    ]

    assert dic == db_data
