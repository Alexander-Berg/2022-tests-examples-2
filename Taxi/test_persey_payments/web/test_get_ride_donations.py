import pytest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
async def test_simple(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/ride_donations?order_ids=order1,order2',
    )

    assert response.status == 200
    assert await response.json() == {
        'orders': [
            {
                'order_id': 'order1',
                'donation': {
                    'status': 'started',
                    'amount_info': {
                        'amount': '123.000000',
                        'currency_code': 'RUB',
                        'currency_sign': '₽',
                    },
                },
            },
            {'order_id': 'order2'},
        ],
    }


@pytest.mark.pgsql('persey_payments', files=['simple_post.sql'])
async def test_post_simple(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.post(
        '/internal/v1/charity/multibrand/ride_donations',
        json={
            'brands': [
                {'brand': 'yataxi', 'order_ids': ['order1', 'order2']},
                {'brand': 'lavka', 'order_ids': ['order2']},
                {'brand': 'eats', 'order_ids': []},
            ],
        },
        headers={'X-Request-Language': 'ru'},
    )

    assert response.status == 200
    assert await response.json() == {
        'brands': [
            {
                'brand': 'yataxi',
                'orders': [
                    {
                        'order_id': 'order1',
                        'donation': {
                            'status': 'started',
                            'amount_info': {
                                'amount': '123.000000',
                                'currency_code': 'RUB',
                                'currency_sign': '₽',
                            },
                        },
                    },
                    {'order_id': 'order2'},
                ],
            },
            {
                'brand': 'lavka',
                'orders': [
                    {
                        'order_id': 'order2',
                        'donation': {
                            'status': 'started',
                            'amount_info': {
                                'amount': '231.000000',
                                'currency_code': 'RUB',
                                'currency_sign': '₽',
                            },
                        },
                    },
                ],
            },
            {'brand': 'eats', 'orders': []},
        ],
    }
