from datetime import timedelta
import pytest
from stall.model.shelf import Shelf, SHELF_TYPES_TECH, SHELF_TYPES_KITCHEN_TECH
from stall.model.store import job_store_check_errors
from stall.model.zone import Zone


async def test_shelves(tap, now, dataset):
    store = await dataset.store()
    shelf1 = await dataset.shelf(store=store)
    for shelf_type in (
            'out',
            'incoming',
            'trash',
            'lost',
            'found',
            'markdown',
            'office',
            'repacking',
            'kitchen_components',
            'kitchen_on_demand',
            'kitchen_trash',
            'kitchen_lost',
            'kitchen_found',
            'parcel',
    ):
        await dataset.shelf(type=shelf_type, store=store)

    await dataset.zone(store=store,
                       effective_from='2021-02-01',
                       effective_till=now()+timedelta(days=2),
                       type='foot'
                       )

    assortment = await dataset.assortment()
    kitchen_assortment = await dataset.assortment()
    markdown_assortment = await dataset.assortment()
    price_list = await dataset.price_list()
    product_group = await dataset.product_group()
    store.assortment_id = assortment.assortment_id
    store.kitchen_assortment_id = kitchen_assortment.assortment_id
    store.markdown_assortment_id = markdown_assortment.assortment_id
    store.price_list_id = price_list.price_list_id
    store.group_id = product_group.group_id
    store.location = {'lon': 66.1, 'lat': 33.1}
    store.slug = 'some_slug'
    with tap.plan(2):
        errors = await store.check_errors()
        tap.eq_ok(errors, set(), 'Ошибок нет')

        shelf1.type = 'out'
        await shelf1.save()
        errors = await store.check_errors()
        tap.eq_ok(errors, {'shelf:store'}, 'Нет складской полки')


async def test_assortment(tap, now, dataset):
    store = await dataset.store()
    for shelf_type in (
            'out',
            'store',
            'trash',
            'lost',
            'found',
            'markdown',
            'office',
            'repacking',
            'kitchen_components',
            'kitchen_on_demand',
            'kitchen_trash',
            'kitchen_lost',
            'kitchen_found',
            'parcel',
            'incoming',
    ):
        await dataset.shelf(type=shelf_type, store=store)
    await dataset.zone(store=store,
                       effective_from='2021-02-01',
                       effective_till=now() + timedelta(days=2),
                       type='foot'
                       )
    assortment = await dataset.assortment()
    kitchen_assortment = await dataset.kitchen_assortment()
    price_list = await dataset.price_list()
    product_group = await dataset.product_group()
    store.group_id = product_group.group_id
    store.price_list_id = price_list.price_list_id
    store.location = {'lon': 66.1, 'lat': 33.1}
    store.slug = 'some_slug'
    with tap.plan(4):
        store.assortment_id = None
        store.kitchen_assortment_id = kitchen_assortment.assortment_id
        errors = await store.check_errors()
        tap.eq_ok(errors, {'assortment:none'}, 'Нет ассортимента')

        store.assortment_id = 'broken_id'
        errors = await store.check_errors()
        tap.eq_ok(errors, {'assortment:not_found'}, 'Не найден ассортимент')

        store.assortment_id = assortment.assortment_id
        errors = await store.check_errors()
        tap.eq_ok(errors, set(), 'Ошибок нет')

        assortment.status = 'disabled'
        await assortment.save()
        errors = await store.check_errors()
        tap.eq_ok(errors, {'assortment:disabled'}, 'Ассортимент disabled')


async def test_price_list(tap, now, dataset):
    store = await dataset.store()
    for shelf_type in (
            'out',
            'store',
            'trash',
            'lost',
            'found',
            'markdown',
            'office',
            'repacking',
            'kitchen_components',
            'kitchen_on_demand',
            'kitchen_trash',
            'kitchen_lost',
            'kitchen_found',
            'parcel',
            'incoming',
    ):
        await dataset.shelf(type=shelf_type, store=store)
    await dataset.zone(store=store,
                       effective_from='2021-02-01',
                       effective_till=now() + timedelta(days=2),
                       type='foot'
                       )

    assortment = await dataset.assortment()
    kitchen_assortment = await dataset.kitchen_assortment()
    price_list = await dataset.price_list()
    product_group = await dataset.product_group()
    store.assortment_id = assortment.assortment_id
    store.kitchen_assortment_id = kitchen_assortment.assortment_id
    store.group_id = product_group.group_id
    store.location = {'lon': 66.1, 'lat': 33.1}
    store.slug = 'some_slug'
    with tap.plan(4):
        errors = await store.check_errors()
        tap.eq_ok(errors, {'price_list:none'}, 'Нет прайслиста')

        store.price_list_id = 'broken_id'
        errors = await store.check_errors()
        tap.eq_ok(errors, {'price_list:not_found'}, 'Не найден прайслист')

        store.price_list_id = price_list.price_list_id
        errors = await store.check_errors()
        tap.eq_ok(errors, set(), 'Ошибок нет')

        price_list.status = 'disabled'
        await price_list.save()
        errors = await store.check_errors()
        tap.eq_ok(errors, {'price_list:disabled'}, 'Прайслист disabled')


async def test_product_group(tap, now, dataset):
    store = await dataset.store()
    for shelf_type in (
            'out',
            'store',
            'trash',
            'lost',
            'found',
            'markdown',
            'office',
            'repacking',
            'kitchen_components',
            'kitchen_on_demand',
            'kitchen_trash',
            'kitchen_lost',
            'kitchen_found',
            'parcel',
            'incoming',
    ):
        await dataset.shelf(type=shelf_type, store=store)
    await dataset.zone(store=store,
                       effective_from='2021-02-01',
                       effective_till=now() + timedelta(days=2),
                       type='foot'
                       )

    assortment = await dataset.assortment()
    kitchen_assortment = await dataset.kitchen_assortment()
    price_list = await dataset.price_list()
    product_group = await dataset.product_group()
    parent_product_group = await dataset.product_group()
    store.price_list_id = price_list.price_list_id
    store.assortment_id = assortment.assortment_id
    store.kitchen_assortment_id = kitchen_assortment.assortment_id
    store.location = {'lon': 66.1, 'lat': 33.1}
    store.slug = 'some_slug'
    with tap.plan(6):
        errors = await store.check_errors()
        tap.eq_ok(errors, {'product_group:none'}, 'Нет иерархии фронта')

        store.group_id = 'broken_id'
        errors = await store.check_errors()
        tap.eq_ok(errors, {'product_group:not_found'},
                  'Не найдена иерархия фронта')

        store.group_id = product_group.group_id
        errors = await store.check_errors()
        tap.eq_ok(errors, set(), 'Ошибок нет')

        product_group.status = 'disabled'
        await product_group.save()
        errors = await store.check_errors()
        tap.eq_ok(errors, {'product_group:disabled'}, 'Иерархия disabled')

        product_group.status = 'removed'
        await product_group.save()
        errors = await store.check_errors()
        tap.eq_ok(errors, {'product_group:removed'}, 'Иерархия removed')

        product_group.status = 'active'
        product_group.parent_group_id = parent_product_group.group_id
        await product_group.save()
        errors = await store.check_errors()
        tap.eq_ok(errors, {'product_group:has_parent'}, 'Иерархия has_parent')


async def test_location_zone(tap, now, dataset):
    store = await dataset.store(location=None)
    for shelf_type in (
            'out',
            'store',
            'trash',
            'lost',
            'found',
            'markdown',
            'office',
            'repacking',
            'kitchen_components',
            'kitchen_on_demand',
            'kitchen_trash',
            'kitchen_lost',
            'kitchen_found',
            'parcel',
            'incoming',
    ):
        await dataset.shelf(type=shelf_type, store=store)
    zones = await Zone.list(
        by='full',
        conditions=[
            ('store_id', store.store_id),
        ],
        sort=(),
    )
    zone1 = zones.list[0]
    zone1.effective_till = now() - timedelta(days=2)
    await zone1.save()

    assortment = await dataset.assortment()
    kitchen_assortment = await dataset.assortment()
    price_list = await dataset.price_list()
    product_group = await dataset.product_group()
    store.assortment_id = assortment.assortment_id
    store.kitchen_assortment_id = kitchen_assortment.assortment_id
    store.price_list_id = price_list.price_list_id
    store.group_id = product_group.group_id
    store.slug = 'some_slug'

    with tap.plan(4):
        errors = await store.check_errors()
        tap.eq_ok(errors, {'location', 'zone:not_found'}, 'Нет локации и зоны')

        store.location = {'lon': 66.1, 'lat': 33.1}
        errors = await store.check_errors()
        tap.eq_ok(errors, {'zone:not_found'}, 'Нет зоны')

        real_zone = await dataset.zone(
            store=store,
            effective_from='2021-02-01',
            effective_till=now() + timedelta(days=2),
            type='foot',
            status='disabled',
        )

        errors = await store.check_errors()
        tap.eq_ok(errors, {'zone:not_active'}, 'Зона не активна')

        real_zone.status = 'active'
        await real_zone.save()
        errors = await store.check_errors()
        tap.eq_ok(errors, set(), 'Ошибок нет')


async def test_slug(tap, now, dataset):
    store = await dataset.store()
    for shelf_type in (
            'out',
            'store',
            'trash',
            'lost',
            'found',
            'markdown',
            'office',
            'repacking',
            'kitchen_components',
            'kitchen_on_demand',
            'kitchen_trash',
            'kitchen_lost',
            'kitchen_found',
            'parcel',
            'incoming',
    ):
        await dataset.shelf(type=shelf_type, store=store)
    await dataset.zone(store=store,
                       effective_from='2021-02-01',
                       effective_till=now() + timedelta(days=2),
                       type='foot'
                       )

    assortment = await dataset.assortment()
    kitchen_assortment = await dataset.assortment()
    price_list = await dataset.price_list()
    product_group = await dataset.product_group()
    store.assortment_id = assortment.assortment_id
    store.kitchen_assortment_id = kitchen_assortment.assortment_id
    store.price_list_id = price_list.price_list_id
    store.group_id = product_group.group_id
    store.location = {'lon': 66.1, 'lat': 33.1}

    with tap.plan(2):
        errors = await store.check_errors()
        tap.eq_ok(errors, {'slug'}, 'Нет slug')
        store.slug = 'some_slug'
        errors = await store.check_errors()
        tap.eq_ok(errors, set(), 'Ошибок нет')


@pytest.mark.parametrize('shelves,kitchen,options,errors', [
    (
        ['incoming', 'store', 'out', 'trash', 'lost', 'found', 'office',
         'markdown', 'parcel', 'repacking',
         'kitchen_components', 'kitchen_on_demand', 'kitchen_trash',
         'kitchen_lost', 'kitchen_found'],
        True,
        {'check_valid_use_markdown': True, 'tristero': True},
        set(),
    ),
    (
        [],
        True,
        {'check_valid_use_markdown': True, 'tristero': True},
        {'shelf:store', 'shelf:office', 'shelf:markdown',
         'shelf:parcel', 'shelf:repacking', 'shelf:kitchen_components'},
    ),
    (
        ['incoming', 'store', 'out', 'trash', 'lost', 'found', 'office',
         'repacking', 'kitchen_components', 'kitchen_on_demand',
         'kitchen_lost', 'kitchen_found', 'kitchen_trash'],
        True,
        {'check_valid_use_markdown': True, 'tristero': True},
        {'shelf:markdown', 'shelf:parcel'},
    ),
    (
        ['incoming', 'store', 'out', 'trash', 'lost', 'found', 'office',
         'repacking', 'kitchen_components', 'kitchen_on_demand',
         'kitchen_lost', 'kitchen_found', 'kitchen_trash'],
        True,
        {'check_valid_use_markdown': False, 'tristero': False},
        set(),
    ),
    (
        ['incoming', 'store', 'out', 'trash', 'lost',
         'found', 'office', 'repacking'],
        True,
        {'check_valid_use_markdown': False, 'tristero': False},
        {'shelf:kitchen_components'},
    ),
    (
        ['incoming', 'store', 'out', 'trash', 'lost',
         'found', 'office', 'repacking'],
        False,
        {'check_valid_use_markdown': False, 'tristero': False},
        set(),
    ),
])
async def test_shelves_conditional(tap, now, dataset, shelves,
                                   kitchen, options, errors):
    store = await dataset.store(options=options)
    await dataset.zone(store=store,
                       effective_from='2021-02-01',
                       effective_till=now() + timedelta(days=2),
                       type='foot'
                       )
    for shelf_type in shelves:
        await dataset.shelf(type=shelf_type, store=store)

    assortment = await dataset.assortment()
    kitchen_assortment = await dataset.assortment()
    price_list = await dataset.price_list()
    product_group = await dataset.product_group()
    store.assortment_id = assortment.assortment_id
    if kitchen:
        store.kitchen_assortment_id = kitchen_assortment.assortment_id
    store.price_list_id = price_list.price_list_id
    store.group_id = product_group.group_id
    store.location = {'lon': 66.1, 'lat': 33.1}
    store.slug = 'some_slug'
    with tap:
        actual_errors = await store.check_errors()
        tap.eq_ok(actual_errors, errors, 'Ожидаемые ошибки')


async def test_location_zone_none(tap, now, dataset):
    store = await dataset.store(location=None)

    for shelf_type in (
            'out',
            'store',
            'trash',
            'lost',
            'found',
            'markdown',
            'office',
            'repacking',
            'kitchen_components',
            'kitchen_on_demand',
            'kitchen_trash',
            'kitchen_lost',
            'kitchen_found',
            'parcel',
            'incoming',
    ):
        await dataset.shelf(type=shelf_type, store=store)
    zones = await Zone.list(
        by='full',
        conditions=[
            ('store_id', store.store_id),
        ],
    )
    zone1 = zones.list[0]
    zone1.effective_till = now() - timedelta(days=2)
    await zone1.save()

    assortment = await dataset.assortment()
    kitchen_assortment = await dataset.assortment()
    price_list = await dataset.price_list()
    product_group = await dataset.product_group()
    store.assortment_id = assortment.assortment_id
    store.kitchen_assortment_id = kitchen_assortment.assortment_id
    store.price_list_id = price_list.price_list_id
    store.group_id = product_group.group_id
    store.slug = 'some_slug'

    with tap.plan(3):
        errors = await store.check_errors()
        tap.eq_ok(errors, {'location', 'zone:not_found'}, 'Нет локации и зоны')

        store.location = {'lon': 66.1, 'lat': 33.1}
        errors = await store.check_errors()
        tap.eq_ok(errors, {'zone:not_found'}, 'Нет зоны')

        await dataset.zone(store=store,
                           status='active',
                           effective_from='2021-02-01',
                           effective_till=None,
                           type='foot'
                           )

        errors = await store.check_errors()
        tap.eq_ok(errors, set(), 'Ошибок нет')


async def test_create_shelves(tap, dataset):
    # pylint: disable=too-many-locals,too-many-statements
    with tap.plan(67, 'проверяем автоматическое создание полок'):
        store = await dataset.store(errors=['zhopka'])
        store_fr = await dataset.store(lang='fr_FR')
        shelves = await Shelf.list_by_store(store_id=store.store_id)
        shelf_types = {s.type for s in shelves}
        shelves_fr = await Shelf.list_by_store(store_id=store_fr.store_id)
        shelf_types_fr = {s.type for s in shelves_fr}

        for t in SHELF_TYPES_TECH + SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t not in shelf_types, f'нет полки {t}')
            tap.ok(t not in shelf_types_fr, f'нет полки {t} в fr')

        await job_store_check_errors(store.store_id, ['check_shelves'])
        await job_store_check_errors(store_fr.store_id, ['check_shelves'])
        await store.reload()
        tap.ok('zhopka' in store.errors, 'проверяем корректность мержа ошибок')
        shelves = await Shelf.list_by_store(store_id=store.store_id)
        shelf_types = {s.type for s in shelves}
        shelves_fr = await Shelf.list_by_store(store_id=store_fr.store_id)
        shelf_types_fr = {s.type for s in shelves_fr}
        for t in SHELF_TYPES_TECH:
            tap.ok(t in shelf_types, f'есть полка {t}')
            tap.ok(t in shelf_types_fr, f'есть полка {t} в fr')
        for t in SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t not in shelf_types, f'нет полки {t}')
            tap.ok(t not in shelf_types, f'нет полки {t} в fr')

        await dataset.shelf(store=store, type='kitchen_components')
        await dataset.shelf(store=store_fr, type='kitchen_components')

        await job_store_check_errors(store.store_id, ['check_shelves'])
        await job_store_check_errors(store_fr.store_id, ['check_shelves'])
        shelves = await Shelf.list_by_store(store_id=store.store_id)
        shelf_types = {s.type for s in shelves}
        shelves_fr = await Shelf.list_by_store(store_id=store_fr.store_id)
        shelf_types_fr = {s.type for s in shelves_fr}
        for t in SHELF_TYPES_TECH + SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t in shelf_types, f'есть полка {t}')
            tap.ok(t in shelf_types_fr, f'есть полка {t} в fr')

        kitchen_on_demand = [
            s for s in shelves if s.type == 'kitchen_on_demand'
        ][0]
        kitchen_on_demand_fr = [
            s for s in shelves_fr if s.type == 'kitchen_on_demand'
        ][0]
        tap.eq(kitchen_on_demand.title, 'Выдача Кухни', 'название ок')
        tap.eq(kitchen_on_demand.rack, 'Выдача Кухни', 'стеллаж ок')
        tap.eq(kitchen_on_demand_fr.title, 'release - sortie', 'название ок fr')
        tap.eq(kitchen_on_demand_fr.rack, 'release', 'стеллаж ок fr')

        trash = [s for s in shelves if s.type == 'trash'][0]
        trash_fr = [s for s in shelves_fr if s.type == 'trash'][0]
        ktrash = [s for s in shelves if s.type == 'kitchen_trash'][0]
        ktrash_fr = [s for s in shelves_fr if s.type == 'kitchen_trash'][0]

        tap.eq(trash.title, 'СПИСАНИЕ', 'название ок')
        tap.eq(trash.rack, 'СПИСАНИЕ', 'стеллаж ок')
        tap.eq(trash_fr.title, 'WRITE_OFF', 'название ок fr')
        tap.eq(trash_fr.rack, 'WRITE_OFF', 'стеллаж ок fr')
        tap.eq(ktrash.title, 'ПФ-Списание', 'название ок')
        tap.eq(ktrash.rack, 'СПИСАНИЕ', 'стеллаж ок')
        tap.eq(ktrash_fr.title, 'KITCHEN_WRITE_OFF', 'название ок fr')
        tap.eq(ktrash_fr.rack, 'WRITE_OFF', 'стеллаж ок fr')


async def test_activate_shelves(tap, dataset):
    with tap.plan(35, 'тестим активацию полок'):
        store = await dataset.store(status='repair')
        shelves = await Shelf.list_by_store(
            store_id=store.store_id, status='active'
        )
        shelf_types = {s.type for s in shelves}
        for t in SHELF_TYPES_TECH + SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t not in shelf_types, f'нет полки {t}')
        add_shelves = []
        for t in SHELF_TYPES_TECH[:2] + SHELF_TYPES_KITCHEN_TECH[:2]:
            add_shelves.append(
                await dataset.shelf(store=store, type=t, status='disabled')
            )
        await job_store_check_errors(store.store_id, ['check_shelves'])
        shelves = await Shelf.list_by_store(
            store_id=store.store_id, status='active'
        )
        shelf_types = {s.type for s in shelves}
        for t in SHELF_TYPES_TECH + SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t not in shelf_types, f'нет полки {t}')

        await store.reload()
        store.status = 'active'
        await dataset.shelf(store=store, type='kitchen_components')
        await store.save()
        await job_store_check_errors(store.store_id, ['check_shelves'])
        shelves = await Shelf.list_by_store(
            store_id=store.store_id, status='active'
        )
        shelf_types = {s.type for s in shelves}
        for t in SHELF_TYPES_TECH[:2] + SHELF_TYPES_KITCHEN_TECH[:2]:
            tap.ok(t in shelf_types, f'есть полка {t}')
        tap.eq(
            [s for s in shelves if s.type == 'incoming'][0].shelf_id,
            add_shelves[0].shelf_id,
            'активировали полку incoming'
        )
        tap.eq(
            [s for s in shelves if s.type == 'out'][0].shelf_id,
            add_shelves[1].shelf_id,
            'активировали полку out'
        )
        tap.eq(
            [s for s in shelves if s.type == 'kitchen_on_demand'][0].shelf_id,
            add_shelves[2].shelf_id,
            'активировали полку kitchen_on_demand'
        )
        tap.eq(
            [s for s in shelves if s.type == 'kitchen_trash'][0].shelf_id,
            add_shelves[3].shelf_id,
            'активировали полку kitchen_trash'
        )
        for t in SHELF_TYPES_TECH + SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t in shelf_types, f'есть полка {t}')
