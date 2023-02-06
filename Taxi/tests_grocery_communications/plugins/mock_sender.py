import pytest


@pytest.fixture(name='sender')
def mock_sender(mockserver):
    class Context:
        def __init__(self):
            self.email = None
            self.check_request_flag = False
            self.args = None
            self.error_code = None
            self.request_method = 'POST'

        def check_request(self, *, email=None, args=None):
            self.email = email
            self.args = args
            self.check_request_flag = True

        def times_send_email_called(self):
            return mock_send_email.times_called

        def times_mock_subscription_called(self):
            return mock_subscription.times_called

        def set_error_code(self, code):
            self.error_code = code

    context = Context()

    @mockserver.json_handler('/sender/api/0/lavka/transactional/slug/send')
    def mock_send_email(request):
        if context.check_request_flag:
            body = request.json
            if context.email is not None:
                assert body['to'][0]['email'] == context.email
            if context.args is not None:
                assert body['args'] == context.args

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        return {
            'result': {
                'status': 'OK',
                'task_id': 'test_sender_task_id',
                'message_id': 'test_sender_message_id',
            },
        }

    @mockserver.json_handler('/sender/api/0/lavka/maillist/slug/subscription')
    def mock_subscription(request):
        assert request.method == context.request_method
        if context.check_request_flag:
            if context.email is not None:
                assert request.form['email'] == context.email
            if context.args is not None:
                assert request.form['params'] == context.args

        if context.error_code:
            return mockserver.make_response(
                json={
                    'result': {
                        'status': 'ERROR',
                        'error': {'email': ['Invalid value']},
                    },
                },
                status=context.error_code,
            )

        if request.method == 'DELETE':
            return {
                'params': {'email': request.form['email']},
                'result': {
                    'status': 'OK',
                    'disabled': 1,
                    'already_disabled': 0,
                },
            }

        return {
            'params': {
                'email': request.form['email'],
                'params': request.form['params'],
            },
            'result': {'status': 'OK'},
        }

    return context
