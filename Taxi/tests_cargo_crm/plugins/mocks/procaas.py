import pytest


@pytest.fixture(name='procaas_ctx')
def _procaas_ctx(mockserver):
    class Context:
        def __init__(self):
            self.create_event_response = None
            self.read_events_response = None
            self.events = []

        def get_create_event_response(self, request, scope, queue):
            if self.create_event_response is not None:
                return self.create_event_response

            respbody = {'event_id': self.extract_idempotency_token(request)}
            return mockserver.make_response(status=200, json=respbody)

        def get_read_events_response(self, request, scope, queue):
            if self.read_events_response is not None:
                return self.read_events_response

            respbody = {'events': self.events}
            return mockserver.make_response(status=200, json=respbody)

        @staticmethod
        def extract_idempotency_token(request):
            return request.headers['X-Idempotency-Token']

    return Context()


@pytest.fixture(name='proxy_handler_get_events')
def _proxy_handler_get_events(mockserver, procaas_ctx):
    @mockserver.json_handler('/cargo-crm/procaas/caching-proxy/events')
    def handler(request):
        scope = request.query['scope'][0]
        queue = request.query['queue'][0]
        return procaas_ctx.get_read_events_response(request, scope, queue)

    return handler


@pytest.fixture(name='procaas_handler_create_event')
def _procaas_handler_create_event(mockserver, procaas_ctx):
    url = r'/processing/v1/(?P<scope>\w+)/(?P<queue>\w+)/create-event'

    @mockserver.json_handler(url, regex=True)
    def handler(request, scope, queue):
        return procaas_ctx.get_create_event_response(request, scope, queue)

    return handler
