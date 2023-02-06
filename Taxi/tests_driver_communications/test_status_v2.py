import pytest

from tests_driver_communications import utils


async def test_driver_messages_status(
        taxi_driver_communications,
        experiments3,
        load_json,
        mock_fleet_parks_list,
        mock_feeds,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_default_feeds()
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chat_with_feeds.json'),
    )

    messages = [
        utils.get_message(
            message_id=utils.DEFAULT_MESSAGE,
            status='read',
            meta=utils.get_feeds_meta_v2(),
        ),
    ]
    response = await utils.set_messages_statuses_v2(
        taxi_driver_communications, body=utils.get_messages_request(messages),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'unique_driver_id,sc_code,result_code',
    [
        ('unique_driver_id1', 200, 200),
        ('unique_driver_id1', 404, 500),
        ('unique_driver_id1', 500, 500),
        (None, 200, 500),
    ],
)
async def test_driver_messages_status_support(
        taxi_driver_communications,
        experiments3,
        load_json,
        mock_fleet_parks_list,
        mock_support_chat,
        unique_drivers,
        unique_driver_id,
        sc_code,
        result_code,
        mock_driver_diagnostics,
):
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    if unique_driver_id is not None:
        unique_drivers.add_driver('db1', 'uuid1', unique_driver_id)
    mock_support_chat.set_response(response={}, code=sc_code, handler='read')
    messages = [
        utils.get_message(
            message_id='123', status='read', meta=utils.get_support_meta_v2(),
        ),
    ]
    response = await utils.set_messages_statuses_v2(
        taxi_driver_communications,
        body=utils.get_messages_request(messages),
        chat_id='support_chat',
    )

    assert response.status_code == result_code
