import pytest


@pytest.mark.pgsql('balance-replica', files=['default.sql'])
async def test_by_bik_200(taxi_balance_replica):
    response = await taxi_balance_replica.post(
        'v1/banks/by_bik', json={'bik': '100000001'},
    )

    assert response.status == 200
    assert response.json() == {
        'accounts': '',
        'bik': '100000001',
        'city': 'city1',
        'cor_acc': '10000000000000000001',
        'cor_acc_type': 'CRSA',
        'hidden': 0,
        'id': 1,
        'info': 'ВРФС',
        'name': 'Банк 1',
        'swift': 'BANK1',
        'update_dt': '2020-01-01T12:00:00Z',
    }


async def test_by_bik_404(taxi_balance_replica):
    response = await taxi_balance_replica.post(
        'v1/banks/by_bik', json={'bik': '999999999'},
    )
    assert response.status == 404
    assert response.json() == {
        'code': 'Bank not found by requested bik',
        'message': 'bank_not_found',
    }


async def test_by_bik_400(taxi_balance_replica):
    response = await taxi_balance_replica.post(
        'v1/banks/by_bik', json={'bik': ''},
    )
    assert response.status == 400
