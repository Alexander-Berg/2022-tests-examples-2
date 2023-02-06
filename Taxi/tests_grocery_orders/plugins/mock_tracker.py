import json

import pytest

RESPONSE = {'id': 'super_id', 'key': 'super_key'}


@pytest.fixture(name='tracker', autouse=True)
def mock_tracker(mockserver):
    class Context:
        def __init__(self):
            self.response_code = '201'
            self.orderid = None
            self.summary = None
            self.queue = None
            self.description = None
            self.tags = None
            self.sendchatterbox = None

        def set_response_code(self, response_code):
            self.response_code = str(response_code)

        def set_request_data(
                self,
                order_id,
                queue,
                summary,
                description=None,
                tags=None,
                create_chatterbox_ticket=False,
        ):
            self.orderid = order_id
            self.queue = queue
            self.summary = summary

            if description is not None:
                self.description = description
            if tags is not None:
                self.tags = tags
            if create_chatterbox_ticket:
                self.sendchatterbox = 'Да'

        def check_request(self, request):
            if self.orderid is not None:
                assert request['OrderId'] == self.orderid
                assert request['unique'] == '{}-feedback'.format(self.orderid)
                assert request['queue'] == self.queue
                assert request['summary'] == self.summary
            if self.description is not None:
                assert request['description'] == self.description
            if self.tags is not None:
                assert request['tags'] == self.tags
            if self.sendchatterbox is not None:
                assert request['sendChatterbox'] == self.sendchatterbox

        def times_called(self):
            return mock_v2_issues.times_called

        def flush(self):
            mock_v2_issues.flush()

    context = Context()

    @mockserver.json_handler('/api-tracker-uservices/v2/issues')
    def mock_v2_issues(request):
        context.check_request(request.json)
        return mockserver.make_response(
            json.dumps(RESPONSE), context.response_code,
        )

    return context
