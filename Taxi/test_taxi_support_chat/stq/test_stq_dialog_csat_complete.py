import bson
import pytest

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.internal import csat
from taxi_support_chat.stq import stq_task

TEST_CREATED_ANSWER = '2018-07-06T13:44:50.456000'


@pytest.mark.parametrize(
    ('chat_id', 'created_answer', 'kwargs', 'expected_doc_fields'),
    (
        (
            '5e285103779fb3831c8b4bde',
            TEST_CREATED_ANSWER,
            {},
            {
                'state': csat.COMPLETE_STATE,
                'complete': True,
                'open': False,
                'close_ticket': False,
                'ask_csat': False,
                'visible': False,
            },
        ),
        (
            '5e285103779fb3831c8b4bdd',
            TEST_CREATED_ANSWER,
            {},
            {
                'state': 'qa_amazing_waiting_finish',
                'complete': False,
                'open': True,
                'close_ticket': False,
                'ask_csat': True,
                'visible': True,
            },
        ),
        (
            '5e285103779fb3831c8b4aa3',
            TEST_CREATED_ANSWER,
            {},
            {
                'state': 'waiting_qa_rating',
                'complete': False,
                'open': True,
                'close_ticket': False,
                'ask_csat': True,
                'visible': True,
            },
        ),
    ),
)
async def test_stq_dialog_csat_complete(
        stq3_context: stq_context.Context,
        mock_chatterbox_tasks,
        chat_id,
        created_answer,
        kwargs,
        expected_doc_fields,
):
    await stq_task.dialog_csat_complete(
        stq3_context, chat_id, created_answer, **kwargs,
    )

    chat = await stq3_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    chat_csat_dialog = chat['csat_dialog']
    assert chat_csat_dialog['state'] == expected_doc_fields['state']
    assert (
        chat_csat_dialog.get('complete', False)
        == expected_doc_fields['complete']
    )
    assert chat['open'] == expected_doc_fields['open']
    assert (
        chat.get('close_ticket', False) == expected_doc_fields['close_ticket']
    )
    assert chat['ask_csat'] == expected_doc_fields['ask_csat']
    assert chat['visible'] == expected_doc_fields['visible']

    if expected_doc_fields['complete']:
        assert mock_chatterbox_tasks.calls[0] == {
            'kwargs': {'external_id': chat_id, 'log_extra': None},
        }
