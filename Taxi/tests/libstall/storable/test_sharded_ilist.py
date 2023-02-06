from libstall import cfg
from tests.libstall.storable.record import ShardedRecord


async def test_not_supported_types(tap):
    with tap:
        with tap.raises(NotImplementedError, 'No supported type'):
            async for i in ShardedRecord.ilist():
                print(i)

        with tap.raises(NotImplementedError, 'No supported type'):
            async for i in ShardedRecord.ilist(by='full'):
                print(i)


async def test_look_desc(tap, uuid):
    value = uuid()
    with tap:
        items = []
        for _ in range(10):
            item = ShardedRecord({'value': value})
            await item.save()
            items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.serial, reverse=True)

        xitems = []
        async for xitem in ShardedRecord.ilist(
                by='look',
                conditions=('value', value),
                limit=5,
        ):
            xitems.append(xitem)

        tap.eq_ok(
            [xi.serial for xi in xitems],
            [i.serial for i in items[:5]],
            'list look with limit',
        )

        xitems = []
        async for xitem in ShardedRecord.ilist(
                by='look',
                conditions=('value', value),
        ):
            xitems.append(xitem)

        tap.eq_ok(
            [xi.serial for xi in xitems],
            [i.serial for i in items],
            'list look with no limit',
        )


async def test_look_asc(tap, uuid):
    value = uuid()
    with tap:
        items = []
        for _ in range(10):
            item = ShardedRecord({'value': value})
            await item.save()
            items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.serial)

        xitems = []
        async for xitem in ShardedRecord.ilist(
                by='look',
                conditions=('value', value),
                direction='ASC',
                limit=5,
        ):
            xitems.append(xitem)

        tap.eq_ok(
            [xi.serial for xi in xitems],
            [i.serial for i in items[:5]],
            'list look with limit',
        )

        xitems = []
        async for xitem in ShardedRecord.ilist(
                by='look',
                conditions=('value', value),
                direction='ASC',
        ):
            xitems.append(xitem)

        tap.eq_ok(
            [xi.serial for xi in xitems],
            [i.serial for i in items],
            'list look with no limit',
        )


async def test_more_than_limit(tap, uuid):
    value = uuid()
    items = []
    for _ in range(int(cfg('cursor.limit')) + 5):
        item = ShardedRecord({'value': value})
        await item.save()
        items.append(item)

    xitems = []
    async for xitem in ShardedRecord.ilist(
            by='look', conditions=('value', value),
    ):
        xitems.append(xitem)

    tap.eq_ok(len(xitems), len(items), 'ok')


async def test_walk_asc(tap, uuid):
    with tap.plan(2, 'Проверяем проход используя walk'):
        value = uuid()

        items = []
        for _ in range(10):
            with ShardedRecord({'value': value}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: x.serial)

        xitems = []
        async for xitem in ShardedRecord.ilist(
                by='walk',
                conditions=('value', value),
                sort=[('serial', 'ASC')],
                limit=5,
        ):
            xitems.append(xitem)

        tap.eq_ok(
            [x.serial for x in xitems],
            [x.serial for x in items[:5]],
            'list walk with limit',
        )

        xitems = []
        async for xitem in ShardedRecord.ilist(
                by='walk',
                conditions=('value', value),
                sort=[('serial', 'ASC')],
        ):
            xitems.append(xitem)

        tap.eq_ok(
            [x.serial for x in xitems],
            [x.serial for x in items],
            'list walk with no limit',
        )
