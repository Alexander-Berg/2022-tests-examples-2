import datetime

import pytest


def call_push(taxi_feedback, request):
    return taxi_feedback.post(
        '/1.0/wanted/push',
        request,
        headers={'YaTaxi-Api-Key': 'feedback_apikey'},
    )


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_push(taxi_feedback, db):
    request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'order_id',
        'reorder_id': 'reorder_id',
        'order_created': '2018-10-09T16:31:13+0000',
        'order_due': '2018-10-09T16:31:14+0000',
        'order_completed': '2018-10-09T16:31:15+0000',
        'park_id': 'park_id',
    }
    response = call_push(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    feedback_doc = db.feedbacks.find_one('order_id')
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
@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_push_too_late(taxi_feedback, db):
    request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'some_order_id',
        'order_created': '2018-10-09T16:31:13+0000',
        'order_due': '2018-10-09T16:31:14+0000',
        'order_completed': '2018-10-09T16:31:15+0000',
        'park_id': 'park_id',
    }
    response = call_push(taxi_feedback, request)
    assert response.status_code == 409
    data = response.json()
    assert data == {'error': {'text': 'Too late'}}


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_push_with_existing(taxi_feedback, db):
    request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'order_with_feedback',
        'order_created': '2018-10-09T16:31:13+0000',
        'order_due': '2018-10-09T16:31:14+0000',
        'order_completed': '2018-10-09T16:31:15+0000',
        'park_id': 'park_id',
    }
    feedback_doc = db.feedbacks.find_one('order_with_feedback')
    response = call_push(taxi_feedback, request)
    assert response.status_code == 409
    assert feedback_doc == db.feedbacks.find_one('order_with_feedback')


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_push_switched_to_card_no_feedback(taxi_feedback, db):
    request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'order_without_feedback',
        'order_created': '2018-10-09T16:31:13+0000',
        'order_due': '2018-10-09T16:31:14+0000',
        'order_completed': '2018-10-09T16:31:15+0000',
        'park_id': 'park_id',
        'switched_to_card': True,
    }
    response = call_push(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    feedback_doc = db.feedbacks.find_one('order_without_feedback')
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
@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_push_switched_to_card_iac_false(taxi_feedback, db):
    request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'order_with_feedback',
        'order_created': '2018-10-09T16:31:13+0000',
        'order_due': '2018-10-09T16:31:14+0000',
        'order_completed': '2018-10-09T16:31:15+0000',
        'park_id': 'park_id',
        'switched_to_card': True,
    }
    response = call_push(taxi_feedback, request)
    assert response.status_code == 200

    feedback_doc = db.feedbacks.find_one('order_with_feedback')
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
@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_push_switched_to_card_iac_true(taxi_feedback, db):
    request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'order_with_feedback_iac_true',
        'order_created': '2018-10-09T16:31:13+0000',
        'order_due': '2018-10-09T16:31:14+0000',
        'order_completed': '2018-10-09T16:31:15+0000',
        'park_id': 'park_id',
        'switched_to_card': True,
    }
    feedback_doc = db.feedbacks.find_one('order_with_feedback_iac_true')
    request['order_id'] = 'order_with_feedback_iac_true'
    response = call_push(taxi_feedback, request)
    assert response.status_code == 409
    assert (
        db.feedbacks.find_one('order_with_feedback_iac_true') == feedback_doc
    )
