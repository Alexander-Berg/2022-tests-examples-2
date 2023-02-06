import pytest

from tests_debt_collector import builders


@pytest.mark.pgsql('eats_debt_collector', files=['eats_debt_collector.sql'])
async def test_debts_by_id(taxi_debt_collector):
    response = await taxi_debt_collector.post(
        '/v1/debts/by_id', {'ids': ['with_two_debtors_id'], 'service': 'eats'},
    )
    assert response.json() == {
        'debts': [
            builders.debt_info(
                'with_two_debtors_id',
                'with_two_debtors_invoice_id',
                ['taxi/phone_id/some_phone_id', 'yandex/uid/some_uid'],
            ),
        ],
    }


@pytest.mark.pgsql('eats_debt_collector', files=['eats_debt_collector.sql'])
async def test_debts_by_id_not_found(taxi_debt_collector):
    response = await taxi_debt_collector.post(
        '/v1/debts/by_id', {'ids': ['unknown_id'], 'service': 'eats'},
    )
    assert response.status_code == 200
    assert response.json() == {'debts': []}
