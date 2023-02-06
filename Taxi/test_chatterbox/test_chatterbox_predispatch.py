# pylint: disable=redefined-outer-name,too-many-arguments,too-many-locals
# pylint: disable=no-member, too-many-lines, inconsistent-return-statements
# pylint: disable=unused-variable
# pylint: disable=protected-access

import datetime
import json
import uuid

import bson
import pytest

from taxi import discovery
from taxi.clients import messenger_chat_mirror
from taxi.clients import translate
from taxi.clients import tvm
from taxi.clients import zen_dash

from chatterbox import stq_task
from chatterbox.internal import tasks_manager
from test_chatterbox import plugins as conftest

TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a1')
DRIVER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a2')
VIP_DRIVER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a3')
SMS_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a4')
SMS_AUTOREPLY_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a7')
ELITE_TASK_ID = bson.ObjectId('5bbcba1dee6a8715ced3e644')
FRAUD_TASK_ID = bson.ObjectId('5bbcba1dee6a8715ced3e666')
ONLINE_TASK_ID = bson.ObjectId('5bbcba1dee6a8715ced3e645')
OPTEUM_TASK_ID = bson.ObjectId('5b4cae5cb2682a126914c2a8')
LAVKA_TASK_ID = bson.ObjectId('5b4cae5cb2682a126914c2a9')
EATS_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2aa')
EATS_APP_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2ab')
EATS_APP_NO_ORDER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2ab')
EATS_COURIER_WITHOUT_ORDER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2bb')
EATS_COURIER_WITH_ORDER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2bc')
EMPTY_PHONE_TASK_ID = bson.ObjectId('5bbcba1dee6a8715ced3e777')
MARKET_ORDER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2dd')
MARKET_NO_ORDER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2ee')
MARKET_WRONG_ORDER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2ff')
MARKET_RETURN_TASK_ID = bson.ObjectId('5b2cae5cb2682a975054b3ee')
GROCERY_TASK_ID_LAVKA = bson.ObjectId('68384913664b45f601ec00bc')
GROCERY_TASK_ID_CLIENT = bson.ObjectId('e09871ad59a236627dfdf706')
GROCERY_TASK_ID_CLIENT_EATS = bson.ObjectId('3d38237285fa4dafc6e88fca')
GROCERY_TASK_ID_CLIENT_EATS_APP = bson.ObjectId('45abb8ef9d27c24d76519c3a')
GROCERY_TASK_ID_LAVKA_NO_ORDER = bson.ObjectId('0ced95bd9518a826128ca869')
MESSENGER_TASK_ID = bson.ObjectId('5c2cae5cb2682a976914c2a1')
COURIER_SLOTS_TASK_ID = bson.ObjectId('3d38237285fa5dafc6e88fca')
COURIER_SLOTS_REOPENED_TASK_ID = bson.ObjectId('3d38237285fa5dafc6e88fcb')
SERVICE_1_TASK_ID = bson.ObjectId('0ced95bd9518a826128ca732')
SERVICE_1_2_TASK_ID = bson.ObjectId('0ced95bd9518a826128ca754')
SERVICE_1_POST_UPDATE_TASK_ID = bson.ObjectId('0ced95bd9518a826128ca932')
SERVICE_1_2_POST_UPDATE_TASK_ID = bson.ObjectId('0ced95bd9518a826128ca954')
NOW = datetime.datetime(2018, 6, 15, 12, 34)
UUID = '00000000000040008000000000000000'


def _dummy_uuid4():
    return uuid.UUID(int=0, version=4)


def dummy_secret(*args, **kwargs):
    return '00000000000040008000000000000000'


# pylint: disable=too-many-statements
@pytest.fixture
def patch_support_chat_request(
        patch_aiohttp_session, response_mock, message_text,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def _dummy_support_chat_request(method, url, **kwargs):
        if url.endswith('/history'):
            return response_mock(
                json={
                    'messages': [
                        {
                            'id': '0',
                            'sender': {'id': 'some_login', 'role': 'support'},
                            'text': 'some support text',
                            'metadata': {'created': '2018-05-05T15:34:57'},
                        },
                        {
                            'id': '1',
                            'sender': {'id': 'some_login', 'role': 'client'},
                            'text': message_text,
                            'metadata': {'created': '2018-05-05T15:34:56'},
                        },
                    ],
                },
            )

        return response_mock(json={})

    return _dummy_support_chat_request


@pytest.fixture
def mock_messenger_request(monkeypatch, mock):
    def _wrap(message_text):
        @mock
        async def _dummy_get_history(*args, **kwargs):
            return {
                'messages': [
                    {
                        'id': '0',
                        'sender': {'id': 'some_login', 'role': 'support'},
                        'text': 'some support text',
                        'metadata': {'created': '2018-05-05T15:34:57'},
                    },
                    {
                        'id': '1',
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': message_text,
                        'metadata': {'created': '2018-05-05T15:34:56'},
                    },
                ],
            }

        monkeypatch.setattr(
            messenger_chat_mirror.MessengerChatMirrorApiClient,
            'get_history',
            _dummy_get_history,
        )
        return _dummy_get_history

    return _wrap


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'english': {
            'name': '1 · English',
            'priority': 1,
            'conditions': {'tags': 'lang_en'},
        },
        'elite': {
            'name': '1 · Элитка',
            'priority': 2,
            'conditions': {'tags': 'elite'},
        },
        'fraud': {
            'name': '1 · Попрошайка',
            'priority': 2,
            'conditions': {'tags': 'fraud'},
        },
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'sms_autoreply_first': {
            'name': 'SMS (автоответы)',
            'priority': 1,
            'autoreply_macro_id': 3,
        },
    },
    CHATTERBOX_META_ENRICH_SERVICES={
        'enabled': True,
        'services': {
            'test_service_1': {
                'enabled': True,
                'tvm_name': 'test',
                'url': 'http://test.ing/enrich_meta/test1',
                'conditions': {},
                'metadata_mapping': {
                    'order_id': 'order_id',
                    'user_id': 'user_id',
                },
            },
            'test_service_2': {
                'enabled': True,
                'tvm_name': 'test',
                'url': 'http://test.ing/enrich_meta/test2',
                'conditions': {
                    'fields/test_service_2_field': {'#exists': True},
                },
                'metadata_mapping': {
                    'some_unfulfilled_field': 'some_unfulfilled_field',
                },
                'meta_prefix': 's2',
            },
        },
    },
    NATIVE_LANGUAGES=['ru'],
)
@pytest.mark.parametrize(
    (
        'task_id',
        'message_text',
        'lang',
        'expected_tags',
        'expected_status',
        'expected_request_data',
        'expected_response_meta',
    ),
    [
        (
            SERVICE_1_TASK_ID,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            'new',
            {
                'test1': {
                    'metadata': {'order_id': '12345', 'user_id': 'user_id'},
                },
            },
            {
                'order_id': '12345',
                'user_id': 'user_id',
                'order_cost': 657,
                'user_score': 4.5,
                'driver_id': 'driver_id_1',
                'plus_user': True,
                'user_tags': ['tag1', 'tag2'],
            },
        ),
        (
            SERVICE_1_2_TASK_ID,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            'new',
            {
                'test1': {
                    'metadata': {'order_id': '12345', 'user_id': 'user_id'},
                },
                'test2': {'metadata': {}},
            },
            {
                'order_id': '12345',
                'user_id': 'user_id',
                'order_cost': 657,
                'user_score': 4.5,
                'driver_id': 'driver_id_1',
                'plus_user': True,
                'user_tags': ['tag1', 'tag2'],
                's2_service_2': True,
            },
        ),
    ],
)
async def test_services_meta_enrich_predispatch(
        cbox: conftest.CboxWrap,
        patch_aiohttp_session,
        response_mock,
        patch_support_chat_request,
        mock_messenger_request,
        stq,
        simple_secdist,
        monkeypatch,
        mock_translate,
        mock_randint,
        mock_get_tags_v1,
        mock_get_user_phone,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_market_crm_get_order_meta,
        mock_personal,
        task_id,
        message_text,
        lang,
        expected_tags,
        expected_status,
        mockserver,
        mock_uuid_uuid4,
        expected_request_data,
        expected_response_meta,
):
    mock_messenger_request(message_text)
    mock_translate(lang)
    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }
    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    @patch_aiohttp_session('http://test.ing/enrich_meta', 'POST')
    def _dummy_enrich_meta(method, url, **kwargs):
        endpoint = url[len('http://test.ing/enrich_meta/') :]
        assert kwargs['json'] == expected_request_data.get(endpoint)
        if endpoint == 'test1':
            response = {
                'metadata': {
                    'order_id': '12345',
                    'user_id': 'user_id',
                    'order_cost': 657,
                    'user_score': 4.5,
                    'driver_id': 'driver_id_1',
                    'plus_user': True,
                    'user_tags': ['tag1', 'tag2'],
                },
            }
        elif endpoint == 'test2':
            response = {'metadata': {'service_2': True}}
        else:
            response = {}
        return response_mock(json=response)

    await stq_task.chatterbox_predispatch(cbox.app, task_id)

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    if lang:
        assert task['meta_info']['task_language'] == lang

    assert task['status'] == expected_status
    assert 'tags' in task
    assert expected_tags == set(task['tags'])

    if expected_response_meta:
        for meta_key, meta_val in expected_response_meta.items():
            assert task['meta_info'].get(meta_key) == meta_val


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'english': {
            'name': '1 · English',
            'priority': 1,
            'conditions': {'tags': 'lang_en'},
        },
        'elite': {
            'name': '1 · Элитка',
            'priority': 2,
            'conditions': {'tags': 'elite'},
        },
        'fraud': {
            'name': '1 · Попрошайка',
            'priority': 2,
            'conditions': {'tags': 'fraud'},
        },
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'sms_autoreply_first': {
            'name': 'SMS (автоответы)',
            'priority': 1,
            'autoreply_macro_id': 3,
        },
    },
    CHATTERBOX_META_ENRICH_SERVICES={
        'enabled': True,
        'services': {
            'test_service_1': {
                'enabled': True,
                'tvm_name': 'test',
                'url': 'http://test.ing/enrich_meta/test1',
                'conditions': {},
                'metadata_mapping': {
                    'order_id': 'order_id',
                    'user_id': 'user_id',
                },
            },
            'test_service_2': {
                'enabled': True,
                'tvm_name': 'test',
                'url': 'http://test.ing/enrich_meta/test2',
                'conditions': {
                    'fields/test_service_2_field': {'#exists': True},
                },
                'metadata_mapping': {
                    'some_unfulfilled_field': 'some_unfulfilled_field',
                },
                'meta_prefix': 's2',
            },
        },
    },
    NATIVE_LANGUAGES=['ru'],
)
@pytest.mark.parametrize(
    (
        'task_id',
        'message_text',
        'lang',
        'expected_tags',
        'expected_status',
        'expected_request_data',
        'expected_response_meta',
    ),
    [
        (
            SERVICE_1_POST_UPDATE_TASK_ID,
            'сообщение на русском',
            'ru',
            set(),
            'reopened',
            {
                'test1': {
                    'metadata': {'order_id': '12345', 'user_id': 'user_id'},
                },
            },
            {
                'order_id': '12345',
                'user_id': 'user_id',
                'order_cost': 657,
                'user_score': 4.5,
                'driver_id': 'driver_id_1',
                'plus_user': True,
                'user_tags': ['tag1', 'tag2'],
            },
        ),
        (
            SERVICE_1_2_POST_UPDATE_TASK_ID,
            'сообщение на русском',
            'ru',
            set(),
            'reopened',
            {
                'test1': {
                    'metadata': {'order_id': '12345', 'user_id': 'user_id'},
                },
                'test2': {'metadata': {}},
            },
            {
                'order_id': '12345',
                'user_id': 'user_id',
                'order_cost': 657,
                'user_score': 4.5,
                'driver_id': 'driver_id_1',
                'plus_user': True,
                'user_tags': ['tag1', 'tag2'],
                's2_service_2': True,
            },
        ),
    ],
)
async def test_services_meta_enrich_post_update(
        cbox: conftest.CboxWrap,
        patch_aiohttp_session,
        response_mock,
        patch_support_chat_request,
        mock_messenger_request,
        stq,
        simple_secdist,
        monkeypatch,
        mock_translate,
        mock_randint,
        mock_get_tags_v1,
        mock_get_user_phone,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_market_crm_get_order_meta,
        mock_personal,
        task_id,
        message_text,
        lang,
        expected_tags,
        expected_status,
        mockserver,
        mock_uuid_uuid4,
        expected_request_data,
        expected_response_meta,
):
    mock_messenger_request(message_text)
    mock_translate(lang)
    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }
    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    @patch_aiohttp_session('http://test.ing/enrich_meta', 'POST')
    def _dummy_enrich_meta(method, url, **kwargs):
        endpoint = url[len('http://test.ing/enrich_meta/') :]
        assert kwargs['json'] == expected_request_data.get(endpoint)
        if endpoint == 'test1':
            response = {
                'metadata': {
                    'order_id': '12345',
                    'user_id': 'user_id',
                    'order_cost': 657,
                    'user_score': 4.5,
                    'driver_id': 'driver_id_1',
                    'plus_user': True,
                    'user_tags': ['tag1', 'tag2'],
                },
            }
        elif endpoint == 'test2':
            response = {'metadata': {'service_2': True}}
        else:
            response = {}
        return response_mock(json=response)

    await stq_task.post_update(cbox.app, task_id)

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})

    assert task['status'] == expected_status
    assert 'tags' in task
    assert expected_tags == set(task['tags'])

    if expected_response_meta:
        for meta_key, meta_val in expected_response_meta.items():
            assert task['meta_info'].get(meta_key) == meta_val


@pytest.mark.now('2020-01-20T11:05:42')
@pytest.mark.parametrize(
    ('metadata', 'order_delay_minutes'),
    [
        ({}, None),
        ({'order_delivered_at': '2020-01-20T18:02:42+0700'}, None),
        (
            {
                'order_promised_at': '2020-01-20T18:02:42+0700',
                'order_delivered_at': '2020-01-20T18:02:42+0700',
            },
            0,
        ),
        (
            {
                'order_promised_at': '2020-01-20T18:02:42+0700',
                'order_delivered_at': '2020-01-20T18:05:42+0700',
            },
            3,
        ),
        (
            {
                'order_promised_at': '2020-01-20T18:02:42+0700',
                'order_cancelled_at': '2020-01-20T18:01:42+0700',
            },
            0,
        ),
        (
            {
                'order_promised_at': '2020-01-20T18:02:42+0700',
                'order_cancelled_at': '2020-01-20T18:05:42+0700',
            },
            3,
        ),
        ({'order_promised_at': '2020-01-20T18:02:42+0700'}, 3),
        ({'order_promised_at': '2020-01-20T18:07:42+0700'}, 0),
    ],
)
def test_calculate_order_delay_minutes(cbox, metadata, order_delay_minutes):
    cbox.app.metadata_manager._calculate_order_delay_minutes(metadata)
    assert metadata.get('order_delay_minutes') == order_delay_minutes


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_AUTOREPLY={
        'client': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['client']}},
            'langs': ['ru', 'fr'],
            'delay_range': [300, 600],
            'project_id': 'client',
            'event_type': 'client',
        },
        'driver': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['driver']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'driver',
            'event_type': 'driver',
            'predispatch_routing': True,
        },
    },
    CHATTERBOX_LINES={
        'english': {
            'name': '1 · English',
            'priority': 1,
            'conditions': {'tags': 'lang_en'},
        },
        'elite': {
            'name': '1 · Элитка',
            'priority': 2,
            'conditions': {'tags': 'elite'},
        },
        'fraud': {
            'name': '1 · Попрошайка',
            'priority': 2,
            'conditions': {'tags': 'fraud'},
        },
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'sms_autoreply_first': {
            'name': 'SMS (автоответы)',
            'priority': 1,
            'autoreply': True,
        },
    },
    NATIVE_LANGUAGES=['ru'],
    CHATTERBOX_ALLOWED_EXTERNAL_TAGS=['support_vip', 'support_elite'],
    CHATTERBOX_PASSENGER_TAGS_ENABLED=True,
    CHATTERBOX_AUTOREPLY_USE_EVENT_TYPE=True,
    PASS_STATUS_IF_FAIL_TO_STQ_CHATTERBOX_AUTOREPLY=True,
    GET_ORDER_META_FROM_EATS_SUPPORT_MISC=True,
    CHATTERBOX_LAVKA_COURIER_SLOTS_INFO_FETCH_ENABLED=True,
    CHATTERBOX_MARKET_RETURN_ENABLED=True,
    CHATTERBOX_MARKET_CHECKOUTER_CHECK_DIFF_ENABLED=True,
)
@pytest.mark.parametrize(
    (
        'task_id',
        'message_text',
        'lang',
        'expected_tags',
        'autoreply_status',
        'autoreply_tags',
        'autoreply_macro_id',
        'expected_status',
        'expected_autoreply_data',
        'expected_autoreply_text',
        'expected_stat',
        'ml_success',
        'expected_autoreply_put_calls',
        'expected_get_tags_v1',
        'expected_get_tags_v2',
        'get_tags_service',
        'event_type',
        'expected_lavka_wms_meta',
        'expected_market_meta',
        'expected_grocery_order_meta',
        'expected_lavka_courier_slots_meta',
        'expected_eats_courier_meta',
    ),
    [
        (
            TASK_ID,
            'сообщение на русском',
            'ru',
            {
                'autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_ru',
                'support_elite',
                'support_vip',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            },
            ['reply', 'close'],
            ['autoreply'],
            1,
            'autoreply_in_progress',
            [
                {'key': 'cancel_time', 'value': 120},
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_distance', 'value': 15.5},
                {'key': 'order_id', 'value': 'order_id'},
                {'key': 'order_pre_distance', 'value': 15.0},
                {'key': 'order_pre_time', 'value': 83},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'order_timestamp', 'value': 1526417460},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            'Какой-то текст',
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'autoreply_request_successful': 1,
                'autoreply_response_with_answer': 1,
            },
            True,
            [
                {
                    'queue': 'chatterbox_common_autoreply_queue',
                    'eta': NOW + datetime.timedelta(minutes=10),
                    'args': [
                        {'$oid': str(TASK_ID)},
                        {'close': {'macro_id': 1}},
                        'client',
                    ],
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            {
                'entities': [
                    {
                        'id': '000000000000000000000000',
                        'type': 'user_phone_id',
                    },
                ],
            },
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        pytest.param(
            TASK_ID,
            'сообщение на русском',
            None,
            {
                'check_ml_autoreply',
                'check_autoreply_project_client',
                'lang_none',
            },
            None,
            [],
            None,
            'new',
            [
                {'key': 'cancel_time', 'value': 120},
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_distance', 'value': 15.5},
                {'key': 'order_id', 'value': 'order_id'},
                {'key': 'order_pre_distance', 'value': 15.0},
                {'key': 'order_pre_time', 'value': 83},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'order_timestamp', 'value': 1526417460},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            None,
            True,
            [],
            None,
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
            marks=[
                pytest.mark.config(
                    CHATTERBOX_FORBIDDEN_EXTERNAL_REQUESTS={
                        'client': {
                            '__default__': False,
                            'predispatch': True,
                            'additional_meta': True,
                        },
                    },
                ),
            ],
        ),
        (
            TASK_ID,
            'сообщение на русском',
            'ru',
            {
                'autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_ru',
                'support_elite',
                'support_vip',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            },
            ['reply'],
            ['autoreply'],
            1,
            'autoreply_in_progress',
            [
                {'key': 'cancel_time', 'value': 120},
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_distance', 'value': 15.5},
                {'key': 'order_id', 'value': 'order_id'},
                {'key': 'order_pre_distance', 'value': 15.0},
                {'key': 'order_pre_time', 'value': 83},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'order_timestamp', 'value': 1526417460},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            'Какой-то текст',
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'autoreply_request_successful': 1,
                'autoreply_response_with_answer': 1,
            },
            True,
            [
                {
                    'queue': 'chatterbox_common_autoreply_queue',
                    'eta': NOW + datetime.timedelta(minutes=10),
                    'args': [
                        {'$oid': str(TASK_ID)},
                        {'comment': {'macro_id': 1}},
                        'client',
                    ],
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            {
                'entities': [
                    {
                        'id': '000000000000000000000000',
                        'type': 'user_phone_id',
                    },
                ],
            },
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            TASK_ID,
            'другое сообщение на русском',
            'ru',
            {
                'ar_nto',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_ru',
                'support_elite',
                'support_vip',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            },
            ['close'],
            ['ar_nto'],
            None,
            'autoreply_in_progress',
            [
                {'key': 'cancel_time', 'value': 120},
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_distance', 'value': 15.5},
                {'key': 'order_id', 'value': 'order_id'},
                {'key': 'order_pre_distance', 'value': 15.0},
                {'key': 'order_pre_time', 'value': 83},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'order_timestamp', 'value': 1526417460},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {
                    'key': 'comment_lowercased',
                    'value': 'другое сообщение на русском',
                },
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'autoreply_request_successful': 1,
                'autoreply_response_dismiss': 1,
            },
            None,
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a1'},
                        {'dismiss': {}},
                        'client',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {'status_if_fail': 'reopened'},
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
            {
                'entities': [
                    {
                        'id': '000000000000000000000000',
                        'type': 'user_phone_id',
                    },
                ],
            },
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            TASK_ID,
            'message en français',
            'fr',
            {
                'autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'foreign_lang',
                'lang_fr',
                'promo',
                'support_elite',
                'support_vip',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            },
            ['reply', 'close'],
            ['promo', 'autoreply'],
            2,
            'autoreply_in_progress',
            [
                {'key': 'cancel_time', 'value': 120},
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_distance', 'value': 15.5},
                {'key': 'order_id', 'value': 'order_id'},
                {'key': 'order_pre_distance', 'value': 15.0},
                {'key': 'order_pre_time', 'value': 83},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'fr'},
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'order_timestamp', 'value': 1526417460},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'message en français'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            'Промокод promocode на 100 ₽',
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'autoreply_request_successful': 1,
                'autoreply_response_with_answer': 1,
            },
            False,
            [
                {
                    'queue': 'chatterbox_common_autoreply_queue',
                    'eta': NOW + datetime.timedelta(minutes=10),
                    'args': [
                        {'$oid': str(TASK_ID)},
                        {'close': {'macro_id': 2}},
                        'client',
                    ],
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            {
                'entities': [
                    {
                        'id': '000000000000000000000000',
                        'type': 'user_phone_id',
                    },
                ],
            },
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            TASK_ID,
            '123456',
            '',
            {
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_none',
                'support_elite',
                'support_vip',
            },
            None,
            None,
            None,
            'new',
            [
                {'key': 'cancel_time', 'value': 120},
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_distance', 'value': 15.5},
                {'key': 'order_id', 'value': 'order_id'},
                {'key': 'order_pre_distance', 'value': 15.0},
                {'key': 'order_pre_time', 'value': 83},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'order_timestamp', 'value': 1526417460},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': '123456'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            None,
            None,
            [],
            {
                'entities': [
                    {
                        'id': '000000000000000000000000',
                        'type': 'user_phone_id',
                    },
                ],
            },
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            TASK_ID,
            '',
            '',
            {
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_none',
                'support_elite',
                'support_vip',
            },
            None,
            None,
            None,
            'new',
            [
                {'key': 'cancel_time', 'value': 120},
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_distance', 'value': 15.5},
                {'key': 'order_id', 'value': 'order_id'},
                {'key': 'order_pre_distance', 'value': 15.0},
                {'key': 'order_pre_time', 'value': 83},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'order_timestamp', 'value': 1526417460},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': ''},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            None,
            None,
            [],
            {
                'entities': [
                    {
                        'id': '000000000000000000000000',
                        'type': 'user_phone_id',
                    },
                ],
            },
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            DRIVER_TASK_ID,
            'сообщение от водителя на русском',
            'ru',
            {
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'lang_ru',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            },
            ['reply', 'close'],
            [],
            1,
            'autoreply_in_progress',
            [
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'driver_phone', 'value': '+74950000000'},
                {'key': 'driver_phone_pd_id', 'value': 'phone_pd_id_18'},
                {'key': 'tariff', 'value': 'econom'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'driver'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {
                    'key': 'comment_lowercased',
                    'value': 'сообщение от водителя на русском',
                },
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            'Какой-то текст',
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'driver_autoreply_request_successful': 1,
                'driver_autoreply_response_with_answer': 1,
            },
            None,
            [
                {
                    'queue': 'chatterbox_common_autoreply_queue',
                    'eta': NOW + datetime.timedelta(minutes=10),
                    'args': [
                        {'$oid': str(DRIVER_TASK_ID)},
                        {'close': {'macro_id': 1}},
                        'driver',
                    ],
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            None,
            None,
            None,
            'driver',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            DRIVER_TASK_ID,
            'сообщение от водителя на русском',
            'ru',
            {
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'lang_ru',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            },
            [],
            [],
            [],
            'new',
            [
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'driver_phone', 'value': '+74950000000'},
                {'key': 'driver_phone_pd_id', 'value': 'phone_pd_id_18'},
                {'key': 'tariff', 'value': 'econom'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'driver'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {
                    'key': 'comment_lowercased',
                    'value': 'сообщение от водителя на русском',
                },
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'driver_autoreply_request_successful': 1,
                'driver_autoreply_response_empty': 1,
            },
            None,
            [],
            None,
            None,
            None,
            'driver',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            DRIVER_TASK_ID,
            'сообщение от водителя на русском',
            'ru',
            {
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'lang_ru',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            },
            None,
            [],
            None,
            'new',
            [
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'driver_phone', 'value': '+74950000000'},
                {'key': 'driver_phone_pd_id', 'value': 'phone_pd_id_18'},
                {'key': 'tariff', 'value': 'econom'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'driver'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {
                    'key': 'comment_lowercased',
                    'value': 'сообщение от водителя на русском',
                },
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'driver_autoreply_request_successful': 1,
                'driver_autoreply_response_empty': 1,
            },
            None,
            [],
            None,
            None,
            None,
            'driver',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            SMS_TASK_ID,
            'сообщение от водителя на русском',
            'fr',
            {'lang_fr', 'foreign_lang'},
            None,
            [],
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        # сделать форвард в vip
        (
            VIP_DRIVER_TASK_ID,
            'сообщение от водителя на русском',
            'ru',
            {
                'lang_ru',
                'check_ml_autoreply',
                'check_autoreply_project_driver',
            },
            None,
            [],
            None,
            'new',
            [
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'driver_phone', 'value': '+74950000000'},
                {'key': 'driver_phone_pd_id', 'value': 'phone_pd_id_18'},
                {'key': 'tariff', 'value': 'vip'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'driver'},
                {'key': 'line', 'value': 'driver_first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {
                    'key': 'comment_lowercased',
                    'value': 'сообщение от водителя на русском',
                },
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            'driver',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            TASK_ID,
            'сообщение на русском',
            'ru',
            {
                'autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_ru',
                'support_elite',
                'support_vip',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            },
            ['reply', 'close'],
            ['autoreply'],
            4,
            'autoreply_in_progress',
            [
                {'key': 'cancel_time', 'value': 120},
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_distance', 'value': 15.5},
                {'key': 'order_id', 'value': 'order_id'},
                {'key': 'order_pre_distance', 'value': 15.0},
                {'key': 'order_pre_time', 'value': 83},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'order_timestamp', 'value': 1526417460},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            'park_compensation 100',
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'autoreply_request_successful': 1,
                'autoreply_response_with_answer': 1,
            },
            None,
            [
                {
                    'queue': 'chatterbox_common_autoreply_queue',
                    'eta': NOW + datetime.timedelta(minutes=10),
                    'args': [
                        {'$oid': str(TASK_ID)},
                        {'close': {'macro_id': 4}},
                        'client',
                    ],
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            {
                'entities': [
                    {
                        'id': '000000000000000000000000',
                        'type': 'user_phone_id',
                    },
                ],
            },
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            TASK_ID,
            'сообщение на русском',
            'ru',
            {
                'autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_ru',
                'support_elite',
                'support_vip',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            },
            ['reply', 'close'],
            ['autoreply'],
            5,
            'autoreply_in_progress',
            [
                {'key': 'cancel_time', 'value': 120},
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_distance', 'value': 15.5},
                {'key': 'order_id', 'value': 'order_id'},
                {'key': 'order_pre_distance', 'value': 15.0},
                {'key': 'order_pre_time', 'value': 83},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'order_timestamp', 'value': 1526417460},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            'refund 100',
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'autoreply_request_successful': 1,
                'autoreply_response_with_answer': 1,
            },
            None,
            [
                {
                    'queue': 'chatterbox_common_autoreply_queue',
                    'eta': NOW + datetime.timedelta(minutes=10),
                    'args': [
                        {'$oid': str(TASK_ID)},
                        {'close': {'macro_id': 5}},
                        'client',
                    ],
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            {
                'entities': [
                    {
                        'id': '000000000000000000000000',
                        'type': 'user_phone_id',
                    },
                ],
            },
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            OPTEUM_TASK_ID,
            'Всем привет!',
            'ru',
            {'lang_ru', 'support_vip', 'support_elite'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            {'entities': [{'id': 'some_park_db_id', 'type': 'park'}]},
            None,
            'tags',
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            LAVKA_TASK_ID,
            'Всем привет!',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            {
                'lavka_wms_store_id': 'some_lavka_store_id',
                'lavka_wms_title': 'some_lavka_title',
                'lavka_wms_cluster': 'some_lavka_cluster',
                'lavka_wms_added_prop': 'some_lavka_added_prop',
            },
            None,
            None,
            None,
            None,
        ),
        (
            MESSENGER_TASK_ID,
            'Всем привет!',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            'tags',
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            EATS_TASK_ID,
            'сообщение на русском',
            'ru',
            {
                'autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_ru',
                'support_elite',
                'support_vip',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            },
            ['reply', 'close'],
            ['autoreply'],
            1,
            'autoreply_in_progress',
            [
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_id', 'value': '12345'},
                {'key': 'service', 'value': 'eats'},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'is_blocked_user', 'value': False},
                {'key': 'eater_id', 'value': 'eater_id'},
                {'key': 'eater_name', 'value': 'Иван Иванович'},
                {'key': 'is_first_order', 'value': False},
                {'key': 'country_code', 'value': 'RU'},
                {'key': 'is_promocode_used', 'value': False},
                {'key': 'order_total_amount', 'value': 777},
                {
                    'key': 'order_delivered_at',
                    'value': '2020-01-20T18:02:42+0700',
                },
                {
                    'key': 'order_promised_at',
                    'value': '2020-01-20T18:00:00+0700',
                },
                {'key': 'order_delay_minutes', 'value': 2},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'autoreply_request_successful': 1,
                'autoreply_response_with_answer': 1,
            },
            True,
            [
                {
                    'queue': 'chatterbox_common_autoreply_queue',
                    'eta': NOW + datetime.timedelta(minutes=10),
                    'args': [
                        {'$oid': str(EATS_TASK_ID)},
                        {'close': {'macro_id': 1}},
                        'client',
                    ],
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            {
                'entities': [
                    {
                        'id': '000000000000000000000000',
                        'type': 'user_phone_id',
                    },
                ],
            },
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            EATS_APP_TASK_ID,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            [
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_id', 'value': '12345'},
                {'key': 'service', 'value': 'eats_app'},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'is_blocked_user', 'value': False},
                {'key': 'eater_id', 'value': 'eater_id'},
                {'key': 'eater_name', 'value': 'Иван Иванович'},
                {'key': 'is_first_order', 'value': False},
                {'key': 'country_code', 'value': 'RU'},
                {'key': 'is_promocode_used', 'value': False},
                {'key': 'order_total_amount', 'value': 777},
                {
                    'key': 'order_delivered_at',
                    'value': '2020-01-20T18:02:42+0700',
                },
                {
                    'key': 'order_promised_at',
                    'value': '2020-01-20T18:00:00+0700',
                },
                {'key': 'order_delay_minutes', 'value': 2},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client_eats_app'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            None,
            True,
            [],
            None,
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            EATS_APP_NO_ORDER_TASK_ID,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            [
                {'key': 'city', 'value': 'Moscow'},
                {'key': 'country', 'value': 'rus'},
                {'key': 'order_id', 'value': '12345'},
                {'key': 'service', 'value': 'eats_app'},
                {'key': 'user_phone', 'value': '+74950000000'},
                {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_18'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'is_blocked_user', 'value': False},
                {'key': 'eater_id', 'value': 'eater_id'},
                {'key': 'eater_name', 'value': 'Иван Иванович'},
                {'key': 'is_first_order', 'value': False},
                {'key': 'country_code', 'value': 'RU'},
                {'key': 'is_promocode_used', 'value': False},
                {'key': 'order_total_amount', 'value': 777},
                {
                    'key': 'order_delivered_at',
                    'value': '2020-01-20T18:02:42+0700',
                },
                {
                    'key': 'order_promised_at',
                    'value': '2020-01-20T18:00:00+0700',
                },
                {'key': 'order_delay_minutes', 'value': 2},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client_eats_app'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            None,
            True,
            [],
            None,
            None,
            'passenger-tags',
            'client',
            None,
            None,
            None,
            None,
            None,
        ),
        (
            MARKET_ORDER_TASK_ID,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            {
                'service': 'market',
                'order_id': '1234567',
                'city': 'Moscow',
                'country': 'rus',
                'user_phone': '+74950000000',
                'buyerAddressCity': 'Москва',
                'creationDate': '2020-01-10T10:10:10+03:00',
                'deliveryFromDate': '2020-01-15',
                'deliveryToDate': '2020-01-20',
                'deliveryService': {
                    'code': '50',
                    'title': 'TestPost',
                    'url': 'http://www.test-post.ru',
                },
                'deliveryType': {
                    'code': 'DELIVERY',
                    'title': 'Доставка курьером',
                },
                'orderdeliverytype': 'PICKUP',
                'originalDeliveryFromDate': '2020-01-14',
                'originalDeliveryToDate': '2020-01-19',
                'status': {'code': 'DELIVERY', 'title': 'передан в доставку'},
                'order_status': 'DELIVERY',
                'title': 1234567,
            },
            None,
            None,
            None,
        ),
        (
            MARKET_NO_ORDER_TASK_ID,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            {
                'service': 'market',
                'city': 'Moscow',
                'country': 'rus',
                'user_phone': '+74950000000',
                'user_phone_pd_id': 'phone_pd_id_18',
            },
            None,
            None,
            None,
        ),
        (
            MARKET_WRONG_ORDER_TASK_ID,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            {
                'service': 'market',
                'city': 'Moscow',
                'country': 'rus',
                'user_phone': '+74950000000',
                'user_phone_pd_id': 'phone_pd_id_18',
            },
            None,
            None,
            None,
        ),
        (
            MARKET_RETURN_TASK_ID,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            {
                'service': 'market',
                'order_return_id': '2384728',
                'order_id': '1234567',
                'return_fast': True,
                'order_status': 'DELIVERY',
                'orderdeliverytype': 'PICKUP',
                'return_delivery_track_code': '80100111111111',
                'return_delivery_post_track_needed': True,
            },
            None,
            None,
            None,
        ),
        (
            GROCERY_TASK_ID_LAVKA,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            {'order_id': '0000000', 'is_canceled': True, 'currency': 'RUB'},
            None,
            None,
        ),
        (
            GROCERY_TASK_ID_CLIENT,
            'сообщение на русском',
            'ru',
            {
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_ru',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            },
            None,
            None,
            None,
            'new',
            [
                {'key': 'order_id', 'value': '0000000'},
                {'key': 'service', 'value': 'grocery'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                {'key': 'is_canceled', 'value': True},
                {'key': 'currency', 'value': 'RUB'},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'client'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            {
                'autoreply_request_successful': 1,
                'autoreply_response_empty': 1,
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'name': 'user_support_chat_stats',
            },
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            {'order_id': '0000000', 'is_canceled': True, 'currency': 'RUB'},
            None,
            None,
        ),
        (
            GROCERY_TASK_ID_CLIENT_EATS,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            {
                'eats_order_id': '0000000',
                'is_canceled': True,
                'currency': 'RUB',
            },
            None,
            None,
        ),
        (
            GROCERY_TASK_ID_CLIENT_EATS_APP,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            {'order_id': '0000000', 'is_canceled': True, 'currency': 'RUB'},
            None,
            None,
        ),
        (
            GROCERY_TASK_ID_LAVKA_NO_ORDER,
            'сообщение на русском',
            'ru',
            {'lang_ru'},
            None,
            None,
            None,
            'new',
            None,
            None,
            None,
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            {},
            None,
            None,
        ),
        (
            COURIER_SLOTS_TASK_ID,
            'сообщение на русском',
            'ru',
            {
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'lang_ru',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            },
            None,
            None,
            None,
            'new',
            [
                {'key': 'park_driver_profile_id', 'value': 'some_courier_id'},
                {'key': 'work_mode', 'value': 'lavka_courier'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'lavka_courier_id', 'value': 'some_courier_id'},
                {
                    'key': 'lavka_current_slot_shift_id',
                    'value': 'some_current_slot_shift_id',
                },
                {
                    'key': 'lavka_current_slot_started_at',
                    'value': 'date_time_format_some_current_slot_started_at',
                },
                {
                    'key': 'lavka_current_slot_closes_at',
                    'value': 'date_time_format_some_current_slot_closes_at',
                },
                {
                    'key': 'lavka_current_slot_real_started_at',
                    'value': (
                        'date_time_format_some_current_slot_real_started_at'
                    ),
                },
                {
                    'key': 'lavka_current_slot_real_closes_at',
                    'value': (
                        'date_time_format_some_current_slot_real_closes_at'
                    ),
                },
                {'key': 'lavka_current_slot_status', 'value': 'processing'},
                {
                    'key': 'lavka_current_slot_store_id',
                    'value': 'some_store_id',
                },
                {'key': 'lavka_current_slot_delivery_type', 'value': 'car'},
                {'key': 'lavka_current_slot_active_pause', 'value': False},
                {
                    'key': 'lavka_last_slot_shift_id',
                    'value': 'some_last_slot_shift_id',
                },
                {
                    'key': 'lavka_last_slot_started_at',
                    'value': 'date_time_format_some_last_slot_started_at',
                },
                {
                    'key': 'lavka_last_slot_closes_at',
                    'value': 'date_time_format_some_last_slot_closes_at',
                },
                {
                    'key': 'lavka_last_slot_real_started_at',
                    'value': 'date_time_format_some_last_slot_real_started_at',
                },
                {
                    'key': 'lavka_last_slot_real_closes_at',
                    'value': 'date_time_format_some_last_slot_real_closes_at',
                },
                {'key': 'lavka_last_slot_status', 'value': 'complete'},
                {'key': 'lavka_last_slot_store_id', 'value': 'some_store_id'},
                {'key': 'lavka_last_slot_delivery_type', 'value': 'car'},
                {'key': 'lavka_store_id', 'value': 'some_lavka_store_id'},
                {'key': 'lavka_title', 'value': 'some_lavka_title'},
                {'key': 'lavka_cluster', 'value': 'some_lavka_cluster'},
                {'key': 'lavka_added_prop', 'value': 'some_lavka_added_prop'},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'driver'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {'key': 'comment_lowercased', 'value': 'сообщение на русском'},
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            {
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'name': 'user_support_chat_stats',
                'driver_autoreply_request_successful': 1,
                'driver_autoreply_response_empty': 1,
            },
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {
                'lavka_courier_id': 'some_courier_id',
                'lavka_added_prop': 'some_lavka_added_prop',
                'lavka_cluster': 'some_lavka_cluster',
                'lavka_current_slot_active_pause': False,
                'lavka_current_slot_closes_at': (
                    'date_time_format_some_current_slot_closes_at'
                ),
                'lavka_current_slot_delivery_type': 'car',
                'lavka_current_slot_real_closes_at': (
                    'date_time_format_some_current_slot_real_closes_at'
                ),
                'lavka_current_slot_real_started_at': (
                    'date_time_format_some_current_slot_real_started_at'
                ),
                'lavka_current_slot_shift_id': 'some_current_slot_shift_id',
                'lavka_current_slot_started_at': (
                    'date_time_format_some_current_slot_started_at'
                ),
                'lavka_current_slot_status': 'processing',
                'lavka_current_slot_store_id': 'some_store_id',
                'lavka_last_slot_closes_at': (
                    'date_time_format_some_last_slot_closes_at'
                ),
                'lavka_last_slot_delivery_type': 'car',
                'lavka_last_slot_real_closes_at': (
                    'date_time_format_some_last_slot_real_closes_at'
                ),
                'lavka_last_slot_real_started_at': (
                    'date_time_format_some_last_slot_real_started_at'
                ),
                'lavka_last_slot_shift_id': 'some_last_slot_shift_id',
                'lavka_last_slot_started_at': (
                    'date_time_format_some_last_slot_started_at'
                ),
                'lavka_last_slot_status': 'complete',
                'lavka_last_slot_store_id': 'some_store_id',
                'lavka_store_id': 'some_lavka_store_id',
                'lavka_title': 'some_lavka_title',
            },
            None,
        ),
        (
            EATS_COURIER_WITHOUT_ORDER_TASK_ID,
            'сообщение от курьера на русском',
            'ru',
            {
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'lang_ru',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            },
            None,
            [],
            None,
            'new',
            [
                {'key': 'park_driver_profile_id', 'value': 'some_courier_id'},
                {'key': 'work_mode', 'value': 'eda_courier'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'driver'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {
                    'key': 'comment_lowercased',
                    'value': 'сообщение от курьера на русском',
                },
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            {
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'name': 'user_support_chat_stats',
                'driver_autoreply_request_successful': 1,
                'driver_autoreply_response_empty': 1,
            },
            None,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            {},
        ),
        (
            EATS_COURIER_WITH_ORDER_TASK_ID,
            'сообщение от курьера на русском',
            'ru',
            {
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'lang_ru',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            },
            None,
            [],
            None,
            'new',
            [
                {'key': 'order_alias_id', 'value': 'order_of_vip_eater'},
                {'key': 'park_driver_profile_id', 'value': 'some_courier_id'},
                {'key': 'work_mode', 'value': 'eda_courier'},
                {
                    'key': 'ml_request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'task_language', 'value': 'ru'},
                {'key': 'city_label', 'value': 'Moscow'},
                {'key': 'brand_id', 'value': 'good_places'},
                {'key': 'order_total_amount', 'value': 777},
                {'key': 'is_vip_eater', 'value': True},
                {'key': 'request_repeated', 'value': True},
                {'key': 'chat_type', 'value': 'driver'},
                {'key': 'line', 'value': 'first'},
                {'key': 'screen_attach', 'value': False},
                {
                    'key': 'request_id',
                    'value': '00000000000040008000000000000000',
                },
                {'key': 'is_reopen', 'value': False},
                {'key': 'number_of_reopens', 'value': 0},
                {'key': 'all_tags', 'value': []},
                {'key': 'last_message_tags', 'value': []},
                {
                    'key': 'comment_lowercased',
                    'value': 'сообщение от курьера на русском',
                },
                {'key': 'number_of_orders', 'value': 0},
                {'key': 'minutes_from_order_creation', 'value': 59039},
                {'key': 'last_support_action', 'value': 'empty'},
            ],
            None,
            {
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'name': 'user_support_chat_stats',
                'driver_autoreply_request_successful': 1,
                'driver_autoreply_response_empty': 1,
            },
            None,
            [],
            None,
            {
                'match': [
                    {
                        'type': 'personal_phone_id',
                        'value': 'vip_eater_phone_id',
                    },
                ],
            },
            'eats-tags',
            None,
            None,
            None,
            None,
            None,
            {
                'city_label': 'Moscow',
                'order_total_amount': 777,
                'brand_id': 'good_places',
                'is_vip_eater': True,
            },
        ),
    ],
)
async def test_predispatch(
        cbox: conftest.CboxWrap,
        patch_aiohttp_session,
        response_mock,
        patch_support_chat_request,
        mock_messenger_request,
        stq,
        simple_secdist,
        monkeypatch,
        mock_translate,
        mock_randint,
        mock_get_tags_v1,
        mock_get_tags_v2,
        mock_get_user_phone,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_market_crm_get_order_meta,
        mock_checkouter_order,
        mock_checkouter_return,
        mock_personal,
        task_id,
        message_text,
        lang,
        expected_tags,
        autoreply_status,
        autoreply_tags,
        autoreply_macro_id,
        expected_status,
        expected_autoreply_data,
        expected_autoreply_text,
        expected_stat,
        ml_success,
        expected_autoreply_put_calls,
        expected_get_tags_v1,
        expected_get_tags_v2,
        event_type,
        get_tags_service,
        mockserver,
        mock_uuid_uuid4,
        expected_lavka_wms_meta,
        expected_market_meta,
        expected_grocery_order_meta,
        expected_lavka_courier_slots_meta,
        expected_eats_courier_meta,
):

    mock_messenger_request(message_text)
    mocked_get_tags_v1 = mock_get_tags_v1(
        tags_setting='simple', tags_service=get_tags_service or 'tags',
    )
    mocked_get_tags_v2 = mock_get_tags_v2(
        tags_setting='simple', tags_service=get_tags_service or 'tags',
    )

    mocked_translate = mock_translate(lang)
    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }
    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    initial_meta_info = (
        await cbox.db.support_chatterbox.find_one({'_id': task_id})
    )['meta_info']

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert kwargs['json']['features'] == expected_autoreply_data

        response = {}
        if autoreply_tags:
            response.setdefault('tag', {})
            response['tag']['add'] = autoreply_tags
        if not autoreply_status:
            return response_mock(json=response)
        if 'reply' in autoreply_status:
            response.setdefault('reply', {})
            response['reply']['text'] = autoreply_macro_id or 1
        if 'close' in autoreply_status:
            response.setdefault('close', {})
        return response_mock(json=response)

    lavka_wms_service = discovery.find_service('lavka-wms')

    @patch_aiohttp_session(lavka_wms_service.url)
    def mock_lavka_wms(method, url, **kwargs):
        assert url == lavka_wms_service.url + '/v1/load'
        data = kwargs['json']
        assert data['store_id'][0] == 'some_lavka_store_id'
        return response_mock(
            json={
                'code': 'OK',
                'store': [
                    {
                        'store_id': 'some_lavka_store_id',
                        'title': 'some_lavka_title',
                        'cluster': 'some_lavka_cluster',
                        'added_prop': 'some_lavka_added_prop',
                    },
                ],
            },
        )

    tracker_base_url = 'https://tracker.yandex.ru/'

    @patch_aiohttp_session(tracker_base_url)
    def mock_tracker(method, url, json, **kwargs):
        if (method == 'patch') and (
                url
                == tracker_base_url + 'issues/market_return_startrek_issue_1'
        ):
            assert json['userEmail'] == 'an@example.com'
            assert json['userPhone'] == '+70001234567'
            return response_mock(json={})
        if (
                method == 'get'
                and url
                == tracker_base_url + 'issues/market_return_startrek_issue_1'
        ):
            return response_mock(
                json={
                    'createdBy': {'id': '1'},
                    'summary': 'сообщение на русском',
                    'createdAt': '2022-03-31T13:31:11.915+0000',
                    'updatedAt': '2022-03-31T13:31:11.915+0000',
                },
            )
        if (
                method == 'get'
                and url
                == tracker_base_url
                + 'issues/market_return_startrek_issue_1/comments'
        ):
            return response_mock(json=[])
        return response_mock(json={})

    lavka_courier_slots_service = discovery.find_service('lavka-courier-slots')

    @patch_aiohttp_session(lavka_courier_slots_service.url)
    def mock_lavka_courier_slots(method, url, **kwargs):
        assert url == lavka_courier_slots_service.url + '/v1/support_info'
        assert method == 'get'
        query_params = kwargs['params']
        assert query_params['courier_id'] == 'some_courier_id'
        return response_mock(
            json={
                'courier_id': query_params['courier_id'],
                'current_slot_shift_id': 'some_current_slot_shift_id',
                'current_slot_started_at': (
                    'date_time_format_some_current_slot_started_at'
                ),
                'current_slot_closes_at': (
                    'date_time_format_some_current_slot_closes_at'
                ),
                'current_slot_real_started_at': (
                    'date_time_format_some_current_slot_real_started_at'
                ),
                'current_slot_real_closes_at': (
                    'date_time_format_some_current_slot_real_closes_at'
                ),
                'current_slot_status': 'processing',
                'current_slot_store_id': 'some_store_id',
                'current_slot_delivery_type': 'car',
                'current_slot_active_pause': False,
                'last_slot_shift_id': 'some_last_slot_shift_id',
                'last_slot_started_at': (
                    'date_time_format_some_last_slot_started_at'
                ),
                'last_slot_closes_at': (
                    'date_time_format_some_last_slot_closes_at'
                ),
                'last_slot_real_started_at': (
                    'date_time_format_some_last_slot_real_started_at'
                ),
                'last_slot_real_closes_at': (
                    'date_time_format_some_last_slot_real_closes_at'
                ),
                'last_slot_status': 'complete',
                'last_slot_store_id': 'some_store_id',
                'last_slot_delivery_type': 'car',
                'store_id': 'some_lavka_store_id',
                'title': 'some_lavka_title',
                'cluster': 'some_lavka_cluster',
                'added_prop': 'some_lavka_added_prop',
            },
        )

    grocery_orders_service = discovery.find_service('grocery-orders')

    @patch_aiohttp_session(grocery_orders_service.url)
    def mock_grocery_orders(method, url, **kwargs):
        assert method == 'post'
        assert (
            url
            == grocery_orders_service.url
            + '/internal/v1/get-chatterbox-order-meta/'
        )
        return response_mock(
            text=json.dumps({'is_canceled': True, 'currency': 'RUB'}),
        )

    support_info_service = discovery.find_service('support_info')

    @patch_aiohttp_session(support_info_service.url, 'POST')
    def _dummy_support_info(method, url, **kwargs):
        if 'autoreply' in url:
            response = {'autoreply': {'status': 'not_satisfy'}}
            initial_meta_info['lang'] = lang
            initial_meta_info['task_language'] = lang
            assert kwargs['json']['metadata']['ml_request_id'] == UUID
            kwargs['json']['metadata'].pop('ml_request_id')
            if autoreply_macro_id:
                response['autoreply']['macro_id'] = autoreply_macro_id
                response['autoreply']['status'] = 'ok'
            return response_mock(json=response)
        if 'payments' in url:
            if (
                    expected_autoreply_text
                    and 'park_compensation' in expected_autoreply_text
            ):
                assert 'X-YaTaxi-API-Key' in kwargs['headers']
                return response_mock(
                    json={'currency': 'RUB', 'compensation_sum': 100},
                )
            if expected_autoreply_text and 'refund' in expected_autoreply_text:
                assert 'X-YaTaxi-API-Key' in kwargs['headers']
                return response_mock(json={'currency': 'RUB', 'new_sum': 100})
        elif 'get_additional_meta' in url:
            initial_meta_info['ml_request_id'] = UUID
            initial_meta_info['task_language'] = lang
            assert kwargs['json'] == {'metadata': initial_meta_info}
            response = {'status': 'ok', 'metadata': initial_meta_info}
            return response_mock(json=response)

    @patch_aiohttp_session('/api/support_promocodes/generate', 'POST')
    def _dummy_generate(*args, **kwargs):
        return response_mock(json={'code': 'promocode'})

    await stq_task.chatterbox_predispatch(cbox.app, task_id)

    translate_calls = mocked_translate.calls
    if translate_calls:
        assert translate_calls
        assert translate_calls[0]['args'] == (
            'get',
            'http://test-translate-url/tr.json/detect',
        )
        assert translate_calls[0]['kwargs']
        assert translate_calls[0]['kwargs']['params']['srv'] == 'taxi'
        assert not translate_calls[0]['kwargs']['json']

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    if lang:
        assert task['meta_info']['task_language'] == lang

    assert task['status'] == expected_status
    assert 'tags' in task
    assert expected_tags == set(task['tags'])

    if expected_lavka_wms_meta is not None:
        for meta_key, meta_val in expected_lavka_wms_meta.items():
            assert task['meta_info'][meta_key] == meta_val
    stats = await cbox.app.db.event_stats.find_one({}, {'_id': False})
    assert stats == expected_stat

    autoreply_put_calls = [
        stq.chatterbox_common_autoreply_queue.next_call()
        for _ in range(stq.chatterbox_common_autoreply_queue.times_called)
    ]
    for call in autoreply_put_calls:
        del call['id']
        del call['kwargs']['log_extra']
        del call['kwargs']['request_id']
    assert autoreply_put_calls == expected_autoreply_put_calls

    if expected_get_tags_v1 is None:
        assert not mocked_get_tags_v1.times_called
    else:
        assert (
            mocked_get_tags_v1.next_call()['request'].json
            == expected_get_tags_v1
        )

    if expected_get_tags_v2 is None:
        assert not mocked_get_tags_v2.times_called
    else:
        assert (
            mocked_get_tags_v2.next_call()['request'].json
            == expected_get_tags_v2
        )

    if expected_market_meta is not None:
        for meta_key, meta_val in expected_market_meta.items():
            assert task['meta_info'][meta_key] == meta_val

    if expected_grocery_order_meta is not None:
        if not expected_grocery_order_meta:
            assert 'is_canceled' not in task['meta_info']
            assert 'currency' not in task['meta_info']
        for meta_key, meta_val in expected_grocery_order_meta.items():
            assert task['meta_info'][meta_key] == meta_val

    if expected_lavka_courier_slots_meta is not None:
        for meta_key, meta_val in expected_lavka_courier_slots_meta.items():
            assert task['meta_info'][meta_key] == meta_val

    if expected_eats_courier_meta is not None:
        for meta_key, meta_val in expected_eats_courier_meta.items():
            assert task['meta_info'][meta_key] == meta_val


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'english': {
            'name': '1 · English',
            'priority': 1,
            'conditions': {'tags': 'lang_en'},
        },
        'elite': {
            'name': '1 · Элитка',
            'priority': 2,
            'conditions': {'tags': 'elite'},
        },
        'fraud': {
            'name': '1 · Попрошайка',
            'priority': 2,
            'conditions': {'tags': 'fraud'},
        },
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'sms_autoreply_first': {
            'name': 'SMS (автоответы)',
            'priority': 1,
            'autoreply_macro_id': 3,
        },
    },
    NATIVE_LANGUAGES=['ru'],
    CHATTERBOX_LAVKA_COURIER_SLOTS_INFO_FETCH_ENABLED=True,
)
@pytest.mark.parametrize(
    (
        'task_id',
        'message_text',
        'lang',
        'expected_tags',
        'expected_status',
        'expected_stat',
        'expected_lavka_courier_slots_meta',
    ),
    [
        (
            COURIER_SLOTS_REOPENED_TASK_ID,
            'сообщение на русском',
            'ru',
            set(),
            'reopened',
            {
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'name': 'user_support_chat_stats',
                'driver_autoreply_request_successful': 1,
                'driver_autoreply_response_empty': 1,
            },
            {
                'lavka_courier_id': 'some_courier_id',
                'lavka_added_prop': 'some_lavka_added_prop',
                'lavka_cluster': 'some_lavka_cluster',
                'lavka_current_slot_active_pause': False,
                'lavka_current_slot_closes_at': (
                    'date_time_format_some_current_slot_closes_at'
                ),
                'lavka_current_slot_delivery_type': 'car',
                'lavka_current_slot_real_closes_at': (
                    'date_time_format_some_current_slot_real_closes_at'
                ),
                'lavka_current_slot_real_started_at': (
                    'date_time_format_some_current_slot_real_started_at'
                ),
                'lavka_current_slot_shift_id': 'some_current_slot_shift_id',
                'lavka_current_slot_started_at': (
                    'date_time_format_some_current_slot_started_at'
                ),
                'lavka_current_slot_status': 'processing',
                'lavka_current_slot_store_id': 'some_store_id',
                'lavka_last_slot_closes_at': (
                    'date_time_format_some_last_slot_closes_at'
                ),
                'lavka_last_slot_delivery_type': 'car',
                'lavka_last_slot_real_closes_at': (
                    'date_time_format_some_last_slot_real_closes_at'
                ),
                'lavka_last_slot_real_started_at': (
                    'date_time_format_some_last_slot_real_started_at'
                ),
                'lavka_last_slot_shift_id': 'some_last_slot_shift_id',
                'lavka_last_slot_started_at': (
                    'date_time_format_some_last_slot_started_at'
                ),
                'lavka_last_slot_status': 'complete',
                'lavka_last_slot_store_id': 'some_store_id',
                'lavka_store_id': 'some_lavka_store_id',
                'lavka_title': 'some_lavka_title',
            },
        ),
    ],
)
async def test_post_update(
        cbox: conftest.CboxWrap,
        patch_aiohttp_session,
        response_mock,
        patch_support_chat_request,
        mock_messenger_request,
        stq,
        simple_secdist,
        monkeypatch,
        mock_translate,
        mock_randint,
        mock_get_tags_v1,
        mock_get_user_phone,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_market_crm_get_order_meta,
        mock_personal,
        task_id,
        message_text,
        lang,
        expected_tags,
        expected_status,
        expected_stat,
        mockserver,
        mock_uuid_uuid4,
        expected_lavka_courier_slots_meta,
):
    mock_messenger_request(message_text)
    mock_translate(lang)
    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }
    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    lavka_courier_slots_service = discovery.find_service('lavka-courier-slots')

    @patch_aiohttp_session(lavka_courier_slots_service.url)
    def mock_lavka_courier_slots(method, url, **kwargs):
        assert url == lavka_courier_slots_service.url + '/v1/support_info'
        assert method == 'get'
        query_params = kwargs['params']
        assert query_params['courier_id'] == 'some_courier_id'
        return response_mock(
            json={
                'courier_id': query_params['courier_id'],
                'current_slot_shift_id': 'some_current_slot_shift_id',
                'current_slot_started_at': (
                    'date_time_format_some_current_slot_started_at'
                ),
                'current_slot_closes_at': (
                    'date_time_format_some_current_slot_closes_at'
                ),
                'current_slot_real_started_at': (
                    'date_time_format_some_current_slot_real_started_at'
                ),
                'current_slot_real_closes_at': (
                    'date_time_format_some_current_slot_real_closes_at'
                ),
                'current_slot_status': 'processing',
                'current_slot_store_id': 'some_store_id',
                'current_slot_delivery_type': 'car',
                'current_slot_active_pause': False,
                'last_slot_shift_id': 'some_last_slot_shift_id',
                'last_slot_started_at': (
                    'date_time_format_some_last_slot_started_at'
                ),
                'last_slot_closes_at': (
                    'date_time_format_some_last_slot_closes_at'
                ),
                'last_slot_real_started_at': (
                    'date_time_format_some_last_slot_real_started_at'
                ),
                'last_slot_real_closes_at': (
                    'date_time_format_some_last_slot_real_closes_at'
                ),
                'last_slot_status': 'complete',
                'last_slot_store_id': 'some_store_id',
                'last_slot_delivery_type': 'car',
                'store_id': 'some_lavka_store_id',
                'title': 'some_lavka_title',
                'cluster': 'some_lavka_cluster',
                'added_prop': 'some_lavka_added_prop',
            },
        )

    await stq_task.post_update(cbox.app, task_id)

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})

    assert task['status'] == expected_status
    assert 'tags' in task
    assert expected_tags == set(task['tags'])

    if expected_lavka_courier_slots_meta is not None:
        for meta_key, meta_val in expected_lavka_courier_slots_meta.items():
            assert task['meta_info'][meta_key] == meta_val


@pytest.mark.parametrize('message_text', ['some text'])
async def test_translate_fail(
        cbox,
        patch_support_chat_request,
        monkeypatch,
        mock,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_get_tags_v1,
        mock_get_user_phone,
        mock_personal,
        message_text,
):
    mock_get_tags_v1('empty', 'passenger-tags')

    @mock
    async def _dummy_detect(*args, **kwargs):
        raise translate.BaseError('AHAHA LOL!')

    @mock
    async def _dummy_autoreply(*args, **kwargs):
        return {'status': 'nope', 'tags': []}

    monkeypatch.setattr(
        translate.TranslateAPIClient, 'detect_language', _dummy_detect,
    )

    monkeypatch.setattr(
        zen_dash.ZenDashAPIClient, 'autoreply', _dummy_autoreply,
    )

    await stq_task.chatterbox_predispatch(cbox.app, TASK_ID)

    detect_calls = _dummy_detect.calls
    assert detect_calls
    assert detect_calls[0]['args'] == (message_text,)

    task = await cbox.db.support_chatterbox.find_one({'_id': TASK_ID})
    assert task['status'] == 'new'
    assert 'tags' in task
    assert 'lang_none' in task['tags']


async def test_dont_reply_if_exception(cbox, patch):
    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }

    @patch('chatterbox.internal.tasks_manager.TasksManager._process_comment')
    async def _process_comment(*args, **kwargs):
        raise tasks_manager.CommentProcessingError

    task_id = bson.ObjectId('5b4cae5cb2682a126914c2a7')
    await stq_task.chatterbox_common_autoreply(
        cbox.app, task_id, {'comment': {'macro_id': 3}}, 'client',
    )

    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert task['status'] == tasks_manager.STATUS_NEW
    assert tasks_manager.ACTION_FAIL_AUTOREPLY in [
        action['action'] for action in task['history']
    ]


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'elite': {
            'name': '1 · Элитка',
            'priority': 2,
            'mode': 'online',
            'conditions': {'tags': 'elite'},
        },
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': False},
        'online': {
            'name': 'Online',
            'priority': 4,
            'mode': 'online',
            'conditions': {'tags': 'online'},
        },
    },
    CHAT_LINE_TRANSITIONS={
        'first': ['elite', 'corp'],
        'second': ['corp', 'first'],
    },
)
@pytest.mark.parametrize(
    'task_id, put_task, message_text',
    [
        (ELITE_TASK_ID, True, 'text'),
        (TASK_ID, False, 'text'),
        (ONLINE_TASK_ID, True, 'text'),
    ],
)
async def test_predispatch_online_chat(
        cbox,
        stq,
        patch_support_chat_request,
        monkeypatch,
        mock,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_get_tags_v1,
        mock_get_user_phone,
        mock_personal,
        task_id,
        put_task,
        message_text,
):
    mock_get_tags_v1('empty', 'passenger-tags')

    @mock
    async def _dummy_detect(*args, **kwargs):
        return {'code': '200', 'lang': 'ru'}

    monkeypatch.setattr(
        translate.TranslateAPIClient, 'detect_language', _dummy_detect,
    )

    await stq_task.chatterbox_predispatch(cbox.app, task_id)

    if put_task:
        assert stq.chatterbox_online_chat_processing.times_called == 1
        call = stq.chatterbox_online_chat_processing.next_call()
        assert call['queue'] == 'chatterbox_online_chat_processing'
        assert call['eta'] == datetime.datetime(1970, 1, 1, 0, 0)
        assert call['args'] == [{'$oid': str(task_id)}, []]
    else:
        assert not stq.chatterbox_online_chat_processing.has_calls


@pytest.mark.config(
    CHATTERBOX_EXTERNAL_TAGS=[
        {
            'meta_info_key': 'phone_type',
            'entity_type': 'personal_phone_id',
            'chat_types': ['client'],
            'tag_services': ['passenger-tags', 'eats-tags'],
        },
    ],
    CHATTERBOX_ALLOWED_EXTERNAL_TAGS=[
        'success_tag_test_passenger',
        'success_tag_test_eats',
    ],
    TVM_RULES=[{'src': 'chatterbox', 'dst': 'personal'}],
    TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    ('task_id', 'message_text', 'expected_tags'),
    [
        (
            TASK_ID,
            'text',
            {'success_tag_test_passenger', 'success_tag_test_eats', 'lang_ru'},
        ),
        (EMPTY_PHONE_TASK_ID, 'text', {'lang_ru'}),
    ],
)
async def test_fetch_tags(
        cbox,
        mock_get_tags_v1,
        mock_personal_phone_id,
        mock,
        mock_personal,
        monkeypatch,
        message_text,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        task_id,
        patch_support_chat_request,
        patch,
        expected_tags,
):
    mock_get_tags_v1('personal_passenger', 'passenger-tags')
    mock_get_tags_v1('personal_eats', 'eats-tags')

    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return 'Ticket 123'

    @patch('taxi.clients.tvm.check_tvm')
    async def check_tvm(request, *args, **kwargs):
        assert request.headers['X-Ya-Service-Ticket'] == 'Ticket chatterbox'
        return tvm.CheckResult(src_service_name='developers')

    @mock
    async def _dummy_detect(*args, **kwargs):
        return {'code': '200', 'lang': 'ru'}

    @mock
    async def _dummy_autoreply(*args, **kwargs):
        return {'status': 'nope', 'tags': []}

    monkeypatch.setattr(
        translate.TranslateAPIClient, 'detect_language', _dummy_detect,
    )

    monkeypatch.setattr(
        zen_dash.ZenDashAPIClient, 'autoreply', _dummy_autoreply,
    )

    await stq_task.chatterbox_predispatch(cbox.app, task_id)

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert 'tags' in task
    assert set(task['tags']) == expected_tags
