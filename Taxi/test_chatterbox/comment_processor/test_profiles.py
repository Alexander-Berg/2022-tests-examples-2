from typing import AbstractSet

import pytest

from test_chatterbox import plugins as conftest


@pytest.mark.parametrize(
    ('profile', 'succeeded_operations'),
    (
        ('support-taxi', {'refund', 'insert_meta'}),
        ('support-zen', {'insert_meta'}),
    ),
)
async def test_profiles(
        cbox: conftest.CboxWrap,
        patch_support_info_refund,
        auth_data: dict,
        profile: str,
        succeeded_operations: AbstractSet[str],
):
    comment_processor = cbox.app.comment_processor
    fixed_price = 100.0
    task_data = {'task_id': '1', 'fixed_price': fixed_price, 'order_id': '1'}
    patch_support_info_refund(
        response={'currency': 'RUB', 'new_sum': fixed_price},
    )

    _, processing_info = await comment_processor.process(
        'Hello! Sorry {{refund:{{meta:fixed_price}}:REASON}}',
        task_data,
        auth_data,
        profile,
    )
    assert processing_info.succeed_operations == succeeded_operations
