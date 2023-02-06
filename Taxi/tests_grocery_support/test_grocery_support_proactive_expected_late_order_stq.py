import copy
from typing import Optional

import pytest

from . import consts


TICKET_QUEUE = 'LAVKA'

CREATE_ISSUE_HANDLER = 'issues'
ISSUES_COUNT_HANDLER = 'issues_count'


@pytest.fixture
def _run_stq(mockserver, stq_runner):
    async def _inner(
            order_id,
            order_status,
            ticket_queue=TICKET_QUEUE,
            ticket_tags=copy.deepcopy(consts.TICKET_TAGS),
            create_chatterbox_ticket=True,
            max_tickets_count=100,
            expect_fail: bool = False,
            exec_tries: Optional[int] = None,
    ):
        await stq_runner.grocery_support_proactive_expected_late_order.call(
            task_id=order_id,
            kwargs={
                'order_id': order_id,
                'order_status': order_status,
                'ticket_queue': ticket_queue,
                'ticket_tags': ticket_tags,
                'max_tickets_count': max_tickets_count,
                'create_chatterbox_ticket': create_chatterbox_ticket,
            },
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


def _get_tracker_request(
        order_id,
        ticket_queue,
        ticket_summary,
        ticket_tags=None,
        send_chatterbox=True,
):
    request = {
        'unique': order_id,
        'OrderId': order_id,
        'queue': ticket_queue,
        'summary': ticket_summary,
        'tags': ticket_tags,
    }
    if send_chatterbox:
        request['sendChatterbox'] = 'Да'

    return request


@pytest.mark.parametrize(
    'order_status, grocery_order_status',
    [
        ('assembled', 'assembled'),
        ('assembled', 'performer_found'),
        ('assembled', 'delivering'),
        ('delivering', 'delivering'),
    ],
)
async def test_basic(
        _run_stq,
        tracker,
        grocery_orders,
        grocery_depots,
        order_status,
        grocery_order_status,
):
    order = grocery_orders.add_order(
        order_id='order_id',
        status=order_status,
        grocery_order_status=grocery_order_status,
        yandex_uid='yandex_uid',
        personal_phone_id='personal_phone_id',
        depot_id='depot_id',
        country_iso3='RUS',
    )
    grocery_depots.add_depot(
        depot_test_id=123,
        legacy_depot_id=order['depot']['id'],
        country_iso3=order['country_iso3'],
    )
    tracker.check_request(
        _get_tracker_request(
            order_id=order['order_id'],
            ticket_queue=TICKET_QUEUE,
            ticket_summary='expected_late_order_summary',
            ticket_tags=copy.deepcopy(consts.TICKET_TAGS),
            send_chatterbox=True,
        ),
    )
    tracker.check_request(
        request={
            'filter': {
                'queue': TICKET_QUEUE,
                'tags': copy.deepcopy(consts.TICKET_TAGS),
                'status': 'open',
            },
        },
        handler=ISSUES_COUNT_HANDLER,
    )
    await _run_stq(order_id=order['order_id'], order_status=order_status)

    if (
            order_status == 'assembled'
            and grocery_order_status in ['assembled', 'performer_found']
    ) or order_status == grocery_order_status:
        assert tracker.times_called(handler=ISSUES_COUNT_HANDLER) == 1
        assert tracker.times_called(handler=CREATE_ISSUE_HANDLER) == 1
    else:
        assert tracker.times_called(handler=ISSUES_COUNT_HANDLER) == 0
        assert tracker.times_called(handler=CREATE_ISSUE_HANDLER) == 0
