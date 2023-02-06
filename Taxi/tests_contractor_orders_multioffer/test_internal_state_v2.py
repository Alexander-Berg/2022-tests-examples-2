import pytest


@pytest.mark.pgsql('contractor_orders_multioffer')
async def test_internal_offer_empty_db(taxi_contractor_orders_multioffer):
    params = {
        'park_id': 'park_id',
        'driver_profile_id': 'driver_profile_id',
        'alias_id': 'alias_id',
    }
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v2/multioffer/state', json=params,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'driver_profile_id, alias_id',
    [('driver_profile_id_not_found', 'alias_id')],
)
@pytest.mark.pgsql(
    'contractor_orders_multioffer', files=['multioffer_internal_state.sql'],
)
async def test_internal_offer_db_404(
        taxi_contractor_orders_multioffer, driver_profile_id, alias_id, pgsql,
):
    params = {
        'park_id': 'park_id',
        'driver_profile_id': driver_profile_id,
        'alias_id': alias_id,
    }
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v2/multioffer/state', json=params,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'driver_profile_id, state, multioffer_id, in_extended_radius',
    [
        (
            'driver_profile_id_1',
            'win',
            '72bcbde8-eaed-460f-8f88-eeb4e056c316',
            False,
        ),
        (
            'driver_profile_id_2',
            'sent',
            '72bcbde8-eaed-460f-8f88-eeb4e056c317',
            True,
        ),
    ],
)
@pytest.mark.pgsql(
    'contractor_orders_multioffer', files=['multioffer_internal_state.sql'],
)
async def test_internal_offer_db_200(
        taxi_contractor_orders_multioffer,
        driver_profile_id,
        state,
        multioffer_id,
        in_extended_radius,
):
    params = {
        'park_id': 'park_id',
        'driver_profile_id': driver_profile_id,
        'alias_id': 'alias_id',
    }
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v2/multioffer/state', json=params,
    )
    assert response.status_code == 200
    json = response.json()
    assert json['multioffer_id'] == multioffer_id
    assert json['state'] == state
    assert json['timeout'] == 15  # like in db
    assert json['play_timeout'] == 12  # like in db
    assert json['candidate'] == {
        'in_extended_radius': in_extended_radius,
        'some_field': 'some_value',
    }
