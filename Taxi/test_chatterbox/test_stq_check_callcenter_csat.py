# pylint: disable=too-many-arguments,redefined-outer-name
import bson
import pytest

from chatterbox import stq_task


FIRST_ATTEMPT = 0


@pytest.mark.parametrize(
    (
        'task_id',
        'call_guid',
        'attempt',
        'expected_meta_calls',
        'expected_callcentr_calls',
    ),
    [
        (
            bson.ObjectId('5b2cae5cb2682a976914caa1'),
            '1',
            FIRST_ATTEMPT,
            [{'id': '1', 'csat_value': '5', 'source': 'callcenter'}],
            True,
        ),
        (
            bson.ObjectId('5c2cae5cb2682a976914caa1'),
            '2',
            FIRST_ATTEMPT,
            None,
            True,
        ),
        (
            bson.ObjectId('5c2cae5cb2682a976914caa1'),
            '2',
            3,
            [{'id': '2', 'source': 'callcenter'}],
            True,
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914caa2'),
            '3',
            FIRST_ATTEMPT,
            [{'id': '3', 'source': 'callcenter'}],
            True,
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914caa3'),
            '4',
            FIRST_ATTEMPT,
            [
                {'id': 'test_id', 'user_id': 'test_user'},
                {'id': '4', 'csat_value': '6', 'source': 'callcenter'},
            ],
            True,
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914caa4'),
            '5',
            FIRST_ATTEMPT,
            [
                {'id': 'test_id', 'user_id': 'test_user'},
                {'id': '5', 'source': 'callcenter'},
            ],
            True,
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914caa5'),
            '6',
            FIRST_ATTEMPT,
            [
                {'id': 'test_id', 'user_id': 'test_user'},
                {'id': '6', 'csat_value': '0', 'source': 'not_callcenter'},
            ],
            False,
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'chatterbox', 'dst': 'callcenter-qa'}],
    STQ_CHATTERBOX_CHECK_CALLCENTER_CSAT=0.1,
)
async def test_check_callcenter_csat(
        cbox,
        mock_callcenter_qa,
        task_id,
        call_guid,
        attempt,
        expected_meta_calls,
        expected_callcentr_calls,
):
    await stq_task.check_callcenter_csat(cbox.app, task_id, call_guid, attempt)

    callcentr_calls = mock_callcenter_qa.has_calls
    assert expected_callcentr_calls == bool(callcentr_calls)
    if callcentr_calls:
        assert mock_callcenter_qa.times_called == 1
        _request_callcenter_qa = mock_callcenter_qa.next_call()['request']
        assert _request_callcenter_qa.path == '/v1/rating/get'
        assert _request_callcenter_qa.json == {'guids': [call_guid]}
        assert _request_callcenter_qa.method == 'POST'

    task = await cbox.app.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id)},
    )
    assert task['meta_info'].get('calls') == expected_meta_calls
