import datetime

import pytest

from fleet_rent.entities import affiliation as aff_ent
from fleet_rent.entities import charging_event as ce_event
from fleet_rent.generated.web import web_context as context_module


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id,
 asset_type, asset_params,
 title,
 driver_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz, acceptance_reason,
 transfer_order_number,
 use_event_queue)
VALUES ('record_id1', 'idempotency_token1',
        'park_id', 1,
        'other', '{"subtype": "misc"}',
        'title',
        'driver_id',
        '2020-01-01+00', '2020-01-04+00',
        'active_days',
        '{"daily_price": "100"}',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', 'acceptance_reason',
        '1',
        TRUE);
INSERT INTO rent.active_day_start_triggers
(rent_id, event_number, park_id, driver_id,
 lower_datetime_bound, upper_datetime_bound)
VALUES ('record_id1', 1, 'park_id', 'driver_id',
        '2020-01-01+00', '2020-01-04+00');
        """,
    ],
)
async def test_schedule_triggered_active_day(
        web_context: context_module.Context, stq, park_stub_factory,
):
    event_at = datetime.datetime(2020, 1, 1, 12, tzinfo=datetime.timezone.utc)

    rent_charging_events = web_context.pg_access.rent_charging_events
    scheduler = web_context.rent_components.charging_event_scheduler

    rent_triggers = await rent_charging_events.get_rent_active_day_triggers(
        'park_id', 'driver_id', event_at,
    )
    assert len(rent_triggers) == 1
    rent, trigger = rent_triggers[0]

    next_event = await scheduler.schedule_triggered_active_day(
        rent, trigger, event_at,
    )

    assert next_event.event_number == 1
    assert next_event.event_at == event_at
    assert stq.fleet_rent_process_charging_event.has_calls


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id,
 asset_type, asset_params,
 title,
 driver_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz, acceptance_reason,
 transfer_order_number,
 use_event_queue)
VALUES ('record_id1', 'idempotency_token1',
        'park_id', 1,
        'other', '{"subtype": "misc"}',
        'title',
        'driver_id',
        '2020-01-01+00', '2020-01-04+00',
        'daily',
        '{
          "daily_price": "100",
          "periodicity": {
            "type": "fraction",
            "params": {
              "numerator": 1,
              "denominator": 1
            }
          }
        }',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', 'acceptance_reason',
        '1',
        TRUE);
INSERT INTO rent.event_queue
(rent_id, event_number, event_at)
VALUES ('record_id1', 1, '2020-01-01+00');
        """,
    ],
)
async def test_schedule_event(
        web_context: context_module.Context, stq, rent_stub_factory,
):
    event = ce_event.TimeEvent(
        event_at=datetime.datetime(2020, 1, 2, tzinfo=datetime.timezone.utc),
        event_number=2,
    )
    rent = rent_stub_factory(record_id='record_id1')
    scheduler = web_context.rent_components.charging_event_scheduler
    pool = web_context.pg.master
    async with pool.acquire() as conn:
        await scheduler.schedule_event(event, rent, None, conn)
    rows = await pool.fetch(
        """SELECT * FROM rent.event_queue WHERE rent_id = 'record_id1'""",
    )
    data = [dict(x) for x in rows]
    for elem in data:
        assert elem.pop('modified_at')
    assert data == [
        {
            'event_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 1,
            'executed_at': None,
            'rent_id': 'record_id1',
        },
        {
            'event_at': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 2,
            'executed_at': None,
            'rent_id': 'record_id1',
        },
    ]
    assert stq.fleet_rent_process_charging_event.has_calls


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id,
 asset_type, asset_params,
 title,
 driver_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz, acceptance_reason,
 transfer_order_number,
 use_event_queue)
VALUES ('record_id1', 'idempotency_token1',
        'park_id', 1,
        'other', '{"subtype": "misc"}',
        'title',
        'driver_id',
        '2020-01-01+00', '2020-01-04+00',
        'daily',
        '{
          "daily_price": "100",
          "periodicity": {
            "type": "fraction",
            "params": {
              "numerator": 1,
              "denominator": 1
            }
          }
        }',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', 'acceptance_reason',
        '1',
        TRUE);
INSERT INTO rent.event_queue
(rent_id, event_number, event_at)
VALUES ('record_id1', 1, '2020-01-01+00');
        """,
    ],
)
async def test_schedule_event_not_override(
        web_context: context_module.Context, stq, rent_stub_factory,
):
    event = ce_event.TimeEvent(
        event_at=datetime.datetime(2020, 1, 2, tzinfo=datetime.timezone.utc),
        event_number=1,
    )
    rent = rent_stub_factory(record_id='record_id1')
    scheduler = web_context.rent_components.charging_event_scheduler
    pool = web_context.pg.master
    async with pool.acquire() as conn:
        await scheduler.schedule_event(event, rent, None, conn)
    rows = await pool.fetch(
        """SELECT * FROM rent.event_queue WHERE rent_id = 'record_id1'""",
    )
    data = [dict(x) for x in rows]
    for elem in data:
        assert elem.pop('modified_at')
    assert data == [
        {
            'event_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 1,
            'executed_at': None,
            'rent_id': 'record_id1',
        },
    ]
    assert stq.fleet_rent_process_charging_event.has_calls


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id,
 asset_type, asset_params,
 title,
 driver_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz, acceptance_reason,
 transfer_order_number,
 use_event_queue)
VALUES ('record_id1', 'idempotency_token1',
        'park_id', 1,
        'other', '{"subtype": "misc"}',
        'title',
        'driver_id',
        '2020-01-01+00', '2020-01-04+00',
        'daily',
        '{
          "daily_price": "100",
          "periodicity": {
            "type": "fraction",
            "params": {
              "numerator": 1,
              "denominator": 1
            }
          }
        }',
        '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', 'acceptance_reason',
        '1',
        TRUE);
        """,
    ],
)
@pytest.mark.parametrize(
    'affiliation',
    [
        None,
        aff_ent.Affiliation(
            record_id='aff_id',
            park_id='park_id',
            local_driver_id='driver_id',
            original_driver_park_id='smz_park_id',
            original_driver_id='smz_driver_id',
            state=aff_ent.AffiliationStateAccepted(),
            creator_uid='some_uid',
            created_at_tz=datetime.datetime(2020, 1, 1),
            modified_at_tz=datetime.datetime(2020, 1, 1),
        ),
    ],
)
async def test_set_event_trigger(
        web_context: context_module.Context,
        stq,
        rent_stub_factory,
        park_stub_factory,
        affiliation,
):
    event = ce_event.ShiftStartEventTrigger(
        order_id=None,
        lower_datetime_bound=datetime.datetime(
            2020, 1, 2, tzinfo=datetime.timezone.utc,
        ),
        upper_datetime_bound=None,
        triggered_at=None,
        event_number=2,
    )
    rent = rent_stub_factory(
        record_id='record_id1', driver_id='driver_id', owner_park_id='park_id',
    )
    scheduler = web_context.rent_components.charging_event_scheduler
    pool = web_context.pg.master
    async with pool.acquire() as conn:
        await scheduler.schedule_event(event, rent, affiliation, conn)
    assert not await pool.fetch(
        """SELECT * FROM rent.event_queue WHERE rent_id = 'record_id1'""",
    )
    rows = await pool.fetch(
        """SELECT * FROM rent.active_day_start_triggers
        WHERE rent_id = 'record_id1'""",
    )
    data = [dict(x) for x in rows]
    for elem in data:
        assert elem.pop('modified_at')
    if affiliation:
        assert data == [
            {
                'driver_id': 'smz_driver_id',
                'event_number': 2,
                'lower_datetime_bound': datetime.datetime(
                    2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                'order_id': None,
                'park_id': 'smz_park_id',
                'rent_id': 'record_id1',
                'triggered_at': None,
                'upper_datetime_bound': None,
            },
        ]
    else:
        assert data == [
            {
                'driver_id': 'driver_id',
                'event_number': 2,
                'lower_datetime_bound': datetime.datetime(
                    2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                'order_id': None,
                'park_id': 'park_id',
                'rent_id': 'record_id1',
                'triggered_at': None,
                'upper_datetime_bound': None,
            },
        ]
    assert not stq.fleet_rent_process_charging_event.has_calls
