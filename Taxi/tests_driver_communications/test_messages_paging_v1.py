import pytest

from tests_driver_communications import utils


@pytest.mark.parametrize(
    'request_json, chat_id, expected_status, expected_response',
    [
        (
            utils.get_paging_request(
                older_than='2020-06-09T12:40:15.277047+0000',
            ),
            'news',
            200,
            'paging_response_older_than.json',
        ),
        (
            utils.get_paging_request(
                newer_than='2020-06-09T12:50:15.277047+0000',
            ),
            'news',
            200,
            'paging_response_newer_than.json',
        ),
        (
            utils.get_paging_request(),
            'news',
            200,
            'paging_response_no_time.json',
        ),
        (
            utils.get_paging_request(
                newer_than='2020-06-09T12:50:15.277047+0000',
            ),
            'news',
            304,
            'failed_to_load_history.json',
        ),
        (
            utils.get_paging_request(
                newer_than='2020-06-09T12:50:15.277047+0000',
            ),
            'bad_chat',
            400,
            'wrong_chat_id.json',
        ),
    ],
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
    unique_drivers.add_driver(
        utils.PARK_ID, utils.PROFILE_ID, utils.UNIQUE_DRIVER_ID,
    )
    if expected_status == 200:
        mock_feeds.set_feeds(
            ['text_feed', 'text_title_image_feed', 'fullscreen_read_feed'],
        )
    else:
        mock_feeds.set_response({}, 304, handler='v1/fetch')
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chat_with_feeds.json'),
    )

    response = await utils.get_messages_paging(
        taxi_driver_communications, body=request_json, chat_id=chat_id,
    )

    assert response.status_code == expected_status
    if expected_status != 304:
        assert response.json() == load_json(expected_response)
