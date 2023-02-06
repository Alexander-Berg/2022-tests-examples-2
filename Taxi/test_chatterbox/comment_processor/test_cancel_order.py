from aiohttp import web
import pytest

from chatterbox import constants
from test_chatterbox import plugins


EATS_CORE_CANCEL_ORDER_URL = '/internal-api/v1/cancel-order'


@pytest.mark.parametrize(
    'comment, expected_comment, reason',
    [
        (
            'Hello! Bye bye! {{eats_cancel:courier.order_is_absent}}',
            'Hello! Bye bye! ',
            'courier.order_is_absent',
        ),
        (
            'Hello! Bye bye! {{eats_cancel:client_no_show}}',
            'Hello! Bye bye! ',
            'client_no_show',
        ),
        (
            'Hello! Bye bye! {{eats_cancel:courier.order_is_absent.test}}',
            'Hello! Bye bye! ',
            'courier.order_is_absent.test',
        ),
    ],
)
async def test_cancel_order_green(
        cbox: plugins.CboxWrap,
        mock_eats_core_cancel_order,
        auth_data: dict,
        comment: str,
        expected_comment: str,
        reason: str,
):
    comment_processor = cbox.app.comment_processor
    task_data = {'task_id': '1', 'order_id': '123'}

    @mock_eats_core_cancel_order(EATS_CORE_CANCEL_ORDER_URL)
    def _mock_core_cancel_order(request):
        assert request.json['reason_code'] == reason
        return {'is_cancelled': True}

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == expected_comment
    assert processing_info.succeed_operations == {'cancel_order'}
    assert processing_info.operations_log == ['Cancel order processed']


@pytest.mark.parametrize(
    'comment, order_id, cancel_order_response, error',
    [
        (
            'Hello! Bye bye! {{eats_cancel:client_no_show}}',
            None,
            {'status': 200, 'response': {'is_cancelled': True}},
            'No order_id in task',
        ),
        (
            'Hello! Bye bye! {{eats_cancel:client_no_show}}',
            'random_order_nr',
            {'status': 400, 'response': {}},
            'Cancel order error',
        ),
        (
            'Hello! Bye bye! {{eats_cancel:client_no_show}}',
            'random_order_nr',
            {'status': 200, 'response': {'is_cancelled': False}},
            'Cancel order error',
        ),
        (
            'Hello! Bye bye! {{eats_cancel:}}',
            None,
            {'status': None, 'response': {'is_cancelled': None}},
            'Cant apply macro: unknown templates',
        ),
    ],
)
async def test_cancel_order_red(
        cbox: plugins.CboxWrap,
        mock_eats_core_cancel_order,
        auth_data: dict,
        comment: str,
        order_id: str,
        cancel_order_response: dict,
        error: str,
):
    comment_processor = cbox.app.comment_processor
    task_data = {'task_id': '1'}

    if order_id:
        task_data['order_id'] = order_id

    @mock_eats_core_cancel_order(EATS_CORE_CANCEL_ORDER_URL)
    def _mock_core_cancel_order(request):
        return web.json_response(
            cancel_order_response['response'],
            status=cancel_order_response['status'],
        )

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == comment
    assert processing_info.error
    assert not processing_info.succeed_operations
    assert processing_info.operations_log == [error]
