import datetime
import json

import bson
import pytest

from taxi_tests.utils import ordered_object


def call_retrieve(taxi_feedback, request):
    return taxi_feedback.post(
        '/1.0/retrieve',
        request,
        headers={'YaTaxi-Api-Key': 'feedback_apikey'},
    )


@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_retrieve(taxi_feedback):
    request = {'order_id': 'order_id', 'from_archive': False}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    expected = {
        'app_comment': True,
        'call_me': True,
        'is_after_complete': True,
        'choices': [
            {'type': 'low_rating_reason', 'value': 'rudedriver'},
            {'type': 'badge', 'value': 'pleasantmusic'},
        ],
        'msg': 'message',
        'rating': 3,
    }
    ordered_object.assert_eq(data, expected, ['choices'])


@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_retrieve_by_reorder_id(taxi_feedback):
    request = {'order_id': 'reorder_id', 'from_archive': False}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    expected = {
        'app_comment': True,
        'call_me': True,
        'is_after_complete': True,
        'choices': [
            {'type': 'low_rating_reason', 'value': 'rudedriver'},
            {'type': 'badge', 'value': 'pleasantmusic'},
        ],
        'msg': 'message',
        'rating': 1,
    }
    ordered_object.assert_eq(data, expected, ['choices'])


@pytest.mark.config(
    FEEDBACK_RETRIEVE_FROM_DBFEEDBACK=True,
    PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new',
)
def test_retrieve_from_feedbacks(taxi_feedback):
    request = {'order_id': 'order_id', 'from_archive': True}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    expected = {
        'app_comment': False,
        'call_me': False,
        'is_after_complete': True,
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'msg': 'good',
        'rating': 4,
    }
    ordered_object.assert_eq(data, expected, ['choices'])


@pytest.mark.config(
    FEEDBACK_RETRIEVE_FROM_DBFEEDBACK=True,
    PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new',
)
def test_retrieve_by_reorder_from_feedbacks(taxi_feedback):
    request = {'order_id': 'reorder_id', 'from_archive': True}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    expected = {
        'app_comment': False,
        'call_me': False,
        'is_after_complete': True,
        'choices': [],
        'msg': 'excellent',
        'rating': 5,
    }
    ordered_object.assert_eq(data, expected, ['choices'])


@pytest.mark.config(
    FEEDBACK_RETRIEVE_FROM_DBFEEDBACK=True,
    FEEDBACK_ARCHIVATION_DELAY=60,
    PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new',
)
@pytest.mark.now('2018-08-10T21:01:30+0300')
def test_retrieve_not_search_archive_with_due(taxi_feedback, mockserver):
    @mockserver.json_handler('/order-archive/v1/order_proc/bulk-retrieve')
    def mock_archive_order_proc(request):
        return mockserver.make_response(status=404)

    request = {
        'order_id': 'unexistent_order_id',
        'from_archive': True,
        'order_due': '2018-08-10T21:00:31+0300',
    }
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 404
    assert mock_archive_order_proc.times_called == 0


@pytest.mark.config(
    FEEDBACK_RETRIEVE_FROM_DBFEEDBACK=True,
    PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new',
)
def test_retrieve_not_search_archive_dbfeedback(taxi_feedback, mockserver):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def mock_archive_order_proc(request):
        return mockserver.make_response(status=404)

    request = {'order_id': 'no_feedback', 'from_archive': True}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 404
    assert mock_archive_order_proc.times_called == 0


@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_retrieve_not_search_archive(taxi_feedback, mockserver):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def mock_archive_order_proc(request):
        return mockserver.make_response(status=404)

    request = {'order_id': 'no_feedback', 'from_archive': True}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 404
    assert mock_archive_order_proc.times_called == 0


@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_retrieve_not_found(taxi_feedback):
    request = {'order_id': 'unexistent_order_id', 'from_archive': False}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 404


@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_retrieve_archive(taxi_feedback, mockserver):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def mock_archive_order_proc(request):
        data = json.loads(request.get_data())
        assert data == {'indexes': ['reorder'], 'id': 'archived_order_id'}
        doc = {
            '_id': 'archived_order_id',
            'order': {
                'feedback': {
                    'app_comment': False,
                    'rating': 3,
                    'c': True,
                    'iac': True,
                    'ct': datetime.datetime(2018, 8, 10, 18, 1, 30),
                    'msg': 'message',
                    'choices': {
                        'low_rating_reason': ['rudedriver'],
                        'badge': ['pleasantmusic'],
                    },
                },
            },
        }
        response = {'doc': doc}
        return mockserver.make_response(bson.BSON.encode(response))

    request = {'order_id': 'archived_order_id', 'from_archive': True}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    expected = {
        'app_comment': False,
        'call_me': True,
        'is_after_complete': True,
        'choices': [
            {'type': 'badge', 'value': 'pleasantmusic'},
            {'type': 'low_rating_reason', 'value': 'rudedriver'},
        ],
        'msg': 'message',
        'rating': 3,
    }
    ordered_object.assert_eq(data, expected, ['choices'])
    assert mock_archive_order_proc.times_called == 1


@pytest.mark.config(
    FEEDBACK_RETRIEVE_FROM_DBFEEDBACK=True,
    PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new',
)
def test_retrieve_archive_dbfeedback(taxi_feedback, mockserver):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def mock_archive_order_proc(request):
        data = json.loads(request.get_data())
        assert data == {'indexes': ['reorder'], 'id': 'archived_order_id'}
        doc = {
            '_id': 'archived_order_id',
            'order': {
                'feedback': {
                    'app_comment': False,
                    'rating': 3,
                    'c': True,
                    'iac': True,
                    'ct': datetime.datetime(2018, 8, 10, 18, 1, 30),
                    'msg': 'message',
                    'choices': {
                        'low_rating_reason': ['rudedriver'],
                        'badge': ['pleasantmusic'],
                    },
                },
            },
        }
        response = {'doc': doc}
        return mockserver.make_response(bson.BSON.encode(response))

    request = {'order_id': 'archived_order_id', 'from_archive': True}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    expected = {
        'app_comment': False,
        'call_me': True,
        'is_after_complete': True,
        'choices': [
            {'type': 'badge', 'value': 'pleasantmusic'},
            {'type': 'low_rating_reason', 'value': 'rudedriver'},
        ],
        'msg': 'message',
        'rating': 3,
    }
    ordered_object.assert_eq(data, expected, ['choices'])
    assert mock_archive_order_proc.times_called == 1


@pytest.mark.config(PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new')
def test_archive_not_found(taxi_feedback, mockserver):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def mock_archive_order_proc(request):
        data = json.loads(request.get_data())
        assert data == {'indexes': ['reorder'], 'id': 'archived_order_id'}
        return mockserver.make_response(status=404)

    request = {'order_id': 'archived_order_id', 'from_archive': True}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 404


@pytest.mark.config(
    FEEDBACK_RETRIEVE_ARCHIVE_FROM_PROC=False,
    PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new',
)
def test_retrieve_from_archive(taxi_feedback, yt_client):
    query = (
        '* FROM '
        '[//home/taxi/unstable/replica/mongo/struct/feedbacks] '
        'WHERE id = "archived_order_id"'
    )

    yt_client.add_select_rows_response(
        query, 'yt-select-feedback-archive-response.json',
    )
    request = {'order_id': 'archived_order_id', 'from_archive': True}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    assert response.json() == {
        'app_comment': False,
        'call_me': False,
        'is_after_complete': False,
        'choices': [
            {'type': 'rating_reason', 'value': 'clean'},
            {'type': 'rating_reason', 'value': 'comfort_ride'},
            {'type': 'rating_reason', 'value': 'polite'},
        ],
        'msg': 'message',
        'rating': 3,
    }


@pytest.mark.config(
    FEEDBACK_RETRIEVE_ARCHIVE_FROM_PROC=False,
    PASSENGER_FEEDBACK_DB_MODE='write_old_new_read_new',
)
def test_retrieve_from_archive_not_found(taxi_feedback, yt_client):
    query = (
        '* FROM '
        '[//home/taxi/unstable/replica/mongo/struct/feedbacks] '
        'WHERE id = "archived_order_id"'
    )

    yt_client.add_select_rows_response(
        query, 'yt-select-feedback-archive-response-empty.json',
    )
    request = {'order_id': 'archived_order_id', 'from_archive': True}
    response = call_retrieve(taxi_feedback, request)
    assert response.status_code == 404
