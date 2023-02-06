from stall.model.shelf import Shelf, import_data, process_import


async def test_create(tap, dataset):
    with tap.plan(17):
        store = await dataset.store()
        user = await dataset.user(store=store)

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'пиво',
                        'barcode': 'xxx',
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'шампусик',
                        'order': 1,
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'вино',
                        'type': 'markdown',
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'водка',
                        'tag': 'freezer',
                    },
                ],
            }
        )

        await import_data(s.stash_id)

        shelves = {
            i.title: i
            for i in await Shelf.list_by_store(store_id=store.store_id)
        }

        tap.eq_ok(len(shelves), 4, 'все полки импортированы')

        tap.eq_ok(shelves['пиво'].barcode, 'xxx', 'barcode')
        tap.eq_ok(shelves['пиво'].order, 0, 'order')
        tap.eq_ok(shelves['пиво'].type, 'store', 'type')
        tap.eq_ok(shelves['пиво'].tags, [], 'tags')

        tap.ok(shelves['шампусик'].barcode, 'barcode')
        tap.eq_ok(shelves['шампусик'].order, 1, 'order')
        tap.eq_ok(shelves['шампусик'].type, 'store', 'type')
        tap.eq_ok(shelves['шампусик'].tags, [], 'tags')

        tap.ok(shelves['вино'].barcode, 'barcode')
        tap.eq_ok(shelves['вино'].order, 0, 'order')
        tap.eq_ok(shelves['вино'].type, 'markdown', 'type')
        tap.eq_ok(shelves['вино'].tags, [], 'tags')

        tap.ok(shelves['водка'].barcode, 'barcode')
        tap.eq_ok(shelves['водка'].order, 0, 'order')
        tap.eq_ok(shelves['водка'].type, 'store', 'type')
        tap.eq_ok(shelves['водка'].tags, ['freezer'], 'tags')


async def test_update(tap, dataset):
    with tap.plan(9):
        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.shelf(
            store=store,
            rack='алко-стеллаж',
            title='пиво',
            barcode='xxx',
        )

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'пиво',
                        'order': 2,
                        'tag': 'freezer'
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'вино',
                        'barcode': 'b1',
                        'order': 3,
                    },
                ],
            }
        )

        await import_data(s.stash_id)

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        tap.eq_ok(len(shelves), 2, 'все полки импортированы')

        shelves = {i.title: i for i in shelves}

        tap.eq_ok(shelves['пиво'].barcode, 'xxx', 'barcode')
        tap.eq_ok(shelves['пиво'].order, 2, 'order')
        tap.eq_ok(shelves['пиво'].tags, ['freezer'], 'tags')
        tap.eq_ok(shelves['пиво'].type, 'store', 'type')

        tap.eq_ok(shelves['вино'].barcode, 'b1', 'barcode')
        tap.eq_ok(shelves['вино'].order, 3, 'order')
        tap.eq_ok(shelves['вино'].tags, [], 'tags')
        tap.eq_ok(shelves['вино'].type, 'store', 'type')


async def test_barcode_dupe(tap, dataset, uuid):
    with tap.plan(4, 'проверяем баркоды на дубли'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        barcode = uuid()

        shelf = await dataset.shelf(
            store=store,
            rack='алко-стеллаж',
            title=uuid(),
            barcode=barcode,
        )

        tap.eq(shelf.barcode, barcode, 'создали полку с баркодом')

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': uuid(),
                        'barcode': barcode,
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': uuid(),
                        'barcode': barcode,
                    },
                ],
            }
        )

        await import_data(s.stash_id)

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        tap.eq_ok(len(shelves), 1, 'полка должны быть одна')

        error_stashes = await dataset.Stash.list(
            by='full',
            conditions=('group', f'error:{s.stash_id}')
        )
        tap.eq(len(error_stashes.list), 1, 'Одна ошибка')
        tap.eq(
            error_stashes.list[0].value.get('code'),
            'ER_BARCODE_DUPLICATED',
            'Ошибка про баркоды'
        )


async def test_shelf_with_stocks(tap, dataset):
    with tap.plan(10, 'Среди полок есть полка с остатками'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf_one = await dataset.shelf(
            store=store,
            rack='клевый-стеллаж',
            type='markdown'
        )
        tap.ok(shelf_one, 'Первая полка')
        shelf_two = await dataset.shelf(
            store=store,
            rack='с-остатками',
            type='markdown'
        )
        tap.ok(shelf_two, 'Вторая полка')
        tap.ok(await dataset.stock(shelf=shelf_two, count=1), 'Остатки')

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': 'клевый-стеллаж',
                        'type': 'store',
                        'shelf': shelf_one.title,
                    },
                    {
                        'rack': 'с-остатками',
                        'type': 'store',
                        'shelf': shelf_two.title,
                    },
                ],
            }
        )

        await import_data(s.stash_id)

        tap.ok(await shelf_one.reload(), 'Забрали первую полку')
        tap.eq(shelf_one.type, 'markdown', 'Остался тип')

        tap.ok(await shelf_two.reload(), 'Забрали вторую полку')
        tap.eq(shelf_one.type, 'markdown', 'Остался старый тип')

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        tap.eq_ok(len(shelves), 2, 'Две полки всего')

        error_stashes = await dataset.Stash.list(
            by='full',
            conditions=('group', f'error:{s.stash_id}')
        )
        tap.eq(len(error_stashes.list), 1, 'Одна ошибка ')
        tap.eq(
            error_stashes.list[0].value.get('code'),
            'ER_SHELF_WITH_STOCKS',
            'Ошибка про остатки'
        )


async def test_get_by_type_list_and_tuple(tap, dataset):
    with tap.plan(2):
        store = await dataset.store()
        user = await dataset.user(store=store)

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'вино',
                        'type': 'office',
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'пиво',
                        'type': 'trash',
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'виски',
                        'type': 'markdown',
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'коньяк',
                        'type': 'parcel',
                    },
                ],
            }
        )

        await import_data(s.stash_id)

        shelves = {
            i.title: i
            for i in await Shelf.list_by_store(store_id=store.store_id)
        }

        tap.eq_ok(len(shelves), 4, 'все полки импортированы')

        shelves_tuple = {
            i.title: i
            for i in await Shelf.list_by_store(
                store_id=store.store_id,
                type=('markdown', 'office')
            )
        }

        shelves_list = {
            i.title: i
            for i in await Shelf.list_by_store(store_id=store.store_id,
                                               type=['trash', 'parcel'])
        }

        tap.eq_ok(len(shelves),
                  len(shelves_list) + len(shelves_tuple),
                  'запрос по списку или кортежу работает')


async def test_shelf_by_external(tap, dataset):
    with tap.plan(8, 'Создание и изменение полок по external'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        first_shelf_eid = 'hell yeah'
        second_shelf_eid = 'amazed'

        stash = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'пиво',
                        'barcode': 'xxx',
                        'external_id': first_shelf_eid,
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'пиво',
                        'order': 1,
                        'external_id': second_shelf_eid,
                        'barcode': 'yyy',
                    },
                ],
            }
        )

        await import_data(stash.stash_id)

        shelves = {
            shelf.external_id: shelf
            for shelf in await Shelf.list_by_store(store_id=store.store_id)
        }
        tap.eq(len(shelves), 2, 'Две полки')

        shelf_one = shelves[first_shelf_eid]
        tap.eq(shelf_one.external_id, first_shelf_eid, 'External')
        tap.eq(shelf_one.title, 'пиво', 'Title')

        shelf_two = shelves[second_shelf_eid]
        tap.eq(shelf_two.external_id, second_shelf_eid, 'External')
        tap.eq(shelf_two.title, 'пиво', 'Title')

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'рыба',
                        'external_id': first_shelf_eid,
                    },
                ],
            }
        )

        await import_data(s.stash_id)

        tap.ok(await shelf_one.reload(), 'Перезабрали полку')
        tap.eq(shelf_one.external_id, first_shelf_eid, 'External')
        tap.eq(shelf_one.title, 'рыба', 'title обновлен')


async def test_title_duplicate(tap, dataset):
    with tap.plan(5, 'Дубли title'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        shelves = [
            await dataset.shelf(
                store=store,
                title='сидр',
            )
            for _ in range(4)
        ]
        tap.ok(all(shelves), 'Несколько полок')

        stash = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': 'новый мой стеллаж',
                        'shelf': 'сидр',
                    },
                ],
            }
        )

        await import_data(stash.stash_id)

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        tap.eq(len(shelves), 4, '4 старые полки')

        tap.ok(
            all(
                shelf.rack != 'новый мой стеллаж'
                for shelf in shelves
            ),
            'Никто не получил новый стеллаж'
        )
        error_stashes = await dataset.Stash.list(
            by='full',
            conditions=('group', f'error:{stash.stash_id}')
        )
        tap.eq(len(error_stashes.list), 1, 'Одна ошибка')
        tap.eq(
            error_stashes.list[0].value.get('code'),
            'ER_TITLE_DUPLICATED',
            'Ошибка про дубли'
        )


async def test_idempotency(tap, dataset):
    with tap.plan(13, 'Проверка идемпотентности'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        second_shelf_eid = 'awesomeeid'

        shelf = await dataset.shelf(
            store=store,
            title='сидр',
            barcode='xxx',
            order=3,
            status='active',
            rack='плохой стеллаж',
        )
        tap.ok(shelf, 'Полка для склада')

        stash = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': 'хороший стеллаж',
                        'shelf': 'сидр',
                        'barcode': 'xxx',
                        'external_id': shelf.external_id,
                        'order': 4,
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'водка',
                        'external_id': '',
                        'barcode': 'yyy',
                    },
                    {
                        'rack': 'алко-стеллаж',
                        'shelf': 'медовуха',
                        'external_id': second_shelf_eid,
                        'barcode': 'zzz',
                    },
                ],
            }
        )

        result = await process_import(stash)
        tap.ok(not result, 'Не было ошибок')

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        tap.eq(len(shelves), 3, 'Теперь три полки')

        result = await process_import(stash)
        tap.ok(not result, 'Повторно без ошибок')

        shelves = {
            shelf.title: shelf
            for shelf in await Shelf.list_by_store(store_id=store.store_id)
        }
        tap.eq(len(shelves), 3, 'Три полки')
        first_shelf = shelves.get('сидр')
        tap.ok(first_shelf, 'Первая полка есть')
        tap.eq(first_shelf.rack, 'хороший стеллаж', 'обновился стеллаж')
        tap.eq(first_shelf.order, 4, 'порядок обновился')

        second_shelf = shelves.get('водка')
        tap.ok(second_shelf, 'Вторая полка без external создалась')
        tap.eq(second_shelf.barcode, 'yyy', 'Правильный баркод')

        third_shelf = shelves.get('медовуха')
        tap.ok(third_shelf, 'Третья полка создалась')
        tap.eq(third_shelf.barcode, 'zzz', 'Правильный баркод')
        tap.eq(third_shelf.external_id, second_shelf_eid, 'External тот')


async def test_switching_titles(tap, dataset):
    with tap.plan(6, 'Проверка перестановки названий'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf_one = await dataset.shelf(
            store=store,
            title='сидр',
        )
        tap.ok(shelf_one, 'Полка сидр для склада')

        shelf_two = await dataset.shelf(
            store=store,
            title='пиво',
        )
        tap.ok(shelf_two, 'Полка пиво для склада')

        stash = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'rack': shelf_one.rack,
                        'shelf': 'пиво',
                        'external_id': shelf_one.external_id,
                    },
                    {
                        'rack': shelf_two.rack,
                        'shelf': 'сидр',
                        'external_id': shelf_two.external_id,
                    },
                ],
            }
        )

        await import_data(stash.stash_id)
        tap.ok(await shelf_one.reload(), 'Перезабрали первую полку')
        tap.eq(shelf_one.title, 'пиво', 'Поменялось название')
        tap.ok(await shelf_two.reload(), 'Перезабрали вторую полку')
        tap.eq(shelf_two.title, 'сидр', 'Поменялось название')


async def test_duplication_bug(tap, dataset, uuid):
    with tap.plan(
        8, 'Создаем полку с тем же названием, но другим external_id'
    ):
        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.shelf(
            store=store,
            rack='алко-стеллаж',
            title='пиво',
            barcode='xxx',
        )

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'rows': [
                    {
                        'external_id': uuid(),
                        'rack': 'алко-стеллаж',
                        'shelf': 'пиво',
                        'order': 2,
                        'tag': 'freezer'
                    }
                ],
            }
        )

        await import_data(s.stash_id)

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        tap.eq_ok(len(shelves), 1, 'новыя полка не создалась')

        tap.eq_ok(shelves[0].title, 'пиво', 'title')
        tap.eq_ok(shelves[0].barcode, 'xxx', 'barcode')
        tap.eq_ok(shelves[0].order, 0, 'order')
        tap.eq_ok(shelves[0].tags, [], 'tags')
        tap.eq_ok(shelves[0].type, 'store', 'type')

        error_stashes = await dataset.Stash.list(
            by='full',
            conditions=('group', f'error:{s.stash_id}')
        )
        tap.eq(len(error_stashes.list), 1, 'Одна ошибка')
        tap.eq(
            error_stashes.list[0].value.get('code'),
            'ER_TITLE_DUPLICATED',
            'Ошибка про дубли'
        )

