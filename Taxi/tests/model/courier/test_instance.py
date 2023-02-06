import pytest

from stall.model.courier import Courier
from stall.model.courier_block import CourierBlock


async def test_instance(tap, uuid):
    with tap.plan(15, 'Создание курьера'):
        external_id = uuid()
        user_id = uuid()
        reason_1 = uuid()
        reason_2 = uuid()
        store_id = uuid()

        courier = Courier({
            'external_id': external_id,
            'first_name': 'Михаил',
            'middle_name': 'Михайлович',
            'last_name': 'Михайлов',
            'blocks': [
                CourierBlock({'source': 'eda', 'reason': reason_1}),
                CourierBlock({'source': 'wms', 'reason': reason_2}),
            ],
            'tags': ['auto', 'velo'],
            'tags_store': [store_id],
            'user_id': user_id,
        })
        tap.ok(courier, 'Объект создан')
        tap.eq(courier.external_id, external_id, 'external_id')
        tap.eq(courier.first_name, 'Михаил', 'first_name')
        tap.eq(courier.middle_name, 'Михайлович', 'middle_name')
        tap.eq(courier.last_name, 'Михайлов', 'last_name')

        # блокировки
        blocks = sorted(courier.blocks, key=lambda x: x['source'])
        tap.eq_ok(len(blocks), 2, '2 блокировки')
        tap.eq_ok(blocks[0]['source'], 'eda', 'блокировка еды')
        tap.eq_ok(blocks[0]['reason'], courier.blocks[0].reason, 'причина')
        tap.eq_ok(blocks[1]['source'], 'wms', 'блокировка еды')
        tap.eq_ok(blocks[1]['reason'], courier.blocks[1].reason, 'причина')

        tap.eq(courier.tags, ['auto', 'velo'], 'tags')
        tap.eq(courier.tags_store, [store_id], 'tags_store')
        tap.eq(courier.user_id, user_id, 'user_id')

        tap.ok(await courier.save(), 'сохранение')
        tap.ok(await courier.save(), 'обновление')


@pytest.mark.parametrize('blocks', (None, []))
async def test_field_blocks(tap, uuid, blocks):
    with tap.plan(7, 'Создание курьера'):
        external_id = uuid()
        courier = Courier({
            'external_id': external_id,
            'blocks': blocks,
        })
        tap.ok(courier, 'Объект создан')
        tap.eq(courier.external_id, external_id, 'external_id')

        tap.ok(await courier.save(), 'сохранение')
        with await courier.reload() as c:
            tap.eq(c.blocks, [], 'создан пустой список')

        tap.ok(await courier.save(), 'обновление')
        with await courier.reload() as c:
            tap.eq(c.blocks, [], 'список пуст')

        courier.rehash({'blocks': None})     # 'пробуем занулить'
        with await courier.reload() as c:
            tap.eq(c.blocks, [], 'пустой список')


async def test_dataset(tap, dataset):
    with tap.plan(1, 'Создание курьера из dataset'):
        courier = await dataset.courier()
        tap.ok(courier, 'объект создан')


async def test_fullname(tap, uuid):
    with tap.plan(5, 'Полное имя'):

        with Courier({
                'external_id': uuid(),
                'first_name': 'Роман',
                'middle_name': 'Владимирович',
                'last_name': 'Николаев',
        }) as courier:
            tap.eq(courier.fullname, 'Николаев Роман Владимирович', 'fullname')

        with Courier({
                'external_id': uuid(),
                'first_name': 'Роман',
                'last_name': 'Николаев',
        }) as courier:
            tap.eq(courier.fullname, 'Николаев Роман', 'first_name + last_name')

        with Courier({
                'external_id': uuid(),
                'first_name': 'Роман',
        }) as courier:
            tap.eq(courier.fullname, 'Роман', 'first_name')

        with Courier({
                'external_id': uuid(),
                'last_name': 'Николаев',
        }) as courier:
            tap.eq(courier.fullname, 'Николаев', 'last_name')

        with Courier({
                'external_id': uuid(),
                'middle_name': 'Владимирович',
        }) as courier:
            tap.eq(courier.fullname, 'Владимирович', 'middle_name')


async def test_job_sync_courier_tags_str(tap, dataset, uuid):
    with tap.plan(3, 'Проверка работы джобы sync_courier_tags'):
        cluster = await dataset.cluster()
        tags = sorted([
            (await dataset.courier_shift_tag(type='courier')).title,
            (await dataset.courier_shift_tag(type='courier')).title,
        ])
        courier = await dataset.courier(cluster=cluster, tags=tags)
        target_shifts = [
            await dataset.courier_shift(
                courier=courier,
                cluster=cluster,
                status='waiting',
                courier_tags=[uuid()],  # какой-то тег
            ),
            await dataset.courier_shift(
                courier=courier,
                cluster=cluster,
                status='waiting',
                courier_tags=None,      # смена назначена ДО появления тегов
            ),
            await dataset.courier_shift(
                courier=courier,
                cluster=cluster,
                status='waiting',
                courier_tags=[],        # курьер был без тега
            ),
            await dataset.courier_shift(
                courier=courier,
                cluster=cluster,
                status='waiting',
                courier_tags=tags,      # теги уже на месте
            ),
        ]

        # неподходящие статусы
        tags_2 = [(await dataset.courier_shift_tag(type='courier')).title]
        ignored_shifts = [
            await dataset.courier_shift(
                status=status,
                courier=courier,
                courier_tags=tags_2,
            )
            for status in ('processing', 'complete', 'leave', 'released')
        ]
        # чужого курьера
        courier_2 = await dataset.courier(cluster=cluster, tags=tags_2)
        ignored_shifts += [
            await dataset.courier_shift(
                status='waiting',
                courier=courier_2,
                courier_tags=tags_2,
            )
        ]
        # никем не взятая
        ignored_shifts += [
            await dataset.courier_shift(status='request', courier_tags=tags_2)
        ]

        tap.ok(
            await Courier.job_sync_courier_tags(
                courier_id=courier.courier_id,
                tags=courier.tags,
            ),
            'успешно завершилась'
        )

        with tap.subtest(2 * len(target_shifts), 'Теги совпадают') as _tap:
            for i, shift in enumerate(target_shifts):
                with await shift.reload():
                    _tap.eq(shift.courier_tags, courier.tags, f'совпали #{i}')
                    _tap.eq(shift.tags, [], f'на свои теги не влияет #{i}')

        with tap.subtest(2 * len(ignored_shifts), 'Теги не изменились') as _tap:
            for i, shift in enumerate(ignored_shifts):
                with await shift.reload():
                    _tap.eq(shift.courier_tags, tags_2, f'остались tags_2 #{i}')
                    _tap.eq(shift.tags, [], f'на свои теги не влияет #{i}')


async def test_job_sync_courier_tags_lst(tap, dataset, uuid):
    with tap.plan(3, 'Проверка работы джобы sync_courier_tags для списка'):
        cluster = await dataset.cluster()
        tags = sorted([
            (await dataset.courier_shift_tag(type='courier')).title,
            (await dataset.courier_shift_tag(type='courier')).title,
        ])
        courier_1 = await dataset.courier(cluster=cluster, tags=tags)
        courier_2 = await dataset.courier(cluster=cluster, tags=tags)
        target_shifts = [
            await dataset.courier_shift(
                courier=courier_1,
                cluster=cluster,
                status='waiting',
                courier_tags=[uuid()],  # какой-то тег
            ),
            await dataset.courier_shift(
                courier=courier_1,
                cluster=cluster,
                status='waiting',
                courier_tags=None,      # смена назначена ДО появления тегов
            ),
            await dataset.courier_shift(
                courier=courier_2,
                cluster=cluster,
                status='waiting',
                courier_tags=[],        # курьер был без тега
            ),
            await dataset.courier_shift(
                courier=courier_2,
                cluster=cluster,
                status='waiting',
                courier_tags=tags,      # теги уже на месте
            ),
        ]

        # неподходящие статусы
        tags_2 = [(await dataset.courier_shift_tag(type='courier')).title]
        ignored_shifts = [
            await dataset.courier_shift(
                status=status,
                courier=courier_1,
                courier_tags=tags_2,
            )
            for status in ('processing', 'complete', 'leave', 'released')
        ]
        # чужого курьера
        courier_3 = await dataset.courier(cluster=cluster, tags=tags_2)
        ignored_shifts += [
            await dataset.courier_shift(
                status='waiting',
                courier=courier_3,
                courier_tags=tags_2,
            )
        ]
        # никем не взятая
        ignored_shifts += [
            await dataset.courier_shift(status='request', courier_tags=tags_2)
        ]

        tap.ok(
            await Courier.job_sync_courier_tags(
                courier_id=[courier_1.courier_id, courier_2.courier_id],
                tags=tags,
            ),
            'успешно завершилась'
        )

        with tap.subtest(2 * len(target_shifts), 'Теги совпадают') as _tap:
            for i, shift in enumerate(target_shifts):
                with await shift.reload():
                    _tap.eq(shift.courier_tags, tags, f'совпали #{i}')
                    _tap.eq(shift.tags, [], f'на свои теги не влияет #{i}')

        with tap.subtest(2 * len(ignored_shifts), 'Теги не изменились') as _tap:
            for i, shift in enumerate(ignored_shifts):
                with await shift.reload():
                    _tap.eq(shift.courier_tags, tags_2, f'остались tags_2 #{i}')
                    _tap.eq(shift.tags, [], f'на свои теги не влияет #{i}')
