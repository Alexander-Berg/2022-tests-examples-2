import pytest

from tests_grocery_orders import transactions


def _get_hash(item_id):
    return item_id


def _sum_items(items):
    sum_items = []
    for item in items:
        sum_items.append(
            {
                'item_id': item.item_id,
                'amount': str(float(item.price) * float(item.quantity)),
            },
        )
    return sum_items


@pytest.fixture(name='transactions_lavka_isr')
def mock_transactions_eda(mockserver):
    @mockserver.json_handler('/transactions-lavka-isr/v2/invoice/retrieve')
    def _mock_invoice_retrieve(request):
        assert request.json.get('id_namespace') == transactions.ID_NAMESPACE
        return context.invoice

    class Context:
        invoice = transactions.DEFAULT_INVOICE

        def retrieve_times_called(self):
            return _mock_invoice_retrieve.times_called

        def flush(self):
            _mock_invoice_retrieve.flush()

        def set_items(self, items):
            sum_to_pay = _sum_items(items)
            self.invoice['sum_to_pay'][0]['items'] = sum_to_pay
            self.invoice['held'][0]['items'] = sum_to_pay
            self.invoice['cleared'][0]['items'] = sum_to_pay
            self.invoice['transactions'][0]['sum'] = sum_to_pay
            self.invoice['transactions'][0]['initial_sum'] = sum_to_pay

    context = Context()
    return context
