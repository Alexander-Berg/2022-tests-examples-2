import pytest

from chatterbox import constants
from test_chatterbox import plugins as conftest


@pytest.mark.parametrize(
    ('comment', 'expected_comment', 'admin_rebill_order_called'),
    (
        (
            'Hello! Sorry{{rebill:100}}',
            'Hello! Sorry',
            {'args': ('1', '1', '100')},
        ),
        (
            'Hello! Sorry{{rebill:100.0}}',
            'Hello! Sorry',
            {'args': ('1', '1', '100.0')},
        ),
        (
            'Hello! Sorry{{rebill:10,0}}',
            'Hello! Sorry',
            {'args': ('1', '1', '10.0')},
        ),
    ),
)
async def test_refund_by_meta(
        cbox: conftest.CboxWrap,
        auth_data: dict,
        comment: str,
        expected_comment: str,
        mock_admin_rebill_order,
        admin_rebill_order_called,
):
    comment_processor = cbox.app.comment_processor
    task_data = {'task_id': '1', 'order_id': '1'}

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )

    assert (
        mock_admin_rebill_order.call['args']
        == admin_rebill_order_called['args']
    )
    assert new_comment == expected_comment
    assert processing_info.succeed_operations == {'rebill'}
    assert processing_info.operations_log == ['Rebill processed']
