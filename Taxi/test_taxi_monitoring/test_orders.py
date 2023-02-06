import pytest


async def test_orders(monitoring_client):
    response = await monitoring_client.get('/orders')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'total': 5,
        'found': 1,
        'cancelled1m': 0,  # broken stat
        'user_fraud': 1,
        'draft': 1,
        'classes': {
            'econom': {
                'total': 3,
                'found': 1,
                'cancelled1m': 0,
                'user_fraud': 1,
                'draft': 0,
            },
        },
        'cities': {
            'moscow': {
                'total': 5,
                'found': 1,
                'cancelled1m': 0,  # broken stat
                'user_fraud': 1,
                'draft': 1,
            },
            'spb': {
                'total': 0,
                'found': 0,
                'cancelled1m': 0,
                'user_fraud': 0,
                'draft': 0,
            },
        },
    }


@pytest.mark.filldb(order_proc='empty')
async def test_orders_empty(monitoring_client):
    response = await monitoring_client.get('/orders')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'total': 0,
        'found': 0,
        'cancelled1m': 0,
        'user_fraud': 0,
        'draft': 0,
        'classes': {},
        'cities': {
            'moscow': {
                'total': 0,
                'found': 0,
                'cancelled1m': 0,
                'user_fraud': 0,
                'draft': 0,
            },
            'spb': {
                'total': 0,
                'found': 0,
                'cancelled1m': 0,
                'user_fraud': 0,
                'draft': 0,
            },
        },
    }
