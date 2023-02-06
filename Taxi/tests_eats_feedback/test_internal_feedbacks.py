import pytest


def get_order(order_nr, pgsql):
    cursor = pgsql['eats_feedback'].cursor()
    cursor.execute(
        'SELECT order_nr, is_deleted '
        'FROM eats_feedback.excluded_orders '
        f'WHERE order_nr=\'{order_nr}\';',
    )
    return cursor.fetchone()


@pytest.mark.parametrize(
    ['params', 'result_json'],
    [
        [
            {'place_id': 1, 'actual': True, 'user_locale': 'ru'},
            'feedbacks_1.json',
        ],
        [
            {
                'place_id': 1,
                'actual': True,
                'user_locale': 'ru',
                'hide_unmoderated': True,
            },
            'feedbacks_1_no_raw.json',
        ],
        [
            {'place_id': 1, 'ratings': '1,2,3,4', 'user_locale': 'ru'},
            'rating_4.json',
        ],
        [
            {'place_id': 1, 'ratings': '4', 'user_locale': 'ru'},
            'rating_4.json',
        ],
        [
            {
                'place_id': 1,
                'predefined_comment_ids': '2, 15, 17',
                'user_locale': 'ru',
            },
            'rating_4.json',
        ],
        [
            {
                'place_id': 1,
                'actual': True,
                'user_locale': 'ru',
                'from': '2021-05-09T11:11:11.1111+00:20',
            },
            'feedbacks_0.json',
        ],
        [
            {
                'place_id': 1,
                'actual': True,
                'user_locale': 'ru',
                'to': '2021-02-09T11:11:11.1111+00:20',
            },
            'feedbacks_0.json',
        ],
        [
            {
                'place_id': 4,
                'actual': True,
                'user_locale': 'ru',
                'from': '2021-05-01T11:11:11.1111+00:20',
            },
            'feedbacks_4.json',
        ],
        [
            {
                'place_id': 4,
                'actual': True,
                'user_locale': 'ru',
                'to': '2021-05-03T11:11:11.1111+00:20',
            },
            'feedbacks_4.json',
        ],
        [
            {
                'place_id': 4,
                'actual': True,
                'user_locale': 'ru',
                'from': '2021-05-01T08:00:00.000+00:00',
                'to': '2021-05-01T20:00:00.000+00:00',
            },
            'feedbacks_5.json',
        ],
    ],
    ids=[
        'place_id=1',
        'place_id=1 and hide raw',
        'ratings=1,2,3,4',
        'ratings=4',
        'predefined_comment_ids=2, 15, 17',
        'with_from_filter_0_feedbacks',
        'with_to_filter_0_feedbacks',
        'place_id=4_with_from_filter_2_feedbacks',
        'place_id=4_with_to_filter_2_feedbacks',
        'place_id=4_with_from_to_filter_1_feedback',
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=[
        'predefined_comments.sql',
        'feedbacks.sql',
        'orders.sql',
        'feedbacks_answer.sql',
    ],
)
async def test_get_feedbacks(
        load_json, taxi_eats_feedback, params, result_json,
):
    response = await taxi_eats_feedback.get(
        '/internal/eats-feedback/v1/feedbacks', params=params,
    )
    assert response.status_code == 200
    assert response.json() == load_json(result_json)


@pytest.mark.parametrize(
    ['params', 'result_json'],
    [
        [{'place_id': 1, 'user_locale': 'ru'}, 'feedbacks_6.json'],
        [
            {
                'place_id': 1,
                'user_locale': 'ru',
                'cursor': '2021-02-10T11:11:16.000000Z',
            },
            'feedbacks_7.json',
        ],
    ],
    ids=['no cursor', 'cursor'],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=[
        'predefined_comments.sql',
        'feedbacks_for_cursor.sql',
        'orders.sql',
        'feedbacks_answer.sql',
    ],
)
@pytest.mark.config(
    EATS_FEEDBACK_CONFIGURATION={
        'rating_actual_size': 200,
        'internal_feedbacks_chunk_size': 3,
    },
)
async def test_get_feedbacks_with_cursor(
        load_json, taxi_eats_feedback, params, result_json,
):
    response = await taxi_eats_feedback.get(
        '/internal/eats-feedback/v1/feedbacks', params=params,
    )
    assert response.status_code == 200
    assert response.json() == load_json(result_json)


@pytest.mark.parametrize(
    [
        'order_nr',
        'undo',
        'place_id',
        'exclude_status',
        'status',
        'result_json',
    ],
    [
        ['ORDER_2', None, 1, 204, 200, 'rating_4.json'],
        ['ORDER_2', True, 1, 204, 200, 'feedbacks_1.json'],
        ['ORDER_3', False, 3, 204, 200, 'feedbacks_0.json'],
        ['ORDER_3', True, 3, 204, 200, 'feedbacks_3.json'],
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=[
        'predefined_comments.sql',
        'feedbacks.sql',
        'orders.sql',
        'feedbacks_answer.sql',
    ],
)
async def test_exclude_feedbacks(
        load_json,
        taxi_eats_feedback,
        order_nr,
        undo,
        place_id,
        exclude_status,
        status,
        result_json,
        pgsql,
):
    response = await taxi_eats_feedback.post(
        '/internal/eats-feedback/v1/exclude',
        json={'order_nr': order_nr, 'undo': undo},
    )
    assert response.status_code == exclude_status
    response = await taxi_eats_feedback.get(
        '/internal/eats-feedback/v1/feedbacks',
        params={'place_id': place_id, 'user_locale': 'ru'},
    )
    assert response.status_code == status
    assert response.json() == load_json(result_json)

    cursor_res = get_order(order_nr, pgsql)
    if undo:
        assert not cursor_res
    else:
        assert cursor_res == (order_nr, not undo)


async def test_restore_feedback(taxi_eats_feedback, pgsql):
    order_nr = 'order'
    orders = [{'undo': None}, {'undo': True}]
    for order in orders:
        await taxi_eats_feedback.post(
            '/internal/eats-feedback/v1/exclude',
            json={'order_nr': order_nr, 'undo': order['undo']},
        )
        assert get_order(order_nr, pgsql) == (order_nr, not order['undo'])
