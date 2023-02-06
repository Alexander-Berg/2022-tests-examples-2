import pytest


@pytest.mark.pgsql('reposition_matcher', files=['modes_zones.sql'])
@pytest.mark.parametrize(
    'mode_name, formulas',
    [
        ('home', ['regular_mode']),
        ('poi', ['surge_mode', 'regular_offer_mode']),
        ('District', ['area_mode', 'destination_district_mode']),
    ],
)
async def test_deviation_formulas_by_mode(
        taxi_reposition_matcher, mode_name, formulas,
):
    response = await taxi_reposition_matcher.get(
        f'v1/admin/deviation_formulas/list_available?mode={mode_name}',
    )
    assert response.status == 200
    assert set(response.json()['deviation_formulas']) == set(formulas)
