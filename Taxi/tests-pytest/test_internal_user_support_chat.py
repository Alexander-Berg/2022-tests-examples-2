import json

import bson
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import user_support_chat
from taxi.external import tvm
from taxi.external import chatterbox


@pytest.inline_callbacks
@pytest.mark.config(TVM_RULES=[{'src': 'stq', 'dst': 'chatterbox'}])
@pytest.mark.parametrize('chat_id, args, kwargs', [
    (
        '5b5b37a2779fb31204bac216',
        [bson.ObjectId('5b5b37a2779fb31204bac216'), 'msg1', 'text', 'text'],
        {}
    ),
    (
        '5b5b37a2779fb31204bac216',
        [bson.ObjectId('5b5b37a2779fb31204bac216'), 'msg1', 'text', 'text'],
        {
            'csat_value': 'amazing',
            'csat_reasons': ['reason1', 'reason2'],
            'public': True,
            'status': 'open'
        }
    ),
    (
        '5b5b37a2779fb31204bac216',
        [bson.ObjectId('5b5b37a2779fb31204bac216'), 'msg1', 'text', 'text'],
        {}
    ),
    (
        '5b5b37aa779fb31204bac217',
        [bson.ObjectId('5b5b37aa779fb31204bac217'), 'msg7', 'text', 'text'],
        {}
    ),
    (
        '5b5b37aa779fb31204bac217',
        [bson.ObjectId('5b5b37aa779fb31204bac217'), 'msg7', 'text', 'csat'],
        {}
    )
])
def test_user_support_chat(monkeypatch, areq_request, chat_id, args, kwargs):
    class FakeLogger(object):
        messages = []

        def info(self, msg, *args, **kwargs):
            self.messages.append(msg % args)
    monkeypatch.setattr(user_support_chat, 'logger', FakeLogger())

    @areq_request
    def requests_request(method, url, **kwargs):
        assert url == 'http://chatterbox.taxi.yandex.net/v1/tasks'
        request = kwargs['json']
        assert request['type'] == 'chat'
        assert request['external_id'] == chat_id
        assert kwargs['headers'][tvm.TVM_TICKET_HEADER] == 'test_ticket'
        return areq_request.response(
            200, body=json.dumps({'id': 'test'})
        )

    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == 'stq'
        assert dst_service_name == 'chatterbox'
        yield async.return_value('test_ticket')

    monkeypatch.setattr(
        tvm, 'get_ticket', get_ticket
    )

    yield user_support_chat.process_user_message(*args, **kwargs)

    chat_doc = yield db.user_chat_messages._collection.find_one(
        {
            'messages.id': args[1]
        }
    )

    assert user_support_chat.logger.messages == [
        'Send user support chat message %s to chatterbox' % args[1],
        'Add task test to chatterbox for chat message %s and chat %s' % (
            args[1], chat_doc['_id']
        )
    ]


@pytest.inline_callbacks
@pytest.mark.config(TVM_RULES=[{'src': 'stq', 'dst': 'chatterbox'}])
@pytest.mark.parametrize('chat_id, args, kwargs', [
    (
        '5b5b37aa779fb31204bac218',
        [bson.ObjectId('5b5b37aa779fb31204bac218'), 'msg8', 'text', 'text'],
        {
            'csat_value': 'amazing',
            'csat_reasons': ['reason1', 'reason2'],
            'public': True,
            'status': 'open',
            'add_tags': ['tag1', 'tag2'],
            'remove_tags': ['tag3', 'tag4'],
            'uploads': ['upload']
        }
    ),
    (
        '5b5b37aa779fb31204bac218',
        [bson.ObjectId('5b5b37aa779fb31204bac218'), 'msg8', 'text', 'csat'],
        {
            'csat_value': 'amazing',
            'csat_reasons': ['reason1', 'reason2'],
            'public': True,
            'status': 'open',
            'add_tags': ['tag1', 'tag2'],
            'remove_tags': ['tag3', 'tag4'],
            'uploads': ['upload']
        }
    )
])
def test_user_support_chat_unprocessable(monkeypatch, areq_request,
                                         chat_id, args, kwargs):
    class FakeLogger(object):
        messages = []

        def info(self, msg, *args, **kwargs):
            self.messages.append(msg % args)

        def warning(self, msg, *args, **kwargs):
            self.messages.append(msg % args)
    monkeypatch.setattr(user_support_chat, 'logger', FakeLogger())
    monkeypatch.setattr(chatterbox, 'logger', FakeLogger())

    @areq_request
    def requests_request(method, url, **kwargs):
        assert url == 'http://chatterbox.taxi.yandex.net/v1/tasks'
        request = kwargs['json']
        assert request['type'] == 'chat'
        assert request['external_id'] == chat_id
        assert kwargs['headers'][tvm.TVM_TICKET_HEADER] == 'test_ticket'
        db.user_chat_messages._collection.update(
            {
                '_id': bson.ObjectId(chat_id)
            },
            {
                '$set': {
                    'author_id': 12345,
                    'ticket_id': 12345
                }
            }
        )
        return areq_request.response(
            410, body=json.dumps({'id': 'test_unproc'})
        )

    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == 'stq'
        assert dst_service_name == 'chatterbox'
        yield async.return_value('test_ticket')

    monkeypatch.setattr(
        tvm, 'get_ticket', get_ticket
    )

    yield user_support_chat.process_user_message(*args, **kwargs)

    assert user_support_chat.logger.messages == [
        'Send user support chat message %s to chatterbox' % args[1],
        '''Sending POST request to http://chatterbox.taxi.yandex.net/v1/tasks'''
        ''' with json: {'type': 'chat', 'external_id': '%s'}''' % chat_id,
        '''Error during performing POST request to '''
        '''http://chatterbox.taxi.yandex.net/v1/tasks'''
        '''with json %s: RequestError [None]: Client Error: 410, '''
        '''response {"id": "test_unproc"}''' % (
            {
                'external_id': chat_id,
                'type': 'chat'
            }
        ),
        'Chatterbox task with external id %s already changes,'
        ' message id %s' % (
            chat_id, args[1],
        )
    ]

    yield user_support_chat.process_user_message(*args, **kwargs)


@pytest.inline_callbacks
@pytest.mark.parametrize(
    ('phone_id', 'platform', 'data',
     'expected_ml_request_id', 'expected_calls'),
    [
        (
            '5b5b37aa779fb31204bad45a',
            'yandex',
            [
                {
                    'metadata': {
                        'ml_request_id': '00000000000040008000000000000000',
                    }
                }
            ],
            '00000000000040008000000000000000',
            1,
        ),
        (
            '5b5b37aa779fb31204bad45a',
            'yandex',
            [
                {
                    'metadata': {
                        'ml_request_id': None,
                    }
                }
            ],
            None,
            1,
        ),
        (
            None,
            'yandex',
            None,
            None,
            0,
        )
    ]
)
def test_get_ml_request_id(areq_request, phone_id, platform, data,
                           expected_ml_request_id, expected_calls):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert url == 'http://support-chat.taxi.yandex.net/v1/chat/search/'
        request = kwargs['json']
        assert request['owner'] == {
            'platform': platform,
            'id': phone_id,
            'role': 'client',
        }
        return areq_request.response(
            200, body=json.dumps({'chats': data})
        )

    ml_request_id = yield user_support_chat.get_ml_request_id(
        phone_id,
        platform,
    )

    assert ml_request_id == expected_ml_request_id

    assert len(requests_request.calls) == expected_calls
