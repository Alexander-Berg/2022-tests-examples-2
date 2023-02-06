import pytest


@pytest.mark.parametrize(
    'stq_task_id, stq_task_feedback, db_expected_feedback',
    [
        # new feedback - full
        ('1234', {'rating': 5, 'comment': 'ok'}, ('1234', 5, 'ok')),
        # new feedback - empty
        ('1234', {}, ('1234', None, None)),
        # new feedback - only rating
        ('1234', {'rating': 5}, ('1234', 5, None)),
        # new feedback - only comment
        ('1234', {'comment': 'ok'}, ('1234', None, 'ok')),
        # update feedback
        ('euid-1', {'rating': 5, 'comment': 'ok'}, ('euid-1', 5, 'ok')),
    ],
)
async def test_stq_add_feedback(
        taxi_eats_ordershistory,
        pgsql,
        stq_task_id,
        stq_task_feedback,
        db_expected_feedback,
):
    request_body = {
        'queue_name': 'eats_ordershistory_add_feedback',
        'task_id': stq_task_id,
        'args': [],
        'kwargs': {'feedback': stq_task_feedback},
    }
    response = await taxi_eats_ordershistory.post(
        'testsuite/stq', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {'failed': False}

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT * FROM eats_ordershistory.feedbacks WHERE order_id = %s;',
        (stq_task_id,),
    )
    feedbacks = list(cursor)
    assert len(feedbacks) == 1
    assert feedbacks[0] == db_expected_feedback
