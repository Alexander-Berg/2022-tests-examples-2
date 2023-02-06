import pytest


@pytest.mark.parametrize(
    ('params', 'expected_result'),
    [
        ({'users': '1,2,4,6'}, {'stars': [2, 0, 1, 1, 3]}),
        ({'users': '1'}, {'stars': [2, 0, 0, 0, 0]}),
    ],
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_reviews_total(
        taxi_eats_tips_payments_web, params, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/reviews/total', params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_result
