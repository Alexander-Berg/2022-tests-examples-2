import datetime
import decimal

import pytest

from fleet_rent.entities import park_billing as park_billing_ent
from fleet_rent.generated.stq3 import stq_context as context_module
from fleet_rent.services import billing_orders
from fleet_rent.services import fleet_transactions_api


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
 'creator_uid', '2020-01-01+00');
INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz,
 transfer_order_number)
VALUES ('rent_id', 'idempotency_token',
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 'affiliation_id',
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_1');
INSERT INTO rent.rent_history
(rent_id, version,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at, ends_at,
 charging_type,
 charging_params,
 charging_starts_at,
 creator_uid, created_at,
 modified_at,
 accepted_at,
 transfer_order_number,
 modification_source,
 use_event_queue,
 use_arbitrary_entries)
VALUES ('rent_id', 1,
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 'affiliation_id',
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00','2020-01-01+00',
 '2020-01-01+00',
 'park_id_1', '{"kind": "driver"}', TRUE, TRUE);
INSERT INTO rent.event_queue
(rent_id, event_number, event_at)
VALUES ('rent_id', 1, '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-01T16:00+00:00')
async def test_process_external(
        stq3_context: context_module.Context, patch, mock_load_park_info, stq,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        assert park_id == 'park_id'
        return 'RUB'

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_owner_billing_info',
    )
    async def _get_owner_billing_info(park_id, actual_at):
        assert park_id == 'park_id'
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='100500',
            billing_client_id='bcli',
            billing_contract_id='bcoi',
        )

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_driver_billing_info',
    )
    async def _get_driver_billing_info(park_id, actual_at):
        assert park_id == 'driver_park_id'
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='1337',
            billing_client_id='bcli2',
            billing_contract_id='bcoi2',
        )

    @patch(
        'fleet_rent.services.billing_orders.'
        'BillingOrdersService.send_transactions_external',
    )
    async def _send(transactions):
        assert len(transactions) == 1
        assert transactions[0] == billing_orders.ExternalTransactionData(
            rent_id='rent_id',
            amount=decimal.Decimal('100'),
            park_id='park_id',
            local_driver_id='driver_id',
            external_park_id='driver_park_id',
            external_driver_id='driver_id',
            scheduled_at=datetime.datetime(
                2020, 1, 1, tzinfo=datetime.timezone.utc,
            ),
            event_at=datetime.datetime(
                2020, 1, 1, 16, tzinfo=datetime.timezone.utc,
            ),
            event_number=1,
            transfer_order_number='park_id_1',
            park_clid='100500',
            park_currency='RUB',
            park_billing_client_id='bcli',
            park_billing_contract_id='bcoi',
            driver_clid='1337',
            driver_billing_client_id='bcli2',
            driver_billing_contract_id='bcoi2',
        )

    use_case = stq3_context.use_cases.charging_event_processing

    await use_case.process(rent_id='rent_id', event_number=1)

    rows = await stq3_context.pg.slave.fetch(
        """SELECT * FROM rent.event_queue
         WHERE rent_id = 'rent_id' ORDER BY event_number""",
    )
    events_state = [dict(x) for x in rows]
    assert events_state[0].pop('executed_at')
    for elem in events_state:
        assert elem.pop('modified_at')
    assert events_state == [
        {
            'event_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 1,
            'rent_id': 'rent_id',
        },
        {
            'event_at': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 2,
            'executed_at': None,
            'rent_id': 'rent_id',
        },
    ]
    assert stq.fleet_rent_process_charging_event.has_calls


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
 'creator_uid', '2020-01-01+00');
INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at_tz, ends_at_tz,
 charging_type,
 charging_params,
 charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz,
 transfer_order_number)
VALUES ('rent_id', 'idempotency_token',
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 'affiliation_id',
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null}}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_1');
INSERT INTO rent.rent_history
(rent_id, version,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at, ends_at,
 charging_type,
 charging_params,
 charging_starts_at,
 creator_uid, created_at,
 modified_at,
 accepted_at,
 transfer_order_number,
 modification_source,
 use_event_queue,
 use_arbitrary_entries,
 start_clid)
VALUES ('rent_id', 1,
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 'affiliation_id',
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null}}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00','2020-01-01+00',
 '2020-01-01+00',
 'park_id_1', '{"kind": "driver"}', TRUE, TRUE, 'old_clid');
INSERT INTO rent.event_queue
(rent_id, event_number, event_at)
VALUES ('rent_id', 1, '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-01T16:00+00:00')
async def test_process_external_clid_change(
        stq3_context: context_module.Context, patch, mock_load_park_info, stq,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        assert park_id == 'park_id'
        return 'RUB'

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_owner_billing_info',
    )
    async def _get_owner_billing_info(park_id, actual_at):
        assert park_id == 'park_id'
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='100500',
            billing_client_id='bcli',
            billing_contract_id='bcoi',
        )

    @patch(
        'fleet_rent.components.park_billing_info.'
        'ParkBillingInfo.get_driver_billing_info',
    )
    async def _get_driver_billing_info(park_id, actual_at):
        assert park_id == 'driver_park_id'
        return park_billing_ent.ParkBillingInfo(
            id=park_id,
            clid='1337',
            billing_client_id='bcli2',
            billing_contract_id='bcoi2',
        )

    @patch(
        'fleet_rent.services.billing_orders.'
        'BillingOrdersService.send_transactions_external',
    )
    async def _send(transactions):
        assert False, 'Must not be called'

    use_case = stq3_context.use_cases.charging_event_processing
    try:
        await use_case.process(rent_id='rent_id', event_number=1)
    except Exception:  # pylint: disable=broad-except
        pass

    rows = await stq3_context.pg.slave.fetch(
        """SELECT * FROM rent.event_queue
         WHERE rent_id = 'rent_id' ORDER BY event_number""",
    )
    events_state = [dict(x) for x in rows]
    for elem in events_state:
        assert elem.pop('modified_at')
    assert events_state == [
        {
            'event_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 1,
            'executed_at': None,
            'rent_id': 'rent_id',
        },
    ]
    assert not stq.fleet_rent_process_charging_event.has_calls


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
 transfer_order_number,
 use_arbitrary_entries)
VALUES ('rent_id', 'idempotency_token',
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_1',
 TRUE);
INSERT INTO rent.rent_history
(rent_id, version,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at, ends_at,
 charging_type,
 charging_params,
 charging_starts_at,
 creator_uid, created_at,
 modified_at,
 accepted_at,
 transfer_order_number,
 modification_source,
 use_event_queue,
 use_arbitrary_entries)
VALUES ('rent_id', 1,
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id', NULL,
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00', '2020-01-01+00',
 'park_id_1', '{"kind": "driver"}', TRUE, TRUE);
INSERT INTO rent.event_queue
(rent_id, event_number, event_at)
VALUES ('rent_id', 1, '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-02T00:00+00:00')
async def test_process_internal_bo(
        stq3_context: context_module.Context, patch, mock_load_park_info, stq,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_internal_currency',
    )
    async def _get_park_internal_currency(park_id: str, now):
        return 'RUB'

    @patch(
        'fleet_rent.services.billing_orders.'
        'BillingOrdersService.send_transactions_internal',
    )
    async def _send(transactions):
        assert len(transactions) == 1
        assert transactions[0] == billing_orders.InternalTransactionData(
            rent_id='rent_id',
            rent_serial_id=1,
            park_id='park_id',
            driver_id='driver_id',
            scheduled_at=datetime.datetime(
                2020, 1, 1, tzinfo=datetime.timezone.utc,
            ),
            event_at=datetime.datetime.fromisoformat('2020-01-02T00:00+00:00'),
            trans_serial_id=1,
            amount=decimal.Decimal('100'),
            currency='RUB',
            transfer_order_number='park_id_1',
            alias_id=None,
        )

    use_case = stq3_context.use_cases.charging_event_processing

    await use_case.process(rent_id='rent_id', event_number=1)

    rows = await stq3_context.pg.slave.fetch(
        """SELECT * FROM rent.event_queue
         WHERE rent_id = 'rent_id' ORDER BY event_number""",
    )
    events_state = [dict(x) for x in rows]
    assert events_state[0].pop('executed_at')
    for elem in events_state:
        assert elem.pop('modified_at')
    assert events_state == [
        {
            'event_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 1,
            'rent_id': 'rent_id',
        },
        {
            'event_at': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 2,
            'executed_at': None,
            'rent_id': 'rent_id',
        },
    ]
    assert stq.fleet_rent_process_charging_event.has_calls


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
 transfer_order_number,
 use_arbitrary_entries)
VALUES ('rent_id', 'idempotency_token',
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 '2020-01-01+00', '2020-01-31+00',
 'active_days',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_1',
 TRUE);
INSERT INTO rent.event_queue
(rent_id, event_number, event_at)
VALUES ('rent_id', 1, '2020-01-01+00');

INSERT INTO rent.active_day_start_triggers
(rent_id, event_number, lower_datetime_bound, upper_datetime_bound,
triggered_at, order_id, park_id, driver_id)
VALUES
('rent_id', 1, '2020-01-10T00:00+00:00', NULL, '2020-01-01+00', 'some_alias',
'park_id', 'driver_id');
INSERT INTO rent.rent_history
(rent_id, version,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at, ends_at,
 charging_type,
 charging_params,
 charging_starts_at,
 creator_uid, created_at,
 modified_at,
 accepted_at,
 transfer_order_number,
 modification_source,
 use_event_queue,
 use_arbitrary_entries)
VALUES ('rent_id', 1,
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id', NULL,
 '2020-01-01+00', '2020-01-31+00',
 'active_days',
 '{"daily_price": "100"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00', '2020-01-01+00',
 'park_id_1', '{"kind": "driver"}', TRUE, TRUE);
""",
    ],
)
@pytest.mark.now('2020-01-02T00:00+00:00')
async def test_process_internal_bo_with_activity_rent(
        stq3_context: context_module.Context, patch, mock_load_park_info, stq,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_internal_currency',
    )
    async def _get_park_internal_currency(park_id: str, now):
        return 'RUB'

    @patch(
        'fleet_rent.services.billing_orders.'
        'BillingOrdersService.send_transactions_internal',
    )
    async def _send(transactions):
        assert len(transactions) == 1
        assert transactions[0] == billing_orders.InternalTransactionData(
            rent_id='rent_id',
            rent_serial_id=1,
            park_id='park_id',
            driver_id='driver_id',
            scheduled_at=datetime.datetime(
                2020, 1, 1, tzinfo=datetime.timezone.utc,
            ),
            event_at=datetime.datetime.fromisoformat('2020-01-02T00:00+00:00'),
            trans_serial_id=1,
            amount=decimal.Decimal('100'),
            currency='RUB',
            transfer_order_number='park_id_1',
            alias_id='some_alias',
        )

    use_case = stq3_context.use_cases.charging_event_processing

    await use_case.process(rent_id='rent_id', event_number=1)

    rows = await stq3_context.pg.slave.fetch(
        """SELECT * FROM rent.event_queue
         WHERE rent_id = 'rent_id' ORDER BY event_number""",
    )
    events_state = [dict(x) for x in rows]
    assert events_state[0].pop('executed_at')
    for elem in events_state:
        assert elem.pop('modified_at')
    assert events_state == [
        {
            'event_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 1,
            'rent_id': 'rent_id',
        },
    ]
    assert not stq.fleet_rent_process_charging_event.has_calls

    rows = await stq3_context.pg.slave.fetch(
        """SELECT * FROM rent.active_day_start_triggers
         WHERE rent_id = 'rent_id' ORDER BY event_number""",
    )
    events_state = [dict(x) for x in rows]
    for elem in events_state:
        assert elem.pop('modified_at')
    assert events_state == [
        {
            'driver_id': 'driver_id',
            'event_number': 1,
            'lower_datetime_bound': datetime.datetime(
                2020, 1, 10, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'order_id': 'some_alias',
            'park_id': 'park_id',
            'rent_id': 'rent_id',
            'triggered_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'upper_datetime_bound': None,
        },
        {
            'driver_id': 'driver_id',
            'event_number': 2,
            'lower_datetime_bound': datetime.datetime(
                2020, 1, 1, 21, 0, tzinfo=datetime.timezone.utc,
            ),
            'order_id': None,
            'park_id': 'park_id',
            'rent_id': 'rent_id',
            'triggered_at': None,
            'upper_datetime_bound': datetime.datetime(
                2020, 1, 31, 0, 0, tzinfo=datetime.timezone.utc,
            ),
        },
    ]


@pytest.mark.now('2020-01-01T12:00+00:00')
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
VALUES ('rent_id', 'idempotency_token',
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_1');
INSERT INTO rent.event_queue
(rent_id, event_number, event_at)
VALUES ('rent_id', 1, '2020-01-01+00');

INSERT INTO rent.rent_history
(rent_id, version,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at, ends_at,
 charging_type,
 charging_params,
 charging_starts_at,
 creator_uid, created_at,
 modified_at,
 accepted_at,
 transfer_order_number,
 modification_source,
 use_event_queue,
 use_arbitrary_entries)
VALUES ('rent_id', 1,
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id', NULL,
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00', '2020-01-01+00',
 'park_id_1', '{"kind": "driver"}', TRUE, FALSE);
        """,
    ],
)
async def test_process_internal_fta(
        stq3_context: context_module.Context, patch, mock_load_park_info, stq,
):
    @patch('fleet_rent.services.fleet_transactions_api.FTAService.send')
    async def _send(transaction):
        assert transaction == fleet_transactions_api.TransactionData(
            rent_id='rent_id',
            park_id='park_id',
            driver_id='driver_id',
            amount=decimal.Decimal('100'),
            title=None,
            rent_serial_id=1,
            event_at=datetime.datetime(
                2020, 1, 1, tzinfo=datetime.timezone.utc,
            ),
            event_number=1,
        )

    use_case = stq3_context.use_cases.charging_event_processing

    await use_case.process(rent_id='rent_id', event_number=1)

    rows = await stq3_context.pg.slave.fetch(
        """SELECT * FROM rent.event_queue
        WHERE rent_id = 'rent_id' ORDER BY event_number""",
    )
    events_state = [dict(x) for x in rows]
    assert events_state[0].pop('executed_at')
    for elem in events_state:
        assert elem.pop('modified_at')
    assert events_state == [
        {
            'event_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 1,
            'rent_id': 'rent_id',
        },
        {
            'event_at': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 2,
            'executed_at': None,
            'rent_id': 'rent_id',
        },
    ]
    assert stq.fleet_rent_process_charging_event.has_calls


@pytest.mark.now('2020-01-03T12:00+00:00')
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
VALUES ('rent_id', 'idempotency_token',
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_1');
INSERT INTO rent.event_queue
(rent_id, event_number, event_at)
VALUES ('rent_id', 1, '2020-01-01+00');
INSERT INTO rent.rent_history
(rent_id, version,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at, ends_at,
 charging_type,
 charging_params,
 charging_starts_at,
 creator_uid, created_at,
 modified_at,
 accepted_at,
 transfer_order_number,
 modification_source,
 use_event_queue,
 use_arbitrary_entries)
VALUES ('rent_id', 1,
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id', NULL,
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00', '2020-01-01+00',
 'park_id_1', '{"kind": "driver"}', TRUE, FALSE);
        """,
    ],
)
async def test_process_internal_fta_event_at_fix(
        stq3_context: context_module.Context, patch, mock_load_park_info, stq,
):
    @patch('fleet_rent.services.fleet_transactions_api.FTAService.send')
    async def _send(transaction):
        assert transaction == fleet_transactions_api.TransactionData(
            rent_id='rent_id',
            park_id='park_id',
            driver_id='driver_id',
            amount=decimal.Decimal('100'),
            title=None,
            rent_serial_id=1,
            event_at=datetime.datetime(
                year=2020,
                month=1,
                day=3,
                hour=12,
                tzinfo=datetime.timezone.utc,
            ),
            event_number=1,
        )

    use_case = stq3_context.use_cases.charging_event_processing

    await use_case.process(rent_id='rent_id', event_number=1)

    rows = await stq3_context.pg.slave.fetch(
        """SELECT * FROM rent.event_queue
         WHERE rent_id = 'rent_id' ORDER BY event_number""",
    )
    events_state = [dict(x) for x in rows]
    assert events_state[0].pop('executed_at')
    for elem in events_state:
        assert elem.pop('modified_at')
    assert events_state == [
        {
            'event_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 1,
            'rent_id': 'rent_id',
        },
        {
            'event_at': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'event_number': 2,
            'executed_at': None,
            'rent_id': 'rent_id',
        },
    ]
    assert stq.fleet_rent_process_charging_event.has_calls


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
VALUES ('rent_id', 'idempotency_token',
 'park_id', 1, 'other', '{"subtype": "misc"}',
 'driver_id',
 '2020-01-01+00', '2020-01-31+00',
 'daily',
 '{"daily_price": "100", "periodicity": {"type": "constant", "params": null},
   "time": "03:00:00"}',
 '2020-01-01+00',
 'creator_uid', '2020-01-01+00',
 '2020-01-01+00',
 'park_id_1');
INSERT INTO rent.event_queue
(rent_id, event_number, event_at)
VALUES ('rent_id', 1, '2020-01-01+00'),
 ('rent_id', 2, '2020-01-02+00'),
 ('rent_id', 3, '2020-01-03+00'),
 ('rent_id', 4, '2020-01-04+00'),
 ('rent_id', 5, '2020-01-05+00');
UPDATE rent.event_queue SET executed_at = NOW()
WHERE rent_id = 'rent_id' AND event_number = 1;
        """,
    ],
)
@pytest.mark.now('2020-01-04T10:00+00:00')
async def test_process_stuck(stq3_context: context_module.Context, patch):
    @patch(
        'fleet_rent.use_cases.charging_event_processing.'
        'ChargingEventProcessing.process',
    )
    async def _process(rent_id, event_number):
        pass

    use_case = stq3_context.use_cases.charging_event_processing

    await use_case.process_stuck()

    calls = [(d['rent_id'], d['event_number']) for d in _process.calls]

    assert calls == [('rent_id', 2), ('rent_id', 3), ('rent_id', 4)]
