import json

import pytest

from protocol.ordercommit import order_commit_common

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'
ORDER_ID = 'order_id'
CORP_PAYMENTMETHODS_PATH = '/corp_integration_api/corp_paymentmethods'
NEW_SURGE_VALUE = 5.0
NORMAL_OFFER_SURGE_VALUE = 2.5


@pytest.fixture
def ordercommit_services(mockserver):
    class context:
        surge_value = 1

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': context.surge_value,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': context.surge_value,
                    'value_smooth': context.surge_value,
                    'sp_surcharge': 0,
                    'sp_alpha': 1.0,
                    'sp_beta': 0.0,
                },
            ],
        }

    return context


def _mock_corp_paymentmethods(mockserver):
    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_corp_paymentmethods(request):
        return {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-decoupled-client',
                    'label': '-',
                    'description': '-',
                    'can_order': True,
                    'cost_center': '',
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'corp_user_id',
                    'client_comment': 'corp_comment',
                    'currency': 'RUB',
                },
            ],
        }


def check(db, decoupling_info):
    proc = db.order_proc.find_one({'_id': ORDER_ID})
    assert proc['order']['decoupling'] == decoupling_info


def check_current_prices(proc, decoupling_info):
    fixed_price = decoupling_info.get('fixed_price')
    calc_price = (
        proc.get('order')
        .get('calc')
        .get('allowed_tariffs')
        .get('__park__')
        .get('econom')
    )
    exp_price = fixed_price if fixed_price else calc_price
    exp_kind = 'fixed' if fixed_price else 'prediction'
    order_commit_common.check_current_prices(proc, exp_kind, exp_price)


def check_price_modifiers(db):
    order_proc = db.order_proc.find_one({'_id': ORDER_ID})
    assert 'price_modifiers' in order_proc
    price_modifiers = order_proc['price_modifiers']
    assert len(price_modifiers) == 1
    assert price_modifiers['items'][0]['reason'] == 'requirements'
    assert price_modifiers['items'][0]['pay_subventions'] is False
    assert price_modifiers['items'][0]['tariff_categories'] == ['econom']
    assert price_modifiers['items'][0]['type'] == 'multiplier'
    assert price_modifiers['items'][0]['value'] == '1.300000'


@pytest.mark.parametrize(
    'offer_id,decoupling_info,expected_code',
    [
        (
            'offer-decoupling_fixed_price',
            {
                'driver_price_info': {
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'fixed_price': 216.355,
                    'sp': 1.0,
                    'sp_alpha': 1.0,
                    'sp_beta': 0.0,
                    'sp_surcharge': 0.0,
                    'paid_supply_price': 100.0,
                    'paid_cancel_in_driving': {
                        'price': 100.0,
                        'free_cancel_timeout': 250,
                        'for_paid_supply': True,
                    },
                    'tariff_id': '585a6f47201dd1b2017a0eab',
                },
                'success': True,
                'user_price_info': {
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'fixed_price': 432.71,
                    'sp': 1.0,
                    'sp_alpha': 1.0,
                    'sp_beta': 0.0,
                    'sp_surcharge': 0.0,
                    'paid_supply_price': 0.0,
                    'paid_cancel_in_driving': {
                        'price': 0.0,
                        'free_cancel_timeout': 250,
                        'for_paid_supply': True,
                    },
                    'tariff_id': (
                        '585a6f47201dd1b2017a0eab-'
                        '507000939f17427e951df9791573ac7e-'
                        '7fc5b2d1115d4341b7be206875c40e11'
                    ),
                },
            },
            200,
        ),
    ],
)
@pytest.mark.filldb(order_offers='ok')
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_ordercommit_decoupling_normal_offer_ok_fixed_price(
        mockserver,
        taxi_protocol,
        db,
        offer_id,
        decoupling_info,
        expected_code,
):
    _mock_corp_paymentmethods(mockserver)

    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.offer': offer_id}},
    )
    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )
    assert response.status_code == expected_code
    check(db, decoupling_info)


@pytest.mark.parametrize(
    'decoupling_info,' 'surge, fallback',
    [
        (
            {
                'driver_price_info': {
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': NEW_SURGE_VALUE,
                    'tariff_id': '585a6f47201dd1b2017a0eab',
                },
                'success': True,
                'user_price_info': {
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'sp': 1.0,
                    'tariff_id': (
                        '585a6f47201dd1b2017a0eab-'
                        '507000939f17427e951df9791573ac7e-'
                        '7fc5b2d1115d4341b7be206875c40e11'
                    ),
                },
            },
            NEW_SURGE_VALUE,
            False,
        ),
        (
            {
                'error': {
                    'stage': 'ordercommit',
                    'reason': 'get_corp_tarif_fail',
                },
                'success': False,
            },
            1.0,
            True,
        ),
    ],
    ids=['decoupled', 'decoupling_failed'],
)
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'protocol', 'dst': 'corp-integration-api'}],
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
    ROUTER_42GROUP_ENABLED=False,
    ROUTER_MAPS_ENABLED=True,
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
def test_decoupling_no_offer(
        taxi_protocol,
        db,
        load_json,
        load_binary,
        mockserver,
        now,
        decoupling_info,
        surge,
        tvm2_client,
        ordercommit_services,
        fallback,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_corp_decoupling(True)
    if not fallback:
        pricing_data_preparer.set_decoupling(True)
        pricing_data_preparer.set_user_category_prices_id(
            'd/585a6f47201dd1b2017a0eab-'
            '507000939f17427e951df9791573ac7e-'
            '7fc5b2d1115d4341b7be206875c40e11/'
            '5f40b7f324414f51a1f9549c65211ea5',
        )
        pricing_data_preparer.set_driver_category_prices_id(
            'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        )
        pricing_data_preparer.set_driver_surge(NEW_SURGE_VALUE)
        pricing_data_preparer.set_user_surge(1.0)

    ordercommit_services.surge_value = surge

    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'24': {'ticket': ticket}}))

    _mock_corp_paymentmethods(mockserver)

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == 200
    check(db, decoupling_info)


@pytest.mark.parametrize(
    'is_fixed, price_changed, expected_code, decoupling_info',
    [
        # fixed and price(corp tariff and surge) changed - throw 406
        (True, True, 406, {}),
        # fixed and price(corp tariff and surge) is the same
        # - remain decoupling from offer
        (
            True,
            False,
            200,
            {
                'driver_price_info': {
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'fixed_price': 309.901,
                    'sp': 1.0,
                    'sp_alpha': 1.0,
                    'sp_beta': 0.0,
                    'sp_surcharge': 0.0,
                    'tariff_id': '585a6f47201dd1b2017a0eab',
                },
                'success': True,
                'user_price_info': {
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'fixed_price': 619.803,
                    'sp': 1.0,
                    'sp_alpha': 1.0,
                    'sp_beta': 0.0,
                    'sp_surcharge': 0.0,
                    'tariff_id': (
                        '585a6f47201dd1b2017a0eab-'
                        '507000939f17427e951df9791573ac7e-'
                        '7fc5b2d1115d4341b7be206875c40e11'
                    ),
                },
            },
        ),
        # not fixed and price(corp tariff and surge) is changed
        # - select new decoupling
        (
            False,
            True,
            200,
            {
                'driver_price_info': {
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': NEW_SURGE_VALUE,
                    'tariff_id': '585a6f47201dd1b2017a0eab',
                },
                'success': True,
                'user_price_info': {
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'sp': 1.0,
                    'tariff_id': (
                        '585a6f47201dd1b2017a0eab-'
                        '507000939f17427e951df9791573ac7e-'
                        '7fc5b2d1115d4341b7be206875c40e11'
                    ),
                },
            },
        ),
        # not fixed and price(corp tariff and surge) is the same
        # - remain decoupling from offer
        (
            False,
            False,
            200,
            {
                'driver_price_info': {
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': 1.0,
                    'sp_alpha': 1.0,
                    'sp_beta': 0.0,
                    'sp_surcharge': 0.0,
                    'tariff_id': '585a6f47201dd1b2017a0eab',
                },
                'success': True,
                'user_price_info': {
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'sp': 1.0,
                    'sp_alpha': 1.0,
                    'sp_beta': 0.0,
                    'sp_surcharge': 0.0,
                    'tariff_id': (
                        '585a6f47201dd1b2017a0eab-'
                        '507000939f17427e951df9791573ac7e-'
                        '7fc5b2d1115d4341b7be206875c40e11'
                    ),
                },
            },
        ),
    ],
    ids=[
        'fixed_changed_price',
        'fixed_same_price',
        'no_fixed_changed_price',
        'no_fixed_same_price',
    ],
)
@pytest.mark.filldb(order_offers='obsolete')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.config(
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
    ROUTER_42GROUP_ENABLED=False,
    ROUTER_MAPS_ENABLED=True,
)
def test_decoupling_obsolete_offer_was_ok_became_ok(
        taxi_protocol,
        db,
        order_experiments,
        load_json,
        mockserver,
        load_binary,
        ordercommit_services,
        is_fixed,
        price_changed,
        expected_code,
        decoupling_info,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=is_fixed)
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_user_category_prices_id(
        'd/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        '5f40b7f324414f51a1f9549c65211ea5',
    )
    pricing_data_preparer.set_driver_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    if price_changed:
        pricing_data_preparer.set_driver_surge(NEW_SURGE_VALUE)
        pricing_data_preparer.set_user_surge(1.0)
    else:
        pricing_data_preparer.set_cost(619.803, 309.901)
        pricing_data_preparer.set_driver_surge(1.0, 1.0)
        pricing_data_preparer.set_user_surge(1.0, 1.0)

    if is_fixed:
        order_experiments.set_value(['fixed_price'])

    if price_changed:
        ordercommit_services.surge_value = NEW_SURGE_VALUE

    _mock_corp_paymentmethods(mockserver)

    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.offer': 'offer-decoupling-obsolete'}},
    )

    db.order_offers.update(
        {'_id': 'offer-decoupling-obsolete'},
        {'$set': {'is_fixed_price': is_fixed}},
    )
    db.order_offers.update(
        {'_id': 'offer-decoupling-obsolete'},
        {'$set': {'prices[0].pricing_data.is_fixed_price': is_fixed}},
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == expected_code
    if expected_code != 200:
        return
    check(db, decoupling_info)


@pytest.mark.parametrize(
    'is_fixed', [True, False], ids=['fixed_price', 'no_fixed_price'],
)
@pytest.mark.filldb(order_offers='obsolete')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.now('2018-04-24T08:15:00+0000')
def test_decoupling_obsolete_offer_was_ok_became_not_ok(
        taxi_protocol,
        db,
        order_experiments,
        load_json,
        mockserver,
        ordercommit_services,
        is_fixed,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_corp_decoupling(True)

    if is_fixed:
        order_experiments.set_value(['fixed_price'])

    db.order_offers.update(
        {'_id': 'offer-decoupling-obsolete'},
        {'$set': {'is_fixed_price': is_fixed}},
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == 406


@pytest.mark.parametrize(
    'is_fixed, expected_code, decoupling_info',
    [
        (True, 406, {}),
        (
            False,
            200,
            {
                'driver_price_info': {
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': NEW_SURGE_VALUE,
                    'tariff_id': '585a6f47201dd1b2017a0eab',
                },
                'success': True,
                'user_price_info': {
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'sp': 1.0,
                    'tariff_id': (
                        '585a6f47201dd1b2017a0eab-'
                        '507000939f17427e951df9791573ac7e-'
                        '7fc5b2d1115d4341b7be206875c40e11'
                    ),
                },
            },
        ),
    ],
    ids=['fixed', 'no_fixed'],
)
@pytest.mark.filldb(order_offers='obsolete')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_decoupling_obsolete_offer_was_not_ok_became_ok(
        taxi_protocol,
        db,
        order_experiments,
        load_json,
        mockserver,
        is_fixed,
        ordercommit_services,
        expected_code,
        decoupling_info,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_fixed_price(enable=is_fixed)
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_user_category_prices_id(
        'd/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        '5f40b7f324414f51a1f9549c65211ea5',
    )
    pricing_data_preparer.set_driver_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )
    pricing_data_preparer.set_driver_surge(NEW_SURGE_VALUE)

    ordercommit_services.surge_value = NEW_SURGE_VALUE

    if is_fixed:
        order_experiments.set_value(['fixed_price'])

    _mock_corp_paymentmethods(mockserver)

    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.offer': 'offer-decoupling-obsolete-fail'}},
    )

    db.order_offers.update(
        {'_id': 'offer-decoupling-obsolete-fail'},
        {'$set': {'is_fixed_price': is_fixed}},
    )

    db.order_offers.update(
        {'_id': 'offer-decoupling-obsolete-fail'},
        {'$set': {'prices[0].pricing_data.is_fixed_price': is_fixed}},
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == expected_code
    if expected_code != 200:
        return
    check(db, decoupling_info)


@pytest.mark.parametrize(
    'is_fixed, expected_code, decoupling_info',
    [
        (True, 406, {}),
        (
            False,
            200,
            {
                'driver_price_info': {
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': NORMAL_OFFER_SURGE_VALUE,
                    'tariff_id': '585a6f47201dd1b2017a0eab',
                },
                'success': True,
                'user_price_info': {
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'sp': 1.0,
                    'tariff_id': (
                        '585a6f47201dd1b2017a0eab-'
                        '507000939f17427e951df9791573ac7e-'
                        '7fc5b2d1115d4341b7be206875c40e11'
                    ),
                },
            },
        ),
    ],
    ids=['fixed', 'no_fixed'],
)
@pytest.mark.parametrize(
    'router_ok', [True, False], ids=['router_ok', 'router_fail'],
)
@pytest.mark.filldb(order_offers='ok')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.config(
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
    ROUTER_42GROUP_ENABLED=False,
    ROUTER_MAPS_ENABLED=True,
)
def test_decoupling_normal_offer_was_not_ok_became_ok(
        taxi_protocol,
        db,
        order_experiments,
        load_json,
        mockserver,
        load_binary,
        is_fixed,
        ordercommit_services,
        expected_code,
        decoupling_info,
        router_ok,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_fixed_price(enable=is_fixed)
    pricing_data_preparer.set_user_category_prices_id(
        'd/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        '5f40b7f324414f51a1f9549c65211ea5',
    )
    pricing_data_preparer.set_driver_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )
    pricing_data_preparer.set_driver_surge(NORMAL_OFFER_SURGE_VALUE)

    if is_fixed:
        order_experiments.set_value(['fixed_price'])

    _mock_corp_paymentmethods(mockserver)

    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.offer': 'offer-decoupling_fail'}},
    )

    db.order_offers.update(
        {'_id': 'offer-decoupling_fail'},
        {'$set': {'is_fixed_price': is_fixed}},
    )

    db.order_offers.update(
        {'_id': 'offer-decoupling-fail'},
        {'$set': {'prices[0].pricing_data.is_fixed_price': is_fixed}},
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == expected_code
    if expected_code != 200:
        return
    check(db, decoupling_info)


@pytest.mark.parametrize(
    'is_fixed, expected_code, decoupling_info',
    [
        (True, 406, {}),
        (
            False,
            200,
            {
                'error': {
                    'stage': 'ordercommit',
                    'reason': 'get_corp_tarif_fail',
                },
                'success': False,
            },
        ),
    ],
    ids=['fixed', 'no_fixed'],
)
@pytest.mark.filldb(order_offers='obsolete')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_decoupling_obsolete_offer_was_not_ok_became_not_ok(
        taxi_protocol,
        db,
        order_experiments,
        load_json,
        mockserver,
        is_fixed,
        ordercommit_services,
        expected_code,
        decoupling_info,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=is_fixed)
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_corp_decoupling(True)

    if is_fixed:
        order_experiments.set_value(['fixed_price'])

    _mock_corp_paymentmethods(mockserver)

    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.offer': 'offer-decoupling-obsolete-fail'}},
    )

    db.order_offers.update(
        {'_id': 'offer-decoupling-obsolete-fail'},
        {'$set': {'is_fixed_price': is_fixed}},
    )

    db.order_offers.update(
        {'_id': 'offer-decoupling-fail'},
        {'$set': {'prices[0].pricing_data.is_fixed_price': is_fixed}},
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == expected_code
    if expected_code != 200:
        return
    check(db, decoupling_info)


@pytest.mark.parametrize(
    'is_fixed, expected_code, decoupling_info',
    [
        (
            True,
            200,
            {
                'error': {
                    'stage': 'calculating_offer',
                    'reason': 'get_corp_tarif_fail',
                },
                'success': False,
            },
        ),
        (
            False,
            200,
            {
                'error': {
                    'stage': 'calculating_offer',
                    'reason': 'get_corp_tarif_fail',
                },
                'success': False,
            },
        ),
    ],
    ids=['fixed', 'no_fixed'],
)
@pytest.mark.filldb(order_offers='ok')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_decoupling_normal_offer_was_not_ok_became_not_ok(
        taxi_protocol,
        db,
        order_experiments,
        load_json,
        mockserver,
        is_fixed,
        expected_code,
        ordercommit_services,
        decoupling_info,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_corp_decoupling(True)

    if is_fixed:
        order_experiments.set_value(['fixed_price'])

    _mock_corp_paymentmethods(mockserver)

    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.offer': 'offer-decoupling_fail'}},
    )

    db.order_offers.update(
        {'_id': 'offer-decoupling_fail'},
        {'$set': {'is_fixed_price': is_fixed}},
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == expected_code
    if expected_code != 200:
        return
    check(db, decoupling_info)


@pytest.mark.filldb(order_offers='obsolete')
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.now('2018-04-24T08:15:00+0000')
def test_decoupling_obsolete_offer_disappear_from_exp(
        taxi_protocol,
        db,
        ordercommit_services,
        load_json,
        mockserver,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_user_category_prices_id(
        'd/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        '5f40b7f324414f51a1f9549c65211ea5',
    )
    pricing_data_preparer.set_driver_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == 406


@pytest.mark.filldb(order_offers='obsolete')
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.now('2018-04-24T08:15:00+0000')
def test_decoupling_obsolete_offer_appear_in_exp(
        taxi_protocol,
        db,
        ordercommit_services,
        load_json,
        mockserver,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_user_category_prices_id(
        'd/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        '5f40b7f324414f51a1f9549c65211ea5',
    )
    pricing_data_preparer.set_driver_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    db.order_offers.update(
        {'_id': 'offer-decoupling-obsolete'}, {'$set': {'extra_data': []}},
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == 406


@pytest.mark.filldb(order_offers='ok')
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_decoupling_normal_offer_price_modifiers(
        taxi_protocol, db, mockserver,
):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.offer': 'offer-decoupling_fixed_price'}},
    )

    _mock_corp_paymentmethods(mockserver)

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )
    assert response.status_code == 200
    check_price_modifiers(db)


CARGO_REQUIREMENTS = {'cargo': 1}


@pytest.mark.order_experiments('fixed_price', 'use_discounts_service')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.filldb(
    requirements='with_multiplier', tariffs='with_multiplier_req',
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_decoupling_no_offer_price_modifiers(
        taxi_protocol,
        db,
        load_json,
        mockserver,
        now,
        ordercommit_services,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_user_category_prices_id(
        'd/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        '5f40b7f324414f51a1f9549c65211ea5',
    )
    pricing_data_preparer.set_driver_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.requirements': CARGO_REQUIREMENTS}},
    )

    _mock_corp_paymentmethods(mockserver)

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )
    assert response.status_code == 200
    check_price_modifiers(db)


@pytest.mark.parametrize(
    'offer_id, order_payment_type',
    [
        ('offer-decoupling_fixed_price', 'cash'),
        ('offer-no-decoupling', 'corp'),
    ],
    ids=['from corp', 'to corp'],
)
@pytest.mark.filldb(order_offers='ok')
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_ordercommit_disallow_change_payment(
        taxi_protocol, db, mockserver, order_payment_type, offer_id,
):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order.request.offer': offer_id,
                'order.request.payment.type': order_payment_type,
                'payment_tech.type': order_payment_type,
            },
        },
    )

    _mock_corp_paymentmethods(mockserver)

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )
    assert response.status_code == 406
    assert response.json() == {
        'error': {'code': 'PAYMENT_TYPE_MISMATCHES_OFFER'},
    }
