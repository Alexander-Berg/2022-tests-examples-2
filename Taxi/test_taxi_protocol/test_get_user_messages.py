# pylint: disable=too-many-arguments, too-many-lines
import json

import pytest

from taxi import discovery
from taxi.clients import support_chat

from test_taxi_protocol import plugins as conftest


@pytest.mark.translations(
    client_messages={
        'user_chat_csat.horrible': {'ru': 'Ужасно', 'en': 'Horrible'},
        'user_chat_csat.bad': {'ru': 'Плохо', 'en': 'Bad'},
        'user_chat_csat.normal': {'ru': 'Нормально', 'en': 'Normal'},
        'user_chat_csat.good': {'ru': 'Хорошо', 'en': 'Good'},
        'user_chat_csat.amazing': {'ru': 'Отлично', 'en': 'Amazing'},
        'user_chat_csat_reasons.template_answer': {
            'ru': 'Ответ шаблоном',
            'en': 'Template answer',
        },
        'user_chat_csat_reasons.problem_not_solved': {
            'ru': 'Проблема не решена',
            'en': 'Problem not solved',
        },
        'user_chat_csat_reasons.disagree_solution': {
            'ru': 'Не согласен с решением',
            'en': 'Disagree solution',
        },
        'user_chat_csat_reasons.long_answer': {
            'ru': 'Долгий ответ',
            'en': 'Long answer',
        },
        'user_chat_csat_reasons.new_key': {
            'ru': 'Другая причина',
            'en': 'Another reason',
        },
        'user_chat_csat_reasons.long_initial_answer': {
            'ru': 'Долгий первичный ответ',
            'en': 'Long initial response',
        },
        'user_chat_csat_reasons.long_interval_answer': {
            'ru': 'Задержка между сообщениями',
            'en': 'Long interval between messages',
        },
        'user_chat_csat.quality_score': {
            'ru': 'Оцените качество службы поддержки сервиса',
            'en': 'Score the quality of the service support',
        },
        'user_chat_csat.response_speed_score': {
            'ru': 'Оцените скорость ответа специалиста поддержки',
            'en': 'Score the response speed of the support specialist',
        },
    },
)
@pytest.mark.config(USER_CHAT_USE_EXPERIMENTS_CSAT=True)
@pytest.mark.parametrize(
    (
        'headers',
        'url',
        'data',
        'ask_csat',
        'user_locale',
        'expected_chat_type',
        'expected_code',
        'lang',
        'expected_result',
        'read_messages',
        'expected_owner',
        'expected_owner_role',
        'expected_platform',
        'message_metadata',
    ),
    [
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88b',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {'id': '5ff4901c583745e089e55be4a8c7a88b'},
            False,
            'ru',
            'visible',
            401,
            'ru',
            None,
            False,
            None,
            None,
            None,
            {},
        ),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88b',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {'id': '5ff4901c583745e089e55be4a8c7a88c'},
            False,
            'ru',
            'visible',
            401,
            'ru',
            None,
            False,
            None,
            None,
            None,
            {},
        ),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {'id': '5ff4901c583745e089e55be4a8c7a88d'},
            False,
            'ru',
            'visible',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '000000000000000000000001',
            'client',
            'yandex',
            {},
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/get_user_messages',
            {},
            False,
            'ru',
            'visible',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '000000000000000000000001',
            'client',
            'yandex',
            {},
        ),
        (
            {
                'X-Yandex-UID': '123',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/realtime/get_user_messages',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'eats_client',
            'yandex',
            {},
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/get_user_messages'
            '/?service=help_yandex_ru',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'help_yandex_client',
            'help_yandex',
            {},
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/get_user_messages'
            '/?service=labs_admin_yandex_ru',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'labs_admin_yandex_client',
            'labs_admin_yandex',
            {},
        ),
        (
            {'X-YaTaxi-User': 'eats_user_id=123'},
            '/eats/v1/support_chat/v1/realtime/get_user_messages'
            '/?service=eats_app',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'eats_app_client',
            'eats_app',
            {},
        ),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {'id': '5ff4901c583745e089e55be4a8c7a88e'},
            False,
            'ru',
            'visible',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'avatar_url': 'support_avatar',
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'messages': [
                    {
                        'id': 'message_id',
                        'author': 'user',
                        'body': 'Привет!',
                        'timestamp': '2018-10-20T12:34:56',
                        'type': 'text',
                        'metadata': {'created': '2018-10-20T12:34:56'},
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                    },
                ],
                'new_messages': 0,
                'support_name': 'саппорт',
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                ],
            },
            True,
            '000000000000000000000002',
            'client',
            'yandex',
            {},
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e'},
            '/4.0/support_chat/v1/regular/get_user_messages',
            {},
            False,
            'ru',
            'visible',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'avatar_url': 'support_avatar',
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'messages': [
                    {
                        'id': 'message_id',
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                        'author': 'user',
                        'body': 'Привет!',
                        'timestamp': '2018-10-20T12:34:56',
                        'type': 'text',
                        'metadata': {'created': '2018-10-20T12:34:56'},
                    },
                ],
                'new_messages': 0,
                'support_name': 'саппорт',
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                ],
            },
            True,
            '000000000000000000000002',
            'client',
            'yandex',
            {},
        ),
        (
            {
                'X-Yandex-UID': '1234',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e',
            },
            '/4.0/support_chat/v1/realtime/get_user_messages',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'avatar_url': 'support_avatar',
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'messages': [
                    {
                        'id': 'message_id',
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                        'author': 'user',
                        'body': 'Привет!',
                        'timestamp': '2018-10-20T12:34:56',
                        'type': 'text',
                        'metadata': {
                            'attachments': [
                                {
                                    'id': (
                                        '91bd810f1195f140024130b901cb929aa12'
                                        'b814f'
                                    ),
                                    'link': (
                                        'support_chat/v1/realtime/som'
                                        'e_chat_id/download_file/91bd810f1'
                                        '195f140024130b901cb929aa12b814f/'
                                        '?service=eats'
                                    ),
                                    'link_preview': (
                                        'support_chat/v1/real'
                                        'time/some_chat_id/downloa'
                                        'd_file/91bd810f1195f14002'
                                        '4130b901cb929aa12b814f/?s'
                                        'ize=preview&service=eats'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'file.pdf',
                                    'preview_height': 84,
                                    'preview_width': 150,
                                    'size': 1753527,
                                    'source': 'mds',
                                },
                            ],
                            'created': '2018-10-20T12:34:56',
                        },
                    },
                ],
                'new_messages': 0,
                'support_name': 'саппорт',
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                ],
            },
            True,
            '1234',
            'eats_client',
            'yandex',
            {
                'attachments': [
                    {
                        'id': '91bd810f1195f140024130b901cb929aa12b814f',
                        'mimetype': 'image/png',
                        'size': 1753527,
                        'source': 'mds',
                        'preview_width': 150,
                        'preview_height': 84,
                        'name': 'file.pdf',
                    },
                ],
            },
        ),
        (
            {'X-Yandex-UID': '1234'},
            '/4.0/support_chat/v1/realtime/get_user_messages'
            '/?service=help_yandex_ru',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'avatar_url': 'support_avatar',
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'messages': [
                    {
                        'id': 'message_id',
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                        'author': 'user',
                        'body': 'Привет!',
                        'timestamp': '2018-10-20T12:34:56',
                        'type': 'text',
                        'metadata': {
                            'attachments': [
                                {
                                    'id': (
                                        '91bd810f1195f140024130b901cb929aa12'
                                        'b814f'
                                    ),
                                    'link': (
                                        'support_chat/v1/realtime/som'
                                        'e_chat_id/download_file/91bd810f1'
                                        '195f140024130b901cb929aa12b814f/'
                                        '?service=help_yandex_ru'
                                    ),
                                    'link_preview': (
                                        'support_chat/v1/real'
                                        'time/some_chat_id/downloa'
                                        'd_file/91bd810f1195f14002'
                                        '4130b901cb929aa12b814f/?s'
                                        'ize=preview&service=help_yandex_ru'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'file.pdf',
                                    'preview_height': 84,
                                    'preview_width': 150,
                                    'size': 1753527,
                                    'source': 'mds',
                                },
                            ],
                            'created': '2018-10-20T12:34:56',
                        },
                    },
                ],
                'new_messages': 0,
                'support_name': 'саппорт',
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                ],
            },
            True,
            '1234',
            'help_yandex_client',
            'help_yandex',
            {
                'attachments': [
                    {
                        'id': '91bd810f1195f140024130b901cb929aa12b814f',
                        'mimetype': 'image/png',
                        'size': 1753527,
                        'source': 'mds',
                        'preview_width': 150,
                        'preview_height': 84,
                        'name': 'file.pdf',
                    },
                ],
            },
        ),
        (
            {'X-Yandex-UID': '1234'},
            '/4.0/support_chat/v1/realtime/get_user_messages'
            '/?service=labs_admin_yandex_ru',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'avatar_url': 'support_avatar',
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'messages': [
                    {
                        'id': 'message_id',
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                        'author': 'user',
                        'body': 'Привет!',
                        'timestamp': '2018-10-20T12:34:56',
                        'type': 'text',
                        'metadata': {
                            'attachments': [
                                {
                                    'id': (
                                        '91bd810f1195f140024130b901cb929aa12'
                                        'b814f'
                                    ),
                                    'link': (
                                        'lab/support_chat/v1/realtime/som'
                                        'e_chat_id/download_file/91bd810f1'
                                        '195f140024130b901cb929aa12b814f/'
                                        '?service=labs_admin_yandex_ru'
                                    ),
                                    'link_preview': (
                                        'lab/support_chat/v1/real'
                                        'time/some_chat_id/downloa'
                                        'd_file/91bd810f1195f14002'
                                        '4130b901cb929aa12b814f/?size=preview'
                                        '&service=labs_admin_yandex_ru'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'file.pdf',
                                    'preview_height': 84,
                                    'preview_width': 150,
                                    'size': 1753527,
                                    'source': 'mds',
                                },
                            ],
                            'created': '2018-10-20T12:34:56',
                        },
                    },
                ],
                'new_messages': 0,
                'support_name': 'саппорт',
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                ],
            },
            True,
            '1234',
            'labs_admin_yandex_client',
            'labs_admin_yandex',
            {
                'attachments': [
                    {
                        'id': '91bd810f1195f140024130b901cb929aa12b814f',
                        'mimetype': 'image/png',
                        'size': 1753527,
                        'source': 'mds',
                        'preview_width': 150,
                        'preview_height': 84,
                        'name': 'file.pdf',
                    },
                ],
            },
        ),
        (
            {'X-YaTaxi-User': 'eats_user_id=1234'},
            '/eats/v1/support_chat/v1/realtime/get_user_messages'
            '/?service=eats_app',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'avatar_url': 'support_avatar',
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'messages': [
                    {
                        'id': 'message_id',
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                        'author': 'user',
                        'body': 'Привет!',
                        'timestamp': '2018-10-20T12:34:56',
                        'type': 'text',
                        'metadata': {
                            'attachments': [
                                {
                                    'id': (
                                        '91bd810f1195f140024130b901cb929aa12'
                                        'b814f'
                                    ),
                                    'link': (
                                        'support_chat/v1/realtime/som'
                                        'e_chat_id/download_file/91bd810f1'
                                        '195f140024130b901cb929aa12b814f/'
                                        '?service=eats_app'
                                    ),
                                    'link_preview': (
                                        'support_chat/v1/real'
                                        'time/some_chat_id/downloa'
                                        'd_file/91bd810f1195f14002'
                                        '4130b901cb929aa12b814f/?size=preview'
                                        '&service=eats_app'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'file.pdf',
                                    'preview_height': 84,
                                    'preview_width': 150,
                                    'size': 1753527,
                                    'source': 'mds',
                                },
                            ],
                            'created': '2018-10-20T12:34:56',
                        },
                    },
                ],
                'new_messages': 0,
                'support_name': 'саппорт',
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                ],
            },
            True,
            '1234',
            'eats_app_client',
            'eats_app',
            {
                'attachments': [
                    {
                        'id': '91bd810f1195f140024130b901cb929aa12b814f',
                        'mimetype': 'image/png',
                        'size': 1753527,
                        'source': 'mds',
                        'preview_width': 150,
                        'preview_height': 84,
                        'name': 'file.pdf',
                    },
                ],
            },
        ),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {'id': '5ff4901c583745e089e55be4a8c7a88e'},
            True,
            'ru',
            'visible',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'ask_csat': True,
                'new_messages': 0,
                'avatar_url': 'support_avatar',
                'support_name': 'саппорт',
                'csat_new_version': False,
                'csat_options': [
                    {
                        'option_key': 'horrible',
                        'option_name': 'Ужасно',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Долгий ответ',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Ответ шаблоном',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Проблема не решена',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Не согласен с решением',
                            },
                        ],
                    },
                    {
                        'option_key': 'bad',
                        'option_name': 'Плохо',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Долгий ответ',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Ответ шаблоном',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Проблема не решена',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Не согласен с решением',
                            },
                        ],
                    },
                    {
                        'option_key': 'normal',
                        'option_name': 'Нормально',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Долгий ответ',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Ответ шаблоном',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Проблема не решена',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Не согласен с решением',
                            },
                        ],
                    },
                    {
                        'option_key': 'good',
                        'option_name': 'Хорошо',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Долгий ответ',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Ответ шаблоном',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Проблема не решена',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Не согласен с решением',
                            },
                        ],
                    },
                    {
                        'option_key': 'amazing',
                        'option_name': 'Отлично',
                        'reasons': [],
                    },
                ],
                'messages': [
                    {
                        'id': 'message_id',
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                        'author': 'user',
                        'body': 'Привет!',
                        'type': 'text',
                        'timestamp': '2018-10-20T12:34:56',
                        'metadata': {'created': '2018-10-20T12:34:56'},
                    },
                ],
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                ],
            },
            True,
            '000000000000000000000002',
            'client',
            'yandex',
            {},
        ),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88f',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {'id': '5ff4901c583745e089e55be4a8c7a88f'},
            True,
            'ru',
            'visible',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'ask_csat': True,
                'new_messages': 0,
                'avatar_url': 'support_avatar',
                'support_name': 'саппорт',
                'csat_new_version': True,
                'csat_options': {
                    'questions': [
                        {
                            'id': 'quality_score',
                            'text': (
                                'Оцените качество службы поддержки сервиса'
                            ),
                            'with_input': False,
                            'values': [
                                {
                                    'id': 'horrible',
                                    'text': 'Ужасно',
                                    'with_input': False,
                                    'reasons': [
                                        {
                                            'id': 'long_answer',
                                            'text': 'Долгий ответ',
                                            'reasons': [
                                                {
                                                    'id': (
                                                        'long_initial_answer'
                                                    ),
                                                    'text': (
                                                        'Долгий первичный '
                                                        'ответ'
                                                    ),
                                                    'with_input': False,
                                                },
                                                {
                                                    'id': (
                                                        'long_interval_answer'
                                                    ),
                                                    'text': (
                                                        'Задержка между '
                                                        'сообщениями'
                                                    ),
                                                    'with_input': False,
                                                },
                                            ],
                                            'with_input': False,
                                        },
                                        {
                                            'id': 'problem_not_solved',
                                            'text': 'Проблема не решена',
                                            'with_input': False,
                                        },
                                        {
                                            'id': 'template_answer',
                                            'text': 'Ответ шаблоном',
                                            'with_input': False,
                                        },
                                        {
                                            'id': 'disagree_solution',
                                            'text': 'Не согласен с решением',
                                            'with_input': False,
                                        },
                                    ],
                                },
                                {
                                    'id': 'good',
                                    'text': 'Хорошо',
                                    'with_input': False,
                                },
                                {
                                    'id': 'amazing',
                                    'text': 'Отлично',
                                    'with_input': False,
                                },
                            ],
                        },
                        {
                            'id': 'response_speed_score',
                            'text': (
                                'Оцените скорость ответа специалиста поддержки'
                            ),
                            'with_input': False,
                            'values': [
                                {
                                    'id': 'horrible',
                                    'text': 'Ужасно',
                                    'with_input': False,
                                },
                                {
                                    'id': 'good',
                                    'text': 'Хорошо',
                                    'with_input': False,
                                },
                                {
                                    'id': 'amazing',
                                    'text': 'Отлично',
                                    'with_input': False,
                                },
                            ],
                        },
                    ],
                },
                'messages': [
                    {
                        'id': 'message_id',
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                        'author': 'user',
                        'body': 'Привет!',
                        'type': 'text',
                        'timestamp': '2018-10-20T12:34:56',
                        'metadata': {'created': '2018-10-20T12:34:56'},
                    },
                ],
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'саппорт',
                        'role': 'support',
                    },
                ],
            },
            True,
            '000000000000000000000003',
            'client',
            'yandex',
            {},
        ),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {'id': '5ff4901c583745e089e55be4a8c7a88e'},
            True,
            'en',
            'visible',
            200,
            'en',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'ask_csat': True,
                'new_messages': 0,
                'avatar_url': 'support_avatar',
                'support_name': 'support_name',
                'csat_new_version': False,
                'csat_options': [
                    {
                        'option_key': 'horrible',
                        'option_name': 'Horrible',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Long answer',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Template answer',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Problem not solved',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Disagree solution',
                            },
                        ],
                    },
                    {
                        'option_key': 'bad',
                        'option_name': 'Bad',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Long answer',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Template answer',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Problem not solved',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Disagree solution',
                            },
                        ],
                    },
                    {
                        'option_key': 'normal',
                        'option_name': 'Normal',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Long answer',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Template answer',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Problem not solved',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Disagree solution',
                            },
                        ],
                    },
                    {
                        'option_key': 'good',
                        'option_name': 'Good',
                        'reasons': [
                            {
                                'reason_key': 'long_answer',
                                'reason_name': 'Long answer',
                            },
                            {
                                'reason_key': 'template_answer',
                                'reason_name': 'Template answer',
                            },
                            {
                                'reason_key': 'problem_not_solved',
                                'reason_name': 'Problem not solved',
                            },
                            {
                                'reason_key': 'disagree_solution',
                                'reason_name': 'Disagree solution',
                            },
                        ],
                    },
                    {
                        'option_key': 'amazing',
                        'option_name': 'Amazing',
                        'reasons': [],
                    },
                ],
                'messages': [
                    {
                        'id': 'message_id',
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                        'author': 'user',
                        'body': 'Привет!',
                        'type': 'text',
                        'timestamp': '2018-10-20T12:34:56',
                        'metadata': {'created': '2018-10-20T12:34:56'},
                    },
                ],
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'support_name',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'support_name',
                        'role': 'support',
                    },
                ],
            },
            True,
            '000000000000000000000002',
            'client',
            'yandex',
            {},
        ),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {'id': '5ff4901c583745e089e55be4a8c7a88e'},
            False,
            'ru',
            'visible',
            200,
            None,
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'avatar_url': 'support_avatar',
                'chat_open': True,
                'chat_visible': True,
                'chat_id': 'some_chat_id',
                'messages': [
                    {
                        'id': 'message_id',
                        'sender': {
                            'id': 'client_id',
                            'platform': 'yandex',
                            'role': 'client',
                        },
                        'text': 'Привет!',
                        'author': 'user',
                        'body': 'Привет!',
                        'timestamp': '2018-10-20T12:34:56',
                        'type': 'text',
                        'metadata': {'created': '2018-10-20T12:34:56'},
                    },
                ],
                'new_messages': 0,
                'support_name': 'default support',
                'participants': [
                    {
                        'id': 'client_id',
                        'platform': 'yandex',
                        'role': 'client',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'support_id',
                        'nickname': 'default support',
                        'role': 'support',
                    },
                    {
                        'avatar_url': 'support_avatar',
                        'id': 'another_support_id',
                        'nickname': 'default support',
                        'role': 'support',
                    },
                ],
            },
            True,
            '000000000000000000000002',
            'client',
            'yandex',
            {},
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/regular/get_user_messages?service=drive',
            {},
            False,
            'ru',
            'visible',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'carsharing_client',
            'yandex',
            {},
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/get_user_messages'
            '/?service=scouts',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'scouts_client',
            'scouts',
            {},
        ),
        (
            {'X-Taxi-Storage-Id': '12'},
            '/4.0/support_chat/v1/realtime/get_user_messages'
            '/?service=lavka_storages',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'lavka_storages_client',
            'lavka_storages',
            {},
        ),
        (
            {'X-Eats-Session': 'test-session-header'},
            'eats/v1/website_support_chat/v1/realtime/get_user_messages'
            '/?service=website',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'website_client',
            'website',
            {},
        ),
        (
            {'X-YaEda-PartnerId': '12'},
            'eats/v1/restapp_support_chat/v1/realtime/get_user_messages'
            '/?service=restapp',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'restapp_client',
            'restapp',
            {},
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/get_user_messages'
            '/?service=market',
            {},
            False,
            'ru',
            'open',
            200,
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'ask_csat': False,
                'chat_open': False,
                'chat_visible': False,
                'messages': [],
                'participants': [],
                'new_messages': 0,
            },
            False,
            '123',
            'market_client',
            'market',
            {},
        ),
    ],
)
async def test_get_user_messages(
        monkeypatch,
        protocol_client,
        protocol_app,
        mock,
        patch,
        mock_chat_defaults,
        mock_get_users,
        mock_exp3_get_values,
        headers,
        url,
        data,
        ask_csat,
        user_locale,
        expected_chat_type,
        expected_code,
        lang,
        expected_result,
        read_messages,
        expected_owner,
        expected_owner_role,
        expected_platform,
        message_metadata,
):
    async def search(self, owner_id, *args, **kwargs):

        assert kwargs.get('chat_type') == expected_chat_type
        test_headers = kwargs.get('headers') or {}
        header_lang = test_headers.get('Accept-Language', 'default')

        translations = {
            'ru': 'саппорт',
            'en': 'support_name',
            'default': 'default support',
        }
        if owner_id not in [
                '000000000000000000000002',
                '000000000000000000000003',
                '1234',
        ]:
            return {'chats': []}
        chats = {
            'chats': [
                {
                    'id': 'some_chat_id',
                    'status': {'is_open': True, 'is_visible': True},
                    'participants': [
                        {
                            'id': 'client_id',
                            'role': 'client',
                            'platform': 'yandex',
                        },
                        {
                            'id': 'support_id',
                            'role': 'support',
                            'nickname': translations.get(header_lang),
                            'avatar_url': 'support_avatar',
                        },
                        {
                            'id': 'another_support_id',
                            'role': 'support',
                            'nickname': translations.get(header_lang),
                            'avatar_url': 'support_avatar',
                        },
                    ],
                    'messages': [
                        {
                            'id': 'message_id',
                            'text': 'Привет!',
                            'metadata': {
                                'created': '2018-10-20T12:34:56',
                                **message_metadata,
                            },
                            'sender': {
                                'id': 'client_id',
                                'role': 'client',
                                'platform': 'yandex',
                            },
                        },
                    ],
                    'metadata': {
                        'ask_csat': ask_csat,
                        'new_messages': 0,
                        'user_locale': user_locale,
                    },
                    'actions': [],
                    'view': {'show_message_input': True},
                },
            ],
        }
        if owner_id == '000000000000000000000003':
            chats['chats'][0]['metadata']['service'] = 'dummy_service'
        return chats

    @mock
    async def read(*args, **kwargs):
        pass

    monkeypatch.setattr(
        protocol_app, 'passport', conftest.MockPassportClient(),
    )
    monkeypatch.setattr(support_chat.SupportChatApiClient, 'search', search)
    monkeypatch.setattr(support_chat.SupportChatApiClient, 'read', read)
    if lang:
        headers['Accept-Language'] = lang

    response = await protocol_client.post(
        url, headers=headers, data=json.dumps(data),
    )
    assert response.status == expected_code
    if expected_result:
        assert await response.json() == expected_result

    if read_messages:
        add_update_call = read.calls[0]
        assert add_update_call['args'] == tuple()
        add_update_call['kwargs'].pop('log_extra')
        assert add_update_call['kwargs'] == {
            'chat_id': 'some_chat_id',
            'owner_id': expected_owner,
            'owner_role': expected_owner_role,
            'platform': expected_platform,
        }
    else:
        assert not read.calls


@pytest.mark.parametrize('auto_read', [True, False])
@pytest.mark.parametrize(
    'headers, url, data',
    [
        (
            {
                'X-Real-IP': '1.1.1.1',
                'Accept-Language': 'ru',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {'id': '5ff4901c583745e089e55be4a8c7a88e'},
        ),
        (
            {
                'Accept-Language': 'ru',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e',
            },
            '/4.0/support_chat/v1/regular/get_user_messages',
            {},
        ),
        (
            {
                'Accept-Language': 'ru',
                'X-Yandex-UID': '1234',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e',
            },
            '/4.0/support_chat/v1/realtime/get_user_messages',
            {},
        ),
        (
            {'Accept-Language': 'ru', 'X-Yandex-UID': '1234'},
            '/4.0/support_chat/v1/realtime/get_user_messages'
            '/?service=help_yandex_ru',
            {},
        ),
    ],
)
@pytest.mark.usefixtures('mock_passport')
async def test_auto_read(
        patch_aiohttp_session,
        response_mock,
        mock_get_users,
        protocol_app,
        protocol_client,
        auto_read,
        headers,
        url,
        data,
):
    support_chat_url = discovery.find_service('support_chat').url
    protocol_app.config.TAXI_PROTOCOL_GET_USER_MESSAGES_AUTO_READ = auto_read

    @patch_aiohttp_session(support_chat_url + '/v1/chat/search', 'POST')
    def search(method, url, **kwargs):
        return response_mock(
            json={
                'chats': [
                    {
                        'id': 'some_chat_id',
                        'status': {'is_open': True, 'is_visible': True},
                        'participants': [
                            {'id': 'client_id', 'role': 'client'},
                            {
                                'id': 'support_id',
                                'role': 'support',
                                'nickname': 'саппорт',
                                'avatar_url': 'support_avatar',
                            },
                            {
                                'id': 'another_support_id',
                                'role': 'support',
                                'nickname': 'саппорт',
                                'avatar_url': 'support_avatar',
                            },
                        ],
                        'messages': [
                            {
                                'id': 'message_id',
                                'text': 'Привет!',
                                'metadata': {'created': '2018-10-20T12:34:56'},
                                'sender': {
                                    'id': 'client_id',
                                    'role': 'client',
                                },
                            },
                        ],
                        'metadata': {
                            'ask_csat': False,
                            'new_messages': 0,
                            'user_locale': 'ru',
                        },
                        'actions': [],
                        'view': {'show_message_input': True},
                    },
                ],
            },
        )

    @patch_aiohttp_session(
        support_chat_url + '/v1/chat/some_chat_id/read', 'POST',
    )
    def read(method, url, **kwargs):
        return response_mock({})

    response = await protocol_client.post(url, headers=headers, json=data)
    assert response.status == 200

    assert search.calls

    if auto_read:
        assert read.calls
    else:
        assert not read.calls
