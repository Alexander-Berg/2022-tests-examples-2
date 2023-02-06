import datetime

import pytest


def construct_default_task_args(
        order_id='order_id', switched_to_card=False, has_reorder_id=True,
):
    user_id = 'user_id'
    phone_id = '123456789012345678901234'
    order_created = '2018-10-09T16:31:13+0000'
    order_due = '2018-10-09T16:31:14+0000'
    order_completed = '2018-10-09T16:31:15+0000'
    park_id = 'park_id'
    args = [
        user_id,
        phone_id,
        order_id,
        order_created,
        order_due,
        order_completed,
        park_id,
    ]

    if switched_to_card:
        args.append(switched_to_card)
    else:
        args.append(None)

    if has_reorder_id:
        reorder_id = 'reorder_id'
        args.append(reorder_id)
    return args


async def call_push_wanted_task(stq_runner, args):
    task_id = '123'
    return await stq_runner.passenger_feedback_push_wanted.call(
        task_id=task_id, args=args,
    )


@pytest.mark.now('2018-08-10T21:01:30+0300')
async def test_push(stq_runner, mongodb):
    args = construct_default_task_args()
    await call_push_wanted_task(stq_runner, args)

    feedback_doc = mongodb.feedbacks_mdb.find_one('order_id')
    feedback_doc.pop('updated')
    assert feedback_doc == {
        '_id': 'order_id',
        'reorder_id': 'reorder_id',
        'user_id': 'user_id',
        'user_phone_id': '123456789012345678901234',
        'created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'order_created': datetime.datetime(2018, 10, 9, 16, 31, 13),
        'order_due': datetime.datetime(2018, 10, 9, 16, 31, 14),
        'order_completed': datetime.datetime(2018, 10, 9, 16, 31, 15),
        'park_id': 'park_id',
        'wanted': True,
    }


@pytest.mark.now('2018-10-15T21:01:30+0300')
async def test_push_too_late(stq_runner, mongodb):
    args = construct_default_task_args()
    await call_push_wanted_task(stq_runner, args)

    feedback_doc = mongodb.feedbacks_mdb.find_one('order_id')
    assert feedback_doc is None


@pytest.mark.now('2018-08-10T21:01:30+0300')
async def test_push_with_existing(stq_runner, mongodb):
    args = construct_default_task_args('order_with_feedback')

    feedback_doc = mongodb.feedbacks_mdb.find_one('order_with_feedback')
    await call_push_wanted_task(stq_runner, args)
    assert feedback_doc == mongodb.feedbacks_mdb.find_one(
        'order_with_feedback',
    )


@pytest.mark.now('2018-08-10T21:01:30+0300')
async def test_push_switched_to_card_no_feedback(stq_runner, mongodb):
    args = construct_default_task_args(
        'order_without_feedback', switched_to_card=True, has_reorder_id=False,
    )
    await call_push_wanted_task(stq_runner, args)

    feedback_doc = mongodb.feedbacks_mdb.find_one('order_without_feedback')
    feedback_doc.pop('updated')
    assert feedback_doc == {
        '_id': 'order_without_feedback',
        'user_id': 'user_id',
        'user_phone_id': '123456789012345678901234',
        'created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'order_created': datetime.datetime(2018, 10, 9, 16, 31, 13),
        'order_due': datetime.datetime(2018, 10, 9, 16, 31, 14),
        'order_completed': datetime.datetime(2018, 10, 9, 16, 31, 15),
        'park_id': 'park_id',
        'wanted': True,
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
async def test_push_switched_to_card_is_after_complete_false(
        stq_runner, mongodb,
):
    args = construct_default_task_args(
        'order_with_feedback', switched_to_card=True, has_reorder_id=False,
    )
    await call_push_wanted_task(stq_runner, args)

    feedback_doc = mongodb.feedbacks_mdb.find_one('order_with_feedback')
    feedback_doc.pop('updated')
    assert feedback_doc == {
        '_id': 'order_with_feedback',
        'user_id': 'user_id',
        'user_phone_id': '123456789012345678901234',
        'created': datetime.datetime(2017, 1, 1, 0, 0),
        'order_created': datetime.datetime(2018, 10, 9, 16, 31, 13),
        'order_due': datetime.datetime(2018, 10, 9, 16, 31, 14),
        'order_completed': datetime.datetime(2018, 10, 9, 16, 31, 15),
        'park_id': 'park_id',
        'wanted': True,
        'data': {
            'app_comment': False,
            'call_me': False,
            'is_after_complete': False,
            'choices': [
                {'type': 'cancelled_reason', 'value': 'driverrequest'},
            ],
        },
        'data_created': datetime.datetime(2017, 1, 1, 0, 0),
        'data_updated': datetime.datetime(2017, 1, 1, 0, 0),
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
async def test_push_switched_to_card_is_after_complete_true(
        stq_runner, mongodb,
):
    args = construct_default_task_args(
        'order_with_feedback_is_after_complete_true', switched_to_card=True,
    )
    feedback_doc = mongodb.feedbacks_mdb.find_one(
        'order_with_feedback_is_after_complete_true',
    )

    await call_push_wanted_task(stq_runner, args)
    assert (
        mongodb.feedbacks_mdb.find_one(
            'order_with_feedback_is_after_complete_true',
        )
        == feedback_doc
    )
