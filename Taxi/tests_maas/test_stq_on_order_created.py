import typing

import pytest


class MyTestCase(typing.NamedTuple):
    sub_id: str = 'sub_id_1'
    coupon_id: str = 'coupon_id_1'
    reschedule_task: bool = False


def _assert_order_info(order, order_id, maas_user_id, sub):
    assert order.order_id == order_id
    assert order.external_order_id
    assert order.maas_user_id == maas_user_id
    assert order.phone_id == sub.phone_id
    assert order.maas_sub_id == sub.sub_id
    assert order.created_at
    assert order.updated_at


def _assert_order_info_is_updated(order, same_order):
    assert same_order.order_id == order.order_id
    assert same_order.external_order_id == order.external_order_id
    assert same_order.maas_user_id == order.maas_user_id
    assert same_order.phone_id == order.phone_id
    assert same_order.maas_sub_id == order.maas_sub_id
    assert same_order.is_maas_order == order.is_maas_order
    assert same_order.created_at == order.created_at
    assert same_order.updated_at != order.updated_at


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(sub_id='not_exist', coupon_id='not_exist'),
            id='subscription_not_found_error',
        ),
        pytest.param(MyTestCase(), id='save_order'),
        pytest.param(MyTestCase(reschedule_task=True), id='task_reschedule'),
    ],
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_stq_on_order_created(
        mockserver, stq_runner, get_subscription_by_id, get_order_by_id, case,
):
    phone_id = '612ca45973872fb3b5b9b40e'
    order_id = 'order_id_1'
    maas_user_id = 'user_id1'

    sub = get_subscription_by_id(case.sub_id)

    @mockserver.json_handler('/vtb-maas/api/0.1/trip/start')
    def _trip_start(_):
        return mockserver.make_response(json={})

    @mockserver.json_handler('/vtb-maas/api/0.1/trip/done')
    def _trip_end(_):
        return mockserver.make_response(json={})

    stq_kwargs = {
        'coupon_id': case.coupon_id,
        'order_id': order_id,
        'phone_id': phone_id,
        'point_a': [32.15101, 51.12101],
        'point_b': [32.15102, 51.12103],
    }

    if sub is None:
        await stq_runner.maas_on_order_created.call(
            task_id=order_id, kwargs=stq_kwargs, expect_fail=True,
        )
        return

    await stq_runner.maas_on_order_created.call(
        task_id=order_id, kwargs=stq_kwargs,
    )

    order = get_order_by_id(order_id)
    _assert_order_info(order, order_id, maas_user_id, sub)

    if case.reschedule_task:
        # run stq task again to emulate rescheduling
        await stq_runner.maas_on_order_created.call(
            task_id=order_id, kwargs=stq_kwargs,
        )
        # make sure order info remains unchanged thru 2nd run
        same_order_saved = get_order_by_id(order_id)
        _assert_order_info_is_updated(order, same_order_saved)

    assert not _trip_start.has_calls
    assert not _trip_end.has_calls
    assert not order.maas_trip_id
    assert order.updated_at == order.created_at
