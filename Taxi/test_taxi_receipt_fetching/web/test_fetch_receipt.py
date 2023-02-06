async def test_fetch_nothing_cached(web_app_client):
    resp = await web_app_client.post('/receipts', json={'order_ids': ['123']})

    assert resp.status == 200
    assert await resp.json() == {'receipts': []}


async def test_fetch_cached_receipt(web_app_client, create_receipt):
    order_id = '123'
    receipt_url = 'https://kek.com/receipt'
    await create_receipt(order_id, receipt_url)

    resp = await web_app_client.post(
        '/receipts', json={'order_ids': [order_id]},
    )

    assert resp.status == 200
    assert await resp.json() == {
        'receipts': [{'order_id': order_id, 'receipt_url': receipt_url}],
    }
