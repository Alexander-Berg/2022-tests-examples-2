from aiohttp import web
import bson
import pytest

from taxi.stq import async_worker_ng

from taxi_coupons_py3.generated.stq3 import stq_context
from taxi_coupons_py3.stq import coupon_finish


ORDER_ID = 'abc1234567890'
YANDEX_UID = 'user123'
USER_PHONE_ID = bson.ObjectId('a9f6d99ea51f42b6b1bb8161')
COUPON_ID = 'promocode'
COST_USAGE = '100.00'


def canonize_order_proc(order_proc, coupon_was_used=False, coupon_valid=False):
    if order_proc is None:
        return None

    order_proc.setdefault('order', {}).setdefault('coupon', {})

    order_proc['_id'] = ORDER_ID
    order_proc['order'].setdefault('application', 'yango_iphone')
    order_proc['order']['user_uid'] = YANDEX_UID
    order_proc['order']['user_phone_id'] = USER_PHONE_ID
    order_proc['order']['coupon']['id'] = COUPON_ID
    order_proc['order']['coupon']['was_used'] = coupon_was_used

    if coupon_valid:
        order_proc['order']['coupon']['valid'] = True

    for attr in ('status', 'taxi_status'):
        if attr not in order_proc['order']:
            order_proc['order'][attr] = None

    return order_proc


def create_task_info(exec_tries=0, reschedule_counter=0):
    return async_worker_ng.TaskInfo(
        id=ORDER_ID,
        exec_tries=exec_tries,
        reschedule_counter=reschedule_counter,
        queue='',
    )


@pytest.mark.parametrize(
    'order_proc, coupon_was_used',
    [
        pytest.param(None, False, id='invalid_order_id'),
        pytest.param(
            {'order': {'coupon': {'valid': False}}}, True, id='invalid_coupon',
        ),
        pytest.param(
            {
                'order': {
                    'coupon': {'valid': True},
                    'status_change_positions': [
                        {'taxi_status': 'transporting'},
                    ],
                },
            },
            False,
            id='order_was_on_taxi_status_transporting',
        ),
    ],
)
async def test_task_without_coupon_finish_request(
        stq3_context: stq_context.Context,
        order_proc,
        coupon_was_used,
        order_archive_mock,
        mock_coupons,
):
    order_proc = canonize_order_proc(order_proc, coupon_was_used)

    if order_proc is not None:
        order_archive_mock.set_order_proc(order_proc)

    @mock_coupons('/internal/coupon_finish')
    async def _coupon_finish(request, **kwargs):
        return web.Response()

    await coupon_finish.task(
        stq3_context, create_task_info(), ORDER_ID, success=coupon_was_used,
    )

    assert _coupon_finish.has_calls is False


@pytest.mark.parametrize(
    'order_proc, coupon_was_used, coupon_finish_params',
    [
        pytest.param(
            {
                'order': {
                    'status': 'finished',
                    'taxi_status': 'expired',
                    'application': 'yango_android',
                },
            },
            True,
            {'success': False, 'application_name': 'yango_android'},
            id='order_does_not_have_performer',
        ),
        pytest.param(
            {
                'order': {
                    'status': 'finished',
                    'taxi_status': 'expired',
                    'performer': {'clid': 'park123'},
                    'application': 'yango_iphone',
                },
            },
            True,
            {'success': False, 'application_name': 'yango_iphone'},
            id='order_has_performer_from_taxi_park',
        ),
        pytest.param(
            {
                'order': {
                    'status': 'finished',
                    'taxi_status': 'expired',
                    'performer': {'car': 'Kia Rio'},
                },
            },
            True,
            {'success': True},
            id='order_has_performer_without_taxi_park',
        ),
        pytest.param(
            {'order': {'status': 'finished'}},
            True,
            {'success': True},
            id='success_coupon_usage',
        ),
        pytest.param(
            {
                'order': {
                    'status_change_positions': [],
                    'application': 'uber_android',
                },
            },
            False,
            {'success': False, 'application_name': 'uber_android'},
            id='unsuccess_coupon_usage',
        ),
    ],
)
async def test_task_with_coupon_finish_request(
        stq3_context: stq_context.Context,
        order_archive_mock,
        order_proc,
        coupon_was_used,
        coupon_finish_params,
        patch,
        mock_coupons,
):
    order_proc = canonize_order_proc(
        order_proc, coupon_was_used, coupon_valid=True,
    )

    order_archive_mock.set_order_proc(order_proc)

    @mock_coupons('/internal/coupon_finish')
    async def _coupon_finish(request, **kwargs):
        body = request.json
        assert body['yandex_uid'] == YANDEX_UID
        assert body['phone_id'] == str(USER_PHONE_ID)
        assert body['order_id'] == ORDER_ID
        assert body['coupon_id'] == COUPON_ID
        assert body['success'] == coupon_finish_params['success']
        assert body.get('application_name') == coupon_finish_params.get(
            'application_name',
        )
        if 'cost_usage' in body:
            assert body['cost_usage'] == str(COST_USAGE)
        return web.json_response({})

    @patch('taxi_coupons_py3.stq.coupon_finish.calculate_cost_usage')
    def _calculate_cost_usage(order):
        return COST_USAGE

    await coupon_finish.task(
        stq3_context, create_task_info(), ORDER_ID, success=coupon_was_used,
    )

    assert _coupon_finish.has_calls is True


@pytest.mark.now('2019-12-01T00:00:00')
async def test_task_with_inconsistent_order_proc_state(
        stq3_context: stq_context.Context, order_archive_mock, mock_coupons,
):
    order_archive_mock.set_order_proc(
        canonize_order_proc(
            {'order': {'status': 'pending', 'status_change_positions': []}},
            coupon_valid=True,
        ),
    )

    @mock_coupons('/internal/coupon_finish')
    async def _coupon_finish(request, **kwargs):
        body = request.json
        assert body['success'] is False
        return web.json_response({})

    max_exec_tries = stq3_context.config.TASK_COUPON_FINISH_MAX_EXEC_TRIES

    for exec_tries in range(max_exec_tries):
        with pytest.raises(Exception):
            await coupon_finish.task(
                stq3_context,
                create_task_info(exec_tries=exec_tries),
                ORDER_ID,
                True,
            )

    await coupon_finish.task(
        stq3_context,
        create_task_info(exec_tries=max_exec_tries),
        ORDER_ID,
        True,
    )
    assert _coupon_finish.times_called == 1


@pytest.mark.parametrize(
    'final_cost_meta, is_new_flow, new_cost_usage',
    [
        (None, False, None),
        ({}, False, None),
        ({'user': {}}, False, None),
        ({'user': {'use_cost_includes_coupon': 0}}, False, None),
        ({'user': {'use_cost_includes_coupon': 10}}, False, None),
        ({'user': {'use_cost_includes_coupon': 1}}, False, None),
        ({'user': {'use_cost_includes_coupon': 1.0}}, False, None),
        (
            {'user': {'use_cost_includes_coupon': 1.0, 'coupon_value': None}},
            False,
            None,
        ),
        (
            {'user': {'use_cost_includes_coupon': 1.0, 'coupon_value': 123}},
            True,
            123,
        ),
        (
            {'user': {'use_cost_includes_coupon': 1.0, 'coupon_value': 3.50}},
            True,
            3.50,
        ),
        ({'user': {'coupon_value': 3.50}}, False, None),
    ],
)
@pytest.mark.parametrize(
    'order, cost_usage',
    [
        pytest.param({}, 0, id='empty_data'),
        pytest.param(
            {'cost': 70, 'coupon': {'value': 110}}, 70, id='use_order_cost',
        ),
        pytest.param(
            {'cost': 130, 'coupon': {'value': 80}}, 80, id='use_coupon_value',
        ),
        pytest.param(
            {'cost': 130, 'coupon': {'value': 80, 'percent': 50}},
            65,
            id='use_percent',
        ),
        pytest.param(
            {'cost': 130, 'coupon': {'value': 80, 'percent': 50, 'limit': 45}},
            45,
            id='use_percent_limit',
        ),
        pytest.param({'cost': None}, 0, id='empty_cost'),
        pytest.param(
            {'cost': 100, 'coupon': {'value': None}},
            0,
            id='empty_coupon_value',
        ),
        pytest.param(
            {'cost': 100, 'coupon': {'value': 70, 'percent': None}},
            70,
            id='empty_coupon_percent',
        ),
        pytest.param(
            {
                'cost': 120,
                'coupon': {'value': 70, 'percent': 50, 'limit': None},
            },
            60,
            id='empty_coupon_limit',
        ),
    ],
)
def test_calculate_cost_usage(
        order, cost_usage, final_cost_meta, is_new_flow, new_cost_usage,
):
    order['current_prices'] = {'final_cost_meta': final_cost_meta}
    assert coupon_finish.calculate_cost_usage(order) == (
        new_cost_usage if is_new_flow else cost_usage
    )


def test_coupon_value_from_pricing_is_zero():
    order = {
        'current_prices': {
            'final_cost_meta': {
                'user': {'use_cost_includes_coupon': 1.0, 'coupon_value': 0.0},
            },
        },
        'cost': 70,
        'coupon': {'value': 110},
    }

    with pytest.raises(coupon_finish.CouponCostUsageFromPricingIsZero):
        coupon_finish.calculate_cost_usage(order)
