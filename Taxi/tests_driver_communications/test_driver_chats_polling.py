import pytest

from tests_driver_communications import utils


@pytest.mark.parametrize(
    'preloaded_feeds, preloaded_feeds_fs, new_msg, new_fs, last_msg_id',
    [
        ([], [], 0, 0, None),
        (
            ['text_feed', 'text_title_feed_viewed'],
            [],
            2,
            0,
            'f6dc672653aa443d9ecf48cc5ef4cb6d',
        ),
        (
            ['text_feed', 'text_title_feed_read'],
            [],
            1,
            0,
            'f6dc672653aa443d9ecf48cc5ef4cb6d',
        ),
        (
            ['text_feed'],
            ['fullscreen_feed'],
            2,
            1,
            'f6dc672653aa443d9ecf48cc5ef4cb6d',
        ),
        (
            ['text_feed_read'],
            ['fullscreen_read_feed'],
            0,
            0,
            'f6dc672653aa443d9ecf48cc5ef4cb6k',
        ),
        (['text_reply'], [], 0, 0, 'f6dc672653aa443d9ecf48cc5ef4cbee'),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['feeds/fullscreens']}},
    },
)
async def test_driver_chats_polling_v2_v3(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        preloaded_feeds,
        preloaded_feeds_fs,
        new_msg,
        new_fs,
        last_msg_id,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(preloaded_feeds)
    mock_feeds.set_feeds(preloaded_feeds_fs, 'fullscreens')
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chats_2_services.json'),
    )
    chat = utils.get_chat(last_polling_time='2020-05-01T11:50:15.277047+0000')
    response = await utils.chats_polling_v2(
        taxi_driver_communications, body=utils.get_chats_request(chats=[chat]),
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['chats']) == 1
    news_chat = response_json['chats'][0]
    assert news_chat['chat_meta']['chat_id'] == 'news'
    assert 'last_polling_time' in news_chat['chat_meta']
    assert news_chat['chat_meta']['chat_sources'] == [
        {
            'channels': [
                'taximeter:City',
                'taximeter:Country',
                'taximeter:Driver',
                'taximeter:Park',
            ],
            'content_sources': ['driver-wall'],
            'source_service': 'feeds',
            'etag': '',
        },
        {
            'channels': [
                'taximeter:City',
                'taximeter:Country',
                'taximeter:Driver',
                'taximeter:Park',
            ],
            'content_sources': ['fullscreens'],
            'source_service': 'feeds',
            'etag': '',
        },
    ]
    assert news_chat['chat_name'] == 'Новости'
    assert news_chat['icon_url'] == 'some_url'
    updates = news_chat['updates']
    assert updates['fullscreen_count'] == new_fs
    assert updates['new_msg_count'] == new_msg
    if last_msg_id is not None:
        assert updates['last_msg']['id'] == last_msg_id
    assert response.headers['X-Polling-Delay'] == '300'

    chat = utils.get_chat_v2(
        last_polling_time='2020-05-01T11:50:15.277047+0000',
    )
    response = await utils.chats_polling_v3(
        taxi_driver_communications, body=utils.get_chats_request(chats=[chat]),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['chats']) == 1
    news_chat = response_json['chats'][0]
    assert news_chat['chat_meta']['id'] == 'news'
    assert 'last_polling_time' in news_chat['chat_meta']
    assert news_chat['chat_meta']['chat_sources'] == [
        {'id': 'feeds/wall', 'etag': ''},
        {'id': 'feeds/fullscreens', 'etag': ''},
    ]
    assert news_chat['chat_name'] == 'Новости'
    assert news_chat['icon_url'] == 'some_url'
    updates = news_chat['updates']
    assert updates['fullscreen_count'] == new_fs
    assert updates['new_msg_count'] == new_msg
    if last_msg_id is not None:
        assert updates['last_msg']['id'] == last_msg_id
    assert response.headers['X-Polling-Delay'] == '300'


async def test_chats_polling_chat_name(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    request_json = load_json('chat_settings_one_chats_2_services.json')
    request_json['configs'][0]['default_value']['chat_settings'][0][
        'title'
    ] = 'driver_communications.taxi_company_mailing'
    experiments3.add_experiments_json(request_json)

    mock_feeds.set_feeds([])
    mock_feeds.set_feeds([], 'fullscreens')

    response = await utils.chats_polling_v2(
        taxi_driver_communications,
        body=utils.get_chats_request(chats=[utils.get_chat()]),
    )
    assert (
        response.json()['chats'][0]['chat_name']
        == 'Рассылка таксопарка "Тестовый Парк"'
    )


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {
            'news': {
                'content_sources': [
                    'feeds/fullscreens1',
                    'feeds/fullscreens2',
                ],
            },
        },
    },
)
async def test_driver_chats_polling_v2_priority(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(['fullscreen_feed'], 'fullscreens')
    experiments3.add_experiments_json(
        load_json('chat_settings_different_priorities.json'),
    )
    response = await utils.chats_polling_v2(
        taxi_driver_communications, body=utils.get_chats_request(chats=[]),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['chats']) == 4
    assert response_json['chats'][0]['chat_meta']['chat_id'] == 'chat_id4'
    assert response_json['chats'][1]['chat_meta']['chat_id'] == 'chat_id3'
    assert response_json['chats'][2]['chat_meta']['chat_id'] == 'chat_id2'
    assert response_json['chats'][3]['chat_meta']['chat_id'] == 'chat_id1'


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {
            'news': {
                'content_sources': [
                    'feeds/fullscreens1',
                    'feeds/fullscreens2',
                ],
            },
        },
    },
    DRIVER_COMMUNICATIONS_POLLING_DELAYS={
        '__default__': {
            '__default__': {
                'chat_id1': 240,
                'chat_id2': 120,
                'chat_id3': 60,
                '__default__': 300,
            },
        },
    },
)
@pytest.mark.now('2020-11-30T00:00:00+00:00')
async def test_driver_chats_polling_v2_config(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(['text_feed', 'text_title_feed_viewed'])
    mock_feeds.set_feeds(['fullscreen_feed'], 'fullscreens')
    experiments3.add_experiments_json(
        load_json('chat_settings_different_priorities.json'),
    )
    chats = []
    for chat_id in ['chat_id1', 'chat_id2', 'chat_id3', 'chat_id4']:
        chats.append(
            utils.get_chat(
                chat_id=chat_id,
                last_polling_time='2020-11-29T23:57:30.277047+0000',
            ),
        )
    response = await utils.chats_polling_v2(
        taxi_driver_communications,
        body=utils.get_chats_request(chats=chats, force_updates=['chat_id1']),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['chats']) == 4
    for chat in response_json['chats']:
        if (
                chat['chat_meta']['chat_id'] == 'chat_id1'
                or chat['chat_meta']['chat_id'] == 'chat_id2'
                or chat['chat_meta']['chat_id'] == 'chat_id3'
        ):
            assert 'updates' in chat
            assert (
                chat['chat_meta']['last_polling_time']
                == '2020-11-30T00:00:00+00:00'
            )
        else:
            assert 'updates' not in chat
            assert (
                chat['chat_meta']['last_polling_time']
                == '2020-11-29T23:57:30.277047+00:00'
            )
    assert response.headers['X-Polling-Delay'] == '60'


@pytest.mark.now('2020-11-30T00:00:00+00:00')
async def test_driver_chats_polling_v2_error(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(['text_feed', 'text_title_feed_viewed'])
    mock_feeds.set_feeds(['fullscreen_feed'], 'fullscreens')
    experiments3.add_experiments_json(
        load_json('chat_settings_different_priorities.json'),
    )
    mock_feeds.set_error(handler='v1/summary')
    chats = []
    for chat_id in ['chat_id1', 'chat_id2', 'chat_id3', 'chat_id4']:
        chats.append(
            utils.get_chat(
                chat_id=chat_id,
                last_polling_time='2020-11-29T23:57:30.277047+0000',
            ),
        )
    response = await utils.chats_polling_v2(
        taxi_driver_communications, body=utils.get_chats_request(chats=chats),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['chats']) == 4
    for chat in response_json['chats']:
        assert 'updates' not in chat
        assert (
            chat['chat_meta']['last_polling_time']
            == '2020-11-29T23:57:30.277047+00:00'
        )


@pytest.mark.parametrize(
    'sc_response,sc_code,last_polling_time,'
    'unique_driver_id,expected_code,expected_file',
    [
        (
            'support_chat_search_reply_error.json',
            500,
            '2019-11-29T23:57:30.277047+0000',
            'unique_driver_id1',
            200,
            'chat_support_polling_resp_empty_error.json',
        ),
        (
            'support_chat_search_reply_empty_chat.json',
            200,
            '2019-11-29T23:57:30.277047+0000',
            'unique_driver_id1',
            200,
            'chat_support_polling_resp_empty.json',
        ),
        (
            'support_chat_search_reply_no_chats.json',
            200,
            '2019-11-29T23:57:30.277047+0000',
            'unique_driver_id1',
            200,
            'chat_support_polling_resp_empty.json',
        ),
        (
            'support_chat_search_reply.json',
            200,
            '2019-11-29T23:57:30.277047+0000',
            'unique_driver_id1',
            200,
            'chat_support_polling_resp.json',
        ),
        (
            'support_chat_search_reply.json',
            200,
            '2020-12-28T06:30:00.277047+0000',
            'unique_driver_id1',
            200,
            'chat_support_polling_resp_last_polling.json',
        ),
        (
            'support_chat_search_reply.json',
            200,
            '2019-11-29T23:57:30.277047+0000',
            None,
            200,
            'chat_support_polling_resp_empty_error.json',
        ),
    ],
)
@pytest.mark.now('2020-12-28T06:35:00+0000')
async def test_driver_chats_polling_v2_support_chat(
        taxi_driver_communications,
        mock_support_chat,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        sc_response,
        sc_code,
        last_polling_time,
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
    request_source = utils.get_support_meta()
    request_source['etag'] = ''
    request_source['content_sources'] = []
    chats = [
        utils.get_chat(
            chat_id='support_chat',
            last_polling_time=last_polling_time,
            chat_sources=[request_source],
        ),
    ]
    response = await utils.chats_polling_v2(
        taxi_driver_communications, body=utils.get_chats_request(chats=chats),
    )
    assert response.status_code == expected_code
    assert response.json() == load_json(expected_file)


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['feeds/fullscreens']}},
    },
)
@pytest.mark.now('2020-11-30T00:00:00+00:00')
async def test_fullscreens_with_no_show_in_chat(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(['text_title_image_feed'])
    mock_feeds.set_feeds(
        ['fullscreen_feed', 'fullscreen_2_feed'], 'fullscreens',
    )
    experiments3.add_experiments_json(
        load_json('chat_settings_fs_show_in_chat.json'),
    )
    chat = utils.get_chat(last_polling_time='2020-05-01T11:50:15.277047+0000')
    response = await utils.chats_polling_v2(
        taxi_driver_communications, body=utils.get_chats_request(chats=[chat]),
    )
    assert response.status_code == 200
    assert response.json()['chats'][0]['updates']['fullscreen_count'] == 2
    assert response.json()['chats'][0]['updates']['new_msg_count'] == 0
