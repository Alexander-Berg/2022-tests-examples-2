from typing import Dict

import pytest


class UserPushContext:
    class Response:
        def __init__(self):
            self.error_code = None

    class Expectations:
        def __init__(self):
            self.title = None
            self.text = None
            self.intent = None
            self.user = None
            self.locale = None
            self.order_id = None
            self.idempotency_token = None

    class Call:
        def __init__(self):
            self.response = UserPushContext.Response()
            self.expected = UserPushContext.Expectations()

    def __init__(self):
        self.calls: Dict(str, UserPushContext.Call) = {}
        self.handler = None

    @property
    def times_called(self):
        return self.handler.times_called


@pytest.fixture(name='mock_ucommunications_user_push')
def mock_user_push(mockserver):
    def _get_expected_push_data(text, title, order_id):
        return {
            'payload': {
                'text': text,
                'title': title,
                'extra': {'order_id': order_id},
            },
        }

    def mock():
        context = UserPushContext()

        @mockserver.json_handler('/ucommunications/user/notification/push')
        def handler(request):
            user_id = request.json['user']
            if user_id not in context.calls:
                return {}

            expected = context.calls[user_id].expected
            response = context.calls[user_id].response

            data = request.json

            if expected.idempotency_token is not None:
                assert (
                    request.headers['X-Idempotency-Token']
                    == expected.idempotency_token
                )
            else:
                assert 'X-Idempotency-Token' in request.headers

            if expected.text is not None and expected.title is not None:
                data['data']['payload']['extra'].pop('id')
                assert data['data'] == _get_expected_push_data(
                    expected.text, expected.title, expected.order_id,
                )

            for key in ['intent', 'user', 'locale']:
                if getattr(expected, key) is not None:
                    assert data[key] == getattr(expected, key)

            if response.error_code is not None:
                return mockserver.make_response(
                    status=response.error_code, json={'message': 'error'},
                )
            return {}

        context.handler = handler

        return context

    return mock
