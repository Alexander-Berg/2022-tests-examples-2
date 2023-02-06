async def test_trust_callback(web_app_client, stq):
    # when Trust posts a callback for some_invoice_id
    response = await web_app_client.post(
        '/v1/callback/trust/payment/some_invoice_id',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data='mode=result&purchase_token=token&trust_refund_id=refund',
    )
    content = await response.text()
    assert response.status == 200, f'response content={content!r}'

    # then we call transactions_events for some_invoice_id
    assert stq.transactions_events.times_called == 1
    assert stq.transactions_events.next_call()['id'] == 'some_invoice_id'


async def test_callback(web_app_client, stq):
    # When some service posts a callback for some_invoice_id
    response = await web_app_client.post(
        '/v1/callback/payment',
        json={
            'invoice_id': 'some_invoice_id',
            'mode': 'result',
            'purchase_token': 'purchase_token',
            'trust_refund_id': 'trust_refund_id',
        },
    )
    assert response.status == 200

    # then we call transactions_events for some_invoice_id
    assert stq.transactions_events.times_called == 1
    assert stq.transactions_events.next_call()['id'] == 'some_invoice_id'
