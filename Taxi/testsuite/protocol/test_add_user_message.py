import pytest


@pytest.mark.now('2017-07-19T17:15:15+0000')
def test_add_user_message(taxi_protocol, load, db, mock_stq_agent, now):
    message_id = '1234567890abcdefghijkl0123456789'
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'message_id': message_id,
        'message': 'Текст сообщения',
        'type': 'text',
    }

    messages_stq = mock_stq_agent.get_tasks(
        'user_support_chat_message', message_id,
    )
    assert len(messages_stq) == 0

    response = taxi_protocol.post('3.0/add_user_message', request)
    assert response.status_code == 200

    data = response.json()
    assert data == {}

    # validate user_message
    message_db = db.user_chat_messages.find_one({'messages.id': message_id})
    assert message_db['last_message_from_user'] is True

    assert len(message_db['messages']) == 2

    assert message_db['messages'][1] == {
        'id': message_id,
        'message': 'Текст сообщения',
        'author': 'user',
        'timestamp': now,
        'message_type': 'text',
    }

    # validate stq
    messages_stq = mock_stq_agent.get_tasks(
        'user_support_chat_message', message_id,
    )

    assert len(messages_stq) == 1
    message_stq = messages_stq[0]
    assert message_stq.id == message_id

    assert message_id in message_stq.args
    assert 'Текст сообщения' in message_stq.args
    assert 'text' in message_stq.args

    response = taxi_protocol.post('3.0/add_user_message', request)
    assert response.status_code == 200

    message_db = db.user_chat_messages.find_one({'messages.id': message_id})
    assert message_db['last_message_from_user'] is True

    assert len(message_db['messages']) == 2


@pytest.mark.now('2017-07-19T17:15:15+0000')
def test_add_user_message_csat(taxi_protocol, load, db, now, mock_stq_agent):
    message_id = '1234567890abcdefghijkl0123456788'
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'message_id': message_id,
        'message_key': 'amazing',
        'reason_codes': ['long_answer', 'template_answer'],
        'type': 'csat',
    }

    messages_stq = mock_stq_agent.get_tasks(
        'user_support_chat_message', message_id,
    )
    assert len(messages_stq) == 0

    response = taxi_protocol.post('3.0/add_user_message', request)
    assert response.status_code == 200

    data = response.json()
    assert data == {}

    # validate user_message
    message_db = db.user_chat_messages.find_one(
        {'user_id': 'b300bda7d41b4bae8d58dfa93221ef16'},
    )
    assert not message_db['ask_csat']
    assert not message_db['open']
    assert len(message_db['messages']) == 1
    assert message_db['csat_value'] == 'amazing'
    assert message_db['csat_reasons'] == ['long_answer', 'template_answer']

    # validate stq
    messages_stq = mock_stq_agent.get_tasks(
        'user_support_chat_message', message_id,
    )
    assert len(messages_stq) == 1

    message_stq = messages_stq[0]
    assert message_stq.id == message_id
    assert message_id in message_stq.args
    assert 'csat' in message_stq.args
    assert message_stq.kwargs.get('csat_value') == 'amazing'
    assert message_stq.kwargs.get('csat_reasons') == [
        'long_answer',
        'template_answer',
    ]
