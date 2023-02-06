async def test_marketplace_payment(taxi_contractor_merch_payments):
    payment_id = 'payment_id-0'

    response = await taxi_contractor_merch_payments.get(
        '/marketplace/v1/payment',
        params={'id': payment_id},
        allow_redirects=False,
    )

    assert response.status == 301
    assert (
        response.headers['Location']
        == 'https://t.me/ProMarketplaceBot?start=payment_id-0'
    )
