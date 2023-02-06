import pytest

from . import common
from . import common_service_info
from . import const
from . import experiments
from . import tests_headers

NOW = '2020-09-09T10:00:00+00:00'


@pytest.mark.now(NOW)
@pytest.mark.parametrize('reward_discounts_enabled', [True, False])
@pytest.mark.parametrize(
    'delivery_conditions',
    [
        [
            {'order_cost': '0', 'delivery_cost': '10'},
            {'order_cost': '100', 'delivery_cost': '5'},
            {'order_cost': '200', 'delivery_cost': '0'},
        ],
        [{'order_cost': '50', 'delivery_cost': '0'}],
    ],
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'}},
    overlord_catalog={
        'discount_short_text': {'ru': '-%(value)s'},
        'discount_short_text_percent': {'ru': '%(value)s%'},
        'to_min_order': {'ru': 'Ещё %(value)s до минимального заказа'},
        'to_free_delivery_without_delivery': {
            'ru': 'До бесплатной доставки ещё %(value)s',
        },
        'to_next_delivery_without_delivery': {
            'ru': 'Ещё %(value)s до доставки за %(next_cost)s',
        },
        'to_next_relative_discount': {
            'ru': 'Ещё %(value)s до скидки —%(discount)s%',
        },
    },
)
@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud',
    [
        pytest.param(
            False,
            True,
            marks=experiments.ANTIFRAUD_CHECK_DISABLED,
            id='no antifraud, not fraud, no check',
        ),
        pytest.param(
            True,
            False,
            marks=experiments.ANTIFRAUD_CHECK_ENABLED,
            id='antifraud, not fraud, check',
        ),
        pytest.param(
            True,
            True,
            marks=experiments.ANTIFRAUD_CHECK_ENABLED,
            id='antifraud, fraud, check',
        ),
    ],
)
async def test_service_info_reward_block(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        antifraud,
        grocery_marketing,
        grocery_p13n,
        grocery_surge,
        grocery_depots,
        tristero_parcels,
        delivery_conditions,
        reward_discounts_enabled,
        antifraud_enabled,
        is_fraud,
):
    """ get service info with reward_block_v2 """

    experiments3.add_config(
        match={
            'predicate': {'type': 'true'},
            'enabled': reward_discounts_enabled,
        },
        name='grocery_show_reward_discounts',
        consumers=['grocery-api/modes'],
        clauses=[
            {
                'predicate': {'type': 'true'},
                'value': {'enabled': reward_discounts_enabled},
            },
        ],
    )

    discount_steps = [
        ('75', '10.2', 'discount_percent'),
        ('150', '20', 'discount_value'),
        ('200', '5.3', 'gain_percent'),
        ('300', '50', 'gain_value'),
    ]
    grocery_p13n.add_cart_modifier_with_rules(steps=discount_steps)

    location = common.DEFAULT_LOCATION
    yandex_uid = tests_headers.HEADER_YANDEX_UID
    orders_count = 2 if not antifraud_enabled else None

    grocery_marketing.add_user_tag(
        'total_orders_count', orders_count, user_id=yandex_uid,
    )
    common_service_info.prepare_depots(
        overlord_catalog, location, grocery_depots,
    )

    common_service_info.set_surge_conditions(
        experiments3, delivery_conditions=delivery_conditions,
    )

    grocery_surge.add_record(
        legacy_depot_id=const.LEGACY_DEPOT_ID,
        timestamp='2020-09-09T10:00:00+00:00',
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    tristero_order = tristero_parcels.add_order(
        order_id='62a88408-b448-429e-8dc0-48f6995fd78e',
        uid=yandex_uid,
        status='received',
        delivery_date='2020-11-02T13:00:42.109234+00:00',
    )
    tristero_order.add_parcel(parcel_id='1', status='in_depot')

    await taxi_grocery_api.invalidate_caches()

    json = {
        'position': {'location': location},
        'additional_data': common.DEFAULT_ADDITIONAL_DATA,
    }
    headers = {}
    headers['X-Yandex-UID'] = yandex_uid
    headers['X-Request-Language'] = 'ru'
    headers['User-Agent'] = common.DEFAULT_USER_AGENT
    headers['X-YaTaxi-Session'] = 'taxi:1'
    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=common.default_on_modifiers_request(
            orders_count, has_parcels=True,
        ),
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200

    assert tristero_parcels.retrieve_orders_v2_times_called == 1
    if reward_discounts_enabled:
        assert grocery_p13n.discount_modifiers_times_called == 1
        assert antifraud.times_discount_antifraud_called() == int(
            antifraud_enabled,
        )

    response_json = response.json()

    if antifraud_enabled and is_fraud:
        assert response_json['notifications'] == [
            {'name': 'catalog_newbie_discount_missing'},
        ]

    assert response_json['is_surge'] is False

    if reward_discounts_enabled:
        if len(delivery_conditions) > 1:
            items = [
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 0 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 10 $SIGN$$CURRENCY$',
                    'reward_short_value': '10 $SIGN$$CURRENCY$',
                    'progress': 100,
                },
                {
                    'type': 'cart_money_discount',
                    'cart_cost_threshold': 'От 75 $SIGN$$CURRENCY$',
                    'reward_value': 'Скидка 10%',
                    'reward_short_value': '10%',
                    'progress': 0,
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 100 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 5 $SIGN$$CURRENCY$',
                    'reward_short_value': '5 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
                {
                    'type': 'cart_money_discount',
                    'cart_cost_threshold': 'От 150 $SIGN$$CURRENCY$',
                    'reward_value': 'Скидка 20 $SIGN$$CURRENCY$',
                    'reward_short_value': '-20 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 200 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 0 $SIGN$$CURRENCY$',
                    'reward_short_value': '0 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
                {
                    'type': 'cart_cashback',
                    'cart_cost_threshold': 'От 200 $SIGN$$CURRENCY$',
                    'reward_value': '5% на Плюс',
                    'reward_short_value': '5%',
                    'progress': 0,
                },
                {
                    'type': 'cart_cashback',
                    'cart_cost_threshold': 'От 300 $SIGN$$CURRENCY$',
                    'reward_value': '50 баллов на Плюс',
                    'reward_short_value': '50',
                    'progress': 0,
                },
            ]
            reward_block = {
                'items': items,
                'till_next_threshold': (
                    'Ещё 75 $SIGN$$CURRENCY$ до скидки —10.2%'
                ),
                'till_next_threshold_numeric': '75',
            }
        else:
            items = [
                {
                    'type': 'min_cart',
                    'cart_cost_threshold': '50 $SIGN$$CURRENCY$',
                    'reward_value': 'Минимальная корзина 50 $SIGN$$CURRENCY$',
                    'reward_short_value': '50 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 50 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 0 $SIGN$$CURRENCY$',
                    'reward_short_value': '0 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
                {
                    'type': 'cart_money_discount',
                    'cart_cost_threshold': 'От 75 $SIGN$$CURRENCY$',
                    'reward_value': 'Скидка 10%',
                    'reward_short_value': '10%',
                    'progress': 0,
                },
                {
                    'type': 'cart_money_discount',
                    'cart_cost_threshold': 'От 150 $SIGN$$CURRENCY$',
                    'reward_value': 'Скидка 20 $SIGN$$CURRENCY$',
                    'reward_short_value': '-20 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
                {
                    'type': 'cart_cashback',
                    'cart_cost_threshold': 'От 200 $SIGN$$CURRENCY$',
                    'reward_value': '5% на Плюс',
                    'reward_short_value': '5%',
                    'progress': 0,
                },
                {
                    'type': 'cart_cashback',
                    'cart_cost_threshold': 'От 300 $SIGN$$CURRENCY$',
                    'reward_value': '50 баллов на Плюс',
                    'reward_short_value': '50',
                    'progress': 0,
                },
            ]
            reward_block = {
                'items': items,
                'till_next_threshold': (
                    'Ещё 50 $SIGN$$CURRENCY$ до минимального заказа'
                ),
                'till_next_threshold_numeric': '50',
            }
    else:
        if len(delivery_conditions) > 1:
            items = [
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 0 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 10 $SIGN$$CURRENCY$',
                    'reward_short_value': '10 $SIGN$$CURRENCY$',
                    'progress': 100,
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 100 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 5 $SIGN$$CURRENCY$',
                    'reward_short_value': '5 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 200 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 0 $SIGN$$CURRENCY$',
                    'reward_short_value': '0 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
            ]
            reward_block = {
                'items': items,
                'till_next_threshold': 'Ещё 100 $SIGN$$CURRENCY$ до доставки за 5 $SIGN$$CURRENCY$',
                'till_next_threshold_numeric': '100',
            }
        else:
            items = [
                {
                    'type': 'min_cart',
                    'cart_cost_threshold': '50 $SIGN$$CURRENCY$',
                    'reward_value': 'Минимальная корзина 50 $SIGN$$CURRENCY$',
                    'reward_short_value': '50 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 50 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 0 $SIGN$$CURRENCY$',
                    'reward_short_value': '0 $SIGN$$CURRENCY$',
                    'progress': 0,
                },
            ]
            reward_block = {
                'items': items,
                'till_next_threshold': (
                    'Ещё 50 $SIGN$$CURRENCY$ до минимального заказа'
                ),
                'till_next_threshold_numeric': '50',
            }
    assert response_json['reward_block'] == reward_block


get_rounding_rules = common_service_info.get_rounding_rules


# Округление цены доставки и отображение происходит с учетом
# значений конфигов CURRENCY_FORMATTING_RULES и CURRENCY_ROUNDING_RULES
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'delivery_cost_shown',
    [
        pytest.param('10.43', marks=get_rounding_rules(2, 0.01)),
        pytest.param('10.4', marks=get_rounding_rules(1, 0.1)),
        pytest.param('10', marks=get_rounding_rules(0, 1)),
    ],
)
@pytest.mark.translations(
    overlord_catalog={
        'delivery_text_cost_range': {'en': 'Delivery %(value)s'},
        'delivery_cost_range': {'en': '%(value)s'},
        'to_free_delivery_without_delivery': {
            'en': 'Till free delivery: %(value)s',
        },
    },
    tariff={'currency_with_sign.default': {'en': '$SIGN$$VALUE$$CURRENCY$'}},
)
async def test_service_paid_delivery_round(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        delivery_cost_shown,
):
    location = [0, 0]
    common_service_info.prepare_depots(
        overlord_catalog, location, grocery_depots,
    )
    common_service_info.set_surge_conditions(
        experiments3,
        delivery_conditions=[
            {'order_cost': '0', 'delivery_cost': '10.43'},
            {'order_cost': '50', 'delivery_cost': '0'},
        ],
    )

    grocery_surge.add_record(
        legacy_depot_id=const.LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    await taxi_grocery_api.invalidate_caches()

    headers = {'X-Request-Language': 'en'}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/service-info',
        json={'position': {'location': location}},
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert (
        response_json['l10n']['delivery_cost']
        == f'Delivery: $SIGN${delivery_cost_shown}$CURRENCY$'
    )
    assert (
        response_json['l10n']['delivery_cost_range']
        == f'$SIGN$0-{delivery_cost_shown}$CURRENCY$'
    )
    items = [
        {
            'type': 'delivery',
            'cart_cost_threshold': 'From $SIGN$0$CURRENCY$',
            'reward_value': f'Delivery: $SIGN${delivery_cost_shown}$CURRENCY$',
            'reward_short_value': f'$SIGN${delivery_cost_shown}$CURRENCY$',
            'progress': 100,
        },
        {
            'type': 'delivery',
            'cart_cost_threshold': 'From $SIGN$50$CURRENCY$',
            'reward_value': 'Free delivery',
            'reward_short_value': '$SIGN$0$CURRENCY$',
            'progress': 0,
        },
    ]
    reward_block = {
        'items': items,
        'till_next_threshold': 'Till free delivery: $SIGN$50$CURRENCY$',
        'till_next_threshold_numeric': '50',
    }
    assert response_json['reward_block'] == reward_block
