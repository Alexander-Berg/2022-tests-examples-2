# pylint: disable=redefined-outer-name,no-member,unused-variable
import datetime

import bson
import pytest

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    'chat_id, message_id, sms_task',
    [
        (
            bson.ObjectId('5a433ca8779fb3302cc784bf'),
            'message_91',
            {
                'group_id': 0,
                'task_id': 1,
                'intent': 'taxi_support_chat_taxi',
                'phone': '+79001234567',
                'text': 'text_sms',
                'status': 'new',
                'created_at': datetime.datetime(2018, 7, 18, 11, 20),
            },
        ),
        (
            bson.ObjectId('5a433ca8779fb3302cc784be'),
            'message_81',
            {
                'group_id': 0,
                'task_id': 1,
                'intent': 'taxi_support_chat_taxi',
                'phone': '+79001234567',
                'text': 'text_sms',
                'status': 'new',
                'created_at': datetime.datetime(2018, 7, 18, 11, 20),
            },
        ),
        (
            bson.ObjectId('5a433ca8779fb3302cc784b1'),
            'message_sms_0',
            {
                'group_id': 0,
                'task_id': 1,
                'intent': 'taxi_support_chat_taxi',
                'phone': '+79001234568',
                'text': 'text_sms_0',
                'status': 'new',
                'created_at': datetime.datetime(2018, 7, 18, 11, 20),
            },
        ),
        (
            bson.ObjectId('5a433ca8779fb3302cc784b2'),
            'message_sms_1',
            {
                'group_id': 0,
                'task_id': 1,
                'intent': 'taxi_support_chat_uber',
                'phone': '+79001234569',
                'text': 'text_sms_1',
                'status': 'new',
                'created_at': datetime.datetime(2018, 7, 18, 11, 20),
            },
        ),
        (
            bson.ObjectId('5a433ca8779fb3302cc784b3'),
            'message_sms_2',
            {
                'group_id': 0,
                'task_id': 1,
                'intent': 'taxi_support_chat_yango',
                'phone': '+79001234566',
                'text': 'text_sms_2',
                'status': 'new',
                'created_at': datetime.datetime(2018, 7, 18, 11, 20),
            },
        ),
        (
            bson.ObjectId('539eb65be7e5b1f53980dfa8'),
            'message_88',
            {
                'created_at': datetime.datetime(2018, 7, 18, 11, 20),
                'group_id': 0,
                'intent': 'taxi_support_chat_uber',
                'phone': '+79001234566',
                'status': 'new',
                'task_id': 1,
                'text': 'text_sms_2',
            },
        ),
        (
            bson.ObjectId('7b31b49ed5344045a0a76a6b'),
            'message_89',
            {
                'created_at': datetime.datetime(2018, 7, 18, 11, 20),
                'group_id': 0,
                'intent': 'taxi_support_chat_taxi',
                'phone': '+88005553535',
                'status': 'new',
                'task_id': 1,
                'text': 'Держи промокод за косяки',
            },
        ),
    ],
)
@pytest.mark.config(
    USER_CHAT_PLATFORM_BY_APPLICATION={
        'iphone': 'yandex',
        'android': 'yandex',
        'uber_android': 'uber',
        'uber_iphone': 'uber',
        'yango_android': 'yango',
        'yango_iphone': 'yango',
    },
    SUPPORT_CHAT_USE_PLATFORM_TO_SEND_NOTIFICATIONS=True,
)
@pytest.mark.now('2018-07-18T11:20:00')
async def test_task(
        stq3_context: stq_context.Context,
        chat_id,
        message_id,
        sms_task,
        stq,
        mock_personal,
):
    @mock_personal('/v1/phones/retrieve')
    def handler(request):
        return {'id': 'user_phone_pd_id', 'value': '+88005553535'}

    await stq_task.sms_notify_task(
        stq3_context, chat_id=chat_id, message_id=message_id,
    )

    assert await stq3_context.mongo.sms_queue.count() == 1
    db_task = await stq3_context.mongo.sms_queue.find_one()
    db_task.pop('_id')
    assert db_task == sms_task


@pytest.mark.parametrize(
    'chat_id, message_id',
    [
        (bson.ObjectId('5a433ca8779fb3302cc784bd'), 'message_80'),
        (bson.ObjectId('5a433ca8779fb3302cc784bc'), 'message_79'),
        (bson.ObjectId('5a433ca8779fb3302cc783bf'), 'message_100'),
    ],
)
@pytest.mark.config(
    USER_CHAT_PLATFORM_BY_APPLICATION={
        'iphone': 'yandex',
        'android': 'yandex',
        'uber_android': 'uber',
        'uber_iphone': 'uber',
        'yango_android': 'yango',
        'yango_iphone': 'yango',
    },
)
@pytest.mark.now('2018-07-18T11:20:00')
async def test_bad_number(
        stq3_context: stq_context.Context, chat_id, message_id,
):

    await stq_task.sms_notify_task(stq3_context, chat_id, message_id)

    assert await stq3_context.mongo.sms_queue.count() == 0
