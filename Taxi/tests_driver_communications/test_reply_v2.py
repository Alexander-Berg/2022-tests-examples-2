import pytest

from tests_driver_communications import consts
from tests_driver_communications import utils


@pytest.mark.parametrize(
    'message_id, action, expected_code, expected_response',
    [
        (
            consts.FEED_ID_MAP[consts.TEXT_TITLE_IMAGE_PARENT],
            'dislike',
            200,
            None,
        ),
        (
            consts.FEED_ID_MAP[consts.TEXT_TITLE_IMAGE_PARENT],
            'like',
            400,
            'reply_like_already_used.json',
        ),
        ('MESSAGE_NOT_FOUND', 'like', 404, 'parent_not_found.json'),
        (
            consts.FEED_ID_MAP[consts.TEXT_TITLE_IMAGE_PARENT],
            'fake_action',
            400,
            'action_not_found.json',
        ),
        (consts.FEED_ID_MAP[consts.NO_META], 'like', 200, None),
    ],
)
@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_driver_messages_reply(
        taxi_driver_communications,
        mock_feeds,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        message_id,
        action,
        expected_code,
        expected_response,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_default_feeds()
    experiments3.add_experiments_json(
        load_json('chat_settings_one_chat_with_feeds.json'),
    )
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            message_id=message_id, meta=utils.get_feeds_meta_v2(),
        ),
        reply=utils.get_reply(value=action),
    )

    response = await utils.set_reply(
        taxi_driver_communications, body=body, version='v2',
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        expected_response = {
            'messages': [],
            'new_message_id': 'f6dc672653aa443d9ecf48cc5ef4cb22',
        }
        assert response.json() == expected_response
    else:
        assert response.json() == load_json(expected_response)


async def test_driver_messages_reply_no_config(
        taxi_driver_communications,
        mock_feeds,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_default_feeds()
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            message_id=consts.FEED_ID_MAP[consts.TEXT_TITLE_IMAGE_PARENT],
            meta=utils.get_feeds_meta_v2(),
        ),
        reply=utils.get_reply(value='dislike'),
    )
    response = await utils.set_reply(
        taxi_driver_communications, body=body, version='v2',
    )
    assert response.status_code == 500
    assert response.json() == {
        'message': 'Config is not found',
        'code': 'INTERNAL_ERROR',
    }


@pytest.mark.parametrize(
    'parent_message_id, reply_type, sc_resp, expected_code',
    [
        (None, 'message', 'support_chat_create_response.json', 200),
        (None, 'action', 'support_chat_create_response.json', 400),
        ('message_id1', 'message', 'support_chat_create_response.json', 200),
        (
            'message_id1',
            'message',
            'support_chat_create_with_parent_response.json',
            200,
        ),
    ],
)
@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_driver_messages_support_existing_chat(
        taxi_driver_communications,
        unique_drivers,
        mock_support_chat,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        parent_message_id,
        reply_type,
        sc_resp,
        expected_code,
        mock_driver_diagnostics,
):
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    mock_support_chat.set_response(
        load_json(sc_resp), code=201, handler='create',
    )
    unique_drivers.add_driver('db1', 'uuid1', 'unique_driver_id1')
    parent_message = None
    if parent_message_id is not None:
        parent_message = utils.get_message(
            message_id=parent_message_id, meta=utils.get_support_meta_v2(),
        )
    body = utils.get_reply_request(
        parent_message=parent_message,
        reply=utils.get_reply(type_=reply_type, value='hi, I have a problem'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        expected_response = {'messages': [], 'new_message_id': 'message_id2'}
        assert response.json() == expected_response
    else:
        assert response.json() == {
            'code': 'BAD_REQUEST',
            'message': 'Not full info for question reply',
        }


@pytest.mark.parametrize(
    'parent_message_id, sc_resp, expected_code',
    [
        (None, 'support_chat_create_new_chat_response.json', 200),
        (
            'message_id1',
            'support_chat_create_new_chat_with_parent_response.json',
            200,
        ),
    ],
)
@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_driver_messages_support_new_chat(
        taxi_driver_communications,
        unique_drivers,
        mock_support_chat,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        parent_message_id,
        sc_resp,
        expected_code,
        mock_driver_diagnostics,
):
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    mock_support_chat.set_response(
        load_json(sc_resp), code=200, handler='create',
    )
    unique_drivers.add_driver('db1', 'uuid1', 'unique_driver_id1')
    parent_message = None
    if parent_message_id is not None:
        parent_message = utils.get_message(
            message_id=parent_message_id, meta=utils.get_support_meta_v2(),
        )
    body = utils.get_reply_request(
        parent_message=parent_message,
        reply=utils.get_reply(type_='message', value='hi, I have a problem'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )

    assert response.status_code == expected_code
    expected_response = {'messages': [], 'new_message_id': 'message_id2'}
    assert response.json() == expected_response


@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_driver_messages_support_error_in_create(
        taxi_driver_communications,
        unique_drivers,
        mock_support_chat,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        mock_driver_diagnostics,
):
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    mock_support_chat.set_response({}, code=404, handler='create')
    unique_drivers.add_driver('db1', 'uuid1', 'unique_driver_id1')
    parent_message = utils.get_message(
        message_id='message_id1', meta=utils.get_support_meta_v2(),
    )
    body = utils.get_reply_request(
        parent_message=parent_message,
        reply=utils.get_reply(type_='message', value='hi, I have a problem'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': 'INTERNAL_ERROR',
        'message': 'Failed to create message',
    }


@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_driver_messages_support_no_unique_driver(
        taxi_driver_communications,
        unique_drivers,
        mock_support_chat,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        mock_driver_diagnostics,
):
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    mock_support_chat.set_response(
        load_json('support_chat_create_new_chat_response.json'),
        code=200,
        handler='create',
    )
    body = utils.get_reply_request(
        parent_message=None,
        reply=utils.get_reply(type_='message', value='hi, I have a problem'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': 'INTERNAL_ERROR',
        'message': 'No unique driver id found.',
    }


@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_driver_messages_reply_use_one_action(
        taxi_driver_communications,
        mock_feeds,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        unique_drivers,
        mock_driver_trackstory,
):
    mock_feeds.set_default_feeds()
    experiments3.add_experiments_json(load_json('one_action_feature.json'))
    message_id = consts.FEED_ID_MAP[consts.NO_META]
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            message_id=message_id, meta=utils.get_feeds_meta_v2(),
        ),
        reply=utils.get_reply(value='like'),
    )

    response = await utils.set_reply(
        taxi_driver_communications, body=body, version='v2',
    )
    assert response.status_code == 200
    expected_response = {
        'messages': [],
        'new_message_id': 'f6dc672653aa443d9ecf48cc5ef4cb22',
    }
    assert response.json() == expected_response

    body = utils.get_reply_request(
        parent_message=utils.get_message(
            message_id=message_id, meta=utils.get_feeds_meta_v2(),
        ),
        reply=utils.get_reply(value='dislike'),
    )

    response = await utils.set_reply(
        taxi_driver_communications, body=body, version='v2',
    )
    assert response.status_code == 400
    assert response.json() == load_json('reply_like_already_used.json')


@pytest.mark.parametrize(
    'attachments, value',
    [
        ([{'id': '1234'}], None),
        ([{'id': '1234'}, {'id': '12345'}], 'some text'),
    ],
)
@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_driver_messages_support_attachment(
        taxi_driver_communications,
        unique_drivers,
        mock_support_chat,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        attachments,
        value,
        mock_driver_diagnostics,
):
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    mock_support_chat.set_response(
        load_json('support_chat_create_new_chat_response.json'),
        code=200,
        handler='create',
    )
    unique_drivers.add_driver('db1', 'uuid1', 'unique_driver_id1')
    body = utils.get_reply_request(
        parent_message=None,
        reply=utils.get_reply(
            type_='message', value=value, attachments=attachments,
        ),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        version='v2',
        chat_id='support_chat',
    )

    assert response.status_code == 200
    expected_response = {'messages': [], 'new_message_id': 'message_id2'}
    assert response.json() == expected_response
