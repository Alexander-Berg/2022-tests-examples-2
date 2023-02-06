import pytest

MULTIOFFER_ID_1 = '72bcbde8-eaed-460f-8f88-eeb4e056c316'
MULTIOFFER_ID_MISSING = '72bcbde8-eaed-460f-8f88-eeb4e056c999'
ORDER_ID_1 = '123'


@pytest.mark.pgsql('contractor_orders_multioffer')
async def test_empty_db(taxi_contractor_orders_multioffer):
    params = {
        'park_id': 'park_id',
        'driver_profile_id': 'driver_profile_id',
        'multioffer_id': MULTIOFFER_ID_1,
    }
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/multioffer/state_for_pricing', json=params,
    )
    assert response.status_code == 404


@pytest.mark.parametrize('match_driver', [True, False])
@pytest.mark.parametrize(
    'driver, paid_supply',
    [('driver_profile_id_1', False), ('driver_profile_id_6', True)],
)
@pytest.mark.pgsql(
    'contractor_orders_multioffer', files=['multioffer_internal_state.sql'],
)
async def test_existing_multioffer_200(
        taxi_contractor_orders_multioffer, match_driver, driver, paid_supply,
):
    params = {
        'park_id': 'park_id',
        'driver_profile_id': driver,
        'multioffer_id': (
            MULTIOFFER_ID_1 if match_driver else MULTIOFFER_ID_MISSING
        ),
    }
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/multioffer/state_for_pricing', json=params,
    )
    if match_driver:
        assert response.status_code == 200
        json = response.json()
        assert json['order_id'] == ORDER_ID_1
        assert json['paid_supply'] == paid_supply
    else:
        assert response.status_code == 404
