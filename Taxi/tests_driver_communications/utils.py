# pylint: disable=dangerous-default-value


# TEXT_TITLE_IMAGE_PARENT
DEFAULT_MESSAGE = 'f6dc672653aa443d9ecf48cc5ef4cb6e'
DEFAULT_CHAT_ID = 'news'

PARK_ID = 'db1'
PROFILE_ID = 'uuid1'
UNIQUE_DRIVER_ID = 'unique_driver_id1'


def get_auth_headers(
        park_id=PARK_ID, driver_profile_id=PROFILE_ID, token=None,
):
    response = {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.07 (1234)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'User-Agent': 'Taximeter 9.07 (1234)',
        'X-Idempotency-Token': 'token',
    }
    if token:
        response['X-Idempotency-Token'] = token
    return response


def get_position():
    return {'lat': 55.744094, 'lon': 37.627920}


def get_driver_info(position=get_position()):
    response = {}
    if position:
        response['position'] = position
    return response


def get_meta():
    return {
        'source_service': 'feeds',
        'content_sources': ['driver-wall'],
        'channels': ['taximeter:Driver', 'taximeter:Park'],
    }


def get_meta_fullscreens():
    return {
        'source_service': 'feeds',
        'content_sources': ['fullscreens'],
        'channels': ['taximeter:Driver', 'taximeter:Park'],
    }


def get_support_meta():
    return {
        'source_service': 'support_chat',
        'content_sources': ['chat_id:12345'],
        'channels': [],
    }


def get_support_meta_v2():
    return {'id': 'support_chat/problem:12345'}


def get_feeds_meta_v2():
    return {'id': 'feeds/wall'}


def get_chat_source():
    return {
        'source_service': 'feeds',
        'content_sources': ['driver-wall'],
        'channels': [
            'taximeter:Driver',
            'taximeter:Park',
            'taximeter:City',
            'taximeter:Country',
        ],
        'etag': '123',
    }


def get_chat_source_v2():
    return {'id': 'feeds/driver-wall', 'etag': '123'}


def get_chat(
        chat_id=DEFAULT_CHAT_ID,
        chat_sources=[get_chat_source()],
        last_polling_time=None,
):
    data = {'chat_id': chat_id}
    if chat_sources is not None:
        data['chat_sources'] = chat_sources
    if last_polling_time is not None:
        data['last_polling_time'] = last_polling_time
    return data


def get_chat_v2(
        chat_id=DEFAULT_CHAT_ID,
        chat_sources=[get_chat_source_v2()],
        last_polling_time=None,
):
    data = {'id': chat_id}
    if chat_sources is not None:
        data['chat_sources'] = chat_sources
    if last_polling_time is not None:
        data['last_polling_time'] = last_polling_time
    return data


def get_message(message_id=DEFAULT_MESSAGE, status=None, meta=get_meta()):
    response = {'message_id': 'text:' + message_id, 'meta': meta}
    if status:
        response['status'] = status
    return response


def get_reply(type_='action', value='like', attachments=None, client_id='123'):
    reply = {'client_id': client_id, 'type': type_}
    if value is not None:
        reply['value'] = value
    if attachments:
        reply['attachments'] = attachments
    return reply


def get_chats_request(
        driver_info=get_driver_info(), chats=[get_chat()], force_updates=None,
):
    response = {'driver_info': driver_info}
    if chats is not None:
        response['chats'] = chats
    if force_updates is not None:
        response['force_updates'] = force_updates
    return response


def get_messages_request(messages=[get_message()]):
    return {'driver_info': get_driver_info(), 'messages': messages}


def get_reply_request(parent_message=get_message(), reply=get_reply()):
    request = {'driver_info': get_driver_info(), 'reply': reply}
    request['driver_info']['appeal_source'] = 'order'
    request['driver_info']['driver_on_order'] = True
    request['driver_info']['work_mode'] = 'some_mode'
    if parent_message is not None:
        request['parent_message'] = parent_message
    return request


def get_paging_request(
        newer_than=None,
        older_than=None,
        chat_meta=get_chat(),
        driver_info=get_driver_info(),
):
    response = {'driver_info': driver_info, 'chat_meta': chat_meta}
    if newer_than:
        response['paging_settings'] = {}
        response['paging_settings']['newer_than'] = newer_than
    if older_than:
        response['paging_settings'] = {}
        response['paging_settings']['older_than'] = older_than
    return response


async def chats_polling_v2(
        taxi_driver_communications,
        body=get_chats_request(),
        chat_id=DEFAULT_CHAT_ID,
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v2/chats/polling',
        headers=get_auth_headers(),
        json=body,
    )


async def chats_polling_v3(
        taxi_driver_communications,
        body=get_chats_request(chats=[get_chat_v2()]),
        chat_id=DEFAULT_CHAT_ID,
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v3/chats/polling',
        headers=get_auth_headers(),
        json=body,
    )


async def get_chats_messages(
        taxi_driver_communications, body=get_chats_request(),
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v1/chats/messages',
        headers=get_auth_headers(),
        json=body,
    )


async def get_fullscreens(
        taxi_driver_communications, body=get_chats_request(),
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v1/fullscreens',
        headers=get_auth_headers(),
        json=body,
    )


async def get_fullscreens_v2(
        taxi_driver_communications,
        body=get_chats_request(chats=[get_chat_v2()]),
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v2/fullscreens',
        headers=get_auth_headers(),
        json=body,
    )


async def set_messages_statuses(
        taxi_driver_communications,
        body=get_messages_request(),
        chat_id=DEFAULT_CHAT_ID,
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v1/chats/messages/status',
        headers=get_auth_headers(token='token'),
        params={'chat_id': chat_id},
        json=body,
    )


async def set_messages_statuses_v2(
        taxi_driver_communications,
        body=get_messages_request(),
        chat_id=DEFAULT_CHAT_ID,
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v2/chats/messages/status',
        headers=get_auth_headers(token='token'),
        params={'chat_id': chat_id},
        json=body,
    )


async def set_reply(
        taxi_driver_communications,
        body=get_reply_request(),
        chat_id=DEFAULT_CHAT_ID,
        version='v1',
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/{}/chats/messages/reply'.format(
            version,
        ),
        headers=get_auth_headers(token='token'),
        params={'chat_id': chat_id},
        json=body,
    )


async def set_attachment(
        taxi_driver_communications, body, chat_id=DEFAULT_CHAT_ID,
):
    headers = get_auth_headers(token='token').copy()
    headers['Content-Type'] = 'image/jpeg'
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v1/chats/attachment',
        headers=headers,
        params={
            'chat_id': chat_id,
            'idempotency_token': 'iii',
            'filename': 'name',
        },
        data=body,
    )


async def get_messages_paging(
        taxi_driver_communications,
        body=get_paging_request(),
        chat_id=DEFAULT_CHAT_ID,
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v1/messages',
        headers=get_auth_headers(token='token'),
        params={'chat_id': chat_id},
        json=body,
    )


async def get_messages_paging_v2(
        taxi_driver_communications,
        body=get_paging_request(chat_meta=get_chat_v2()),
        chat_id=DEFAULT_CHAT_ID,
):
    return await taxi_driver_communications.post(
        'driver/v1/driver-communications/v2/messages',
        headers=get_auth_headers(token='token'),
        params={'chat_id': chat_id},
        json=body,
    )


def get_fullscreen_chats(response_json):
    expected_response_json = {}
    expected_response_json['chats'] = []
    for chat in response_json['chats']:
        if chat['type'] == 'fullscreen':
            expected_response_json['chats'].append(chat)
    return expected_response_json


def get_source_id(source):
    if source['source_service'] == 'feeds':
        if source['content_sources'] == ['fullscreens']:
            return 'feeds/fullscreens'
        if source['content_sources'] == ['driver-wall']:
            return 'feeds/wall'
    if source['source_service'] == 'support_chat':
        return 'support_chat/problem'
    return ''


def get_response_chat_v2(chat):
    chat['chat_meta']['id'] = chat['chat_meta']['chat_id']
    del chat['chat_meta']['chat_id']
    if chat['chat_meta']['chat_sources']:
        chat_sources = []
        for source in chat['chat_meta']['chat_sources']:
            chat_sources.append(
                {'id': get_source_id(source), 'etag': source['etag']},
            )
        chat['chat_meta']['chat_sources'] = chat_sources
    for message in chat['messages']:
        message_meta = {}
        message_meta['id'] = get_source_id(message['backend_meta'])
        message['backend_meta'] = message_meta
        message['date'] = message['messages'][0]['date']
        if 'sender' in message['messages'][0]:
            message['sender'] = message['messages'][0]['sender']
        if 'client_id' in message['messages'][0]:
            message['client_id'] = message['messages'][0]['client_id']
        title = ''
        for submsg in message['messages']:
            del submsg['date']
            if 'sender' in submsg:
                del submsg['sender']
            if submsg['type'] == 'text' and submsg['text'].startswith('**'):
                submsg['type'] = 'title'
                submsg['text'] = submsg['text'].replace('**', '')
                title = submsg['text']
        for submsg in message['messages']:
            if submsg['type'] == 'text':
                if title:
                    submsg['reply_title'] = title
                else:
                    if 'title' in submsg:
                        submsg['reply_title'] = submsg['title']
                    else:
                        submsg['reply_title'] = submsg['text']
    return chat


def get_response_chats_v2(expected_response_v1):
    for chat in expected_response_v1['chats']:
        chat = get_response_chat_v2(chat)
    return expected_response_v1


def get_fullscreen_chats_v2(response_json):
    expected_response_v1 = get_fullscreen_chats(response_json)
    return get_response_chats_v2(expected_response_v1)
