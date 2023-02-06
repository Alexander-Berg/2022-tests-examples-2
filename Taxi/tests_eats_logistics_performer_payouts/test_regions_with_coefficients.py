import pytest


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_coefficients.sql'],
)
async def test_regions_with_coefficients(
        taxi_eats_logistics_performer_payouts,
):
    expected_response = ['1', '2', '__default__']
    response = await taxi_eats_logistics_performer_payouts.get(
        '/v1/admin/regions-with-coefficients',
    )
    assert response.status_code == 200
    assert sorted(response.json()['region_ids']) == sorted(expected_response)
