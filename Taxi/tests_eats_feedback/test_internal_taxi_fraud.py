import pytest


def load_feedbacks_table(pgsql):
    with pgsql['eats_feedback'].cursor() as cursor:
        cursor.execute(
            'SELECT id, comment, order_nr, fraud_skip '
            + 'FROM eats_feedback.order_feedbacks ORDER BY id ASC',
        )
        return list(list(row) for row in cursor)


def get_last_row_ts(pgsql):
    with pgsql['eats_feedback'].cursor() as cursor:
        cursor.execute('SELECT last_row_ts FROM taxi_fraud.retrieve_state')
        return next(cursor)[0]


def set_last_row_ts(pgsql, row_ts):
    with pgsql['eats_feedback'].cursor() as cursor:
        cursor.execute(
            'UPDATE taxi_fraud.retrieve_state SET last_row_ts = %s', [row_ts],
        )
        assert cursor.rowcount == 1


@pytest.mark.pgsql('eats_feedback', files=['feedbacks.sql'])
@pytest.mark.yt(dyn_table_data=['yt_bad_orders.yaml'])
async def test_batch_1_and_2(
        load_json, taxi_eats_feedback, pgsql, yt_apply_force,
):
    assert get_last_row_ts(pgsql) is None
    assert load_feedbacks_table(pgsql) == load_json('feedbacks_before.json')

    response = await taxi_eats_feedback.post(
        'service/cron', json={'task_name': 'taxi_fraud'},
    )
    assert response.status_code == 200

    assert get_last_row_ts(pgsql) == 1619000200
    assert load_feedbacks_table(pgsql) == load_json(
        'feedbacks_after_1_and_2.json',
    )


@pytest.mark.pgsql('eats_feedback', files=['feedbacks.sql'])
@pytest.mark.yt(dyn_table_data=['yt_bad_orders.yaml'])
async def test_batch_2(load_json, taxi_eats_feedback, pgsql, yt_apply_force):
    assert get_last_row_ts(pgsql) is None
    assert load_feedbacks_table(pgsql) == load_json('feedbacks_before.json')

    set_last_row_ts(pgsql, 1619000100)

    response = await taxi_eats_feedback.post(
        'service/cron', json={'task_name': 'taxi_fraud'},
    )
    assert response.status_code == 200

    assert get_last_row_ts(pgsql) == 1619000200
    assert load_feedbacks_table(pgsql) == load_json('feedbacks_after_2.json')
