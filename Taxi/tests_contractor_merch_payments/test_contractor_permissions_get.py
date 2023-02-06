import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.experiments3(
    filename='contractor_permissions_config_validation.json',
)
@pytest.mark.parametrize(
    ['contractor_id', 'is_balance_payment_enabled'],
    [
        pytest.param('contractor-id-1', True),
        pytest.param('contractor-id-2', False),
        pytest.param('contractor-id-10', False),
        pytest.param('contractor-id-10', False),
    ],
)
async def test_contractor_permissions_config_validation(
        taxi_contractor_merch_payments,
        mock_fleet_parks,
        mock_driver_tags,
        contractor_id,
        is_balance_payment_enabled,
):
    response = await taxi_contractor_merch_payments.get(
        '/driver/v1/contractor-merch-payments/contractor/permissions',
        utils.get_headers('park-id-1', contractor_id),
    )

    assert response.status == 200
    assert response.json() == {
        'is_balance_payment_enabled': is_balance_payment_enabled,
    }


@pytest.mark.experiments3(
    filename='contractor_merch_permissions_config_with_driver_tags.json',
)
@pytest.mark.parametrize(
    ['contractor_id', 'driver_tags', 'is_balance_payment_enabled'],
    [
        pytest.param('contractor-id-1', [], False),
        pytest.param(
            'contractor-id-2', ['merchant_enabled', 'some_tag'], True,
        ),
        pytest.param('contractor-id-3', ['tag1', 'tag2'], False),
    ],
)
async def test_contractor_permissions_config_with_tags_validation(
        taxi_contractor_merch_payments,
        mock_fleet_parks,
        mock_driver_tags,
        contractor_id,
        driver_tags,
        is_balance_payment_enabled,
):
    mock_driver_tags.fields_update = {'tags': driver_tags}

    response = await taxi_contractor_merch_payments.get(
        '/driver/v1/contractor-merch-payments/contractor/permissions',
        utils.get_headers('park-id-1', contractor_id),
    )

    assert response.status == 200
    assert response.json() == {
        'is_balance_payment_enabled': is_balance_payment_enabled,
    }
