import pytest

from protocol.order_test_utils import couponreserve  # noqa: F401


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


def init_coupon(db, order_id, coupon_id):
    """
    Set values of 'coupon' field, if coupon will be valid
    """

    if coupon_id:
        db.order_proc.update(
            {'_id': order_id},
            {
                '$set': {
                    'order.coupon': {
                        'id': coupon_id,
                        # see default values in
                        # protocol/lib/src/models/order2.cpp
                        # in func
                        # ::mongo::BSONObj
                        # ToBsonCouponObj(const Request& request)
                        'valid': True,
                        'valid_any': False,
                        'was_used': False,
                    },
                },
            },
        )


@pytest.mark.parametrize(
    'coupon_id, coupon_expected',
    [
        # no coupon field in order
        (None, {}),
        (
            'onlyoneusage123',
            {
                'id': 'onlyoneusage123',
                'series': 'onlyoneusage',
                'was_used': True,
                'valid': True,
                'valid_any': False,
                'value': 200,
            },
        ),
    ],
)
@pytest.mark.parametrize('url', ('3.0/ordercommit', 'internal/ordercommit'))
def test_reserve_coupon(
        taxi_protocol,
        surge,
        couponreserve,  # noqa: F811
        db,
        url,
        coupon_id,
        coupon_expected,
):
    """
    Check coupon using:
    1) no coupon field in order
    2) 'coupon' field in order
    """

    init_coupon(db, 'id_pending', coupon_id)

    request = {'id': 'user_id', 'orderid': 'id_pending'}
    response = taxi_protocol.post(url, request)
    assert response.status_code == 200, response.content

    proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert proc is not None

    order_coupon = proc['order'].get('coupon')
    assert order_coupon is not None

    if coupon_expected != {}:
        assert 'reserve_token' in order_coupon
        # token is randomly generated, we can't compare the exact value
        order_coupon.pop('reserve_token')

    assert order_coupon == coupon_expected


@pytest.mark.filldb(promocode_usages2='rollback')
@pytest.mark.parametrize(
    'url, response_code',
    [('3.0/ordercommit', 406), ('internal/ordercommit', 200)],
)
def test_release_coupon(taxi_protocol, mock_stq_agent, url, response_code):
    """
    order status is rollback,
    so should be rollbacked via STQ finish_coupon
    """
    order_id = 'id_rollback'
    request = {'id': 'user_id', 'orderid': order_id}
    response = taxi_protocol.post(url, request)
    assert response.status_code == response_code, response.content

    tasks = mock_stq_agent.get_tasks('finish_coupon')
    assert tasks

    for task in tasks:
        task.kwargs.pop('log_extra')

        assert task.kwargs == {
            'order_id': order_id,
            'phone_id': '5714f45e98956f06baaae3d4',
            'yandex_uid': '',
            'device_id': 'E4249906-EA48-4269-A8D1-D230572845ED',
            'application': 'iphone',
            'coupon': {'id': 'promocode321', 'used': False},
        }
