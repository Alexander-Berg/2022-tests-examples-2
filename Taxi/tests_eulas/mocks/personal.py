import pytest


class PersonalPhoneRetrieveContext:
    class Response:
        def __init__(self):
            self.phone = None
            self.error_code = None

    class Expectations:
        def __init__(self):
            self.personal_phone_id = None

    class Call:
        def __init__(self):
            self.response = PersonalPhoneRetrieveContext.Response()
            self.expected = PersonalPhoneRetrieveContext.Expectations()

    def __init__(self):
        self.call = PersonalPhoneRetrieveContext.Call()
        self.handler = None

    @property
    def times_called(self):
        return self.handler.times_called


@pytest.fixture(name='mock_personal_phones_retrieve')
def mock_phones_retrieve(mockserver):
    context = PersonalPhoneRetrieveContext()

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def handler(request):
        expected = context.call.expected
        response = context.call.response

        if expected.personal_phone_id is not None:
            assert request.json == {
                'id': expected.personal_phone_id,
                'primary_replica': False,
            }
        if response.error_code is not None:
            return mockserver.make_response(
                status=response.error_code,
                json={'code': str(response.error_code), 'message': 'error'},
            )

        return {'id': request.json['id'], 'value': response.phone}

    context.handler = handler
    return context
