from typing import Callable

import pytest

from support_info import app
from support_info.internal import autoreply_source


@pytest.mark.parametrize(
    ('order', 'expected_result'),
    (
        (
            {
                '_id': 'order_id',
                'price_modifiers': {'items': [{'reason': 'ya_plus'}]},
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                's': 'finished',
                                'q': 'reject',
                                'r': 'autocancel',
                            },
                        ],
                    },
                },
                'order': {
                    'feedback': {
                        'msg': 'message',
                        'choices': {
                            'cancelled_reason': ['driverrequest'],
                            'low_rating_reason': ['rudedriver'],
                        },
                    },
                    'discount': {'reason': 'analytics', 'value': 100},
                    'request': {
                        'comment': 'Комментарий к заказу',
                        'payment': {'type': 'corp'},
                    },
                    'status': 'finished',
                    'taxi_status': 'complete',
                },
            },
            {
                'ya_plus': True,
                'order_events_autocancel': True,
                'cancelled_reason': ['driverrequest'],
                'rating_reason': ['rudedriver'],
                'rating_comments': 'message',
                'discount_value': 100,
                'discount_reason': 'analytics',
                'order_comment': 'Комментарий к заказу',
                'corp_order_flg': True,
                'status': 'finished',
                'taxi_status': 'complete',
                'hidden_discount': True,
            },
        ),
        (
            {
                '_id': 'order_id',
                'price_modifiers': {'items': [{'reason': 'other'}]},
                'order': {
                    'discount': {'reason': 'analytics', 'value': 0},
                    'request': {'payment': {'type': 'card'}},
                    'status': 'cancelled',
                },
                'order_info': {'statistics': {'status_updates': []}},
            },
            {
                'corp_order_flg': False,
                'discount_reason': 'analytics',
                'order_events_autocancel': False,
                'status': 'cancelled',
                'ya_plus': False,
                'hidden_discount': False,
            },
        ),
        (
            {
                '_id': 'order_id',
                'order': {
                    'request': {'payment': {'type': 'card'}},
                    'status': 'cancelled',
                },
                'order_info': {'statistics': {'status_updates': []}},
            },
            {
                'corp_order_flg': False,
                'order_events_autocancel': False,
                'status': 'cancelled',
                'ya_plus': False,
                'hidden_discount': False,
            },
        ),
    ),
)
async def test_order_proc_data_source(
        support_info_app: app.SupportInfoApplication,
        patch_order_proc_retrieve: Callable,
        order: dict,
        expected_result: dict,
):
    patch_order_proc_retrieve(order=order)

    order_source = autoreply_source.OrderProcDataSource(
        archive_api_client=support_info_app.archive_api_client,
        config=support_info_app.config,
    )

    result = await order_source.get_data({'order_id': order['_id']})

    assert result == expected_result
