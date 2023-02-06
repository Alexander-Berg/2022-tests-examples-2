import datetime

from stall.model.order_required import OrderRequired
from stall.model.sampling_condition import SamplingCondition
from libstall import json_pp


async def test_total_price(tap, dataset):
    with tap.plan(2):
        product1 = await dataset.product()
        product2 = await dataset.product()
        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        condition = SamplingCondition({
            'condition_type': 'total_price_above',
            'total_price': '1235.12',
        })
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(await condition.evaluate(order), 'Condition met')

        order = await dataset.order(type='order', required=required,
                                    total_price='1235.03')
        tap.ok(not await condition.evaluate(order), 'Condition not met')


async def test_group_present(tap, dataset):
    with tap.plan(2):
        group = await dataset.product_group(
            timetable=[{'type': 'everyday', 'begin': '00:00', 'end': '00:00'}])
        product1 = await dataset.product(groups=[group.group_id])
        product2 = await dataset.product()
        condition = SamplingCondition({
            'condition_type': 'group_present',
            'group_id': group.group_id,
        })

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(await condition.evaluate(order), 'Condition met')

        required = [
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(not await condition.evaluate(order), 'Condition not met')


async def test_product_present(tap, dataset):
    with tap.plan(2):
        product1 = await dataset.product()
        product2 = await dataset.product()
        condition = SamplingCondition({
            'condition_type': 'product_present',
            'product_id': product1.product_id,
        })

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(await condition.evaluate(order), 'Condition met')

        required = [
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(not await condition.evaluate(order), 'Condition not met')


async def test_and(tap, dataset):
    with tap.plan(3):
        product1 = await dataset.product()
        product2 = await dataset.product()

        condition1 = SamplingCondition({
            'condition_type': 'total_price_above',
            'total_price': '1235.12',
        })
        condition2 = SamplingCondition({
            'condition_type': 'product_present',
            'product_id': product1.product_id,
        })
        condition = SamplingCondition({
            'condition_type': 'and',
            'children': [condition1, condition2],
        })

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1235.03')
        tap.ok(not await condition.evaluate(order), 'Condition not met')

        required = [
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.03')
        tap.ok(not await condition.evaluate(order), 'Condition not met')

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.03')
        tap.ok(await condition.evaluate(order), 'Condition met')


async def test_or(tap, dataset):
    with tap.plan(3):
        product1 = await dataset.product()
        product2 = await dataset.product()

        condition1 = SamplingCondition({
            'condition_type': 'total_price_above',
            'total_price': '1235.12',
        })
        condition2 = SamplingCondition({
            'condition_type': 'product_present',
            'product_id': product1.product_id,
        })
        condition = SamplingCondition({
            'condition_type': 'or',
            'children': [condition1, condition2],
        })

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1235.03')
        tap.ok(await condition.evaluate(order), 'Condition met')

        required = [
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.03')
        tap.ok(await condition.evaluate(order), 'Condition met')

        required = [
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1235.03')
        tap.ok(not await condition.evaluate(order), 'Condition not met')


async def test_constant_true(tap, dataset):
    with tap.plan(1):
        condition = SamplingCondition({
            'condition_type': 'constant_true',
        })
        order = await dataset.order(type='order')
        tap.ok(await condition.evaluate(order), 'Condition met')


async def test_not(tap, dataset):
    with tap.plan(2):
        product1 = await dataset.product()
        product2 = await dataset.product()
        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        condition1 = SamplingCondition({
            'condition_type': 'total_price_above',
            'total_price': '1235.12',
        })
        condition = SamplingCondition({
            'condition_type': 'not',
            'children': [condition1],
        })
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(not await condition.evaluate(order), 'Condition not met')

        order = await dataset.order(type='order', required=required,
                                    total_price='1235.03')
        tap.ok(await condition.evaluate(order), 'Condition met')


async def test_dump_load(tap, dataset):
    with tap.plan(7):
        product1 = await dataset.product()
        product2 = await dataset.product()

        condition1 = SamplingCondition({
            'condition_type': 'total_price_above',
            'total_price': '1235.12',
        })
        condition2 = SamplingCondition({
            'condition_type': 'product_present',
            'product_id': product1.product_id,
        })
        condition = SamplingCondition({
            'condition_type': 'or',
            'children': [condition1, condition2],
        })

        condition = SamplingCondition(json_pp.loads(json_pp.dumps(condition)))

        tap.eq_ok(
            condition.children[0].condition_type,
            condition1.condition_type,
            'condition 1 type loaded correctly'
        )
        tap.eq_ok(
            condition.children[0].total_price,
            condition1.total_price,
            'condition 1 total_price loaded correctly'
        )

        tap.eq_ok(
            condition.children[1].condition_type,
            condition2.condition_type,
            'condition 2 type loaded correctly'
        )
        tap.eq_ok(
            condition.children[1].product_id,
            condition2.product_id,
            'condition 2 product_id loaded correctly'
        )

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1235.03')
        tap.ok(await condition.evaluate(order), 'Condition met')

        required = [
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.03')
        tap.ok(await condition.evaluate(order), 'Condition met')

        required = [
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1235.03')
        tap.ok(not await condition.evaluate(order), 'Condition not met')


async def test_sub_group_present(tap, dataset):
    with tap.plan(2):
        group0 = await dataset.product_group(
            timetable=[{'type': 'everyday', 'begin': '00:00', 'end': '00:00'}])
        group1 = await dataset.product_group(
            parent_group_id=group0.group_id,
            timetable=[{'type': 'everyday', 'begin': '00:00', 'end': '00:00'}])
        group2 = await dataset.product_group(
            parent_group_id=group1.group_id,
            timetable=[{'type': 'everyday', 'begin': '00:00', 'end': '00:00'}])
        group3 = await dataset.product_group(
            parent_group_id=group2.group_id,
            timetable=[{'type': 'everyday', 'begin': '00:00', 'end': '00:00'}])
        another_group = await dataset.product_group(
            timetable=[{'type': 'everyday', 'begin': '00:00', 'end': '00:00'}],
            parent_group_id=group0.group_id)
        product1 = await dataset.product(groups=[group3.group_id])
        product2 = await dataset.product(groups=[another_group.group_id])
        condition = SamplingCondition({
            'condition_type': 'group_present',
            'group_id': group1.group_id,
        })

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(await condition.evaluate(order), 'Condition met')

        required = [
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(not await condition.evaluate(order), 'Condition not met')


async def test_product_present_count(tap, dataset):
    with tap.plan(2):
        product1 = await dataset.product()
        product2 = await dataset.product()
        condition = SamplingCondition({
            'condition_type': 'product_present',
            'product_id': product1.product_id,
            'count': 3,
        })

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 3}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(await condition.evaluate(order), 'Condition met')

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
            OrderRequired({'product_id': product2.product_id, 'count': 3}),
        ]
        order = await dataset.order(type='order', required=required,
                                    total_price='1236.23')
        tap.ok(not await condition.evaluate(order), 'Condition not met')


async def test_tag_present(tap, dataset):
    with tap.plan(3):
        condition = SamplingCondition({
            'condition_type': 'tag_present',
            'client_tag': 'tag1',
        })

        order = await dataset.order(
            type='order',
            attr={'client_tags': ['tag0', 'tag1', 'tag2']})
        tap.ok(await condition.evaluate(order), 'Condition met')

        order = await dataset.order(type='order')
        tap.ok(not await condition.evaluate(order),
               'Condition not met, no client_tags')

        order = await dataset.order(
            type='order',
            attr={'client_tags': ['tag0', 'tag2']})
        tap.ok(not await condition.evaluate(order),
               'Condition not met, required client_tag not present')


async def test_group_timetable(tap, dataset):
    with tap.plan(2):
        group1 = await dataset.product_group(
            timetable=[{'type': 'everyday', 'begin': '00:00', 'end': '00:00'}])
        group2 = await dataset.product_group(
            parent_group_id=group1.group_id,
            timetable=[{'type': 'everyday', 'begin': '00:00', 'end': '00:00'}])
        group3 = await dataset.product_group(
            parent_group_id=group2.group_id,
            timetable=[{'type': 'everyday', 'begin': '11:00', 'end': '12:00'},
                       {'type': 'everyday', 'begin': '13:00', 'end': '14:00'},
                       {'type': 'everyday', 'begin': '15:00', 'end': '16:00'}])
        product1 = await dataset.product(groups=[group3.group_id])
        condition = SamplingCondition({
            'condition_type': 'group_present',
            'group_id': group1.group_id,
        })

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
        ]
        order = await dataset.order(type='order', required=required)
        order.created = datetime.datetime(2021, 9, 21, 13, 30,
                                          tzinfo=datetime.timezone.utc)

        store = await dataset.store(tz='UTC')
        order.store_id = store.store_id
        tap.eq(await condition.evaluate(order), True, 'Condition met')

        store = await dataset.store(tz='Europe/Moscow')
        order.store_id = store.store_id
        tap.eq(await condition.evaluate(order), False, 'Condition not met')


async def test_group_empty_timetable(tap, dataset):
    with tap.plan(1):
        group1 = await dataset.product_group(timetable=[])
        group2 = await dataset.product_group(parent_group_id=group1.group_id,
                                             timetable=[])
        group3 = await dataset.product_group(
            parent_group_id=group2.group_id,
            timetable=[])
        product1 = await dataset.product(groups=[group3.group_id])
        condition = SamplingCondition({
            'condition_type': 'group_present',
            'group_id': group1.group_id,
        })

        required = [
            OrderRequired({'product_id': product1.product_id, 'count': 2}),
        ]
        order = await dataset.order(type='order', required=required)

        tap.eq(await condition.evaluate(order), True, 'Condition met')
