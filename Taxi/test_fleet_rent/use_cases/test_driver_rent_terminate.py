import datetime

import pytest

from fleet_rent.generated.web import web_context as context
from fleet_rent.use_cases import driver_rent_terminate


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
     rejected_at_tz, rejection_reason,
     transfer_order_number)
    VALUES ('rejected_record_id', 'idempotency_token',
     'park_id', 1,
     'car', '{"car_id": "car_id"}',
     'park_driver_id',
     'affiliation_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00', 'Rejected by driver',
     'park_id_1')
        """,
    ],
)
async def test_terminate_failed(web_context: context.Context):
    with pytest.raises(driver_rent_terminate.RentCannotBeTerminated):
        await web_context.use_cases.driver_rent_terminate.terminate(
            rent_id='rejected_record_id',
            driver_id='driver_id',
            driver_park_id='driver_park_id',
        )

    scheduled = await web_context.pg.master.fetch(
        'SELECT * FROM rent.park_comm_sync_rent_termination',
    )
    assert not scheduled


async def test_terminate_not_found(web_context: context.Context):
    with pytest.raises(driver_rent_terminate.RentNotFound):
        await web_context.use_cases.driver_rent_terminate.terminate(
            rent_id='bad_record_id',
            driver_id='driver_id',
            driver_park_id='driver_park_id',
        )

    scheduled = await web_context.pg.master.fetch(
        'SELECT * FROM rent.park_comm_sync_rent_termination',
    )
    assert not scheduled


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
     terminated_at_tz, termination_reason,
     transfer_order_number)
    VALUES ('terminated_record_id', 'idempotency_token',
     'park_id', 1,
     'car', '{"car_id": "car_id"}',
     'park_driver_id',
     'affiliation_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00', 'Terminated by driver',
     'park_id_1')
        """,
    ],
)
@pytest.mark.now('2020-01-02')
async def test_terminate_not_modified(web_context: context.Context):
    await web_context.use_cases.driver_rent_terminate.terminate(
        rent_id='terminated_record_id',
        driver_id='driver_id',
        driver_park_id='driver_park_id',
    )
    scheduled = await web_context.pg.master.fetch(
        'SELECT * FROM rent.park_comm_sync_rent_termination',
    )
    assert not scheduled


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
    VALUES ('record_id', 'idempotency_token',
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
async def test_terminate_ok(web_context: context.Context):
    await web_context.use_cases.driver_rent_terminate.terminate(
        rent_id='record_id',
        driver_id='driver_id',
        driver_park_id='driver_park_id',
    )
    scheduled = await web_context.pg.master.fetch(
        'SELECT * FROM rent.park_comm_sync_rent_termination',
    )
    assert scheduled

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
        assert rh_.pop('terminated_at')
    assert rent_history == [
        {
            'acceptance_reason': 'Accepted by driver',
            'accepted_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'affiliation_id': 'affiliation_id',
            'asset_params': {'car_id': 'car_id'},
            'asset_type': 'car',
            'balance_notify_limit': None,
            'begins_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_params': None,
            'charging_starts_at': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_type': 'free',
            'comment': None,
            'created_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'creator_uid': 'creator_uid',
            'driver_id': 'park_driver_id',
            'ends_at': datetime.datetime(
                2020, 1, 31, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'last_seen_at': None,
            'modification_source': {'kind': 'driver'},
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'rejected_at': None,
            'rejection_reason': None,
            'rent_id': 'record_id',
            'termination_reason': 'Terminated by driver',
            'title': None,
            'transfer_order_number': 'park_id_1',
            'use_arbitrary_entries': False,
            'use_event_queue': False,
            'version': 1,
            'start_clid': None,
        },
    ]
