import pytest

from tests_driver_communications import utils


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {
            'news': {'content_sources': ['feeds/contractor/fullscreens']},
        },
    },
)
@pytest.mark.experiments3(filename='chats_with_thematic_settings.json')
@pytest.mark.now('2021-07-01T12:35:00+0000')
async def test_driver_v3_polling(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(['text_feed', 'text_dsat', 'fullscreen_3_feed'])
    mock_feeds.set_feeds(
        ['fullscreen_3_feed', 'fullscreen_4_feed'], 'contractor-fullscreen',
    )
    mock_feeds.set_feeds(
        ['text_title_feed', 'fullscreen_4_feed'], 'contractor-money',
    )

    chats = [
        utils.get_chat_v2('orders'),
        utils.get_chat_v2('promo'),
        utils.get_chat_v2('news'),
        utils.get_chat_v2('bonuses'),
    ]
    response = await utils.chats_polling_v3(
        taxi_driver_communications, body=utils.get_chats_request(chats=chats),
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json == load_json('response/multi_thematic_chats.json')


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {
            'news': {'content_sources': ['feeds/contractor/fullscreens']},
        },
    },
)
@pytest.mark.experiments3(filename='config_with_tags_clause.json')
@pytest.mark.now('2021-07-01T12:35:00+0000')
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            'response/multi_thematic_chats.json',
            marks=pytest.mark.driver_tags_match(
                dbid='db1', uuid='uuid1', tags=[],
            ),
        ),
        pytest.param(
            'response/chats_with_tag.json',
            marks=pytest.mark.driver_tags_match(
                dbid='db1', uuid='uuid1', tags=['contractor_marketplace'],
            ),
        ),
    ],
)
async def test_driver_v3_polling_tags_in_kwargs(
        taxi_driver_communications,
        mockserver,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        expected_response,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_feeds(['text_feed', 'text_dsat', 'fullscreen_3_feed'])
    mock_feeds.set_feeds(
        ['fullscreen_3_feed', 'fullscreen_4_feed'], 'contractor-fullscreen',
    )
    mock_feeds.set_feeds(
        ['text_title_feed', 'fullscreen_4_feed'], 'contractor-money',
    )
    chats = [
        utils.get_chat_v2('orders'),
        utils.get_chat_v2('promo'),
        utils.get_chat_v2('news'),
        utils.get_chat_v2('bonuses'),
    ]
    response = await utils.chats_polling_v3(
        taxi_driver_communications, body=utils.get_chats_request(chats=chats),
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json == load_json(expected_response)
