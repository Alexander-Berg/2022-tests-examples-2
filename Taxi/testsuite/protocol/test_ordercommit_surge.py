import pytest


ORDER_ID = 'surge_12'
USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'


@pytest.mark.filldb(order_proc='pending')
@pytest.mark.parametrize(
    'new_surge_value, surge_variable_name',
    [(1.1, 'sp'), (1.2, 'sp'), (1.3, 'spr')],
)
@pytest.mark.order_experiments('forced_surge')
def test_ordercommit_change_surge_price(
        taxi_protocol,
        mockserver,
        db,
        new_surge_value,
        surge_variable_name,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    """
    Tests that surge price from order
    correctly changed by surge price from offer

    If offer-surge bigger then order-surge
        then offer-surge will be created as 'spr'
        and old surge 'sp' will be deleted
    In the other way 'sp' will be changed with
        the new surge
    """

    order_before = db.order_proc.find_one({'_id': ORDER_ID})
    surge_price_before = order_before['order']['request']['sp']
    assert surge_price_before == 1.2

    pricing_data_preparer.set_user_surge(new_surge_value)

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )
    assert response.status_code == 200

    order_after = db.order_proc.find_one({'_id': ORDER_ID})
    surge_price_after = order_after['order']['request'][surge_variable_name]
    assert surge_price_after == new_surge_value


@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('forced_surge')
def test_ordercommit_request_forced_surge_changed(
        taxi_protocol, mockserver, db, config, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    """
        Tests that forced surge has lifetime
    """

    magic_surge_price = 1.3
    pricing_data_preparer.set_user_surge(magic_surge_price)

    config.set_values(dict(DEFAULT_URGENCY=0))
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': 'surge_12_future'},
    )

    assert response.status_code == 406
    data = response.json()
    assert data['error'] == {'code': 'FORCED_SURGE_CHANGED'}


@pytest.mark.now('2020-01-29T12:00:00+0000')
@pytest.mark.filldb(
    order_proc='surge_bug_23003', tariff_settings='fixed_price',
)
@pytest.mark.order_experiments('forced_surge', 'fixed_price')
@pytest.mark.parametrize('exp_status_code', [200, 406])
def test_ordercommit_surge_bug_23003(
        taxi_protocol,
        mockserver,
        db,
        config,
        experiments3,
        load_json,
        exp_status_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    if exp_status_code == 200:
        pricing_data_preparer.set_cost(649.065706112, 649.065706112)
        pricing_data_preparer.set_user_surge(3.0)
        pricing_data_preparer.set_driver_surge(3.0)
        experiments3.add_experiments_json(
            load_json('experiments3_fix_surge_23003.json'),
        )
        taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': 'surge_bug_23003'},
    )

    assert response.status_code == exp_status_code
    if exp_status_code != 200:
        data = response.json()
        assert data['error'] == {'code': 'PRICE_CHANGED'}
