import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
MENU_REVISION = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'
MENU_REVISION_STQ = 'MS4xNjI4NDI0MDAwMDAwLmdLMG5kbEFxNlFCSjFON2xoTmRwUFE'
MENU_REVISION_WITH_VALIDATION = (
    'MS4xNjI4NDI0MDAwMDAwLndIeHU2SWFZUkdldzVqdUxCYXlGcGc'
)
MENU_REVISION_FOR_MERGE = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFlu'
MENU_REVISION_DERIVED = 'MS4xNjI4NDI0MDAwMDAwLmlvbmtyU2pOd0hWVmVjQjhBd1RBR0E'
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
        'moderation_called',
    ),
    [
        pytest.param(
            0,
            MENU_REVISION,
            2,
            'sent_menu.json',
            0,
            MENU_REVISION,
            0,
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_MENU_UPDATE_METHOD={
                        'use_merging': False,
                        'use_incremental_update': False,
                    },
                ),
            ],
            id='no merging config',
        ),
        pytest.param(
            1,
            MENU_REVISION_STQ,
            4,
            'sent_menu.json',
            0,
            MENU_REVISION,
            0,
            id='merging config',
        ),
        pytest.param(
            1,
            MENU_REVISION_WITH_VALIDATION,
            4,
            'sent_menu_validation.json',
            1,
            MENU_REVISION_WITH_VALIDATION,
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
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_stq_update_menu_success(
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
        moderation_called,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        expected = load_json(sent_menu)
        req_json = request.json
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

    db_data = pg_get_revisions()
    assert len(db_data) == revisions_count


@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_stq_update_menu_error(
        stq_runner, mockserver, stq, load_json, mock_eats_catalog_storage,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'statusCode': 400,
                'type': 'bad_request',
                'errors': [
                    {
                        'message': (
                            'No result was found '
                            'for query although at least one row was expected.'
                        ),
                    },
                ],
                'context': '',
            },
        )

    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data_empty.json')

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION,
        kwargs={'place_id': int(PLACE_ID), 'revision': MENU_REVISION},
        expect_fail=True,
    )

    assert core_menu_update.times_called == 1
    assert stq.eats_restapp_menu_update_menu_status.times_called == 0
    assert mock_place_menu.times_called == 1


async def test_stq_update_menu_no_data(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        mock_eats_catalog_storage,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        return {
            'jobId': '86fde2da-3c74-4408-909c-985a8b3c3bc1',
            'isNewJob': True,
        }

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION,
        kwargs={'place_id': int(PLACE_ID), 'revision': MENU_REVISION},
        expect_fail=False,
    )

    assert core_menu_update.times_called == 0
    assert stq.eats_restapp_menu_update_menu_status.times_called == 0


@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_stq_update_core_fail(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        taxi_config,
        load_json,
        mock_eats_catalog_storage,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def core_menu_update(request):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'statusCode': 400,
                'type': 'some_error',
                'errors': [],
                'context': 'Some unknown error',
            },
        )

    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data_empty.json')

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION,
        kwargs={'place_id': int(PLACE_ID), 'revision': MENU_REVISION},
        expect_fail=True,
    )

    assert mock_place_menu.times_called == 1
    assert core_menu_update.times_called == 1
    assert stq.eats_restapp_menu_update_menu_status.times_called == 0

    db_data = pg_get_revisions()
    assert len(db_data) == 4

    # emulate last retry
    retries = taxi_config.get('EATS_RESTAPP_MENU_MENU_UPDATE_RETRIES')[
        'retries_limit'
    ]

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION,
        kwargs={'place_id': int(PLACE_ID), 'revision': MENU_REVISION},
        expect_fail=False,
        exec_tries=retries + 1,
    )

    assert core_menu_update.times_called == 1
    assert stq.eats_restapp_menu_update_menu_status.times_called == 0

    db_data = pg_get_revisions()
    assert len(db_data) == 4


@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data_merging.sql',))
async def test_stq_update_menu_success_merging(
        stq_runner, mockserver, stq, pg_get_revisions, load_json, testpoint,
):
    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
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
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data_conflict.sql',))
async def test_stq_update_menu_success_conflict(
        stq_runner, mockserver, stq, pg_get_revisions, load_json, testpoint,
):
    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
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

    db_data = pg_get_revisions()
    assert len(db_data) == 4


@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
    EATS_RESTAPP_MENU_SEND_STOP_MENU_ITEMS_SETTINGS={'enabled': True},
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data_merging.sql',))
async def test_stq_send_notification_about_new_stoped_items(
        stq_runner, mockserver, stq, pg_get_revisions, load_json, testpoint,
):
    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def _core_menu_get(request):
        return load_json('base_data_merging.json')

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def _core_menu_update(request):
        expected = load_json('sent_menu_merging.json')
        req_json = request.json
        req_json['lastChange'] = expected['lastChange']
        return {'jobId': UPDATE_JOB_ID, 'isNewJob': True}

    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications(request):
        assert request.json == {
            'recipients': {'place_ids': [109151]},
            'data': {'stoped_items': ['1234595']},
            'event_mode': 'delayed',
            'idempotency_token': 'stop-menu-items-109151',
        }
        return mockserver.make_response(status=204)

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION_FOR_MERGE,
        kwargs={
            'place_id': int(PLACE_ID),
            'revision': MENU_REVISION_FOR_MERGE,
        },
        expect_fail=False,
    )

    assert _mock_communications.times_called == 1


@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
    EATS_RESTAPP_MENU_SEND_STOP_MENU_ITEMS_SETTINGS={'enabled': True},
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data_merging.sql',))
async def test_stq_is_success_if_communications_return_error(
        stq_runner, mockserver, stq, pg_get_revisions, load_json, testpoint,
):
    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def _core_menu_get(request):
        return load_json('base_data_merging.json')

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/add-parsing-job',
    )
    def _core_menu_update(request):
        expected = load_json('sent_menu_merging.json')
        req_json = request.json
        req_json['lastChange'] = expected['lastChange']
        return {'jobId': UPDATE_JOB_ID, 'isNewJob': True}

    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'Some Error'},
        )

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION_FOR_MERGE,
        kwargs={
            'place_id': int(PLACE_ID),
            'revision': MENU_REVISION_FOR_MERGE,
        },
        expect_fail=False,
    )

    assert _mock_communications.times_called == 1
