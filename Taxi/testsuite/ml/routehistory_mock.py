import json


class RoutehistoryFixture(object):
    def __init__(self, mockserver, tvm2_client, db, load_json):
        self.mockserver = mockserver
        self.tvm2_client = tvm2_client
        self.db = db
        self.load_json = load_json
        self.expected_request = None
        self.expected_headers = None
        self.response = None
        self.called = False
        self._add_mock()

    def finalize(self):
        if self.expected_request:
            assert self.called

    def expect_request(self, request, headers=None):
        if isinstance(request, str):
            request = self.load_json(request)
        if isinstance(headers, str):
            headers = self.load_json(headers)
        self.expected_request = request
        self.expected_headers = headers

    def set_response(self, response):
        if not response:
            response = {'results': []}
        elif isinstance(response, str):
            response = self.load_json(response)
        self.response = response

    def _add_mock(self):
        self.tvm2_client.set_ticket(json.dumps({'42': {'ticket': 'ticket'}}))

        @self.mockserver.json_handler('/routehistory/routehistory/get')
        def routehistory_get(request):
            self.called = True
            assert 'X-Ya-Service-Ticket' in request.headers
            assert request.headers['X-Ya-Service-Ticket'] == 'ticket'
            if self.expected_request is not False:
                assert request.json == self.expected_request
                if self.expected_headers:
                    for key, value in self.expected_headers.items():
                        assert request.headers[key] == value
            return self.response
