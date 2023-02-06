# pylint: disable=too-many-lines, protected-access, unused-variable
# pylint: disable=redefined-outer-name,no-member,expression-not-assigned
import datetime
import json

import bson
import pytest

TRANSLATIONS = {
    'user_support_chat.support_name.dmitry': {
        'ru': 'Андрей',
        'en': 'andrew',
        'lv': 'Jūratė',
    },
    'user_support_chat.support_name.yandex_support': {
        'ru': 'Саппорт яндекс',
        'en': 'Yandex support',
        'lt': 'Jūratė',
        'az': 'test',
    },
    'user_support_chat.support_name.uber_support': {
        'ru': 'Саппорт uber',
        'en': 'Uber support',
        'az': 'Uber support',
        'ky': 'ub sup',
    },
    'user_support_chat.support_name.samir': {'ru': 'Самир', 'en': 'samir'},
    'user_support_chat.support_name.dias': {'ru': 'Самир', 'en': 'dias'},
    'user_support_chat.support_name.alihan': {'ru': 'Самир', 'en': 'alihan'},
    'user_support_chat.support_name.miras': {'ru': 'Самир', 'en': 'miras'},
}


USER_CHAT_SUPPORTS = {
    'rus': {
        'yandex': [
            {'tanker_key': 'dmitry', 'url': '0'},
            {'tanker_key': 'andrew', 'url': '1'},
            {'tanker_key': 'pavel', 'url': '2'},
            {'tanker_key': 'artem', 'url': '3'},
        ],
        'uber': [{'tanker_key': 'uber_support', 'url': '4'}],
        '__default__': [{'tanker_key': 'yandex_support', 'url': '5'}],
    },
    'kaz': {
        'yandex': [
            {'tanker_key': 'dias', 'url': '5', 'tags': ['business_client']},
            {'tanker_key': 'miras', 'url': '5'},
            {
                'tanker_key': 'alihan',
                'url': '5',
                'tags': ['test_tag', 'vip_tag'],
            },
            {'tanker_key': 'ajzere', 'url': '5'},
        ],
        'uber': [{'tanker_key': 'uber_support', 'url': '4'}],
        '__default__': [{'tanker_key': 'yandex_support', 'url': '5'}],
    },
    'civ': {
        'yandex': [
            {'tanker_key': 'patrick', 'url': '5'},
            {'tanker_key': 'fernand', 'url': '5'},
            {'tanker_key': 'richard', 'url': '5'},
            {'tanker_key': 'cheik', 'url': '5'},
        ],
        'uber': [{'tanker_key': 'uber_support', 'url': '4'}],
        '__default__': [{'tanker_key': 'yandex_support', 'url': '5'}],
    },
    '__default__': {
        'yandex': [{'tanker_key': 'yandex_support', 'url': '5'}],
        'uber': [{'tanker_key': 'uber_support', 'url': '4'}],
        '__default__': [{'tanker_key': 'yandex_support', 'url': '5'}],
    },
}
DATE_1 = datetime.datetime(2020, 5, 1).isoformat()
DATE_2 = datetime.datetime(2020, 5, 2).isoformat()


@pytest.mark.parametrize(
    'data, status_code, expected_response, user_api_response',
    [
        (
            {
                'chat_id': 'test_id',
                'forwarded_messages_id': ['message_1', 'message_2'],
            },
            400,
            {},
            {},
        ),
        ({'new_chat_type': 'client_support'}, 400, {}, {}),
        ({'chat_id': '5dc549ae779fb31bac3cc641'}, 400, {}, {}),
        ({'forwarded_messages_id': ['message_1', 'message_2']}, 400, {}, {}),
        (
            {
                'chat_id': 'test_id',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'bad_chat_id'}},
            {},
        ),
        (
            {
                'chat_id': '5dc549ae779fb31bac3cc641',
                'forwarded_messages_id': ['message_1', 'message_2'],
                'new_chat_type': 'client_support',
            },
            404,
            {},
            {},
        ),
        (
            {
                'chat_id': '5dcd5251779fb3187c486e6e',
                'forwarded_messages_id': ['message_101', 'message_102'],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'forward_support_messages'}},
            {
                'items': [
                    {'id': '1', 'phone_id': 'phone_id', 'updated': DATE_1},
                ],
            },
        ),
        (
            {
                'chat_id': '5dcd5251779fb3187c486e6e',
                'forwarded_messages_id': ['message_102'],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'forward_support_messages'}},
            {
                'items': [
                    {'id': '1', 'phone_id': 'phone_id', 'updated': DATE_1},
                ],
            },
        ),
        (
            {
                'chat_id': '5dcd5251779fb3187c486e6e',
                'forwarded_messages_id': ['message_101', 'message_33'],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'forward_messages_from_other_chat'}},
            {
                'items': [
                    {'id': '1', 'phone_id': 'phone_id', 'updated': DATE_1},
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ece779fb3302cc784bb',
                'forwarded_messages_id': [
                    'message_21',
                    'message_22',
                    'message_23',
                ],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'forward_support_messages'}},
            {
                'items': [
                    {'id': '1', 'phone_id': 'phone_id', 'updated': DATE_1},
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ece779fb3302cc784bb',
                'forwarded_messages_id': [
                    'message_21',
                    'message_23',
                    'message_33',
                ],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'forward_messages_from_other_chat'}},
            {
                'items': [
                    {'id': '1', 'phone_id': 'phone_id', 'updated': DATE_1},
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ca8779fb3302cc784ba',
                'forwarded_messages_id': ['message_11'],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'unsupported_chat_type'}},
            {
                'items': [
                    {'id': '1', 'phone_id': 'phone_id', 'updated': DATE_1},
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ca8779fb3302cc784bf',
                'forwarded_messages_id': ['message_71'],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'unsupported_chat_type'}},
            {
                'items': [
                    {'id': '1', 'phone_id': 'phone_id', 'updated': DATE_1},
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ece779fb3302cc784bc',
                'forwarded_messages_id': ['message_31'],
                'new_chat_type': 'safety_center_support',
            },
            400,
            {'error': {'reason_code': 'forbidden_chat_type'}},
            {
                'items': [
                    {'id': '1', 'phone_id': 'phone_id', 'updated': DATE_1},
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ece779fb3302cc784bc',
                'forwarded_messages_id': ['message_31'],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'no_new_owner_id'}},
            {'items': []},
        ),
        (
            {
                'chat_id': '5b436ece779fb3302cc784bc',
                'forwarded_messages_id': ['message_31'],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'no_phone_id'}},
            {'items': [{'id': '1', 'updated': DATE_1}]},
        ),
        (
            {
                'chat_id': '5b436ece779fb3302cc784bc',
                'forwarded_messages_id': ['message_31'],
                'new_chat_type': 'client_support',
            },
            400,
            {'error': {'reason_code': 'invalid_owner_id'}},
            {
                'items': [
                    {'id': '1', 'phone_id': 'bad_phone_id', 'updated': DATE_1},
                ],
            },
        ),
    ],
)
@pytest.mark.config(
    FORWARD_NEW_OWNER_SEARCH_PARAMS={
        'client_support': {
            'use_same_owner': False,
            'use_user_api': True,
            'user_api_search_field': {'eats_support': 'yandex_uid'},
        },
        'safety_center_support': {
            'use_same_owner': False,
            'use_user_api': True,
            'user_api_search_field': {'eats_support': 'yandex_uid'},
        },
    },
)
async def test_bad_codes(
        web_app_client,
        data,
        status_code,
        expected_response,
        mockserver,
        user_api_response,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_users_search(request):
        assert request.json == {
            'yandex_uid': '12345',
            'authorized': True,
            'primary_replica': False,
        }
        return user_api_response

    response = await web_app_client.post(
        '/v1/chat/forward/', data=json.dumps(data),
    )
    assert response.status == status_code
    if response.status == 400 and expected_response:
        data = await response.json()
        assert data == expected_response


@pytest.mark.now('2019-11-08T11:20:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_GENDER_BY_COUNTRY_PLATFORM_CHAT_TYPE={
        '__default__': {
            '__default__': {
                'driver_support': ['female'],
                'client_support': ['male'],
                'eats_support': ['male'],
                'safety_center_support': ['male'],
            },
        },
    },
)
@pytest.mark.parametrize(
    'data, status_code, user_api_response',
    [
        (
            {
                'chat_id': '5dc5745e779fb31bac3cc645',
                'forwarded_messages_id': ['message_81', 'message_83'],
                'new_chat_type': 'client_support',
            },
            409,
            {
                'items': [
                    {
                        'id': '1',
                        'phone_id': '5dc574a0779fb31bac3cc646',
                        'updated': DATE_1,
                    },
                ],
            },
        ),
        (
            {
                'chat_id': '5dc5745e779fb31bac3cc645',
                'forwarded_messages_id': ['message_81'],
                'new_chat_type': 'client_support',
            },
            409,
            {
                'items': [
                    {
                        'id': '1',
                        'phone_id': '5dc574a0779fb31bac3cc649',
                        'updated': DATE_1,
                    },
                ],
            },
        ),
    ],
)
async def test_conflict(
        web_app_client, data, status_code, mockserver, user_api_response,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_users_search(request):
        assert request.json == {
            'yandex_uid': '123456',
            'authorized': True,
            'primary_replica': False,
        }
        return user_api_response

    response = await web_app_client.post(
        '/v1/chat/forward/', data=json.dumps(data),
    )
    assert response.status == status_code


@pytest.mark.now('2019-11-08T11:20:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_GENDER_BY_COUNTRY_PLATFORM_CHAT_TYPE={
        '__default__': {
            '__default__': {
                'driver_support': ['female'],
                'client_support': ['male'],
                'eats_support': ['male'],
                'safety_center_support': ['male'],
                'carsharing_support': ['male'],
            },
        },
    },
    FORWARD_NEW_OWNER_SEARCH_PARAMS={
        'client_support': {
            'use_same_owner': False,
            'use_user_api': True,
            'user_api_search_field': {'eats_support': 'yandex_uid'},
        },
        'carsharing_support': {
            'use_same_owner': False,
            'use_user_api': True,
            'user_api_search_field': {'client_support': 'id'},
            'chat_doc_search_field': {'client_support': 'user_id'},
            'user_owner_field': {'client_support': 'yandex_uid'},
        },
    },
    SUPPORT_CHAT_FORWARD_MAPPING={
        'eats_support': ['client_support'],
        'client_support': ['carsharing_support'],
    },
)
@pytest.mark.parametrize(
    'data, status_code, expected_id, user_api_request, user_api_response,'
    'expected_new_chat',
    [
        (
            {
                'chat_id': '5b436ece779fb3302cc784bc',
                'forwarded_messages_id': ['message_31'],
                'new_chat_type': 'client_support',
            },
            201,
            '',
            {
                'yandex_uid': '12345',
                'authorized': True,
                'primary_replica': False,
            },
            {
                'items': [
                    {
                        'id': '1',
                        'phone_id': '5dc55679779fb31bac3cc642',
                        'updated': DATE_1,
                    },
                ],
            },
            {
                'open': True,
                'visible': False,
                'user_country': 'rus',
                'user_application': 'android',
                'user_locale': 'ru',
                'ask_csat': False,
                'retry_csat_request': False,
                'owner_id': '5dc55679779fb31bac3cc642',
                'ticket_status': 'open',
                'ticket_processed': True,
                'type': 'client_support',
                'incident_timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                'last_message_from_user': True,
                'platform': 'yandex',
                'support_avatar_url': '0',
                'support_name': 'Андрей',
                'user_id': 'user_id3',
                'tanker_key': 'user_support_chat.support_name.dmitry',
                'updated': datetime.datetime(2019, 11, 8, 11, 20),
                'messages': [
                    {
                        'id': 'forwarded_message_31',
                        'author': 'user',
                        'author_id': '5dc55679779fb31bac3cc642',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                        'metadata': {'field': 'value'},
                    },
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ece779fb3302cc784bc',
                'forwarded_messages_id': ['message_31', 'message_33'],
                'new_chat_type': 'client_support',
            },
            201,
            '',
            {
                'yandex_uid': '12345',
                'authorized': True,
                'primary_replica': False,
            },
            {
                'items': [
                    {
                        'id': '1',
                        'phone_id': '5dc55679779fb31bac3cc642',
                        'updated': DATE_2,
                    },
                    {
                        'id': '2',
                        'phone_id': '5dc55679779fb31bac3cc643',
                        'updated': DATE_1,
                    },
                ],
            },
            {
                'open': True,
                'visible': False,
                'user_country': 'rus',
                'user_application': 'android',
                'user_locale': 'ru',
                'ask_csat': False,
                'retry_csat_request': False,
                'owner_id': '5dc55679779fb31bac3cc642',
                'type': 'client_support',
                'ticket_status': 'open',
                'ticket_processed': True,
                'incident_timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                'last_message_from_user': True,
                'platform': 'yandex',
                'support_avatar_url': '0',
                'support_name': 'Андрей',
                'user_id': 'user_id3',
                'tanker_key': 'user_support_chat.support_name.dmitry',
                'updated': datetime.datetime(2019, 11, 8, 11, 20),
                'messages': [
                    {
                        'id': 'forwarded_message_31',
                        'author': 'user',
                        'message': 'text_1',
                        'author_id': '5dc55679779fb31bac3cc642',
                        'timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                        'metadata': {'field': 'value'},
                    },
                    {
                        'id': 'forwarded_message_33',
                        'author': 'user',
                        'author_id': '5dc55679779fb31bac3cc642',
                        'message': 'text_3',
                        'timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                    },
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ece779fb3302cc784bc',
                'forwarded_messages_id': ['message_31'],
                'new_chat_type': 'client_support',
            },
            200,
            '5b436ece779fb3302cc784bd',
            {
                'yandex_uid': '12345',
                'authorized': True,
                'primary_replica': False,
            },
            {
                'items': [
                    {
                        'id': '1',
                        'phone_id': '5dc56585779fb31bac3cc644',
                        'updated': DATE_1,
                    },
                ],
            },
            {
                'open': True,
                'visible': True,
                'user_country': 'rus',
                'user_application': 'android',
                'user_locale': 'ru',
                'ask_csat': False,
                'retry_csat_request': False,
                'owner_id': '5dc56585779fb31bac3cc644',
                'type': 'client_support',
                'incident_timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                'last_message_from_user': True,
                'platform': 'yandex',
                'new_messages': 1,
                'support_avatar_url': 2,
                'support_name': 'Петр',
                'text_indexed': True,
                'ticket_status': 'open',
                'ticket_processed': True,
                'user_id': 'user_id3',
                'updated': datetime.datetime(2019, 11, 8, 11, 20),
                'messages': [
                    {
                        'id': 'message_41',
                        'author': 'user',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
                    },
                    {
                        'id': 'message_42',
                        'author': 'support',
                        'message': 'text_2',
                        'timestamp': datetime.datetime(
                            2018, 7, 10, 11, 12, 50,
                        ),
                    },
                    {
                        'id': 'forwarded_message_31',
                        'author': 'user',
                        'message': 'text_1',
                        'author_id': '5dc56585779fb31bac3cc644',
                        'timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                        'metadata': {'field': 'value'},
                    },
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ece779fb3302cc784bc',
                'forwarded_messages_id': ['message_31', 'message_33'],
                'new_chat_type': 'client_support',
            },
            200,
            '5b436ece779fb3302cc784bf',
            {
                'yandex_uid': '12345',
                'authorized': True,
                'primary_replica': False,
            },
            {
                'items': [
                    {
                        'id': '1',
                        'phone_id': '5b4f5092779fb332fcc26153',
                        'updated': DATE_1,
                    },
                ],
            },
            {
                'open': True,
                'visible': False,
                'user_country': 'rus',
                'user_application': 'android',
                'user_locale': 'ru',
                'ask_csat': False,
                'retry_csat_request': False,
                'owner_id': '5b4f5092779fb332fcc26153',
                'type': 'client_support',
                'incident_timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                'last_message_from_user': True,
                'platform': 'yandex',
                'ticket_status': 'open',
                'ticket_processed': True,
                'support_avatar_url': 2,
                'support_name': 'Петр',
                'text_indexed': True,
                'user_id': 'user_id3',
                'updated': datetime.datetime(2019, 11, 8, 11, 20),
                'messages': [
                    {
                        'id': 'message_61',
                        'author': 'user',
                        'message': 'text_6',
                        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
                    },
                    {
                        'id': 'message_62',
                        'author': 'support',
                        'message': 'text_7',
                        'author_id': 'some_support',
                        'timestamp': datetime.datetime(
                            2018, 7, 10, 11, 12, 50,
                        ),
                    },
                    {
                        'id': 'forwarded_message_31',
                        'author': 'user',
                        'author_id': '5b4f5092779fb332fcc26153',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                        'metadata': {'field': 'value'},
                    },
                    {
                        'id': 'forwarded_message_33',
                        'author_id': '5b4f5092779fb332fcc26153',
                        'author': 'user',
                        'message': 'text_3',
                        'timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                    },
                ],
            },
        ),
        (
            {
                'chat_id': '5b436ca8779fb3302cc784ba',
                'forwarded_messages_id': ['message_11'],
                'new_chat_type': 'carsharing_support',
            },
            201,
            '',
            {'authorized': True, 'primary_replica': False, 'id': 'user_id1'},
            {'items': [{'id': '1', 'yandex_uid': '12345', 'updated': DATE_1}]},
            {
                'open': True,
                'visible': False,
                'user_country': 'rus',
                'user_application': 'android',
                'user_locale': 'ru',
                'ask_csat': False,
                'retry_csat_request': False,
                'owner_id': '12345',
                'ticket_status': 'open',
                'ticket_processed': True,
                'type': 'carsharing_support',
                'incident_timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                'last_message_from_user': True,
                'platform': 'yandex',
                'support_avatar_url': '0',
                'support_name': 'Андрей',
                'user_id': 'user_id1',
                'chatterbox_id': 'chatterbox_id',
                'text_indexed': True,
                'user_phone_id': bson.ObjectId('5b4f5059779fb332fcc26152'),
                'tanker_key': 'user_support_chat.support_name.dmitry',
                'updated': datetime.datetime(2019, 11, 8, 11, 20),
                'messages': [
                    {
                        'id': 'forwarded_message_11',
                        'author': 'carsharing_client',
                        'author_id': '12345',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2019, 11, 8, 11, 20),
                        'metadata': {
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'name': 'filename.txt',
                                },
                            ],
                        },
                    },
                ],
            },
        ),
    ],
)
async def test_simple_forward(
        web_app_client,
        web_context,
        stq,
        data,
        status_code,
        expected_id,
        user_api_request,
        expected_new_chat,
        mockserver,
        user_api_response,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_users_search(request):
        assert request.json == user_api_request
        return user_api_response

    old_chat = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(data['chat_id'])},
    )
    old_chat.pop('updated')
    response = await web_app_client.post(
        '/v1/chat/forward/', data=json.dumps(data),
    )

    old_chat_updated = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(data['chat_id'])},
    )
    for message in old_chat_updated['messages']:
        if message['id'] in data['forwarded_messages_id']:
            assert message['metadata']['forwarded']
            message['metadata'].pop('forwarded')
            if not message['metadata']:
                message.pop('metadata')
        else:
            assert 'forwarded' not in message.get('metadata', {})
    old_chat_updated.pop('updated')
    assert old_chat == old_chat_updated

    assert response.status == status_code
    response_data = await response.json()
    if status_code == 200:
        assert response_data['chat_id'] == expected_id

    call = stq.support_chat_forward_attachments.next_call()
    assert stq.is_empty
    call.pop('kwargs')
    call.pop('id')
    assert call == {
        'args': [
            old_chat['owner_id'],
            {'$oid': response_data['chat_id']},
            [
                'forwarded_%s' % message_id
                for message_id in data['forwarded_messages_id']
            ],
        ],
        'queue': 'support_chat_forward_attachments',
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
    }

    new_chat = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(response_data['chat_id'])},
    )
    new_chat_id = str(new_chat.pop('_id'))
    assert new_chat == expected_new_chat

    response = await web_app_client.post(
        '/v1/chat/forward/', data=json.dumps(data),
    )
    assert response.status == 200
    response_data = await response.json()
    assert new_chat_id == response_data['chat_id']
    new_chat = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(response_data['chat_id'])},
    )
    new_chat.pop('_id')
    assert new_chat == expected_new_chat
