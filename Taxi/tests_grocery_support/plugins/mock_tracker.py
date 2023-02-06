import json

import pytest

CREATE_ISSUE_RESPONSE = {'id': 'super_id', 'key': 'super_key'}
ISSUES_COUNT_RESPONSE = 1

CREATE_ISSUE_HANDLER = 'issues'
ISSUES_COUNT_HANDLER = 'issues_count'


@pytest.fixture(name='tracker', autouse=True)
def mock_tracker(mockserver):
    class Context:
        def __init__(self):
            self.response = {
                CREATE_ISSUE_HANDLER: CREATE_ISSUE_RESPONSE,
                ISSUES_COUNT_HANDLER: ISSUES_COUNT_RESPONSE,
            }
            self.response_code = {
                CREATE_ISSUE_HANDLER: '201',
                ISSUES_COUNT_HANDLER: '200',
            }
            self.request = {}

        def set_response_code(
                self, response_code, handler=CREATE_ISSUE_HANDLER,
        ):
            self.response_code[handler] = str(response_code)

        def check_request(self, request, handler=CREATE_ISSUE_HANDLER):
            self.request[handler] = request

        def times_called(self, handler=CREATE_ISSUE_HANDLER):
            if handler == CREATE_ISSUE_HANDLER:
                return mock_v2_issues.times_called
            return mock_v2_issues_count.times_called

        def flush(self):
            mock_v2_issues.flush()
            mock_v2_issues_count.flush()

    context = Context()

    @mockserver.json_handler('/api-tracker-uservices/v2/issues')
    def mock_v2_issues(request):
        if CREATE_ISSUE_HANDLER in context.request:
            context_request = context.request[CREATE_ISSUE_HANDLER]
            if context_request is not None:
                for key in context_request:
                    assert context_request[key] == request.json[key]
        return mockserver.make_response(
            json.dumps(context.response[CREATE_ISSUE_HANDLER]),
            context.response_code[CREATE_ISSUE_HANDLER],
        )

    @mockserver.json_handler('/api-tracker-uservices/v2/issues/_count')
    def mock_v2_issues_count(request):
        if ISSUES_COUNT_HANDLER in context.request:
            context_request = context.request[ISSUES_COUNT_HANDLER]
            if context_request is not None:
                for key in context_request:
                    assert context_request[key] == request.json[key]
        return mockserver.make_response(
            json.dumps(context.response[ISSUES_COUNT_HANDLER]),
            context.response_code[ISSUES_COUNT_HANDLER],
        )

    return context
