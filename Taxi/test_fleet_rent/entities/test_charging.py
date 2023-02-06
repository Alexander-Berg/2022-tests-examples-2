import datetime as dt
import decimal

import pytest

from fleet_rent.entities import charging as charging_entities
from fleet_rent.entities import charging_event as ce_entities
from fleet_rent.entities import daily_periodicity as periodicity


@pytest.mark.parametrize(
    'daily_price, limit, full_tries, is_full_finished',
    [(4, 5, 1, False), (4, 3, 0, False), (4, 10, 2, False), (4, 8, 2, True)],
)
def test_charging_amounts_deposit(
        daily_price, limit, full_tries, is_full_finished,
):
    charging = charging_entities.ChargingDaily(
        daily_price=decimal.Decimal(daily_price),
        total_withhold_limit=decimal.Decimal(limit),
        periodicity=periodicity.DailyPeriodicityConstant(),
        starts_at=dt.datetime.fromisoformat('2020-10-10T00:00+00:00'),
        finishes_at=dt.datetime.fromisoformat('2020-12-10T00:00+00:00'),
        time=dt.time(0, 0),
    )

    event = charging.get_next_event(dt.timezone.utc)
    for i in range(full_tries):
        assert event is not None
        assert event.event_number == i + 1
        assert charging.get_charging_amount(event) == decimal.Decimal(
            daily_price,
        )
        assert charging.get_charging_amount(event) == decimal.Decimal(
            daily_price,
        )

        event = charging.get_next_event(dt.timezone.utc, event)

    if is_full_finished:
        assert event is None
        return

    assert event is not None
    assert event.event_number == full_tries + 1
    assert charging.get_charging_amount(event) == decimal.Decimal(
        limit % daily_price,
    )
    assert charging.get_charging_amount(event) == decimal.Decimal(
        limit % daily_price,
    )

    assert charging.get_next_event(dt.timezone.utc, event) is None
    assert charging.get_next_event(dt.timezone.utc, event) is None


@pytest.mark.parametrize(
    'daily_price, limit, full_tries, is_full_finished',
    [(4, 5, 1, False), (4, 3, 0, False), (4, 10, 2, False), (4, 8, 2, True)],
)
def test_charging_amounts_deposit_activity(
        daily_price, limit, full_tries, is_full_finished,
):
    charging = charging_entities.ChargingActiveDays(
        daily_price=decimal.Decimal(daily_price),
        total_withhold_limit=decimal.Decimal(limit),
        starts_at=dt.datetime.fromisoformat('2020-10-10T00:00+00:00'),
        finishes_at=dt.datetime.fromisoformat('2020-12-10T00:00+00:00'),
    )

    trigger = charging.get_next_event_trigger(dt.timezone.utc)
    for i in range(full_tries):
        assert trigger is not None
        assert trigger.event_number == i + 1
        event = trigger.to_timed(
            dt.datetime(2020, 11, 10, tzinfo=dt.timezone.utc),
        )
        assert charging.get_charging_amount(event) == decimal.Decimal(
            daily_price,
        )
        assert charging.get_charging_amount(event) == decimal.Decimal(
            daily_price,
        )

        trigger = charging.get_next_event_trigger(dt.timezone.utc, event)

    if is_full_finished:
        assert trigger is None
        return

    assert trigger is not None
    assert trigger.event_number == full_tries + 1
    event = trigger.to_timed(dt.datetime(2020, 11, 10, tzinfo=dt.timezone.utc))
    assert charging.get_charging_amount(event) == decimal.Decimal(
        limit % daily_price,
    )
    assert charging.get_charging_amount(event) == decimal.Decimal(
        limit % daily_price,
    )

    assert charging.get_next_event_trigger(dt.timezone.utc, event) is None
    assert charging.get_next_event_trigger(dt.timezone.utc, event) is None


def test_charging_daily_change_time():
    park_tz = dt.timezone(offset=dt.timedelta(hours=5))
    charging = charging_entities.ChargingDaily(
        daily_price=decimal.Decimal(10),
        total_withhold_limit=None,
        periodicity=periodicity.DailyPeriodicityConstant(),
        starts_at=dt.datetime.fromisoformat('2020-10-10T00:00+00:00'),
        finishes_at=dt.datetime.fromisoformat('2020-12-10T00:00+00:00'),
        time=None,
    )

    event = charging.get_next_event_from_prev(park_tz, None)
    assert isinstance(event, ce_entities.TimeEvent)
    assert event.event_at.time() == dt.time(hour=5)
    assert event.event_at.date() == dt.date(year=2020, month=10, day=10)
    assert event.event_at.tzinfo == park_tz
    for hour in [11, 6, 17, 18]:
        charging = charging_entities.ChargingDaily(
            daily_price=decimal.Decimal(10),
            total_withhold_limit=None,
            periodicity=periodicity.DailyPeriodicityConstant(),
            starts_at=dt.datetime.fromisoformat('2020-10-10T00:00+00:00'),
            finishes_at=dt.datetime.fromisoformat('2020-12-10T00:00+00:00'),
            time=dt.time(hour=hour),
        )
        next_event = charging.get_next_event_from_prev(park_tz, event)
        assert next_event is not None
        assert isinstance(next_event, ce_entities.TimeEvent)
        assert next_event.event_number == event.event_number + 1
        assert (
            next_event.event_at.date() - event.event_at.date()
            == dt.timedelta(days=1)
        )
        assert next_event.event_at.time().hour == hour
        assert next_event.event_at.tzinfo == park_tz
        event = next_event


@pytest.mark.parametrize(
    'daily_price, limit, full_tries, is_full_finished',
    [(4, 5, 1, False), (4, 3, 0, False), (4, 10, 2, False), (4, 8, 2, True)],
)
def test_charging_amounts_deposit_inh(
        daily_price, limit, full_tries, is_full_finished,
):
    charging = charging_entities.ChargingDaily(
        daily_price=decimal.Decimal(daily_price),
        total_withhold_limit=decimal.Decimal(limit),
        periodicity=periodicity.DailyPeriodicityConstant(),
        starts_at=dt.datetime.fromisoformat('2020-10-10T00:00+00:00'),
        finishes_at=dt.datetime.fromisoformat('2020-12-10T00:00+00:00'),
        time=dt.time(0, 0),
    )

    event = charging.get_next_event_from_prev(dt.timezone.utc, None)
    assert isinstance(event, ce_entities.TimeEvent)
    for i in range(full_tries):
        assert event is not None
        assert isinstance(event, ce_entities.TimeEvent)
        assert event.event_number == i + 1
        assert charging.get_charging_amount(event) == decimal.Decimal(
            daily_price,
        )
        assert charging.get_charging_amount(event) == decimal.Decimal(
            daily_price,
        )

        event = charging.get_next_event_from_prev(dt.timezone.utc, event)

    if is_full_finished:
        assert event is None
        return

    assert event is not None
    assert isinstance(event, ce_entities.TimeEvent)
    assert event.event_number == full_tries + 1
    assert charging.get_charging_amount(event) == decimal.Decimal(
        limit % daily_price,
    )
    assert charging.get_charging_amount(event) == decimal.Decimal(
        limit % daily_price,
    )

    assert charging.get_next_event_from_prev(dt.timezone.utc, event) is None
    assert charging.get_next_event_from_prev(dt.timezone.utc, event) is None


@pytest.mark.parametrize(
    'daily_price, limit, full_tries, is_full_finished',
    [(4, 5, 1, False), (4, 3, 0, False), (4, 10, 2, False), (4, 8, 2, True)],
)
def test_charging_amounts_deposit_activity_inh(
        daily_price, limit, full_tries, is_full_finished,
):
    charging = charging_entities.ChargingActiveDays(
        daily_price=decimal.Decimal(daily_price),
        total_withhold_limit=decimal.Decimal(limit),
        starts_at=dt.datetime.fromisoformat('2020-10-10T00:00+00:00'),
        finishes_at=dt.datetime.fromisoformat('2020-12-10T00:00+00:00'),
    )

    trigger = charging.get_next_event_from_prev(dt.timezone.utc, None)
    assert isinstance(trigger, ce_entities.ShiftStartEventTrigger)
    for i in range(full_tries):
        assert trigger is not None
        assert isinstance(trigger, ce_entities.ShiftStartEventTrigger)
        assert trigger.event_number == i + 1
        event = trigger.to_timed(
            dt.datetime(2020, 11, 10, tzinfo=dt.timezone.utc),
        )
        assert charging.get_charging_amount(event) == decimal.Decimal(
            daily_price,
        )
        assert charging.get_charging_amount(event) == decimal.Decimal(
            daily_price,
        )

        trigger = charging.get_next_event_from_prev(dt.timezone.utc, event)

    if is_full_finished:
        assert trigger is None
        return

    assert trigger is not None
    assert isinstance(trigger, ce_entities.ShiftStartEventTrigger)
    assert trigger.event_number == full_tries + 1
    event = trigger.to_timed(dt.datetime(2020, 11, 10, tzinfo=dt.timezone.utc))
    assert charging.get_charging_amount(event) == decimal.Decimal(
        limit % daily_price,
    )
    assert charging.get_charging_amount(event) == decimal.Decimal(
        limit % daily_price,
    )

    assert charging.get_next_event_from_prev(dt.timezone.utc, event) is None
    assert charging.get_next_event_from_prev(dt.timezone.utc, event) is None
