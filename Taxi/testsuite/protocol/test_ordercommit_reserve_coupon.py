import json
import re

import pytest

from protocol.order_test_utils import couponreserve  # noqa: F401
from protocol.ordercommit import order_commit_common


def is_valid_reserve_token(token):
    pattern = re.compile('^[A-Za-z0-9]{20}$')
    return pattern.match(token) is not None


@pytest.fixture()
def surge(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.2,
                    'reason': 'pins_free',
                    'antisurge': False,
                },
            ],
        }


@pytest.fixture(name='mock_coupons')
def _mock_coupons(mockserver):
    class Context:
        _reserve_token = None
        _user_agent = None
        _response_code = 200
        _response_body = {
            'exists': True,
            'valid': True,
            'valid_any': True,
            'value': 200,
            'series': 'onlyoneusage',
        }

        @property
        def reserve_token(self):
            return self._reserve_token

        def set_reserve_token(self, value):
            self._reserve_token = value

        @property
        def user_agent(self):
            return self._user_agent

        def set_user_agent(self, value):
            self._user_agent = value

        @property
        def response_code(self):
            return self._response_code

        def set_response_code(self, value):
            self._response_code = value

        @property
        def response_body(self):
            return self._response_body

        def set_response_body(self, value):
            self._response_body = value

    context = Context()

    @mockserver.json_handler('/coupons/v1/couponreserve')
    def mock_couponreserve(request):
        headers = dict(request.headers)

        assert 'X-Idempotency-Token' in headers
        assert is_valid_reserve_token(headers['X-Idempotency-Token'])

        if context.user_agent:
            assert 'User-Agent' in headers
            assert headers['User-Agent'] == context.user_agent

        context.set_reserve_token(headers['X-Idempotency-Token'])

        return mockserver.make_response(
            json.dumps(context.response_body), context.response_code,
        )

    context.couponreserve = mock_couponreserve

    return context


def remove_offer_from_order(db, order_id):
    db.order_proc.update(
        {'_id': order_id},
        {'$unset': {'order.offer': '', 'order.request.offer': ''}},
    )


def init_order(db, order_id, coupon):
    if not coupon:
        return
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.coupon': {
                    'id': coupon,
                    # see default values in protocol/lib/src/models/order2.cpp
                    # in func
                    # ::mongo::BSONObj ToBsonCouponObj(const Request& request)
                    'valid': True,
                    'valid_any': False,
                    'was_used': False,
                },
            },
        },
    )


def init_offer(db, order_id, coupon):
    offer = db.order_proc.find_one(order_id)['order']['offer']
    to_set = {'coupon': {'code': coupon, 'value': 100}} if coupon else {}
    db.order_offers.update({'_id': offer}, {'$set': {'extra_data': to_set}})


def check_order_proc_current_prices(db, order_id):
    # in this test fixed price fore econom is disabled,
    # so we compare with calc
    order_proc = db.order_proc.find_one({'_id': order_id})
    calc = (
        order_proc.get('order')
        .get('calc')
        .get('allowed_tariffs')
        .get('__park__')
    )
    order_commit_common.check_current_prices(
        order_proc, 'prediction', calc['econom'],
    )


@pytest.mark.parametrize('offer_coupon', ['onlyoneusage', None])
@pytest.mark.config(MULTIORDER_LIMITS_ENABLED=True)
def test_coupon_was_applied_only_once(
        taxi_protocol, surge, couponreserve, db, offer_coupon,  # noqa: F811
):
    # use coupon first time: should be used successfully
    init_offer(db, 'id_pending', offer_coupon)
    init_order(db, 'id_pending', 'onlyoneusage')

    if not offer_coupon:
        remove_offer_from_order(db, 'id_pending')

    request = {'id': 'user_id', 'orderid': 'id_pending'}
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200, response.content

    order_proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert order_proc is not None

    coupon = order_proc['order']['coupon']
    assert coupon['was_used'] is True
    assert coupon['valid'] is True
    assert coupon['valid_any'] is False

    check_order_proc_current_prices(db, request['orderid'])

    # use coupon second time: should NOT be used
    init_offer(db, 'id_pending_double_reservation_check', offer_coupon)
    init_order(db, 'id_pending_double_reservation_check', 'onlyoneusage')

    if not offer_coupon:
        remove_offer_from_order(db, 'id_pending_double_reservation_check')

    request = {
        'id': 'user_id',
        'orderid': 'id_pending_double_reservation_check',
    }
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200, response.content

    order_proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert order_proc is not None

    coupon = order_proc['order']['coupon']
    assert coupon['was_used'] is False
    assert coupon['valid'] is False
    assert coupon['valid_any'] is False


@pytest.mark.parametrize(
    'coupons_code, coupons_response',
    [
        pytest.param(
            200,
            {
                'exists': True,
                'valid': True,
                'valid_any': True,
                'value': 100,
                'series': '_referral_',
            },
            id='coupons_ok_request',
        ),
        pytest.param(200, {}, id='coupons_incorrect_response'),
        pytest.param(400, {'message': 'errors'}, id='coupons_bad_request'),
        pytest.param(
            429, {'message': 'unavailable'}, id='coupons_service_unavailable',
        ),
        pytest.param(500, {}, id='coupons_internal_server_error'),
    ],
)
@pytest.mark.parametrize(
    'offer_with_coupon, order_with_coupon, order_with_offer, '
    'reserve_call_expected, ordercommit_expected_code',
    [
        pytest.param(True, True, True, True, 200, id='order_offer_match'),
        pytest.param(
            False, True, True, False, 200, id='mismatch_no_coupon_in_offer',
        ),
        pytest.param(
            True, False, True, False, 406, id='mismatch_no_coupon_in_order',
        ),
        pytest.param(
            False, False, True, False, 200, id='order_offer_no_coupon',
        ),
        pytest.param(False, False, False, False, 200, id='no_offer_no_coupon'),
        pytest.param(
            False, True, False, True, 200, id='no_offer_order_with_coupon',
        ),
    ],
)
def test_couponreserve_order_offer_coupon(
        taxi_protocol,
        db,
        mock_coupons,
        coupons_code,
        coupons_response,
        offer_with_coupon,
        order_with_coupon,
        order_with_offer,
        reserve_call_expected,
        ordercommit_expected_code,
):
    order_id = 'id_pending'
    user_agent = 'ru.yandextaxi.android'

    mock_coupons.set_user_agent(user_agent)
    mock_coupons.set_response_code(coupons_code)
    mock_coupons.set_response_body(coupons_response)

    # patch db fixtures
    init_offer(db, order_id, 'onlyoneusage' if offer_with_coupon else None)
    init_order(db, order_id, 'onlyoneusage' if order_with_coupon else None)

    if not order_with_offer:
        remove_offer_from_order(db, order_id)

    response = taxi_protocol.post(
        '3.0/ordercommit',
        {'id': 'user_id', 'orderid': order_id},
        headers={'User-Agent': user_agent},
    )

    protocol_expected_code = ordercommit_expected_code
    # This corresponds to the case when there is a valid coupon in order and
    # offer but reserve request failed. In that situation we need to throw
    # PRICE_CHANGED error in order to inform a user that coupon has not been
    # reserved and another attempt to create order should be made.
    if (
            order_with_offer
            and reserve_call_expected
            and (coupons_code != 200 or coupons_response == {})
    ):
        protocol_expected_code = 406

    assert response.status_code == protocol_expected_code

    if reserve_call_expected:
        assert mock_coupons.couponreserve.times_called > 0
    else:
        assert mock_coupons.couponreserve.times_called == 0


@pytest.mark.parametrize(
    'order_coupon, offer_coupon, result_coupon, service_code, commit_code',
    [
        pytest.param(
            'promocode', None, 'promocode', 500, 200, id='coupon_from_order',
        ),
        pytest.param(
            'promocode',
            'promocode',
            'promocode',
            500,
            406,
            id='coupon_from_order_and_offer',
        ),
        pytest.param(
            'promocode',
            'coupon',
            None,
            None,
            406,
            id='order_offer_coupon_mismatch',
        ),
        pytest.param(
            None, 'promocode', None, None, 406, id='coupon_in_offer_only',
        ),
        pytest.param(None, None, None, None, 200, id='no_coupon'),
    ],
)
def test_couponreserve_server_error(
        taxi_protocol,
        mockserver,
        mock_stq_agent,
        db,
        order_coupon,
        offer_coupon,
        result_coupon,
        service_code,
        commit_code,
):
    order_id = 'id_pending'
    reserve_token = {'value': None}

    @mockserver.handler('/coupons/v1/couponreserve')
    def mock_couponreserve(request):
        content = json.loads(request.get_data())
        headers = dict(request.headers)

        assert content['code'] == result_coupon
        assert content['order_id'] == order_id
        check_type = 'short' if offer_coupon else 'full'
        assert content['check_type'] == check_type

        assert 'X-Idempotency-Token' in headers
        reserve_token['value'] = headers['X-Idempotency-Token']

        return mockserver.make_response('', service_code)

    init_offer(db, order_id, offer_coupon)
    init_order(db, order_id, order_coupon)

    if not offer_coupon:
        remove_offer_from_order(db, order_id)

    response = taxi_protocol.post(
        '3.0/ordercommit', {'id': 'user_id', 'orderid': order_id},
    )
    assert response.status_code == commit_code

    if result_coupon is not None:
        assert mock_couponreserve.times_called > 0
    else:
        assert mock_couponreserve.times_called == 0

    if order_coupon is not None:
        tasks = mock_stq_agent.get_tasks('finish_coupon')
        assert tasks

        for task in tasks:
            task.kwargs.pop('log_extra')

            assert task.id == order_id + '_' + (
                reserve_token['value'] or 'NULL'
            )

            expected_args = {
                'order_id': order_id,
                'phone_id': '5714f45e98956f06baaae3d4',
                'yandex_uid': '4003514353',
                'device_id': 'E4249906-EA48-4269-A8D1-D230572845ED',
                'card_id': 'card-x8372',
                'application': 'iphone',
                'coupon': {'id': order_coupon, 'used': False},
            }
            if reserve_token['value'] is not None:
                expected_args['token'] = reserve_token['value']
            assert task.kwargs == expected_args

    if commit_code == 200 and (
            order_coupon is not None and offer_coupon is not None
    ):
        pricing_data = db.order_proc.find_one(order_id)['order'][
            'pricing_data'
        ]
        assert 'data' in pricing_data['user']
        assert 'coupon' not in pricing_data['user']['data']
        assert 'data' in pricing_data['driver']
        assert 'coupon' not in pricing_data['driver']['data']


def test_reserve_via_coupons_success(taxi_protocol, mock_coupons, db):
    # use coupon first time: should be used successfully
    init_order(db, 'id_pending', 'onlyoneusage')
    init_offer(db, 'id_pending', 'onlyoneusage')

    request = {'id': 'user_id', 'orderid': 'id_pending'}
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200, response.content

    def check_coupon(coupon):
        assert coupon.get('was_used') is True
        assert coupon['valid'] is True
        assert coupon['valid_any'] is False

        assert 'reserve_token' in coupon
        assert is_valid_reserve_token(coupon['reserve_token'])
        assert coupon['reserve_token'] == mock_coupons.reserve_token

    order_proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert order_proc is not None

    check_coupon(order_proc['order']['coupon'])

    check_order_proc_current_prices(db, request['orderid'])


@pytest.mark.config(COMMIT_PLUGINS_ENABLED=True)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='order_maker_plugin_overdraft',
    consumers=['client_protocol/commit_handling'],
    clauses=[
        {
            'title': '',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_commit_error_after_successful_reserve(
        taxi_protocol, mockserver, mock_stq_agent, mock_coupons, db,
):
    order_id = 'id_pending'
    coupon = 'promocode'

    init_offer(db, order_id, coupon)
    init_order(db, order_id, coupon)

    # set debt in order to fail ordercommit after couponreserve
    @mockserver.json_handler('/debts/v1/overdraft/limit')
    def mock_debts(request):
        return {'remaining_limit': 0, 'currency': 'RUB', 'has_debts': True}

    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.request.accepted': ['overdraft']}},
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', {'id': 'user_id', 'orderid': order_id},
    )
    assert response.status_code == 406

    assert mock_coupons.couponreserve.times_called == 1
    assert mock_debts.times_called == 1

    tasks = mock_stq_agent.get_tasks('finish_coupon')
    assert tasks

    for task in tasks:
        task.kwargs.pop('log_extra')

        assert task.id == order_id + '_' + mock_coupons.reserve_token

        assert task.kwargs == {
            'order_id': order_id,
            'phone_id': '5714f45e98956f06baaae3d4',
            'yandex_uid': '4003514353',
            'device_id': 'E4249906-EA48-4269-A8D1-D230572845ED',
            'card_id': 'card-x8372',
            'application': 'iphone',
            'coupon': {'id': coupon, 'used': False},
            'token': mock_coupons.reserve_token,
        }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='maas_series_pricing_settings',
    consumers=['protocol/ordercommit'],
    clauses=[
        {'title': '', 'value': {'maasx5': {}}, 'predicate': {'type': 'true'}},
    ],
)
def test_maas_coupon_success(taxi_protocol, mock_coupons, db):
    init_offer(db, 'id_pending', 'maasx5_123')
    init_order(db, 'id_pending', 'maasx5_123')

    mock_coupons.response_body['series'] = 'maasx5'

    request = {'id': 'user_id', 'orderid': 'id_pending'}
    response = taxi_protocol.post('3.0/ordercommit', request)

    assert mock_coupons.couponreserve.times_called == 1

    assert response.status_code == 200, response.content


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='maas_series_pricing_settings',
    consumers=['protocol/ordercommit'],
    clauses=[
        {'title': '', 'value': {'maasx5': {}}, 'predicate': {'type': 'true'}},
    ],
)
@pytest.mark.translations(
    client_messages={
        'common_errors.MAAS_FLOW_FAILED': {
            'ru': 'Заказ по абонементу не удалось создать',
        },
    },
)
def test_maas_coupon_reserve_failed(taxi_protocol, mock_coupons, db):
    init_offer(db, 'id_pending', 'maasx5_123')
    init_order(db, 'id_pending', 'maasx5_123')

    mock_coupons.response_body['valid'] = False
    mock_coupons.response_body['series'] = 'maasx5'

    request = {'id': 'user_id', 'orderid': 'id_pending'}
    response = taxi_protocol.post('3.0/ordercommit', request)

    assert mock_coupons.couponreserve.times_called == 1

    assert response.status_code == 406, response.content
    assert response.json() == {
        'error': {
            'code': 'MAAS_FLOW_FAILED',
            'text': 'Заказ по абонементу не удалось создать',
        },
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='maas_series_pricing_settings',
    consumers=['protocol/ordercommit'],
    clauses=[
        {'title': '', 'value': {'maasx5': {}}, 'predicate': {'type': 'true'}},
    ],
)
@pytest.mark.translations(
    client_messages={
        'common_errors.MAAS_FLOW_FAILED': {
            'ru': 'Заказ по абонементу не удалось создать',
        },
    },
)
@pytest.mark.parametrize(
    'pricing_coupon_value, expected_status_code',
    [
        pytest.param(100, 200, id='ok'),
        pytest.param(0, 406, id='coupon_was_not_applied_1'),
        pytest.param(None, 406, id='coupon_was_not_applied_2'),
    ],
)
def test_maas_coupon_with_pricing(
        taxi_protocol,
        mock_coupons,
        db,
        mockserver,
        load_json,
        pricing_coupon_value,
        expected_status_code,
):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        resp = load_json('pdp_v2_prepare_response.json')

        if pricing_coupon_value is not None:
            resp['categories']['econom']['user']['meta'][
                'coupon_value'
            ] = pricing_coupon_value

        return resp

    init_order(db, 'id_pending', 'maasx5_123')
    remove_offer_from_order(db, 'id_pending')
    db.order_offers.remove({'_id': 'offer_id'})

    mock_coupons.response_body['series'] = 'maasx5'

    request = {'id': 'user_id', 'orderid': 'id_pending'}
    response = taxi_protocol.post('3.0/ordercommit', request)

    assert mock_coupons.couponreserve.times_called == 1
    assert _mock_v2_prepare.times_called == 1

    assert response.status_code == expected_status_code, response.content

    if expected_status_code == 406:
        assert response.json() == {
            'error': {
                'code': 'MAAS_FLOW_FAILED',
                'text': 'Заказ по абонементу не удалось создать',
            },
        }
