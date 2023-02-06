# pylint: disable=too-many-lines
import argparse
import asyncio
from collections import defaultdict
import datetime
import random

import pytest

from scripts.cron.create_move_orders_kitchen import (
    generate_order_conditions,
    generate_threshold,
    create_orders_common,
    create_orders_script,
    job_create_orders,
    get_order_by_store,
)
from stall.model.product_components import ProductComponents, ProductVariant


VALID_FOR_SURE = datetime.date.today() + datetime.timedelta(days=300)


@pytest.mark.non_parallel
async def test_generate_conditions(tap, dataset):
    with tap.plan(6, 'базовые кейсы с различным инпутом'):
        product = await dataset.product()
        product_variant = ProductVariant(
            product_id=product.product_id, count=100
        )
        product.components = ProductComponents([[product_variant]])
        await product.save()

        ass = await dataset.kitchen_assortment()
        await dataset.assortment_product(
            assortment_id=ass.assortment_id,
            product_id=product.product_id,
        )

        store = await dataset.full_store(
            kitchen_assortment_id=ass.assortment_id
        )

        await dataset.stock(
            product=product,
            shelf_type='kitchen_components',
            store=store,
            count=499,
        )

        await dataset.StoreStock.daemon(exit_at_endlog=True)
        thresholds = {product.product_id: 500}

        conds, order_descs = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
            try_additional_generate=False,
        )
        tap.eq_ok(
            conds[product.product_id][0][product.product_id],
            500,
            'нужно чтоб на полке было 500'
        )
        tap.ok(
            not order_descs,
            'не хватает товара для пополнения kitchen_components'
        )

        conds, order_descs = await generate_order_conditions(
            store=store,
            threshold_trigger_multiplier=5,
            threshold_target_multiplier=5,
            try_additional_generate=False,
        )
        tap.eq_ok(
            conds[product.product_id][0][product.product_id],
            500,
            'нужно чтоб на полке было 500'
        )

        await dataset.stock(
            product=product,
            store=store,
            count=1,
            reserve=1,
            valid=VALID_FOR_SURE,
        )

        _, order_descs = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
            try_additional_generate=False,
        )
        tap.ok(
            not order_descs,
            'не хватает товара для пополнения kitchen_components, '
            'так как он зарезервирован'
        )

        await dataset.stock(
            product=product,
            store=store,
            count=1,
            reserve=0,
            valid=VALID_FOR_SURE,
        )
        _, order_descs = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
            try_additional_generate=False,
        )
        tap.eq_ok(
            order_descs,
            {product.product_id: 1},
            'возможен заказ на 1 упаковку'
        )

        await dataset.stock(
            product=product,
            shelf_type='kitchen_components',
            store=store,
            count=1,
            valid=VALID_FOR_SURE,
        )
        await dataset.StoreStock.daemon_cycle()
        _, order_descs = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
            try_additional_generate=False,
        )
        tap.ok(not order_descs, 'заказы на пополнение не нужны')


# pylint: disable=too-many-locals
@pytest.mark.non_parallel
async def test_generate_conds_variants(tap, dataset):
    with tap.plan(10, 'кейсы с разными вариантами на conditions'):
        subproducts = [await dataset.product() for _ in range(3)]
        products = [await dataset.product() for _ in range(2)]
        comps1 = [
            [(subproducts[0], 100), (subproducts[1], 100)],
            [(subproducts[2], 50)],
        ]
        comps2 = [[(subproducts[1], 200)]]
        comps = [comps1, comps2]
        for i, p in enumerate(products):
            cur_comps = ProductComponents(
                [
                    [
                        ProductVariant(product_id=subp.product_id, count=cnt)
                        for subp, cnt in c
                    ]
                    for c in comps[i]
                ]
            )
            p.components = cur_comps
            await p.save()

        ass = await dataset.kitchen_assortment()
        for p in products:
            await dataset.assortment_product(
                assortment_id=ass.assortment_id,
                product_id=p.product_id,
            )

        store = await dataset.full_store(
            kitchen_assortment_id=ass.assortment_id
        )

        for sp in subproducts:
            await dataset.stock(
                product=sp,
                shelf_type='kitchen_components',
                store=store,
                count=199,
            )

        await dataset.StoreStock.daemon(exit_at_endlog=True)

        pids = [p.product_id for p in products]
        spids = [sp.product_id for sp in subproducts]
        thresholds = {
            spids[0]: 200,
            spids[1]: 400,
            spids[2]: 201,
        }

        conds, _ = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
        )
        tap.eq(conds[pids[0]][0][spids[1]], 400, '400')
        tap.eq(conds[pids[0]][0][spids[0]], 200, '200')
        tap.eq(conds[pids[0]][1][spids[2]], 201, '201')
        tap.eq(conds[pids[1]][0][spids[1]], 400, '400')

        thresholds[spids[0]] = 199
        conds, _ = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
        )
        tap.eq(len(conds[pids[0]]), 1, 'only 1 missing')
        tap.eq(conds[pids[0]][0][spids[2]], 201, '201')
        tap.eq(conds[pids[1]][0][spids[1]], 400, '400')

        thresholds[spids[2]] = 199
        conds, _ = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
        )
        tap.eq(conds[pids[1]][0][spids[1]], 400, '400')
        tap.ok(not conds.get(pids[0]), '1st product ok')

        thresholds[spids[1]] = 199
        conds, _ = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
        )
        tap.ok(not conds, 'all products ok')


async def test_generate_thresholds(tap, dataset):
    with tap.plan(3, 'базовые кейсы с различным инпутом'):
        product = await dataset.product()
        product_variant = ProductVariant(
            product_id=product.product_id, count=100
        )
        product.components = ProductComponents([[product_variant]])
        await product.save()

        ass = await dataset.kitchen_assortment()
        await dataset.assortment_product(
            assortment_id=ass.assortment_id,
            product_id=product.product_id,
        )

        store = await dataset.store(kitchen_assortment_id=ass.assortment_id)

        thresholds = await generate_threshold(
            kitchen_assortment_id=store.kitchen_assortment_id, multiplier=2
        )
        tap.eq(thresholds, {product.product_id: 200}, '200')

        thresholds = await generate_threshold(
            products=[product], multiplier=2
        )
        tap.eq(thresholds, {product.product_id: 200}, '200')

        thresholds = await generate_threshold(
            kitchen_assortment_id=ass.assortment_id, multiplier=2
        )
        tap.eq(thresholds, {product.product_id: 200}, '200')


# pylint: disable=too-many-branches
async def test_random_conds_orders(tap, dataset, cfg):
    cfg.set('business.kitchen_autorestocking.threshold_trigger_multiplier', 2)
    cfg.set('business.kitchen_autorestocking.threshold_target_multiplier', 2)
    count = 10
    with tap.plan(
            4*count + 5,
            f'генерим {count} рандомных продуктов, чекаем все'
    ):
        products = [await dataset.product() for _ in range(count)]
        subproducts = [
            await dataset.product(quants=random.randint(1, count**2))
            for _ in range(count)
        ]

        for p in products:
            # генерим рандомный набор компонент длины >= 1
            comps = set()
            comps.add(random.randrange(0, count))
            for i in range(count):
                if random.randint(0, 1):
                    comps.add(i)
            comps = [{i} for i in comps]
            for comp in comps:
                for i in range(count):
                    if random.randint(0, 1):
                        comp.add(i)
            comps = ProductComponents(
                [
                    [
                        ProductVariant(
                            product_id=subproducts[i].product_id,
                            count=(
                                random.randint(2, count) *
                                random.randint(1, subproducts[i].quants)
                            ),
                        )
                        for i in comp
                    ]
                    for comp in comps
                ]
            )

            p.components = comps
            await p.save()

        ass = await dataset.kitchen_assortment()
        for p in products:
            await dataset.assortment_product(
                assortment_id=ass.assortment_id,
                product_id=p.product_id,
            )

        store = await dataset.store(kitchen_assortment_id=ass.assortment_id)

        thresholds = await generate_threshold(
            kitchen_assortment_id=store.kitchen_assortment_id, multiplier=2
        )

        for i, p in enumerate(products):
            tap.ok(
                all(
                    2*v.count <= thresholds[v.product_id]
                    for c in p.components for v in c
                ),
                f'{i+1}-й продукт насыщен порогами'
            )

        conds, order_descs = await generate_order_conditions(
            store=store,
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )

        for i, p in enumerate(products):
            csp = conds[p.product_id]
            tap.ok(
                all(
                    2*v.count <= cond_comp[v.product_id]
                    for c in p.components for v in c for cond_comp in csp
                    if v.product_id in cond_comp
                ),
                f'{i+1}-й продукт насыщен условиями'
            )

        tap.eq(order_descs, {}, 'ничего не можем заказать')

        enough_for_one = (count**3)//min([sp.quants for sp in subproducts])
        await dataset.stock(
            product=subproducts[0],
            store=store,
            count=2*enough_for_one + 1,
            valid=VALID_FOR_SURE,
        )

        _, order_descs = await generate_order_conditions(
            store=store,
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
            try_additional_generate=False,
        )

        tap.eq(
            len(order_descs),
            1,
            'можем заказать 1 продукт по порогам'
        )

        for sp in subproducts:
            thresholds[sp.product_id] = (count**10)*sp.quants
        _, order_descs = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
            try_additional_generate=False,
        )

        tap.ok(
            not order_descs,
            'ничего не можем заказать, если ориентируемся на пороги'
        )

        _, order_descs = await generate_order_conditions(
            store=store,
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
        )

        tap.eq(
            len(order_descs),
            1,
            'можем заказать 1 продукт, но пороги не выполним'
        )

        for sp in subproducts[1:]:
            for _ in range(8):
                await dataset.stock(
                    product=sp,
                    store=store,
                    count=enough_for_one,
                    reserve=random.randint(
                        enough_for_one//2, 3*enough_for_one//4
                    ),
                    valid=VALID_FOR_SURE,
                )

        _, order_descs = await generate_order_conditions(
            store=store, try_additional_generate=False,
        )

        for i, p in enumerate(products):
            tap.ok(
                all(
                    any(
                        2*v.count <= order_descs.get(v.product_id, 0)
                        for v in c
                    )
                    for c in p.components
                ),
                f'можем заказать {i+1}-й продукт по порогам',
            )

        _, order_descs = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
            try_additional_generate=False,
        )

        tap.ok(
            not order_descs,
            'ничего не можем заказать, если ориентируемся на пороги'
        )

        _, order_descs = await generate_order_conditions(
            store=store,
            trigger_thresholds=thresholds,
            target_thresholds=thresholds,
        )

        for i, p in enumerate(products):
            tap.ok(
                all(
                    any(
                        2 * v.count <= order_descs.get(v.product_id, 0)
                        for v in c
                    )
                    for c in p.components
                ),
                f'можем заказать {i+1}-й продукт не по порогам',
            )


async def test_thresholds_mapping(tap, dataset):
    with tap.plan(3, 'проверяем генерацию порогов по маппингу'):
        products = [await dataset.product() for _ in range(2)]
        subproducts = [await dataset.product() for _ in range(2)]

        for i, p in enumerate(products):
            p.components = ProductComponents(
                [
                    [
                        ProductVariant(
                            product_id=sp.product_id,
                            count=100*(i-j+2)+1,
                        )
                    ]
                    for j, sp in enumerate(subproducts)
                ]
            )
            await p.save()

        ass = await dataset.kitchen_assortment()
        for p in products:
            await dataset.assortment_product(
                assortment_id=ass.assortment_id,
                product_id=p.product_id,
            )

        store = await dataset.store(kitchen_assortment_id=ass.assortment_id)

        thresholds = await generate_threshold(
            kitchen_assortment_id=store.kitchen_assortment_id, multiplier=1
        )

        tap.eq(
            thresholds,
            {
                subproducts[0].product_id: 301,
                subproducts[1].product_id: 201,
            },
            'пороги с multiplier=1',
        )

        mapping = {products[1].product_id: 1}
        thresholds = await generate_threshold(
            kitchen_assortment_id=store.kitchen_assortment_id,
            multiplier=2,
            mapping=mapping
        )

        tap.eq(
            thresholds,
            {
                subproducts[0].product_id: 402,
                subproducts[1].product_id: 202,
            },
            'пороги с multiplier=2 и маппингом',
        )

        mapping = {
            p.product_id: 1 for p in products
        }
        thresholds = await generate_threshold(
            kitchen_assortment_id=store.kitchen_assortment_id,
            multiplier=2,
            mapping=mapping
        )

        tap.eq(
            thresholds,
            {
                subproducts[0].product_id: 301,
                subproducts[1].product_id: 201,
            },
            'пороги с фулл маппингом=1',
        )


@pytest.mark.non_parallel
async def test_create_orders_basic(tap, dataset, wait_order_status):
    # pylint: disable=too-many-statements
    with tap.plan(16, 'тестируем базовый кейс create_orders'):
        product = await dataset.product(quants=50)
        product_variant = ProductVariant(
            product_id=product.product_id, count=100
        )
        product.components = ProductComponents([[product_variant]])
        await product.save()

        ass = await dataset.kitchen_assortment()
        await dataset.assortment_product(
            assortment_id=ass.assortment_id,
            product_id=product.product_id,
        )

        store = await dataset.full_store(
            kitchen_assortment_id=ass.assortment_id,
        )

        await dataset.stock(
            product=product,
            shelf_type='kitchen_components',
            store=store,
            count=49,
        )
        await dataset.StoreStock.daemon(exit_at_endlog=True)

        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )

        order = await get_order_by_store(store)
        tap.ok(not order, 'ордер не был создан')

        await dataset.stock(
            product=product,
            shelf_type='store',
            store=store,
            count=1,
            valid=VALID_FOR_SURE,
        )

        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )

        order = await get_order_by_store(store)
        tap.ok(not order, 'все еще не создан')

        await dataset.stock(
            product=product,
            shelf_type='store',
            store=store,
            count=1,
            valid=VALID_FOR_SURE,
        )

        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
            try_additional_generate=False,
        )

        order = await get_order_by_store(store)
        tap.ok(not order, 'все еще не создан')

        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )

        order = await get_order_by_store(store)
        tap.ok(not order, 'все еще не создан')

        store.rehash(options={'exp_gargantua': True})
        await store.save()

        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )

        order = await get_order_by_store(store)
        tap.ok(order, 'ордер был создан')
        tap.ok(
            all(
                r.product_id == product.product_id
                for r in order.required
            ),
            'все заказы на один и тот же продукт'
        )
        tap.eq(
            sum(r.count for r in order.required),
            2,
            'нужно перетащить две пачки'
        )
        await order.cancel()
        await wait_order_status(order, ('canceled', 'done'))

        shelf = await dataset.shelf(store=store)
        await dataset.stock(
            product=product,
            shelf=shelf,
            shelf_type='store',
            store=store,
            count=9,
            valid=VALID_FOR_SURE,
        )

        await create_orders_common(
            [store],
            threshold_trigger_multiplier=5,
            threshold_target_multiplier=5,
        )

        order = await get_order_by_store(store)
        tap.ok(order, 'ордер был создан')
        tap.ok(len(order.required) > 1, 'в required больше 1 полки')
        tap.ok(
            all(
                r.product_id == product.product_id
                for r in order.required
            ),
            'все заказы на один и тот же продукт',
        )
        tap.eq(
            sum(r.count for r in order.required),
            10,
            'нужно перетащить 10 пачек'
        )

        old_order = order
        await create_orders_common(
            [store],
            threshold_trigger_multiplier=5,
            threshold_target_multiplier=5,
        )
        order = await get_order_by_store(store)
        tap.ok(order, 'ордер был создан')
        tap.eq(old_order.order_id, order.order_id, 'заказ не поменялся')

        await order.cancel()
        await wait_order_status(order, ('canceled', 'done'))

        await create_orders_common(
            [store],
            threshold_trigger_multiplier=300,
            threshold_target_multiplier=300,
            try_additional_generate=False,
        )
        order = await get_order_by_store(store)
        tap.ok(not order, 'заказа нет')


async def test_create_orders_shelves(tap, dataset, wait_order_status):
    # pylint: disable=too-many-statements
    with tap.plan(23, 'проверяем, что кладем на правильные полки'):
        sps = [await dataset.product() for _ in range(2)]
        ps = [await dataset.product() for _ in range(2)]
        pvs = [
            ProductVariant(
                product_id=sp.product_id, count=5
            )
            for sp in sps
        ]

        ps[0].components = ProductComponents([[pvs[0]], [pvs[1]]])
        await ps[0].save()

        ass = await dataset.kitchen_assortment()
        await dataset.assortment_product(
            assortment_id=ass.assortment_id,
            product_id=ps[0].product_id,
        )

        store = await dataset.full_store(
            kitchen_assortment_id=ass.assortment_id,
            options={'exp_gargantua': True},
        )

        kshelf = await dataset.shelf(store=store, type='kitchen_components')
        await dataset.stock(store=store, product=sps[0], shelf=kshelf, count=0)

        shelves_store = [await dataset.shelf(store=store) for _ in range(6)]
        for i in range(6):
            await dataset.stock(
                store=store,
                product=sps[0],
                shelf=shelves_store[i],
                count=i+1,
                valid=VALID_FOR_SURE,
            )
            await dataset.stock(
                store=store,
                product=sps[1],
                shelf=shelves_store[5-i],
                count=i+1,
                valid=VALID_FOR_SURE,
            )

        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )
        order = await get_order_by_store(store)
        tap.ok(order, 'ордер был создан')
        tap.eq(len(order.required), 4, '4 полки')

        srcdst2req = {
            (r.src_shelf_id, r.dst_shelf_id): r
            for r in order.required
        }
        sp0_6 = srcdst2req[(shelves_store[5].shelf_id, kshelf.shelf_id)]
        tap.eq(sp0_6.product_id, sps[0].product_id, 'правильный pid')
        tap.eq(sp0_6.count, 6, 'берем все с полки')
        srcdst2req.pop((shelves_store[5].shelf_id, kshelf.shelf_id))
        sp0_4 = srcdst2req[(shelves_store[4].shelf_id, kshelf.shelf_id)]
        tap.eq(sp0_4.product_id, sps[0].product_id, 'правильный pid')
        tap.eq(sp0_4.count, 4, 'берем 4 с полки')
        srcdst2req.pop((shelves_store[4].shelf_id, kshelf.shelf_id))
        cnts = {4, 6}
        sh_ids = {shelves_store[i].shelf_id for i in range(2)}
        for r in srcdst2req.values():
            tap.ok(r.count in cnts, 'cnt ok')
            tap.ok(r.src_shelf_id in sh_ids, 'shelf ok')
            cnts.remove(r.count)
            sh_ids.remove(r.src_shelf_id)

        pvs2 = pvs.copy()
        for v in pvs2:
            v.count = 1
        sps.append(await dataset.product(tags=['freezer']))
        pvs2.append(ProductVariant(product_id=sps[2].product_id, count=1))
        ps[1].components = ProductComponents([[pv] for pv in pvs2])
        await ps[1].save()

        shelf_freezer = await dataset.shelf(
            store=store,
            tags=['freezer']
        )
        await dataset.stock(
            store=store,
            product=sps[2],
            count=100,
            shelf=shelf_freezer,
            valid=VALID_FOR_SURE,
        )
        await dataset.assortment_product(
            assortment_id=ass.assortment_id,
            product_id=ps[1].product_id,
        )

        old_order = order
        await order.cancel()
        await wait_order_status(order, ('canceled', 'done'))
        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )
        order = await get_order_by_store(store)
        tap.ok(order, 'ордер был создан')
        tap.ok(not old_order.order_id == order.order_id, 'заказ поменялся')
        old_req = sorted(
            order.required, key=lambda x: x.src_shelf_id + x.dst_shelf_id
        )
        new_req = sorted(
            order.required, key=lambda x: x.src_shelf_id + x.dst_shelf_id
        )
        tap.eq(old_req, new_req, 'required совпадают')

        await dataset.shelf(
            store=store, type='kitchen_components',
            tags=['freezer'], status='disabled'
        )

        await order.cancel()
        await wait_order_status(order, ('canceled', 'done'))
        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )
        order = await get_order_by_store(store)
        tap.ok(order, 'ордер был создан')

        r_freezer = [
            r for r in order.required
            if r.product_id == sps[2].product_id
        ]
        tap.eq(len(r_freezer), 0, 'no hand_move to disabled shelf')

        kshelf_freezer = await dataset.shelf(
            store=store, type='kitchen_components', tags=['freezer']
        )

        await order.cancel()
        await wait_order_status(order, ('canceled', 'done'))
        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )
        order = await get_order_by_store(store)
        tap.ok(order, 'ордер был создан')

        r_freezer = next(
            iter(
                [
                    r for r in order.required
                    if r.product_id == sps[2].product_id
                ]
            )
        )
        tap.eq(r_freezer.product_id, sps[2].product_id, 'product_id')
        tap.eq(r_freezer.src_shelf_id, shelf_freezer.shelf_id, 'src_shelf_id')
        tap.eq(r_freezer.dst_shelf_id, kshelf_freezer.shelf_id, 'dst_shelf_id')
        tap.eq(r_freezer.count, 2, 'count')


async def test_create_orders_script(tap, dataset, wait_order_status):
    # pylint: disable=too-many-statements
    with tap.plan(19, 'тестируем работу скрипта и режим merge'):
        sps = [await dataset.product() for _ in range(2)]
        ps = [await dataset.product() for _ in range(2)]
        pvs = {
            ps[0].product_id: [
                ProductVariant(
                    product_id=sps[0].product_id, count=4
                ),
                ProductVariant(
                    product_id=sps[1].product_id, count=9
                ),
            ],
            ps[1].product_id: [
                ProductVariant(
                    product_id=sps[0].product_id, count=11
                ),
                ProductVariant(
                    product_id=sps[1].product_id, count=5
                ),
                ProductVariant(
                    product_id=sps[0].product_id, count=13,
                )
            ],
        }
        for p in ps:
            p.components = ProductComponents(
                [[pv] for pv in pvs[p.product_id]]
            )
            await p.save()

        ass = await dataset.kitchen_assortment()
        for p in ps:
            await dataset.assortment_product(
                assortment_id=ass.assortment_id,
                product_id=p.product_id,
            )

        store = await dataset.full_store(
            kitchen_assortment_id=ass.assortment_id,
            options={'exp_gargantua': True},
        )

        for sp in sps:
            for i in range(25):
                await dataset.stock(
                    store=store,
                    product=sp,
                    count=100,
                    valid=VALID_FOR_SURE - datetime.timedelta(days=i*2+1),
                )

        args = argparse.Namespace(
            store=store.store_id,
            products=sps[0].product_id,
            merge=True,
            apply=False,
            trigger_multiplier=2,
            target_multiplier=2,
            delay=0,
        )

        tap.ok(not await create_orders_script(args), 'не смогли найти продукт')

        args.products = ps[0].product_id
        tap.ok(not await create_orders_script(args), 'не включен apply')

        args.apply = True
        tap.ok(await create_orders_script(args), 'создали ордер')
        order = await get_order_by_store(store)
        tap.ok(order, 'нашли ордер')
        tap.eq(len(order.required), 2, 'два переноса')

        p0sp0 = [
            r for r in order.required
            if r.product_id == sps[0].product_id
        ][0]
        p0sp1 = [
            r for r in order.required
            if r.product_id == sps[1].product_id
        ][0]
        tap.eq(p0sp0.count, 8, 'компонента первого сп=8')
        tap.eq(p0sp1.count, 18, 'компонента второго сп=18')

        async def wait_and_wait_order_status(order, sec=1):
            await asyncio.sleep(sec)
            await wait_order_status(order, ('canceled', 'done'))

        args.products = ps[1].product_id
        cancel_task = asyncio.create_task(
            wait_and_wait_order_status(order)
        )
        tap.ok(await create_orders_script(args), 'создали ордер')
        await cancel_task
        order = await get_order_by_store(store)
        tap.ok(order, 'нашли ордер')
        tap.eq(len(order.required), 2, 'два переноса')
        p0sp0 = [
            r for r in order.required
            if r.product_id == sps[0].product_id
        ][0]
        p0sp1 = [
            r for r in order.required
            if r.product_id == sps[1].product_id
        ][0]
        tap.eq(p0sp0.count, 26, 'компонента первого сп=26')
        tap.eq(p0sp1.count, 18, 'компонента второго сп=18')

        args.trigger_multiplier = 1
        args.target_multiplier = 1
        args.merge = False
        args.products = None
        cancel_task = asyncio.create_task(
            wait_and_wait_order_status(order)
        )
        tap.ok(await create_orders_script(args), 'создали ордер')
        await cancel_task
        order = await get_order_by_store(store)
        tap.ok(order, 'нашли ордер')
        tap.eq(len(order.required), 2, 'два переноса')
        p0sp0 = [
            r for r in order.required
            if r.product_id == sps[0].product_id
        ][0]
        p0sp1 = [
            r for r in order.required
            if r.product_id == sps[1].product_id
        ][0]
        tap.eq(p0sp0.count, 13, 'компонента первого сп=13')
        tap.eq(p0sp1.count, 9, 'компонента второго сп=9')


async def test_create_orders_all(tap, dataset, wait_order_status):
    with tap.plan(81, 'создаем много лавок, продуктов и заказов'):
        def random_count():
            cnt = random.randint(1, 10)
            for _ in range(5):
                if random.randint(0, 1):
                    cnt += random.randint(10, 20)
                else:
                    break
            return cnt

        async def wait_and_wait_order_status(order, sec=3):
            await asyncio.sleep(sec)
            await wait_order_status(order, ('canceled', 'done'))

        stores = [
            await dataset.full_store(options={'exp_gargantua': True})
            for _ in range(3)
        ]
        store2ps = {}
        store2sps = {}
        for store in stores:
            sps = [await dataset.product() for _ in range(8)]
            ps = [await dataset.product() for _ in range(4)]
            store2ps[store.store_id] = ps
            store2sps[store.store_id] = sps
            for p in ps:
                pvs = [
                    ProductVariant(
                        product_id=sp.product_id, count=random_count()
                    )
                    for sp in sps
                ]
                p.components = ProductComponents([[pv] for pv in pvs])
                await p.save()

            ass = await dataset.kitchen_assortment()
            for p in ps:
                await dataset.assortment_product(
                    assortment_id=ass.assortment_id,
                    product_id=p.product_id,
                )

            store.kitchen_assortment_id = ass.assortment_id
            await store.save()

            for sp in sps:
                await dataset.stock(
                    store=store,
                    product=sp,
                    count=1000000,
                    valid=VALID_FOR_SURE,
                )

        await create_orders_common(
            stores,
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )

        for store in stores:
            ps = store2ps[store.store_id]
            sps = store2sps[store.store_id]
            order = await get_order_by_store(store)
            tap.ok(order, 'order нашелся')
            pseudostocks = {}
            for r in order.required:
                pseudostocks[r.product_id] = r.count
            for p in ps:
                tap.ok(
                    all(
                        2*c[0].count <= pseudostocks[c[0].product_id]
                        for c in p.components
                    ),
                    'хватит на две порции',
                )
            for i, sp in enumerate(sps):
                tap.ok(
                    any(
                        2*c[0].count > pseudostocks[c[0].product_id] - 1
                        for p in ps
                        for c in p.components
                    ),
                    f'сабпродукта {i+1} положено сколько надо',
                )

        tasks = [
            asyncio.create_task(
                create_orders_common(
                    stores,
                    threshold_trigger_multiplier=3,
                    threshold_target_multiplier=3,
                )
            )
        ]
        for store in stores:
            order = await get_order_by_store(store)
            tasks.append(
                asyncio.create_task(wait_and_wait_order_status(order))
            )
        for task in reversed(tasks):
            await task

        for store in stores:
            ps = store2ps[store.store_id]
            sps = store2sps[store.store_id]
            order = await get_order_by_store(store)
            tap.ok(order, 'order нашелся')
            pseudostocks = {}
            for r in order.required:
                pseudostocks[r.product_id] = r.count
            for p in ps:
                tap.ok(
                    all(
                        3*c[0].count <= pseudostocks[c[0].product_id]
                        for c in p.components
                    ),
                    'хватит на две порции',
                )
            for i, sp in enumerate(sps):
                tap.ok(
                    any(
                        3*c[0].count > pseudostocks[c[0].product_id] - 1
                        for p in ps
                        for c in p.components
                    ),
                    f'сабпродукта {i+1} положено сколько надо',
                )


async def test_create_orders_job(tap, dataset, wait_order_status):
    with tap.plan(8, 'проверяем функцию для джоб'):
        product = await dataset.product(quants=3)
        product_variant = ProductVariant(
            product_id=product.product_id, count=10
        )
        product.components = ProductComponents([[product_variant]])
        await product.save()

        ass = await dataset.kitchen_assortment()
        await dataset.assortment_product(
            assortment_id=ass.assortment_id,
            product_id=product.product_id,
            trigger_threshold=None,
            target_threshold=None,
        )

        store = await dataset.full_store(
            kitchen_assortment_id=ass.assortment_id,
            options={'exp_gargantua': True},
        )
        await dataset.stock(
            product=product,
            store=store,
            count=3,
            valid=VALID_FOR_SURE,
        )

        stores = [store.store_id]
        await job_create_orders(
            stores,
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )

        order = await get_order_by_store(store)
        tap.ok(not order, 'ничего не можем перенести')

        await dataset.stock(
            product=product,
            store=store,
            count=4,
            valid=VALID_FOR_SURE,
        )
        await job_create_orders(
            stores,
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )

        order = await get_order_by_store(store)
        tap.ok(
            all(
                r.product_id == product.product_id for r in order.required
            ),
            'переносим один товар'
        )
        tap.eq(sum(r.count for r in order.required), 7, 'несем 7 пачек')

        old_order = order
        await job_create_orders(
            stores,
            threshold_trigger_multiplier=3,
            threshold_target_multiplier=3,
        )
        order = await get_order_by_store(store)
        tap.eq(old_order.order_id, order.order_id, 'ордер остался')

        await dataset.stock(
            product=product,
            store=store,
            count=3,
            valid=VALID_FOR_SURE,
        )

        await order.cancel()
        await wait_order_status(order, ('canceled', 'done'))
        await job_create_orders(
            stores,
            threshold_trigger_multiplier=3,
            threshold_target_multiplier=3,
        )

        await order.cancel()
        await wait_order_status(order, ('canceled', 'done'))
        order = await get_order_by_store(store)
        tap.ok(
            all(
                r.product_id == product.product_id for r in order.required
            ),
            'переносим один товар'
        )
        tap.eq(sum(r.count for r in order.required), 10, 'несем 10 пачек')


async def test_create_orders_stocks(tap, dataset, uuid):
    with tap.plan(9, 'проверяем кейс с большим кол-вом разных стоков'):
        product = await dataset.product(quants=3)
        product_variant = ProductVariant(
            product_id=product.product_id, count=10
        )
        product.components = ProductComponents([[product_variant]])
        await product.save()

        ass = await dataset.kitchen_assortment()
        await dataset.assortment_product(
            assortment_id=ass.assortment_id,
            product_id=product.product_id,
        )

        store = await dataset.full_store(
            kitchen_assortment_id=ass.assortment_id,
            options={'exp_gargantua': True},
        )

        shelves = []
        for i in range(10):
            shelves.append(await dataset.shelf(store=store))
            valid = VALID_FOR_SURE - datetime.timedelta(days=i)
            if i == 9:
                valid = None
            await dataset.stock(
                store=store,
                shelf=shelves[-1],
                product=product,
                count=1,
                lot=str(i),
                valid=valid,
            )
        await dataset.stock(
            store=store,
            product=product,
            count=0,
            lot=uuid(),
            valid=VALID_FOR_SURE-datetime.timedelta(days=100)
        )

        await create_orders_common(
            [store],
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=2,
        )
        order = await get_order_by_store(store)
        tap.ok(order, 'создали ордер')
        tap.eq(len(order.required), 7, '7 переносов')
        for i, r in enumerate(order.required):
            tap.eq(r.src_shelf_id, shelves[9-i].shelf_id, 'берем тухлое')


@pytest.mark.non_parallel
async def test_gen_conds_diff_thresholds(tap, dataset):
    with tap.plan(4, 'проверяем работу trigger/target порогов'):
        product = await dataset.product(quants=3)
        product_variant = ProductVariant(
            product_id=product.product_id, count=10
        )
        product.components = ProductComponents([[product_variant]])
        await product.save()

        ass = await dataset.kitchen_assortment()
        await dataset.assortment_product(
            assortment_id=ass.assortment_id,
            product_id=product.product_id,
        )

        store = await dataset.full_store(
            kitchen_assortment_id=ass.assortment_id
        )
        await dataset.stock(
            store=store,
            count=300,
            product=product,
        )

        conds, order_descs = await generate_order_conditions(
            store=store,
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=5,
        )

        tap.eq(
            conds[product.product_id][0],
            {product.product_id: 50},
            'условия правильные'
        )
        tap.eq(
            order_descs,
            {product.product_id: 50},
            'описание заказа правильное'
        )

        await dataset.stock(
            store=store,
            shelf_type='kitchen_components',
            count=20,
            product=product,
        )
        await dataset.StoreStock.daemon(exit_at_endlog=True)
        conds, order_descs = await generate_order_conditions(
            store=store,
            threshold_trigger_multiplier=2,
            threshold_target_multiplier=5,
        )

        tap.eq(conds, {}, 'условия правильные')
        tap.eq(order_descs, {}, 'описание заказа правильное')


async def test_script_many_products(tap, dataset, wait_order_status):
    with tap.plan(7, 'тестируем работу скрипта с несколькими продуктами'):
        ps = [await dataset.product() for _ in range(3)]
        ass = await dataset.kitchen_assortment()
        store = await dataset.full_store(
            kitchen_assortment_id=ass.assortment_id,
            options={'exp_gargantua': True},
        )

        for p in ps:
            p.components = ProductComponents(
                [[ProductVariant(product_id=p.product_id, count=1)]]
            )
            await p.save()
            await dataset.assortment_product(product=p, assortment=ass)
            await dataset.stock(
                store=store,
                product=p,
                count=300,
            )

        args = argparse.Namespace(
            store=store.store_id,
            products=ps[0].product_id + '  ',
            merge=True,
            apply=True,
            trigger_multiplier=1,
            target_multiplier=5,
            delay=0,
        )
        await create_orders_script(args)
        order = await get_order_by_store(store)
        tap.ok(order, 'создали ордер')
        tap.eq(len(order.required), 1, 'один перенос')
        await order.cancel()
        await wait_order_status(order, ('canceled', 'done'))

        args.products = ' ' + ' '.join([p.product_id for p in ps]) + ' '
        await create_orders_script(args)
        order = await get_order_by_store(store)
        tap.ok(order, 'создали ордер')
        tap.eq(len(order.required), 3, 'три переноса')

        args.products = None
        await create_orders_script(args)
        old_order_id = order.order_id
        order = await get_order_by_store(store)
        tap.ok(order, 'создали ордер')
        tap.eq(old_order_id, order.order_id, 'тот же ордер')


@pytest.mark.non_parallel
async def test_job_func_many_stores(tap, dataset, wait_order_status):
    # pylint: disable=too-many-statements
    with tap.plan(38, 'тестим джобу с разными параметрами в ассортиментах'):
        stores = [
            await dataset.full_store(options={'exp_gargantua': True})
            for _ in range(2)
        ]
        rands = {s.store_id: random.randint(10, 50) for s in stores}
        ps = {}
        asss = {}
        aps = defaultdict(dict)
        for s in stores:
            asss[s.store_id] = await dataset.kitchen_assortment()
            s.kitchen_assortment_id = asss[s.store_id].assortment_id
            await s.save()

            ps[s.store_id] = [await dataset.product() for _ in range(6)]
            for i, p in enumerate(ps[s.store_id]):
                p.components = ProductComponents(
                    [[ProductVariant(
                        product_id=p.product_id, count=1,
                    )]]
                )
                await p.save()
                aps[s.store_id][p.product_id] = (
                    await dataset.assortment_product(
                        product=p,
                        assortment=asss[s.store_id],
                        trigger_threshold=rands[s.store_id],
                        target_threshold=2*rands[s.store_id],
                    )
                )
                await dataset.stock(store=s, product=p, count=10000)

            sid = s.store_id
            aps[sid][ps[sid][0].product_id].trigger_threshold = 0
            aps[sid][ps[sid][1].product_id].trigger_threshold = 0
            aps[sid][ps[sid][1].product_id].target_threshold = 0
            aps[sid][ps[sid][3].product_id].trigger_threshold = None
            aps[sid][ps[sid][4].product_id].target_threshold = None
            aps[sid][ps[sid][5].product_id].trigger_threshold = None
            aps[sid][ps[sid][5].product_id].target_threshold = None
            for ap in aps[sid].values():
                await ap.save()

        await job_create_orders(
            stores=[s.store_id for s in stores],
            threshold_trigger_multiplier=5,
            threshold_target_multiplier=105,
        )
        for s in stores:
            sid = s.store_id
            order = await get_order_by_store(s)
            tap.ok(order, 'создали ордер')
            p2req = {r.product_id: r for r in order.required}
            tap.eq(len(p2req), 4, '4 required')
            tap.ok(ps[sid][0].product_id not in p2req, 'нету первого продукта')
            tap.ok(ps[sid][1].product_id not in p2req, 'нету второго продукта')
            cnts2_5 = [2*rands[sid], 2*rands[sid], 105, 105]
            for i in range(2, 6):
                tap.eq(
                    p2req[ps[sid][i].product_id].count,
                    cnts2_5[i-2],
                    f'ок {i+1} продукт',
                )
            for p in ps[sid]:
                await dataset.stock(
                    store=s,
                    product=p,
                    shelf_type='kitchen_components',
                    count=5,
                )
        await dataset.StoreStock.daemon(exit_at_endlog=True)

        async def wait_and_wait_order_status(order, sec=3):
            await asyncio.sleep(sec)
            await wait_order_status(order, ('canceled', 'done'))

        tasks = [
            asyncio.create_task(
                job_create_orders(
                    stores=[s.store_id for s in stores],
                    threshold_trigger_multiplier=5,
                    threshold_target_multiplier=105,
                )
            )
        ]
        for store in stores:
            order = await get_order_by_store(store)
            tasks.append(
                asyncio.create_task(wait_and_wait_order_status(order))
            )
        for task in reversed(tasks):
            await task

        for s in stores:
            sid = s.store_id
            order = await get_order_by_store(s)
            tap.ok(order, 'создали ордер')
            p2req = {r.product_id: r for r in order.required}
            tap.eq(len(p2req), 2, '2 required')
            tap.ok(ps[sid][0].product_id not in p2req, 'нету первого продукта')
            tap.ok(ps[sid][1].product_id not in p2req, 'нету второго продукта')
            tap.ok(
                ps[sid][3].product_id not in p2req, 'нету четвертого продукта'
            )
            tap.ok(ps[sid][5].product_id not in p2req, 'нету шестого продукта')
            cnts2_5 = [2*rands[sid], None, 105]
            for i in [2, 4]:
                tap.eq(
                    p2req[ps[sid][i].product_id].count,
                    cnts2_5[i-2] - 5,
                    f'ок {i+1} продукт',
                )
            await order.cancel()
            await wait_order_status(order, ('canceled', 'done'))
            for p in ps[sid]:
                await dataset.stock(
                    store=s,
                    product=p,
                    shelf_type='kitchen_components',
                    count=rands[sid] - 5,
                )
        await dataset.StoreStock.daemon(exit_at_endlog=True)

        await job_create_orders(
            stores=[s.store_id for s in stores],
            threshold_trigger_multiplier=5,
            threshold_target_multiplier=105,
        )

        for s in stores:
            order = await get_order_by_store(s)
            tap.ok(not order, 'не создали ордер')


@pytest.mark.parametrize(
    'params,expected_descs',  # каждый сток вложен в следующий
    [
        (
            {
                'additional': True,  # try_additional_generate
                'stocks': {1: 4},  # номер сабпродукта: его количество
                'message': 'берем единственный продукт до упора',
            },
            {1: 4}  # номер сабпродукта: его количество
        ),
        (
            {
                'additional': False,
                'stocks': {1: 6},
                'message': 'берем единственный продукт по порогам',
            },
            {1: 5}
        ),
        (
            {
                'additional': True,
                'stocks': {0: 20, 1: 6},
                'message': 'берем только первый вариант до упора',
            },
            {0: 20}
        ),
        (
            {
                'additional': False,
                'stocks': {0: 40, 1: 6},
                'message': 'не берем ничего, пороги не выполняются',
            },
            {}
        ),
        (
            {
                'additional': False,
                'stocks': {0: 51, 1: 6},
                'message': 'берем только первый вариант по порогам',
            },
            {0: 50}
        ),
        (
            {
                'additional': True,
                'stocks': {0: 51, 1: 6, 4: 56},
                'message': 'теперь берем сабпродукт[4] до упора',
            },
            {0: 50, 4: 56}
        ),
        (
            {
                'additional': True,
                'stocks': {0: 50, 1: 6, 2: 10, 3: 16, 4: 56},
                'message': 'набираем до упора что можем',
            },
            {0: 50, 2: 10, 3: 16}
        ),
        (
            {
                'additional': False,
                'stocks': {0: 50, 1: 6, 2: 10, 3: 20, 4: 65},
                'message': 'набираем по порогам что можем, без сп[4]',
            },
            {0: 50, 3: 20}
        ),
        (
            {
                'additional': False,
                'stocks': {0: 50, 1: 6, 2: 35, 3: 20, 4: 65},
                'message': 'насыщаем по порогам всё',
            },
            {0: 50, 2: 35, 3: 20}
        ),
    ]
)
async def test_order_descs_priorities(tap, dataset, params, expected_descs):
    with tap.plan(1, 'тестируем выбор приоритета'):
        store = await dataset.store()
        ps = [await dataset.product() for _ in range(2)]
        sps = [await dataset.product() for _ in range(5)]
        pcs0 = ProductComponents([
            [
                ProductVariant(product_id=sps[0].product_id, count=10),
                ProductVariant(product_id=sps[1].product_id, count=1),
            ],
            [
                ProductVariant(product_id=sps[2].product_id, count=7),
                ProductVariant(product_id=sps[3].product_id, count=4),
            ],
        ])
        ps[0].components = pcs0
        await ps[0].save()
        pcs1 = ProductComponents([
            [
                ProductVariant(product_id=sps[2].product_id, count=2),
                ProductVariant(product_id=sps[4].product_id, count=11),
            ],
            [
                ProductVariant(product_id=sps[3].product_id, count=3),
                ProductVariant(product_id=sps[4].product_id, count=13),
            ],
        ])
        ps[1].components = pcs1
        await ps[1].save()

        ass = await dataset.assortment()
        for p in ps:
            await dataset.assortment_product(
                product=p,
                assortment=ass,
            )
        store.kitchen_assortment_id = ass.assortment_id
        await store.save()

        for idx, cnt in params['stocks'].items():
            await dataset.stock(product=sps[idx], count=cnt, store=store)

        func_params = {
            'store': store,
            'threshold_trigger_multiplier': 1,
            'threshold_target_multiplier': 5,
            'try_additional_generate': params['additional'],
        }
        _, order_descs = await generate_order_conditions(**func_params)

        tap.note(params['message'])
        tap.eq(
            order_descs,
            {sps[idx].product_id: cnt for idx, cnt in expected_descs.items()},
            'ответ соответствует всем нашим смелым ожиданиям',
        )


async def test_job_func_fail_cancel(tap, dataset, cfg):
    cfg.set('business.kitchen_autorestocking.cycle_timeout', 2)
    with tap.plan(3, 'тестим фейл отмены предыдущего ордера'):
        store = await dataset.full_store(options={'exp_gargantua': True})
        ps = [await dataset.product() for _ in range(3)]
        ass = await dataset.kitchen_assortment()
        store.kitchen_assortment_id = ass.assortment_id
        await store.save()
        aps = {}
        for p in ps:
            p.components = ProductComponents(
                [[ProductVariant(
                    product_id=p.product_id, count=1,
                )]]
            )
            await p.save()
            aps[p.product_id] = (
                await dataset.assortment_product(
                    product=p,
                    assortment=ass,
                    trigger_threshold=10,
                    target_threshold=69,
                )
            )
            await dataset.stock(store=store, product=p, count=10000)

        await job_create_orders(
            stores=[store.store_id],
            threshold_trigger_multiplier=5,
            threshold_target_multiplier=105,
        )

        order = await get_order_by_store(store)
        tap.ok(order, 'создали ордер')
        await dataset.stock(
            store=store,
            product=ps[0],
            shelf_type='kitchen_components',
            count=5,
        )
        await dataset.StoreStock.daemon(exit_at_endlog=True)

        await job_create_orders(
            stores=[store.store_id],
            threshold_trigger_multiplier=5,
            threshold_target_multiplier=105,
        )

        await order.reload()
        tap.eq(order.target, 'canceled', 'цель canceled')
        tap.eq(order.status, 'reserving', 'ордер не двигался')
