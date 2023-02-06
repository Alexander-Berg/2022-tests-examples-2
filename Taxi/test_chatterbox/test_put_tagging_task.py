# pylint: disable=too-many-lines, too-many-arguments, redefined-outer-name
# pylint: disable=unused-variable, too-many-locals, no-member
import datetime
import http

import pytest

NOW = datetime.datetime(2019, 8, 27, 9, 10)


@pytest.mark.config(
    CHATTERBOX_TAGS_SERVICE_CONDITIONS=[
        {
            'condition_tags': ['tag', 'driver_tagging'],
            'tag_to_add': 'call_request_tag',
            'entity_type': 'dbid_uuid',
            'tag_lifetime': 86400,
        },
        {
            'condition_tags': ['tag', 'tag_tagging'],
            'tag_to_add': 'phone_tag',
            'entity_type': 'user_phone_id',
        },
    ],
)
@pytest.mark.parametrize(
    'task_id, action, params, data, expected_stq_args',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            'close',
            {'additional_tag': 'test_tag'},
            {'comment': 'test'},
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'close',
            {},
            {'comment': 'test', 'tags': ['test_tag']},
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'dismiss',
            {},
            {'tags': ['test_tag']},
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'close',
            {},
            {'comment': 'test', 'tags': ['driver_tagging']},
            [
                [
                    {'$oid': '5b2cae5cb2682a976914c2a1'},
                    'call_request_tag',
                    'dbid_uuid',
                    86400,
                ],
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'close',
            {},
            {'comment': 'test', 'tags': ['tag_tagging']},
            [
                [
                    {'$oid': '5b2cae5cb2682a976914c2a1'},
                    'phone_tag',
                    'user_phone_id',
                    None,
                ],
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'close',
            {},
            {'comment': 'test', 'tags': ['driver_tagging', 'tag_tagging']},
            [
                [
                    {'$oid': '5b2cae5cb2682a976914c2a1'},
                    'call_request_tag',
                    'dbid_uuid',
                    86400,
                ],
                [
                    {'$oid': '5b2cae5cb2682a976914c2a1'},
                    'phone_tag',
                    'user_phone_id',
                    None,
                ],
            ],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_put_tagging_task(
        cbox,
        stq,
        task_id,
        action,
        params,
        data,
        expected_stq_args,
        mock_chat_add_update,
        mock_chat_get_history,
):
    mock_chat_get_history({'messages': []})
    await cbox.post(
        '/v1/tasks/%s/%s' % (task_id, action), params=params, data=data,
    )

    assert cbox.status == http.HTTPStatus.OK
    stq_calls = [
        stq.chatterbox_add_tag_to_tags_service.next_call()
        for _ in range(stq.chatterbox_add_tag_to_tags_service.times_called)
    ]
    if expected_stq_args:
        assert len(stq_calls) == len(expected_stq_args)
        for i, stq_call in enumerate(stq_calls):
            assert stq_call['args'] == expected_stq_args[i]
    else:
        assert not stq_calls
