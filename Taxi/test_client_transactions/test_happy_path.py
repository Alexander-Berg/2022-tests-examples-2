async def test_transactions(library_context, mockserver, patch):
    @mockserver.json_handler('/transactions/invoice/update')
    def _transaction_invoice_update(request):
        tvm_header = request.headers['X-Ya-Service-Ticket']
        assert tvm_header == 'random_tvm_ticket'
        assert request.json == {
            'id': 'random_order',
            'operation_id': '1.2',
            'originator': 'antifraud',
            'items': [],
            'version': 123,
            'payment': {
                'type': 'card',
                'method': 'card-payment_id',
                'billing_id': 'billing_id',
            },
        }
        return {}

    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    # pylint: disable=unused-variable
    async def get_auth_headers(*args, **kwargs):
        return {'X-Ya-Service-Ticket': 'random_tvm_ticket'}

    payment = {
        'type': 'card',
        'method': 'card-payment_id',
        'billing_id': 'billing_id',
    }

    await library_context.transactions.invoice_update(
        'random_order',
        operation_id='1.2',
        items=[],
        payment=payment,
        originator='antifraud',
        version=123,
        log_extra=None,
    )
    assert _transaction_invoice_update.next_call() is not None
