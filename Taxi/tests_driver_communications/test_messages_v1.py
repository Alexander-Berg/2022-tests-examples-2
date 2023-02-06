import pytest

from tests_driver_communications import utils


@pytest.mark.parametrize(
    'request_json, chat_settings',
    [
        # no info from taximeter, but has config
        (
            utils.get_paging_request(
                driver_info=utils.get_driver_info(position=None),
                chat_meta=None,
            ),
            'chat_settings_one_chat_with_feeds.json',
        ),
        # not existing channel in config (fail to personalize)
        (
            utils.get_paging_request(
                driver_info=utils.get_driver_info(), chat_meta=None,
            ),
            'chat_settings_not_existing_channel.json',
        ),
        # not existing content source in config (fail request to feeds)
        (
            utils.get_paging_request(
                driver_info=utils.get_driver_info(), chat_meta=None,
            ),
            'chat_settings_not_existing_content_source.json',
        ),
        # not existing service in config (fail to find personalizer)
        (
            utils.get_paging_request(
                driver_info=utils.get_driver_info(), chat_meta=None,
            ),
            'chat_settings_not_existing_service.json',
        ),
        # recieved ok source
        (utils.get_paging_request(), 'chat_settings_one_chat_with_feeds.json'),
    ],
)
async def test_messages_nothing_changed_in_feeds(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        request_json,
        chat_settings,
        unique_drivers,
        mock_driver_trackstory,
):
    unique_drivers.add_driver(
        utils.PARK_ID, utils.PROFILE_ID, utils.UNIQUE_DRIVER_ID,
    )
    mock_feeds.set_response({}, 304, handler='v1/fetch')
    if chat_settings is not None:
        experiments3.add_experiments_json(load_json(chat_settings))

    response = await utils.get_messages_paging(
        taxi_driver_communications, body=request_json,
    )

    assert response.status_code == 304


async def test_messages_no_config(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    unique_drivers.add_driver(
        utils.PARK_ID, utils.PROFILE_ID, utils.UNIQUE_DRIVER_ID,
    )
    mock_feeds.set_response({}, 304, handler='v1/fetch')
    response = await utils.get_messages_paging(
        taxi_driver_communications,
        body=utils.get_paging_request(
            driver_info=utils.get_driver_info(position=None), chat_meta=None,
        ),
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': 'INTERNAL_ERROR',
        'message': 'Failed to get config.',
    }


@pytest.mark.parametrize(
    'preloaded_feeds,preloaded_feeds_fs,response_file',
    [
        (
            ['text_feed', 'text_title_feed'],
            [],
            'one_chat_2_new_messages_2_feeds_services.json',
        ),
        (
            ['text_feed', 'text_title_feed_viewed'],
            [],
            'one_chat_2_new_messages_with_viewed.json',
        ),
        (
            ['text_feed', 'text_title_feed_read'],
            [],
            'one_chat_1_new_1_old.json',
        ),
        (
            ['text_feed_read', 'text_title_feed_read'],
            [],
            'one_chat_2_old_messages.json',
        ),
        (
            ['text_title_image_feed'],
            ['fullscreen_feed', 'very_old_msg'],
            'one_chat_one_fullscreen_2_feeds_services.json',
        ),
        (
            ['text_title_image_feed'],
            ['fullscreen_read_feed', 'very_old_msg'],
            'one_chat_one_read_fullscreen.json',
        ),
        (
            ['text_title_image_feed'],
            ['fullscreen_viewed_feed', 'very_old_msg'],
            'one_chat_one_viewed_fullscreen.json',
        ),
        (
            ['text_title_image_feed'],
            ['fullscreen_feed', 'fullscreen_2_feed', 'very_old_msg'],
            'two_fullscreens.json',
        ),
        (['text_title_image_feed', 'text_reply'], [], 'one_with_reply.json'),
        (
            ['text_title_image_feed', 'text_reply_on_deleted'],
            [],
            'one_with_reply_on_deleted.json',
        ),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['feeds/fullscreens']}},
    },
)
@pytest.mark.parametrize('limit', [1, 2, 1000])
async def test_messages_different_feeds(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        preloaded_feeds,
        preloaded_feeds_fs,
        response_file,
        limit,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(preloaded_feeds)
    mock_feeds.set_feeds(preloaded_feeds_fs, 'fullscreens')
    mock_feeds.set_limit(limit)
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chats_2_services.json'),
    )

    response = await utils.get_messages_paging(
        taxi_driver_communications, chat_id='news',
    )

    assert response.status_code == 200
    assert response.json() == load_json(response_file)['chats'][0]


@pytest.mark.parametrize(
    'sc_response,sc_code,unique_driver_id,expected_code,expected_file',
    [
        (
            'support_chat_search_reply_error.json',
            500,
            'unique_driver_id1',
            304,
            None,
        ),
        (
            'support_chat_search_reply_empty_chat.json',
            200,
            'unique_driver_id1',
            200,
            'chat_support_resp_empty.json',
        ),
        (
            'support_chat_search_reply_no_chats.json',
            200,
            'unique_driver_id1',
            200,
            'chat_support_resp_empty.json',
        ),
        (
            'support_chat_search_reply.json',
            200,
            'unique_driver_id1',
            200,
            'chat_support_resp.json',
        ),
        (
            'support_chat_search_reply_files.json',
            200,
            'unique_driver_id1',
            200,
            'chat_support_resp_files.json',
        ),
        ('support_chat_search_reply.json', 200, None, 304, None),
    ],
)
async def test_messages_support_chat(
        taxi_driver_communications,
        mock_support_chat,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        sc_response,
        sc_code,
        unique_driver_id,
        expected_code,
        expected_file,
        mock_driver_diagnostics,
):
    if unique_driver_id is not None:
        unique_drivers.add_driver('db1', 'uuid1', unique_driver_id)
    mock_support_chat.set_response(
        response=load_json(sc_response), code=sc_code,
    )
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    response = await utils.get_messages_paging(
        taxi_driver_communications, chat_id='support_chat',
    )
    assert response.status_code == expected_code
    if expected_code == 304:
        return
    expected_json = load_json(expected_file)
    response_json = response.json()
    expected_json['chat_meta']['chat_sources'][0]['etag'] = response_json[
        'chat_meta'
    ]['chat_sources'][0]['etag']
    assert response_json == expected_json


async def test_messages_feeds_metrics(
        taxi_driver_communications,
        taxi_driver_communications_monitor,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_response({}, 500, handler='v1/fetch')
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chats_2_services.json'),
    )
    await taxi_driver_communications.tests_control(reset_metrics=True)
    metrics = await taxi_driver_communications_monitor.get_metric(
        'feeds_source',
    )
    assert metrics == {'fetch_all_failed': 0, 'fetch_all_ok': 0}
    response = await utils.get_messages_paging(
        taxi_driver_communications, chat_id='news',
    )
    metrics = await taxi_driver_communications_monitor.get_metric(
        'feeds_source',
    )
    assert metrics == {'fetch_all_failed': 2, 'fetch_all_ok': 0}
    assert response.status_code == 304


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['feeds/fullscreens']}},
    },
)
async def test_messages_one_source_unchanged_and_empty(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(['text_title_image_feed', 'text_reply_on_deleted'])
    mock_feeds.set_feeds(['fullscreen_read_feed'], 'fullscreens')
    mock_feeds.set_limit(1)
    mock_feeds.set_response({}, 304, handler='v1/fetch', service='fullscreens')
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chats_2_services.json'),
    )

    response = await utils.get_messages_paging(
        taxi_driver_communications, chat_id='news',
    )

    assert response.status_code == 200
    expected_json = load_json('one_with_reply_on_deleted.json')['chats'][0]
    expected_json['chat_meta']['chat_sources'][1]['etag'] = ''
    assert response.json() == expected_json


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['feeds/fullscreens']}},
    },
)
async def test_messages_all_new_are_shown(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(['text_feed', 'text_title_feed'])
    mock_feeds.set_feeds(['fullscreen_viewed_feed'], 'fullscreens')
    mock_feeds.set_limit(1)
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chats_2_services.json'),
    )

    response = await utils.get_messages_paging(
        taxi_driver_communications, chat_id='news',
    )

    assert response.status_code == 200
    assert len(response.json()['messages']) == 3
