import pytest


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_factors_get_200(taxi_eats_logistics_performer_payouts):
    response = await taxi_eats_logistics_performer_payouts.get('/v1/factors')
    assert response.status == 200
    print(response.json())
    factors = response.json().get('factors')
    assert factors
    assert factors[0].get('subject_type').get('id') == 1
    assert factors[0].get('subject_type').get('name') == 'performer'
    assert factors[0].get('subject_type').get('id') == 1
    assert factors[0].get('subject_type').get('name') == 'performer'
