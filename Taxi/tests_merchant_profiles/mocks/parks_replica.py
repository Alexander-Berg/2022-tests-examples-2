import pytest


@pytest.fixture
def mock_parks_replica(mockserver):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _parks_replica(request):
        return context.response

    class Context:
        def __init__(self):
            self.handler = _parks_replica
            self.response = {'billing_client_id': '187701087'}

    context = Context()

    return context
