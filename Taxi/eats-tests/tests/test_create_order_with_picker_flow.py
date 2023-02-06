from eats_tests.utils import order_statuses


def test_create_order_in_retail(
        launch,
        core,
        eats_cart,
        list_payment_methods,
        stq,
        picker,
        cargo_claims,
):
    launch.set_host('http://eats-launch.eda.yandex.net')
    core.set_host('https://eda.yandex')
    eats_cart.set_host('http://eats-cart.eda.yandex.net')
    stq.set_host('http://stq-agent.taxi.yandex.net')
    picker.set_host('http://eats-picker-orders.eda.yandex.net')

    eater_id = 5
    passport_uid = 555

    list_payment_methods.set_payment_methods(
        data=[{'id': 'card-1', 'number': '51002222****4444'}],
    )

    cargo_claims.add_performer_for_user(
        user_phone='+79682777000',
        yandex_uid='555',
        courier_id=3,
        name='test2',
        legal_name='test_legal_name2',
    )

    response = launch.launch_native(
        session_eater_id=5, passport_eater_id=125, passport_uid=passport_uid,
    )
    assert response.status_code == 200

    response = eats_cart.add_item(
        item_id=4,
        eater_id=eater_id,
        passport_uid=passport_uid,
        phone_id='9aef863cae894bb39a9fabaea851fabc',
        email_id='3',
        latitude=55.766491,
        longitude=37.622333,
    )
    assert response.status_code == 200, response.text

    response = core.go_checkout(
        address_identity=3,
        provider='eats',
        eater_id=eater_id,
        passport_uid=passport_uid,
        latitude=55.766491,
        longitude=37.622333,
    )
    assert response.status_code == 200, response.text

    offers = response.json().get('offers', None)
    assert offers

    possible_payment = offers[0].get('possiblePayment')
    cost_for_customer = float(possible_payment['costForCustomer']['value'])

    response = core.create_order(
        eater_id=eater_id,
        user_email='test@test.ru',
        user_phone_number='+79682777000',
        user_first_name='Test',
        latitude=55.766491,
        longitude=37.622333,
        payment_method_id=5,
        persons_quantity=1,
        card_id='card-1',
        passport_uid=passport_uid,
        cost_for_customer=cost_for_customer,
        address_comment=(
            'wait_after_picking - 0, '
            'wait_after_picked_up - 0, '
            'wait_after_packing - 0'
        ),
    )
    assert response.status_code == 200, response.text
    order_nr = response.json()['order_nr']

    stq.payment_confirmed_task(order_id=order_nr)

    core.wait_for_order_status_changed(
        order_nr=order_nr,
        eater_id=eater_id,
        passport_uid=passport_uid,
        expected_status=order_statuses.EatsOrderStatus.CALL_CENTER_CONFIRMED,
        max_timeout=30,
    )

    core.set_host('http://eda.yandex-team.ru')
    response = core.order_send_immediately(order_nr=order_nr)
    assert response.status_code == 200, response.text

    picker.wait_order_sync(order_nr=order_nr)
    picker.wait_for_picker_complete_order(order_nr=order_nr)
