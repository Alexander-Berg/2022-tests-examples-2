import pytest


@pytest.fixture(name='grocery_crm')
def mock_grocery_crm(mockserver):
    class Context:
        def __init__(self):
            self.informer = None
            self.check_informer_request = {}
            self.get_informer_request = None

        def set_user_informer(self, informer_id, informer_info):
            self.informer = {'id': informer_id, 'info': informer_info}

        def check_informer_check_request(self, request, headers):
            self.check_informer_request['request'] = request
            self.check_informer_request['headers'] = headers

        def check_informer_get_request(self, request):
            self.get_informer_request = request

        def times_check_informer_called(self):
            return mock_check_informer.times_called

        def times_get_informer_called(self):
            return mock_get_informer.times_called

    context = Context()

    @mockserver.json_handler('/grocery-crm/internal/user/v1/check-informer')
    def mock_check_informer(request):
        if 'request' in context.check_informer_request:
            for key, value in context.check_informer_request[
                    'request'
            ].items():
                assert request.json[key] == value
        if 'headers' in context.check_informer_request:
            for key, value in context.check_informer_request[
                    'headers'
            ].items():
                assert request.headers[key] == value
        if context.informer is not None:
            return {'informer_id': context.informer['id']}
        return {}

    @mockserver.json_handler('/grocery-crm/internal/user/v1/get-informer')
    def mock_get_informer(request):
        if context.get_informer_request is not None:
            assert request.json == context.get_informer_request
        if context.informer is not None:
            return {'informer': context.informer['info']}
        return mockserver.make_response('', 404)

    return context
