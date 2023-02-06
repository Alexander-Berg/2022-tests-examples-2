import pytest

from processing_antifraud.models import events
from processing_antifraud.modules.processing_events.status_handlers import (
    transporting,
)


@pytest.mark.config(
    TVM_RULES=[{'src': 'processing-antifraud', 'dst': 'stq-agent'}],
)
async def test_transporting_event(
        stq, stq3_context, stq_runner, order_core_mock,
):
    order_core_mock('order_core_mock.json')

    await stq_runner.antifraud_processing_events.call(
        args=('order_id', 'handle_transporting', 3),
    )
    assert stq.processing_antifraud.times_called == 1

    event_list = await events.Events.get_unfinished_events(
        stq3_context.mongo, 'order_id',
    )

    assert len(event_list) == 1

    event = event_list[0].to_dict()
    event.pop('_id')
    event.pop('updated')

    assert event == {
        'order_id': 'order_id',
        'processing_index': 3,
        'antifraud_index': 0,
        'event_name': 'driver_transporting',
        'status': 'pending',
        'finished': False,
        'kwargs': {
            'alias_id': 'alias_id',
            'category_id': '877721c0f6b246488fb639acdfb4602d',
            'coupon': {},
            'db_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'discount_multiplier': 1.0,
            'fixed_price': True,
            'order_id': 'order_id',
            'processing_index': 3,
            'surge': {'alpha': 0, 'beta': 1, 'surcharge': 0, 'surge': 1.0},
            'tariff_class': 'business',
            'transporting_time': '2020-05-12T08:03:01.244+00:00',
        },
    }


async def test_missing_transporting(
        stq, stq3_context, stq_runner, order_core_mock,
):
    order_core_mock('order_core_assigned.json')

    with pytest.raises(transporting.UnknownTransportingTime):
        await transporting.handler(stq3_context, 'order_waiting', 3)
