import datetime

import bson
import pytest


def assert_req_is_correct(req):
    assert req.query['order_id'] == 'basic-order'
    assert 'due' not in req.query


@pytest.fixture(name='mock_cancel')
def _mock_cancel(mockserver, mongodb):
    @mockserver.handler('/order-core/internal/processing/v1/event/cancel')
    def mock_cancel(req):
        assert_req_is_correct(req)
        assert req.query['order_id'] == 'basic-order'

        body = bson.BSON(req.get_data()).decode()
        update_obj = {}
        if 'extra_update' in body.keys() and body['extra_update'] is not None:
            update_obj = body['extra_update']
        if '$set' not in update_obj.keys():
            update_obj['$set'] = {}
        update_obj['$set']['order.version'] = 1
        update_obj['$set']['processing'] = {'version': 1, 'need_start': True}
        update_obj['$set']['order_info.need_sync'] = True
        update_obj['$set']['order_info.statistics.status_updates'] = [
            {
                'a': body['event_arg'],
                'h': True,
                'c': datetime.datetime(2019, 10, 21, 17, 15),
                'x-idempotency-token': req.headers['X-Idempotency-Token'],
            },
        ]
        for key, value in body['event_extra_payload'].items():
            update_obj['$set']['order_info.statistics.status_updates'][0][
                key
            ] = value
        update_obj['$set']['order_info.statistics.status_updates'][0][
            's'
        ] = 'cancelled'
        request_filter = {'_id': req.query['order_id']}
        if 'filter' in body.keys() and body['filter'] is not None:
            request_filter = body['filter']
        mongodb.order_proc.update(request_filter, update_obj)

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({}),
        )

    return mock_cancel


@pytest.mark.parametrize('only_unassigned', [True, False])
@pytest.mark.parametrize(
    'order_status, order_taxi_status, allow_unassigned',
    [
        ('pending', None, True),
        ('cancelled', 'transporting', True),
        ('cancelled', 'driving', True),
        ('assigned', None, False),
        ('assigned', 'driving', False),
        ('assigned', 'waiting', False),
    ],
)
async def test_order_cancel_statuses(
        taxi_order_core,
        mongodb,
        only_unassigned,
        order_status,
        order_taxi_status,
        allow_unassigned,
        stq,
        now,
        mock_cancel,
):
    assert (
        mongodb.order_proc.update(
            {'_id': 'basic-order'},
            {
                '$set': {
                    'order.status': order_status,
                    'order.taxi_status': order_taxi_status,
                },
            },
        )['nModified']
        == 1
    )

    params = {'orderid': 'basic-order-reorder-id', 'userid': 'user'}
    if only_unassigned:
        params['only_unassigned'] = True

    if only_unassigned and not allow_unassigned:
        expected_status = order_status
        expected_code = 400
        expect_cancel_order = False
    else:
        expected_status = 'cancelled'
        expected_code = 200
        expect_cancel_order = True

    with stq.flushing():
        assert stq.is_empty
        result = await taxi_order_core.post(
            '/v1/tc/order-cancel', params=params,
        )
        assert result.status_code == expected_code
        new_proc = mongodb.order_proc.find_one({'_id': 'basic-order'})
        assert new_proc['order']['status'] == expected_status

        if expect_cancel_order:
            assert mock_cancel.times_called == 1
        assert stq.is_empty


@pytest.mark.parametrize('order_id', ['basic-order', 'basic-order-reorder-id'])
@pytest.mark.parametrize('order_status', ['pending', 'cancelled'])
@pytest.mark.parametrize('coupon_was_used', [True, False, None])
async def test_ensure_idempotency(
        taxi_order_core,
        mongodb,
        stq,
        order_id,
        order_status,
        coupon_was_used,
        mock_cancel,
):
    update = {'$set': {'order.status': order_status}}
    if order_status == 'cancelled':
        update['$push'] = {
            'order_info.statistics.status_updates': {'s': 'cancelled'},
        }
    if coupon_was_used is not None:
        update['$set']['order.coupon.was_used'] = coupon_was_used
    mongodb.order_proc.update({'_id': 'basic-order'}, update)

    params = {'orderid': order_id, 'userid': 'user'}
    with stq.flushing():
        assert stq.is_empty

        for _ in range(3):
            result = await taxi_order_core.post(
                '/v1/tc/order-cancel', params=params,
            )
            assert result.status_code == 200

        proc = mongodb.order_proc.find_one({'_id': 'basic-order'})
        status_updates_statuses = [
            i['s'] for i in proc['order_info']['statistics']['status_updates']
        ]
        assert status_updates_statuses == ['cancelled']  # exactly one
        if coupon_was_used is not None:
            assert not proc['order']['coupon']['was_used']
        else:
            assert not proc['order']['coupon']
        assert mock_cancel.times_called == 3


@pytest.mark.now(datetime.datetime(2019, 10, 21, 17, 15).isoformat())
@pytest.mark.config(MAX_TRANSPORTING_TIME_TO_CANCEL=5 * 60)
@pytest.mark.parametrize('only_unassigned', [True, False])
@pytest.mark.parametrize(
    'transporting_status_ts, should_cancel',
    [
        # threshold is 5 minutes from now
        (datetime.datetime(2019, 10, 21, 17, 11), True),
        (datetime.datetime(2019, 10, 21, 17, 9), False),
    ],
)
async def test_order_cancel_in_transporting(
        taxi_order_core,
        mongodb,
        only_unassigned,
        stq,
        transporting_status_ts,
        should_cancel,
        mock_cancel,
):
    assert (
        mongodb.order_proc.update(
            {'_id': 'basic-order'},
            {
                '$set': {
                    'order.status': 'assigned',
                    'order.taxi_status': 'transporting',
                    'order.status_updated': transporting_status_ts,
                },
            },
        )['nModified']
        == 1
    )
    params = {'orderid': 'basic-order-reorder-id', 'userid': 'user'}
    if only_unassigned:
        params['only_unassigned'] = True

    if should_cancel and not only_unassigned:
        expected_code = 200
        expected_status = 'cancelled'
        expect_cancel = True
    else:
        expected_code = 400
        expected_status = 'assigned'
        expect_cancel = False

    with stq.flushing():
        assert stq.is_empty
        result = await taxi_order_core.post(
            '/v1/tc/order-cancel', params=params,
        )
        assert result.status_code == expected_code
        new_proc = mongodb.order_proc.find_one({'_id': 'basic-order'})
        assert new_proc['order']['status'] == expected_status

        if expect_cancel:
            assert mock_cancel.times_called == 1
        assert stq.is_empty


@pytest.mark.now(datetime.datetime(2019, 10, 21, 17, 15).isoformat())
@pytest.mark.parametrize('coupon_was_used', [True, False, None])
async def test_order_cancel_no_coupon_was_used(
        taxi_order_core, mongodb, coupon_was_used, mock_cancel,
):
    set_obj = {
        '$set': {
            'order.status': 'assigned',
            'order.taxi_status': 'transporting',
            'order.status_updated': datetime.datetime(2019, 10, 21, 17, 11),
        },
    }
    if coupon_was_used is not None:
        set_obj['$set']['order.coupon.was_used'] = coupon_was_used
    upd_result = mongodb.order_proc.update({'_id': 'basic-order'}, set_obj)
    assert upd_result['nModified'] == 1
    params = {
        'orderid': 'basic-order-reorder-id',
        'userid': 'user',
        'only_unassigned': False,
    }
    result = await taxi_order_core.post('/v1/tc/order-cancel', params=params)
    assert result.status_code == 200
    assert mock_cancel.times_called == 1
    new_proc = mongodb.order_proc.find_one({'_id': 'basic-order'})
    if coupon_was_used is not None:
        assert not new_proc['order']['coupon']['was_used']
    else:
        assert not new_proc['order']['coupon']


@pytest.mark.now(datetime.datetime(2019, 10, 21, 17, 15).isoformat())
async def test_order_cancel_basic(taxi_order_core, mongodb, mock_cancel):
    set_obj = {
        '$set': {
            'order.status': 'assigned',
            'order.taxi_status': 'transporting',
            'order.status_updated': datetime.datetime(2019, 10, 21, 17, 11),
        },
    }
    upd_result = mongodb.order_proc.update({'_id': 'basic-order'}, set_obj)
    assert upd_result['nModified'] == 1
    params = {
        'orderid': 'basic-order-reorder-id',
        'userid': 'user',
        'only_unassigned': False,
    }
    result = await taxi_order_core.post('/v1/tc/order-cancel', params=params)
    assert result.status_code == 200
    assert mock_cancel.times_called == 1
    new_proc = mongodb.order_proc.find_one({'_id': 'basic-order'})
    assert new_proc == {
        '_id': 'basic-order',
        '_shard_id': 0,
        'commit_state': 'done',
        'order': {
            'coupon': {},
            'status': 'cancelled',
            'status_updated': datetime.datetime(2019, 10, 21, 17, 15),
            'taxi_status': 'transporting',
            'user_id': 'user',
            'version': 1,
        },
        'order_info': {
            'need_sync': True,
            'statistics': {
                'status_updates': [
                    {
                        'a': {'cancelled_by': 'order-core'},
                        'c': datetime.datetime(2019, 10, 21, 17, 15),
                        'h': True,
                        's': 'cancelled',
                        'x-idempotency-token': 'cancel-order-from-protocol',
                    },
                ],
            },
        },
        'processing': {'need_start': True, 'version': 1},
        'reorder': {'id': 'basic-order-reorder-id'},
        'status': 'finished',
    }
