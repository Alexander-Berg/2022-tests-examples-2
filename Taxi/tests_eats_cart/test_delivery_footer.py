import copy
from typing import List

import pytest

from . import utils

PLACE_SLUG = 'place123'

PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'shippingType': 'delivery',
    'deliveryTime': '2021-04-04T08:00:00+00:00',
}

TRANSLATIONS = {
    'eats-reward-composer': {
        'description': {
            'ru': (
                'Очень тестовое описание. '
                'Доставка стоит %(delivery_cost)s %(sign)s.'
            ),
        },
        'text': {'ru': 'Доставка стоит %(delivery_cost)s %(sign)s.'},
    },
}


def get_enable_footer(enabled: bool):
    return pytest.mark.experiments3(
        name='eats_cart_enable_footer',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        is_config=True,
        default_value={'enabled': enabled},
    )


def get_composers_list(composers: List[str]):
    return pytest.mark.experiments3(
        name='eats_reward_composers',
        consumers=['eats_cart/reward_composer'],
        is_config=True,
        default_value={'composers': composers},
    )


def setup_rover_experiment(enabled: bool):
    return pytest.mark.experiments3(
        name='eda_yandex_rover_courier',
        consumers=['eats_cart/with_place_info'],
        is_config=False,
        default_value={'enabled': enabled},
    )


def get_composer(
        composer_name, text, description, prioriry=None, priority=None,
):
    return pytest.mark.experiments3(
        name=composer_name,
        consumers=['eats_cart/reward_composer'],
        is_config=True,
        default_value={
            'prioriry': prioriry,
            'priority': priority,
            'reward_banner': {
                'text': {
                    'color': [
                        {'theme': 'dark', 'value': '#ffffff'},
                        {'theme': 'light', 'value': '#000000'},
                    ],
                    'text': text,
                    'styles': {},
                },
                'description': {
                    'color': [
                        {'theme': 'dark', 'value': '#ffffff'},
                        {'theme': 'light', 'value': '#000000'},
                    ],
                    'text': description,
                    'styles': {},
                },
                'icon': 'icon',
            },
        },
    )


@get_enable_footer(False)
@get_composers_list(['threshold_delivery'])
@pytest.mark.experiments3(filename='exp3_threshold_composer.json')
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text()
async def test_disable_footer(taxi_eats_cart, local_services):
    eater_id = 'eater3'
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = ['2', '232323']
    local_services.asap = True

    params = copy.deepcopy(PARAMS)

    # we always expect shippingType delivery because it is in db
    local_services.set_params(copy.deepcopy(params))
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    resp_json = response.json()
    assert 'footer' not in resp_json


@get_enable_footer(True)
@pytest.mark.experiments3(
    name='eats_cart_user_promo',
    consumers=['eats_cart/user_only'],
    is_config=False,
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    name='eats_reward_composers',
    consumers=['eats_cart/reward_composer'],
    is_config=True,
    clauses=[
        {
            'title': 'eda_new_user',
            'value': {'composers': []},
            'predicate': {
                'type': 'bool',
                'init': {'arg_name': 'is_eda_new_user'},
            },
        },
    ],
    default_value={'composers': ['delivery_price']},
)
@get_composers_list(['delivery_price'])
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.config(EATS_REWARD_COMPOSER_MAX_THRESHOLD={'RUB': 0})
@pytest.mark.experiments3(filename='exp3_delivery_price_composer.json')
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text()
@pytest.mark.parametrize('eda_new_user', [True, False])
@pytest.mark.parametrize(
    'expected_description',
    [
        pytest.param(
            'Очень тестовое описание. Доставка стоит 20 ₽.',
            marks=setup_rover_experiment(False),
        ),
        pytest.param(
            'ROVER. Доставка стоит 20 ₽.', marks=setup_rover_experiment(True),
        ),
    ],
)
async def test_delivery_price_footer(
        taxi_eats_cart,
        local_services,
        expected_description,
        mockserver,
        eda_new_user,
):
    @mockserver.json_handler('/eda-delivery-price/v1/user-promo')
    def _user_promo(_):
        return {
            'is_eda_new_user': eda_new_user,
            'is_retail_new_user': False,
            'tags': [],
        }

    eater_id = 'eater3'
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = ['2', '232323']
    local_services.asap = True

    params = copy.deepcopy(PARAMS)

    # we always expect shippingType delivery because it is in db
    local_services.set_params(copy.deepcopy(params))
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    resp_json = response.json()
    if eda_new_user:
        assert 'footer' not in resp_json
    else:
        assert resp_json['footer'] == {
            'reward_banner': {
                'description': {
                    'color': [
                        {'theme': 'dark', 'value': '#ffffff'},
                        {'theme': 'light', 'value': '#000000'},
                    ],
                    'text': expected_description,
                },
                'icon': 'delivery',
                'name': {
                    'color': [
                        {'theme': 'dark', 'value': '#ffffff'},
                        {'theme': 'light', 'value': '#000000'},
                    ],
                    'text': 'Доставка стоит 20 ₽.',
                },
            },
        }


@get_enable_footer(True)
@get_composers_list(['threshold_delivery'])
@pytest.mark.config(EATS_REWARD_COMPOSER_MAX_THRESHOLD={'RUB': 0})
@pytest.mark.experiments3(filename='exp3_threshold_composer.json')
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text()
async def test_max_threshold_footer(taxi_eats_cart, local_services):
    eater_id = 'eater3'
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = ['2', '232323']
    local_services.asap = True

    params = copy.deepcopy(PARAMS)

    # we always expect shippingType delivery because it is in db
    local_services.set_params(copy.deepcopy(params))
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    resp_json = response.json()
    assert 'footer' not in resp_json


@get_enable_footer(True)
@get_composers_list(['threshold_delivery'])
@pytest.mark.experiments3(filename='exp3_threshold_composer.json')
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text()
async def test_cart_threshold_footer(taxi_eats_cart, local_services):

    eater_id = 'eater3'
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = ['2', '232323']
    local_services.asap = True

    params = copy.deepcopy(PARAMS)

    # we always expect shippingType delivery because it is in db
    local_services.set_params(copy.deepcopy(params))
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    resp_json = response.json()
    assert resp_json['footer'] == {
        'reward_banner': {
            'description': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': (
                    'Очень тестовое описание. '
                    'Доставка 20 ₽. Еще 10 ₽ и будет 10 ₽.'
                ),
            },
            'icon': 'delivery',
            'name': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': 'Доставка 20 ₽. Еще 10 ₽ и будет 10 ₽.',
            },
        },
    }


@get_enable_footer(True)
@get_composers_list(['free_delivery'])
@pytest.mark.experiments3(filename='exp3_free_delivery_composer.json')
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text()
async def test_cart_free_delivery_footer(taxi_eats_cart, local_services):
    eater_id = 'eater3'
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = ['2', '232323']
    local_services.asap = True

    params = copy.deepcopy(PARAMS)

    # we always expect shippingType delivery because it is in db
    local_services.set_params(copy.deepcopy(params))
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    resp_json = response.json()

    assert resp_json['footer'] == {
        'reward_banner': {
            'description': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': (
                    'Очень тестовое описание. '
                    'Доставка 20 ₽. До бесплатной еще 20 ₽.'
                ),
            },
            'icon': 'delivery',
            'name': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': 'Доставка 20 ₽ 0. До бесплатной еще 20 ₽.',
            },
        },
    }


@get_enable_footer(True)
@get_composers_list(['surge'])
@pytest.mark.experiments3(filename='exp3_surge_composer.json')
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.config(EATS_REWARD_COMPOSER_CURRENCY_ROUNDING={'RUB': 2})
@utils.additional_payment_text()
async def test_cart_surge_footer(taxi_eats_cart, local_services, load_json):

    eater_id = 'eater2'

    surge_info = {
        'delivery_fee': '18.12',
        'additional_fee': '10.11',
        'level': 1,
    }

    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = ['2', '232323']
    local_services.asap = True

    catalog_response = load_json('eats_catalog_internal_place.json')
    catalog_response['place']['surge_info'] = surge_info

    local_services.catalog_place_response = catalog_response
    local_services.set_params(copy.deepcopy(PARAMS))

    params = copy.deepcopy(PARAMS)

    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    resp_json = response.json()
    assert resp_json['footer'] == {
        'reward_banner': {
            'description': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': (
                    'Очень тестовое описание. '
                    'Доставка за 18,12 ₽ потому что Повышенный'
                    ' спрос Заказов сейчас очень много — чтобы еда прие'
                    'хала в срок, стоимость доставки временно увеличена '
                    'Описание повышенного спроса'
                ),
            },
            'icon': 'surge',
            'name': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': (
                    'Доставка за 18,12 ₽ потому что Повышенный'
                    ' спрос Заказов сейчас очень много — чтобы еда прие'
                    'хала в срок, стоимость доставки временно увеличена '
                    'Описание повышенного спроса'
                ),
            },
        },
    }


@get_enable_footer(True)
@get_composers_list(['min_cart'])
@pytest.mark.config(EATS_REWARD_COMPOSER_MAX_THRESHOLD={'RUB': 0})
@pytest.mark.config(EATS_REWARD_COMPOSER_CURRENCY_ROUNDING={'RUB': 1})
@pytest.mark.experiments3(filename='exp3_min_cart_composer.json')
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text()
async def test_cart_min_cart_footer(taxi_eats_cart, local_services):
    eater_id = 'eater3'

    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = ['2', '232323']
    local_services.asap = True

    delivery_price_response = {
        'surge_result': {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 100,
                'deliveryFee': 0,
                'loadLevel': 100,
            },
        },
        'service_fee': '15',
    }
    delivery_price_response['cart_delivery_price'] = {
        'min_cart': '400.23',
        'delivery_fee': '0',
        'next_delivery_threshold': {'amount_need': '200', 'next_cost': '400'},
    }

    local_services.set_params(copy.deepcopy(PARAMS))
    local_services.delivery_price_status = 200
    local_services.delivery_price_response = delivery_price_response

    params = copy.deepcopy(PARAMS)

    # we always expect shippingType delivery because it is in db
    local_services.set_params(copy.deepcopy(params))
    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    resp_json = response.json()

    assert resp_json['footer'] == {
        'reward_banner': {
            'description': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': 'Очень тестовое описание. ' 'До заказа еще 260,2 ₽.',
            },
            'icon': 'delivery',
            'name': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': 'До заказа еще 260,2 ₽',
            },
        },
    }


@get_enable_footer(True)
@get_composers_list(['retail_delivery_and_weight'])
@pytest.mark.config(EATS_REWARD_COMPOSER_MAX_THRESHOLD={'RUB': 0})
@pytest.mark.experiments3(
    filename='exp3_retail_delivery_and_weight_composer.json',
)
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@utils.additional_payment_text()
@pytest.mark.parametrize(
    'delivery_fee, weight_fee, sum_to_free_delivery,'
    'amount_need, next_cost, description_txt, name_txt',
    [
        pytest.param(
            '100',
            None,
            None,
            '150',
            '50',
            None,
            'Доставка 100 ₽ · Еще 150 ₽, и будет 50 ₽',
            id='without_weight_fee',
        ),
        pytest.param(
            '100',
            0,
            None,
            '150',
            '50',
            None,
            'Доставка 100 ₽ · Еще 150 ₽, и будет 50 ₽',
            id='weight_fee=0',
        ),
        pytest.param(
            '100',
            10,
            '30',
            '150',
            '50',
            'Доплата 10 ₽ за тяжелый заказ',
            'Доставка 100 ₽ · Еще 150 ₽, и будет 50 ₽',
            id='with_weight_fee',
        ),
        pytest.param(
            '100',
            None,
            '30',
            '133',
            '0',
            None,
            'Доставка 100 ₽ · До бесплатной 30 ₽',
            id='without_weight_fee, with_sum_to_free_delivery',
        ),
        pytest.param(
            '100',
            12,
            '30',
            '133',
            '50',
            'Доплата 12 ₽ за тяжелый заказ',
            'Доставка 100 ₽ · Еще 133 ₽, и будет 50 ₽',
            id='with_weight_fee, with_sum_to_free_delivery',
        ),
        pytest.param(
            '0',
            12,
            '30',
            '133',
            '188',
            'Доплата 12 ₽ за тяжелый заказ',
            'Доставка 0 ₽',
            id='with_weight_fee, delivery_cost_zero',
        ),
        pytest.param(
            '0',
            None,
            '30',
            '133',
            '188',
            None,
            'Доставка 0 ₽',
            id='with_weight_fee, delivery_cost_zero',
        ),
    ],
)
async def test_cart_retail_delivery_and_weight_footer(
        taxi_eats_cart,
        local_services,
        delivery_fee,
        weight_fee,
        sum_to_free_delivery,
        amount_need,
        next_cost,
        description_txt,
        name_txt,
):
    """
        Тест расширенного футера (при непустой корзине)
    """
    eater_id = 'eater3'

    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = ['2', '232323']
    local_services.asap = True

    local_services.delivery_price_response = {
        'cart_delivery_price': {
            'min_cart': '0',
            'delivery_fee': delivery_fee,
            'next_delivery_threshold': {
                'amount_need': amount_need,
                'next_cost': next_cost,
            },
            'sum_to_free_delivery': sum_to_free_delivery,
        },
        'surge_result': {'placeId': 1},
        'service_fee': '15',
    }

    if weight_fee is not None:
        local_services.delivery_price_response['cart_delivery_price'][
            'weight_fee'
        ] = str(weight_fee)

    local_services.delivery_price_status = 200
    local_services.set_params(copy.deepcopy(PARAMS))

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    reward_banner = response.json()['footer']['reward_banner']

    color = [
        {'theme': 'dark', 'value': '#ffffff'},
        {'theme': 'light', 'value': '#000000'},
    ]

    assert reward_banner['name']['text'] == name_txt
    assert reward_banner['name']['color'] == color
    assert reward_banner['icon'] == 'delivery'
    if weight_fee is not None and weight_fee != 0:
        assert reward_banner['description']['text'] == description_txt
        assert reward_banner['description']['color'] == color


@get_enable_footer(True)
@get_composers_list(['promo'])
@get_composer(
    'eats_reward_promo_composer',
    'Промо старая цена {delivery_cost_without_promo},'
    ' новая новая цена {delivery_cost}',
    'test',
)
@utils.delivery_discount_enabled()
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.additional_payment_text()
@utils.discounts_applicator_enabled(True)
async def test_promo_footer(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_order_stats,
        mockserver,
):

    eater_id = 'eater2'
    eats_order_stats()
    params = copy.deepcopy(PARAMS)
    local_services.available_discounts = True
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(232323), '2']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    catalog_response = load_json('eats_catalog_internal_place.json')

    local_services.catalog_place_response = catalog_response

    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    local_services.catalog_place_id = 123
    discounts_resp = load_json('eats_discounts_free_delivery.json')

    del discounts_resp['match_results'][-1]

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_match_discounts(request):
        assert 'check' in request.json['common_conditions']['conditions']
        assert 'surge_range' in request.json['common_conditions']['conditions']
        assert (
            'delivery_method'
            in request.json['common_conditions']['conditions']
        )
        assert (
            'shipping_types' in request.json['common_conditions']['conditions']
        )
        return discounts_resp

    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    resp_json = response.json()
    assert resp_json['footer'] == {
        'reward_banner': {
            'description': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': 'test',
            },
            'icon': 'icon',
            'name': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': 'Промо старая цена 20, новая новая цена 0',
            },
        },
    }


@get_enable_footer(True)
@get_composers_list(['next_promo', 'free_delivery'])
@get_composer(
    'eats_reward_next_promo_composer',
    'Промо старая цена {delivery_cost}.',
    'Еще {amount_need} до {promo_value}',
    priority=100,
    prioriry=20,
)
@get_composer(
    'eats_reward_free_delivery_composer',
    'Не будет показываться',
    'тест',
    prioriry=100,
    priority=20,
)
@utils.delivery_discount_enabled()
@pytest.mark.now('2021-04-04T08:00:00.4505+00:00')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.config(EATS_REWARD_COMPOSER_CURRENCY_ROUNDING={'RUB': 2})
@utils.additional_payment_text()
@utils.discounts_applicator_enabled(True)
async def test_next_promo_footer(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_order_stats,
        mockserver,
):

    eater_id = 'eater2'
    eats_order_stats()
    params = copy.deepcopy(PARAMS)
    local_services.available_discounts = True
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(232323), '2']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    catalog_response = load_json('eats_catalog_internal_place.json')

    local_services.catalog_place_response = catalog_response

    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    local_services.catalog_place_id = 123
    discounts_resp = load_json('eats_discounts_free_delivery.json')

    del discounts_resp['match_results'][-1]

    discounts_resp['match_results'][0]['discounts'][0]['money_value'][
        'menu_value'
    ] = (
        {
            'value': [
                {
                    'discount': {'value': '10', 'value_type': 'fraction'},
                    'from_cost': '700',
                },
            ],
            'value_type': 'table',
        }
    )

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_match_discounts(request):
        assert 'check' in request.json['common_conditions']['conditions']
        assert 'surge_range' in request.json['common_conditions']['conditions']
        assert (
            'delivery_method'
            in request.json['common_conditions']['conditions']
        )
        assert (
            'shipping_types' in request.json['common_conditions']['conditions']
        )
        return discounts_resp

    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1

    resp_json = response.json()
    assert resp_json['footer'] == {
        'reward_banner': {
            'description': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': 'Еще 552,04 до 10',
            },
            'icon': 'icon',
            'name': {
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#000000'},
                ],
                'text': 'Промо старая цена 20.',
            },
        },
    }


@pytest.mark.pgsql('eats_cart', files=['delivery_discount.sql'])
async def test_extra_fee_payload_parsing(
        taxi_eats_cart, local_services, load_json,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(232323), '2']
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    catalog_response = load_json('eats_catalog_internal_place.json')
    local_services.catalog_place_response = catalog_response

    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    local_services.catalog_place_id = 123

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers('eater_eda_discount'),
    )

    assert response.status_code == 200
