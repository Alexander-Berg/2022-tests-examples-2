import pytest

from tests_driver_communications import utils


@pytest.mark.parametrize(
    'request_json, chat_settings',
    [
        # no config found
        (
            utils.get_chats_request(
                driver_info=utils.get_driver_info(position=None),
                chats=[utils.get_chat(chat_sources=None)],
            ),
            None,
        ),
        # no info from taximeter, but has config
        (
            utils.get_chats_request(
                driver_info=utils.get_driver_info(position=None),
                chats=[utils.get_chat(chat_sources=None)],
            ),
            'chat_settings_one_chat_with_feeds.json',
        ),
        # not existing channel in config (fail to personalize)
        (
            utils.get_chats_request(
                driver_info=utils.get_driver_info(),
                chats=[utils.get_chat(chat_sources=None)],
            ),
            'chat_settings_not_existing_channel.json',
        ),
        # not existing content source in config (fail request to feeds)
        (
            utils.get_chats_request(
                driver_info=utils.get_driver_info(),
                chats=[utils.get_chat(chat_sources=None)],
            ),
            'chat_settings_not_existing_content_source.json',
        ),
        # not existing service in config (fail to find personalizer)
        (
            utils.get_chats_request(
                driver_info=utils.get_driver_info(),
                chats=[utils.get_chat(chat_sources=None)],
            ),
            'chat_settings_not_existing_service.json',
        ),
        # have two chats, both empty
        (
            utils.get_chats_request(
                driver_info=utils.get_driver_info(),
                chats=[utils.get_chat(chat_sources=None)],
            ),
            'chat_settings_two_chats_with_feeds.json',
        ),
        (
            utils.get_chats_request(
                driver_info=utils.get_driver_info(), chats=[],
            ),
            'chat_settings_one_chat_with_feeds.json',
        ),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['feeds/wall']}},
    },
)
async def test_fullscreens_nothing_changed_in_feeds(
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

    response = await utils.get_fullscreens(
        taxi_driver_communications, body=request_json,
    )

    assert response.status_code == 304


@pytest.mark.parametrize(
    'preloaded_feeds,preloaded_feeds_fs,response_file',
    [
        (['text_feed', 'text_title_feed'], [], 'one_chat_2_new_messages.json'),
        (
            ['text_title_image_feed'],
            ['fullscreen_feed'],
            'one_chat_one_fullscreen.json',
        ),
        (
            ['text_title_image_feed'],
            ['fullscreen_read_feed'],
            'one_chat_one_read_fullscreen.json',
        ),
        (
            ['text_title_image_feed'],
            ['fullscreen_viewed_feed'],
            'one_chat_one_viewed_fullscreen.json',
        ),
        (
            ['text_title_image_feed'],
            ['fullscreen_feed', 'fullscreen_2_feed'],
            'two_fullscreens.json',
        ),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['feeds/fullscreens']}},
    },
)
@pytest.mark.now('2020-11-30T00:00:00+00:00')
async def test_fullscreens_different_feeds_first_request(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        preloaded_feeds,
        preloaded_feeds_fs,
        response_file,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(preloaded_feeds)
    mock_feeds.set_feeds(preloaded_feeds_fs, 'fullscreens')
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chats_2_services.json'),
    )

    response = await utils.get_fullscreens(
        taxi_driver_communications,
        body=utils.get_chats_request(
            chats=[utils.get_chat(chat_sources=None)],
        ),
    )

    assert response.status_code == 200
    assert response.json() == utils.get_fullscreen_chats(
        load_json(response_file),
    )


@pytest.mark.parametrize(
    'preloaded_feeds,response_file',
    [
        (
            ['text_title_image_feed', 'fullscreen_feed', 'fullscreen_2_feed'],
            'two_fullscreens.json',
        ),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['blabla']}},
    },
)
async def test_fullscreens_wrong_provider(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        preloaded_feeds,
        response_file,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(preloaded_feeds)
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chats_2_services.json'),
    )

    response = await utils.get_fullscreens(
        taxi_driver_communications,
        body=utils.get_chats_request(
            chats=[utils.get_chat(chat_sources=None)],
        ),
    )

    assert response.status_code == 304


@pytest.mark.parametrize(
    'preloaded_feeds,preloaded_feeds_fs,response_file,last_polling_time',
    [
        (
            ['text_title_image_feed'],
            ['fullscreen_feed', 'fullscreen_2_feed'],
            'two_fullscreens.json',
            '2020-04-01T11:50:15.277047+0000',
        ),
        (
            ['text_title_image_feed'],
            ['fullscreen_feed', 'fullscreen_2_feed'],
            None,
            '2020-12-01T11:50:15.277047+0000',
        ),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['feeds/fullscreens']}},
    },
)
@pytest.mark.now('2020-11-30T00:00:00+00:00')
async def test_fullscreens_with_last_polling_time(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        mocked_time,
        load_json,
        preloaded_feeds,
        preloaded_feeds_fs,
        response_file,
        last_polling_time,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(preloaded_feeds)
    mock_feeds.set_feeds(preloaded_feeds_fs, 'fullscreens')
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chats_2_services.json'),
    )

    response = await utils.get_fullscreens(
        taxi_driver_communications,
        body=utils.get_chats_request(
            chats=[
                utils.get_chat(
                    chat_sources=None, last_polling_time=last_polling_time,
                ),
            ],
        ),
    )
    assert response.status_code == 200
    if response_file is None:
        assert response.json() == {'chats': []}
        return
    assert response.json() == utils.get_fullscreen_chats(
        load_json(response_file),
    )
