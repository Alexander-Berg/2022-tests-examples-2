# type: ignore[dict-item]

import pytest


@pytest.mark.parametrize(
    ['order_nrs', 'expected_response'],
    [
        [  # id=greenflow
            [
                '100000-100011',
                '100000-100022',
                '100000-100033',
                '100000-100044',
            ],
            (200, 'feedback_response.json'),
        ],
        [  # id=partly_nonexistent_feedback
            [
                '100000-100010',  # not exist
                '100000-100011',
                '100011-000000',
                '100022-000000',
                '100000-100033',
            ],
            (200, 'partly_existent_feedback_response.json'),
        ],
        [  # id=validation_error
            [100500],
            (400, 'validation_error_response.json'),
        ],
    ],
    ids=['greenflow', 'partly_existent_feedback', 'validation_error'],
)
@pytest.mark.config(EATS_FEEDBACK_PG_SELECT_FEEDBACK_LIMIT={'limit': 3})
@pytest.mark.pgsql('eats_feedback', files=['feedbacks.sql', 'orders.sql'])
@pytest.mark.now('2020-07-24T12:00:00+00:00')
async def test_get_feedbacks_for_orders_history(
        # ---- fixtures ----
        load_json,
        taxi_eats_feedback,
        # ---- parameters ----
        order_nrs,
        expected_response,
):
    expected_code, expected_body = expected_response

    response = await taxi_eats_feedback.post(
        '/internal/eats-feedback/v1/get-feedbacks-for-orders-history',
        json={'order_nrs': order_nrs},
    )

    assert response.status_code == expected_code
    if expected_body is not None:
        assert response.json() == load_json(expected_body)
