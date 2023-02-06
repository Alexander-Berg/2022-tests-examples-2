# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from eats_restapp_support_chat_plugins.generated_tests import *


@pytest.fixture
def _mock_support_chat(mockserver, load_json):
    data = load_json('support_chat_search_response.json')

    def _format_response(chats):
        return {'chats': chats, 'limit': data['limit'], 'total': data['total']}

    @mockserver.json_handler('/support-chat/v1/chat/search')
    def _mock(request):
        assert request.json['limit'] == 50
        assert request.json['offset'] == 0
        chat_ids = request.json.get('chat_ids')
        if chat_ids:
            chats_by_id = {chat['id']: chat for chat in data['chats']}
            return _format_response(
                [chats_by_id[chat_ids[0]]]
                if chat_ids[0] in chats_by_id
                else [],
            )
        chats = data['chats']
        chats = [
            chat
            for chat in chats
            if chat['participants'][1]['id'] in request.json['owners']['ids']
        ]
        role = request.json.get('meta_fields', {}).get('restapp_role')
        if role:
            chats = [
                chat
                for chat in chats
                if chat['metadata'].get('restapp_role') == role
            ]
        author = request.json.get('meta_fields', {}).get('restapp_author')
        if author:
            chats = [
                chat
                for chat in chats
                if chat['metadata'].get('restapp_author') == author
            ]
        topic = request.json.get('meta_fields', {}).get('ticket_subject')
        if topic:
            chats = [
                chat
                for chat in chats
                if chat['metadata'].get('ticket_subject') == topic
            ]
        order_id = request.json.get('meta_fields', {}).get('restapp_order_id')
        if order_id:
            chats = [
                chat
                for chat in chats
                if chat['metadata'].get('restapp_order_id') == order_id
            ]
        return _format_response(chats)

    return _mock


@pytest.mark.parametrize(
    'partner_id,params,expected_response',
    [
        (
            1,
            {},
            [
                {
                    'author': 'test1@yandex.ru',
                    'chat_id': '01',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '222',
                    'topic': 'test_topic',
                    'order_id': '',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': False,
                },
                {
                    'author': 'test2@yandex.ru',
                    'chat_id': '02',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '222',
                    'topic': 'test_topic',
                    'order_id': '',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': False,
                },
            ],
        ),
        (
            # partner 2 can see his own chats only cause of his role
            2,
            {},
            [
                {
                    'author': 'test2@yandex.ru',
                    'chat_id': '02',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '222',
                    'topic': 'test_topic',
                    'order_id': '',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': False,
                },
                {
                    'author': 'test2@yandex.ru',
                    'chat_id': '03',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '333',
                    'topic': 'test_topic_1',
                    'order_id': 'test_order_id',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': True,
                },
            ],
        ),
        (
            1,
            {'chat_id': '01'},
            [
                {
                    'author': 'test1@yandex.ru',
                    'chat_id': '01',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '222',
                    'topic': 'test_topic',
                    'order_id': '',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': False,
                },
            ],
        ),
        (1, {'chat_id': '2_3'}, []),
        (
            1,
            {'author': '2'},
            [
                {
                    'author': 'test2@yandex.ru',
                    'chat_id': '02',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '222',
                    'topic': 'test_topic',
                    'order_id': '',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': False,
                },
            ],
        ),
        (
            2,
            {'place_ids': ['333']},
            [
                {
                    'author': 'test2@yandex.ru',
                    'chat_id': '03',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '333',
                    'topic': 'test_topic_1',
                    'order_id': 'test_order_id',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': True,
                },
            ],
        ),
        (
            2,
            {'topic': 'test_topic'},
            [
                {
                    'author': 'test2@yandex.ru',
                    'chat_id': '02',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '222',
                    'topic': 'test_topic',
                    'order_id': '',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': False,
                },
            ],
        ),
        (
            2,
            {'order_id': 'test_order_id'},
            [
                {
                    'author': 'test2@yandex.ru',
                    'chat_id': '03',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '333',
                    'topic': 'test_topic_1',
                    'order_id': 'test_order_id',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': True,
                },
            ],
        ),
        (
            3,
            {'order_id': 'test_order_id'},
            [
                {
                    'author': 'test2@yandex.ru',
                    'chat_id': '03',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '333',
                    'topic': 'test_topic_1',
                    'order_id': 'test_order_id',
                    'status': 'open',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': True,
                },
                {
                    'author': 'test3@yandex.ru',
                    'chat_id': '04',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '333',
                    'topic': 'test_topic_1',
                    'order_id': 'test_order_id',
                    'status': 'pending',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': True,
                },
                {
                    'author': 'test3@yandex.ru',
                    'chat_id': '05',
                    'last_message_created_at': '2020-09-04T15:26:43+00:00',
                    'last_message_text': 'hi2',
                    'new_message_count': 0,
                    'place_id': '333',
                    'topic': 'test_topic_1',
                    'order_id': 'test_order_id',
                    'status': 'solved',
                    'created_at': '2020-09-04T15:24:43+00:00',
                    'ask_csat': True,
                },
            ],
        ),
    ],
)
async def test_chat_list_get(
        _mock_support_chat,
        taxi_eats_restapp_support_chat,
        partner_id,
        params,
        expected_response,
):
    response = await taxi_eats_restapp_support_chat.get(
        '/4.0/restapp-front/support_chat/v1/chat/list',
        headers={'X-YaEda-PartnerId': str(partner_id)},
        params=params,
    )
    assert response.status == 200
    assert response.json()['chats'] == expected_response
    assert _mock_support_chat.times_called == 1


@pytest.mark.config(
    EATS_RESTAPP_SUPPORT_CHAT_SEARCH_SETTINGS={
        'substring_search': True,
        'translate_keyboard_layout': True,
        'text_search_limit': 6,
    },
)
@pytest.mark.parametrize(
    'text,chats_found,expected_request_text_values',
    [
        ('Ghbdtn', True, ['Ghbdtn']),
        ('Ghbdtn', False, ['Ghbdtn', 'Привет']),
        ('12345', False, ['12345']),
        ('123456789', False, ['123456']),
    ],
)
async def test_chat_list_get_search_by_text(
        _mock_support_chat,
        taxi_eats_restapp_support_chat,
        mockserver,
        load_json,
        text,
        chats_found,
        expected_request_text_values,
):
    request_text_values = []

    @mockserver.json_handler('/support-chat/v1/chat/search_by_text')
    def _mock_search_by_text(request):
        assert request.json['text']
        request_text_values.append(request.json['text'])
        assert request.json['substring_search']
        assert request.json['limit'] == 50
        assert request.json['offset'] == 0
        if chats_found:
            data = load_json('support_chat_search_response.json')
            chats = [data['chats'][0]]
        else:
            chats = []
        return {'chats': chats, 'limit': 50, 'total': 0}

    response = await taxi_eats_restapp_support_chat.get(
        '/4.0/restapp-front/support_chat/v1/chat/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'text': text},
    )
    assert response.status == 200
    assert _mock_support_chat.times_called == 0
    assert _mock_search_by_text.times_called == len(request_text_values)
    assert request_text_values == expected_request_text_values


@pytest.mark.parametrize(
    'calendar_response,sla_value,work_in_holidays,topic,expected_sla',
    [
        (
            {'holidays': [{'date': '2020-09-04', 'type': 'weekday'}]},
            4,
            False,
            'test_topic',
            '2020-09-04T19:24:43+00:00',
        ),
        (
            {
                'holidays': [
                    {'date': '2020-09-04', 'type': 'weekend'},
                    {'date': '2020-09-05', 'type': 'weekday'},
                ],
            },
            4,
            False,
            'test_topic',
            '2020-09-05T01:00:00+00:00',
        ),
        (
            {
                'holidays': [
                    {'date': '2020-09-04', 'type': 'weekend'},
                    {'date': '2020-09-05', 'type': 'weekday'},
                ],
            },
            4,
            True,
            'test_topic',
            '2020-09-04T19:24:43+00:00',
        ),
        (
            {
                'holidays': [
                    {'date': '2020-09-04', 'type': 'weekday'},
                    {'date': '2020-09-05', 'type': 'weekend'},
                    {'date': '2020-09-06', 'type': 'weekday'},
                ],
            },
            12,
            False,
            'test_topic',
            '2020-09-06T03:24:43+00:00',
        ),
    ],
)
async def test_chat_list_get_sla(
        mockserver,
        _mock_support_chat,
        taxi_eats_restapp_support_chat,
        calendar_response,
        sla_value,
        work_in_holidays,
        topic,
        expected_sla,
        taxi_config,
):
    @mockserver.json_handler('/yandex-calendar/internal/get-holidays')
    def _mock(request):
        return calendar_response

    taxi_config.set_values(
        {
            'EATS_RESTAPP_SUPPORT_CHAT_TOPICS_SLA_SETTINGS': {
                '__default__': {'sla_value': 0, 'work_in_holidays': False},
                topic: {
                    'sla_value': sla_value,
                    'work_in_holidays': work_in_holidays,
                },
            },
        },
    )

    partner_id = 1
    params = {'chat_id': '01'}
    response = await taxi_eats_restapp_support_chat.get(
        '/4.0/restapp-front/support_chat/v1/chat/list',
        headers={'X-YaEda-PartnerId': str(partner_id)},
        params=params,
    )

    assert response.status == 200
    chats = response.json()['chats']
    assert len(chats) == 1
    assert chats[0]['sla'] == expected_sla
