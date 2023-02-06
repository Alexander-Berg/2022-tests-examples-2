import pytest


def load_feedback_answer_table(pgsql):
    with pgsql['eats_feedback'].cursor() as cursor:
        cursor.execute(
            'SELECT id, comment, comment_status '
            + 'FROM eats_feedback.feedback_answer ORDER BY id ASC',
        )
        return list(list(row) for row in cursor)


def get_last_applied_table(pgsql):
    with pgsql['eats_feedback'].cursor() as cursor:
        cursor.execute(
            'SELECT last_table_number FROM'
            ' moderation.feedback_answer_retrieve_state',
        )
        return next(cursor)[0]


@pytest.mark.pgsql('eats_feedback', files=['feedback_answer.sql'])
@pytest.mark.yt(
    schemas=['yt_feedback_answer_moderation_1.yaml'],
    static_table_data=['yt_feedback_answer_moderation_1.yaml'],
)
async def test_batch_1(
        load_json,
        taxi_eats_feedback,
        pgsql,
        yt_apply_force,
        taxi_eats_feedback_monitor,
        stq,
):
    assert get_last_applied_table(pgsql) is None
    assert load_feedback_answer_table(pgsql) == load_json(
        'feedback_answer_before.json',
    )

    metrics_before = await taxi_eats_feedback_monitor.get_metrics(
        'feedback-answer-moderation-retrieve',
    )
    statistics_before = metrics_before['feedback-answer-moderation-retrieve']

    response = await taxi_eats_feedback.post(
        'service/cron', json={'task_name': 'feedback-answer-moderation'},
    )

    assert response.status_code == 200
    metrics_after = await taxi_eats_feedback_monitor.get_metrics(
        'feedback-answer-moderation-retrieve',
    )

    statistics_after = metrics_after['feedback-answer-moderation-retrieve']
    assert (
        statistics_after['success-retrieve']
        - statistics_before['success-retrieve']
        == 1
    )

    assert get_last_applied_table(pgsql) == 1618994001000
    assert load_feedback_answer_table(pgsql) == load_json(
        'feedback_answer_after_1.json',
    )
    assert stq.eats_place_rating_feedback_answer.times_called == 2
    arg = stq.eats_place_rating_feedback_answer.next_call()
    assert arg['queue'] == 'eats_place_rating_feedback_answer'
    assert arg['args'] == []
    assert arg['kwargs']['answer'] == {
        'feedback_id': 12,
        'answer_id': 1200,
        'text': 'Newer good comment',
    }
    assert arg['kwargs']['place_id'] == 1
    assert arg['kwargs']['order_nr'] == 'ORDER_12'

    arg = stq.eats_place_rating_feedback_answer.next_call()
    assert arg['queue'] == 'eats_place_rating_feedback_answer'
    assert arg['args'] == []
    assert arg['kwargs']['answer'] == {'feedback_id': 11, 'answer_id': 1100}
    assert arg['kwargs']['place_id'] == 1
    assert arg['kwargs']['order_nr'] == 'ORDER_11'


@pytest.mark.pgsql('eats_feedback', files=['feedback_answer.sql'])
@pytest.mark.yt(
    schemas=['yt_feedback_answer_moderation_2.yaml'],
    static_table_data=['yt_feedback_answer_moderation_2.yaml'],
)
async def test_batch_2(
        load_json, taxi_eats_feedback, pgsql, yt_apply_force, stq,
):
    assert get_last_applied_table(pgsql) is None
    assert load_feedback_answer_table(pgsql) == load_json(
        'feedback_answer_before.json',
    )

    response = await taxi_eats_feedback.post(
        'service/cron', json={'task_name': 'feedback-answer-moderation'},
    )
    assert response.status_code == 200

    assert get_last_applied_table(pgsql) == 1618994002000
    assert load_feedback_answer_table(pgsql) == load_json(
        'feedback_answer_after_2.json',
    )
    assert stq.eats_place_rating_feedback_answer.times_called == 2
    arg = stq.eats_place_rating_feedback_answer.next_call()
    assert arg['queue'] == 'eats_place_rating_feedback_answer'
    assert arg['args'] == []
    assert arg['kwargs']['answer'] == {
        'feedback_id': 22,
        'answer_id': 2200,
        'text': 'Newest good comment',
    }
    assert arg['kwargs']['place_id'] == 1
    assert arg['kwargs']['order_nr'] == 'ORDER_22'

    arg = stq.eats_place_rating_feedback_answer.next_call()
    assert arg['queue'] == 'eats_place_rating_feedback_answer'
    assert arg['args'] == []
    assert arg['kwargs']['answer'] == {'feedback_id': 21, 'answer_id': 2100}
    assert arg['kwargs']['place_id'] == 1
    assert arg['kwargs']['order_nr'] == 'ORDER_21'


@pytest.mark.pgsql('eats_feedback', files=['feedback_answer.sql'])
@pytest.mark.yt(
    schemas=[
        'yt_feedback_answer_moderation_1.yaml',
        'yt_feedback_answer_moderation_2.yaml',
    ],
    static_table_data=[
        'yt_feedback_answer_moderation_1.yaml',
        'yt_feedback_answer_moderation_2.yaml',
    ],
)
async def test_batches_1_and_2(
        load_json, taxi_eats_feedback, pgsql, yt_apply_force, stq,
):
    assert get_last_applied_table(pgsql) is None
    assert load_feedback_answer_table(pgsql) == load_json(
        'feedback_answer_before.json',
    )

    response = await taxi_eats_feedback.post(
        'service/cron', json={'task_name': 'feedback-answer-moderation'},
    )
    assert response.status_code == 200

    assert get_last_applied_table(pgsql) == 1618994002000
    assert load_feedback_answer_table(pgsql) == load_json(
        'feedback_answer_after_1_and_2.json',
    )
    assert stq.eats_place_rating_feedback_answer.times_called == 4

    arg = stq.eats_place_rating_feedback_answer.next_call()
    assert arg['queue'] == 'eats_place_rating_feedback_answer'
    assert arg['args'] == []
    assert arg['kwargs']['answer'] == {
        'feedback_id': 12,
        'answer_id': 1200,
        'text': 'Newer good comment',
    }
    assert arg['kwargs']['place_id'] == 1
    assert arg['kwargs']['order_nr'] == 'ORDER_12'

    arg = stq.eats_place_rating_feedback_answer.next_call()
    assert arg['queue'] == 'eats_place_rating_feedback_answer'
    assert arg['args'] == []
    assert arg['kwargs']['answer'] == {'feedback_id': 11, 'answer_id': 1100}
    assert arg['kwargs']['place_id'] == 1
    assert arg['kwargs']['order_nr'] == 'ORDER_11'

    arg = stq.eats_place_rating_feedback_answer.next_call()
    assert arg['queue'] == 'eats_place_rating_feedback_answer'
    assert arg['args'] == []
    assert arg['kwargs']['answer'] == {
        'feedback_id': 22,
        'answer_id': 2200,
        'text': 'Newest good comment',
    }
    assert arg['kwargs']['place_id'] == 1
    assert arg['kwargs']['order_nr'] == 'ORDER_22'

    arg = stq.eats_place_rating_feedback_answer.next_call()
    assert arg['queue'] == 'eats_place_rating_feedback_answer'
    assert arg['args'] == []
    assert arg['kwargs']['answer'] == {'feedback_id': 21, 'answer_id': 2100}
    assert arg['kwargs']['place_id'] == 1
    assert arg['kwargs']['order_nr'] == 'ORDER_21'
