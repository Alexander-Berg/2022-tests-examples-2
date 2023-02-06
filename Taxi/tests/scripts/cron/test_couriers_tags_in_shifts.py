from collections import defaultdict
from datetime import timedelta

from scripts.cron.couriers_tags_in_shifts import (
    get_couriers,
    process_courier_tags,
    upload_grocery_tags,
)
from scripts.couriers import TAG_BEGINNER
from stall.client.grocery_tags import client as client_gt
from stall.model.stash import Stash


async def test_get_couriers(tap, dataset, now, uuid, cfg):
    with tap.plan(6, 'Проверка выдачи курьеров'):
        cfg.set('cursor.limit', 1)
        _now = now()

        cluster = await dataset.cluster()
        courier_1 = await dataset.courier(
            cluster=cluster,
            tags_updated=_now + timedelta(seconds=2),
        )
        courier_2 = await dataset.courier(
            cluster=cluster,
            tags_updated=_now + timedelta(seconds=4),
        )
        courier_3 = await dataset.courier(
            cluster=cluster,
            tags_updated=_now + timedelta(seconds=6),
        )

        # теги не менялись или чужой кластер
        await dataset.courier(cluster=cluster, tags_updated=None)
        await dataset.courier(tags_updated=_now)

        stash = Stash({
            'name': uuid(),
            'value': {
                'cursor': None,
            }
        })
        agen = get_couriers(stash=stash, cluster_id=cluster.cluster_id)
        async for couriers in agen:
            tap.eq(len(couriers), 1, 'только один курьер')
            tap.eq(couriers[0].courier_id, courier_1.courier_id, 'первый')
            break

        async for couriers in agen:
            tap.eq(len(couriers), 1, 'только один курьер')
            tap.eq(couriers[0].courier_id, courier_2.courier_id, 'второй')
            break

        async for couriers in agen:
            tap.eq(len(couriers), 1, 'только один курьер')
            tap.eq(couriers[0].courier_id, courier_3.courier_id, 'третий')
            break

        async for _ in agen:
            tap.failed('Должно быть только 3 курьера')


async def test_one_courier(tap, dataset, now):
    with tap.plan(2, 'Назначение тегов на waiting-смены одного курьера'):
        _now = now()

        cluster = await dataset.cluster()
        tags = sorted([
            (await dataset.courier_shift_tag(type='courier')).title,
            (await dataset.courier_shift_tag(type='courier')).title,
        ])
        courier = await dataset.courier(
            cluster=cluster,
            tags_updated=_now + timedelta(seconds=2),
            tags=tags,
        )

        # теги не менялись или чужой кластер
        await dataset.courier(cluster=cluster, tags_updated=None)
        await dataset.courier(tags_updated=_now)

        shifts = [
            await dataset.courier_shift(
                status='waiting',
                courier=courier,
                cluster=cluster,
                courier_tags=None,
            ) for _ in range(3)
        ]

        ignored = await dataset.courier_shift(
            status='complete',
            courier=courier,
            cluster=cluster,
            courier_tags=None,
        )

        await process_courier_tags(cluster_id=cluster.cluster_id)

        with tap.subtest(len(shifts), 'Теги изменились') as _tap:
            for i, shift in enumerate(shifts):
                with await shift.reload():
                    _tap.eq(shift.courier_tags, tags, f'теги обновились #{i}')

        with await ignored.reload():
            tap.eq(ignored.courier_tags, None, 'теги сохранились')


async def test_several_courier_gather(tap, dataset, now):
    # pylint: disable=too-many-locals
    with tap.plan(2, 'Назначение тегов на waiting-смены нескольких курьеров'):
        _now = now()

        cluster = await dataset.cluster()
        tags = sorted([
            (await dataset.courier_shift_tag(type='courier')).title,
            (await dataset.courier_shift_tag(type='courier')).title,
        ])

        # два курьера с одинаковыми тегами в одну таску
        courier_1 = await dataset.courier(
            cluster=cluster,
            tags_updated=_now + timedelta(seconds=2),
            tags=tags,
        )
        courier_2 = await dataset.courier(
            cluster=cluster,
            tags_updated=_now + timedelta(seconds=2),
            tags=tags,
        )
        # третий курьер - во вторую
        courier_3 = await dataset.courier(
            cluster=cluster,
            tags_updated=_now + timedelta(seconds=3),
            tags=[],
        )

        # теги не менялись или чужой кластер (для get_couriers внутри)
        await dataset.courier(cluster=cluster, tags_updated=None)
        await dataset.courier(tags_updated=_now)

        shift2courier_tags = {}
        shifts, ignored = [], []
        for courier in courier_1, courier_2, courier_3:
            for _ in range(3):
                shift = await dataset.courier_shift(
                    status='waiting',
                    courier=courier,
                    courier_tags=None,
                )
                shift2courier_tags[shift.courier_shift_id] = courier.tags
                shifts.append(shift)

            ignored.append(
                await dataset.courier_shift(
                    status='complete',
                    courier=courier_1,
                    courier_tags=None,
                )
            )

        await process_courier_tags(cluster_id=cluster.cluster_id)

        with tap.subtest(len(shifts), 'Теги изменились') as _tap:
            for i, shift in enumerate(shifts):
                with await shift.reload():
                    _tap.eq(
                        shift.courier_tags,
                        shift2courier_tags[shift.courier_shift_id],
                        f'теги обновились #{i}',
                    )

        with tap.subtest(len(ignored), 'Теги не изменились') as _tap:
            for ignored in ignored:
                with await ignored.reload():
                    _tap.eq(ignored.courier_tags, None, 'теги сохранились')


async def test_upload_tags_no_request(tap, dataset, ext_api):
    with tap.plan(4, 'Игнорируем некоторые случае при загрузке тегов'):
        async def handler(request):  # pylint: disable=unused-argument
            tap.failed('вызова не должно произойти')
            return 200, 'OK'

        await dataset.courier_shift_tag(title=TAG_BEGINNER)
        tag = (await dataset.courier_shift_tag()).title

        couriers_empty = []
        couriers_no_tags = [await dataset.courier() for _ in range(10)]

        couriers_equal_tags = []
        for tags in ([TAG_BEGINNER], [TAG_BEGINNER, tag], [tag]):
            _courier = await dataset.courier(tags=tags)
            _courier.vars['last_synced_tags'] = tags
            await _courier.save()
            couriers_equal_tags.append(_courier)

        couriers_not_change_beginner = []
        for tags, last_synced in (
            ([tag], []),    # обычный курьер потерял обычный тег
            ([], [tag]),    # обычный курьер приобрел обычный тег
            ([TAG_BEGINNER, tag], [TAG_BEGINNER]),  # новичок потерял тег
            ([TAG_BEGINNER], [TAG_BEGINNER, tag]),  # новичок приобрел тег
        ):
            _courier = await dataset.courier(tags=tags)
            _courier.vars['last_synced_tags'] = last_synced
            await _courier.save()
            couriers_not_change_beginner.append(_courier)

        async with await ext_api(client_gt, handler):
            tap.ok(await upload_grocery_tags(couriers_empty) is None,
                   'пустой список на вход')

            tap.ok(await upload_grocery_tags(couriers_no_tags) is None,
                   'курьеры без тегов вовсе')

            tap.ok(not await upload_grocery_tags(couriers_not_change_beginner),
                   'курьеры, у которых не происходит изменение тега Новичок')

            tap.ok(await upload_grocery_tags(couriers_equal_tags) is None,
                   'курьеры с идентичными tags и last_synced_tags')


async def test_upload_tags_request(tap, dataset, ext_api):
    with tap.plan(3, 'Снимаем и назначаем теги через сервис тегов'):
        async def handler(request):  # pylint: disable=unused-argument
            data = await request.json()

            for entity in data['append']:
                for tag in entity['tags']:
                    courier2tags_append[tag['entity']].add(tag['name'])

            for entity in data['remove']:
                for tag in entity['tags']:
                    courier2tags_remove[tag['entity']].add(tag['name'])
            return 200, 'OK'

        courier2tags_append = defaultdict(set)
        courier2tags_remove = defaultdict(set)

        await dataset.courier_shift_tag(title=TAG_BEGINNER)
        tag_1 = (await dataset.courier_shift_tag()).title
        tag_2 = (await dataset.courier_shift_tag()).title

        # тег добавлен
        courier_1 = await dataset.courier(tags=[tag_1, TAG_BEGINNER])
        courier_1.vars['last_synced_tags'] = []

        # тег убран
        courier_2 = await dataset.courier(tags=[])
        courier_2.vars['last_synced_tags'] = [tag_2, TAG_BEGINNER]

        # тег заменен
        courier_3 = await dataset.courier(tags=[tag_2])
        courier_3.vars['last_synced_tags'] = [TAG_BEGINNER]

        async with await ext_api(client_gt, handler):
            lst = [courier_1, courier_2, courier_3]
            tap.ok(not await upload_grocery_tags(lst), 'отработало успешно')
            tap.eq(
                courier2tags_append,
                {
                    courier_1.external_id: {tag_1, TAG_BEGINNER},
                    courier_3.external_id: {tag_2},
                },
                'теги, которые будут назначены'
            )
            tap.eq(
                courier2tags_remove,
                {
                    courier_2.external_id: {tag_2, TAG_BEGINNER},
                    courier_3.external_id: {TAG_BEGINNER},
                },
                'теги, которые будут сняты'
            )
