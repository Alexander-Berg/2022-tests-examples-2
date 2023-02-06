import decimal

import pytest

from testsuite.utils import http

from fleet_rent.use_cases import driver_balance_by_park


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
async def test_get_balances(web_context, patch, mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/list')
    async def _list(request: http.Request):
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'login',
                    'name': 'Лещ',
                    'is_active': True,
                    'city_id': 'city_id',
                    'tz_offset': 3,
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'country_id',
                    'provider_config': {'type': 'none', 'clid': 'clid'},
                    'demo_mode': False,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.rent_and_internal_balance_by_park',
    )
    async def _get_balance(currency, affiliations):
        assert currency == 'RUB'
        return {'park_id': (decimal.Decimal(200), decimal.Decimal(100))}

    elements = await driver_balance_by_park.get_balances(
        web_context, 'driver_id', 'driver_park_id', 'RUB',
    )
    assert elements == [
        driver_balance_by_park.ParkBalances(
            park_id='park_id',
            park_name='Лещ',
            rent_balance=decimal.Decimal(200),
            internal_balance=decimal.Decimal(100),
        ),
    ]
