import pytest

from chatterbox import constants
from test_chatterbox import plugins as conftest


@pytest.mark.parametrize(
    ('comment', 'expected_comment'),
    (
        (
            'Hello! Sorry {{park_compensation:{{meta:fixed_price}}}}',
            'Hello! Sorry 100.0',
        ),
        (
            'Hello! Sorry {{park_compensation_hide:{{meta:fixed_price}}}}',
            'Hello! Sorry ',
        ),
    ),
)
async def test_compensation_by_meta(
        cbox: conftest.CboxWrap,
        patch_support_info_compensation,
        auth_data: dict,
        comment: str,
        expected_comment: str,
):
    comment_processor = cbox.app.comment_processor
    fixed_price = 100.0
    task_data = {'task_id': '1', 'fixed_price': fixed_price, 'order_id': '1'}
    patch_support_info_compensation(
        response={'currency': 'RUB', 'compensation_sum': fixed_price},
    )

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == expected_comment
    assert processing_info.succeed_operations == {
        'compensation',
        'insert_meta',
    }
    assert processing_info.operations_log == [
        'Insert meta fixed_price processed',
        'Compensation processed',
    ]
