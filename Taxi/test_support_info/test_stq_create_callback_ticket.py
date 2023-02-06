# pylint: disable=no-member
import datetime

import pytest

from taxi import discovery
from taxi.stq import client as stq_client

from support_info import stq_task


@pytest.mark.now('2021-01-10T12:00:00+0300')
@pytest.mark.parametrize(
    'driver_uuid, ticket_data, expected_create_ticket, driver_tags,'
    'expected_tags',
    [
        (
            '1_1',
            {
                'db': '59de5222293145d09d31cd1604f8f656',
                'driver_signal': 'Harry',
                'subject': 'ZOMG!',
                'tags': ['some', 'tags'],
                'app_version': '1.0',
                'device_model': 'iPhone X',
                'activity': 0.5,
                'rating': 5.0,
                'request_id': '123456',
            },
            {
                'custom_fields': {
                    'appVersion': '1.0',
                    'deviceModel': 'iPhone X',
                    'driverName': 'Швабрэ Старая Пристарая',
                    'taximeterVersion': '8.80',
                    'driverLicense': '97АВ123457',
                    'DriverUuid': '1_1',
                    'driverSignal': 'Harry',
                    'parkDbId': '2_2',
                    'clid': '100500',
                    'ParkPhone': '+79123',
                    'parkName': 'park_name',
                    'country': 'rus',
                },
                'queue': 'SUPPARTNERS',
                'summary': (
                    'Заказ обратного звонка водителю Швабрэ Старая '
                    'Пристарая ()'
                ),
                'description': 'ZOMG!',
                'tags': [
                    'не_в_крутилку',
                    'не_требует_закрытия',
                    'category_driver',
                    'заказ_звонка',
                ],
                'unique': '123456-callback-request',
            },
            [],
            [],
        ),
        (
            'with_phone',
            {
                'db': '59de5222293145d09d31cd1604f8f656',
                'driver_signal': 'Harry',
                'subject': 'Initial Message',
                'tags': ['some_tag'],
                'app_version': '1.0',
                'device_model': 'iPhone X',
                'activity': 0.5,
                'rating': 5.0,
                'request_id': '123456',
            },
            {},
            ['driver_tag_1', 'driver_tag_2'],
            [
                {'change_type': 'add', 'tag': 'some_tag'},
                {'change_type': 'add', 'tag': 'callback_driver_request'},
                {'change_type': 'add', 'tag': 'driver_tag_1'},
                {'change_type': 'add', 'tag': 'driver_tag_2'},
                {'change_type': 'delete', 'tag': 'driver_oktell_callback_tag'},
            ],
        ),
        (
            'with_phone',
            {
                'db': '59de5222293145d09d31cd1604f8f656',
                'driver_signal': 'Harry',
                'subject': 'Initial Message',
                'tags': ['some_tag'],
                'app_version': '1.0',
                'device_model': 'iPhone X',
                'activity': 0.5,
                'rating': 5.0,
                'request_id': '123456',
            },
            {},
            None,
            [
                {'change_type': 'add', 'tag': 'some_tag'},
                {'change_type': 'add', 'tag': 'callback_driver_request'},
                {'change_type': 'delete', 'tag': 'driver_oktell_callback_tag'},
            ],
        ),
        (
            'oktell_phone',
            {
                'db': '59de5222293145d09d31cd1604f8f656',
                'driver_signal': 'Harry',
                'subject': 'Initial Message',
                'tags': ['some_tag'],
                'app_version': '1.0',
                'device_model': 'iPhone X',
                'activity': 0.5,
                'rating': 5.0,
                'request_id': '123456',
            },
            {},
            None,
            [
                {'change_type': 'add', 'tag': 'some_tag'},
                {'change_type': 'add', 'tag': 'callback_driver_request'},
                {'change_type': 'add', 'tag': 'driver_oktell_callback_tag'},
            ],
        ),
    ],
)
async def test_create_callback_ticket(
        support_info_app_stq,
        mock_st_create_ticket,
        mock_driver_profiles,
        mock_driver_trackstory,
        mock_driver_priority,
        driver_uuid,
        ticket_data,
        expected_create_ticket,
        driver_tags,
        expected_tags,
        response_mock,
        patch_aiohttp_session,
        mockserver,
        patch,
):
    chatterbox_url = discovery.find_service('chatterbox').url
    support_chat_url = discovery.find_service('support_chat').url

    @mockserver.json_handler('/experiments3/v1/experiments')
    def _dummy_experiments_request(request):
        assert request.json == {
            'consumer': 'stq/driver_callback',
            'args': [
                {'name': 'driver_id', 'type': 'string', 'value': driver_uuid},
            ],
        }
        items = []
        if driver_uuid == 'oktell_phone':
            items.append({'name': 'driver_oktell_callback', 'value': {}})
        return {'items': items, 'version': 1}

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _dummy_driver_tags_request(*args, **kwargs):
        if driver_tags is None:
            return mockserver.make_response('', status=400)
        return {'tags': driver_tags}

    @patch_aiohttp_session(chatterbox_url, 'POST')
    def _dummy_chatterbox_request(method, url, **kwargs):
        assert url == chatterbox_url + '/v1/tasks'

        assert kwargs['json']['metadata']['update_tags'] == expected_tags

        for meta_action in kwargs['json']['metadata']['update_meta']:
            if meta_action['field_name'] == 'user_phone':
                return response_mock(json={'id': 'task_id'})

        raise AssertionError

    @patch_aiohttp_session(support_chat_url, 'POST')
    def _dummy_support_chat_request(method, url, **kwargs):
        assert url == support_chat_url + '/v1/chat'
        assert kwargs['json']['owner']['role'] == 'sms_client'
        assert kwargs['json']['owner']['id'] == 'callback_driver_+79999999999'
        assert kwargs['json']['metadata']['owner_phone'] == '+79999999999'
        return response_mock(json={'id': 'chat_id'})

    @patch('support_info.internal.stq_callback_ticket.execute_query')
    def _dummy_execute_query(connection_data, query):
        assert connection_data == {
            'host': 'db',
            'user': 'user',
            'password': 'password',
            'database': 'db',
        }
        assert (
            query
            == """
        IF EXISTS (SELECT [Ident]
                   FROM [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
                       WHERE [Number] = '+79999999999'
               -- Только открытых
               and IsNull([Closed],0) = 0)
          --
          BEGIN
            -- Закрываем открытых старых
            Update [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
            Set [Closed] = 1
               ,[ClosedNote] = 'Дубль, абонент загружен как новый'
                WHERE [Number] = '+79999999999'
              -- Только открытых
              and IsNull([Closed],0) = 0
          END -- EXISTS

        --  Сохраняем нового абонента
        Insert Into [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
        ([DateAdd],[Number],[Fio],[Source], [RequestId])
        values (GetDate(),'+79999999999','Водитель Лучший Мировой',
        'procedure', 'task_id')
    """
        )

    await stq_task.create_callback_ticket(
        support_info_app_stq, driver_uuid, ticket_data,
    )

    driver_doc = await support_info_app_stq.db.secondary.dbdrivers.find_one(
        {'driver_id': driver_uuid},
    )
    stq_calls = stq_client.put.calls
    if driver_doc['phones'] == ['']:
        create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
        assert create_ticket_kwargs == expected_create_ticket
        assert not stq_calls
    else:
        assert _dummy_chatterbox_request.calls
        assert _dummy_support_chat_request.calls
        if driver_uuid == 'oktell_phone':
            stq_calls[0].pop('loop')
            stq_calls[0].pop('kwargs')
            assert stq_calls[0] == {
                'args': ('task_id',),
                'queue': 'support_info_callback_oktell_task_queue',
                'task_id': None,
                'eta': datetime.datetime(2021, 1, 10, 9, 0, 10),
            }
        else:
            assert not stq_calls


@pytest.mark.now('2021-01-10T12:00:00+0300')
@pytest.mark.parametrize(
    'use_dialogscript, expected_query_filename, task_data, expected_params',
    [
        (
            False,
            'oktell_legacy_query.sql',
            {
                'id': 'task_id',
                'line': 'first',
                'status': 'new',
                'meta_info': {},
            },
            None,
        ),
        (
            False,
            'oktell_legacy_query.sql',
            {
                'id': 'task_id',
                'line': 'first',
                'status': 'predispatch',
                'meta_info': {'driver_phone': '+79999999999'},
            },
            None,
        ),
        (
            False,
            'oktell_legacy_query.sql',
            {
                'id': 'task_id',
                'line': 'first',
                'status': 'new',
                'meta_info': {'driver_phone': '+79999999999'},
            },
            (
                'first',
                '+79999999999',
                '+79999999999',
                'first',
                '+79999999999',
                '',
                'first',
                'task_id',
                '+79999999999',
                '',
                'first',
                'task_id',
            ),
        ),
        (
            False,
            'oktell_legacy_query.sql',
            {
                'id': 'task_id',
                'line': 'second',
                'status': 'reopened',
                'meta_info': {
                    'driver_phone': '+79999999998',
                    'driver_name': 'Тестовый Тест',
                },
            },
            (
                'second',
                '+79999999998',
                '+79999999998',
                'second',
                '+79999999998',
                'Тестовый Тест',
                'second',
                'task_id',
                '+79999999998',
                'Тестовый Тест',
                'second',
                'task_id',
            ),
        ),
        (
            True,
            'oktell_actual_query.sql',
            {
                'id': 'task_id',
                'line': 'first',
                'status': 'new',
                'meta_info': {},
            },
            None,
        ),
        (
            True,
            'oktell_actual_query.sql',
            {
                'id': 'task_id',
                'line': 'first',
                'status': 'predispatch',
                'meta_info': {'driver_phone': '+79999999999'},
            },
            None,
        ),
        (
            True,
            'oktell_actual_query.sql',
            {
                'id': 'task_id',
                'line': 'first',
                'status': 'new',
                'meta_info': {'driver_phone': '+79999999999'},
            },
            (
                'first',
                '+79999999999',
                '+79999999999',
                'first',
                '+79999999999',
                '',
                'first',
                'task_id',
                '+79999999999',
                '',
                'first',
                'task_id',
                '+79999999999',
                '',
                'first',
                'task_id',
            ),
        ),
        (
            True,
            'oktell_actual_query.sql',
            {
                'id': 'task_id',
                'line': 'second',
                'status': 'reopened',
                'meta_info': {
                    'driver_phone': '+79999999998',
                    'driver_name': 'Тестовый Тест',
                },
            },
            (
                'second',
                '+79999999998',
                '+79999999998',
                'second',
                '+79999999998',
                'Тестовый Тест',
                'second',
                'task_id',
                '+79999999998',
                'Тестовый Тест',
                'second',
                'task_id',
                '+79999999998',
                'Тестовый Тест',
                'second',
                'task_id',
            ),
        ),
    ],
)
async def test_create_oktell_task(
        support_info_app_stq,
        load,
        task_data,
        use_dialogscript,
        expected_query_filename,
        expected_params,
        patch_aiohttp_session,
        mockserver,
        response_mock,
        patch,
):
    chatterbox_url = discovery.find_service('chatterbox').url
    cfg = support_info_app_stq.config
    cfg.SUPPORT_INFO_USE_DIALOGSCRIPT_TO_CHECK_OKTELL = use_dialogscript
    expected_query = load(expected_query_filename)

    @patch_aiohttp_session(chatterbox_url, 'GET')
    def _dummy_chatterbox_request(method, url, **kwargs):
        assert url == chatterbox_url + '/v1/tasks/task_id'
        return response_mock(json=task_data)

    @patch('support_info.internal.stq_callback_ticket.execute_query')
    def _dummy_execute_query(connection_data, query, params):
        assert connection_data == {
            'host': 'db',
            'user': 'user',
            'password': 'password',
            'database': 'db',
        }
        assert params == expected_params
        assert query.strip() == expected_query.strip()

    await stq_task.create_callback_oktell_task(support_info_app_stq, 'task_id')
    stq_calls = stq_client.put.calls
    if task_data['status'] == 'predispatch':
        stq_calls[0].pop('loop')
        stq_calls[0].pop('kwargs')
        assert stq_calls[0] == {
            'args': ('task_id',),
            'queue': 'support_info_callback_oktell_task_queue',
            'task_id': None,
            'eta': datetime.datetime(2021, 1, 10, 9, 0, 10),
        }
    else:
        assert not stq_calls
        if not task_data['meta_info'].get('driver_phone'):
            assert not _dummy_execute_query.calls
        else:
            assert _dummy_execute_query.calls
