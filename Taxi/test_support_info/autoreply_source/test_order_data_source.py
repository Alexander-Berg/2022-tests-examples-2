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
                'payment_tech': {
                    'history': [
                        {'decision': 'refund', 'reason_code': 'WRONG_FARE'},
                        {'decision': 'accept', 'reason_code': 'REASON'},
                    ],
                    'need_disp_accept': True,
                },
                'billing_tech': {
                    'compensations': [{'status': 'compensation_success'}],
                },
            },
            {
                'refund_reason': ['WRONG_FARE'],
                'payment_tech_need_disp_accept': True,
                'payment_decisions': ['refund', 'accept'],
                'compensation_success': True,
            },
        ),
    ),
)
async def test_order_data_source(
        support_info_app: app.SupportInfoApplication,
        patch_get_order_by_id: Callable,
        order: dict,
        expected_result: dict,
):
    await _order_test_process(
        support_info_app, patch_get_order_by_id, order, expected_result,
    )


@pytest.mark.config(
    DRIVER_ML_AUTOREPLY_FIELDS={
        'order': {'fields': ['field1'], 'mapping': {'field1': 'field2'}},
    },
)
@pytest.mark.parametrize(
    ('order', 'expected_result'),
    (
        (
            {'_id': 'order_id2', 'field1': 'abc'},
            {'field2': 'abc', 'compensation_success': False},
        ),
    ),
)
async def test_order_mapping(
        support_info_app: app.SupportInfoApplication,
        patch_get_order_by_id: Callable,
        order: dict,
        expected_result: dict,
):
    await _order_test_process(
        support_info_app, patch_get_order_by_id, order, expected_result,
    )


async def _order_test_process(
        support_info_app: app.SupportInfoApplication,
        patch_get_order_by_id: Callable,
        order: dict,
        expected_result: dict,
):
    patch_get_order_by_id(order=order)

    order_source = autoreply_source.OrderDataSource(
        archive_api_client=support_info_app.archive_api_client,
        config=support_info_app.config,
    )

    result = await order_source.get_data({'order_id': order['_id']})

    assert result == expected_result
