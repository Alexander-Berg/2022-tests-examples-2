import datetime

import pytest

from fleet_rent.generated.web import web_context as context
from fleet_rent.use_cases import driver_rent_details


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.affiliations
    (record_id, state,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz)
    VALUES
    ('affiliation_id', 'new',
     'park_id', 'park_driver_id',
     'driver_park_id', 'driver_id',
     'creator_uid', '2020-01-01+00')
        """,
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     owner_park_id, owner_serial_id,
     asset_type, asset_params,
     driver_id,
     affiliation_id,
     begins_at_tz, ends_at_tz,
     charging_type,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz, acceptance_reason,
     transfer_order_number)
    VALUES ('rent_id', 'idempotency_token',
     'park_id', 1,
     'car', '{"car_id": "car_id"}',
     'park_driver_id',
     'affiliation_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00', 'Accepted by driver',
     'park_id_1')
        """,
    ],
)
async def test_get_details(
        web_context: context.Context,
        patch,
        park_stub_factory,
        mock_load_billing_data,
        mock_load_park_contacts,
        mock_load_car_info,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_currency(*args, **kwargs):
        return 'RUB'

    with pytest.raises(driver_rent_details.NotFound):
        await web_context.use_cases.driver_rent_details.get_rent_details(
            rent_id='rent_id',
            driver_id='wrong_driver',
            driver_park_id='wrong_park',
            now=datetime.datetime(
                2020, 1, 1, 12, tzinfo=datetime.timezone.utc,
            ),
        )

    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info_batch')
    async def _get_park_info_batch(park_ids):
        return {park_id: park_stub_factory(id=park_id) for park_id in park_ids}

    data = await web_context.use_cases.driver_rent_details.get_rent_details(
        rent_id='rent_id',
        driver_id='driver_id',
        driver_park_id='driver_park_id',
        now=datetime.datetime(2020, 1, 1, 12, tzinfo=datetime.timezone.utc),
    )
    assert data.affiliation.record_id == 'affiliation_id'
    assert isinstance(data.asset_data, driver_rent_details.AssetDataCar)
    assert data.asset_data.car_data.id == 'car_id'
    assert data.driver_currency == 'RUB'
    assert data.driver_park.id == 'driver_park_id'
    assert data.owner_park.id == 'park_id'
    assert data.owner_park_billing.clid == '100500'
    assert data.owner_park_contacts.id == 'park_id'
    assert data.rent.record_id == 'rent_id'
