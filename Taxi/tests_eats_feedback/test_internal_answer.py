import pytest


@pytest.mark.parametrize(
    [
        'params',
        'result_json_before',
        'result_json_after',
        'update_params',
        'result_json_after_update',
    ],
    [
        pytest.param(
            {
                'feedback_id': 2,
                'comment': 'comment',
                'coupon': {
                    'currency_code': 'RUB',
                    'expire_at': '2022-03-08T20:59:00+00:00',
                    'limit': '1999.99',
                    'percent': 10,
                },
            },
            'feedbacks_no_answer.json',
            'feedbacks_1.json',
            {
                'answer_id': 1,
                'answer_status_code': 1,
                'coupon': {
                    'coupon': 'COUPON',
                    'currency_code': 'RUB',
                    'expire_at': '2022-03-08T20:59:00+00:00',
                    'limit': '1999.99',
                    'percent': 10,
                },
            },
            'feedbacks_update.json',
            marks=pytest.mark.pgsql(
                'eats_feedback',
                files=[
                    'predefined_comments.sql',
                    'feedbacks.sql',
                    'orders.sql',
                ],
            ),
        ),
        pytest.param(
            {'feedback_id': 1, 'comment': 'comment1'},
            'feedbacks_no_answer.json',
            'feedbacks_2.json',
            {'answer_id': 1, 'answer_status_code': 1},
            'feedbacks_2.json',
            marks=pytest.mark.pgsql(
                'eats_feedback',
                files=[
                    'predefined_comments.sql',
                    'feedbacks.sql',
                    'orders.sql',
                ],
            ),
        ),
        pytest.param(
            {'feedback_id': 1, 'comment': 'comment2'},
            'feedbacks_2.json',
            'feedbacks_3.json',
            {'answer_id': 1, 'answer_status_code': 1},
            'feedbacks_3.json',
            marks=pytest.mark.pgsql(
                'eats_feedback',
                files=[
                    'predefined_comments.sql',
                    'feedbacks.sql',
                    'feedbacks_answer.sql',
                    'orders.sql',
                ],
            ),
        ),
    ],
    ids=['comment+coupon', 'comment only', 'second comment'],
)
async def test_post_answer(
        load_json,
        taxi_eats_feedback,
        params,
        result_json_before,
        result_json_after,
        update_params,
        result_json_after_update,
):
    response = await taxi_eats_feedback.get(
        '/internal/eats-feedback/v1/feedbacks',
        params={'place_id': 1, 'actual': True, 'user_locale': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(result_json_before)

    response = await taxi_eats_feedback.post(
        '/internal/eats-feedback/v1/answer', json=params,
    )

    assert response.status_code == 204

    response2 = await taxi_eats_feedback.get(
        '/internal/eats-feedback/v1/feedbacks',
        params={'place_id': 1, 'actual': True, 'user_locale': 'ru'},
    )
    assert response2.status_code == 200
    assert response2.json() == load_json(result_json_after)

    response3 = await taxi_eats_feedback.post(
        '/internal/eats-feedback/v1/answer/update', json=update_params,
    )
    assert response3.status_code == 204

    response4 = await taxi_eats_feedback.get(
        '/internal/eats-feedback/v1/feedbacks',
        params={'place_id': 1, 'actual': True, 'user_locale': 'ru'},
    )
    assert response4.status_code == 200
    assert response4.json() == load_json(result_json_after_update)


async def test_post_answer_400(load_json, taxi_eats_feedback):
    response = await taxi_eats_feedback.post(
        '/internal/eats-feedback/v1/answer', json={'feedback_id': 2},
    )

    assert response.status_code == 400


async def test_post_update_answer_400(load_json, taxi_eats_feedback):
    response = await taxi_eats_feedback.post(
        '/internal/eats-feedback/v1/answer/update',
        json={
            'answer_id': 1,
            'answer_status_code': 1,
            'coupon': {
                'coupon': 'COUPON',
                'currency_code': 'RUB',
                'expire_at': '2022-03-08T20:59:00+00:00',
                'limit': '1999.99',
                'percent': 10,
                'value': 3000,
            },
        },
    )

    assert response.status_code == 400
