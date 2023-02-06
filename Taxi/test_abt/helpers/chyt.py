import re
import typing as tp


class ChytClientMock:
    calls: tp.List[tp.Any]

    def __init__(self, clients_cls, responses):
        self._responses = responses
        self._clients_cls = clients_cls
        self.calls = []

    async def execute(self, query, *args, **kwargs):
        self.calls.append(
            (self._remove_testsuite_query_name(query), args, kwargs),
        )
        self._clients_cls.calls.append(self.calls[-1])

        query_name = self._extract_testsuite_query_name(query)
        response = self._responses.get(query_name)

        if response is None:
            raise ValueError(f'No mock answer for query: {query}')

        return response

    def _remove_testsuite_query_name(self, query: str) -> str:
        self._extract_testsuite_query_name(query)
        return ''.join(query.split('\n')[1:])

    def _extract_testsuite_query_name(self, query: str) -> str:
        first_line = query.split('\n')[0]
        match = re.search('testsuite/([a-z_]+)', first_line)

        assert (
            match is not None
        ), 'First line of query must be: testsuite/<query_name>'

        return match.group(1)


class ChytClientsMock:
    calls: tp.List[tp.Any]

    def __init__(self):
        self._responses = {}
        self.calls = []

    # for test preparation
    def set_mock_response(self, query_name, response):
        self._responses[query_name] = response

    def set_mock_responses(self, responses):
        for query_name, response in responses.items():
            self.set_mock_response(query_name, response)

    # mocked method
    def get_client(self, client_config):
        return ChytClientMock(self, self._responses)
