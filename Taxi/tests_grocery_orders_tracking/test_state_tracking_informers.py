import datetime

import pytest

from tests_grocery_orders_tracking import configs
from tests_grocery_orders_tracking import headers
from tests_grocery_orders_tracking import models

# we have to use actual now here,
# because we use PG's NOW() in cache and it's not mockable
NOW_FOR_CACHE = datetime.datetime.now()
HEADERS = {
    'X-YaTaxi-Pass-Flags': 'ya-plus',
    'X-YaTaxi-User': 'eats_user_id=test_eats_user_id',
    'X-YaTaxi-Session': 'test_domain:test_session',
    'X-YaTaxi-Bound-Sessions': 'old_test_domain:old_test_session',
}


def _setup_order(
        pgsql,
        grocery_cart,
        status,
        dispatch_status_info=models.DispatchStatusInfo(),
):
    order = models.Order(
        pgsql=pgsql,
        status=status,
        created=NOW_FOR_CACHE,
        dispatch_status_info=dispatch_status_info,
    )
    grocery_cart.add_cart(cart_id=order.cart_id)
    return order


def _setup_informer(
        pgsql,
        created,
        order_id,
        informer_type,
        compensation_type=None,
        situation_code=None,
        raw_compensation_info=None,
):
    informer = models.Informer(
        pgsql=pgsql,
        created=created,
        informer_type=informer_type,
        order_id=order_id,
        compensation_type=compensation_type,
        situation_code=situation_code,
        raw_compensation_info=raw_compensation_info,
    )

    return informer


async def test_basic(
        taxi_grocery_orders_tracking,
        pgsql,
        grocery_cart,
        grocery_depots,
        cargo,
        experiments3,
):
    configs.tracking_informers_config(experiments3)

    order_1 = _setup_order(pgsql, grocery_cart, 'assembled')
    order_2 = _setup_order(
        pgsql,
        grocery_cart,
        'delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='pickup_arrived',
        ),
    )

    informer_1 = _setup_informer(
        pgsql, NOW_FOR_CACHE, order_1.order_id, 'long_courier_search',
    )
    _setup_informer(pgsql, NOW_FOR_CACHE, order_2.order_id, 'custom')
    informer_2 = _setup_informer(
        pgsql, NOW_FOR_CACHE, order_2.order_id, 'long_delivery',
    )

    grocery_depots.add_depot(legacy_depot_id=order_2.depot_id)

    await taxi_grocery_orders_tracking.invalidate_caches(
        clean_update=False, cache_names=['informers-pg-cache'],
    )

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [
                {'id': order_1.order_id},
                {'id': order_2.order_id},
            ],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200

    orders = response.json()['grocery_orders']

    # Otherwise test may flap
    if orders[0]['id'] == order_1.order_id:
        assert (
            orders[0]['tracking_info']['informer_info']['informer_type']
            == informer_1.informer_type
        )
        assert (
            orders[1]['tracking_info']['informer_info']['informer_type']
            == informer_2.informer_type
        )
    else:
        assert (
            orders[1]['tracking_info']['informer_info']['informer_type']
            == informer_1.informer_type
        )
        assert (
            orders[0]['tracking_info']['informer_info']['informer_type']
            == informer_2.informer_type
        )


@pytest.mark.parametrize(
    'informer_type, compensation_info, expected_text,'
    'expected_modal_title, expected_modal_text, used_modal',
    [
        (
            'late_order_promocode',
            {'compensation_value': 69},
            'Late order informer with promocode text',
            '69% Promocode Title',
            '69% Promocode Text',
            configs.PROMOCODE_MODAL,
        ),
        (
            'late_order_promocode',
            {'compensation_value': 69},
            'Late order informer with promocode text',
            '69₽ Voucher Title',
            '69₽ Voucher Text',
            configs.FIXED_VOUCHER_MODAL,
        ),
        (
            'compensation',
            {'generated_promo': 'LOLKEK', 'compensation_value': 123},
            'Test situation happened. We gave you a '
            'compensation - click for details.',
            'Compensation for you',
            'Test situation happened. We are giving you a '
            '123 ₽ promocode LOLKEK for your next orders.',
            configs.PROMOCODE_MODAL,
        ),
    ],
)
async def test_informer_translation(
        taxi_grocery_orders_tracking,
        pgsql,
        grocery_cart,
        grocery_depots,
        cargo,
        informer_type,
        compensation_info,
        expected_text,
        expected_modal_title,
        expected_modal_text,
        used_modal,
        experiments3,
):
    configs.tracking_informers_config(experiments3, used_modal)

    order = _setup_order(
        pgsql,
        grocery_cart,
        'delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='pickup_arrived',
        ),
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    _setup_informer(
        pgsql,
        NOW_FOR_CACHE,
        order.order_id,
        informer_type,
        compensation_type='promocode',
        situation_code='test_code',
        raw_compensation_info=compensation_info,
    )

    await taxi_grocery_orders_tracking.invalidate_caches(
        clean_update=False, cache_names=['informers-pg-cache'],
    )

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200

    informer_info = response.json()['grocery_orders'][0]['tracking_info'][
        'informer_info'
    ]
    assert informer_info['text'] == expected_text
    assert informer_info['modal']['title'] == expected_modal_title
    assert informer_info['modal']['text'] == expected_modal_text


@configs.CRM_INFORMERS_ENABLED
@configs.FEEDBACK_ENABLED
@pytest.mark.parametrize('feedback_available', [True, False])
async def test_crm_informer(
        taxi_grocery_orders_tracking,
        pgsql,
        cargo,
        experiments3,
        grocery_cart,
        grocery_depots,
        feedback_available,
        grocery_crm,
):
    configs.tracking_informers_config(experiments3)

    order = _setup_order(
        pgsql,
        grocery_cart,
        'delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='pickup_arrived',
        ),
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    crm_informer_id = '7aa39782-c40c-49ea-9083-03edbb5e89a4'
    crm_informer = {
        'text': 'informer_text',
        'picture': 'informer_pic',
        'modal': {
            'title': 'modal_title',
            'text': 'modal_text',
            'picture': 'modal_pic',
            'buttons': [
                {'action': 'share', 'text': 'shr_btn_text'},
                {'action': 'copy', 'text': 'cpy_btn_text'},
            ],
        },
    }

    product_feedback = {
        'available_products_for_feedback': [
            {
                'product_id': 'some_id',
                'product_name': 'moms spaghetti',
                'product_img_url': 'url',
            },
        ],
    }

    models.Informer(
        pgsql=pgsql,
        order_id=order.order_id,
        informer_type='custom',
        raw_compensation_info={'crm_informer_id': crm_informer_id},
    )

    if feedback_available:
        models.Informer(
            pgsql=pgsql,
            order_id=order.order_id,
            informer_type='products_feedback',
            raw_compensation_info=product_feedback,
        )

    grocery_crm.set_user_informer(crm_informer_id, crm_informer)
    grocery_crm.check_informer_get_request({'informer_id': crm_informer_id})

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200
    assert grocery_crm.times_get_informer_called() == 1

    orders = response.json()['grocery_orders']
    informer_info = orders[0]['tracking_info'].get('informer_info')

    crm_informer['modal']['button'] = {
        'action': 'share',
        'text': 'shr_btn_text',
    }
    crm_informer['informer_type'] = 'custom'
    assert informer_info == crm_informer

    if feedback_available:
        assert orders[0]['available_products_for_feedback'] == product_feedback
    else:
        assert 'available_products_for_feedback' not in orders[0]


@configs.CRM_INFORMERS_ENABLED
@configs.FEEDBACK_ENABLED
async def test_feedback_from_cache(
        taxi_grocery_orders_tracking,
        pgsql,
        cargo,
        experiments3,
        grocery_cart,
        grocery_depots,
        grocery_crm,
):
    configs.tracking_informers_config(experiments3)

    order = _setup_order(
        pgsql,
        grocery_cart,
        'delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='pickup_arrived',
        ),
    )
    raw_feedback_info = {
        'available_products_for_feedback': [
            {
                'product_id': 'some_id',
                'product_name': 'moms spaghetti',
                'product_img_url': 'url',
            },
        ],
    }

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.Informer(
        pgsql=pgsql,
        order_id=order.order_id,
        informer_type='products_feedback',
        raw_compensation_info={
            'available_products_for_feedback': [
                {
                    'product_id': 'some_id',
                    'product_name': 'moms spaghetti',
                    'product_img_url': 'url',
                },
            ],
        },
    )
    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200

    orders = response.json()['grocery_orders']
    products = orders[0]['available_products_for_feedback']
    assert products == raw_feedback_info


@configs.FEEDBACK_ENABLED
async def test_no_feedback_with_system_informers(
        taxi_grocery_orders_tracking,
        pgsql,
        cargo,
        experiments3,
        grocery_cart,
        grocery_depots,
        grocery_crm,
):
    configs.tracking_informers_config(experiments3)

    order = _setup_order(
        pgsql,
        grocery_cart,
        'delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='pickup_arrived',
        ),
    )
    raw_feedback_info = {
        'available_products_for_feedback': [
            {
                'product_id': 'some_id',
                'product_name': 'moms spaghetti',
                'product_img_url': 'url',
            },
        ],
    }

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    models.Informer(
        pgsql=pgsql,
        order_id=order.order_id,
        informer_type='products_feedback',
        raw_compensation_info=raw_feedback_info,
    )
    _setup_informer(
        pgsql,
        NOW_FOR_CACHE,
        order.order_id,
        'compensation',
        raw_compensation_info={
            'generated_promo': 'LOLKEK',
            'compensation_value': 123,
        },
    )
    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200

    orders = response.json()['grocery_orders']
    assert 'available_products_for_feedback' not in orders[0]
