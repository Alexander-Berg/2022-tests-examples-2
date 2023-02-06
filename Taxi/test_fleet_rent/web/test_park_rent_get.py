import pytest


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     owner_park_id, owner_serial_id, asset_type, asset_params,
     driver_id,
     begins_at_tz, ends_at_tz,
     charging_type,
     charging_params,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz,
     transfer_order_number)
    VALUES ('record_id', 'idempotency_token',
     'park_id', 1, 'other', '{"subtype": "misc"}',
     'driver_id',
     '2020-01-01+00', '2020-01-31+00',
     'daily',
     '{
        "daily_price": "100",
        "total_withhold_limit": "500",
        "periodicity": {
            "type": "constant",
            "params": null
        },
        "time": "03:00:00"
     }',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00',
     'park_id_1')
        """,
    ],
)
@pytest.mark.now('2020-03-01T00:00:00')
async def test_get(web_app_client, mock_load_park_info):
    response404 = await web_app_client.get(
        '/v1/park/rents', params={'serial_id': 2, 'park_id': 'park_id'},
    )
    assert response404.status == 404

    response0 = await web_app_client.get(
        '/v1/park/rents', params={'serial_id': 1, 'park_id': 'park_id'},
    )
    assert response0.status == 200
    data1 = await response0.json()
    assert data1 == {
        'accepted_at': '2020-01-01T03:00:00+03:00',
        'begins_at': '2020-01-01T03:00:00+03:00',
        'asset': {'type': 'other', 'subtype': 'misc'},
        'owner_park_id': 'park_id',
        'owner_serial_id': 1,
        'charging': {
            'type': 'daily',
            'daily_price': '100',
            'total_withhold_limit': '500',
            'periodicity': {'type': 'constant'},
            'time': '03:00:00',
        },
        'charging_starts_at': '2020-01-02T03:00:00+03:00',
        'created_at': '2020-01-01T03:00:00+03:00',
        'creator_uid': 'creator_uid',
        'driver_id': 'driver_id',
        'ends_at': '2020-01-31T03:00:00+03:00',
        'record_id': 'record_id',
        'state': 'ended',
    }


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.affiliations
    (record_id, state,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz, modified_at_tz)
    VALUES
    ('affiliation_id', 'active',
     'park_id', 'local_driver_id',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     affiliation_id,
     owner_park_id, owner_serial_id, asset_type, asset_params,
     driver_id,
     begins_at_tz, ends_at_tz,
     charging_type,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz,
     transfer_order_number)
    VALUES ('record_id', 'idempotency_token',
     'affiliation_id',
     'park_id', 1, 'other', '{"subtype": "misc"}',
     'driver_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00',
     'park_id_1')
        """,
    ],
)
@pytest.mark.now('2020-03-01T00:00:00')
async def test_get_external(web_app_client, mock_load_park_info):
    response404 = await web_app_client.get(
        '/v1/park/rents', params={'serial_id': 2, 'park_id': 'park_id'},
    )
    assert response404.status == 404

    response0 = await web_app_client.get(
        '/v1/park/rents', params={'serial_id': 1, 'park_id': 'park_id'},
    )
    assert response0.status == 200
    data1 = await response0.json()
    assert data1 == {
        'accepted_at': '2020-01-01T03:00:00+03:00',
        'begins_at': '2020-01-01T03:00:00+03:00',
        'asset': {'type': 'other', 'subtype': 'misc'},
        'owner_park_id': 'park_id',
        'affiliation_id': 'affiliation_id',
        'owner_serial_id': 1,
        'charging': {'type': 'free'},
        'charging_starts_at': '2020-01-02T03:00:00+03:00',
        'created_at': '2020-01-01T03:00:00+03:00',
        'creator_uid': 'creator_uid',
        'driver_id': 'driver_id',
        'ends_at': '2020-01-31T03:00:00+03:00',
        'record_id': 'record_id',
        'state': 'ended',
        'billing_topic': 'taxi/periodic_payment/clid/100500/1',
    }
