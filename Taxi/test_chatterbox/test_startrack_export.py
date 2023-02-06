# pylint: disable=protected-access,too-many-locals,too-many-arguments
# pylint: disable=no-member,too-many-lines
import datetime

import bson
import pytest
import pytz

from taxi.clients import startrack

from chatterbox import stq_task
from test_chatterbox import plugins as conftest

NOW = datetime.datetime(2018, 5, 7, 12, 44, 56)
TASK_UPDATED = datetime.datetime(2018, 5, 7, 12, 34, 56)


# pylint: disable=invalid-name
pytestmark = pytest.mark.usefixtures('mock_uuid_fixture')


@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'num_from': 'phones',
            'num_to': 'phones',
        },
    },
)
@pytest.mark.parametrize(
    (
        'stq_kwargs',
        'task_id_str',
        'inner_comments',
        'public_messages',
        'expected_import_ticket',
        'expected_import_comment',
        'expected_update_ticket',
        'expected_create_link',
        'expected_ticket_status',
        'expected_task_status',
        'expected_download',
    ),
    [
        (
            {'action': 'export'},
            '5b2cae5cb2682a976914c2a1',
            [
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 17, 34, 56),
                    'comment': 'Test comment',
                },
                {
                    'login': 'another_login',
                    'created': datetime.datetime(2018, 5, 5, 18, 34, 56),
                    'comment': 'Another test comment',
                },
            ],
            [
                {
                    'sender': {'role': 'client', 'id': 'client_id'},
                    'text': 'Client message',
                    'metadata': {
                        'created': '2018-05-05T13:34:56',
                        'attachments': [{'id': 'first_client_attachment_id'}],
                    },
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {
                        'created': '2018-05-05T14:34:56',
                        'attachments': [{'id': 'support_attachment_id'}],
                    },
                },
                {
                    'sender': {'role': 'sms_client', 'id': 'client_id'},
                    'text': 'Next client message',
                    'metadata': {
                        'created': '2018-05-05T15:34:56',
                        'attachments': [
                            {'id': 'second_client_attachment_id'},
                            {'id': 'third_client_attachment_id'},
                        ],
                    },
                },
            ],
            {
                'queue': {'key': 'TESTQUEUE'},
                'chatterboxId': '5b2cae5cb2682a976914c2a1',
                'summary': 'Чат от 05.05.2018 15:34:56',
                'tags': ['one', 'two', 'three'],
                'description': (
                    'Ссылка на таск в chatterbox: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2a1 \nClient message'
                ),
                'createdAt': '2018-05-05T12:34:56',
                'updatedAt': '2018-05-07T14:34:56',
                'createdBy': 456,
                'updatedBy': 123,
                'line': 'first',
                'status': {'key': 'open'},
                'userPhone': 'some_user_phone',
                'city': 'Moscow',
                'chatterboxButton': 'chatterbox_urgent',
                'csatValue': '5',
                'csatReasons': 'fast_answer, thank_you',
                'macroId': 'some_macro_id',
                'supportLogin': 'test_user',
                'themes': '1,2',
                'mlSuggestionSuccess': 'True',
                'mlSuggestions': '3,4',
                'clientThematic': 'client_thematic',
                'unique': '2104653bdac343e39ac57869d0bd738d',
                'external_id': 'some_user_chat_message_id',
            },
            [
                {
                    'text': 'toert выполнил действие "create" (00:00)',
                    'createdAt': '2018-05-05T12:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test public comment',
                    'createdAt': '2018-05-05T14:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Next client message',
                    'createdAt': '2018-05-05T15:34:56',
                    'createdBy': 456,
                },
                {
                    'text': (
                        'Заказ в Такси: https://ymsh-admin.mobile'
                        '.yandex-team.ru/?order_id=some_order_id\n'
                        'Заказ в Таксометре: /redirect/to/order'
                        '?db=db_id&order=order_alias\n'
                        'Платежи: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?payments_order_id=some_order_id\n'
                        'Поездки пользователя: https://tariff-editor.taxi'
                        '.yandex-team.ru/orders?phone=+71234567890\n'
                        'Логи: https://ymsh-admin.mobile.yandex-team.ru/'
                        '?log_order_id=some_order_id\n'
                        'Водитель: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?driver_id=id_uuid\n'
                    ),
                    'createdAt': '2018-05-05T16:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test comment',
                    'createdAt': '2018-05-05T17:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Another test comment',
                    'createdAt': '2018-05-05T18:34:56',
                    'createdBy': 123,
                },
                {
                    'createdAt': '2018-05-06T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id совершил звонок '
                        'с номера +7900 на номер +7901\n'
                        'Время создания звонка: 06.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_1, url_2\n'
                        'Ошибка: -\n'
                        'АТС: \n'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id1 совершил звонок '
                        'с номера +7902 на номер +7903\n'
                        'Время создания звонка: 07.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_3, url_4\n'
                        'Ошибка: err\n'
                        'АТС: \n'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор совершил звонок с номера +7902 на номер '
                        '+7903 Время окончания вызова: 07.05.2018 14:22:33 '
                        'Направление вызова: входящий Инициатор разрыва '
                        'звонка: трубку положила вызывающая сторона '
                        'Идентификатор вызова: id1 Запись звонка: '
                        '[\'https://supchat.taxi.dev.yandex-team.ru/'
                        'chatterbox-api/v1/tasks/5b2cae5cb2682a976914c2a1/'
                        'sip_record/id1/0\']'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор совершил звонок с номера +7902 на номер'
                        ' +7903 Время окончания вызова:  '
                        'Направление вызова: исходящий Инициатор разрыва '
                        'звонка: трубку положила вызывающая сторона '
                        'Идентификатор вызова: id1 '
                        'Запись звонка: '
                        '[\'https://supchat.taxi.dev.yandex-team.ru/'
                        'chatterbox-api/v1/tasks/5b2cae5cb2682a976914c2a1/'
                        'sip_record/id1/0\']'
                    ),
                },
            ],
            {'tags': {'add': 'source_chatterbox'}},
            None,
            'open',
            'exported',
            [
                ({'id': 'first_client_attachment_id'}, 'client_id', 'client'),
                ({'id': 'support_attachment_id'}, 'some_login', 'support'),
                (
                    {'id': 'second_client_attachment_id'},
                    'client_id',
                    'sms_client',
                ),
                (
                    {'id': 'third_client_attachment_id'},
                    'client_id',
                    'sms_client',
                ),
            ],
        ),
        (
            {'action': 'export'},
            '5b2cae5cb2682a976914c2b1',
            [
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 17, 34, 56),
                    'comment': 'Test comment',
                },
                {
                    'login': 'another_login',
                    'created': datetime.datetime(2018, 5, 5, 18, 34, 56),
                    'comment': 'Another test comment',
                },
            ],
            [
                {
                    'sender': {'role': 'client', 'id': 'client_id'},
                    'text': 'Client message',
                    'metadata': {
                        'created': '2018-05-05T13:34:56',
                        'attachments': [{'id': 'first_client_attachment_id'}],
                    },
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {
                        'created': '2018-05-05T14:34:56',
                        'attachments': [{'id': 'support_attachment_id'}],
                    },
                },
                {
                    'sender': {'role': 'sms_client', 'id': 'client_id'},
                    'text': 'Next client message',
                    'metadata': {
                        'created': '2018-05-05T15:34:56',
                        'attachments': [
                            {'id': 'second_client_attachment_id'},
                            {'id': 'third_client_attachment_id'},
                        ],
                    },
                },
            ],
            {
                'queue': {'key': 'TESTQUEUE'},
                'chatterboxId': '5b2cae5cb2682a976914c2b1',
                'summary': 'Чат от 05.05.2018 15:34:56',
                'tags': ['one', 'two', 'three'],
                'description': (
                    'Ссылка на таск в chatterbox: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2b1 \nClient message'
                ),
                'createdAt': '2018-05-05T12:34:56',
                'updatedAt': '2018-05-07T14:34:56',
                'createdBy': 456,
                'updatedBy': 123,
                'line': 'first',
                'status': {'key': 'open'},
                'userPhone': 'some_user_phone',
                'city': 'Moscow',
                'chatterboxButton': 'chatterbox_urgent',
                'csatValue': '5',
                'csatReasons': 'fast_answer, thank_you',
                'macroId': 'some_macro_id',
                'themes': '1,2',
                'mlSuggestionSuccess': 'True',
                'mlSuggestions': '3,4',
                'clientThematic': 'client_thematic',
                'unique': '2104653bdac343e39ac57869d0bd738d',
                'supportLogin': 'test_user',
                'external_id': 'some_user_chat_message_id_6',
            },
            [
                {
                    'text': 'toert выполнил действие "create" (00:00)',
                    'createdAt': '2018-05-05T12:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test public comment',
                    'createdAt': '2018-05-05T14:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Next client message',
                    'createdAt': '2018-05-05T15:34:56',
                    'createdBy': 456,
                },
                {
                    'text': (
                        'Заказ в Такси: https://ymsh-admin.mobile'
                        '.yandex-team.ru/?order_id=some_order_id\n'
                        'Заказ в Таксометре: /redirect/to/order'
                        '?db=db_id&order=order_alias\n'
                        'Платежи: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?payments_order_id=some_order_id\n'
                        'Поездки пользователя: https://tariff-editor.taxi'
                        '.yandex-team.ru/orders?phone=+79001211221\n'
                        'Логи: https://ymsh-admin.mobile.yandex-team.ru/'
                        '?log_order_id=some_order_id\n'
                        'Водитель: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?driver_id=id_uuid\n'
                    ),
                    'createdAt': '2018-05-05T16:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test comment',
                    'createdAt': '2018-05-05T17:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Another test comment',
                    'createdAt': '2018-05-05T18:34:56',
                    'createdBy': 123,
                },
                {
                    'createdAt': '2018-05-06T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id совершил звонок '
                        'с номера  на номер +7901\n'
                        'Время создания звонка: 06.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_1, url_2\n'
                        'Ошибка: -\n'
                        'АТС: \n'
                    ),
                },
            ],
            {'tags': {'add': 'source_chatterbox'}},
            None,
            'open',
            'exported',
            [
                ({'id': 'first_client_attachment_id'}, 'client_id', 'client'),
                ({'id': 'support_attachment_id'}, 'some_login', 'support'),
                (
                    {'id': 'second_client_attachment_id'},
                    'client_id',
                    'sms_client',
                ),
                (
                    {'id': 'third_client_attachment_id'},
                    'client_id',
                    'sms_client',
                ),
            ],
        ),
        (
            {'action': 'export'},
            '5b2cae5cb2682a976914c2a1',
            [
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 17, 34, 56),
                    'comment': 'Test comment',
                },
                {
                    'login': 'another_login',
                    'created': datetime.datetime(2018, 5, 5, 18, 34, 56),
                    'comment': 'Another test comment',
                },
            ],
            [
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {
                        'created': '2018-05-05T14:34:56',
                        'attachments': [{'id': 'support_attachment_id'}],
                    },
                },
            ],
            {
                'queue': {'key': 'TESTQUEUE'},
                'chatterboxId': '5b2cae5cb2682a976914c2a1',
                'summary': 'Чат от 05.05.2018 15:34:56',
                'tags': ['one', 'two', 'three'],
                'description': (
                    'Ссылка на таск в chatterbox: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2a1 \n'
                    'Чат инициирован саппортом some_login: \n'
                    ' Test public comment'
                ),
                'createdAt': '2018-05-05T12:34:56',
                'updatedAt': '2018-05-07T14:34:56',
                'createdBy': 456,
                'updatedBy': 123,
                'line': 'first',
                'status': {'key': 'open'},
                'userPhone': 'some_user_phone',
                'city': 'Moscow',
                'chatterboxButton': 'chatterbox_urgent',
                'csatValue': '5',
                'csatReasons': 'fast_answer, thank_you',
                'macroId': 'some_macro_id',
                'supportLogin': 'test_user',
                'themes': '1,2',
                'mlSuggestionSuccess': 'True',
                'mlSuggestions': '3,4',
                'clientThematic': 'client_thematic',
                'unique': '2104653bdac343e39ac57869d0bd738d',
                'external_id': 'some_user_chat_message_id',
            },
            [
                {
                    'text': 'toert выполнил действие "create" (00:00)',
                    'createdAt': '2018-05-05T12:34:56',
                    'createdBy': 123,
                },
                {
                    'text': (
                        'Заказ в Такси: https://ymsh-admin.mobile'
                        '.yandex-team.ru/?order_id=some_order_id\n'
                        'Заказ в Таксометре: /redirect/to/order'
                        '?db=db_id&order=order_alias\n'
                        'Платежи: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?payments_order_id=some_order_id\n'
                        'Поездки пользователя: https://tariff-editor.taxi'
                        '.yandex-team.ru/orders?phone=+71234567890\n'
                        'Логи: https://ymsh-admin.mobile.yandex-team.ru/'
                        '?log_order_id=some_order_id\n'
                        'Водитель: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?driver_id=id_uuid\n'
                    ),
                    'createdAt': '2018-05-05T16:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test comment',
                    'createdAt': '2018-05-05T17:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Another test comment',
                    'createdAt': '2018-05-05T18:34:56',
                    'createdBy': 123,
                },
                {
                    'createdAt': '2018-05-06T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id совершил звонок '
                        'с номера +7900 на номер +7901\n'
                        'Время создания звонка: 06.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_1, url_2\n'
                        'Ошибка: -\n'
                        'АТС: \n'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id1 совершил звонок '
                        'с номера +7902 на номер +7903\n'
                        'Время создания звонка: 07.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_3, url_4\n'
                        'Ошибка: err\n'
                        'АТС: \n'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор совершил звонок с номера +7902 на номер'
                        ' +7903 Время окончания вызова: 07.05.2018 14:22:33 '
                        'Направление вызова: входящий Инициатор разрыва '
                        'звонка: трубку положила вызывающая сторона '
                        'Идентификатор вызова: id1 Запись звонка: '
                        '[\'https://supchat.taxi.dev.yandex-team.ru/'
                        'chatterbox-api/v1/tasks/5b2cae5cb2682a976914c2a1/'
                        'sip_record/id1/0\']'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор совершил звонок с номера +7902 на номер'
                        ' +7903 Время окончания вызова:  '
                        'Направление вызова: исходящий Инициатор разрыва '
                        'звонка: трубку положила вызывающая сторона '
                        'Идентификатор вызова: id1 '
                        'Запись звонка: '
                        '[\'https://supchat.taxi.dev.yandex-team.ru/'
                        'chatterbox-api/v1/tasks/5b2cae5cb2682a976914c2a1/'
                        'sip_record/id1/0\']'
                    ),
                },
            ],
            {'tags': {'add': 'source_chatterbox'}},
            None,
            'open',
            'exported',
            [({'id': 'support_attachment_id'}, 'some_login', 'support')],
        ),
        (
            {'action': 'export'},
            '5c2cae5cb2682a976914c2a1',
            [
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 17, 34, 56),
                    'comment': 'Test comment',
                },
                {
                    'login': 'another_login',
                    'created': datetime.datetime(2018, 5, 5, 18, 34, 56),
                    'comment': 'Another test comment',
                },
            ],
            [
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {
                        'created': '2018-05-05T14:34:56',
                        'attachments': [{'id': 'support_attachment_id'}],
                    },
                },
            ],
            {
                'queue': {'key': 'TESTQUEUE'},
                'chatterboxId': '5c2cae5cb2682a976914c2a1',
                'summary': 'Чат от 05.05.2018 15:34:56',
                'tags': ['one', 'two', 'three'],
                'description': (
                    'Ссылка на таск в chatterbox: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5c2cae5cb2682a976914c2a1 \n'
                    'Чат инициирован саппортом some_login: \n'
                    ' Test public comment'
                ),
                'createdAt': '2018-05-05T12:34:56',
                'updatedAt': '2018-05-07T14:34:56',
                'createdBy': 456,
                'updatedBy': 123,
                'external_id': 'some_messenger_chat_message_id',
                'line': 'first',
                'status': {'key': 'open'},
                'userPhone': 'some_user_phone',
                'city': 'Moscow',
                'chatterboxButton': 'chatterbox_urgent',
                'csatValue': '5',
                'csatReasons': 'fast_answer, thank_you',
                'macroId': 'some_macro_id',
                'supportLogin': 'test_user',
                'themes': '1,2',
                'mlSuggestionSuccess': 'True',
                'mlSuggestions': '3,4',
                'clientThematic': 'client_thematic',
                'unique': '2104653bdac343e39ac57869d0bd738d',
            },
            [
                {
                    'text': 'toert выполнил действие "create" (00:00)',
                    'createdAt': '2018-05-05T12:34:56',
                    'createdBy': 123,
                },
                {
                    'text': (
                        'Заказ в Такси: https://ymsh-admin.mobile'
                        '.yandex-team.ru/?order_id=some_order_id\n'
                        'Заказ в Таксометре: /redirect/to/order'
                        '?db=db_id&order=order_alias\n'
                        'Платежи: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?payments_order_id=some_order_id\n'
                        'Поездки пользователя: https://tariff-editor.taxi'
                        '.yandex-team.ru/orders?phone=+71234567890\n'
                        'Логи: https://ymsh-admin.mobile.yandex-team.ru/'
                        '?log_order_id=some_order_id\n'
                        'Водитель: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?driver_id=id_uuid\n'
                    ),
                    'createdAt': '2018-05-05T16:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test comment',
                    'createdAt': '2018-05-05T17:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Another test comment',
                    'createdAt': '2018-05-05T18:34:56',
                    'createdBy': 123,
                },
                {
                    'createdAt': '2018-05-06T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id совершил звонок '
                        'с номера +7900 на номер +7901\n'
                        'Время создания звонка: 06.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_1, url_2\n'
                        'Ошибка: -\n'
                        'АТС: \n'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id1 совершил звонок '
                        'с номера +7902 на номер +7903\n'
                        'Время создания звонка: 07.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_3, url_4\n'
                        'Ошибка: err\n'
                        'АТС: \n'
                    ),
                },
            ],
            {'tags': {'add': 'source_chatterbox'}},
            None,
            'open',
            'exported',
            [({'id': 'support_attachment_id'}, 'some_login', 'support')],
        ),
        (
            {'action': 'export'},
            '5b2cae5cb2682a976914c2a2',
            [
                {
                    'login': 'super_user',
                    'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                    'comment': 'Too long tags:\ntoo_long_for_startrack_tag\n',
                },
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 13, 34, 56),
                    'comment': 'Test comment',
                },
                {
                    'login': 'another_login',
                    'created': datetime.datetime(2018, 5, 5, 15, 34, 56),
                    'comment': 'Another test comment',
                },
            ],
            [
                {
                    'sender': {'role': 'driver'},
                    'text': 'Client message',
                    'metadata': {'created': '2018-05-05T13:34:56'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {'created': '2018-05-05T14:34:56'},
                },
            ],
            {
                'queue': {'key': 'TESTQUEUE'},
                'chatterboxId': '5b2cae5cb2682a976914c2a2',
                'summary': 'Чат от 05.05.2018 15:34:56',
                'tags': ['chatterbox_bad_tags', 't_w_o', 'three', 'abcde'],
                'description': (
                    'Ссылка на таск в chatterbox: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2a2 \nClient message'
                ),
                'createdAt': '2018-05-05T12:34:56',
                'updatedAt': '2018-05-07T14:34:56',
                'createdBy': 456,
                'updatedBy': 123,
                'line': 'second',
                'status': {'key': 'open'},
                'userPhone': 'some_user_phone',
                'city': 'Moscow',
                'chatterboxButton': 'chatterbox_urgent',
                'macroId': 'some_macro_id',
                'unique': '2104653bdac343e39ac57869d0bd738d',
                'external_id': 'some_user_chat_message_id_2',
            },
            [
                {
                    'text': 'Too long tags:\n' 'too_long_for_startrack_tag\n',
                    'createdAt': '2018-05-05T12:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test comment',
                    'createdAt': '2018-05-05T13:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test public comment',
                    'createdAt': '2018-05-05T14:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Another test comment',
                    'createdAt': '2018-05-05T15:34:56',
                    'createdBy': 123,
                },
            ],
            {'tags': {'add': 'source_chatterbox'}},
            [
                {
                    'ticket_id': 'TESTQUEUE-1',
                    'related_ticket_id': 'TESTQUEUE-3',
                    'relationship': None,
                },
                {
                    'ticket_id': 'TESTQUEUE-1',
                    'related_ticket_id': 'TESTQUEUE-4',
                    'relationship': None,
                },
            ],
            'open',
            'exported',
            [],
        ),
        (
            {'action': 'export'},
            '5b2cae5cb2682a976914c2a2',
            [
                {
                    'login': 'super_user',
                    'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                    'comment': 'Too long tags',
                },
            ],
            [
                {
                    'sender': {'role': 'driver'},
                    'text': 'Client message',
                    'metadata': {'created': '2018-05-05T13:34:56'},
                }
                for _ in range(998)
            ],
            {
                'queue': {'key': 'TESTQUEUE'},
                'chatterboxId': '5b2cae5cb2682a976914c2a2',
                'summary': 'Чат от 05.05.2018 15:34:56',
                'tags': [
                    'chatterbox_bad_tags',
                    't_w_o',
                    'three',
                    'abcde',
                    'chatterbox_comment_limit_reached_tag',
                ],
                'description': (
                    'Ссылка на таск в chatterbox: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2a2 \nClient message'
                ),
                'createdAt': '2018-05-05T12:34:56',
                'updatedAt': '2018-05-07T14:34:56',
                'createdBy': 456,
                'updatedBy': 123,
                'line': 'second',
                'status': {'key': 'open'},
                'userPhone': 'some_user_phone',
                'city': 'Moscow',
                'chatterboxButton': 'chatterbox_urgent',
                'macroId': 'some_macro_id',
                'unique': '2104653bdac343e39ac57869d0bd738d',
                'external_id': 'some_user_chat_message_id_2',
            },
            [
                {
                    'text': 'Too long tags',
                    'createdAt': '2018-05-05T12:34:56',
                    'createdBy': 123,
                },
            ]
            + [
                {
                    'text': 'Client message',
                    'createdAt': '2018-05-05T13:34:56',
                    'createdBy': 456,
                }
                for _ in range(997)
            ],
            {'tags': {'add': 'source_chatterbox'}},
            [
                {
                    'ticket_id': 'TESTQUEUE-1',
                    'related_ticket_id': 'TESTQUEUE-3',
                    'relationship': None,
                },
                {
                    'ticket_id': 'TESTQUEUE-1',
                    'related_ticket_id': 'TESTQUEUE-4',
                    'relationship': None,
                },
            ],
            'open',
            'exported',
            [],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    STARTRACK_SUPPORT_USER_ID=123,
    STARTRACK_CLIENT_USER_ID=456,
    MAX_STARTRACK_TAG_LENGTH=30,
    STARTRACK_SUPPORT_ARCHIVE_QUEUE='TESTQUEUE',
    STARTRACK_SUPPORT_ARCHIVE_QUEUE_BY_LINE={'__default__': 'TESTQUEUE'},
)
async def test_startrack_export(
        cbox,
        mock_st_import_ticket,
        mock_st_get_ticket_with_status,
        mock_st_import_comment,
        mock_st_get_comments,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_st_import_file,
        mock_st_create_link,
        mock_get_chat,
        mock_source_download_file,
        mock_st_update_ticket,
        mock_personal,
        stq_kwargs,
        task_id_str,
        inner_comments,
        public_messages,
        expected_import_ticket,
        expected_import_comment,
        expected_update_ticket,
        expected_create_link,
        expected_ticket_status,
        expected_task_status,
        expected_download,
):
    mock_st_get_ticket_with_status('closed')
    st_comments = [
        {
            'id': 'some_comment_id',
            'createdAt': '2018-01-02T03:45:00.000Z',
            'createdBy': {'id': 'some_id'},
            'updatedAt': '2018-01-02T03:45:00.000Z',
            'updatedBy': {'id': 'some_id'},
            'text': i['text'],
        }
        for i in public_messages
    ]
    mock_st_get_comments(st_comments)
    mock_chat_get_history({'messages': public_messages})
    mocked_update_ticket = mock_st_update_ticket('open')
    task_id = bson.objectid.ObjectId(task_id_str)

    startrack_ticket = {
        'key': 'TESTQUEUE-1',
        'self': 'tracker/TESTQUEUE-1',
        'createdAt': '2018-05-05T12:34:56',
        'updatedAt': '2018-05-05T14:34:56',
        'status': {'key': 'open'},
    }
    mocked_import_ticket = mock_st_import_ticket(startrack_ticket)

    startrack_comment = {
        'id': 'some_imported_comment_id',
        'key': 'dummy',
        'self': 'tracker/TESTQUEUE-1/comments/dummy',
    }
    mocked_import_comment = mock_st_import_comment(startrack_comment)

    db_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    inner_comments.extend(
        await cbox.app.startrack_manager._prepare_hidden_comments_for_export(
            db_task,
        ),
    )

    await stq_task.startrack_ticket_import(cbox.app, task_id, **stq_kwargs)
    del public_messages[0]

    cycle_range = len(public_messages) + len(inner_comments) + 1
    for _ in range(cycle_range):
        await stq_task.startrack_comment_import(
            cbox.app,
            task_id,
            startrack_ticket=startrack_ticket,
            inner_comments=inner_comments,
            public_messages=public_messages,
            **stq_kwargs,
        )

    import_ticket_calls = mocked_import_ticket.calls
    assert import_ticket_calls[0]['kwargs']['json'] == expected_import_ticket
    assert import_ticket_calls[0]['kwargs']['params'] == {'enableSla': 'true'}

    import_comment_calls = mocked_import_comment.calls
    if expected_import_comment is None:
        assert not import_comment_calls
    else:
        assert len(import_comment_calls) == len(expected_import_comment)
        for i, call in enumerate(import_comment_calls):
            assert call['ticket_id'] == 'TESTQUEUE-1'
            assert call['data'] == expected_import_comment[i]

    create_link_calls = mock_st_create_link.calls
    if expected_create_link is None:
        assert not create_link_calls
    else:
        assert create_link_calls == expected_create_link

    if expected_update_ticket is not None:
        update_ticket_calls = mocked_update_ticket.calls
        assert update_ticket_calls[0]['ticket'] == 'TESTQUEUE-1'
        assert update_ticket_calls[0]['kwargs'] == expected_update_ticket

    db_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert db_task['startrack_ticket'] == 'TESTQUEUE-1'
    assert db_task['startrack_ticket_status'] == expected_ticket_status
    assert db_task['status'] == expected_task_status

    mock_source_download_file_calls = mock_source_download_file.calls
    if mock_source_download_file_calls:
        for i, call in enumerate(mock_source_download_file_calls):
            assert call['args'][1:] == expected_download[i]


@pytest.mark.parametrize(
    ('public_messages', 'expected_filename'),
    [
        (
            [
                {
                    'sender': {'role': 'client', 'id': 'client_id'},
                    'text': 'Client message',
                    'metadata': {
                        'created': '2018-05-05T13:34:56',
                        'attachments': [
                            {
                                'id': 'first_client_attachment_id',
                                'name': 'abc',
                            },
                        ],
                    },
                },
            ],
            'abc',
        ),
        (
            [
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {
                        'created': '2018-05-05T14:34:56',
                        'attachments': [{'id': 'support_attachment_id'}],
                    },
                },
            ],
            'support_attachment_id',
        ),
        (
            [
                {
                    'sender': {'role': 'sms_client', 'id': 'client_id'},
                    'text': 'Next client message',
                    'metadata': {
                        'created': '2018-05-05T15:34:56',
                        'attachments': [
                            {
                                'id': 'second_client_attachment_id',
                                'name': (
                                    'abcdewwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
                                    'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
                                    'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
                                    'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
                                    'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
                                    'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
                                    'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww.jpg'
                                ),
                            },
                        ],
                    },
                },
            ],
            'cdewwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
            'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
            'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
            'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
            'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
            'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
            'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww.jpg',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    STARTRACK_SUPPORT_USER_ID=123,
    STARTRACK_CLIENT_USER_ID=456,
    MAX_STARTRACK_TAG_LENGTH=30,
    STARTRACK_SUPPORT_ARCHIVE_QUEUE='TESTQUEUE',
    STARTRACK_SUPPORT_ARCHIVE_QUEUE_BY_LINE={'__default__': 'TESTQUEUE'},
)
async def test_startrack_export_filename_length(
        cbox,
        mock,
        monkeypatch,
        mock_st_import_ticket,
        mock_st_get_ticket_with_status,
        mock_st_import_comment,
        mock_st_get_comments,
        mock_chat_get_history,
        mock_st_import_file,
        mock_st_create_link,
        mock_get_chat,
        mock_source_download_file,
        mock_st_update_ticket,
        public_messages,
        expected_filename,
):
    mock_st_get_ticket_with_status('closed')
    st_comments = [
        {
            'id': 'some_comment_id',
            'createdAt': '2018-01-02T03:45:00.000Z',
            'createdBy': {'id': 'some_id'},
            'updatedAt': '2018-01-02T03:45:00.000Z',
            'updatedBy': {'id': 'some_id'},
            'text': i['text'],
        }
        for i in public_messages
    ]
    mock_st_get_comments(st_comments)
    mock_chat_get_history({'messages': public_messages})
    mock_st_update_ticket('open')
    task_id = bson.objectid.ObjectId('5b2cae5cb2682a976914c2a1')

    startrack_ticket = {
        'key': 'TESTQUEUE-1',
        'self': 'tracker/TESTQUEUE-1',
        'createdAt': '2018-05-05T12:34:56',
        'updatedAt': '2018-05-05T14:34:56',
        'status': {'key': 'open'},
    }
    mocked_import_ticket = mock_st_import_ticket(startrack_ticket)

    @mock
    async def dummy_import_file(*args, **kwargs):
        assert kwargs.get('filename') == expected_filename

    monkeypatch.setattr(
        startrack.StartrackAPIClient, 'import_file', dummy_import_file,
    )

    await stq_task.startrack_ticket_import(cbox.app, task_id, action='export')

    import_ticket_calls = mocked_import_ticket.calls
    assert import_ticket_calls

    db_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert db_task['startrack_ticket'] == 'TESTQUEUE-1'
    assert db_task['startrack_ticket_status'] == 'open'


@pytest.mark.parametrize(
    'task_id_str,export_kwargs,inner_comments,public_messages,'
    'expected_update_ticket,expected_create_comment,expected_create_link,'
    'expected_ticket_status,expected_task_status',
    [
        (
            '5b2cae5cb2682a976914c2a3',
            {'action': 'export'},
            [
                {
                    'login': 'super_user',
                    'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                    'comment': 'Too long tags:\ntoo_long_for_startrack_tag\n',
                },
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 13, 34, 56),
                    'comment': 'Test comment',
                },
            ],
            [
                {
                    'sender': {'role': 'client'},
                    'text': 'Client message',
                    'metadata': {'created': '2018-05-05T13:34:56Z'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {'created': '2018-05-05T14:34:56Z'},
                },
            ],
            {
                'tags': [
                    'chatterbox_bad_tags',
                    't_w_o',
                    'three',
                    'answer_from_startrack_only',
                    'forwarded_from_chatterbox',
                ],
                'custom_fields': {
                    'chatterboxButton': 'chatterbox_urgent',
                    'city': 'Moscow',
                    'macroId': 'some_macro_id',
                    'userPhone': 'some_user_phone',
                    'line': 'second',
                },
            },
            [
                {
                    'text': (
                        'Too long tags:\n'
                        'toooooooooooo_long_f_r_st_rtrack_tag'
                    ),
                },
            ],
            None,
            'closed',
            'exported',
        ),
        (
            '5b2cae5cb2682a976914c2a5',
            {'action': 'export'},
            [
                {
                    'login': 'super_user',
                    'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                    'comment': 'Too long tags:\ntoo_long_for_startrack_tag\n',
                },
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 13, 34, 56),
                    'comment': 'Test comment',
                },
            ],
            [
                {
                    'sender': {'role': 'client'},
                    'text': 'Client message',
                    'metadata': {'created': '2018-05-05T13:34:56Z'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {'created': '2018-05-05T14:34:56Z'},
                },
            ],
            {
                'tags': [
                    'chatterbox_bad_tags',
                    't_w_o',
                    'three',
                    'answer_from_startrack_only',
                    'forwarded_from_chatterbox',
                ],
                'custom_fields': {
                    'chatterboxButton': 'chatterbox_urgent',
                    'city': 'Moscow',
                    'macroId': 'some_macro_id',
                    'userPhone': 'some_user_phone',
                    'line': 'second',
                },
            },
            [
                {
                    'text': (
                        'Too long tags:\n'
                        'toooooooooooo_long_f_r_st_rtrack_tag'
                    ),
                },
            ],
            [
                {
                    'ticket_id': 'TESTQUEUE-2',
                    'related_ticket_id': 'TESTQUEUE-3',
                    'relationship': None,
                },
                {
                    'ticket_id': 'TESTQUEUE-2',
                    'related_ticket_id': 'TESTQUEUE-4',
                    'relationship': None,
                },
            ],
            'closed',
            'exported',
        ),
        (
            '5b2cae5cb2682a976914c2a6',
            {'action': 'export'},
            [],
            [],
            {
                'tags': [
                    'one',
                    'two',
                    'three',
                    'answer_from_startrack_only',
                    'forwarded_from_chatterbox',
                ],
                'custom_fields': {'line': 'first'},
            },
            None,
            None,
            'open',
            'exported',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    STARTRACK_SUPPORT_USER_ID=123,
    STARTRACK_CLIENT_USER_ID=456,
    MAX_STARTRACK_TAG_LENGTH=30,
    STARTRACK_SUPPORT_ARCHIVE_QUEUE='TESTQUEUE',
)
async def test_startrack_to_startrack(
        cbox,
        mock_st_get_ticket_with_status,
        mock_st_get_comments,
        mock_st_import_ticket,
        mock_chat_get_history,
        mock_st_update_ticket,
        mock_st_create_comment,
        mock_st_import_file,
        mock_st_create_link,
        mock_source_download_file,
        task_id_str,
        export_kwargs,
        inner_comments,
        public_messages,
        expected_update_ticket,
        expected_create_comment,
        expected_create_link,
        expected_ticket_status,
        expected_task_status,
):
    mock_st_get_ticket_with_status(expected_ticket_status)
    st_comments = [
        {
            'id': 'some_comment_id',
            'createdAt': '2018-01-02T03:45:00.000Z',
            'createdBy': {'id': 'some_id'},
            'updatedAt': '2018-01-02T03:45:00.000Z',
            'updatedBy': {'id': 'some_id'},
            'text': i['text'],
        }
        for i in public_messages
    ]
    mock_st_get_comments(st_comments)
    mock_chat_get_history({'messages': public_messages})
    task_id = bson.objectid.ObjectId(task_id_str)

    startrack_ticket = {
        'key': 'TESTQUEUE-1',
        'self': 'tracker/TESTQUEUE-1',
        'createdAt': '2018-05-05T12:34:56',
        'updatedAt': '2018-05-05T14:34:56',
        'status': {'key': 'open'},
    }
    mocked_import_ticket = mock_st_import_ticket(startrack_ticket)
    mocked_update_ticket = mock_st_update_ticket('open')

    db_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    inner_comments.extend(
        await cbox.app.startrack_manager._prepare_hidden_comments_for_export(
            db_task,
        ),
    )

    await stq_task.startrack_ticket_import(cbox.app, task_id, **export_kwargs)
    if public_messages:
        del public_messages[0]

    import_ticket_calls = mocked_import_ticket.calls
    assert not import_ticket_calls

    update_ticket_calls = mocked_update_ticket.calls
    assert update_ticket_calls[0]['ticket'] == db_task['external_id']
    assert update_ticket_calls[0]['kwargs'] == expected_update_ticket

    create_comment_calls = mock_st_create_comment.calls
    if expected_create_comment is None:
        assert not create_comment_calls
    else:
        assert len(create_comment_calls) == len(expected_create_comment)
        for i, call in enumerate(create_comment_calls):
            assert call['args'] == (db_task['external_id'],)
            assert call['kwargs'] == expected_create_comment[i]

    create_link_calls = mock_st_create_link.calls
    if expected_create_link is None:
        assert not create_link_calls
    else:
        assert create_link_calls == expected_create_link

    db_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert db_task['startrack_ticket'] == db_task['external_id']
    assert db_task['startrack_ticket_status'] == expected_ticket_status
    assert db_task['status'] == expected_task_status


@pytest.mark.parametrize(
    'task_id_str, import_ticket_calls',
    [('5b2cae5cb2682a976914c2a1', 2), ('5b2cae5cb2682a976914c2a4', 1)],
)
async def test_no_need_to_export(
        cbox,
        db,
        mock_chat_get_history,
        monkeypatch,
        mock,
        task_id_str,
        import_ticket_calls,
):
    @mock
    async def dummy_import_ticket(*args, **kwargs):
        raise startrack.BaseError

    @mock
    async def dummy_search(*args, **kwargs):
        if task_id_str == '5b2cae5cb2682a976914c2a4':
            return [{'key': 'TESTQUEUE-1', 'status': {'key': 'open'}}]
        return []

    monkeypatch.setattr(
        startrack.StartrackAPIClient, 'import_ticket', dummy_import_ticket,
    )

    monkeypatch.setattr(startrack.StartrackAPIClient, 'search', dummy_search)

    mock_chat_get_history(
        {
            'messages': [
                {
                    'sender': {'role': 'client', 'id': 'client_id'},
                    'text': 'Client message',
                    'metadata': {'created': '2018-05-05T13:34:56'},
                },
            ],
        },
    )

    task_id = bson.ObjectId(task_id_str)
    with pytest.raises(startrack.BaseError):
        await stq_task.startrack_ticket_import(
            cbox.app, task_id, action='export',
        )

    try:
        await stq_task.startrack_ticket_import(
            cbox.app, task_id, action='export',
        )
    except startrack.BaseError:
        task = await db.support_chatterbox.find_one({'_id': task_id})
        assert 'startrack_ticket' not in task
    else:
        task = await db.support_chatterbox.find_one({'_id': task_id})
        assert task['startrack_ticket'] == 'TESTQUEUE-1'

    assert len(dummy_import_ticket.calls) == import_ticket_calls


@pytest.mark.config(
    EXTERNAL_STARTRACK_DISABLE={'support-taxi': True},
    CHATTERBOX_STARTRACK_DISABLED_DELAY=600,
)
@pytest.mark.now('2019-01-30T14:00:00.000Z')
@pytest.mark.parametrize('task_id_str', ['5b2cae5cb2682a976914c2a1'])
async def test_startrack_disabled(
        cbox, stq, mock_chat_get_history, monkeypatch, mock, task_id_str,
):
    await _test_disable_startrack(
        cbox, stq, mock_chat_get_history, monkeypatch, mock, task_id_str,
    )


@pytest.mark.config(
    EXTERNAL_STARTRACK_REQUESTS_RATE={
        'support-taxi': {'import_ticket': 0, 'import_comment': 0},
    },
    CHATTERBOX_STARTRACK_DISABLED_DELAY=600,
)
@pytest.mark.now('2019-01-30T14:00:00.000Z')
@pytest.mark.parametrize('task_id_str', ['5b2cae5cb2682a976914c2a1'])
async def test_startrack_disabled_rate(
        cbox, stq, mock_chat_get_history, monkeypatch, mock, task_id_str,
):
    await _test_disable_startrack(
        cbox, stq, mock_chat_get_history, monkeypatch, mock, task_id_str,
    )


async def _test_disable_startrack(
        cbox, stq, mock_chat_get_history, monkeypatch, mock, task_id_str,
):
    @mock
    async def dummy_search(*args, **kwargs):
        return []

    monkeypatch.setattr(startrack.StartrackAPIClient, 'search', dummy_search)

    mock_chat_get_history(
        {
            'messages': [
                {
                    'sender': {'role': 'client', 'id': 'client_id'},
                    'text': 'Client message',
                    'metadata': {'created': '2018-05-05T13:34:56'},
                },
            ],
        },
    )

    task_id = bson.ObjectId(task_id_str)

    await stq_task.startrack_ticket_import(cbox.app, task_id, action='export')

    put_call = stq.startrack_ticket_import_queue.next_call()
    assert put_call['args'] == [{'$oid': str(task_id)}]
    assert put_call['eta'] == datetime.datetime(2019, 1, 30, 14, 10)

    startrack_ticket = {
        'key': 'TESTQUEUE-1',
        'self': 'tracker/TESTQUEUE-1',
        'createdAt': '2018-05-05T12:34:56',
        'updatedAt': '2018-05-05T14:34:56',
        'status': {'key': 'open'},
    }

    inner_comments = [
        {
            'login': 'some_login',
            'created': datetime.datetime(2018, 5, 5, 17, 34, 56),
            'comment': 'Test comment',
        },
        {
            'login': 'another_login',
            'created': datetime.datetime(2018, 5, 5, 18, 34, 56),
            'comment': 'Another test comment',
        },
    ]

    await stq_task.startrack_comment_import(
        cbox.app,
        task_id,
        startrack_ticket,
        inner_comments,
        [],
        action='export',
    )
    put_call = stq.startrack_comment_import_queue.next_call()
    expected_inner_comments = [
        {
            **comment,
            'created': {
                '$date': (
                    comment['created']
                    .replace(tzinfo=pytz.UTC)
                    .astimezone(pytz.timezone('Europe/Moscow'))
                    .timestamp()
                    * 1000
                ),
            },
        }
        for comment in inner_comments
    ]
    assert put_call['args'] == [
        {'$oid': str(task_id)},
        startrack_ticket,
        expected_inner_comments,
        [],
    ]
    assert put_call['eta'] == datetime.datetime(2019, 1, 30, 14, 10)

    public_comments = [
        {
            'sender': {'role': 'driver'},
            'text': 'Client message',
            'metadata': {'created': '2018-05-05T13:34:56'},
        },
        {
            'sender': {'id': 'some_login', 'role': 'support'},
            'text': 'Test public comment',
            'metadata': {'created': '2018-05-05T14:34:56'},
        },
    ]

    await stq_task.startrack_comment_import(
        cbox.app,
        task_id,
        startrack_ticket,
        [],
        public_comments,
        action='export',
    )
    put_call = stq.startrack_comment_import_queue.next_call()
    assert put_call['args'] == [
        {'$oid': str(task_id)},
        startrack_ticket,
        [],
        public_comments,
    ]
    assert put_call['eta'] == datetime.datetime(2019, 1, 30, 14, 10)


@pytest.mark.config(
    EXTERNAL_STARTRACK_REQUESTS_RATE={'support-taxi': {'hidden_comment': 0}},
    CHATTERBOX_STARTRACK_DISABLED_DELAY=600,
)
@pytest.mark.now('2019-01-30T14:00:00.000Z')
async def test_disabled_hidden_comment(stq, cbox):
    await stq_task.startrack_hidden_comment(
        cbox.app, 'TESTQUEUE-1', 'comment', 0,
    )
    put_call = stq.startrack_hidden_comment_queue.next_call()
    assert put_call['args'] == ['TESTQUEUE-1', 'comment', 0]
    assert put_call['eta'] == datetime.datetime(2019, 1, 30, 14, 10)


async def test_stq_add_hidden_comment(cbox, mock_st_create_comment, patch):
    @patch(
        'chatterbox.internal.tasks_manager.'
        'TasksManager.set_external_comment_id',
    )
    async def _set_external_comment_id(
            task_external_id, comment, external_comment_id, **kwargs,
    ):
        assert comment == 'comment'
        assert external_comment_id == 1005005505045045040
        assert task_external_id == 'TESTQUEUE-1'

    await stq_task.startrack_hidden_comment(
        cbox.app, 'TESTQUEUE-1', 'comment', 0,
    )

    assert _set_external_comment_id.calls


@pytest.mark.parametrize(
    (
        'task_id_str',
        'inner_comments',
        'public_messages',
        'expected_import_ticket',
        'expected_import_comment',
        'expected_update_ticket',
        'expected_create_link',
        'expected_ticket_status',
    ),
    [
        (
            '5b2cae5cb2682a976914c2b9',
            [
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 17, 34, 56),
                    'comment': 'Test comment',
                },
                {
                    'login': 'another_login',
                    'created': datetime.datetime(2018, 5, 5, 18, 34, 56),
                    'comment': 'Another test comment',
                },
            ],
            [
                {
                    'sender': {'role': 'client', 'id': 'client_id'},
                    'text': 'Client message',
                    'metadata': {
                        'created': '2018-05-05T13:34:56',
                        'attachments': [{'id': 'first_client_attachment_id'}],
                    },
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {
                        'created': '2018-05-05T14:34:56',
                        'attachments': [{'id': 'support_attachment_id'}],
                    },
                },
                {
                    'sender': {'role': 'sms_client', 'id': 'client_id'},
                    'text': 'Next client message',
                    'metadata': {
                        'created': '2018-05-05T15:34:56',
                        'attachments': [
                            {'id': 'second_client_attachment_id'},
                            {'id': 'third_client_attachment_id'},
                        ],
                    },
                },
            ],
            {
                'queue': {'key': 'TESTQUEUE'},
                'summary': 'Копия тикета: 5b2cae5cb2682a976914c2b9',
                'tags': ['one', 'two', 'three', 'additional_tag'],
                'description': (
                    'Ссылка на таск в chatterbox: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2b9 \nClient message'
                ),
                'createdAt': '2018-05-05T12:34:56',
                'updatedAt': '2018-05-07T14:34:56',
                'createdBy': 456,
                'updatedBy': 123,
                'line': 'first',
                'status': {'key': 'open'},
                'userPhone': 'some_user_phone',
                'city': 'Moscow',
                'chatterboxButton': 'chatterbox_urgent',
                'csatValue': '5',
                'csatReasons': 'fast_answer, thank_you',
                'macroId': 'some_macro_id',
                'supportLogin': 'test_user',
                'themes': '1,2',
                'mlSuggestionSuccess': 'True',
                'mlSuggestions': '3,4',
                'clientThematic': 'client_thematic',
                'unique': '2104653bdac343e39ac57869d0bd738d',
                'external_id': 'some_user_chat_message_id_4',
            },
            [
                {
                    'text': 'toert выполнил действие "create" (00:00)',
                    'createdAt': '2018-05-05T12:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test public comment',
                    'createdAt': '2018-05-05T14:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Next client message',
                    'createdAt': '2018-05-05T15:34:56',
                    'createdBy': 456,
                },
                {
                    'text': (
                        'Заказ в Такси: https://ymsh-admin.mobile'
                        '.yandex-team.ru/?order_id=some_order_id\n'
                        'Заказ в Таксометре: /redirect/to/order'
                        '?db=db_id&order=order_alias\n'
                        'Платежи: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?payments_order_id=some_order_id\n'
                        'Поездки пользователя: https://tariff-editor.taxi'
                        '.yandex-team.ru/orders?phone=+71234567890\n'
                        'Логи: https://ymsh-admin.mobile.yandex-team.ru/'
                        '?log_order_id=some_order_id\n'
                        'Водитель: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?driver_id=id_uuid\n'
                    ),
                    'createdAt': '2018-05-05T16:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test comment',
                    'createdAt': '2018-05-05T17:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Another test comment',
                    'createdAt': '2018-05-05T18:34:56',
                    'createdBy': 123,
                },
                {
                    'createdAt': '2018-05-06T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id совершил звонок '
                        'с номера +7900 на номер +7901\n'
                        'Время создания звонка: 06.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_1, url_2\n'
                        'Ошибка: -\n'
                        'АТС: \n'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id1 совершил звонок '
                        'с номера +7902 на номер +7903\n'
                        'Время создания звонка: 07.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_3, url_4\n'
                        'Ошибка: err\n'
                        'АТС: \n'
                    ),
                },
            ],
            {'tags': {'add': 'copy_from_chatterbox'}},
            None,
            'open',
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            [
                {
                    'login': 'some_login',
                    'created': datetime.datetime(2018, 5, 5, 17, 34, 56),
                    'comment': 'Test comment',
                },
                {
                    'login': 'another_login',
                    'created': datetime.datetime(2018, 5, 5, 18, 34, 56),
                    'comment': 'Another test comment',
                },
            ],
            [
                {
                    'sender': {'role': 'client', 'id': 'client_id'},
                    'text': 'Client message',
                    'metadata': {
                        'created': '2018-05-05T13:34:56',
                        'attachments': [{'id': 'first_client_attachment_id'}],
                    },
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {
                        'created': '2018-05-05T14:34:56',
                        'attachments': [{'id': 'support_attachment_id'}],
                    },
                },
                {
                    'sender': {'role': 'sms_client', 'id': 'client_id'},
                    'text': 'Next client message',
                    'metadata': {
                        'created': '2018-05-05T15:34:56',
                        'attachments': [
                            {'id': 'second_client_attachment_id'},
                            {'id': 'third_client_attachment_id'},
                        ],
                    },
                },
            ],
            {
                'queue': {'key': 'TESTQUEUE'},
                'summary': 'Копия тикета: 5b2cae5cb2682a976914c2b0',
                'tags': ['one', 'two', 'three', 'additional_tag'],
                'description': (
                    'Ссылка на таск в chatterbox: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2b0 \nClient message'
                ),
                'createdAt': '2018-05-05T12:34:56',
                'updatedAt': '2018-05-07T14:34:56',
                'createdBy': 456,
                'updatedBy': 123,
                'line': 'first',
                'status': {'key': 'open'},
                'userPhone': 'some_user_phone',
                'city': 'Moscow',
                'chatterboxButton': 'chatterbox_urgent',
                'csatValue': '5',
                'csatReasons': 'fast_answer, thank_you',
                'macroId': 'some_macro_id',
                'supportLogin': 'test_user',
                'themes': '1,2',
                'mlSuggestionSuccess': 'True',
                'mlSuggestions': '3,4',
                'clientThematic': 'client_thematic',
                'unique': '2104653bdac343e39ac57869d0bd738d',
                'external_id': 'some_user_chat_message_id_5',
            },
            [
                {
                    'text': 'toert выполнил действие "create" (00:00)',
                    'createdAt': '2018-05-05T12:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test public comment',
                    'createdAt': '2018-05-05T14:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Next client message',
                    'createdAt': '2018-05-05T15:34:56',
                    'createdBy': 456,
                },
                {
                    'text': (
                        'Заказ в Такси: https://ymsh-admin.mobile'
                        '.yandex-team.ru/?order_id=some_order_id\n'
                        'Заказ в Таксометре: /redirect/to/order'
                        '?db=performer_db_id&order=order_alias\n'
                        'Платежи: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?payments_order_id=some_order_id\n'
                        'Поездки пользователя: https://tariff-editor.taxi'
                        '.yandex-team.ru/orders?phone=+71234567890\n'
                        'Логи: https://ymsh-admin.mobile.yandex-team.ru/'
                        '?log_order_id=some_order_id\n'
                        'Водитель: https://ymsh-admin.mobile.yandex'
                        '-team.ru/?driver_id=performer_id_uuid\n'
                    ),
                    'createdAt': '2018-05-05T16:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Test comment',
                    'createdAt': '2018-05-05T17:34:56',
                    'createdBy': 123,
                },
                {
                    'text': 'Another test comment',
                    'createdAt': '2018-05-05T18:34:56',
                    'createdBy': 123,
                },
                {
                    'createdAt': '2018-05-06T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id совершил звонок '
                        'с номера +7900 на номер +7901\n'
                        'Время создания звонка: 06.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_1, url_2\n'
                        'Ошибка: -\n'
                        'АТС: \n'
                    ),
                },
                {
                    'createdAt': '2018-05-07T11:22:33',
                    'createdBy': 123,
                    'text': (
                        'Оператор user_id1 совершил звонок '
                        'с номера +7902 на номер +7903\n'
                        'Время создания звонка: 07.05.2018 14:22:33\n'
                        'Время установления соединения: '
                        '01.01.2019 14:22:33\n'
                        'Время ответа на вызов: 01.01.2019 14:22:33\n'
                        'Время окончания вызова: -\n'
                        'Направление вызова: исходящий\n'
                        'Статус звонка: отвечен\n'
                        'Инициатор разрыва звонка: -\n'
                        'Идентификатор вызова: provider_id\n'
                        'Список записей звонка: url_3, url_4\n'
                        'Ошибка: err\n'
                        'АТС: \n'
                    ),
                },
            ],
            {'tags': {'add': 'copy_from_chatterbox'}},
            None,
            'open',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    STARTRACK_SUPPORT_USER_ID=123,
    STARTRACK_CLIENT_USER_ID=456,
    MAX_STARTRACK_TAG_LENGTH=30,
    STARTRACK_SUPPORT_COPY_QUEUE='TESTQUEUE',
)
@pytest.mark.translations(
    chatterbox={'copy_to_tracker': {'ru': 'Копия тикета: {task_id}'}},
)
async def test_startrack_copy(
        cbox: conftest.CboxWrap,
        mock_st_import_ticket,
        mock_st_get_ticket_with_status,
        mock_st_import_comment,
        mock_st_create_comment_old,
        mock_st_get_comments,
        mock_chat_get_history,
        mock_st_import_file,
        mock_st_create_link,
        mock_get_chat,
        mock_source_download_file,
        mock_st_update_ticket,
        mock_random_str_uuid,
        task_id_str,
        inner_comments,
        public_messages,
        expected_import_ticket,
        expected_import_comment,
        expected_update_ticket,
        expected_create_link,
        expected_ticket_status,
):
    mock_st_get_ticket_with_status('closed')
    st_comments = [
        {
            'id': 'some_comment_id',
            'createdAt': '2018-01-02T03:45:00.000Z',
            'createdBy': {'id': 'some_id'},
            'updatedAt': '2018-01-02T03:45:00.000Z',
            'updatedBy': {'id': 'some_id'},
            'text': i['text'],
        }
        for i in public_messages
    ]
    mock_st_get_comments(st_comments)
    mock_chat_get_history({'messages': public_messages})
    mocked_update_ticket = mock_st_update_ticket('open')
    task_id = bson.objectid.ObjectId(task_id_str)
    mock_random_str_uuid()

    startrack_ticket = {
        'key': 'TESTQUEUE-1',
        'self': 'tracker/TESTQUEUE-1',
        'createdAt': '2018-05-05T12:34:56',
        'updatedAt': '2018-05-05T14:34:56',
        'status': {'key': 'open'},
    }
    mocked_import_ticket = mock_st_import_ticket(startrack_ticket)

    startrack_comment = {
        'id': 'some_imported_comment_id',
        'key': 'dummy',
        'self': 'tracker/TESTQUEUE-1/comments/dummy',
    }
    mocked_import_comment = mock_st_import_comment(startrack_comment)

    finish_comment = {
        'id': 'some_finish_comment_id',
        'key': 'dummy',
        'self': 'tracker/TESTQUEUE-1/comments/dummy',
    }
    mocked_finish_comment = mock_st_create_comment_old(finish_comment)

    db_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    inner_comments.extend(
        await cbox.app.startrack_manager._prepare_hidden_comments_for_export(
            db_task,
        ),
    )

    await cbox.post(
        '/v1/tasks/{}/tracker_copy'.format(task_id),
        params={
            'additional_tag': 'additional_tag',
            'summary_tanker_key': 'copy_to_tracker',
            'queue': 'TESTQUEUE',
        },
        data={},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == 200
    assert cbox.body_data == {
        'next_frontend_action': 'open_url',
        'url': 'https://tracker.yandex.ru/TESTQUEUE-1',
    }

    del public_messages[0]

    cycle_range = len(public_messages) + len(inner_comments) + 1
    for _ in range(cycle_range):
        await stq_task.startrack_comment_import(
            cbox.app,
            task_id,
            startrack_ticket=startrack_ticket,
            inner_comments=inner_comments,
            public_messages=public_messages,
            action='copy',
        )

    import_ticket_calls = mocked_import_ticket.calls
    assert import_ticket_calls[0]['kwargs']['json'] == expected_import_ticket

    import_comment_calls = mocked_import_comment.calls
    if expected_import_comment is None:
        assert not import_comment_calls
    else:
        assert len(import_comment_calls) == len(expected_import_comment)
        for i, call in enumerate(import_comment_calls):
            assert call['ticket_id'] == 'TESTQUEUE-1'
            assert call['data'] == expected_import_comment[i]

    assert mocked_finish_comment.calls[0] == {
        'text': (
            'Ссылка на таск в chatterbox: '
            'https://supchat.taxi.dev.yandex-team.ru/chat/'
            '{} \n'.format(task_id)
        ),
        'ticket_id': 'TESTQUEUE-1',
    }

    create_link_calls = mock_st_create_link.calls
    if expected_create_link is None:
        assert not create_link_calls
    else:
        assert create_link_calls == expected_create_link

    if expected_update_ticket is not None:
        update_ticket_calls = mocked_update_ticket.calls
        assert update_ticket_calls[0]['ticket'] == 'TESTQUEUE-1'
        assert update_ticket_calls[0]['kwargs'] == expected_update_ticket

    db_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert 'startrack_ticket' not in db_task
    assert 'startrack_ticket_status' not in db_task

    assert db_task['history'][-1] == {
        'action_id': 'test_uid',
        'action': 'tracker_copy',
        'in_addition': False,
        'created': datetime.datetime(2018, 5, 7, 12, 44, 56),
        'login': 'superuser',
        'line': 'first',
    }


@pytest.mark.translations(
    chatterbox={
        'errors.tracker_copy_unique': {'ru': 'Копия уже создана {ticket_url}'},
    },
)
async def test_startrack_copy_unique(
        cbox: conftest.CboxWrap,
        mock_st_get_comments,
        mock_chat_get_history,
        mock_st_import_ticket,
        mock_st_get_ticket_by_unique_id,
):
    mock_st_get_comments([])
    mock_chat_get_history(
        {
            'messages': [
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'Test public comment',
                    'metadata': {
                        'created': '2018-05-05T14:34:56',
                        'attachments': [],
                    },
                },
            ],
        },
    )

    mocked_import_ticket = mock_st_import_ticket(status=409)
    startrack_ticket = {
        'key': 'TESTQUEUE-1',
        'self': 'tracker/TESTQUEUE-1',
        'createdAt': '2018-05-05T12:34:56',
        'updatedAt': '2018-05-05T14:34:56',
        'status': {'key': 'open'},
    }
    mock_st_get_ticket_by_unique_id(response=startrack_ticket)

    unique_prefix = 'prefix_'
    task_id = '5b2cae5cb2682a976914c2b9'
    unique = unique_prefix + task_id

    await cbox.post(
        '/v1/tasks/{}/tracker_copy'.format(task_id),
        params={
            'queue': 'TESTQUEUE',
            'summary_tanker_key': 'copy_to_tracker',
            'unique_prefix': unique_prefix,
        },
        data={},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == 409
    assert cbox.body_data == {
        'next_frontend_action': 'open_url',
        'url': 'https://tracker.yandex.ru/TESTQUEUE-1',
        'message': 'Копия уже создана https://tracker.yandex.ru/TESTQUEUE-1',
        'status': 'Chat already copy',
    }
    import_ticket_calls = mocked_import_ticket.calls
    assert import_ticket_calls[0]['kwargs']['json']['unique'] == unique
