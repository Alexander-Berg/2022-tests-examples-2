import pytest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_GOALS=[
        {
            'city': 'Moscow',
            'initial_sum': 100,
            'total_sum': 1000,
            'fund': 'some_fund',
            'org_donations': [
                {'org_id': 'yandex', 'org_name': 'Yandex', 'sum': 1000000},
            ],
        },
        {
            'city': 'SPb',
            'initial_sum': 300000,
            'total_sum': 1000000,
            'fund': 'some_fund',
        },
        {
            'city': 'Vologda',
            'initial_sum': 0,
            'total_sum': 100,
            'fund': 'some_fund',
        },
        {
            'city': 'Moscow',
            'initial_sum': 100,
            'total_sum': 1000,
            'fund': 'other_fund',
        },
    ],
)
async def test_simple(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.get('/payments/v1/goal')

    assert response.status == 400

    response = await taxi_persey_payments_web.get(
        '/payments/v1/goal?city=Rostov&fund=some_fund',
    )

    assert response.status == 404

    # Simple
    response = await taxi_persey_payments_web.get(
        '/payments/v1/goal?city=Moscow&fund=some_fund',
    )

    assert response.status == 200
    assert await response.json() == {
        'initial_sum': 100,
        'total_sum': 1000,
        'current_sum': 543,
        'completed': True,
        'city': 'Moscow',
        'fund': 'some_fund',
        'org_donations': [
            {'org_id': 'yandex', 'org_name': 'Yandex', 'sum': 1000000},
        ],
    }

    # Completed
    response = await taxi_persey_payments_web.get(
        '/payments/v1/goal?city=SPb&fund=some_fund',
    )

    assert response.status == 200
    assert await response.json() == {
        'initial_sum': 300000,
        'total_sum': 1000000,
        'current_sum': 700000,
        'completed': True,
        'city': 'SPb',
        'fund': 'some_fund',
        'org_donations': [],
    }

    # No donations yet
    response = await taxi_persey_payments_web.get(
        '/payments/v1/goal?city=Vologda&fund=some_fund',
    )

    assert response.status == 200
    assert await response.json() == {
        'initial_sum': 0,
        'total_sum': 100,
        'current_sum': 0,
        'completed': False,
        'city': 'Vologda',
        'fund': 'some_fund',
        'org_donations': [],
    }

    # Other fund test
    response = await taxi_persey_payments_web.get(
        '/payments/v1/goal?city=Moscow&fund=other_fund',
    )

    assert response.status == 200
    assert await response.json() == {
        'initial_sum': 100,
        'total_sum': 1000,
        'current_sum': 0,
        'completed': False,
        'city': 'Moscow',
        'fund': 'other_fund',
        'org_donations': [],
    }
