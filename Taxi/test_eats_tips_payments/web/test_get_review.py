import http

import pytest

NOT_FOUND_RESPONSE = {
    'code': 'review_not_found',
    'message': 'review not found',
}


@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.parametrize(
    ('review_id', 'expected_status', 'expected_result'),
    (
        (
            '1',
            http.HTTPStatus.OK,
            {
                'quick_choices': [],
                'rating': 1,
                'review': (
                    'вы все дураки одна я умная в белом пальто стою красивая'
                ),
            },
        ),
        (
            '2',
            http.HTTPStatus.OK,
            {
                'quick_choices': [
                    'service',
                    'quality',
                    'clean',
                    'atmosphere',
                    'speed',
                    'good_atmosphere',
                    'delicious_food',
                    'delightful_service',
                    'good_speed',
                    'master_gold_hand',
                ],
                'rating': 5,
                'review': 'отзыв о пользователе 4 со всеми быстрыми ответами',
            },
        ),
        (
            '3',
            http.HTTPStatus.OK,
            {
                'quick_choices': [
                    'service',
                    'clean',
                    'atmosphere',
                    'delicious_food',
                ],
                'rating': 3,
                'review': 'отзыв о пользователе 4 со частью быстрых ответов',
            },
        ),
        ('4', http.HTTPStatus.OK, {'quick_choices': [], 'rating': 4}),
        (
            '5',
            http.HTTPStatus.OK,
            {'quick_choices': [], 'rating': 5, 'photo': 'ссылка_на_фото'},
        ),
        # no review
        ('777', http.HTTPStatus.NOT_FOUND, NOT_FOUND_RESPONSE),
        ('qwerty', http.HTTPStatus.NOT_FOUND, NOT_FOUND_RESPONSE),
    ),
)
async def test_get_review(
        taxi_eats_tips_payments_web,
        review_id,
        expected_status,
        expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/v1/users/waiters/review', params={'review_id': review_id},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
