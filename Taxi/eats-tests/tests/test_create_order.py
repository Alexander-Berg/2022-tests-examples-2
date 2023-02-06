def test_create_order_and_reject_by_payment_system(
        launch, core, eats_cart, list_payment_methods, stq, mysql,
):
    launch.set_host('http://eats-launch.eda.yandex.net')
    core.set_host('https://eda.yandex')
    eats_cart.set_host('http://eats-cart.eda.yandex.net')
    stq.set_host('http://stq-agent.taxi.yandex.net')

    list_payment_methods.set_payment_methods(
        data=[{'id': 'card-1', 'number': '51002222****4444'}],
    )

    response = launch.launch_native(
        session_eater_id=4, passport_eater_id=124, passport_uid=666,
    )
    assert response.status_code == 200, response.text

    response = eats_cart.add_item(
        item_id=1,
        eater_id=4,
        passport_uid=666,
        phone_id='9aef863cae894bb39a9fabaea851fcde',
        email_id='2',
        latitude=55.766491,
        longitude=37.622333,
    )
    assert response.status_code == 200, response.text

    response = core.go_checkout(
        address_identity=2,
        provider='eats',
        eater_id=4,
        passport_uid=666,
        latitude=55.766491,
        longitude=37.622333,
    )
    assert response.status_code == 200, response.text

    offers = response.json().get('offers', None)
    assert offers

    possible_payment = offers[0].get('possiblePayment')
    cost_for_customer = float(possible_payment['costForCustomer']['value'])

    response = core.create_order(
        eater_id=4,
        user_email='dddddd@ddd.ddd',
        user_phone_number='+79682777666',
        user_first_name='Иван',
        latitude=55.766491,
        longitude=37.622333,
        payment_method_id=5,
        persons_quantity=1,
        card_id='card-1',
        passport_uid=666,
        cost_for_customer=cost_for_customer,
    )
    assert response.status_code == 200, response.text
    order_nr = response.json()['order_nr']

    stq.payment_canceled_task(order_id=order_nr)
