import pytest


class PersonalStoreContext:
    class Response:
        def __init__(self):
            self.personal_id = None
            self.error_code = None
            self.error_message = None

    class Request:
        def __init__(self, value=None, validate=None):
            self.value = value
            self.validate = validate

        def to_json(self):
            result = {}
            if self.value is not None:
                result['value'] = self.value
            if self.validate is not None:
                result['validate'] = self.validate
            return result

        def __str__(self):
            return '_'.join([str(self.value), str(self.validate)])

    def __init__(self):
        self.responses = dict()
        self.handler = None

    def on_call(self, value=None, validate=None):
        key = str(PersonalStoreContext.Request(value, validate))
        self.responses[key] = PersonalStoreContext.Response()
        return self.responses[key]

    def get_response(self, request_json):
        return self.responses[
            str(
                PersonalStoreContext.Request(
                    request_json['value'], request_json['validate'],
                ),
            )
        ]

    @property
    def times_called(self):
        return self.handler.times_called


def _mock_store(mockserver, version, data_type):
    context = PersonalStoreContext()

    @mockserver.json_handler(f'/personal-market/{version}/{data_type}/store')
    def handler(request):
        response = context.get_response(request.json)

        if response.error_code is not None:
            return mockserver.make_response(
                status=response.error_code,
                json={
                    'code': str(response.error_code),
                    'message': response.error_message,
                },
            )

        return {'value': request.json['value'], 'id': response.personal_id}

    context.handler = handler
    return context


@pytest.fixture(name='mock_personal_phones_store')
def _mock_personal_phones_store(mockserver):
    return _mock_store(mockserver, 'v1', 'phones')


@pytest.fixture(name='mock_personal_emails_store')
def _mock_personal_emails_store(mockserver):
    return _mock_store(mockserver, 'v1', 'emails')
