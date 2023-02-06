import pytest


class BillingOrdersContext:
    def __init__(self):
        self.docs = []
        self.calls = 0
        self.docs_count = 0

    def add_doc(self, doc):
        self.docs.append(doc)
        self.docs_count += 1
        return self.docs_count


@pytest.fixture
def billing_orders(mockserver):
    billing_orders_ctx = BillingOrdersContext()

    @mockserver.json_handler('/billing_orders/v1/process_event')
    def _mock_process_event(request):
        doc_id = billing_orders_ctx.add_doc(request.get_data())
        billing_orders_ctx.calls += 1
        return {'doc': {'id': doc_id}}

    return billing_orders_ctx
