import pytest


@pytest.mark.experiments3(filename='maas_user_promotion_exp.json')
@pytest.mark.experiments3(filename='maas_shortcuts_params_exp.json')
@pytest.mark.experiments3(filename='maas_zone_exp.json')
@pytest.mark.translations(
    client_messages={
        'maas_shortcuts.account.title': {'ru': 'Купить абонемент'},
        'maas_shortcuts.account.subtitle': {'ru': 'Поездки по подписке'},
        'maas_shortcuts.ride_to_metro.title': {'ru': 'К метро'},
        'maas_shortcuts.ride_to_metro.subtitle': {'ru': 'Абонемент'},
        'maas_shortcuts.ride_from_metro.title': {'ru': 'От метро'},
        'maas_shortcuts.ride_from_metro.subtitle': {'ru': 'Абонемент 2'},
    },
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'phone_id, to_metro, title, subtitle, deeplink, trips_left,'
    'has_top_scenario',
    [
        pytest.param(
            'no_subscription_phone_id',
            True,
            'Купить абонемент',
            'Поездки по подписке',
            'yandextaxi://maas-ride?mode=account',
            0,
            True,
            id='no_subscription',
        ),
        pytest.param(
            'expired_phone_id',
            True,
            'Купить абонемент',
            'Поездки по подписке',
            'yandextaxi://maas-ride?mode=account',
            0,
            False,
            id='expired_subscription',
        ),
        pytest.param(
            'active_phone_id',
            True,
            'К метро',
            'Абонемент',
            'yandextaxi://maas-ride?mode=ride_to_metro'
            '&coupon=test_coupon_id',
            1,
            True,
            id='active_subscription_to_metro',
        ),
        pytest.param(
            'active_phone_id',
            False,
            'От метро',
            'Абонемент 2',
            'yandextaxi://maas-ride?mode=ride_from_metro'
            '&coupon=test_coupon_id',
            1,
            True,
            id='active_subscription_from_metro',
        ),
        pytest.param(
            'active_phone_id',
            False,
            '',
            '',
            '',
            0,
            False,
            id='active_subscription_no_trips_left',
        ),
        pytest.param(
            'active_phone_id',
            False,
            'От метро',
            'Абонемент 2',
            'yandextaxi://maas-ride?mode=ride_from_metro'
            '&coupon=test_coupon_id',
            None,
            True,
            id='active_subscription_coupons_failed',
        ),
    ],
)
async def test_products(
        taxi_maas,
        mockserver,
        load_json,
        to_metro,
        phone_id,
        title,
        subtitle,
        deeplink,
        trips_left,
        has_top_scenario,
        coupon_state_mock,
):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        response_file = 'stops_nearby_response.json'

        return mockserver.make_response(json=load_json(response_file))

    await taxi_maas.invalidate_caches()

    yandex_uid = '123456'
    coupon_state_mock(
        phone_id,
        error_code=222 if trips_left is None else None,
        trips_count=trips_left,
        coupon_id='test_coupon_id',
        yandex_uid=yandex_uid,
    )
    point_a = [37.5, 55.5] if to_metro else [37.467, 55.736]
    response = await taxi_maas.post(
        '/4.0/maas/v1/products',
        headers={
            'X-Yandex-Uid': yandex_uid,
            'X-YaTaxi-UserId': 'testsuite',
            'X-YaTaxi-PhoneId': phone_id,
        },
        json={'point_a': point_a, 'appearance_mode': 'default'},
    )
    assert response.status_code == 200

    if not has_top_scenario:
        assert response.json()['scenario_tops'] == []
        return

    assert len(response.json()['scenario_tops']) == 1
    result_scenario = response.json()['scenario_tops'][0]
    assert result_scenario['scenario'] == 'maas'

    assert len(result_scenario['shortcuts']) == 1
    result_shortcut = result_scenario['shortcuts'][0]
    assert result_shortcut['content'] == {
        'color': '#EAE8E2',
        'subtitle': subtitle,
        'text_color': '#21201F',
        'title': title,
        'overlays': [{'image_tag': 'car_image_tag', 'shape': 'car'}],
    }
    assert result_shortcut['scenario'] == 'maas'
    assert result_shortcut['scenario_params'] == {
        'maas_params': {'deeplink': deeplink},
    }


@pytest.mark.experiments3(filename='maas_user_promotion_exp.json')
@pytest.mark.experiments3(filename='maas_shortcuts_params_exp.json')
@pytest.mark.experiments3(filename='maas_zone_exp.json')
@pytest.mark.translations(
    client_messages={
        'maas_shortcuts.account.title': {'ru': 'Купить абонемент'},
        'maas_shortcuts.account.subtitle': {'ru': 'Поездки по подписке'},
        'maas_shortcuts.ride_to_metro.title': {'ru': 'К метро'},
        'maas_shortcuts.ride_to_metro.subtitle': {'ru': 'Абонемент'},
        'maas_shortcuts.ride_from_metro.title': {'ru': 'От метро'},
        'maas_shortcuts.ride_from_metro.subtitle': {'ru': 'Абонемент 2'},
    },
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_ultima(taxi_maas, mockserver, load_json, coupon_state_mock):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        return mockserver.make_response(
            json=load_json('stops_nearby_response.json'),
        )

    yandex_uid = '123456'
    phone_id = 'active_phone_id'
    title = 'К метро'
    subtitle = 'Абонемент'
    deeplink = (
        'yandextaxi://maas-ride?mode=ride_to_metro&coupon=test_coupon_id'
    )
    coupon_state_mock(
        phone_id,
        trips_count=1,
        coupon_id='test_coupon_id',
        yandex_uid=yandex_uid,
    )
    response = await taxi_maas.post(
        '/4.0/maas/v1/products',
        headers={
            'X-Yandex-Uid': yandex_uid,
            'X-YaTaxi-UserId': 'testsuite',
            'X-YaTaxi-PhoneId': phone_id,
        },
        json={'point_a': [37.5, 55.5], 'appearance_mode': 'ultima'},
    )
    assert response.status_code == 200
    assert len(response.json()['scenario_tops']) == 1
    result_scenario = response.json()['scenario_tops'][0]
    assert result_scenario['scenario'] == 'maas'

    assert len(result_scenario['shortcuts']) == 1
    result_shortcut = result_scenario['shortcuts'][0]
    assert result_shortcut['content'] == {
        'color': '#222222',
        'subtitle': subtitle,
        'text_color': '#21201F',
        'title': title,
        'overlays': [{'image_tag': 'ultima_car_image_tag', 'shape': 'car'}],
    }
    assert result_shortcut['scenario'] == 'maas'
    assert result_shortcut['scenario_params'] == {
        'maas_params': {'deeplink': deeplink},
    }


@pytest.mark.experiments3(filename='maas_user_promotion_exp.json')
@pytest.mark.experiments3(filename='maas_shortcuts_params_exp_with_extra.json')
@pytest.mark.experiments3(filename='maas_zone_exp.json')
@pytest.mark.translations(
    client_messages={
        'maas_shortcuts.account.title': {'ru': 'Купить абонемент'},
        'maas_shortcuts.account.subtitle': {'ru': 'Поездки по подписке'},
        'maas_shortcuts.ride_to_metro.title': {'ru': 'К метро'},
        'maas_shortcuts.ride_to_metro.subtitle': {'ru': 'Абонемент'},
        'maas_shortcuts.ride_from_metro.title': {'ru': 'От метро'},
        'maas_shortcuts.ride_from_metro.subtitle': {'ru': 'Абонемент 2'},
    },
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_products_extra_shortcuts(
        taxi_maas, mockserver, load_json, coupon_state_mock,
):
    @mockserver.json_handler('/persuggest/internal/persuggest/v1/stops_nearby')
    def _stops_nearby(request):
        return mockserver.make_response(
            json=load_json('stops_nearby_response.json'),
        )

    yandex_uid = '123456'
    phone_id = 'active_phone_id'
    coupon_state_mock(
        phone_id,
        trips_count=1,
        coupon_id='test_coupon_id',
        yandex_uid=yandex_uid,
    )
    response = await taxi_maas.post(
        '/4.0/maas/v1/products',
        headers={
            'X-Yandex-Uid': yandex_uid,
            'X-YaTaxi-UserId': 'testsuite',
            'X-YaTaxi-PhoneId': phone_id,
        },
        json={'point_a': [37.5, 55.5], 'appearance_mode': 'ultima'},
    )
    assert response.status_code == 200
    assert len(response.json()['scenario_tops']) == 1
    result_scenario = response.json()['scenario_tops'][0]
    assert result_scenario['scenario'] == 'maas'

    assert len(result_scenario['shortcuts']) == 3
    assert 'tags' not in result_scenario['shortcuts'][0]  # original shortcut
    assert result_scenario['shortcuts'][1]['tags'] == ['kek']
    assert result_scenario['shortcuts'][2]['tags'] == ['lol']
