import json
import pytest

from taxi.external import pymlaas


@pytest.mark.parametrize(
    'text,request_id,expected_urgency,expected_json',
    [
        (
            'should_be_urgent',
            None,
            0.8,
            {'text': 'should_be_urgent'}
        ),
        (
            'other_text',
            'some_id',
            0.2,
            {'text': 'other_text', 'request_id': 'some_id'},
        ),
    ]
)
@pytest.inline_callbacks
def test_urgent_comments_detection(mock, areq_request, text, request_id,
                                   expected_urgency, expected_json):
    @mock
    @areq_request
    def aresponse(method, url, **kwargs):
        assert 'json' in kwargs
        assert 'text' in kwargs['json']

        assert 'headers' in kwargs
        assert 'Content-Type' in kwargs['headers']
        assert kwargs['headers']['Content-Type'] == 'application/json'
        assert 'User-Agent' in kwargs['headers']
        assert kwargs['headers']['User-Agent'] == 'arequests'

        if kwargs['json']['text'] == 'should_be_urgent':
            result = 0.8
        else:
            result = 0.2

        return 200, json.dumps({'urgency_probability': result}), {}

    data = {'text': text}
    if request_id:
        data['request_id'] = request_id
    urgency = yield pymlaas.urgent_comments_detection(data)
    assert urgency == expected_urgency

    aresponce_call = aresponse.calls[0]
    assert aresponce_call['args'] == (
        'POST', 'http://pyml.test.url/urgent_comments_detection',
    )
    assert aresponce_call['kwargs']['json'] == expected_json


@pytest.mark.parametrize(
    'data,expected_need_response,expected_json',
    [
        (
            {'comment': 'should_be_readonly'},
            False,
            {'comment': 'should_be_readonly'}
        ),
        (
            {'comment': 'other_text'},
            True,
            {'comment': 'other_text'},
        ),
    ]
)
@pytest.inline_callbacks
def test_client_tickets_read_only(mock, areq_request, data,
                                  expected_need_response, expected_json):
    @mock
    @areq_request
    def aresponse(method, url, **kwargs):
        assert 'json' in kwargs
        assert 'comment' in kwargs['json']

        assert 'headers' in kwargs
        assert 'Content-Type' in kwargs['headers']
        assert kwargs['headers']['Content-Type'] == 'application/json'
        assert 'User-Agent' in kwargs['headers']
        assert kwargs['headers']['User-Agent'] == 'arequests'

        if kwargs['json']['comment'] == 'should_be_readonly':
            result = 0
        else:
            result = 1

        return 200, json.dumps({'need_response': result}), {}

    need_response = yield pymlaas.client_tickets_read_only(data)
    assert need_response == expected_need_response

    aresponce_call = aresponse.calls[0]
    assert aresponce_call['args'] == (
        'POST', 'http://pyml.test.url/client_tickets_read_only',
    )
    assert aresponce_call['kwargs']['json'] == expected_json
