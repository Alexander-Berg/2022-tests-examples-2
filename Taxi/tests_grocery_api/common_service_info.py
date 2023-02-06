import datetime
import pytest

from . import const


def prepare_depots(
        overlord_catalog,
        location,
        grocery_depots,
        state='open',
        depot_id=const.DEPOT_ID,
        legacy_depot_id=const.LEGACY_DEPOT_ID,
        switch_time='2020-09-09T10:00:00+00:00',
        all_day=False,
        with_rover=False,
        address='depot address',
):
    overlord_catalog.clear()
    overlord_catalog.add_depot(
        depot_id=depot_id, legacy_depot_id=legacy_depot_id, address=address,
    )
    overlord_catalog.add_location(
        location=location,
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
        state=state,
        switch_time=switch_time,
        all_day=all_day,
        with_rover=with_rover,
    )
    overlord_catalog.set_depot_status(state)

    # TODO: add logic when switched to g-depot resolver in LAVKABACKEND-8255
    switch_datetime = datetime.datetime.fromisoformat(switch_time)
    timetable = [
        {
            'day_type': 'Everyday',
            'working_hours': {
                'from': {
                    'hour': switch_datetime.hour,
                    'minute': switch_datetime.minute,
                },
                'to': {
                    'hour': switch_datetime.hour,
                    'minute': switch_datetime.minute,
                },
            },
        },
    ]
    if state == 'open':
        state = 'active'
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        location=location,
        address=address,
        status=state,
        timetable=timetable,
    )


def set_surge_conditions(experiments3, delivery_conditions=None):
    value = {
        'data': [
            {
                'payload': {'delivery_conditions': delivery_conditions},
                'timetable': [
                    {'to': '24:00', 'from': '00:00', 'day_type': 'everyday'},
                ],
            },
        ],
        'enabled': True,
    }

    experiments3.add_config(
        name='grocery-surge-delivery-conditions',
        consumers=['grocery-surge-client/surge'],
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
    )


def get_rounding_rules(format_precision, rounding_precision):
    return pytest.mark.config(
        CURRENCY_FORMATTING_RULES={
            'RUB': {'__default__': 1, 'grocery': format_precision},
        },
        CURRENCY_ROUNDING_RULES={
            'RUB': {'__default__': 1, 'grocery': rounding_precision},
            '__default__': {'__default__': 0.01, 'grocery': 0.01},
        },
    )
