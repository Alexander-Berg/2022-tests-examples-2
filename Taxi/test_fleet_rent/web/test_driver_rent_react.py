import datetime as dt

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
     transfer_order_number)
    VALUES ('record_id', 'idempotency_token',
     'park_id', 1,
     'car', '{"car_id": "car_id"}',
     'park_driver_id',
     'affiliation_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     'park_id_1')
        """,
    ],
)
async def test_accept(
        web_app_client,
        mock_load_park_info,
        driver_auth_headers,
        patch,
        web_context,
):
    @patch(
        'fleet_rent.components.charging_event_scheduler.'
        'ChargingEventScheduler.schedule_first_event',
    )
    async def _schedule(
            rent, park, affiliation, latest_event=None, connection=None,
    ):
        assert rent.record_id == 'record_id'

    response404 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/react',
        params={'rent_id': 'bad_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response404.status == 404

    assert not _schedule.calls

    response200_1 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/react',
        params={'rent_id': 'record_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response200_1.status == 200

    assert _schedule.calls

    response200_2 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/react',
        params={'rent_id': 'record_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response200_2.status == 200

    response409 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/react',
        params={'rent_id': 'record_id', 'reaction': 'reject'},
        headers=driver_auth_headers,
    )
    assert response409.status == 409

    rent_history = [
        {**x}
        for x in await web_context.pg.master.fetch(
            """SELECT * FROM rent.rent_history
            WHERE rent_id ='record_id'
            ORDER BY version DESC;""",
        )
    ]
    for rh_ in rent_history:
        assert rh_.pop('modified_at')
        assert rh_.pop('accepted_at')
    assert rent_history == [
        {
            'modification_source': '{"kind": "driver"}',
            'acceptance_reason': 'Accepted by driver',
            'affiliation_id': 'affiliation_id',
            'asset_params': '{"car_id": "car_id"}',
            'asset_type': 'car',
            'balance_notify_limit': None,
            'begins_at': dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc),
            'charging_params': None,
            'charging_starts_at': dt.datetime(
                2020, 1, 2, 0, 0, tzinfo=dt.timezone.utc,
            ),
            'charging_type': 'free',
            'comment': None,
            'created_at': dt.datetime(
                2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc,
            ),
            'creator_uid': 'creator_uid',
            'driver_id': 'park_driver_id',
            'ends_at': dt.datetime(2020, 1, 31, 0, 0, tzinfo=dt.timezone.utc),
            'last_seen_at': None,
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'rejected_at': None,
            'rejection_reason': None,
            'rent_id': 'record_id',
            'terminated_at': None,
            'termination_reason': None,
            'title': None,
            'transfer_order_number': 'park_id_1',
            'use_arbitrary_entries': False,
            'use_event_queue': False,
            'version': 1,
            'start_clid': None,
        },
    ]


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
     transfer_order_number)
    VALUES ('record_id', 'idempotency_token',
     'park_id', 1,
     'car', '{"car_id": "car_id"}',
     'park_driver_id',
     'affiliation_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     'park_id_1')
        """,
    ],
)
async def test_reject(web_app_client, driver_auth_headers, patch, web_context):
    @patch(
        'fleet_rent.components.charging_event_scheduler.'
        'ChargingEventScheduler.schedule_first_event',
    )
    async def _schedule(*args, **kwargs):
        pass

    response404 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/react',
        params={'rent_id': 'bad_id', 'reaction': 'reject'},
        headers=driver_auth_headers,
    )
    assert response404.status == 404

    assert not _schedule.calls

    response200_1 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/react',
        params={'rent_id': 'record_id', 'reaction': 'reject'},
        headers=driver_auth_headers,
    )
    assert response200_1.status == 200

    assert not _schedule.calls

    response200_2 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/react',
        params={'rent_id': 'record_id', 'reaction': 'reject'},
        headers=driver_auth_headers,
    )
    assert response200_2.status == 200

    response409 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/react',
        params={'rent_id': 'record_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response409.status == 409

    rent_history = [
        {**x}
        for x in await web_context.pg.master.fetch(
            """SELECT * FROM rent.rent_history
            WHERE rent_id ='record_id'
            ORDER BY version ASC;""",
        )
    ]
    for rh_ in rent_history:
        assert rh_.pop('modified_at')
        assert rh_.pop('rejected_at')
    assert rent_history == [
        {
            'modification_source': '{"kind": "driver"}',
            'acceptance_reason': None,
            'accepted_at': None,
            'affiliation_id': 'affiliation_id',
            'asset_params': '{"car_id": "car_id"}',
            'asset_type': 'car',
            'balance_notify_limit': None,
            'begins_at': dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc),
            'charging_params': None,
            'charging_starts_at': dt.datetime(
                2020, 1, 2, 0, 0, tzinfo=dt.timezone.utc,
            ),
            'charging_type': 'free',
            'comment': None,
            'created_at': dt.datetime(
                2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc,
            ),
            'creator_uid': 'creator_uid',
            'driver_id': 'park_driver_id',
            'ends_at': dt.datetime(2020, 1, 31, 0, 0, tzinfo=dt.timezone.utc),
            'last_seen_at': None,
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'rejection_reason': 'Rejected by driver',
            'rent_id': 'record_id',
            'terminated_at': None,
            'termination_reason': None,
            'title': None,
            'transfer_order_number': 'park_id_1',
            'use_arbitrary_entries': False,
            'use_event_queue': False,
            'version': 1,
            'start_clid': None,
        },
    ]
