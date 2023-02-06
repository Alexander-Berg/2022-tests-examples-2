import pytest

from tests_cargo_crm import const


async def test_activate_cargo_servises(taxi_cargo_crm, mocked_corp_clients):
    mocked_corp_clients.services_cargo.set_expected_data(
        {
            'deactivate_threshold_date': None,
            'deactivate_threshold_ride': None,
            'is_test': False,
            'is_active': True,
            'is_visible': True,
        },
    )
    mocked_corp_clients.services_cargo.set_response(
        200,
        {
            'deactivate_threshold_date': None,
            'deactivate_threshold_ride': None,
            'is_test': False,
            'is_active': False,
            'is_visible': False,
        },
    )

    response = await taxi_cargo_crm.post(
        '/functions/activate-cargo-servises',
        json={'corp_client_id': const.CORP_CLIENT_ID},
    )

    assert response.status == 200

    # get and update
    assert mocked_corp_clients.services_cargo_times_called == 2
