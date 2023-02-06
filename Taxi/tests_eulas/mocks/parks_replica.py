import pytest


class ParksReplicaRetrieveContext:
    class Response:
        def __init__(self):
            self.park_data = None
            self.error_code = None

    class Expectations:
        def __init__(self):
            self.park_id = None
            self.fields = None

    class Call:
        def __init__(self):
            self.response = ParksReplicaRetrieveContext.Response()
            self.expected = ParksReplicaRetrieveContext.Expectations()

    def __init__(self):
        self.call = ParksReplicaRetrieveContext.Call()
        self.handler = None

    @property
    def times_called(self):
        return self.handler.times_called


@pytest.fixture(name='mock_parks_replica_retrieve')
def mock_retrieve(mockserver):
    context = ParksReplicaRetrieveContext()

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def handler(request):
        expected = context.call.expected
        response = context.call.response

        if expected.park_id is not None:
            assert request.json['id_in_set'] == [expected.park_id]
        if expected.fields is not None:
            assert request.json['projection'] == expected.fields
        if response.error_code is not None:
            return mockserver.make_response(
                status=response.error_code,
                json={'code': str(response.error_code), 'message': 'error'},
            )

        return {
            'parks': [
                {'data': response.park_data, 'park_id': expected.park_id},
            ],
        }

    context.handler = handler
    return context
