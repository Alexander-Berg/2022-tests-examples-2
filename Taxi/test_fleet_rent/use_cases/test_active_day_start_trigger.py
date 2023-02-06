import datetime

import pytest

from fleet_rent.generated.stq3 import stq_context as context_module


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_base(stq3_context: context_module.Context, patch):
    order_at = datetime.datetime(2020, 1, 1, 12, tzinfo=datetime.timezone.utc)

    @patch(
        'fleet_rent.components.charging_event_scheduler.'
        'ChargingEventScheduler.schedule_triggered_active_day',
    )
    async def _schedule(rent, trigger, event_at):
        assert rent.record_id == 'record_id'
        assert trigger.event_number == 1
        assert event_at == order_at

    use_case = stq3_context.use_cases.active_day_start_trigger

    await use_case.process_finished_order(
        park_id='park_id',
        driver_id='driver_id',
        order_at=order_at,
        order_id='alias_id',
    )

    record = await stq3_context.pg.master.fetchrow(
        'SELECT * FROM rent.active_day_start_triggers',
    )
    assert record['triggered_at'] == order_at
    assert record['order_id'] == 'alias_id'


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_fail_fast_check(stq3_context: context_module.Context, patch):
    # Time outside range
    order_at = datetime.datetime(2020, 2, 1, 12, tzinfo=datetime.timezone.utc)

    @patch(
        'fleet_rent.pg_access.rent_charging_events.'
        'EventQueueAccessor.get_rent_active_day_triggers',
    )
    async def get(*args, **kwargs):
        raise Exception('Should not happen')

    use_case = stq3_context.use_cases.active_day_start_trigger

    await use_case.process_finished_order(
        park_id='park_id',
        driver_id='driver_id',
        order_at=order_at,
        order_id='alias_id',
    )

    assert not get.calls
