import datetime

from tests_driver_communications import utils


async def test_chats_full_flow(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        mock_support_chat,
        unique_drivers,
        experiments3,
        load_json,
        mock_driver_diagnostics,
        mock_driver_trackstory,
):
    unique_drivers.add_driver(
        utils.PARK_ID, utils.PROFILE_ID, utils.UNIQUE_DRIVER_ID,
    )
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )

    # opened panel
    response = await utils.chats_polling_v3(
        taxi_driver_communications,
        body=utils.get_chats_request(chats=[utils.get_chat_v2()]),
    )
    assert response.status_code == 200
    assert 'updates' not in response.json()

    # opened chat
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
    assert not response.json()['messages']

    # write msg
    msg_text1 = 'hi, I have a problem'
    body = utils.get_reply_request(
        parent_message=None,
        reply=utils.get_reply(
            type_='message', value=msg_text1, client_id='client0',
        ),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )
    assert response.status_code == 200
    assert response.json()['new_message_id'] == 'message_id0'

    # check chat state
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
    message_group = response.json()['messages'][0]
    assert message_group['messages'][0]['text'] == msg_text1
    assert message_group['client_id'] == 'client0'
    assert message_group['id'] == 'message_id0'

    # check panel state
    response = await utils.chats_polling_v3(
        taxi_driver_communications,
        body=utils.get_chats_request(chats=[utils.get_chat_v2()]),
    )
    assert response.status_code == 200
    updates = response.json()['chats'][0]['updates']
    assert updates['new_msg_count'] == 0
    assert updates['last_msg']['id'] == 'message_id0'
    assert updates['last_msg']['messages'][0]['text'] == msg_text1

    # add support response
    support_msg_text1 = 'I can help you'
    mock_support_chat.create_support_response(
        support_msg_text1,
        (
            datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(days=1)
        ).isoformat(),
        reply_to=['message_id0', 'undefined'],
    )

    # opened panel
    response = await utils.chats_polling_v3(
        taxi_driver_communications,
        body=utils.get_chats_request(chats=[utils.get_chat_v2()]),
    )
    assert response.status_code == 200
    updates = response.json()['chats'][0]['updates']
    assert updates['new_msg_count'] == 1
    assert updates['last_msg']['id'] == 'message_id1'
    assert updates['last_msg']['is_new']
    assert updates['last_msg']['messages'][0]['text'] == support_msg_text1

    # opened chat
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
    assert len(response.json()['messages']) == 2
    message_group = response.json()['messages'][1]
    assert message_group['messages'][0]['text'] == support_msg_text1
    assert len(message_group['messages'][0]['replies']) == 2
    assert (
        message_group['messages'][0]['replies'][0]['text']
        == 'Сообщение не актуально.'
    )
    assert (
        message_group['messages'][0]['replies'][1]['id'] == 'text:message_id0'
    )
    assert message_group['is_new']
    assert message_group['id'] == 'message_id1'

    # read msg
    messages = [
        utils.get_message(
            message_id='message_id1',
            status='read',
            meta=utils.get_support_meta_v2(),
        ),
    ]
    response = await utils.set_messages_statuses_v2(
        taxi_driver_communications,
        body=utils.get_messages_request(messages),
        chat_id='support_chat',
    )
    assert response.status_code == 200

    # opened panel
    response = await utils.chats_polling_v3(
        taxi_driver_communications,
        body=utils.get_chats_request(chats=[utils.get_chat_v2()]),
    )
    assert response.status_code == 200
    updates = response.json()['chats'][0]['updates']
    assert updates['new_msg_count'] == 0
    assert 'is_new' not in updates['last_msg']

    # write reply with parent
    msg_text2 = 'found_solution'
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            meta=utils.get_support_meta_v2(), message_id='message_id1',
        ),
        reply=utils.get_reply(type_='message', value=msg_text2),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )
    assert response.status_code == 200
    assert not response.json()['messages']
    assert response.json()['new_message_id'] == 'message_id2'
    assert 'chat_settings' not in response.json()

    # send file
    mock_support_chat.set_response(
        {'attachment_id': 'attach_id1'}, code=200, handler='attach',
    )
    response = await utils.set_attachment(
        taxi_driver_communications,
        body='somebinarydata',
        chat_id='support_chat',
    )

    # write msg with attach
    msg_text3 = 'look at this meme'
    body = utils.get_reply_request(
        parent_message=None,
        reply=utils.get_reply(
            type_='message',
            value=msg_text3,
            attachments=[{'id': 'attach_id1'}],
        ),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )
    assert response.status_code == 200
    assert response.json()['new_message_id'] == 'message_id3'

    # check chat
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
    assert len(response.json()['messages']) == 4
    message_group = response.json()['messages'][2]
    assert message_group['id'] == 'message_id2'
    assert (
        message_group['messages'][0]['replies'][0]['id'] == 'text:message_id1'
    )
    assert message_group['messages'][0]['text'] == msg_text2
    message_group = response.json()['messages'][3]
    assert message_group['id'] == 'message_id3'
    assert 'attachment' in message_group['messages'][0]
    assert message_group['messages'][0]['type'] == 'attachment'
    assert message_group['messages'][1]['text'] == msg_text3

    # set csat
    mock_support_chat.set_csat()

    # check panel state
    response = await utils.chats_polling_v3(
        taxi_driver_communications,
        body=utils.get_chats_request(chats=[utils.get_chat_v2()]),
    )
    assert response.status_code == 200
    updates = response.json()['chats'][0]['updates']
    assert updates['new_msg_count'] == 1
    assert updates['last_msg']['id'] == 'csat1'

    # check_chat
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
    assert len(response.json()['messages']) == 5
    message_group = response.json()['messages'][4]
    assert message_group['id'] == 'csat1'
    assert message_group['messages'][0]['text'] == 'how do you like support?'
    assert message_group['sender'] == 'Опрос'
    assert len(message_group['messages'][0]['actions']) == 4
    assert 'actions' not in response.json()
    assert not response.json()['input_field']

    # problem not solved
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            message_id='csat1', meta=utils.get_support_meta_v2(),
        ),
        reply=utils.get_reply(type_='action', value='exit1'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['chat_settings']['show_input_field']
    assert not response_json['messages']
    assert response_json['new_message_id'] == 'csat1:answer'

    # check_chat
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
    assert len(response.json()['messages']) == 4
    message_group = response.json()['messages'][3]
    assert message_group['id'] == 'message_id3'
    assert 'actions' not in response.json()
    assert response.json()['input_field']

    # set csat
    mock_support_chat.set_csat()

    # check_chat
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
    assert len(response.json()['messages']) == 5
    assert 'actions' not in response.json()
    assert not response.json()['input_field']

    # mark 2
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            meta=utils.get_support_meta_v2(), message_id='csat1',
        ),
        reply=utils.get_reply(type_='action', value='mark2'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )
    assert response.status_code == 200
    assert response.json()['new_message_id'] == 'csat1:answer'
    assert not response.json()['chat_settings']['show_input_field']
    assert len(response.json()['messages']) == 1
    message = response.json()['messages'][0]
    assert message['id'] == 'csat2'
    assert message['messages'][0]['text'] == 'select reason'

    # check panel state
    response = await utils.chats_polling_v3(
        taxi_driver_communications,
        body=utils.get_chats_request(chats=[utils.get_chat_v2()]),
    )
    assert response.status_code == 200
    updates = response.json()['chats'][0]['updates']
    assert updates['new_msg_count'] == 1
    assert updates['last_msg']['id'] == 'csat2'

    # select reason
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            meta=utils.get_support_meta_v2(), message_id='csat2',
        ),
        reply=utils.get_reply(type_='action', value='reason2'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )
    assert response.status_code == 200
    assert response.json()['new_message_id'] == 'csat2:answer'
    assert not response.json()['chat_settings']['show_input_field']
    assert len(response.json()['messages']) == 1
    message = response.json()['messages'][0]
    assert message['id'] == 'csat3'
    assert message['messages'][0]['text'] == 'something else?'

    # request change reason
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            meta=utils.get_support_meta_v2(), message_id='csat3',
        ),
        reply=utils.get_reply(type_='action', value='transition2'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )
    assert response.status_code == 200
    assert response.json()['new_message_id'] == 'csat3:answer'
    assert not response.json()['chat_settings']['show_input_field']
    assert len(response.json()['messages']) == 1
    message = response.json()['messages'][0]
    assert message['id'] == 'csat2'
    assert message['messages'][0]['text'] == 'select reason'

    # select reason
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            meta=utils.get_support_meta_v2(), message_id='csat2',
        ),
        reply=utils.get_reply(type_='action', value='reason2'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )
    assert response.status_code == 200
    assert response.json()['new_message_id'] == 'csat2:answer'
    assert not response.json()['chat_settings']['show_input_field']
    assert len(response.json()['messages']) == 1
    message = response.json()['messages'][0]
    assert message['id'] == 'csat3'
    assert message['messages'][0]['text'] == 'something else?'

    # check chat
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
    assert len(response.json()['messages']) == 9
    message_group = response.json()['messages'][7]
    assert message_group['id'] == 'csat2:answer'
    assert message_group['messages'][0]['text'] == 'good service'
    assert 'actions' not in response.json()
    assert not response.json()['input_field']

    # close chat
    body = utils.get_reply_request(
        parent_message=utils.get_message(
            meta=utils.get_support_meta_v2(), message_id='csat3',
        ),
        reply=utils.get_reply(type_='action', value='exit2'),
    )
    response = await utils.set_reply(
        taxi_driver_communications,
        body=body,
        chat_id='support_chat',
        version='v2',
    )
    assert response.status_code == 200
    assert response.json()['new_message_id'] == 'csat3:answer'
    assert response.json()['chat_settings']['show_input_field']
    assert not response.json()['messages']

    # check chat
    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
    assert not response.json()['messages']
    assert 'actions' not in response.json()
    assert response.json()['input_field']


async def test_no_support_chat(
        taxi_driver_communications,
        mock_feeds,
        mock_fleet_parks_list,
        unique_drivers,
        experiments3,
        load_json,
        mock_driver_diagnostics,
        mock_support_chat,
):
    unique_drivers.add_driver(
        utils.PARK_ID, utils.PROFILE_ID, utils.UNIQUE_DRIVER_ID,
    )
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )

    mock_driver_diagnostics.set_enabled(False)
    mock_support_chat.set_passed_dkvu(False)

    response = await utils.get_messages_paging_v2(
        taxi_driver_communications,
        chat_id='support_chat',
        body=utils.get_paging_request(
            chat_meta=utils.get_chat_v2(chat_id='support_chat'),
        ),
    )
    assert response.status_code == 200
