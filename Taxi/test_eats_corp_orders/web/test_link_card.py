import pytest


async def test_add_new_corp_method(
        taxi_eats_corp_orders_web,
        eats_user,
        check_payment_methods_db,
        load_json,
        yandex_uid,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment-method/link',
        json={
            'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
            'type': 'corp',
            'name': 'Yandex Badge',
        },
        headers={'X-Eats-User': eats_user, 'X-Yandex-UID': yandex_uid},
    )
    assert response.status == 200

    check_payment_methods_db(load_json('expected.json')['new_corp'])


async def test_add_new_card_method(
        taxi_eats_corp_orders_web,
        eats_user,
        check_payment_methods_db,
        load_json,
        yandex_uid,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment-method/link',
        json={
            'id': 'card:a45f93536c0a402c904dd458a8bd3a88:RUB',
            'type': 'card',
            'number': '1234',
            'system': 'mastercard',
        },
        headers={'X-Eats-User': eats_user, 'X-Yandex-UID': yandex_uid},
    )
    assert response.status == 200

    check_payment_methods_db(load_json('expected.json')['new_card'])


@pytest.mark.pgsql('eats_corp_orders', files=['existing_corp_method.sql'])
async def test_add_new_card_method_when_corp_exists(
        taxi_eats_corp_orders_web,
        eats_user,
        check_payment_methods_db,
        load_json,
        yandex_uid,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment-method/link',
        json={
            'id': 'card:a45f93536c0a402c904dd458a8bd3a88:RUB',
            'type': 'card',
            'number': '1234',
            'system': 'mastercard',
        },
        headers={'X-Eats-User': eats_user, 'X-Yandex-UID': yandex_uid},
    )
    assert response.status == 200

    check_payment_methods_db(
        load_json('expected.json')['new_card_corp_exists'],
    )


@pytest.mark.pgsql('eats_corp_orders', files=['existing_corp_method.sql'])
async def test_overwrite_existing(
        taxi_eats_corp_orders_web,
        eats_user,
        check_payment_methods_db,
        load_json,
        yandex_uid,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment-method/link',
        json={'id': 'corp:new:RUB', 'type': 'corp', 'name': 'Elegant name'},
        headers={'X-Eats-User': eats_user, 'X-Yandex-UID': yandex_uid},
    )
    assert response.status == 200

    check_payment_methods_db(load_json('expected.json')['overwrite_existing'])
