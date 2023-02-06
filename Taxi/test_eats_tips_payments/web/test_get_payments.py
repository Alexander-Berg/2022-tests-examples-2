import pytest


@pytest.mark.parametrize(
    'params, expected_status, expected_result',
    [
        (
            {'users': '6,4'},
            200,
            {
                'transactions': [
                    {
                        'user_id': 6,
                        'amount': 3000.0,
                        'datetime': '2021-09-16T18:58:04+03:00',
                        'quick_choices': [],
                        'rating': 5,
                        'review': 'отзыв о пользователе 6 с платежом',
                    },
                    {
                        'user_id': 4,
                        'datetime': '2021-09-16T18:53:04+03:00',
                        'rating': 3,
                        'review': (
                            'отзыв о пользователе 4 со частью быстрых ответов'
                        ),
                        'quick_choices': [
                            'Сервис',
                            'Чистота',
                            'Атмосфера',
                            'Вкусная еда и напитки',
                        ],
                    },
                    {
                        'user_id': 4,
                        'datetime': '2021-09-16T18:53:03+03:00',
                        'rating': 5,
                        'review': (
                            'отзыв о пользователе 4 со всеми быстрыми ответами'
                        ),
                        'quick_choices': [
                            'Сервис',
                            'Еда и качество напитков',
                            'Чистота',
                            'Атмосфера',
                            'Скорость обслуживания',
                            'Прекрасная атмосфера',
                            'Вкусная еда и напитки',
                            'Душевный сервис',
                            'Быстрое обслуживание',
                            'Мастер - золотые руки',
                        ],
                    },
                    {
                        'user_id': 6,
                        'amount': 4000.0,
                        'datetime': '1970-01-01T03:01:40+03:00',
                        'quick_choices': [],
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_get_payments(
        taxi_eats_tips_payments_web, params, expected_status, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/payments', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
