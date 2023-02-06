import pytest


DEFAULT_CHARITY_INFO = {'status': 'never_subscribed', 'donated': False}


@pytest.fixture(name='persey_core', autouse=True)
def mock_persey_core(mockserver):
    class Context:
        def __init__(self):
            self.charity_subscription_info = DEFAULT_CHARITY_INFO

        def set_charity_subscription_info(self, charity_subscription_info):
            self.charity_subscription_info = charity_subscription_info

        def subs_status_times_called(self):
            return mock_subs_status.times_called

        def flush(self):
            mock_subs_status.flush()

    context = Context()

    @mockserver.json_handler('/persey-core/persey-core/user-ride-subs-status')
    def mock_subs_status(request):
        return mockserver.make_response(
            json={
                'by_brand': {'lavka': context.charity_subscription_info},
                'any_brand': {'status': 'is_subscribed', 'donated': True},
            },
            status=200,
        )

    return context
