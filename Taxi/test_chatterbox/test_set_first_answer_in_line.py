import datetime
import http

import bson
import pytest


NOW = datetime.datetime(2021, 7, 16, 3, 49, 46)


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'types': ['client']},
        'second': {'types': ['client']},
    },
    CHAT_LINE_TRANSITIONS={'first': ['second']},
    CHATTERBOX_CHANGE_LINE_STATUSES={'in_progress': 'in_progress'},
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.usefixtures('mock_chat_add_update')
@pytest.mark.parametrize(
    'task_id, messages, action, params, data, expected_first_answer_time',
    [
        ('5d398480779fb3180875201c', [], None, {}, {}, None),
        (
            '5d398480779fb3180875201c',
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2021-07-16T03:49:36+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2021-07-16T03:49:56+0000'},
                },
            ],
            None,
            {},
            {},
            20,
        ),
        (
            '5d398480779fb3180875201c',
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2021-07-16T03:49:36+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2021-07-16T03:49:56+0000'},
                },
            ],
            'forward',
            {'line': 'second'},
            {'hidden_comment': 'some hidden comment'},
            10,
        ),
        (
            '5d398480779fb3180875201c',
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2021-07-16T03:49:56+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2021-07-16T03:50:16+0000'},
                },
            ],
            'move',
            {'line': 'second'},
            {'hidden_comment': 'some hidden comment'},
            20,
        ),
        (
            '5d398480779fb3180875201c',
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2021-07-16T03:49:26+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2021-07-16T03:49:36+0000'},
                },
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2021-07-16T03:50:00+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2021-07-16T03:51:00+0000'},
                },
            ],
            None,
            {},
            {},
            10,
        ),
        (
            '5d398480779fb3180875202c',
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2021-07-16T03:47:30+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2021-07-16T03:48:30+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2021-07-16T03:50:46+0000'},
                },
            ],
            'forward',
            {'line': 'second'},
            {'hidden_comment': 'some hidden comment'},
            60,
        ),
    ],
)
async def test_set_first_answer_in_line(
        cbox,
        task_id,
        messages,
        action,
        params,
        data,
        expected_first_answer_time,
        mock_chat_get_history,
):

    mock_chat_get_history({'messages': messages})
    if action:
        await cbox.post(
            '/v1/tasks/{0}/{1}'.format(task_id, action),
            params=params,
            data=data,
        )
        assert cbox.status == http.HTTPStatus.OK

    # this request does not add new messages, only initiates the call of
    # the function _add_answer_statistics that sets first_answer_in_line
    await cbox.post(
        '/v1/tasks/{0}/communicate'.format(task_id), data={'comment': 'dummy'},
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id)},
    )

    last_record = task['history'][-1]
    assert (
        last_record.get('first_answer_in_line') == expected_first_answer_time
    )
