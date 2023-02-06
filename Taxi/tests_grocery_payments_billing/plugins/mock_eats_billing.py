import pytest


@pytest.fixture(name='eats_billing')
def mock_eats_billing(mockserver):
    class Context:
        def __init__(self):
            self.check_create_data = None

        def check_create_request(self, data):
            self.check_create_data = data

        def create_times_called(self):
            return _mock_create_billing_doc.times_called

    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_create_billing_doc(request):
        if context.check_create_data is not None:
            assert request.json == context.check_create_data

        return {'status': '200'}

    context = Context()
    return context
