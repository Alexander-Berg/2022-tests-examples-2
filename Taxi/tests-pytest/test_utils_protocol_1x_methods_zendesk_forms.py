import datetime

import cgi
import json
import mocks
import pytest

from taxi.core import db
from taxi.external import zendesk
from utils.protocol_1x.methods import zendesk_forms

NOW = datetime.datetime(2019, 1, 1, 0, 0)


@pytest.fixture
def zclient(monkeypatch, mock):
    @mock
    def _attachment_upload(filename, data, content_type='application/binary',
                           log_extra=None):
        return {
            'upload': {
                'token': 'some_zendesk_token',
            },
        }

    class Client(object):
        attachment_upload = _attachment_upload

    zclient = Client()

    def get_zendesk_client():
        return zclient

    monkeypatch.setattr(
        zendesk, 'get_zendesk_client', get_zendesk_client
    )

    return zclient


@pytest.fixture
def mock_field_storage(monkeypatch):
    class MockedField:
        def __init__(self, name, question_id, value, content_type, filename):
            self.name = name
            self.disposition_options = {
                'filename': filename,
            }
            if content_type:
                self.headers = {
                    'content-type': content_type,
                }
                self.value = value
            else:
                self.value = json.dumps(
                    {
                        'question': {'id': question_id},
                        'value': value,
                    },
                )
                self.headers = {}

    class MockedFieldStorage(dict):
        def __init__(self, fp=None, headers=None, environ=None,
                     strict_parsing=None):
            self.headers = headers
            self.environ = environ
            super(MockedFieldStorage, self).__init__({
                field_name: MockedField(
                    question_id=field['question_id'],
                    name=field_name,
                    value=field['value'],
                    content_type=field.get('content_type'),
                    filename=field.get('filename'),
                ) for field_name, field in fp.items()
            })

    monkeypatch.setattr(cgi, 'FieldStorage', MockedFieldStorage)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'message_id,data,headers,expected_status,expected_response,'
    'expected_stq_put,expected_form_data,expected_attach_calls',
    [
        (
            'msg1',
            {
                'phone': {
                    'question_id': 'field1',
                    'value': '+71234567890',
                },
            },
            {
                'x-delivery-id': 'msg1',
                'x-form-id': 'some_form_id',
                'yataxi-name': 'yataxi',
                'yataxi-orderid': 'some_order_id',
                'yataxi-userid': 'some_user_id',
                'yataxi-source': 'app',
                'content-type': 'application/json',
            },
            None,
            {},
            {
                'args': ('msg1',),
                'eta': datetime.datetime(2019, 1, 1, 0, 1),
                'kwargs': {},
                'queue': 'zendesk_forms',
                'task_id': 'msg1',
            },
            {
                '_id': 'msg1',
                'form_id': 'some_form_id',
                'user_id': 'some_user_id',
                'order_id': 'some_order_id',
                'fields': {'field_field1': '+71234567890'},
                'source': 'app',
                'phone': '+',
                'user_platform': 'yandex',
                'pass_phone_permission': None,
                'zone': None,
                'service': 'taxi',
                'authorized': 'some_user_id',
                'locale': 'ru',
                'attachment_ids': [],
                'support_chat_attachments': [],
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'email': 'noname',
                'name': 'yataxi',
            },
            None,
        ),
        (
            'msg1',
            {
                'phone': {
                    'question_id': 'field1',
                    'value': '+71234567890',
                },
            },
            {
                'x-delivery-id': 'msg1',
                'x-form-id': 'some_form_id',
                'yataxi-name': 'yataxi',
                'yataxi-orderid': 'some_order_id',
                'yataxi-userid': 'user_id_without_phone',
                'yataxi-source': 'app',
                'content-type': 'application/json',
            },
            None,
            {},
            {
                'args': ('msg1',),
                'eta': datetime.datetime(2019, 1, 1, 0, 1),
                'kwargs': {},
                'queue': 'zendesk_forms',
                'task_id': 'msg1',
            },
            {
                '_id': 'msg1',
                'form_id': 'some_form_id',
                'user_id': 'user_id_without_phone',
                'order_id': 'some_order_id',
                'fields': {'field_field1': '+71234567890'},
                'source': 'app',
                'phone': '+',
                'user_platform': 'yandex',
                'pass_phone_permission': None,
                'zone': None,
                'service': 'taxi',
                'authorized': 'user_id_without_phone',
                'locale': 'ru',
                'attachment_ids': [],
                'support_chat_attachments': [],
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'email': 'noname',
                'name': 'yataxi',
            },
            None,
        ),
        (
            'msg1',
            {
                'phone': {
                    'question_id': 'field1',
                    'value': '+71234567890',
                },
            },
            {
                'x-delivery-id': 'msg1',
                'x-form-id': 'some_form_id',
                'yataxi-name': 'yataxi',
                'yataxi-orderid': 'some_order_id',
                'yataxi-userid': 'missing_user_id',
                'yataxi-source': 'app',
                'content-type': 'application/json',
            },
            None,
            {},
            {
                'args': ('msg1',),
                'eta': datetime.datetime(2019, 1, 1, 0, 1),
                'kwargs': {},
                'queue': 'zendesk_forms',
                'task_id': 'msg1',
            },
            {
                '_id': 'msg1',
                'form_id': 'some_form_id',
                'user_id': 'missing_user_id',
                'order_id': 'some_order_id',
                'fields': {'field_field1': '+71234567890'},
                'source': 'app',
                'phone': '+',
                'user_platform': 'yandex',
                'pass_phone_permission': None,
                'zone': None,
                'service': 'taxi',
                'authorized': 'missing_user_id',
                'locale': 'ru',
                'attachment_ids': [],
                'support_chat_attachments': [],
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'email': 'noname',
                'name': 'yataxi',
            },
            None,
        ),
        (
            'msg1',
            {
                'phone': {
                    'question_id': 'field1',
                    'value': '+71234567890',
                },
                'file': {
                    'question_id': 'field2',
                    'value': 'Hello there',
                    'content_type': 'text/plain',
                },
                'file_1': {
                    'question_id': 'field_3',
                    'value': 'File',
                    'content_type': 'text/plain',
                }
            },
            {
                'x-delivery-id': 'msg1',
                'x-form-id': 'some_form_id',
                'yataxi-name': 'yataxi',
                'yataxi-orderid': 'some_order_id',
                'yataxi-userid': 'some_user_id',
                'yataxi-source': 'app',
                'content-type': 'application/json',
            },
            None,
            {},
            {
                'args': ('msg1',),
                'eta': datetime.datetime(2019, 1, 1, 0, 1),
                'kwargs': {},
                'queue': 'zendesk_forms',
                'task_id': 'msg1',
            },
            {
                '_id': 'msg1',
                'form_id': 'some_form_id',
                'user_id': 'some_user_id',
                'order_id': 'some_order_id',
                'fields': {'field_field1': '+71234567890'},
                'source': 'app',
                'phone': '+',
                'user_platform': 'yandex',
                'pass_phone_permission': None,
                'zone': None,
                'service': 'taxi',
                'authorized': 'some_user_id',
                'locale': 'ru',
                'attachment_ids': [],
                'support_chat_attachments': [
                    {
                        'id': 'some_attachment_id_0',
                        'name': 'attachment',
                    },
                    {
                        'id': 'some_attachment_id_1',
                        'name': 'attachment',
                    }
                ],
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'email': 'noname',
                'name': 'yataxi',
            },
            [
                {
                    'params': {
                        'filename': 'attachment',
                        'idempotency_token': 'msg1_0',
                        'sender_id': 'some_phone_id',
                        'sender_role': 'client',
                    },
                    'data': 'File',
                    'headers': {},
                    'json': None,
                    'log_extra': None,
                },
                {
                    'params': {
                        'filename': 'attachment',
                        'idempotency_token': 'msg1_1',
                        'sender_id': 'some_phone_id',
                        'sender_role': 'client',
                    },
                    'data': 'Hello there',
                    'headers': {},
                    'json': None,
                    'log_extra': None,
                },
            ]
        ),
        (
            'msg1',
            {
                'phone': {
                    'question_id': 'field1',
                    'value': '+71234567890',
                },
            },
            {
                'x-delivery-id': 'msg1',
                'x-form-id': 'some_form_id',
                'yataxi-name': 'yataxi',
                'yataxi-orderid': 'some_order_id',
                'yataxi-userid': 'some_user_id',
                'yataxi-source': 'app',
                'yataxi-pass-phone-permission': 'True',
                'content-type': 'application/json',
            },
            None,
            {},
            {
                'args': ('msg1',),
                'eta': datetime.datetime(2019, 1, 1, 0, 1),
                'kwargs': {},
                'queue': 'zendesk_forms',
                'task_id': 'msg1',
            },
            {
                '_id': 'msg1',
                'form_id': 'some_form_id',
                'user_id': 'some_user_id',
                'order_id': 'some_order_id',
                'fields': {'field_field1': '+71234567890'},
                'source': 'app',
                'phone': '+',
                'user_platform': 'yandex',
                'pass_phone_permission': True,
                'zone': None,
                'service': 'taxi',
                'authorized': 'some_user_id',
                'locale': 'ru',
                'attachment_ids': [],
                'support_chat_attachments': [],
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'email': 'noname',
                'name': 'yataxi',
            },
            None,
        ),
    ],
)
@pytest.inline_callbacks
def test_zendesk_forms(patch, zclient, mock_field_storage, areq_request,
                       message_id, data, headers, expected_status,
                       expected_response, expected_stq_put, expected_form_data,
                       expected_attach_calls):
    @patch('taxi_stq._client.put')
    @pytest.inline_callbacks
    def _dummy_put(queue, eta=None, task_id=None, args=None, kwargs=None):
        yield

    support_chat_attach_calls = []

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        if 'support-chat' in url:
            assert url.startswith('http://support-chat.taxi.yandex.net')
            if 'attach_file' in url:
                attachment_id = 'some_attachment_id_%s' % (
                    len(support_chat_attach_calls)
                )
                support_chat_attach_calls.append(kwargs)
                return areq_request.response(
                    200,
                    body=json.dumps(
                        {
                            'attachment_id': attachment_id,
                        },
                    ),
                )

    request = mocks.FakeRequest(
        raw_content=data,
        headers=headers,
    )
    response = yield zendesk_forms.Method().POST(request)
    assert request.response_code == expected_status
    if expected_status is None:
        assert response == expected_response

    stq_put_calls = _dummy_put.calls
    if expected_stq_put is None:
        assert not stq_put_calls
    else:
        del stq_put_calls[0]['kwargs']['log_extra']
        assert stq_put_calls[0] == expected_stq_put

    form_data = yield db.zendesk_form_integrations.find_one(
        {'_id': message_id},
    )
    assert form_data == expected_form_data

    if expected_attach_calls is None:
        assert not support_chat_attach_calls
    else:
        sorted_attach_calls = sorted(
            support_chat_attach_calls,
            key=lambda x: x['params']['idempotency_token']
        )
        assert sorted_attach_calls == expected_attach_calls
