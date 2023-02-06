import pytest


@pytest.fixture(name='grocery_goals')
def mock_grocery_goals(mockserver):
    class Context:
        def __init__(self):
            self.skus = None
            self.order_id = None
            self.response_http_code = 200
            self.error_code = None
            self.failed_skus = None

        def reserve_times_called(self):
            return mock_reserve.times_called

        def release_times_called(self):
            return mock_release.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-goals/internal/v1/goals/v1/reward/reserve',
    )
    def mock_reserve(request):
        assert request.json['skus'] == context.skus
        assert request.json['order_id'] == context.order_id

        if context.response_http_code != 200:
            return mockserver.make_response(
                status=context.response_http_code,
                json={
                    'code': context.error_code,
                    'failed_skus': context.failed_skus,
                },
            )
        return {}

    @mockserver.json_handler(
        '/grocery-goals/internal/v1/goals/v1/reward/release',
    )
    def mock_release(request):
        assert request.json['skus'] == context.skus
        assert request.json['order_id'] == context.order_id

        if context.response_http_code != 200:
            return mockserver.make_response(
                status=context.response_http_code,
                json={
                    'code': context.error_code,
                    'failed_skus': context.failed_skus,
                },
            )
        return {}

    return context
