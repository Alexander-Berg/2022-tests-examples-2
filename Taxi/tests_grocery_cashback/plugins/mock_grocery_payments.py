from typing import List

import pytest

from .. import models

RETRIEVE = 'retrieve-handler'


@pytest.fixture(name='grocery_payments', autouse=True)
def mock_grocery_payments(mockserver):
    class Context:
        def __init__(self):
            self.error_code = {}
            self.transactions = []

        def add_transaction(self, status, items: List[models.TransactionItem]):
            self.transactions.append(
                models.Transaction(status=status, items=items),
            )

        def set_error_code(self, handler, code):
            self.error_code[handler] = code

        def times_retrieve_called(self):
            return mock_retrieve.times_called

        def flush_all(self):
            mock_retrieve.flush()

    context = Context()

    @mockserver.json_handler('/grocery-payments/payments/v1/retrieve')
    def mock_retrieve(request):
        if RETRIEVE in context.error_code:
            code = context.error_code[RETRIEVE]
            return mockserver.make_response('{}', code)

        transactions = []
        for transaction in context.transactions:
            items = []
            for item in transaction.items:
                items.append(
                    {
                        'item_id': item.item_id,
                        'quantity': item.quantity,
                        'amount': item.amount,
                        'price': item.get_price(),
                    },
                )

            transactions.append(
                {
                    'created': '2020-03-13T07:19:00+00:00',
                    'status': transaction.status,
                    'transaction_type': 'payment',
                    'payment_method': {'type': 'card', 'id': 'payment_id'},
                    'external_payment_id': 'external_payment_id',
                    'items': items,
                },
            )

        response = {'transactions': transactions}

        return response

    return context
