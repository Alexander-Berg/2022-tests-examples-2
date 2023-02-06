import pytest


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
    ('record_id1', 'accepted',
     'park_id1', 'local_driver_id1',
     'original_driver_park_id1', 'original_driver_id1',
     'creator_uid', '2020-01-01+00', '2020-01-01+00'),
    ('record_id2', 'active',
     'park_id2', 'local_driver_id2',
     'original_driver_park_id2', 'original_driver_id2',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     owner_park_id, owner_serial_id, asset_type, asset_params,
     driver_id,
     affiliation_id,
     begins_at_tz, ends_at_tz,
     charging_type,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz,
     transfer_order_number)
    VALUES ('record_id', 'idempotency_token',
     'park_id2', 1, 'other', '{"subtype": "misc"}',
     'driver_id',
     'record_id2',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00',
     'park_id2_1')
        """,
    ],
)
async def test_recall(web_app_client, mock_load_park_info, patch):
    @patch(
        'fleet_rent.services.driver_notifications.'
        'DriverNotificationsService.terminated_rent',
    )
    async def _push(affiliation, park, rent):
        assert rent.record_id == 'record_id'

    response404 = await web_app_client.post(
        '/v1/park/affiliations/recall',
        params={
            'record_id': 'missing_record_id',
            'park_id': 'park_id1',
            'dispatcher_uid': 'dispatcher',
        },
    )
    assert response404.status == 404

    response409 = await web_app_client.post(
        '/v1/park/affiliations/recall',
        params={
            'record_id': 'record_id1',
            'park_id': 'park_id1',
            'dispatcher_uid': 'dispatcher',
        },
    )
    assert response409.status == 409

    response200 = await web_app_client.post(
        '/v1/park/affiliations/recall',
        params={
            'record_id': 'record_id2',
            'park_id': 'park_id2',
            'dispatcher_uid': 'dispatcher',
        },
    )
    assert response200.status == 200

    response_rent = await web_app_client.get(
        '/v1/park/rents', params={'serial_id': 1, 'park_id': 'park_id2'},
    )
    assert response_rent.status == 200
    data = await response_rent.json()
    assert data.pop('terminated_at')
    assert data == {
        'accepted_at': '2020-01-01T03:00:00+03:00',
        'begins_at': '2020-01-01T03:00:00+03:00',
        'asset': {'type': 'other', 'subtype': 'misc'},
        'owner_park_id': 'park_id2',
        'owner_serial_id': 1,
        'charging': {'type': 'free'},
        'charging_starts_at': '2020-01-02T03:00:00+03:00',
        'created_at': '2020-01-01T03:00:00+03:00',
        'creator_uid': 'creator_uid',
        'driver_id': 'driver_id',
        'ends_at': '2020-01-31T03:00:00+03:00',
        'record_id': 'record_id',
        'state': 'park_terminated',
        'termination_reason': 'Terminated by park, due to affiliation recall',
        'affiliation_id': 'record_id2',
        'billing_topic': 'taxi/periodic_payment/clid/100500/1',
    }
    assert _push.calls
