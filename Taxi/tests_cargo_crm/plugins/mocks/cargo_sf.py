import pytest


@pytest.fixture(name='amo_lead_event_set_response')
def _amo_lead_event_set_response():
    class Context:
        def __init__(self):
            self.status_code = 200
            self.request_json = {}
            self.response_json = {'id': 'amo_object_id'}

        def set_response(
                self,
                status_code: int,
                request_json: dict,
                response_json: dict,
        ):
            self.status_code = status_code
            self.request_json = request_json
            self.response_json = response_json

        def get_context(self, request):
            return {
                'status_code': self.status_code,
                'request_json': self.request_json,
                'response_json': self.response_json,
            }

    return Context()


@pytest.fixture(name='amo_lead_event_response', autouse=True)
def _amo_lead_event_response(mockserver, amo_lead_event_set_response):
    @mockserver.json_handler(
        '/cargo-sf/internal/cargo-sf/amocrm/internal-requests/lead-event',
    )
    def handler(request):
        query_context = amo_lead_event_set_response.get_context(request)
        if query_context['status_code'] == 200:
            assert request.json == query_context['request_json']
        return mockserver.make_response(
            status=query_context['status_code'],
            json=query_context['response_json'],
        )

    return handler
