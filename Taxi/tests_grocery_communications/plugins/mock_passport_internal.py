import pytest


@pytest.fixture(name='passport_internal')
def mock_ucommunications(mockserver):
    class Context:
        def __init__(self):
            self.client_ip = '1.1.1.1'
            self.expected_body = None
            self.track_id = None
            self.status = 'ok'
            self.errors = None
            self.display_language = None
            self.number = None
            self.deny_resend_until = None
            self.code_length = None
            self.calling_number_template = None
            self.check_code = None
            self.check_country = None
            self.check_display_language = None
            self.check_number = None

        def configure_headers(self, client_ip='1.1.1.1'):
            self.client_ip = client_ip

        def configure(
                self,
                *,
                expected_body=None,
                track_id=None,
                status=None,
                errors=None,
                number=None,
                deny_resend_until=None,
                code_length=None,
                calling_number_template=None,
                display_language=None,
        ):
            self.display_language = display_language
            self.expected_body = expected_body
            self.track_id = track_id
            self.status = status
            self.errors = errors
            self.number = number
            self.deny_resend_until = deny_resend_until
            self.code_length = code_length
            self.calling_number_template = calling_number_template

        def check(
                self,
                *,
                check_country=None,
                check_display_language=None,
                check_number=None,
                check_code=None,
        ):
            self.check_country = check_country
            self.check_display_language = check_display_language
            self.check_number = check_number
            self.check_code = check_code

        def times_phone_submit_called(self):
            return mock_phone_confirm_submit.times_called

        def times_phone_commit_called(self):
            return mock_phone_confirm_commit.times_called

    context = Context()

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    def mock_phone_confirm_submit(request):
        assert request.headers['Ya-Consumer-Client-Ip'] == context.client_ip
        assert request.form['number'] == context.check_number
        assert (
            request.form['display_language'] == context.check_display_language
        )

        if context.check_country:
            assert request.form['country'] == context.check_country
        else:
            assert 'country' not in request.form

        response = {'status': context.status}

        if context.track_id is not None:
            response['track_id'] = context.track_id
        if context.errors is not None:
            response['errors'] = context.errors
        if context.number is not None:
            response['number'] = context.number
        if context.deny_resend_until is not None:
            response['deny_resend_until'] = context.deny_resend_until
        if context.code_length is not None:
            response['code_length'] = context.code_length
        if context.calling_number_template is not None:
            response[
                'calling_number_template'
            ] = context.calling_number_template

        return response

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def mock_phone_confirm_commit(request):
        assert request.headers['Ya-Consumer-Client-Ip'] == context.client_ip
        assert request.form['track_id'] == context.track_id
        assert request.form['code'] == context.check_code

        response = {'status': context.status}

        if context.track_id is not None:
            response['track_id'] = context.track_id
        if context.errors is not None:
            response['errors'] = context.errors
        if context.number is not None:
            response['number'] = context.number

        return response

    return context
