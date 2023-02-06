import json

import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
MENU_REVISION = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'
MENU_REVISION_BASE = 'base_revision_hash'
MENU_REVISION_FOR_MERGE = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFlu'
MENU_REVISION_DERIVED = 'MS4xNjI4NDI0MDAwMDAwLmg1M3VsNjRHQ3htSm1YTnRKbmVpR0E'
MENU_REVISION_NEW_BASE = 'MS4xNjA5NDU5MjAwMDAwLlVqZ2tIS3h1d1FsNWRyV3JLSV9vUUE'
UPDATE_JOB_ID = '86fde2da-3c74-4408-909c-985a8b3c3bc1'


@pytest.mark.parametrize(
    ('sent_request', 'base_data', 'moderation_tasks_count', 'moderation_file'),
    [
        pytest.param(
            'sent_request_same.json',
            'base_data_same.json',
            0,
            None,
            marks=[
                pytest.mark.pgsql(
                    'eats_restapp_menu', files=('fill_data_same.sql',),
                ),
            ],
            id='no changes',
        ),
        pytest.param(
            'sent_request_changed.json',
            'base_data_changed.json',
            4,
            'moderation_params.json',
            marks=[
                pytest.mark.pgsql(
                    'eats_restapp_menu', files=('fill_data_changed.sql',),
                ),
            ],
            id='with changes',
        ),
    ],
)
@pytest.mark.now('2021-08-08T12:00:00Z')
@pytest.mark.experiments3(filename='moderation_flow_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_MENU_UPDATE_METHOD={
        'use_merging': True,
        'use_incremental_update': True,
    },
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
async def test_stq_update_menu_incremental_success(
        stq_runner,
        mockserver,
        stq,
        pg_get_revisions,
        load_json,
        testpoint,
        sent_request,
        base_data,
        moderation_tasks_count,
        moderation_file,
        mock_eats_catalog_storage,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/submit-changes',
    )
    def core_menu_update(request):
        assert request.query['place_id'] == PLACE_ID
        assert request.json == load_json(sent_request)
        return mockserver.make_response(status=204, json={})

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def core_menu_get(request):
        return load_json(base_data)

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

    assert core_menu_get.times_called == 1
    assert core_menu_update.times_called == 1
    assert merge_menu.times_called == 1
    assert stq.eats_restapp_menu_update_menu_status.times_called == 0
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
        if 'modified_value' in req_data['payload']:
            req_data['payload']['modified_value'] = json.loads(
                req_data['payload']['modified_value'],
            )
        assert {
            'context': req_data['context'],
            'payload': req_data['payload'],
            'queue': req_data['queue'],
            'scope': req_data['scope'],
        } == expected[i]

    db_data = pg_get_revisions()
    assert len(db_data) == 4
