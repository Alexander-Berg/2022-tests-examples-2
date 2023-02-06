import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
MENU_REVISION = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'
MENU_REVISION_STQ = 'MS4xNjI4NDI0MDAwMDAwLmJDb012aVBoQW1Db2hUUGhubmZxLXc'
UPDATE_JOB_ID = '86fde2da-3c74-4408-909c-985a8b3c3bc1'


@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.parametrize(
    (
        'merge_called',
        'merge_called_new',
        'result_revision',
        'revisions_count',
        'sent_menu',
        'moderation_called',
    ),
    [
        pytest.param(
            1,
            0,
            MENU_REVISION_STQ,
            4,
            'sent_menu_disabled.json',
            0,
            id='no image',
        ),
        pytest.param(
            1,
            0,
            MENU_REVISION_STQ,
            4,
            'sent_menu_image.json',
            0,
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
                        'url_prefix': (
                            'https://testing.eda.tst.yandex.net/images'
                        ),
                        'image_postfix': '.jpg',
                        'thumbnail_postfix': '-80x80.jpg',
                        'image_processing_enabled': True,
                    },
                ),
            ],
            id='image',
        ),
        pytest.param(
            0,
            1,
            MENU_REVISION_STQ,
            4,
            'sent_menu_enabled.json',
            3,
            marks=[
                pytest.mark.experiments3(
                    filename='moderation_flow_settings.json',
                ),
                pytest.mark.config(
                    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
                        'url_prefix': (
                            'https://testing.eda.tst.yandex.net/images'
                        ),
                        'image_postfix': '.jpg',
                        'thumbnail_postfix': '-80x80.jpg',
                        'image_processing_enabled': True,
                    },
                ),
            ],
            id='image + moderation',
        ),
    ],
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_images_enrichment_update(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        load_json,
        merge_called,
        merge_called_new,
        result_revision,
        revisions_count,
        sent_menu,
        mock_eats_catalog_storage,
        moderation_called,
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
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data.json')

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def mock_place_menu_new(request):
        return load_json('base_data.json')

    await stq_runner.eats_restapp_menu_update_menu.call(
        task_id=MENU_REVISION,
        kwargs={'place_id': int(PLACE_ID), 'revision': MENU_REVISION},
        expect_fail=False,
    )

    assert mock_place_menu.times_called == merge_called
    assert mock_place_menu_new.times_called == merge_called_new
    assert core_menu_update.times_called == 1
    assert stq.eats_restapp_menu_update_menu_status.times_called == 1
    assert (
        stq.eats_restapp_menu_moderate_menu.times_called == moderation_called
    )

    db_data = pg_get_revisions()
    assert len(db_data) == revisions_count
