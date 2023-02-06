import datetime

import freezegun
import pytest
from sqlalchemy.exc import IntegrityError

from taxi.robowarehouse.lib.concepts import courier_order_stages
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@pytest.mark.asyncio
async def test_get_all_empty():
    result = await courier_order_stages.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_get_all():
    courier_order_stage1 = await courier_order_stages.factories.create()
    courier_order_stage2 = await courier_order_stages.factories.create()

    result = await courier_order_stages.get_all()

    assert_items_equal([r.to_dict() for r in result], [courier_order_stage1.to_dict(), courier_order_stage2.to_dict()])


@pytest.mark.asyncio
async def test_get_by_order_id_not_found_error():
    order_stage = await courier_order_stages.factories.create(effective_time=2)
    await courier_order_stages.factories.create()

    with pytest.raises(courier_order_stages.exceptions.CourierOrderStageNotFoundError):
        await courier_order_stages.get_by_order_id(
            order_id=order_stage.order_id,
            time=datetime_utils.timestamp_to_datetime(1),
        )


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_by_order_id_default_time():
    order_stage = await courier_order_stages.factories.create(effective_time=2)
    await courier_order_stages.factories.create()

    result = await courier_order_stages.get_by_order_id(order_id=order_stage.order_id)

    assert result.to_dict() == order_stage.to_dict()


@pytest.mark.parametrize('effective_times, time, expected_index', [
    ([], 1, None),
    ([2], 1, None),
    ([2], 2, 0),
    ([2], 3, 0),
    ([1, 2], 0, None),
    ([1, 2], 1, 0),
    ([1, 2], 2, 1),
    ([1, 2], 3, 1),
    ([4, 2, 1], 1, 2),
    ([4, 2, 1], 2, 1),
    ([4, 2, 1], 3, 1),
    ([4, 2, 1], 4, 0),
])
@pytest.mark.asyncio
async def test_get_by_order_id_specific_time(effective_times, time, expected_index):
    await courier_order_stages.factories.create()
    order = await orders.factories.create()

    order_stages = []
    for effective_time in effective_times:
        order_stages.append(await courier_order_stages.factories.create(
            order_id=order.order_id,
            effective_time=datetime_utils.timestamp_to_datetime(effective_time),
        ))

    result = await courier_order_stages.get_by_order_id(
        order_id=order.order_id,
        time=datetime_utils.timestamp_to_datetime(time),
        raise_not_found=False,
    )

    if expected_index is None:
        assert result is None
    else:
        assert result.to_dict() == order_stages[expected_index].to_dict()


@pytest.mark.asyncio
async def test_create():
    courier_order_stage1 = await courier_order_stages.factories.create()
    courier_order_stage2 = courier_order_stages.factories.build(order_id=courier_order_stage1.order_id)

    result = await courier_order_stages.create(
        courier_order_stages.CreateCourierOrderStageRequest.from_orm(courier_order_stage2))

    assert result.to_dict() == courier_order_stage2.to_dict()

    db_courier_order_stages = await courier_order_stages.get_all()
    assert_items_equal([m.to_dict() for m in db_courier_order_stages],
                       [courier_order_stage1.to_dict(), courier_order_stage2.to_dict()])


@pytest.mark.asyncio
async def test_create_no_order():
    order_id = generate_id()
    courier_order_stage1 = courier_order_stages.factories.build(order_id=order_id)

    with pytest.raises(IntegrityError) as e:
        await courier_order_stages.create(
            courier_order_stages.CreateCourierOrderStageRequest.from_orm(courier_order_stage1))

    assert f'Key (order_id)=({order_id}) is not present in table "orders".' in str(e.value)

    db_courier_order_stages = await courier_order_stages.get_all()
    assert db_courier_order_stages == []


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_not_found():
    delta_2m = datetime.timedelta(minutes=2)
    delta_30s = datetime.timedelta(seconds=30)
    now = datetime_utils.get_now()
    await courier_order_stages.factories.create(type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
                                                effective_time=now - delta_2m)
    await courier_order_stages.factories.create(type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
                                                effective_time=now - delta_30s)

    result = await courier_order_stages.get_courier_freeze(now=now)
    assert result == ({}, {})


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_first_open_only():
    delta_5m = datetime.timedelta(minutes=5)
    delta_4m = datetime.timedelta(minutes=4)

    now = datetime_utils.get_now()

    order = await orders.factories.create()
    order_stage = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_5m,
        order_id=order.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_4m,
        order_id=order.order_id
    )

    opened_freeze, taken_freeze = await courier_order_stages.get_courier_freeze(now=now)

    opened_freeze = {k: v.to_dict() for k, v in opened_freeze.items()}

    assert taken_freeze == {}
    assert opened_freeze == {order.order_id: order_stage.to_dict()}


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_first_few_opened():
    now = datetime_utils.get_now()

    delta_5m = datetime.timedelta(minutes=5)
    delta_4m = datetime.timedelta(minutes=4)

    order1 = await orders.factories.create()
    order2 = await orders.factories.create()

    order_stage1 = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_5m,
        order_id=order1.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_4m,
        order_id=order1.order_id,
    )

    order_stage2 = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_5m,
        order_id=order2.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_4m,
        order_id=order2.order_id,
    )

    opened_freeze, taken_freezed = await courier_order_stages.get_courier_freeze(now=now)

    expected = {stage.order_id: stage.to_dict() for stage in (order_stage1, order_stage2)}
    opened_freeze = {k: v.to_dict() for k, v in opened_freeze.items()}

    assert taken_freezed == {}
    assert opened_freeze == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_after_taken():
    now = datetime_utils.get_now()

    delta_5m = datetime.timedelta(minutes=5)
    delta_4m = datetime.timedelta(minutes=4)
    delta_2m = datetime.timedelta(minutes=2)

    order1 = await orders.factories.create()
    order2 = await orders.factories.create()

    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_5m,
        order_id=order1.order_id
    )
    order_stage1 = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_4m,
        order_id=order1.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_2m,
        order_id=order1.order_id
    )

    order_stage2 = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_5m,
        order_id=order2.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_2m,
        order_id=order2.order_id
    )

    opened_freeze, taken_freeze = await courier_order_stages.get_courier_freeze(now=now)

    opened_freeze = {k: v.to_dict() for k, v in opened_freeze.items()}
    taken_freeze = {k: v.to_dict() for k, v in taken_freeze.items()}

    expected_opened_freeze = {order2.order_id: order_stage2.to_dict()}
    expected_taken_freeze = {order1.order_id: order_stage1.to_dict()}

    assert opened_freeze == expected_opened_freeze
    assert taken_freeze == expected_taken_freeze


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_opened_and_close():
    now = datetime_utils.get_now()

    delta_5m = datetime.timedelta(minutes=5)
    delta_4m = datetime.timedelta(minutes=4)
    delta_2m = datetime.timedelta(minutes=2)

    order1 = await orders.factories.create()

    await courier_order_stages.factories.create(type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
                                                effective_time=now - delta_5m,
                                                order_id=order1.order_id)
    await courier_order_stages.factories.create(type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
                                                effective_time=now - delta_4m,
                                                order_id=order1.order_id)
    await courier_order_stages.factories.create(type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
                                                effective_time=now - delta_2m,
                                                order_id=order1.order_id)

    result = await courier_order_stages.get_courier_freeze(now=now)

    assert result == ({}, {})


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_first_taken():
    now = datetime_utils.get_now()

    delta_3m = datetime.timedelta(minutes=3)
    delta_2m = datetime.timedelta(minutes=2)

    order1 = await orders.factories.create()

    order_stage = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_3m,
        order_id=order1.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_2m,
        order_id=order1.order_id
    )

    opened_freeze, taken_freeze = await courier_order_stages.get_courier_freeze(now=now)
    taken_freeze = {k: v.to_dict() for k, v in taken_freeze.items()}

    expected_taken_freeze = {order1.order_id: order_stage.to_dict()}

    assert opened_freeze == {}
    assert taken_freeze == expected_taken_freeze


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_taken_after_opened():
    now = datetime_utils.get_now()

    delta_3m = datetime.timedelta(minutes=3)
    delta_30s = datetime.timedelta(seconds=30)

    order1 = await orders.factories.create()

    order_stage = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_3m,
        order_id=order1.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_30s,
        order_id=order1.order_id
    )

    opened_freeze, taken_freeze = await courier_order_stages.get_courier_freeze(now=now)
    taken_freeze = {k: v.to_dict() for k, v in taken_freeze.items()}

    expected_taken_freeze = {order1.order_id: order_stage.to_dict()}

    assert opened_freeze == {}
    assert taken_freeze == expected_taken_freeze


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_few_taken():
    now = datetime_utils.get_now()

    delta_3m = datetime.timedelta(minutes=3)
    delta_2m = datetime.timedelta(minutes=2)
    delta_30s = datetime.timedelta(seconds=30)

    order1 = await orders.factories.create()
    order2 = await orders.factories.create()
    order3 = await orders.factories.create()

    order_stage1 = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_3m,
        order_id=order1.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_30s,
        order_id=order1.order_id,
    )
    order_stage2 = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_3m,
        order_id=order2.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_2m,
        order_id=order2.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_30s,
        order_id=order2.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_30s,
        order_id=order3.order_id,
    )

    opened_freeze, taken_freeze = await courier_order_stages.get_courier_freeze(now=now)

    opened_freeze = {k: v.to_dict() for k, v in opened_freeze.items()}
    taken_freeze = {k: v.to_dict() for k, v in taken_freeze.items()}

    expected_opened_freeze = {}
    expected_taken_freeze = {order1.order_id: order_stage1.to_dict(), order2.order_id: order_stage2.to_dict()}

    assert opened_freeze == expected_opened_freeze
    assert taken_freeze == expected_taken_freeze


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_taken_and_close():
    now = datetime_utils.get_now()

    delta_3m = datetime.timedelta(minutes=3)
    delta_30s = datetime.timedelta(seconds=30)

    order1 = await orders.factories.create()

    await courier_order_stages.factories.create(type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
                                                effective_time=now - delta_3m,
                                                order_id=order1.order_id)
    await courier_order_stages.factories.create(type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
                                                effective_time=now - delta_30s,
                                                order_id=order1.order_id)

    result = await courier_order_stages.get_courier_freeze(now=now)

    assert result == ({}, {})


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_freeze_after_emergency_exit():
    now = datetime_utils.get_now()

    delta_6m = datetime.timedelta(minutes=6)
    delta_5m = datetime.timedelta(minutes=5)
    delta_4m = datetime.timedelta(minutes=4)
    delta_2m = datetime.timedelta(minutes=2)
    delta_30s = datetime.timedelta(seconds=30)

    order1 = await orders.factories.create()
    order2 = await orders.factories.create()
    order3 = await orders.factories.create()

    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_6m,
        order_id=order1.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.EXITED_EMERGENCY,
        effective_time=now - delta_5m,
        order_id=order1.order_id,
    )
    order_stage1 = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_4m,
        order_id=order1.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_6m,
        order_id=order2.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.EXITED_EMERGENCY,
        effective_time=now - delta_5m,
        order_id=order2.order_id,
    )
    order_stage2 = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_2m,
        order_id=order2.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.EXITED_EMERGENCY,
        effective_time=now - delta_2m,
        order_id=order3.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_30s,
        order_id=order3.order_id,
    )

    opened_freeze, taken_freeze = await courier_order_stages.get_courier_freeze(now=now)

    opened_freeze = {k: v.to_dict() for k, v in opened_freeze.items()}
    taken_freeze = {k: v.to_dict() for k, v in taken_freeze.items()}

    expected_opened_freeze = {order1.order_id: order_stage1.to_dict()}
    expected_taken_freeze = {order2.order_id: order_stage2.to_dict()}

    assert opened_freeze == expected_opened_freeze
    assert taken_freeze == expected_taken_freeze


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_stage_time():
    now = datetime_utils.get_now()

    delta_6m = datetime.timedelta(minutes=6)
    delta_5m = datetime.timedelta(minutes=5)
    delta_4m = datetime.timedelta(minutes=4)
    delta_2m = datetime.timedelta(minutes=2)
    delta_30s = datetime.timedelta(seconds=30)

    order = await orders.factories.create()

    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED
    )
    stage_open = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now-delta_6m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now-delta_5m,
        order_id=order.order_id,
    )
    stage_taken = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now-delta_4m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now-delta_2m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now-delta_30s,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
        effective_time=now,
        order_id=order.order_id,
    )

    open_time, taken_time = await courier_order_stages.get_courier_stage_time(order.order_id)

    assert open_time == stage_taken.effective_time - stage_open.effective_time
    assert taken_time == now - stage_taken.effective_time


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_stage_time_emergency_exit_before_open():
    now = datetime_utils.get_now()

    delta_6m = datetime.timedelta(minutes=6)
    delta_5m = datetime.timedelta(minutes=5)
    delta_4m = datetime.timedelta(minutes=4)
    delta_2m = datetime.timedelta(minutes=2)

    order = await orders.factories.create()

    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now-delta_6m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.EXITED_EMERGENCY,
        effective_time=now-delta_5m,
        order_id=order.order_id,
    )
    stage_open = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now-delta_4m,
        order_id=order.order_id,
    )
    stage_taken = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now-delta_2m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
        effective_time=now,
        order_id=order.order_id,
    )

    open_time, taken_time = await courier_order_stages.get_courier_stage_time(order.order_id)

    assert open_time == stage_taken.effective_time - stage_open.effective_time
    assert taken_time == now - stage_taken.effective_time


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_stage_time_emergency_exit_before_taken():
    now = datetime_utils.get_now()

    delta_6m = datetime.timedelta(minutes=6)
    delta_5m = datetime.timedelta(minutes=5)
    delta_4m = datetime.timedelta(minutes=4)

    order = await orders.factories.create()

    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now-delta_6m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.EXITED_EMERGENCY,
        effective_time=now-delta_5m,
        order_id=order.order_id,
    )
    stage_taken = await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now-delta_4m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
        effective_time=now,
        order_id=order.order_id,
    )

    open_time, taken_time = await courier_order_stages.get_courier_stage_time(order.order_id)

    assert open_time is None
    assert taken_time == now - stage_taken.effective_time


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_stage_time_emergency_exit_after_taken():
    now = datetime_utils.get_now()

    delta_6m = datetime.timedelta(minutes=6)
    delta_5m = datetime.timedelta(minutes=5)
    delta_4m = datetime.timedelta(minutes=4)

    order = await orders.factories.create()

    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now-delta_6m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now-delta_5m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.EXITED_EMERGENCY,
        effective_time=now-delta_4m,
        order_id=order.order_id,
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
        effective_time=now,
        order_id=order.order_id,
    )

    open_time, taken_time = await courier_order_stages.get_courier_stage_time(order.order_id)

    assert open_time is None
    assert taken_time is None
