import datetime

import pytest

from fleet_rent.generated.web import web_context as wc


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_park_terminate(
        web_app_client, web_context: wc.Context, patch, mock_load_park_info,
):
    @patch(
        'fleet_rent.services.driver_notifications.'
        'DriverNotificationsService.terminated_rent',
    )
    async def _push(affiliation, park, rent):
        assert rent.record_id == 'record_id'

    response = await web_app_client.post(
        '/v1/park/rents/terminate',
        params={
            'park_id': 'park_id',
            'user_id': 'terminator',
            'record_id': 'record_id',
        },
    )
    assert response.status == 200

    terminated = await web_context.pg_access.rent.park_get_rent(
        record_id='record_id', park_id='park_id',
    )
    assert terminated.termination_reason
    assert terminated.terminated_at

    triggers = await web_context.pg.master.fetch(
        'SELECT * FROM rent.active_day_start_triggers',
    )
    assert [t['event_number'] for t in triggers] == [1]

    rent_history = [
        {**x}
        for x in await web_context.pg.master.fetch(
            """SELECT * FROM rent.rent_history
            WHERE rent_id ='record_id'
            ORDER BY version ASC;""",
        )
    ]
    for rh_ in rent_history:
        assert rh_.pop('created_at')
        assert rh_.pop('modified_at')
        assert rh_.pop('accepted_at')
    assert not rent_history[0].pop('terminated_at')
    assert rent_history[1].pop('terminated_at')
    assert rent_history == [
        {
            'acceptance_reason': None,
            'affiliation_id': 'affiliation_id',
            'asset_params': '{"subtype": "misc"}',
            'asset_type': 'other',
            'balance_notify_limit': None,
            'begins_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_params': '{"daily_price": "100"}',
            'charging_starts_at': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_type': 'active_days',
            'comment': None,
            'creator_uid': 'creator_uid',
            'driver_id': 'driver_id',
            'ends_at': datetime.datetime(
                2020, 1, 31, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'last_seen_at': None,
            'modification_source': '{"uid": "user_uid", "kind": "dispatcher"}',
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'rejected_at': None,
            'rejection_reason': None,
            'rent_id': 'record_id',
            'termination_reason': None,
            'title': None,
            'transfer_order_number': 'park_id_1',
            'use_arbitrary_entries': False,
            'use_event_queue': True,
            'version': 1,
            'start_clid': None,
        },
        {
            'acceptance_reason': None,
            'affiliation_id': 'affiliation_id',
            'asset_params': '{"subtype": "misc"}',
            'asset_type': 'other',
            'balance_notify_limit': None,
            'begins_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_params': '{"daily_price": "100"}',
            'charging_starts_at': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_type': 'active_days',
            'comment': None,
            'creator_uid': 'creator_uid',
            'driver_id': 'driver_id',
            'ends_at': datetime.datetime(
                2020, 1, 31, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'last_seen_at': None,
            'modification_source': (
                '{"uid": "terminator", "kind": "dispatcher"}'
            ),
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'rejected_at': None,
            'rejection_reason': None,
            'rent_id': 'record_id',
            'termination_reason': 'Terminated by park, uid=terminator',
            'title': None,
            'transfer_order_number': 'park_id_1',
            'use_arbitrary_entries': False,
            'use_event_queue': True,
            'version': 2,
            'start_clid': None,
        },
    ]
