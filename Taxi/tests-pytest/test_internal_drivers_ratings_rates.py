# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import pytest

from taxi.internal import dbh
from taxi.internal.drivers_ratings import rates
from taxi.internal.order_kit.plg import order_fsm

TEST_ORDER_ID = 'test_order_id'
TEST_ORDER_ALIAS_ID = 'test_order_alias_id'
TEST_CITY_ID = 'test_city_id'
TEST_ZONE = 'test_nearest_zone'
TEST_DRIVER_ID = 'test_driver_id'
TEST_LICENSE = 'test_license'
TEST_DRIVER_EVENT_ID = 'test_driver_event_id'
TEST_UNIQUE_DRIVER_ID = 'test_unique_driver_id'
TEST_DB_ID = 'test_db_id'

DEFAULT = '__default__'
SPB = 'spb'
ADDRESS = 'Any address'
LOCATION = [37.0, 52.0]
PRICE = 400.4


class FakeOrderFsm(order_fsm.OrderFsm):
    def __init__(self, proc):
        super(FakeOrderFsm, self).__init__(proc)
        self.event_index = len(proc.order_info.statistics.status_updates) - 1


@pytest.mark.now('2016-09-01T13:00:00.0')
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'status_updates,driverrequest,chain_parent,'
    'expected_field,due_time,driver_exps', [
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'i': 3, 'q': 'reject', 'r': 'manual'},
    ],
     False, False, None, None,
     []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'i': 3, 'q': 'reject'},
    ], False, True, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'i': 3, 'q': 'reject', 'r': 'autocancel'},
    ], False, False, None, None, []),

    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'i': 3, 'q': 'offer_timeout'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'i': 3, 'q': 'offer_timeout'},
    ], False, True, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 2},
        {'q': 'reject'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 2},
        {'q': 'reject'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 2},
        {'q': 'reject'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 3},
        {'q': 'reject'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 2},
        {'q': 'reject'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 3},
        {'q': 'reject'},
        {'q': 'seen', 'i': 1},
        {'q': 'reject'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 2},
        {'q': 'reject'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 3},
        {'q': 'reject'},
        {'q': 'seen', 'i': 1},
        {'q': 'reject'},
        {'q': 'seen', 'i': 1},
        {'q': 'reject'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 2},
        {'q': 'reject'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 3},
        {'q': 'reject'},
        {'q': 'seen', 'i': 1},
        {'q': 'reject'},
        {'q': 'seen', 'i': 1},
        {'q': 'reject'},
        {'q': 'seen', 'i': 1},
        {'q': 'offer_timeout'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 2},
        {'q': 'reject'},
        {'q': 'seen', 'i': 3},
        {'s': 'assigned', 'i': 3},
        {'s': 'pending', 'q': 'autoreorder'},
        {'q': 'seen', 'i': 3},
        {'q': 'reject'},
        {'q': 'seen', 'i': 1},
        {'q': 'reject'},
        {'q': 'seen', 'i': 1},
        {'q': 'reject'},
        {'q': 'seen', 'i': 1},
        {'q': 'offer_timeout'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'s': 'finished', rates.OFFER_TIMEOUT_FIELD: 'complete'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'s': 'finished', 't': 'cancelled'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'s': 'finished', 't': 'failed'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'s': 'cancelled'},
    ],
     True, False, None, None, []
    ),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'s': 'cancelled'},
    ],
     True, False, None, None, []
    ),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'s': 'cancelled'},
    ], False, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'cancelled'},
    ], True, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'s': 'cancelled'},
    ], True, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'t': 'waiting', 'c': datetime.datetime(2016, 9, 1)},
        {'s': 'finished', 't': 'cancelled',
         'c': datetime.datetime(2016, 9, 1, 0, 9)},
    ], True, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'t': 'waiting', 'c': datetime.datetime(2016, 9, 1)},
        {'s': 'finished', 't': 'cancelled',
         'c': datetime.datetime(2016, 9, 1, 0, 9)},
    ], True, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'t': 'waiting', 'c': datetime.datetime(2016, 9, 1)},
        {'s': 'finished', 't': 'cancelled',
         'c': datetime.datetime(2016, 9, 1, 0, 9)},
    ], True, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'t': 'waiting', 'c': datetime.datetime(2016, 9, 1)},
        {'s': 'finished', 't': 'cancelled',
         'c': datetime.datetime(2016, 9, 1, 0, 9)},
    ], True, False, None, None, []),
    ([
        {'s': 'pending', 'q': 'create'},
        {'q': 'seen', 'i': 0},
        {'s': 'assigned', 'i': 0},
        {'t': 'waiting', 'c': datetime.datetime(2016, 9, 1)},
        {'s': 'finished', 't': 'cancelled',
         'c': datetime.datetime(2016, 9, 1, 0, 11)},
    ], True, False, rates.LONG_WAITING_FIELD, None, []),
    ([
         {'s': 'pending', 'q': 'create'},
         {'q': 'seen', 'i': 0},
         {'s': 'assigned', 'i': 0},
         {'t': 'waiting', 'c': datetime.datetime(2016, 9, 1, 12, 47)},
         {'s': 'finished', 't': 'cancelled',
          'c': datetime.datetime(2016, 9, 1, 12, 56)},
     ], True, False, None, None, []),
    ([
         {'s': 'pending', 'q': 'create'},
         {'q': 'seen', 'i': 0},
         {'s': 'assigned', 'i': 0},
         {'t': 'waiting', 'c': datetime.datetime(2016, 9, 1, 12, 45)},
         {'s': 'finished', 't': 'cancelled',
          'c': datetime.datetime(2016, 9, 1, 12, 56)},
     ], True, False, None,
     datetime.datetime(2016, 9, 1, 12, 47), []),
    ([
         {'s': 'pending', 'q': 'create'},
         {'q': 'seen', 'i': 0},
         {'s': 'assigned', 'i': 0},
         {'t': 'waiting', 'c': datetime.datetime(2016, 9, 1, 12, 45)},
         {'s': 'finished', 't': 'cancelled',
          'c': datetime.datetime(2016, 9, 1, 12, 56)},
     ], True, False, rates.LONG_WAITING_FIELD,
     datetime.datetime(2016, 9, 1, 12, 46), []),
    ([
         {'s': 'pending', 'q': 'create'},
         {'q': 'seen', 'i': 0},
         {'s': 'assigned', 'i': 0},
         {'t': 'waiting', 'c': datetime.datetime(2016, 9, 1)},
         {'t': 'transporting', 'c': datetime.datetime(2016, 9, 1, 0, 11)},
         {'s': 'finished', 't': 'cancelled',
          'c': datetime.datetime(2016, 9, 1, 0, 11)},
         ], True, False, None, None, []),
])
def test_order_status_parser(
        status_updates, driverrequest, chain_parent,
        expected_field, due_time, driver_exps
):
    driver_lics = ['lic%d' % i for i in range(0, 4)]
    for su in status_updates:
        if 'c' not in su:
            su['c'] = datetime.datetime.utcnow()
    order_proc = dbh.order_proc.Doc({
        '_id': 'orderid',
        dbh.order_proc.Doc.candidates:
            [
                {
                    'driver_license': lic,
                    'cp': chain_parent,
                    'tariff_class': 'econom',
                } for lic in driver_lics
            ],
        dbh.order_proc.Doc.order_info: {
            'statistics': {
                'status_updates': status_updates,
            }
        },
        'order': {
            'experiments': ['direct_assignment'],
            'city': TEST_CITY_ID,
        }
    })

    if driverrequest:
        order_proc['order']['feedback'] = {
            'choices': {
                'cancelled_reason': ['driverrequest']
            },
            'status': 'finished',
            'taxi_status': 'complete',
        }

    if due_time is None:
        due_time = datetime.datetime(2016, 9, 1)

    candidate_alias_id = 1
    for candidate in order_proc.candidates:
        candidate.driver_experiments = driver_exps
        candidate.alias_id = str(candidate_alias_id)
        alias = order_proc.aliases.new()
        alias.due = due_time
        alias.id = str(candidate_alias_id)
        candidate_alias_id += 1

    waiting_time_rules = {DEFAULT: 10 * 60}
    state = FakeOrderFsm(proc=order_proc)
    field = rates.parse_order_status(
        state,
        waiting_time_rules,
    )
    assert field == expected_field
