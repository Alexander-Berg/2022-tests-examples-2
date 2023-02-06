import pytest


@pytest.fixture(name='eats_core_order_revision')
def mock_eats_core_order_revision(mockserver):
    class Context:
        def __init__(self):
            self.check_list_data = None
            self.check_customer_services_data = None
            self.data_revisions = None
            self.data_customer_services = None

        def check_list(self, **kwargs):
            self.check_list_data = kwargs

        def check_customer_services(self, **kwargs):
            self.check_customer_services_data = kwargs

        def mock_list(self, revisions):
            self.data_revisions = revisions

        def mock_customer_services(self, customer_services):
            self.data_customer_services = customer_services

        def list_times_called(self):
            return _mock_list.times_called

        def customer_services_times_called(self):
            return _mock_customer_services_details.times_called

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1/order-revision/list',
    )
    def _mock_list(request):
        if context.check_list_data is not None:
            for key, value in context.check_list_data.items():
                assert request.args[key] == value, key

        return {
            'order_id': request.args['order_id'],
            'revisions': context.data_revisions or [],
        }

    @mockserver.json_handler(
        '/eats-core-order-revision'
        + '/internal-api/v1/order-revision/customer-services/details',
    )
    def _mock_customer_services_details(request):
        if context.check_customer_services_data is not None:
            for key, value in context.check_customer_services_data.items():
                assert request.json[key] == value, key

        return {
            'revision_id': request.json['revision_id'],
            'created_at': '2021-06-12T12:40:00+00:00',
            'customer_services': context.data_customer_services or [],
        }

    context = Context()
    return context
