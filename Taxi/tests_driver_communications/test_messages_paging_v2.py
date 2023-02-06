import pytest

from tests_driver_communications import utils


@pytest.mark.parametrize(
    'request_json, chat_id, expected_status, expected_response',
    [
        (
            utils.get_paging_request(
                chat_meta=utils.get_chat_v2(),
                older_than='2020-06-09T12:40:15.277047+0000',
            ),
            'news',
            200,
            'paging_response_older_than.json',
        ),
        (
            utils.get_paging_request(
                chat_meta=utils.get_chat_v2(),
                newer_than='2020-06-09T12:50:15.277047+0000',
            ),
            'news',
            200,
            'paging_response_newer_than.json',
        ),
        (
            utils.get_paging_request(chat_meta=utils.get_chat_v2()),
            'news',
            200,
            'paging_response_no_time.json',
        ),
        (
            utils.get_paging_request(
                chat_meta=utils.get_chat_v2(),
                newer_than='2020-06-09T12:50:15.277047+0000',
            ),
            'news',
            304,
            'failed_to_load_history.json',
        ),
        (
            utils.get_paging_request(
                chat_meta=utils.get_chat_v2(),
                newer_than='2020-06-09T12:50:15.277047+0000',
            ),
            'bad_chat',
            400,
            'wrong_chat_id.json',
        ),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_PROVIDERS={
        'fullscreens': {'news': {'content_sources': ['feeds/fullscreens']}},
    },
)
async def test_messages_paging(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        request_json,
        chat_id,
        expected_status,
        expected_response,
        unique_drivers,
        mock_driver_trackstory,
):
    if expected_status == 200:
        mock_feeds.set_feeds(['text_feed', 'text_title_image_feed'])
        mock_feeds.set_feeds(
            ['fullscreen_read_feed', 'very_old_msg'], 'fullscreens',
        )
    else:
        mock_feeds.set_response({}, 304, handler='v1/fetch')
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chats_2_services.json'),
    )

    response = await utils.get_messages_paging_v2(
        taxi_driver_communications, body=request_json, chat_id=chat_id,
    )

    assert response.status_code == expected_status
    if expected_status != 304:
        assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    'load_reply, request_json, sc_code, expected_code',
    [
        (
            True,
            utils.get_paging_request(
                older_than='2020-09-04T15:26:15+00:00',
                chat_meta=utils.get_chat_v2(chat_id='support_chat'),
            ),
            500,
            304,
        ),
        (
            True,
            utils.get_paging_request(
                older_than='2020-09-04T15:26:15+00:00',
                chat_meta=utils.get_chat_v2(chat_id='support_chat'),
            ),
            200,
            200,
        ),
        (
            False,
            utils.get_paging_request(
                older_than='2020-09-04T15:26:15+00:00',
                chat_meta=utils.get_chat_v2(chat_id='support_chat'),
            ),
            200,
            304,
        ),
        (
            True,
            utils.get_paging_request(
                newer_than='2020-09-04T15:21:15+00:00',
                chat_meta=utils.get_chat_v2(chat_id='support_chat'),
            ),
            200,
            200,
        ),
        (
            False,
            utils.get_paging_request(
                newer_than='2020-09-04T15:21:15+00:00',
                chat_meta=utils.get_chat_v2(chat_id='support_chat'),
            ),
            200,
            304,
        ),
    ],
)
async def test_messages_support_chat_paging(
        taxi_driver_communications,
        mock_support_chat,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_drivers,
        load_reply,
        request_json,
        sc_code,
        expected_code,
        mock_driver_diagnostics,
        mock_driver_trackstory,
):
    unique_drivers.add_driver('db1', 'uuid1', 'unique_driver_id1')
    if load_reply:
        mock_support_chat.set_response(
            response=load_json('support_chat_search_reply.json'), code=sc_code,
        )
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat_messages.json'),
    )
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications, chat_id='support_chat', body=request_json,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        expected_json = load_json('chat_support_resp.json')
        assert (
            response_json['chat_meta']['chat_sources'][0]['etag']
            != expected_json['chat_meta']['chat_sources'][0]['etag']
        )
        del response_json['chat_meta']['chat_sources'][0]['etag']
        del expected_json['chat_meta']['chat_sources'][0]['etag']
        assert response_json == expected_json
