import datetime as dt
import json
from typing import Any
from typing import Dict

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import scheduled_slots_tools


def _make_insert_reservation_for_cache(
        slot_name: str,
        mode: str,
        mode_settings: Dict[str, Any],
        park_id: str,
        driver_id: str,
        created_at: dt.datetime,
        updated_ts: dt.datetime,
        increment: int,
        is_deleted: bool,
):
    slot_query = f"""
        SELECT id FROM booking.scheduled_slots
        WHERE name =  '{slot_name}'
        AND mode = '{mode}'
        """
    return f"""
        WITH slot AS ({slot_query})
        INSERT INTO booking.scheduled_slots_reservations
        (slot_id, park_id, driver_id, accepted_mode_settings,
        created_at, is_deleted, updated_ts, increment)
        VALUES ((SELECT id FROM slot),
        '{park_id}', '{driver_id}', '{json.dumps(mode_settings)}',
        '{created_at}', '{is_deleted}',
        '{updated_ts}', '{increment}')
        """


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_slot_quota_query(
            '0ea9b01927df4b73bd98bd25d8789daa',
            'some_mode',
            {'slot_id': '0ea9b01927df4b73bd98bd25d8789daa', 'rule_version': 5},
            dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
            'some_quota',
            1,
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            'a69bed5a215244168f190c5ad935be37',
            'some_mode',
            {'slot_id': 'a69bed5a215244168f190c5ad935be37', 'rule_version': 6},
            dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
            'some_quota2',
            1,
        ),
        _make_insert_reservation_for_cache(
            'a69bed5a215244168f190c5ad935be37',
            'some_mode',
            {'slot_id': '0ea9b01927df4b73bd98bd25d8789daa', 'rule_version': 1},
            'parkid0',
            'driverid0',
            created_at=dt.datetime(2021, 2, 4, 3, 1, tzinfo=dt.timezone.utc),
            updated_ts=dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            increment=1,
            is_deleted=False,
        ),
        _make_insert_reservation_for_cache(
            'a69bed5a215244168f190c5ad935be37',
            'some_mode',
            {'slot_id': 'a69bed5a215244168f190c5ad935be37', 'rule_version': 1},
            'parkid0',
            'driverid0',
            created_at=dt.datetime(2021, 2, 4, 3, 2, tzinfo=dt.timezone.utc),
            updated_ts=dt.datetime(2021, 2, 4, 4, 2, tzinfo=dt.timezone.utc),
            increment=2,
            is_deleted=True,
        ),
        _make_insert_reservation_for_cache(
            '0ea9b01927df4b73bd98bd25d8789daa',
            'some_mode',
            {'slot_id': 'a69bed5a215244168f190c5ad935be37', 'rule_version': 2},
            'parkid1',
            'driverid1',
            created_at=dt.datetime(2021, 2, 4, 3, 3, tzinfo=dt.timezone.utc),
            updated_ts=dt.datetime(2021, 2, 4, 4, 3, tzinfo=dt.timezone.utc),
            increment=3,
            is_deleted=False,
        ),
    ],
)
@pytest.mark.now('2021-02-04T04:05:00+00:00')
async def test_logistic_workshifts_slots_cache_smoke(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
):
    await taxi_driver_mode_subscription.invalidate_caches(
        clean_update=True,
        cache_names=['logistic-workshifts-slots-reservations-cache'],
    )

    response = await taxi_driver_mode_subscription.post(
        '/v1/logistic-workshifts/slots/reservation-updates',
        params={'consumer': 'test'},
        json={'only_checked_documents': False},
        headers={'X-Ya-Service-Ticket': common.MOCK_TICKET},
    )
    assert response.status_code == 200
    actual_response = response.json()

    # this field does not use mocked time
    actual_response.pop('cache_lag')

    assert actual_response == {
        'last_modified': '2021-02-04T04:03:00Z',
        'last_revision': '2021-02-04T04:03:00+0000_3',
        'logistic_workshifts_slots_reservations': [
            {
                'data': {
                    'driver_id': 'driverid0',
                    'offer_identity': {
                        'rule_version': '1',
                        'slot_id': '0ea9b01927df4b73bd98bd25d8789daa',
                    },
                    'park_id': 'parkid0',
                    'reservation_date': '2021-02-04T03:01:00.000',
                },
                'id': '1',
                'revision': '2021-02-04T04:01:00+0000_1',
            },
            {
                'data': {
                    'driver_id': 'driverid0',
                    'offer_identity': {
                        'rule_version': '1',
                        'slot_id': 'a69bed5a215244168f190c5ad935be37',
                    },
                    'park_id': 'parkid0',
                    'reservation_date': '2021-02-04T03:02:00.000',
                },
                'id': '2',
                'revision': '2021-02-04T04:02:00+0000_2',
                'is_deleted': True,
            },
            {
                'data': {
                    'driver_id': 'driverid1',
                    'offer_identity': {
                        'rule_version': '2',
                        'slot_id': 'a69bed5a215244168f190c5ad935be37',
                    },
                    'park_id': 'parkid1',
                    'reservation_date': '2021-02-04T03:03:00.000',
                },
                'id': '3',
                'revision': '2021-02-04T04:03:00+0000_3',
            },
        ],
    }
