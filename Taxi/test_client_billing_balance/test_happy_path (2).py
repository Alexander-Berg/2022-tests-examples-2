async def test_billing_balance(library_context, patch):
    @patch('taxi.clients.billing_v2.BalanceClient.create_offer')
    async def test_request(some_argument):
        return

    await library_context.client_billing_balance_v2.create_offer(1)

    assert test_request.calls == [{'some_argument': 1}]
