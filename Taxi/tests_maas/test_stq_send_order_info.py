import typing

import pytest


class MyTestCase(typing.NamedTuple):
    sub_id: str = 'sub_id_1'
    coupon_id: str = 'coupon_id_1'
    coupon_was_used: bool = True
    reschedule_task: bool = False


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(
                sub_id='not_exist',
                coupon_id='not_exist',
                coupon_was_used=False,
            ),
            id='subscription_not_found_error',
        ),
        pytest.param(
            MyTestCase(coupon_was_used=False),
            id='do_not_send_order_info_to_vtb_maas',
        ),
        pytest.param(MyTestCase(), id='send_order_info_to_vtb_maas'),
        pytest.param(
            MyTestCase(reschedule_task=True),
            id='send_order_info_to_vtb_maas_with_task_reschedule',
        ),
    ],
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_stq_send_order_info(
        mockserver, stq_runner, get_subscription_by_id, get_order_by_id, case,
):
    phone_id = '612ca45973872fb3b5b9b40e'
    order_id = 'order_id_1'
    order_start = '2021-08-18T12:00:27.87+00:00'
    order_end = '2021-08-18T12:30:27.87+00:00'
    maas_user_id = 'user_id1'
    maas_trip_id = 'maas_trip_id_1'

    sub = get_subscription_by_id(case.sub_id)

    def _assert_trip_details(trip):
        assert trip['service_trip_id']
        assert trip['terminal_id']
        assert trip['count'] == 1
        assert trip['status'] == 'DONE'
        time = trip['time']
        assert time['start'] == order_start
        assert time['end'] == order_end

    def _assert_order_info(order):
        assert order.order_id == order_id
        assert order.external_order_id
        assert order.maas_user_id == maas_user_id
        assert order.phone_id == sub.phone_id
        assert order.maas_sub_id == sub.sub_id
        assert order.is_maas_order == case.coupon_was_used
        assert order.created_at
        assert order.updated_at

    def _assert_order_info_is_the_same(order, same_order):
        assert same_order.order_id == order.order_id
        assert same_order.external_order_id == order.external_order_id
        assert same_order.maas_user_id == order.maas_user_id
        assert same_order.phone_id == order.phone_id
        assert same_order.maas_sub_id == order.maas_sub_id
        assert same_order.is_maas_order == order.is_maas_order
        assert same_order.created_at == order.created_at
        if case.coupon_was_used:
            assert same_order.updated_at != order.updated_at
        else:
            assert same_order.updated_at == order.updated_at

    @mockserver.json_handler('/vtb-maas/api/0.1/trip/start')
    def _trip_start(request):
        assert request.json['maas_user_id'] == maas_user_id
        assert request.json['maas_sub_id'] == case.sub_id
        _assert_trip_details(request.json['trip'])
        return mockserver.make_response(json={'maas_trip_id': maas_trip_id})

    @mockserver.json_handler('/vtb-maas/api/0.1/trip/done')
    def _trip_end(request):
        assert request.json['maas_trip_id'] == maas_trip_id
        _assert_trip_details(request.json['trip'])
        return mockserver.make_response(json={})

    stq_kwargs = {
        'coupon_id': case.coupon_id,
        'coupon_was_used': case.coupon_was_used,
        'order_id': order_id,
        'phone_id': phone_id,
        'order_start': order_start,
        'order_end': order_end,
    }

    if sub is None:
        await stq_runner.maas_send_order_info.call(
            task_id=order_id, kwargs=stq_kwargs, expect_fail=True,
        )
        return

    await stq_runner.maas_send_order_info.call(
        task_id=order_id, kwargs=stq_kwargs,
    )

    order = get_order_by_id(order_id)
    _assert_order_info(order)

    if case.reschedule_task:
        # run stq task again to emulate rescheduling
        await stq_runner.maas_send_order_info.call(
            task_id=order_id, kwargs=stq_kwargs,
        )
        # make sure order info remains unchanged thru 2nd run
        same_order = get_order_by_id(order_id)
        _assert_order_info_is_the_same(order, same_order)

    if case.coupon_was_used:
        assert _trip_start.has_calls
        assert _trip_end.has_calls
        assert order.maas_trip_id == maas_trip_id
        assert order.updated_at != order.created_at
    else:
        assert not _trip_start.has_calls
        assert not _trip_end.has_calls
        assert not order.maas_trip_id
        assert order.updated_at == order.created_at
