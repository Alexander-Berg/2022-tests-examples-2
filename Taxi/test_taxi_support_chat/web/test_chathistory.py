import http
import json

import pytest


TRANSLATIONS = {
    'ivan': {'ru': 'Иван', 'en': 'Ivan'},
    'petr': {'ru': 'Петр', 'en': 'Petr'},
}


async def test_invalid_id(web_app_client):
    response = await web_app_client.post(
        '/v1/chat/not_found_id/history', data=json.dumps({}),
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST


async def test_not_found(web_app_client):
    response = await web_app_client.post(
        '/v1/chat/5b436c16779fb3302cc784b9/history', data=json.dumps({}),
    )
    assert response.status == http.HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'service_ticket,chat_id,expected_status',
    [
        (
            'backend_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.OK,
        ),
        (
            'backend_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.OK,
        ),
        (
            'disp_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            'disp_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.OK,
        ),
        (
            'corp_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            'corp_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.FORBIDDEN,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_chat_type_access(
        web_app_client,
        mock_tvm_keys,
        service_ticket,
        chat_id,
        expected_status,
):
    response = await web_app_client.post(
        '/v1/chat/{}/history'.format(chat_id),
        data=json.dumps({}),
        headers={'X-Ya-Service-Ticket': service_ticket},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'chat_id,data,expected_result',
    [
        (
            '5b436ca8779fb3302cc784ba',
            {'include_metadata': False},
            {
                'newest_message_id': 'message_12',
                'total': 2,
                'new_message_count': 2,
                'messages': [
                    {
                        'id': 'message_11',
                        'text': 'text_1',
                        'metadata': {
                            'created': '2018-07-01T02:03:50+0000',
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'name': 'filename.txt',
                                },
                                {
                                    'link': 'test_url_2',
                                    'id': 'message_11_1',
                                    'link_preview': 'link_preview',
                                    'preview_width': 150,
                                    'preview_height': 200,
                                    'name': 'file_1',
                                    'mimetype': 'image/png',
                                    'size': 20000,
                                },
                            ],
                        },
                        'sender': {
                            'id': 'some_user_id',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                    {
                        'id': 'message_12',
                        'text': 'text_2',
                        'metadata': {'created': '2018-07-04T05:06:50+0000'},
                        'sender': {
                            'id': 'support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                ],
            },
        ),
        (
            '5b436ca8779fb3302cc784ba',
            {'include_metadata': True, 'include_participants': True},
            {
                'newest_message_id': 'message_12',
                'total': 2,
                'new_message_count': 2,
                'metadata': {
                    'created': '2018-07-10T10:09:50+0000',
                    'updated': '2018-07-11T12:15:50+0000',
                    'ask_csat': False,
                    'last_message_from_user': False,
                    'new_messages': 2,
                    'user_locale': 'ru',
                    'csat_value': 'good',
                    'csat_reasons': ['fast answer', 'thank you'],
                    'chatterbox_id': 'chatterbox_id',
                    'metadata_field_1': 'value_1',
                    'csat_new_version': False,
                    'csat_options': [
                        {
                            'option_key': 'horrible',
                            'option_name': 'user_chat_csat.horrible',
                            'reasons': [
                                {
                                    'reason_key': 'long_answer',
                                    'reason_name': (
                                        'user_chat_csat_reasons.long_answer'
                                    ),
                                },
                                {
                                    'reason_key': 'template_answer',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'template_answer'
                                    ),
                                },
                                {
                                    'reason_key': 'problem_not_solved',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'problem_not_solved'
                                    ),
                                },
                                {
                                    'reason_key': 'disagree_solution',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'disagree_solution'
                                    ),
                                },
                            ],
                        },
                        {
                            'option_key': 'bad',
                            'option_name': 'user_chat_csat.bad',
                            'reasons': [
                                {
                                    'reason_key': 'long_answer',
                                    'reason_name': (
                                        'user_chat_csat_reasons.long_answer'
                                    ),
                                },
                                {
                                    'reason_key': 'template_answer',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'template_answer'
                                    ),
                                },
                                {
                                    'reason_key': 'problem_not_solved',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'problem_not_solved'
                                    ),
                                },
                                {
                                    'reason_key': 'disagree_solution',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'disagree_solution'
                                    ),
                                },
                            ],
                        },
                        {
                            'option_key': 'normal',
                            'option_name': 'user_chat_csat.normal',
                            'reasons': [
                                {
                                    'reason_key': 'long_answer',
                                    'reason_name': (
                                        'user_chat_csat_reasons.long_answer'
                                    ),
                                },
                                {
                                    'reason_key': 'template_answer',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'template_answer'
                                    ),
                                },
                                {
                                    'reason_key': 'problem_not_solved',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'problem_not_solved'
                                    ),
                                },
                                {
                                    'reason_key': 'disagree_solution',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'disagree_solution'
                                    ),
                                },
                            ],
                        },
                        {
                            'option_key': 'good',
                            'option_name': 'user_chat_csat.good',
                            'reasons': [
                                {
                                    'reason_key': 'long_answer',
                                    'reason_name': (
                                        'user_chat_csat_reasons.long_answer'
                                    ),
                                },
                                {
                                    'reason_key': 'template_answer',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'template_answer'
                                    ),
                                },
                                {
                                    'reason_key': 'problem_not_solved',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'problem_not_solved'
                                    ),
                                },
                                {
                                    'reason_key': 'disagree_solution',
                                    'reason_name': (
                                        'user_chat_csat_reasons.'
                                        'disagree_solution'
                                    ),
                                },
                            ],
                        },
                        {
                            'option_key': 'amazing',
                            'option_name': 'user_chat_csat.amazing',
                            'reasons': [],
                        },
                    ],
                },
                'messages': [
                    {
                        'id': 'message_11',
                        'text': 'text_1',
                        'metadata': {
                            'created': '2018-07-01T02:03:50+0000',
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'name': 'filename.txt',
                                },
                                {
                                    'link': 'test_url_2',
                                    'link_preview': 'link_preview',
                                    'preview_width': 150,
                                    'preview_height': 200,
                                    'id': 'message_11_1',
                                    'name': 'file_1',
                                    'mimetype': 'image/png',
                                    'size': 20000,
                                },
                            ],
                        },
                        'sender': {
                            'id': 'some_user_id',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                    {
                        'id': 'message_12',
                        'text': 'text_2',
                        'metadata': {'created': '2018-07-04T05:06:50+0000'},
                        'sender': {
                            'id': 'support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                ],
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': 4,
                        'nickname': 'Иван',
                    },
                    {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
            },
        ),
        (
            '5b436ece779fb3302cc784bb',
            {
                'include_participants': False,
                'range': {'message_ids': {'newer_than': 'message_23'}},
            },
            {
                'newest_message_id': 'message_25',
                'total': 5,
                'new_message_count': 0,
                'messages': [
                    {
                        'id': 'message_24',
                        'text': 'text_4',
                        'metadata': {'created': '2018-07-16T17:18:50+0000'},
                        'sender': {
                            'id': 'another_support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                    {
                        'id': 'message_25',
                        'text': 'text_5',
                        'metadata': {'created': '2018-07-19T20:21:50+0000'},
                        'sender': {
                            'id': 'user',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                ],
            },
        ),
        (
            '5b436ece779fb3302cc784bb',
            {
                'include_participants': False,
                'range': {
                    'message_ids': {'newer_than': 'message_23', 'limit': 1},
                },
            },
            {
                'newest_message_id': 'message_24',
                'total': 5,
                'new_message_count': 0,
                'messages': [
                    {
                        'id': 'message_24',
                        'text': 'text_4',
                        'metadata': {'created': '2018-07-16T17:18:50+0000'},
                        'sender': {
                            'id': 'another_support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                ],
            },
        ),
        (
            '5b436ece779fb3302cc784bb',
            {
                'include_participants': False,
                'range': {
                    'message_ids': {
                        'newer_than': 'message_21',
                        'older_than': 'message_25',
                    },
                },
            },
            {
                'newest_message_id': 'message_24',
                'total': 5,
                'new_message_count': 0,
                'messages': [
                    {
                        'id': 'message_22',
                        'text': 'text_2',
                        'metadata': {'created': '2018-07-10T11:12:50+0000'},
                        'sender': {
                            'id': 'some_support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                    {
                        'id': 'message_23',
                        'text': 'text_3',
                        'metadata': {'created': '2018-07-13T14:15:50+0000'},
                        'sender': {
                            'id': 'user',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                    {
                        'id': 'message_24',
                        'text': 'text_4',
                        'metadata': {'created': '2018-07-16T17:18:50+0000'},
                        'sender': {
                            'id': 'another_support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                ],
            },
        ),
        (
            '5b436ece779fb3302cc784bb',
            {
                'include_participants': False,
                'range': {
                    'message_ids': {
                        'newer_than': 'message_21',
                        'older_than': 'message_25',
                        'limit': 2,
                    },
                },
            },
            {
                'newest_message_id': 'message_23',
                'total': 5,
                'new_message_count': 0,
                'messages': [
                    {
                        'id': 'message_22',
                        'text': 'text_2',
                        'metadata': {'created': '2018-07-10T11:12:50+0000'},
                        'sender': {
                            'id': 'some_support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                    {
                        'id': 'message_23',
                        'text': 'text_3',
                        'metadata': {'created': '2018-07-13T14:15:50+0000'},
                        'sender': {
                            'id': 'user',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                ],
            },
        ),
        (
            '5b436ece779fb3302cc784bb',
            {
                'include_participants': False,
                'range': {'message_ids': {'limit': 3}},
            },
            {
                'newest_message_id': 'message_23',
                'total': 5,
                'new_message_count': 0,
                'messages': [
                    {
                        'id': 'message_21',
                        'text': 'text_1',
                        'metadata': {'created': '2018-07-04T05:06:50+0000'},
                        'sender': {
                            'id': 'user',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                    {
                        'id': 'message_22',
                        'text': 'text_2',
                        'metadata': {'created': '2018-07-10T11:12:50+0000'},
                        'sender': {
                            'id': 'some_support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                    {
                        'id': 'message_23',
                        'text': 'text_3',
                        'metadata': {'created': '2018-07-13T14:15:50+0000'},
                        'sender': {
                            'id': 'user',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                ],
            },
        ),
        (
            '5b436ece779fb3302cc784bf',
            {
                'include_participants': True,
                'range': {'message_ids': {'limit': 5}},
            },
            {
                'newest_message_id': 'message_65',
                'total': 5,
                'new_message_count': 0,
                'messages': [
                    {
                        'id': 'message_61',
                        'text': 'text_1 +79991112233',
                        'metadata': {'created': '2018-07-04T05:06:50+0000'},
                        'sender': {
                            'id': 'user',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                    {
                        'id': 'message_62',
                        'text': 'text 111122********4442',
                        'metadata': {'created': '2018-07-10T11:12:50+0000'},
                        'sender': {
                            'id': 'some_support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                    {
                        'id': 'message_63',
                        'text': 'text 111122******4444',
                        'metadata': {'created': '2018-07-13T14:15:50+0000'},
                        'sender': {
                            'id': 'user',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                    {
                        'id': 'message_64',
                        'text': 'text 111122******4444',
                        'metadata': {'created': '2018-07-16T17:18:50+0000'},
                        'sender': {
                            'id': 'some_support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                    {
                        'id': 'message_65',
                        'text': 'text_5 1111 2222 3333 4445',
                        'metadata': {'created': '2018-07-19T20:21:50+0000'},
                        'sender': {
                            'id': 'user',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                    },
                ],
                'participants': [
                    {
                        'id': 'some_support',
                        'role': 'support',
                        'avatar_url': 2,
                        'nickname': 'Петр',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'platform': 'yandex',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
            },
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {
                'include_participants': True,
                'range': {'message_ids': {'limit': 3}},
            },
            {
                'newest_message_id': 'message_72',
                'total': 2,
                'new_message_count': 2,
                'messages': [
                    {
                        'id': 'message_71',
                        'text': 'text_1',
                        'metadata': {'created': '2018-07-01T02:03:50+0000'},
                        'sender': {
                            'id': 'driver',
                            'role': 'driver',
                            'sender_type': 'client',
                        },
                    },
                    {
                        'id': 'message_72',
                        'text': 'text_2',
                        'metadata': {
                            'created': '2018-07-04T05:06:50+0000',
                            'order_id': 'some_order_id',
                        },
                        'sender': {
                            'id': 'support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                    },
                ],
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': 4,
                        'nickname': 'Иван',
                    },
                    {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'driver',
                        'is_owner': True,
                    },
                ],
            },
        ),
        (
            '5a436ca8779fb3302cc784bf',
            {'include_participants': True, 'include_metadata': True},
            {
                'newest_message_id': 'message_81',
                'total': 1,
                'new_message_count': 0,
                'messages': [
                    {
                        'id': 'message_81',
                        'text': 'text_1',
                        'metadata': {'created': '2018-07-01T02:03:50+0000'},
                        'sender': {
                            'id': 'facebook_user',
                            'role': 'facebook_user',
                            'sender_type': 'client',
                        },
                    },
                ],
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': None,
                        'nickname': '',
                    },
                    {
                        'id': '1960892827353512',
                        'role': 'facebook_user',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-05T10:59:50+0000',
                    'updated': '2018-07-11T12:15:50+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'chatterbox_id': 'chatterbox_id_fb',
                    'page': '563720454066049',
                },
            },
        ),
        (
            '5b436ece779fb3302cc784bb',
            {
                'include_participants': False,
                'range': {
                    'message_ids': {'newer_than': 'message_25', 'limit': 1},
                },
            },
            {'total': 5, 'new_message_count': 0, 'messages': []},
        ),
    ],
)
@pytest.mark.config(SUPPORT_CHAT_CSAT_CONTROL_ENABLED=True)
async def test_chathistory(
        web_app_client, dummy_tvm_check, chat_id, data, expected_result,
):
    response = await web_app_client.post(
        '/v1/chat/%s/history' % chat_id, data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.OK
    assert await response.json() == expected_result


@pytest.mark.filldb(user_chat_messages='participants')
@pytest.mark.parametrize(
    ('chat_id', 'expected_participants'),
    [
        (
            '5b436ca8779fb3302cc784ba',
            [
                {
                    'avatar_url': 4,
                    'id': 'support',
                    'nickname': 'Иван',
                    'role': 'support',
                },
                {
                    'id': '5b4f5059779fb332fcc26152',
                    'role': 'client',
                    'is_owner': True,
                },
                {'id': 'first_user_id', 'role': 'client'},
                {'id': 'second_user_id', 'role': 'client'},
            ],
        ),
    ],
)
async def test_chathistory_participants(
        web_app_client,
        dummy_tvm_check,
        chat_id: str,
        expected_participants: dict,
):
    response = await web_app_client.post(
        '/v1/chat/{}/history'.format(chat_id),
        json={'include_participants': True},
    )
    assert response.status == 200
    result = await response.json()
    assert result['participants'] == expected_participants


@pytest.mark.parametrize(
    'message_ids_range',
    [
        {'older_than': 'missing_message_id'},
        {'newer_than': 'missing_message_id'},
        {
            'older_than': 'missing_message_id',
            'newer_than': 'missing_message_id',
        },
    ],
)
async def test_invalid_range(
        web_app_client, dummy_tvm_check, message_ids_range,
):
    response = await web_app_client.post(
        '/v1/chat/5b436ece779fb3302cc784bf/history',
        data=json.dumps({'range': {'message_ids': message_ids_range}}),
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    'chat_id, lang_map',
    [
        (
            '5b436ece779fb3302cc784bb',
            {None: 'Иван', 'ru': 'Иван', 'en': 'Ivan'},
        ),
        (
            '5b436ece779fb3302cc784bd',
            {None: 'Петр', 'ru': 'Петр', 'en': 'Petr'},
        ),
    ],
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.filldb(user_chat_messages='translation')
async def test_chat_history_translations(
        web_app_client, dummy_tvm_check, chat_id, lang_map,
):

    for lang, support_name in lang_map.items():
        headers = {}
        if lang:
            headers['Accept-Language'] = lang
        response = await web_app_client.post(
            '/v1/chat/{}/history'.format(chat_id),
            data=json.dumps({'include_participants': True}),
            headers=headers,
        )
        assert response.status == http.HTTPStatus.OK
        chat = await response.json()

        assert chat['participants'][0]['nickname'] == support_name
