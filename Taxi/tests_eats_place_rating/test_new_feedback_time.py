import datetime

import pytest


@pytest.mark.now('2022-06-07T00:00:00+0000')
@pytest.mark.pgsql('eats_place_rating', files=('pg_new_feedbacks_views.sql',))
async def test_new_feedback_time_stq(stq_runner, mockserver, pgsql):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal'
        '/communications/v1/send-event-bulk',
    )
    def mock_sticker_send(request):
        assert request.json == {
            'recipients_with_data': [
                {
                    'data': {
                        'rating': 1,
                        'place_id': 1,
                        'feedback_created_at': '2021-03-06T00:00:00+00:00',
                        'comment': 'comment1',
                        'order_nr': 'order_nr1',
                        'predefined_comments': '1,2',
                    },
                    'recipients': {'place_ids': [1]},
                    'event_mode': 'asap',
                },
                {
                    'data': {
                        'rating': 1,
                        'place_id': 1,
                        'feedback_created_at': '2021-03-05T00:00:00+00:00',
                        'comment': 'comment1',
                        'order_nr': 'order_nr1',
                        'predefined_comments': '1,2',
                    },
                    'recipients': {'place_ids': [1]},
                    'event_mode': 'asap',
                },
                {
                    'data': {
                        'rating': 2,
                        'place_id': 2,
                        'feedback_created_at': '2021-03-02T00:00:00+00:00',
                        'comment': 'comment2',
                        'order_nr': 'order_nr2',
                        'predefined_comments': '1,2',
                    },
                    'recipients': {'place_ids': [2]},
                    'event_mode': 'asap',
                },
                {
                    'data': {
                        'rating': 3,
                        'place_id': 3,
                        'feedback_created_at': '2021-03-02T00:00:00+00:00',
                        'comment': 'comment3',
                        'order_nr': 'order_nr3',
                        'predefined_comments': '1,2',
                    },
                    'recipients': {'place_ids': [3]},
                    'event_mode': 'asap',
                },
            ],
        }
        return mockserver.make_response(status=204)

    await stq_runner.eats_place_rating_new_feedback_time.call(
        task_id='fake_task',
        kwargs={
            'feedbacks': [
                {
                    'rating': 1,
                    'place_id': 1,
                    'feedback_created_at': '2021-03-06T00:00:00+00:00',
                    'comment': 'comment1',
                    'order_nr': 'order_nr1',
                    'predefined_comments': '1,2',
                },
                {
                    'rating': 1,
                    'place_id': 1,
                    'feedback_created_at': '2021-03-05T00:00:00+00:00',
                    'comment': 'comment1',
                    'order_nr': 'order_nr1',
                    'predefined_comments': '1,2',
                },
                {
                    'rating': 2,
                    'place_id': 2,
                    'feedback_created_at': '2021-03-02T00:00:00+00:00',
                    'comment': 'comment2',
                    'order_nr': 'order_nr2',
                    'predefined_comments': '1,2',
                },
                {
                    'rating': 3,
                    'place_id': 3,
                    'feedback_created_at': '2021-03-02T00:00:00+00:00',
                    'comment': 'comment3',
                    'order_nr': 'order_nr3',
                    'predefined_comments': '1,2',
                },
            ],
        },
    )

    assert mock_sticker_send.times_called == 1

    expected_result = [
        (1, datetime.date(2022, 6, 7)),
        (2, datetime.date(2022, 6, 7)),
        (3, datetime.date(2022, 6, 7)),
    ]
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT place_id, last_feedback_time::DATE '
        'FROM eats_place_rating.new_feedbacks_views '
        'ORDER BY place_id;',
    )
    result = cursor.fetchall()
    assert result == expected_result
