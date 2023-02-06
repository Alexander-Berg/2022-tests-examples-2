import pytest


@pytest.fixture(name='mock_market_utils')
def mock_market_utils(mockserver):
    def _empty_callback(request):
        pass

    class Context:
        def __init__(self):
            self.check_api_add_request_body = (None,)
            self.check_api_add_response_code = (None,)
            self.check_api_add_check_callback = (_empty_callback,)

        def check_api_add_request(
                self,
                check_request_body=None,
                response_code=None,
                check_callback=_empty_callback,
        ):
            self.check_api_add_request_body = check_request_body
            self.check_api_add_response_code = response_code
            self.check_api_add_check_callback = check_callback

        @property
        def api_event_add_called(self):
            return mock_market_utils_event_add.times_called

    @mockserver.json_handler('/market-utils/api/event/add')
    def mock_market_utils_event_add(request):
        context.check_api_add_check_callback(request)

        # remove uncheckable fields
        assert 'sourceId' in request.json
        assert 'checkouter_event_created_ts' in request.json['data']

        del request.json['sourceId']
        del request.json['data']['checkouter_event_created_ts']

        if context.check_api_add_request_body is not None:
            assert request.json == context.check_api_add_request_body

        return mockserver.make_response(
            status=context.check_api_add_response_code,
        )

    context = Context()
    return context
