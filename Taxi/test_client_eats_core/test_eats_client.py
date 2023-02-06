async def test_go_checkout(library_context, mockserver, load_json):
    @mockserver.json_handler('/api/v2/cart/go-checkout')
    def go_checkout():  # pylint: disable=W0612
        return mockserver.make_response(
            json=load_json('go_checkout.json'), status=200,
        )

    response = await library_context.client_eats_core.go_checkout(
        phpsessid='test',
        eats_user_id=1,
        user_address_id=1,
        phone_id='aaaa',
        email_id='bbbb',
        yandex_uid='123',
        longitude=0.000,
        latitude=0.000,
    )
    assert 'offers' in response


async def test_create_order(library_context, mockserver, load_json):
    @mockserver.json_handler('/api/v1/orders')
    def create_order():  # pylint: disable=W0612
        return mockserver.make_response(
            json=load_json('create_order.json'), status=200,
        )

    order_nr = await library_context.client_eats_core.create_order(
        user_email='aaa@aaa',
        user_phone_number='+79006666666',
        user_first_name='test',
        longitude=54.232323,
        latitude=34.678436,
        phpsessid='test',
        eats_user_id=3,
        payment_method_id=5,
    )
    assert order_nr == '220329-214131'
