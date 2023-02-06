import datetime
import itertools
import json

import bson
import pytest

from taxi_tests.utils import ordered_object


def call_bulk_retrieve(taxi_feedback, request):
    return taxi_feedback.post(
        '/1.0/retrieve/bulk',
        request,
        headers={'YaTaxi-Api-Key': 'feedback_apikey'},
    )


def test_bulk_retrieve(taxi_feedback):
    request = {
        'order_ids': ['order_id', 'order_id_2', 'nonexistent_order_id'],
        'from_archive': False,
    }
    response = call_bulk_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    expected = [
        {
            'order_id': 'order_id',
            'feedback': {
                'rating': 3,
                'call_me': True,
                'choices': [
                    {'type': 'low_rating_reason', 'value': 'rudedriver'},
                    {'type': 'badge', 'value': 'pleasantmusic'},
                ],
                'msg': 'message',
                'is_after_complete': True,
                'app_comment': True,
            },
        },
        {
            'order_id': 'order_id_2',
            'feedback': {
                'rating': 5,
                'call_me': True,
                'choices': [],
                'msg': 'message',
                'is_after_complete': True,
                'app_comment': True,
            },
        },
    ]
    ordered_object.assert_eq(data['items'], expected, ['', 'feedback.choices'])


@pytest.mark.config(FEEDBACK_RETRIEVE_FROM_DBFEEDBACK=True)
def test_bulk_retrieve_from_feedbacks(taxi_feedback):
    request = {
        'order_ids': ['order_id', 'order_id_2', 'nonexistent_order_id'],
        'from_archive': False,
    }
    response = call_bulk_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    expected = [
        {
            'order_id': 'order_id',
            'feedback': {
                'rating': 4,
                'call_me': True,
                'choices': [
                    {'type': 'badge', 'value': 'pleasantmusic'},
                    {'type': 'low_rating_reason', 'value': 'rudedriver'},
                ],
                'msg': 'massage',
                'is_after_complete': True,
                'app_comment': False,
            },
        },
        {
            'order_id': 'order_id_2',
            'feedback': {
                'rating': 4,
                'call_me': True,
                'choices': [],
                'msg': 'message',
                'is_after_complete': True,
                'app_comment': True,
            },
        },
    ]
    ordered_object.assert_eq(data['items'], expected, ['', 'feedback.choices'])


def test_empty_request(taxi_feedback):
    response = call_bulk_retrieve(
        taxi_feedback, request={'order_ids': [], 'from_archive': False},
    )
    assert response.status_code == 400


def test_retrieve_archive(taxi_feedback, mockserver):
    @mockserver.json_handler('/order-archive/v1/order_proc/bulk-retrieve')
    def mock_archive_order_proc(request):
        data = json.loads(request.get_data())
        assert data == {'ids': ['archived_order_id']}
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
        response = {'items': [{'doc': doc}]}
        return mockserver.make_response(bson.BSON.encode(response))

    request = {'order_ids': ['archived_order_id'], 'from_archive': True}
    response = call_bulk_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    expected = {
        'items': [
            {
                'order_id': 'archived_order_id',
                'feedback': {
                    'rating': 3,
                    'call_me': True,
                    'choices': [
                        {'type': 'badge', 'value': 'pleasantmusic'},
                        {'type': 'low_rating_reason', 'value': 'rudedriver'},
                    ],
                    'msg': 'message',
                    'is_after_complete': True,
                    'app_comment': False,
                },
            },
        ],
    }
    ordered_object.assert_eq(data, expected, ['items.feedback.choices'])

    assert mock_archive_order_proc.times_called == 1


def test_archive_not_found(taxi_feedback, mockserver):
    @mockserver.json_handler('/order-archive/v1/order_proc/bulk-retrieve')
    def mock_archive_order_proc(request):
        data = json.loads(request.get_data())
        assert data == {'ids': ['archived_order_id']}
        response = {'items': []}
        return mockserver.make_response(bson.BSON.encode(response))

    request = {'order_ids': ['archived_order_id'], 'from_archive': True}
    response = call_bulk_retrieve(taxi_feedback, request)
    assert response.status_code == 200
    assert response.json() == {'items': []}


@pytest.mark.config(FEEDBACK_RETRIEVE_ARCHIVE_FROM_PROC=False)
def test_bulk_retrieve_from_archive(taxi_feedback, yt_client):
    ids = ['archived_order_id', 'another_archived_order_id', 'nonexistent_id']

    # Motivation: storing order ids as a hashset inside (unknown order)
    for permutation in itertools.permutations(ids):
        query = (
            '* FROM '
            '[//home/taxi/unstable/replica/mongo/struct/feedbacks] '
            'WHERE id IN ({0})'
        ).format(', '.join('"' + id + '"' for id in permutation))

        yt_client.add_select_rows_response(
            query, 'yt-select-feedback-archive-response-in.json',
        )

    request = {'order_ids': ids, 'from_archive': True}
    response = call_bulk_retrieve(taxi_feedback, request)

    def key_getter(d):
        return d['order_id']

    expected = {
        'items': sorted(
            [
                {
                    'order_id': 'archived_order_id',
                    'feedback': {
                        'rating': 3,
                        'call_me': False,
                        'choices': [
                            {'type': 'rating_reason', 'value': 'clean'},
                            {'type': 'rating_reason', 'value': 'comfort_ride'},
                            {'type': 'rating_reason', 'value': 'polite'},
                        ],
                        'msg': 'message',
                        'is_after_complete': False,
                        'app_comment': False,
                    },
                },
                {
                    'order_id': 'another_archived_order_id',
                    'feedback': {
                        'rating': 3,
                        'call_me': False,
                        'choices': [
                            {'type': 'rating_reason', 'value': 'clean'},
                            {'type': 'rating_reason', 'value': 'comfort_ride'},
                            {'type': 'rating_reason', 'value': 'polite'},
                        ],
                        'msg': 'message',
                        'is_after_complete': False,
                        'app_comment': False,
                    },
                },
            ],
            key=key_getter,
        ),
    }

    actual = response.json()

    assert response.status_code == 200
    assert set(actual.keys()) == {'items'}
    assert {'items': sorted(actual['items'], key=key_getter)} == expected
