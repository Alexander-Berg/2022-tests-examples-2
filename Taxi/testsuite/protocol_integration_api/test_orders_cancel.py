import json

import pytest

from protocol.ordercommit import order_commit_common

USER1 = 'user1'

TRACKER_POSITION = {
    'direction': 328,
    'lat': 55.757743019358564,
    'lon': 37.61672446877377,
    'speed': 30,
    'timestamp': 1502366306,
}

DECOUPLING = {
    'driver_price_info': {
        'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
        'fixed_price': 317.0,
        'sp': 1.0,
        'sp_alpha': 1.0,
        'sp_beta': 0.0,
        'sp_surcharge': 0.0,
        'tariff_id': '585a6f47201dd1b2017a0eab',
    },
    'success': True,
    'user_price_info': {
        'category_id': '5f40b7f324414f51a1f9549c65211ea5',
        'fixed_price': 633.0,
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
}

EN_HEADERS = {'Accept-Language': 'en'}
RU_HEADERS = {'Accept-Language': 'ru'}
CC_EN_HEADERS = {'Accept-Language': 'en', 'User-Agent': 'call_center'}
CC_RU_HEADERS = {'Accept-Language': 'ru', 'User-Agent': 'call_center'}


def make_response(mockserver, response, status=200):
    if isinstance(response, dict):
        response = json.dumps(response)
    return mockserver.make_response(response, status)


@pytest.fixture
def mock_statistics(mockserver):
    class Context:
        health_raw = [{'fallbacks': []}, 200]
        store_raw = [{}, 200]

        def set_health_raw(self, resp, status=200):
            self.health_raw = [resp, status]

        def set_store_raw(self, resp, status=200):
            self.store_raw = [resp, status]

        def set_health(self, fallbacks):
            self.health_raw[0]['fallbacks'] = fallbacks

    context = Context()

    @mockserver.handler('/statistics/v1/service/health')
    def mock_health(request):
        return make_response(
            mockserver, context.health_raw[0], context.health_raw[1],
        )

    @mockserver.handler('/statistics/v1/metrics/store')
    def mock_store(request):
        return make_response(
            mockserver, context.store_raw[0], context.store_raw[1],
        )

    return context


@pytest.fixture()
def make_corp_payment(db, order_id):
    db.orders.find_and_modify(
        {'_id': order_id, '_shard_id': 0},
        {'$set': {'payment_tech.type': 'corp'}},
        False,
    )


def make_decoupling_checks(
        db, order_id, response, user_cost, driver_cost, fallback,
):
    assert response.status_code == 200
    content = response.json()

    assert content['status'] == 'cancelled'

    proc = db.order_proc.find_one(order_id)
    assert proc['order']['cost'] == user_cost

    decoupling = proc['order']['decoupling']
    assert decoupling['driver_price_info']['cost'] == driver_cost
    assert decoupling['user_price_info']['cost'] == user_cost
    order_commit_common.check_current_prices(proc, 'final_cost', user_cost)

    current_prices = proc['order']['current_prices']
    assert current_prices['kind'] == 'final_cost'
    assert current_prices['final_cost'] == {
        'driver': {'total': driver_cost},
        'user': {'total': user_cost},
    }
    assert current_prices['final_cost_meta'] == {
        'driver': {
            'driver_meta': driver_cost,
            'paid_cancel_in_waiting_price': driver_cost,
        },
        'user': {
            'user_meta': user_cost,
            'paid_cancel_in_waiting_price': user_cost,
        },
    }


@pytest.mark.parametrize(
    'use_order_core',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    PROCESSING_BACKEND_CPP_SWITCH=[
                        'cancel-order-from-protocol',
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.config(CALLCENTER_ORDER_TIME_TO_CANCEL=600)
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'order_id,reason',
    [
        pytest.param(
            'order_assigned_driving', None, id='order assigned driving',
        ),
        pytest.param(
            'order_assigned_waiting',
            ['usererror'],
            id='order assigned waiting',
        ),
        pytest.param(
            'order_status_update',
            ['driverrequest', 'usererror'],
            id='order status update less than conf time',
        ),
    ],
)
@pytest.mark.parametrize(
    'passenger_feedback_called',
    [
        pytest.param(False, id='old_feedback'),
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='exp3_use_passenger_feedback.json',
            ),
            id='new_feedback',
        ),
    ],
)
def test_orders_cancel_simple(
        db,
        taxi_integration,
        recalc_order,
        tracker,
        order_id,
        reason,
        now,
        mockserver,
        passenger_feedback_called,
        use_order_core,
        mock_order_core,
):
    @mockserver.json_handler('/feedback/1.0/save')
    def mock_feedback_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': True,
            'call_me': False,
            'order_id': order_id,
            'order_cancelled': True,
            'phone_id': '',
            'choices': [
                {'type': 'cancelled_reason', 'value': value}
                for value in reason
                if reason is not None
            ],
            'created_time': '2018-01-01T08:30:00+0000',
            'order_created_time': '2016-12-15T09:35:00+0000',
            'app_comment': False,
            'order_completed': False,
            'allow_overwrite': True,
            'order_zone': 'moscow',
            'id': USER1,
            'badges': [],
        }
        return {}

    @mockserver.json_handler(
        '/passenger_feedback/passenger-feedback/v2/feedback',
    )
    def mock_passenger_feedback_save(request):
        data = json.loads(request.get_data())
        assert data['order_taxi_status']
        del data['order_taxi_status']
        assert data == {
            'call_me': False,
            'order_id': order_id,
            'phone_id': '',
            'choices': {
                'cancelled_reason': [
                    value for value in reason if reason is not None
                ],
                'low_rating_reason': [],
                'rating_reason': [],
            },
            'created_time': '2018-01-01T08:30:00+00:00',
            'order_created_time': '2016-12-15T09:35:00+00:00',
            'app_comment': False,
            'order_zone': 'moscow',
            'id': USER1,
            'order_status': 'cancelled',
        }
        return {}

    tracker.set_position(
        'driver_id', now, 55.73341076871702, 37.58917997300821,
    )

    request = {'userid': USER1, 'orderid': order_id}
    if reason is not None:
        request['cancelled_reason'] = reason

    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=CC_RU_HEADERS,
    )
    assert response.status_code == 200
    if reason is not None:
        if not passenger_feedback_called:
            mock_feedback_save.wait_call()
        else:
            mock_passenger_feedback_save.wait_call()

    data = response.json()
    assert data['status'] == 'cancelled'

    proc = db.order_proc.find_one({'_id': order_id, 'order.user_id': USER1})
    assert 'order' in proc
    order = proc['order']
    assert order['status'] == 'cancelled'
    assert proc['processing'] == {'need_start': True, 'version': 1}
    assert proc['status'] == 'finished'
    assert proc['order_info']['need_sync'] is True
    assert proc['order_info']['statistics']['status_updates'][-1] == {
        'c': now,
        'h': True,
        's': 'cancelled',
        'q': 'cancel',
    }
    assert mock_order_core.post_event_times_called == bool(use_order_core)


@pytest.mark.parametrize(
    'cross_device_enabled, check_user_by_uid',
    [
        pytest.param(False, False),
        pytest.param(
            True, False, marks=[pytest.mark.config(CROSSDEVICE_ENABLED=True)],
        ),
        pytest.param(
            True,
            True,
            marks=[
                pytest.mark.config(
                    CROSSDEVICE_ENABLED=True,
                    INTEGRATION_ORDERS_CANCEL_CHECK_USER_BY_UID=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'get_uid_with_user_api',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    INTEGRATION_ORDERS_CANCEL_GET_UID_WITH_USER_API=True,
                    USER_API_USERS_ENDPOINTS={'users/get': True},
                ),
            ],
        ),
    ],
)
@pytest.mark.config(CALLCENTER_ORDER_TIME_TO_CANCEL=600)
@pytest.mark.now('2018-01-01T11:30:00+0300')
def test_cross_device(
        db,
        taxi_integration,
        tracker,
        now,
        cross_device_enabled,
        check_user_by_uid,
        get_uid_with_user_api,
        mock_user_api,
):
    user_id = 'user2'
    order_id = 'order_assigned_driving'
    tracker.set_position(
        'driver_id', now, 55.73341076871702, 37.58917997300821,
    )

    request = {'userid': user_id, 'orderid': order_id}

    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=CC_RU_HEADERS,
    )

    if cross_device_enabled:
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'cancelled'
    else:
        assert response.status_code == 404

    proc = db.order_proc.find_one({'_id': order_id, 'order.user_id': 'user1'})
    assert 'order' in proc
    if cross_device_enabled:
        assert proc['order']['status'] == 'cancelled'
        assert proc['status'] == 'finished'
    else:
        assert proc['order']['status'] == 'assigned'
    if get_uid_with_user_api:
        assert mock_user_api.users_get_times_called == 1 + int(
            check_user_by_uid,
        )


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'order_id',
    (
        pytest.param('order_assigned_driving', id='order assigned driving'),
        pytest.param(
            'order_transporting',
            id='order assigned transporting, time to cancel is ok',
        ),
    ),
)
@pytest.mark.config(
    PROCESSING_BACKEND_CPP_SWITCH=['cancel-order-from-protocol'],
)
@pytest.mark.config(CALLCENTER_ORDER_TIME_TO_CANCEL=750)
def test_orders_cancel_callcenter_enabled(
        db, taxi_integration, tracker, order_id, now, mockserver,
):
    tracker.set_position(
        'driver_id', now, 55.73341076871702, 37.58917997300821,
    )

    request = {'userid': USER1, 'orderid': order_id}

    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=CC_RU_HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data['status'] == 'cancelled'
    proc = db.order_proc.find_one({'_id': order_id, 'order.user_id': USER1})
    assert 'order' in proc
    order = proc['order']
    assert order['status'] == 'cancelled'
    assert proc['processing'] == {'need_start': True, 'version': 1}
    assert proc['status'] == 'finished'
    assert proc['order_info']['need_sync'] is True
    assert proc['order_info']['statistics']['status_updates'][-1] == {
        'c': now,
        'h': True,
        's': 'cancelled',
        'q': 'cancel',
    }


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    ('order_id', 'is_cancelled', 'user_id'),
    (
        pytest.param(
            'order_assigned_driving',
            True,
            'user1',
            id='order assigned driving',
        ),
        pytest.param(
            'order_transporting',
            False,
            'user1',
            id='order assigned transporting, too many time gone',
        ),
    ),
)
@pytest.mark.config(CALLCENTER_ORDER_TIME_TO_CANCEL=0)
@pytest.mark.config(
    PROCESSING_BACKEND_CPP_SWITCH=['cancel-order-from-protocol'],
)
def test_orders_cancel_callcenter_disabled(
        db,
        taxi_integration,
        tracker,
        order_id,
        user_id,
        now,
        mockserver,
        is_cancelled,
):

    tracker.set_position(
        'driver_id', now, 55.73341076871702, 37.58917997300821,
    )

    request = {'userid': user_id, 'orderid': order_id}

    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=CC_RU_HEADERS,
    )
    data = response.json()
    if is_cancelled:
        assert response.status_code == 200
        assert data['status'] == 'cancelled'
        proc = db.order_proc.find_one(
            {'_id': order_id, 'order.user_id': 'user1'},
        )
        assert 'order' in proc
        order = proc['order']
        assert order['status'] == 'cancelled'
        assert proc['processing'] == {'need_start': True, 'version': 1}
        assert proc['status'] == 'finished'
        assert proc['order_info']['need_sync'] is True
        assert proc['order_info']['statistics']['status_updates'][-1] == {
            'c': now,
            'h': True,
            's': 'cancelled',
            'q': 'cancel',
        }
    else:
        assert response.status_code == 409
        proc = db.order_proc.find_one(
            {'_id': order_id, 'order.user_id': 'user1'},
        )
        assert 'order' in proc
        order = proc['order']
        assert order['status'] != 'cancelled'


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.config(
    INTEGRATION_ORDER_TIME_TO_CANCEL=600,
    ENABLE_PAID_CANCEL=True,
    PROCESSING_BACKEND_CPP_SWITCH=['cancel-order-from-protocol'],
)
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
def test_orders_cancel_paid_supply(db, taxi_integration, mockserver):
    order_id = 'order_assigned_driving_paid_supply'

    request = {'userid': USER1, 'orderid': order_id}

    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=CC_RU_HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data['status'] == 'cancelled'

    proc = db.order_proc.find_one({'_id': order_id, 'order.user_id': 'user1'})
    assert 'order' in proc
    order = proc['order']
    assert order['status'] == 'cancelled'
    assert order['cost'] == 75


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'order_id,reason',
    [('order_status_update', ['driverrequest', 'usererror'])],
)
@pytest.mark.config(CALLCENTER_ORDER_TIME_TO_CANCEL=600)
@pytest.mark.config(
    PROCESSING_BACKEND_CPP_SWITCH=['cancel-order-from-protocol'],
)
def test_race(
        db,
        taxi_integration,
        recalc_order,
        tracker,
        order_id,
        testpoint,
        reason,
        now,
        mockserver,
):
    """
    Test checks:
    1. cancel
    2. race while cancelling
    3. cancel after cancelling
    """

    @mockserver.json_handler('/feedback/1.0/save')
    def mock_feedback_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': True,
            'call_me': False,
            'order_id': order_id,
            'order_cancelled': True,
            'phone_id': '',
            'choices': [
                {'type': 'cancelled_reason', 'value': value}
                for value in reason
                if reason is not None
            ],
            'created_time': '2018-01-01T08:30:00+0000',
            'order_created_time': '2016-12-15T09:35:00+0000',
            'app_comment': False,
            'order_completed': False,
            'allow_overwrite': True,
            'order_zone': 'moscow',
            'id': 'user1',
            'badges': [],
        }
        return {}

    tracker.set_position(
        'driver_id', now, 55.73341076871702, 37.58917997300821,
    )

    request = {'userid': 'user1', 'orderid': order_id}
    if reason is not None:
        request['cancelled_reason'] = reason

    proc_base = {}
    query = {'_id': order_id, 'order.user_id': 'user1'}

    testpoint_calls = []
    testpoint_name = 'orderscancel::on_cancel'

    @testpoint(testpoint_name)
    def call_parallel_cancel(input_data):

        if len(testpoint_calls) > 0:
            return  # avoid recursive calls
        testpoint_calls.append(input_data)

        # 1. cancel
        response = taxi_integration.post(
            'v1/orders/cancel', request, headers=CC_RU_HEADERS,
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'cancelled'

        if reason is not None:
            mock_feedback_save.wait_call()

        proc = db.order_proc.find_one(query)
        proc_base.update(proc)
        assert 'order' in proc
        order = proc['order']
        assert order['status'] == 'cancelled'
        assert proc['processing'] == {'need_start': True, 'version': 1}
        assert proc['status'] == 'finished'
        assert proc['order_info']['need_sync'] is True
        assert proc['order_info']['statistics']['status_updates'][-1] == {
            'c': now,
            'h': True,
            's': 'cancelled',
            'q': 'cancel',
        }

    # 2. race while cancelling
    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=CC_RU_HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data == {}
    assert not mock_feedback_save.has_calls  # dont call as already called
    second_proc = db.order_proc.find_one(query)
    assert proc_base == second_proc

    # 3. cancel after cancelling
    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=CC_RU_HEADERS,
    )
    assert response.status_code == 200

    assert not mock_feedback_save.has_calls
    data = response.json()
    assert data == {}

    # check request hasn't changed order_proc
    second_proc = db.order_proc.find_one(query)
    assert proc_base == second_proc


@pytest.mark.parametrize(
    ('sourceid', 'code'),
    (
        ('corp_cabinet', 200),
        ('alice', 200),
        ('svo_order', 200),
        ('uber', 400),
        ('wrong', 400),
    ),
)
@pytest.mark.config(INTEGRATION_ORDER_TIME_TO_CANCEL=600)
def test_sourceid(
        db,
        taxi_integration,
        recalc_order,
        tracker,
        now,
        mockserver,
        sourceid,
        code,
):
    """
    Check allowable values of sourceid in request for int-api
    """

    order_id = 'order_assigned_driving'

    tracker.set_position(
        'driver_id', now, 55.73341076871702, 37.58917997300821,
    )

    request = {'userid': 'user1', 'orderid': order_id, 'sourceid': sourceid}

    response = taxi_integration.post('v1/orders/cancel', request)
    assert response.status_code == code, response
    data = response.json()

    if code == 200:
        assert data['status'] == 'cancelled'
    elif code == 400:
        assert data == {'error': {'text': 'source_id invalid'}}
    else:
        assert False


@pytest.mark.parametrize(
    'sourceid,code',
    [
        ('corp_cabinet', 409),
        ('alice', 409),
        ('svo_order', 409),
        ('cargo', 200),
    ],
)
@pytest.mark.config(CARGO_ORDERS_CANCEL_FORBIDDEN=True)
@pytest.mark.config(INTEGRATION_ORDER_TIME_TO_CANCEL=600)
def test_cargo_sourceid(
        db,
        taxi_integration,
        recalc_order,
        tracker,
        now,
        mockserver,
        sourceid,
        code,
):
    """
    Check that cargo order cannot be cancelled outside the cargo
    """

    order_id = 'cargo_order'

    tracker.set_position(
        'driver_id', now, 55.73341076871702, 37.58917997300821,
    )

    request = {'userid': 'user1', 'orderid': order_id, 'sourceid': sourceid}

    response = taxi_integration.post('v1/orders/cancel', request)
    assert response.status_code == code, response
    data = response.json()

    if code == 200:
        assert data['status'] == 'cancelled'
    elif code == 409:
        assert data == {
            'error': {'code': 'IS_CARGO_ORDER', 'text': 'IS_CARGO_ORDER'},
        }
    else:
        assert False


@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['good'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {'match': 'good', '@app_name': 'good', '@app_ver1': '2'},
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
@pytest.mark.parametrize(
    'user_agent,code',
    [('good', 200), ('siri', 400)],
    ids=['valid_app', 'invalid_app'],
)
def test_application(taxi_integration, recalc_order, user_agent, code):
    response = taxi_integration.post(
        'v1/orders/cancel',
        {'userid': 'user1', 'orderid': 'order_assigned_driving'},
        headers={'User-Agent': user_agent},
    )

    assert response.status_code == code, response
    data = response.json()

    if code == 200:
        assert data['status'] == 'cancelled'
    elif code == 400:
        assert data == {'error': {'text': 'Invalid application'}}
    else:
        assert False


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'body,expected_code,expected_response',
    [
        (
            {'userid': 'user_not_found', 'orderid': 'order_assigned_driving'},
            404,
            'Proc with order_id: order_assigned_driving and user_id: '
            'user_not_found not found',
        ),
        (
            {'userid': 'user1', 'orderid': 'order_not_found'},
            404,
            'Proc with order_id: order_not_found and user_id: user1 not found',
        ),
        ({'orderid': 'order_assigned_driving'}, 400, 'no userid'),
        (
            {
                'userid': 'user1',
                'orderid': 'order_transporting_cant_be_cancelled',
            },
            409,
            'PAID_CANCEL_IS_DISABLED',
        ),
        (
            {'userid': 'user1', 'orderid': 'order_without_candidate_index'},
            409,
            'PAID_CANCEL_IS_DISABLED',
        ),
    ],
    ids=[
        'proc not found by user_id',
        'user_id is required',
        'proc not found by order_id',
        'order cant be cancelled by time',
        'support missing candidate index',
    ],
)
@pytest.mark.config(INTEGRATION_ORDER_TIME_TO_CANCEL=600)
def test_orders_cancel_errors(
        taxi_integration,
        recalc_order,
        tracker,
        body,
        expected_code,
        expected_response,
        mockserver,
        now,
        db,
):
    tracker.set_position(
        'driver_id', now, 55.73341076871702, 37.58917997300821,
    )

    response = taxi_integration.post(
        'v1/orders/cancel', json=body, headers=CC_RU_HEADERS,
    )
    assert response.status_code == expected_code, response.text

    data = response.json()
    assert data['error']['text'] == expected_response


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.config(INTEGRATION_ORDER_TIME_TO_CANCEL=600)
@pytest.mark.config(
    PROCESSING_BACKEND_CPP_SWITCH=['cancel-order-from-protocol'],
)
def test_orders_cancel_with_feedback_service(
        db, taxi_integration, tracker, mockserver, now,
):
    tracker.set_position(
        'driver_id', now, 55.73341076871702, 37.58917997300821,
    )
    order_id = 'order_assigned_driving'

    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': True,
            'call_me': False,
            'order_id': order_id,
            'reorder_id': 'reorder_id',
            'order_cancelled': True,
            'phone_id': '59246c5b6195542e9b084206',
            'choices': [{'type': 'cancelled_reason', 'value': 'usererror'}],
            'created_time': '2018-01-01T08:30:00+0000',
            'order_created_time': '2016-12-15T09:35:00+0000',
            'app_comment': False,
            'allow_overwrite': True,
            'order_completed': False,
            'order_zone': 'moscow',
            'id': 'user1',
            'badges': [],
        }
        return {}

    request = {
        'userid': 'user1',
        'orderid': order_id,
        'cancelled_reason': ['usererror'],
    }

    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=CC_RU_HEADERS,
    )
    assert response.status_code == 200

    assert mock_service_save.times_called == 1

    data = response.json()
    assert data == {'status': 'cancelled'}

    proc = db.order_proc.find_one({'_id': order_id, 'order.user_id': 'user1'})
    assert 'order' in proc
    order = proc['order']
    assert order['status'] == 'cancelled'
    assert proc['processing'] == {'need_start': True, 'version': 1}
    assert proc['status'] == 'finished'
    assert proc['order_info']['need_sync'] is True
    assert proc['order_info']['statistics']['status_updates'][-1] == {
        'c': now,
        'h': True,
        's': 'cancelled',
        'q': 'cancel',
    }


@pytest.mark.parametrize(
    'order_id,state,expected_state,error_code,sourceid,headers',
    [
        (
            'order_assigned_driving',
            'paid',
            'free',
            'INCOMPATIBLE_CANCEL_STATE',
            'corp_cabinet',
            RU_HEADERS,
        ),
        (
            'order_assigned_waiting',
            'paid',
            'free',
            'INCOMPATIBLE_CANCEL_STATE',
            'corp_cabinet',
            RU_HEADERS,
        ),
        (
            'order_with_performer',
            'free',
            'paid',
            'INCOMPATIBLE_CANCEL_STATE',
            'corp_cabinet',
            RU_HEADERS,
        ),
    ],
    ids=['driving', 'waiting', 'transporting, could cancel'],
)
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.filldb(orders='corp_payment')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.config(INTEGRATION_TIME_TO_CANCEL_CORP_CABINET=120)
def test_wrong_cancel_state(
        taxi_integration,
        tracker,
        now,
        mockserver,
        db,
        order_id,
        state,
        expected_state,
        error_code,
        sourceid,
        headers,
):
    tracker.set_position(
        'driver_id', now, 55.757743019358564, 37.61672446877377,
    )

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return TRACKER_POSITION

    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        return {}

    if not sourceid:  # call_center
        make_corp_payment(db, order_id)

    request = {
        'userid': 'user1',
        'orderid': order_id,
        'cancel_state': state,
        'cancelled_reason': ['usererror'],
    }

    if sourceid:
        request['sourceid'] = sourceid

    response = taxi_integration.post(
        'v1/orders/cancel', json=request, headers=headers,
    )
    assert response.status_code == 409, response.text
    assert mock_service_save.times_called == 0

    data = response.json()
    assert data['cancel_rules']['state'] == expected_state
    assert data['error']['code'] == data['error']['text'] == error_code


@pytest.mark.parametrize(
    ('sourceid', 'headers'),
    [('corp_cabinet', EN_HEADERS)],
    ids=['corp cabinet order'],
)
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.filldb(orders='corp_payment')
@pytest.mark.config(INTEGRATION_TIME_TO_CANCEL_CORP_CABINET=120)
def test_paid_cancel(
        taxi_integration, tracker, now, mockserver, sourceid, headers, db,
):
    tracker.set_position(
        'driver_id', now, 55.757743019358564, 37.61672446877377,
    )

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return TRACKER_POSITION

    @mockserver.json_handler('/feedback/1.0/save')
    def mock_feedback_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': True,
            'call_me': False,
            'order_id': order_id,
            'order_cancelled': True,
            'phone_id': '',
            'choices': [{'type': 'cancelled_reason', 'value': 'usererror'}],
            'created_time': '2018-01-01T08:30:00+0000',
            'order_created_time': '2016-12-15T09:35:00+0000',
            'app_comment': False,
            'order_completed': False,
            'allow_overwrite': True,
            'order_zone': 'moscow',
            'id': 'user1',
            'badges': [],
        }
        return {}

    order_id = 'order_with_performer'
    if not sourceid:  # call_center
        make_corp_payment(db, order_id)

    request = {
        'userid': 'user1',
        'orderid': order_id,
        'cancel_state': 'paid',
        'cancelled_reason': ['usererror'],
    }
    if sourceid:
        request['sourceid'] = sourceid

    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=headers,
    )
    assert response.status_code == 200
    assert mock_feedback_save.times_called == 1

    data = response.json()
    assert data['status'] == 'cancelled'


@pytest.mark.parametrize(
    'sourceid, headers',
    [('corp_cabinet', EN_HEADERS), (None, CC_EN_HEADERS)],
    ids=['corp cabinet order', 'call center order with corp payment'],
)
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.filldb(orders='corp_payment')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.config(INTEGRATION_TIME_TO_CANCEL_CORP_CABINET=60)
def test_paid_cancel_disabled_by_time(
        taxi_integration, tracker, now, mockserver, sourceid, headers, db,
):
    tracker.set_position(
        'driver_id', now, 55.757743019358564, 37.61672446877377,
    )

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return TRACKER_POSITION

    @mockserver.json_handler('/feedback/1.0/save')
    def mock_feedback_save(request):
        return {}

    order_id = 'order_with_performer'
    if not sourceid:  # call_center
        make_corp_payment(db, order_id)

    request = {
        'userid': 'user1',
        'orderid': order_id,
        'cancel_state': 'paid',
        'cancelled_reason': ['usererror'],
    }
    if sourceid:
        request['sourceid'] = sourceid

    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=headers,
    )
    assert response.status_code == 409, response.text
    assert mock_feedback_save.times_called == 0

    data = response.json()
    assert data['error']['code'] == 'INCOMPATIBLE_CANCEL_STATE'
    cancel_rules = {
        'message': 'Cancellation time is over',
        'message_support': (
            'Please indicate if the driver\'s at fault. Describe'
            ' what happened — we will check everything,'
            ' and correct the situation.'
        ),
        'state': 'disabled',
        'title': 'Cancellation is unavailable',
    }
    assert data['cancel_rules'] == cancel_rules


@pytest.mark.parametrize(
    'sourceid, headers, user_cost, driver_cost',
    [('corp_cabinet', EN_HEADERS, 198, 99)],
    ids=['corp cabinet order'],
)
@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.filldb(orders='corp_payment')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.config(INTEGRATION_TIME_TO_CANCEL_CORP_CABINET=120)
def test_paid_cancel_decoupling(
        taxi_integration,
        tracker,
        recalc_order,
        now,
        mockserver,
        sourceid,
        headers,
        db,
        load_json,
        user_cost,
        driver_cost,
):
    tracker.set_position(
        'driver_id', now, 55.757743019358564, 37.61672446877377,
    )

    recalc_order.set_driver_recalc_result(
        driver_cost, driver_cost, {'driver_meta': driver_cost},
    )
    recalc_order.set_user_recalc_result(
        user_cost, user_cost, {'user_meta': user_cost},
    )

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return TRACKER_POSITION

    @mockserver.json_handler('/feedback/1.0/save')
    def mock_feedback_save(request):
        return {}

    @mockserver.json_handler('/corp_integration_api/tariffs')
    def mock_tariffs(request):
        return load_json('tariffs_response.json')

    order_id = 'order_with_performer'

    if not sourceid:  # call_center
        make_corp_payment(db, order_id)

    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.decoupling': DECOUPLING}},
    )

    request = {
        'userid': 'user1',
        'orderid': order_id,
        'cancel_state': 'paid',
        'cancelled_reason': ['usererror'],
    }
    if sourceid:
        request['sourceid'] = sourceid

    response = taxi_integration.post(
        'v1/orders/cancel', request, headers=headers,
    )
    make_decoupling_checks(
        db, order_id, response, user_cost, driver_cost, False,
    )
