import pytest

from tests_driver_diagnostics import utils


@pytest.mark.experiments3(filename='diagnostics_internal_restrictions.json')
@pytest.mark.config(
    DRIVER_DIAGNOSTICS_CHECK_PROVIDERS=True,
    PRO_DIAGNOSTICS_ORDER_PROVIDER_ITEMS={
        '__default__': 'driver_diagnostics_items',
        'lavka': 'driver_diagnostics_items_eda_lavka',
    },
)
@pytest.mark.parametrize(
    'reasons, orders_provider, absolute_blocks, blocks',
    [
        ({'fetch_tags': ['tag1', 'tag2', 'tag3']}, {'taxi': True}, 2, 1),
        ({}, {'taxi': True}, 0, 1),
        ({'qc_blocks': []}, {'lavka': True}, 0, 1),
    ],
)
async def test_internal_v1_restrictions(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_profiles,
        reasons,
        orders_provider,
        absolute_blocks,
        blocks,
):
    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, orders_provider=orders_provider,
    )
    candidates.set_response_reasons(reasons, {'qc_blocks': []})

    response = await taxi_driver_diagnostics.post(
        'internal/driver-diagnostics/v1/restrictions?consumer=consumer',
        headers=utils.get_headers(),
        json=utils.get_internal_body(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'restrictions': {'absolute_blocks': absolute_blocks, 'blocks': blocks},
    }
