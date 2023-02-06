import pytest


def load_feedbacks_table(pgsql):
    with pgsql['eats_feedback'].cursor() as cursor:
        cursor.execute(
            'SELECT id, comment, order_nr, comment_status '
            + 'FROM eats_feedback.order_feedbacks ORDER BY id ASC',
        )
        return list(list(row) for row in cursor)


def get_last_applied_table(pgsql):
    with pgsql['eats_feedback'].cursor() as cursor:
        cursor.execute(
            'SELECT last_table_number FROM moderation.retrieve_state',
        )
        return next(cursor)[0]


@pytest.mark.pgsql('eats_feedback', files=['feedbacks.sql'])
@pytest.mark.yt(
    schemas=['yt_comment_moderation_1.yaml'],
    static_table_data=['yt_comment_moderation_1.yaml'],
)
async def test_batch_1(
        load_json,
        taxi_eats_feedback,
        pgsql,
        yt_apply_force,
        taxi_eats_feedback_monitor,
):
    assert get_last_applied_table(pgsql) is None
    assert load_feedbacks_table(pgsql) == load_json('feedbacks_before.json')

    metrics_before = await taxi_eats_feedback_monitor.get_metrics(
        'feedback-moderation-retrieve',
    )
    statistics_before = metrics_before['feedback-moderation-retrieve']

    response = await taxi_eats_feedback.post(
        'service/cron', json={'task_name': 'feedback-moderation'},
    )

    assert response.status_code == 200
    metrics_after = await taxi_eats_feedback_monitor.get_metrics(
        'feedback-moderation-retrieve',
    )

    statistics_after = metrics_after['feedback-moderation-retrieve']
    assert (
        statistics_after['success-retrieve']
        - statistics_before['success-retrieve']
        == 1
    )

    assert get_last_applied_table(pgsql) == 1618994001000
    assert load_feedbacks_table(pgsql) == load_json('feedbacks_after_1.json')


@pytest.mark.pgsql('eats_feedback', files=['feedbacks.sql'])
@pytest.mark.yt(
    schemas=['yt_comment_moderation_2.yaml'],
    static_table_data=['yt_comment_moderation_2.yaml'],
)
async def test_batch_2(load_json, taxi_eats_feedback, pgsql, yt_apply_force):
    assert get_last_applied_table(pgsql) is None
    assert load_feedbacks_table(pgsql) == load_json('feedbacks_before.json')

    response = await taxi_eats_feedback.post(
        'service/cron', json={'task_name': 'feedback-moderation'},
    )
    assert response.status_code == 200

    assert get_last_applied_table(pgsql) == 1618994002000
    assert load_feedbacks_table(pgsql) == load_json('feedbacks_after_2.json')


@pytest.mark.pgsql('eats_feedback', files=['feedbacks.sql'])
@pytest.mark.yt(
    schemas=['yt_comment_moderation_1.yaml', 'yt_comment_moderation_2.yaml'],
    static_table_data=[
        'yt_comment_moderation_1.yaml',
        'yt_comment_moderation_2.yaml',
    ],
)
async def test_batches_1_and_2(
        load_json, taxi_eats_feedback, pgsql, yt_apply_force,
):
    assert get_last_applied_table(pgsql) is None
    assert load_feedbacks_table(pgsql) == load_json('feedbacks_before.json')

    response = await taxi_eats_feedback.post(
        'service/cron', json={'task_name': 'feedback-moderation'},
    )
    assert response.status_code == 200

    assert get_last_applied_table(pgsql) == 1618994002000
    assert load_feedbacks_table(pgsql) == load_json(
        'feedbacks_after_1_and_2.json',
    )


@pytest.mark.pgsql('eats_feedback', files=['feedbacks.sql'])
@pytest.mark.yt(
    schemas=['yt_comment_moderation_3.yaml'],
    static_table_data=['yt_comment_moderation_3.yaml'],
)
@pytest.mark.config(
    EATS_FEEDBACK_SEND_TO_RESTAPP_COMMUNICATIONS={
        'enabled': True,
        'size_chunk': 5,
        'event_type': 'feedback',
    },
)
async def test_send_feedbacks(
        load_json, taxi_eats_feedback, pgsql, yt_apply_force, stq,
):

    assert get_last_applied_table(pgsql) is None
    assert load_feedbacks_table(pgsql) == load_json('feedbacks_before.json')

    response = await taxi_eats_feedback.post(
        'service/cron', json={'task_name': 'feedback-moderation'},
    )
    assert response.status_code == 200

    assert get_last_applied_table(pgsql) == 1618994002000
    assert load_feedbacks_table(pgsql) == load_json(
        'feedbacks_after_1_and_2.json',
    )
    arg = await stq.eats_place_rating_new_feedback_time.wait_call()
    assert arg['kwargs']['feedbacks'] == [
        {
            'comment': 'Newer good comment',
            'feedback_created_at': '2021-02-12T14:11:16+00:00',
            'order_nr': 'ORDER_12',
            'place_id': 1,
            'rating': 3,
        },
        {
            'comment': 'Newest good comment',
            'feedback_created_at': '2021-02-12T14:11:16+00:00',
            'order_nr': 'ORDER_22',
            'place_id': 1,
            'rating': 3,
        },
    ]
