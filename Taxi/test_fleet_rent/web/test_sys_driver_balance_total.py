import decimal

import pytest


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
    ('affiliation_id', 'active',
     'park_id', 'local_driver_id',
     'driver_park_id', 'driver_id',
     'creator_uid', '2020-01-01+00')
        """,
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     owner_park_id, owner_serial_id, asset_type, asset_params,
     driver_id, affiliation_id,
     begins_at_tz, ends_at_tz,
     charging_type,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz,
     transfer_order_number)
    VALUES ('record_id', 'idempotency_token',
     'park_id', 1, 'other', '{"subtype": "misc"}',
     'driver_id', 'affiliation_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00',
     'park_id_1')
        """,
    ],
)
async def test_get_total(web_app_client, patch):
    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.get_total_driver_balance',
    )
    async def _get(currency, affiliations):
        assert currency == 'RUB'
        affiliations = list(affiliations)
        assert len(affiliations) == 1
        assert affiliations[0].record_id == 'affiliation_id'
        return decimal.Decimal(100)

    response = await web_app_client.get(
        '/fleet-rent/v1/sys/driver-balance/total',
        params={
            'driver_id': 'driver_id',
            'park_id': 'driver_park_id',
            'currency': 'RUB',
        },
    )
    assert response.status == 200
    assert await response.json() == {'amount': '100'}
