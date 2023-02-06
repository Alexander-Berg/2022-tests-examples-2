from eats_tests.utils import order_statuses


def test_basic_happy_path(
        launch, core, eats_cart, list_payment_methods, stq, cargo_claims,
):
    launch.set_host('http://eats-launch.eda.yandex.net')
    core.set_host('https://eda.yandex')
    eats_cart.set_host('http://eats-cart.eda.yandex.net')
    stq.set_host('http://stq-agent.taxi.yandex.net')

    list_payment_methods.set_payment_methods(
        data=[{'id': 'card-1', 'number': '51002222****4444'}],
    )

    cargo_claims.add_performer_for_user(
        user_phone='+79682777450',
        yandex_uid='333',
        courier_id=2,
        name='test1',
        legal_name='test_legal_name1',
    )

    response = launch.launch_native(
        session_eater_id=3, passport_eater_id=123, passport_uid=333,
    )
    assert response.status_code == 200

    response = eats_cart.add_item(
        item_id=1,
        eater_id=3,
        passport_uid=333,
        phone_id='9aef863cae894bb39a9fabaea851fcd1',
        email_id='1',
        latitude=55.766491,
        longitude=37.622333,
    )
    assert response.status_code == 200, response.text

    response = core.go_checkout(
        address_identity=1,
        provider='eats',
        eater_id=3,
        passport_uid=333,
        latitude=55.766491,
        longitude=37.622333,
    )
    assert response.status_code == 200, response.text

    offers = response.json().get('offers', None)
    assert offers

    possible_payment = offers[0].get('possiblePayment')
    cost_for_customer = float(possible_payment['costForCustomer']['value'])

    response = core.create_order(
        eater_id=3,
        user_email='cccccc@ccc.ccc',
        user_phone_number='+79682777450',
        user_first_name='Козьма',
        latitude=55.766491,
        longitude=37.622333,
        payment_method_id=5,
        persons_quantity=1,
        card_id='card-1',
        passport_uid=333,
        cost_for_customer=cost_for_customer,
    )
    assert response.status_code == 200, response.text
    order_nr = response.json()['order_nr']

    stq.payment_confirmed_task(order_id=order_nr)

    core.wait_for_order_status_changed(
        order_nr=order_nr,
        eater_id=3,
        passport_uid=333,
        expected_status=order_statuses.EatsOrderStatus.CALL_CENTER_CONFIRMED,
        max_timeout=30,
    )

    core.wait_for_courier_assigned(
        order_nr=order_nr, eater_id=3, passport_uid=333, max_timeout=120,
    )

    cargo_claims.mark_order_as_delivered(order_nr=order_nr)

    core.wait_for_order_status_changed(
        order_nr=order_nr,
        eater_id=3,
        passport_uid=333,
        expected_status=order_statuses.EatsOrderStatus.ARRIVED_TO_CUSTOMER,
        max_timeout=60,
    )
