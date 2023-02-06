import datetime
import json

import pytest


ORDERCOMMIT_URL = '3.0/ordercommit'


@pytest.mark.parametrize(
    (
        'preorder_request_id',
        'set_due',
        'oso',
        'expected_code',
        'expected_error',
    ),
    [
        # Some tests are duplicates of what is in other parts - just to be sure
        pytest.param(
            None,
            False,
            True,
            200,
            {},
            id='Not a preorder without due - should work',
        ),
        pytest.param(
            None,
            False,
            False,
            200,
            {},
            id='Not a preorder without due, OSO False - should work',
        ),
        pytest.param(
            None,
            True,
            True,
            406,
            {'code': 'TARIFF_IS_UNAVAILABLE'},
            id='Not a preorder, due set, OSO True - should fail',
        ),
        pytest.param(
            None,
            True,
            False,
            200,
            {},
            id='Not a preorder, due set, OSO False - should work',
        ),
        pytest.param(
            'preorder_request_id_1',
            True,
            True,
            200,
            {},
            id='Preorder, due set, OSO True - should work',
        ),
        pytest.param(
            'preorder_request_id_1',
            True,
            False,
            200,
            {},
            id='Preorder, due set, OSO False - should work',
        ),
    ],
)
def test_ordercommit_for_preorder(
        taxi_protocol,
        load,
        mockserver,
        db,
        preorder_request_id,
        set_due,
        oso,
        expected_code,
        expected_error,
        pricing_data_preparer,
):
    """
    Check that ordercommit doesn't fail if order.due is present,
    but only_for_soon_orders flag is set in the zone
    """

    pricing_data_preparer.set_locale('ru')

    _mock_surge(mockserver)

    # Update only_for_soon_orders flag (oso)
    db.tariff_settings.update({'hz': 'moscow'}, {'$set': {'s.0.oso': oso}})

    # Update order_proc
    update_set = {}
    update_set['order.preorder_request_id'] = preorder_request_id
    if set_due:
        update_set['order.request.due'] = datetime.datetime.utcnow()
    if update_set:
        db.order_proc.update({'_id': 'orderid'}, {'$set': update_set})

    # Do the actual request
    request = {'id': 'user_id', 'orderid': 'orderid'}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)

    assert response.status_code == expected_code
    if expected_code > 200:
        assert response.json() == {'error': expected_error}


# don't test common::preorder::FilterPreorderClasses  function here
# expect it was tested in routestats tests
@pytest.mark.now('2019-06-26T21:19:09+0300')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True,
    PREORDER_PAYMENT_METHODS=['cash'],
    PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    'allowed_time_info,order_classes,response_code',
    (
        (
            [],
            [
                {
                    'name': 'econom',
                    'value': 1.0,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
                {
                    'name': 'vip',
                    'value': 1.0,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
            406,
        ),
        (
            [
                {
                    'class': 'econom',
                    'interval_minutes': 15,
                    'allowed_time_ranges': [
                        {
                            'from': '2017-05-25T11:20:00+0300',
                            'to': '2099-05-25T11:40:00+0300',
                        },
                    ],
                },
            ],
            [
                {
                    'name': 'econom',
                    'value': 1.0,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
            200,
        ),
        ([], [], 406),
    ),
)
def test_request_for_preorder(
        now,
        taxi_protocol,
        mockserver,
        load_json,
        db,
        allowed_time_info,
        order_classes,
        response_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    _mock_surge(mockserver)

    @mockserver.json_handler('/preorder/4.0/preorder/v1/availability')
    def check_availability(request):
        return {
            'preorder_request_id': 'preorder_request_id_1',
            'allowed_time_info': allowed_time_info,
        }

    update_set = {}
    update_set['order.request.due'] = now
    update_set['order.request.classes'] = order_classes
    db.order_proc.update({'_id': 'orderid'}, {'$set': update_set})

    request = {'id': 'user_id', 'orderid': 'orderid'}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)

    assert response.status_code == response_code


@pytest.mark.now('2019-06-26T21:19:09+0300')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True,
    PREORDER_PAYMENT_METHODS=['cash'],
    PREORDER_CLASSES=['econom'],
)
def test_request_route(
        now, taxi_protocol, mockserver, load_json, db, pricing_data_preparer,
):
    """
    Check that all route points passed to preorder/v1/availability
    and in right order
    """

    pricing_data_preparer.set_locale('ru')

    _mock_surge(mockserver)

    order_proc = db.order_proc.find_one({'_id': 'orderid'})
    full_route = [order_proc['order']['request']['source']['geopoint']]
    destinations = order_proc['order']['request']['destinations']
    full_route.extend(dest['geopoint'] for dest in destinations)

    @mockserver.json_handler('/preorder/4.0/preorder/v1/availability')
    def check_availability(request):
        data = json.loads(request.get_data())
        assert data['route'] == full_route

        return {
            'preorder_request_id': 'preorder_request_id_1',
            'allowed_time_info': [
                {
                    'class': 'econom',
                    'interval_minutes': 15,
                    'allowed_time_ranges': [
                        {
                            'from': '2017-05-25T11:20:00+0300',
                            'to': '2099-05-25T11:40:00+0300',
                        },
                    ],
                },
            ],
        }

    update_set = {'order.request.due': now}
    db.order_proc.update({'_id': 'orderid'}, {'$set': update_set})

    request = {'id': 'user_id', 'orderid': 'orderid'}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)

    assert response.status_code == 200


def _mock_surge(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.0,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }


@pytest.mark.now('2019-06-26T21:19:09+0300')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True,
    PREORDER_PAYMENT_METHODS=['cash'],
    PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    'requirement, ret_code',
    (
        pytest.param(3, 200, id='check_one_chair'),
        pytest.param([7, 3], 406, id='check_two_chairs'),
    ),
)
def test_preorder_requirements_max_options(
        taxi_protocol,
        load_json,
        db,
        mockserver,
        requirement,
        ret_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler('/v1/configs/updates')
    def experiments3_proxy(*args, **kwargs):
        return load_json('requirements_black_list.json')

    _mock_surge(mockserver)

    update_set = {}
    if isinstance(requirement, list):
        for n, val in enumerate(requirement, start=0):
            update_set[
                'order.request.requirements.childchair_for_child_tariff.'
                + str(n)
            ] = val
    else:
        update_set[
            'order.request.requirements.childchair_for_child_tariff'
        ] = requirement

    db.order_proc.update({'_id': 'reqs_order'}, {'$set': update_set})

    request = {'id': 'user_id', 'orderid': 'reqs_order'}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)

    assert response.status_code == ret_code


@pytest.mark.now('2019-06-26T21:19:09+0300')
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True,
    PREORDER_PAYMENT_METHODS=['cash'],
    PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    'requirement, ret_code',
    (pytest.param(1, 200, id='200'), pytest.param(2, 406, id='406')),
)
def test_preorder_requirements_list(
        taxi_protocol,
        load_json,
        db,
        mockserver,
        requirement,
        ret_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler('/v1/configs/updates')
    def experiments3_proxy(*args, **kwargs):
        return load_json('requirements_black_list.json')

    _mock_surge(mockserver)

    update_set = {'order.request.requirements.cargo_loaders': requirement}

    db.order_proc.update({'_id': 'reqs_cargo'}, {'$set': update_set})

    request = {'id': 'user_id', 'orderid': 'reqs_cargo'}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == ret_code
