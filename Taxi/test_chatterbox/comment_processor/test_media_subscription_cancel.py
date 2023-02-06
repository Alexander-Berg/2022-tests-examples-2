from typing import List
from typing import Set

import aiohttp.web
import pytest

from chatterbox import constants
from test_chatterbox import plugins as conftest


@pytest.mark.parametrize(
    (
        'comment',
        'expected_comment',
        'task_data',
        'response',
        'status',
        'expected_request',
        'operations_log',
        'succeed_operations',
        'meta_update',
    ),
    (
        (
            'comment {{media_subscription_cancel:123}} comm',
            'comment  comm',
            {'task_id': 'task_1'},
            {'result': 'cancel', 'status': 'success'},
            200,
            {
                'uid': '123',
                'reason': 'https://supchat.taxi.yandex-team.ru/chat/task_1',
            },
            ['Subscription cancel processed'],
            {'subscription_cancel'},
            {'meta_info.cancel_result': 'cancel'},
        ),
        (
            'comment {{media_subscription_cancel:1234}} comm2',
            'comment  comm2',
            {'task_id': 'task_2', 'user_uid': '5678'},
            {'result': 'error', 'status': 'success'},
            200,
            {
                'uid': '1234',
                'reason': 'https://supchat.taxi.yandex-team.ru/chat/task_2',
            },
            ['Subscription cancel processed'],
            {'subscription_cancel'},
            {'meta_info.cancel_result': 'error'},
        ),
        (
            'comment {{media_subscription_cancel}} comm3',
            'comment  comm3',
            {'task_id': 'task_3', 'user_uid': '5678'},
            {'status': 'error'},
            200,
            {
                'uid': '5678',
                'reason': 'https://supchat.taxi.yandex-team.ru/chat/task_3',
            },
            ['Subscription cancel processed'],
            {'subscription_cancel'},
            {},
        ),
        (
            'comment {{media_subscription_cancel}} comm3',
            'comment {{media_subscription_cancel}} comm3',
            {'task_id': 'task_3', 'user_uid': '5678'},
            {'status': 'error'},
            500,
            {
                'uid': '5678',
                'reason': 'https://supchat.taxi.yandex-team.ru/chat/task_3',
            },
            ['Media support request error'],
            set(),
            {},
        ),
        (
            'comment {{media_subscription_cancel}} comm3',
            'comment {{media_subscription_cancel}} comm3',
            {'task_id': 'task_3'},
            {},
            200,
            {
                'uid': '5678',
                'reason': 'https://supchat.taxi.yandex-team.ru/chat/task_3',
            },
            ['Yandex uid not in macro and not in metadata'],
            set(),
            {},
        ),
        (
            'comment {{media_subscription_cancel:sdf}} comm3',
            'comment {{media_subscription_cancel:sdf}} comm3',
            {'task_id': 'task_3'},
            {},
            200,
            {
                'uid': '5678',
                'reason': 'https://supchat.taxi.yandex-team.ru/chat/task_3',
            },
            ['Cant apply macro: unknown templates'],
            set(),
            {},
        ),
        (
            'comment {{media_subscription_cancel123}} comm3',
            'comment {{media_subscription_cancel123}} comm3',
            {'task_id': 'task_3'},
            {},
            200,
            {
                'uid': '5678',
                'reason': 'https://supchat.taxi.yandex-team.ru/chat/task_3',
            },
            ['Cant apply macro: unknown templates'],
            set(),
            {},
        ),
    ),
)
async def test_subscription_cancel(
        cbox: conftest.CboxWrap,
        mockserver,
        auth_data: dict,
        comment: str,
        expected_comment: str,
        task_data: dict,
        response: dict,
        status: int,
        expected_request: dict,
        operations_log: List[str],
        succeed_operations: Set[str],
        meta_update: dict,
):
    @mockserver.json_handler('/music/stop-active-interval/')
    def _dummy_subscription_cancel(request):
        assert request.json == expected_request
        return aiohttp.web.json_response(response, status=status)

    comment_processor = cbox.app.comment_processor
    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )

    assert new_comment == expected_comment
    assert processing_info.operations_log == operations_log
    assert processing_info.succeed_operations == succeed_operations
    assert processing_info.update_metadata == meta_update
