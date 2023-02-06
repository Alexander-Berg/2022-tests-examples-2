# pylint: disable=too-many-arguments,too-many-lines
import json

import pytest

from taxi.clients import support_chat

from test_taxi_protocol import plugins as conftest


@pytest.mark.parametrize(
    'headers, url, data, chat_id, expected_code, lang, expected_result,'
    'expected_owner_id, expected_owner_role, message_metadata',
    [
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88v'},
            '/4.0/support_chat/v1/regular/supporthistorydetails',
            {'user_id': '5ff4901c583745e089e55be4a8c7a88v'},
            '59e4a18c779fb327d02e4c48',
            401,
            'ru',
            None,
            None,
            None,
            {},
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistorydetails',
            {'user_id': '5ff4901c583745e089e55be4a8c7a88d'},
            '59e4a18c779fb327d02e4c49',
            200,
            'ru',
            {
                'avatar_url': 'test1',
                'support_name': 'имя1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {
                            'id': '000000000000000000000000',
                            'role': 'client',
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'имя1',
                        'role': 'support',
                    },
                    {'id': '000000000000000000000000', 'role': 'client'},
                ],
            },
            '000000000000000000000000',
            'client',
            {},
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistorydetails',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'ru',
            {
                'avatar_url': 'test1',
                'support_name': 'имя1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {
                            'id': '000000000000000000000000',
                            'role': 'client',
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'имя1',
                        'role': 'support',
                    },
                    {'id': '000000000000000000000000', 'role': 'client'},
                ],
            },
            '000000000000000000000000',
            'client',
            {},
        ),
        (
            {
                'X-Yandex-UID': '123',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/realtime/supporthistorydetails',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'ru',
            {
                'avatar_url': 'test1',
                'support_name': 'имя1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {'id': '123', 'role': 'eats_client'},
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'имя1',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'eats_client'},
                ],
            },
            '123',
            'eats_client',
            {},
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistorydetails',
            {'user_id': '5ff4901c583745e089e55be4a8c7a88d'},
            '59e4a18c779fb327d02e4c49',
            200,
            'en',
            {
                'avatar_url': 'test1',
                'support_name': 'name1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {
                            'id': '000000000000000000000000',
                            'role': 'client',
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'name1',
                        'role': 'support',
                    },
                    {'id': '000000000000000000000000', 'role': 'client'},
                ],
            },
            '000000000000000000000000',
            'client',
            {},
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistorydetails',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'en',
            {
                'avatar_url': 'test1',
                'support_name': 'name1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {
                            'id': '000000000000000000000000',
                            'role': 'client',
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'name1',
                        'role': 'support',
                    },
                    {'id': '000000000000000000000000', 'role': 'client'},
                ],
            },
            '000000000000000000000000',
            'client',
            {},
        ),
        (
            {
                'X-Yandex-UID': '123',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/realtime/supporthistorydetails',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'en',
            {
                'avatar_url': 'test1',
                'support_name': 'name1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {'id': '123', 'role': 'eats_client'},
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'name1',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'eats_client'},
                ],
            },
            '123',
            'eats_client',
            {},
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistorydetails',
            {'user_id': '5ff4901c583745e089e55be4a8c7a88d'},
            '59e4a18c779fb327d02e4c49',
            200,
            None,
            {
                'avatar_url': 'test1',
                'support_name': 'default support',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {
                            'id': '000000000000000000000000',
                            'role': 'client',
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'default support',
                        'role': 'support',
                    },
                    {'id': '000000000000000000000000', 'role': 'client'},
                ],
            },
            '000000000000000000000000',
            'client',
            {},
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d'},
            '/4.0/support_chat/v1/regular/supporthistorydetails',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            None,
            {
                'avatar_url': 'test1',
                'support_name': 'default support',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {
                            'id': '000000000000000000000000',
                            'role': 'client',
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'default support',
                        'role': 'support',
                    },
                    {'id': '000000000000000000000000', 'role': 'client'},
                ],
            },
            '000000000000000000000000',
            'client',
            {},
        ),
        (
            {
                'X-Yandex-UID': '123',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88d',
            },
            '/4.0/support_chat/v1/realtime/supporthistorydetails',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            None,
            {
                'avatar_url': 'test1',
                'support_name': 'default support',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'sender': {'id': '123', 'role': 'eats_client'},
                        'metadata': {
                            'created': '2017-12-11T18:08:56+0300',
                            'attachments': [
                                {
                                    'id': (
                                        '91bd810f1195f140024130b901cb929aa12'
                                        'b814f'
                                    ),
                                    'link': (
                                        'support_chat/v1/realtime/59e'
                                        '4a18c779fb327d02e4c49/download_fi'
                                        'le/91bd810f1195f140024130b901cb92'
                                        '9aa12b814f/?service=eats'
                                    ),
                                    'link_preview': (
                                        'support_chat/v1/real'
                                        'time/59e4a18c779fb327d02e'
                                        '4c49/download_file/91bd81'
                                        '0f1195f140024130b901cb929'
                                        'aa12b814f/?size=preview&'
                                        'service=eats'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'file.pdf',
                                    'preview_height': 84,
                                    'preview_width': 150,
                                    'size': 1753527,
                                    'source': 'mds',
                                },
                            ],
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'sender': {'id': 'support_id', 'role': 'support'},
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'default support',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'eats_client'},
                ],
            },
            '123',
            'eats_client',
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
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/supporthistorydetails'
            '/?service=help_yandex_ru',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            None,
            {
                'avatar_url': 'test1',
                'support_name': 'default support',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'sender': {'id': '123', 'role': 'help_yandex_client'},
                        'metadata': {
                            'created': '2017-12-11T18:08:56+0300',
                            'attachments': [
                                {
                                    'id': (
                                        '91bd810f1195f140024130b901cb929aa12'
                                        'b814f'
                                    ),
                                    'link': (
                                        'support_chat/v1/realtime/59e'
                                        '4a18c779fb327d02e4c49/download_fi'
                                        'le/91bd810f1195f140024130b901cb92'
                                        '9aa12b814f/?service='
                                        'help_yandex_ru'
                                    ),
                                    'link_preview': (
                                        'support_chat/v1/real'
                                        'time/59e4a18c779fb327d02e'
                                        '4c49/download_file/91bd81'
                                        '0f1195f140024130b901cb929'
                                        'aa12b814f/?size=preview&'
                                        'service=help_yandex_ru'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'file.pdf',
                                    'preview_height': 84,
                                    'preview_width': 150,
                                    'size': 1753527,
                                    'source': 'mds',
                                },
                            ],
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'sender': {'id': 'support_id', 'role': 'support'},
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'default support',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'help_yandex_client'},
                ],
            },
            '123',
            'help_yandex_client',
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
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/supporthistorydetails'
            '/?service=labs_admin_yandex_ru',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            None,
            {
                'avatar_url': 'test1',
                'support_name': 'default support',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'sender': {
                            'id': '123',
                            'role': 'labs_admin_yandex_client',
                        },
                        'metadata': {
                            'created': '2017-12-11T18:08:56+0300',
                            'attachments': [
                                {
                                    'id': (
                                        '91bd810f1195f140024130b901cb929aa12'
                                        'b814f'
                                    ),
                                    'link': (
                                        'lab/support_chat/v1/realtime/59e'
                                        '4a18c779fb327d02e4c49/download_fi'
                                        'le/91bd810f1195f140024130b901cb92'
                                        '9aa12b814f/?service='
                                        'labs_admin_yandex_ru'
                                    ),
                                    'link_preview': (
                                        'lab/support_chat/v1/real'
                                        'time/59e4a18c779fb327d02e'
                                        '4c49/download_file/91bd81'
                                        '0f1195f140024130b901cb929'
                                        'aa12b814f/?size=preview&'
                                        'service=labs_admin_yandex_ru'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'file.pdf',
                                    'preview_height': 84,
                                    'preview_width': 150,
                                    'size': 1753527,
                                    'source': 'mds',
                                },
                            ],
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'sender': {'id': 'support_id', 'role': 'support'},
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'default support',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'labs_admin_yandex_client'},
                ],
            },
            '123',
            'labs_admin_yandex_client',
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
            {'X-YaTaxi-User': 'eats_user_id=123'},
            '/eats/v1/support_chat/v1/realtime/supporthistorydetails'
            '/?service=eats_app',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            None,
            {
                'avatar_url': 'test1',
                'support_name': 'default support',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'sender': {'id': '123', 'role': 'eats_app_client'},
                        'metadata': {
                            'created': '2017-12-11T18:08:56+0300',
                            'attachments': [
                                {
                                    'id': (
                                        '91bd810f1195f140024130b901cb929aa12'
                                        'b814f'
                                    ),
                                    'link': (
                                        'support_chat/v1/realtime/59e'
                                        '4a18c779fb327d02e4c49/download_fi'
                                        'le/91bd810f1195f140024130b901cb92'
                                        '9aa12b814f/?service=eats_app'
                                    ),
                                    'link_preview': (
                                        'support_chat/v1/real'
                                        'time/59e4a18c779fb327d02e'
                                        '4c49/download_file/91bd81'
                                        '0f1195f140024130b901cb929'
                                        'aa12b814f/?size=preview&'
                                        'service=eats_app'
                                    ),
                                    'mimetype': 'image/png',
                                    'name': 'file.pdf',
                                    'preview_height': 84,
                                    'preview_width': 150,
                                    'size': 1753527,
                                    'source': 'mds',
                                },
                            ],
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'sender': {'id': 'support_id', 'role': 'support'},
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'default support',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'eats_app_client'},
                ],
            },
            '123',
            'eats_app_client',
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
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e'},
            '/4.0/support_chat/v1/regular/supporthistorydetails',
            {'user_id': '5ff4901c583745e089e55be4a8c7a88e'},
            '59e4a18c779fb327d02e4c49',
            404,
            'ru',
            {},
            '000000000000000000000000',
            'client',
            {},
        ),
        (
            {'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e'},
            '/4.0/support_chat/v1/regular/supporthistorydetails',
            {},
            '59e4a18c779fb327d02e4c49',
            404,
            'ru',
            {},
            '000000000000000000000000',
            'client',
            {},
        ),
        (
            {
                'X-Yandex-UID': '1234',
                'X-YaTaxi-UserId': '5ff4901c583745e089e55be4a8c7a88e',
            },
            '/4.0/support_chat/v1/realtime/supporthistorydetails',
            {},
            '59e4a18c779fb327d02e4c49',
            404,
            'ru',
            {},
            '123',
            'eats_client',
            {},
        ),
        (
            {'X-Yandex-UID': '1234'},
            '/4.0/support_chat/v1/realtime/supporthistorydetails'
            '/?service=help_yandex_ru',
            {},
            '59e4a18c779fb327d02e4c49',
            404,
            'ru',
            {},
            '123',
            'help_yandex_client',
            {},
        ),
        (
            {'X-Yandex-UID': '1234'},
            '/4.0/support_chat/v1/realtime/supporthistorydetails'
            '/?service=labs_admin_yandex_ru',
            {},
            '59e4a18c779fb327d02e4c49',
            404,
            'ru',
            {},
            '123',
            'labs_admin_yandex_client',
            {},
        ),
        (
            {'X-YaTaxi-User': 'eats_user_id=1234'},
            '/4.0/support_chat/v1/realtime/supporthistorydetails'
            '/?service=eats_app',
            {},
            '59e4a18c779fb327d02e4c49',
            404,
            'ru',
            {},
            '123',
            'eats_app_client',
            {},
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/supporthistorydetails/'
            '?service=scouts',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'ru',
            {
                'avatar_url': 'test1',
                'support_name': 'имя1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {'id': '123', 'role': 'scouts_client'},
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'имя1',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'scouts_client'},
                ],
            },
            '123',
            'scouts_client',
            {},
        ),
        (
            {'X-Taxi-Storage-Id': '123'},
            '/4.0/support_chat/v1/realtime/supporthistorydetails/'
            '?service=lavka_storages',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'ru',
            {
                'avatar_url': 'test1',
                'support_name': 'имя1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {
                            'id': '123',
                            'role': 'lavka_storages_client',
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'имя1',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'lavka_storages_client'},
                ],
            },
            '123',
            'lavka_storages_client',
            {},
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/regular/supporthistorydetails/'
            '?service=drive',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'ru',
            {
                'avatar_url': 'test1',
                'support_name': 'имя1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {'id': '123', 'role': 'carsharing_client'},
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'имя1',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'carsharing_client'},
                ],
            },
            '123',
            'carsharing_client',
            {},
        ),
        (
            {'X-Eats-Session': 'test-session-header'},
            '/eats/v1/website_support_chat/v1/realtime/supporthistorydetails/'
            '?service=website',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'ru',
            {
                'avatar_url': 'test1',
                'support_name': 'имя1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {
                            'id': '13c726a0440481a6d4208f6d834961400f7c8906',
                            'role': 'website_client',
                        },
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'имя1',
                        'role': 'support',
                    },
                    {
                        'id': '13c726a0440481a6d4208f6d834961400f7c8906',
                        'role': 'website_client',
                    },
                ],
            },
            '13c726a0440481a6d4208f6d834961400f7c8906',
            'website_client',
            {},
        ),
        (
            {'X-YaEda-PartnerId': '12'},
            '/eats/v1/restapp_support_chat/v1/realtime/supporthistorydetails/'
            '?service=restapp',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'ru',
            {
                'avatar_url': 'test1',
                'support_name': 'имя1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {'id': '12', 'role': 'restapp_client'},
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'имя1',
                        'role': 'support',
                    },
                    {'id': '12', 'role': 'restapp_client'},
                ],
            },
            '12',
            'restapp_client',
            {},
        ),
        (
            {'X-Yandex-UID': '123'},
            '/4.0/support_chat/v1/realtime/supporthistorydetails/'
            '?service=market',
            {},
            '59e4a18c779fb327d02e4c49',
            200,
            'ru',
            {
                'avatar_url': 'test1',
                'support_name': 'имя1',
                'messages': [
                    {
                        'id': 'mid21',
                        'message_id': 'mid21',
                        'message_type': 'text',
                        'text': 'test',
                        'message_timestamp': '2017-12-11T18:08:56+0300',
                        'author': 'user',
                        'metadata': {'created': '2017-12-11T18:08:56+0300'},
                        'sender': {'id': '123', 'role': 'market_client'},
                    },
                    {
                        'id': 'mid22',
                        'message_id': 'mid22',
                        'message_type': 'text',
                        'text': 'test_supp',
                        'message_timestamp': '2017-12-11T18:45:39+0300',
                        'author': 'support',
                        'metadata': {'created': '2017-12-11T18:45:39+0300'},
                        'sender': {'id': 'support_id', 'role': 'support'},
                    },
                ],
                'participants': [
                    {
                        'avatar_url': 'test1',
                        'nickname': 'имя1',
                        'role': 'support',
                    },
                    {'id': '123', 'role': 'market_client'},
                ],
            },
            '123',
            'market_client',
            {},
        ),
    ],
)
async def test_supporthistory(
        monkeypatch,
        protocol_client,
        protocol_app,
        mock_get_users,
        headers,
        url,
        data,
        chat_id,
        expected_code,
        lang,
        expected_result,
        expected_owner_id,
        expected_owner_role,
        message_metadata,
):
    async def get_history(
            self,
            chat_id,
            include_participants=False,
            include_metadata=False,
            **kwargs,
    ):

        headers = kwargs.get('headers') or {}
        header_lang = headers.get('Accept-Language', 'default')

        translations = {
            'ru': 'имя1',
            'en': 'name1',
            'default': 'default support',
        }
        if chat_id != '59e4a18c779fb327d02e4c49':
            raise support_chat.NotFoundError
        return {
            'participants': [
                {
                    'avatar_url': 'test1',
                    'nickname': translations.get(header_lang),
                    'role': 'support',
                },
                {'id': expected_owner_id, 'role': expected_owner_role},
            ],
            'messages': [
                {
                    'id': 'mid21',
                    'text': 'test',
                    'metadata': {
                        'created': '2017-12-11T18:08:56+0300',
                        **message_metadata,
                    },
                    'sender': {
                        'id': expected_owner_id,
                        'role': expected_owner_role,
                    },
                },
                {
                    'id': 'mid22',
                    'text': 'test_supp',
                    'metadata': {'created': '2017-12-11T18:45:39+0300'},
                    'sender': {'id': 'support_id', 'role': 'support'},
                },
            ],
        }

    monkeypatch.setattr(
        protocol_app, 'passport', conftest.MockPassportClient(),
    )
    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_history', get_history,
    )
    if lang:
        headers['Accept-Language'] = lang
    data['chat_id'] = chat_id
    response = await protocol_client.post(
        url, headers=headers, data=json.dumps(data),
    )
    assert response.status == expected_code
    if expected_result is not None:
        assert await response.json() == expected_result
