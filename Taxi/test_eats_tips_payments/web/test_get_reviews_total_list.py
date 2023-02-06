import pytest


@pytest.mark.parametrize(
    ('params', 'expected_result'),
    [
        (
            {'users': '1,2,4,6'},
            {
                'values': [
                    {'stars': [2, 0, 0, 0, 0], 'user_id': 1},
                    {'stars': [0, 0, 0, 1, 1], 'user_id': 2},
                    {'stars': [0, 0, 1, 0, 1], 'user_id': 4},
                    {'stars': [0, 0, 0, 0, 1], 'user_id': 6},
                ],
            },
        ),
        (
            {'users': '1'},
            {'values': [{'stars': [2, 0, 0, 0, 0], 'user_id': 1}]},
        ),
    ],
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_reviews_total_list(
        taxi_eats_tips_payments_web, params, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/reviews/total/list', params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_result
