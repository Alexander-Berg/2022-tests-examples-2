
import datetime

from libstall.util import time2time
from stall.model.analytics.store_health import StoreHealth
from stall.model.analytics.store_problem import StoreProblem
from stall.model.analytics.tablo_metrics import TabloMetric
from scripts.cron.detect_store_problems import main


async def test_hasnt_problems(
        tap, now, time_mock, cfg, tzone, dataset, clickhouse_client,
):
    # pylint: disable=unused-argument, protected-access, too-many-arguments
    # pylint: disable=too-many-locals
    with tap.plan(13, 'Проблем быть не должно'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store, type='stowage')
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        cfg._db.o['health_monitoring']['type_thresholds'] = {
            'stowage': {
                'processing': {
                    'duration_total': 90
                }
            }
        }
        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
            items_count=1,
            items_uniq=1,
            suggests_count=1,
        )
        time_mock.set(today_at_12 + datetime.timedelta(seconds=121))

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        problems = await StoreProblem.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
                ('is_resolved', False)
            ),
        )
        tap.eq(len(problems.list), 0, 'Проблем нет')

        store_health = await StoreHealth.load(
            ['store', store.store_id],
            by='conflict'
        )
        tap.ok(store_health, 'Инфа по здоровью есть')
        tap.eq(store_health.has_problem, False, 'Лавка здорова')
        tap.eq(store_health.reason, None, 'Причина пустая')

        supervisor_health = await StoreHealth.load(
            ['supervisor', f'EMPTY:{store.company_id}:{store.cluster_id}'],
            by='conflict'
        )
        tap.ok(supervisor_health, 'Инфа по здоровью есть')
        tap.eq(supervisor_health.has_problem, False, 'Супервизор здоров')
        tap.eq(supervisor_health.reason, None, 'Причина пустая')

        cluster_health = await StoreHealth.load(
            ['cluster', store.cluster_id],
            by='conflict'
        )
        tap.ok(cluster_health, 'Инфа по здоровью есть')
        tap.eq(cluster_health.has_problem, False, 'Кластер здоров')
        tap.eq(cluster_health.reason, None, 'Причина пустая')

        company_health = await StoreHealth.load(
            ['company', store.company_id],
            by='conflict'
        )
        tap.ok(company_health, 'Инфа по здоровью есть')
        tap.eq(company_health.has_problem, False, 'Компания здорова')
        tap.eq(company_health.reason, None, 'Причина пустая')


async def test_has_problems(
        tap, now, time_mock, cfg, tzone, dataset, clickhouse_client,
):
    # pylint: disable=unused-argument, protected-access, too-many-arguments
    with tap.plan(13, 'Проблема есть. Найдем.'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store, type='stowage')
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        cfg._db.o['health_monitoring']['type_thresholds'] = {
            'stowage': {
                'processing': {
                    'duration_total': 60
                }
            }
        }
        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
            items_count=1,
            items_uniq=1,
            suggests_count=1,
        )
        time_mock.set(today_at_12 + datetime.timedelta(seconds=121))

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        problems = await StoreProblem.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
                ('is_resolved', False)
            ),
        )
        tap.eq(len(problems.list), 1, '1 проблема')
        with problems.list[0] as p:
            tap.eq(len(p.details), 1, 'Проблема в одном документе')
            tap.eq(p.details[0].order_id, order.order_id, 'order_id')
            tap.eq(p.details[0].duration, 61, 'duration')
            tap.eq(p.is_active, True, 'is_active')

        tap.note('Выполним вторую проверку через минуту')
        time_mock.set(today_at_12 + datetime.timedelta(seconds=181))

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        problems = await StoreProblem.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
                ('is_resolved', False)
            ),
        )
        tap.eq(len(problems.list), 1, '1 проблема')
        with problems.list[0] as p:
            tap.eq(len(p.details), 1, 'Проблема в одном документе')
            tap.eq(p.details[0].order_id, order.order_id, 'order_id')
            tap.eq(p.details[0].duration, 121, 'duration')
            tap.eq(p.is_active, True, 'is_active')

        store_health = await StoreHealth.load(
            ['store', store.store_id],
            by='conflict'
        )
        tap.ok(store_health, 'Инфа по здоровью есть')
        tap.eq(store_health.has_problem, True, 'Лавка не здорова')
        tap.eq(store_health.reason, 'document', 'Из-за документов')


async def test_second_orders_in_problem(
        tap, now, time_mock, cfg, tzone, dataset, clickhouse_client,
):
    # pylint: disable=unused-argument, protected-access, too-many-arguments
    # pylint: disable=too-many-locals, too-many-statements
    with tap.plan(3, 'Если появился новый документ, то добавим его в проблему'):
        store = await dataset.store(tz='UTC')
        order_1 = await dataset.order(store=store, type='stowage')
        order_2 = await dataset.order(store=store, type='stowage')
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        cfg._db.o['health_monitoring']['type_thresholds'] = {
            'stowage': {
                'processing': {
                    'duration_total': 60
                }
            }
        }

        await dataset.ch_wms_order_status_update(
            order=order_1,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
            items_count=1,
            items_uniq=1,
            suggests_count=1,
        )
        time_mock.set(today_at_12 + datetime.timedelta(seconds=121))

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        with tap.subtest(7, '1 проблема по одному документу') as taps:
            problems = await StoreProblem.list(
                by='full',
                conditions=(
                    ('store_id', store.store_id),
                    ('is_resolved', False)
                ),
            )
            taps.eq(len(problems.list), 1, '1 проблема')
            with problems.list[0] as p:
                taps.eq(len(p.details), 1, 'Проблема в одном документе')
                taps.eq(p.details[0].order_id, order_1.order_id, 'order_id')
                taps.eq(p.is_active, True, 'is_active')

            store_health = await StoreHealth.load(
                ['store', store.store_id],
                by='conflict'
            )
            taps.ok(store_health, 'Инфа по здоровью есть')
            taps.eq(store_health.has_problem, True, 'Лавка не здорова')
            taps.eq(store_health.reason, 'document', 'Из-за документов')

        await dataset.ch_wms_order_status_update(
            order=order_1,
            status='complete',
            timestamp=today_at_12 + datetime.timedelta(seconds=120),
            items_count=1,
            items_uniq=1,
            suggests_count=1,
        )
        time_mock.set(today_at_12 + datetime.timedelta(seconds=121))

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        with tap.subtest(
                7,
                'Документ закрыт, новых проблем нет, старая осталась'
        ) as taps:
            problems = await StoreProblem.list(
                by='full',
                conditions=(
                    ('store_id', store.store_id),
                    ('is_resolved', False)
                ),
            )
            taps.eq(len(problems.list), 1, '1 проблема')
            with problems.list[0] as p:
                taps.eq(len(p.details), 1, 'Проблема в одном документе')
                taps.eq(p.details[0].order_id, order_1.order_id, 'order_id')
                taps.eq(p.is_active, False, 'is_active')

            store_health = await StoreHealth.load(
                ['store', store.store_id],
                by='conflict'
            )
            taps.ok(store_health, 'Инфа по здоровью есть')
            taps.eq(store_health.has_problem, False, 'Лавка здорова')
            taps.eq(store_health.reason, None, 'Причина пустая')

        await dataset.ch_wms_order_status_update(
            order=order_2,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=120),
            items_count=1,
            items_uniq=1,
            suggests_count=1,
        )
        time_mock.set(today_at_12 + datetime.timedelta(seconds=200))

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        with tap.subtest(
                8,
                'Открыли новый документ. Добавили в проблему второй документ'
        ) as taps:
            problems = await StoreProblem.list(
                by='full',
                conditions=(
                    ('store_id', store.store_id),
                    ('is_resolved', False)
                ),
            )
            taps.eq(len(problems.list), 1, '1 проблема')
            with problems.list[0] as p:
                taps.eq(len(p.details), 2, 'Проблема в двух документах')
                taps.eq(p.details[0].order_id, order_1.order_id, 'order_1_id')
                taps.eq(p.details[1].order_id, order_2.order_id, 'order_2_id')
                taps.eq(p.is_active, True, 'is_active')

            store_health = await StoreHealth.load(
                ['store', store.store_id],
                by='conflict'
            )
            taps.ok(store_health, 'Инфа по здоровью есть')
            taps.eq(store_health.has_problem, True, 'Лавка не здорова')
            taps.eq(store_health.reason, 'document', 'Из-за документов')


async def test_add_order_in_count_problem(
        tap, now, time_mock, cfg, tzone, dataset, clickhouse_client,
):
    # pylint: disable=unused-argument, protected-access, too-many-arguments
    # pylint: disable=too-many-locals, too-many-statements
    with tap.plan(3, 'Добавим документ в count проблему'):
        store = await dataset.store(tz='UTC')
        order_1 = await dataset.order(store=store, type='stowage')
        order_2 = await dataset.order(store=store, type='stowage')
        order_3 = await dataset.order(store=store, type='stowage')
        different_order = await dataset.order(store=store, type='order')
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        cfg._db.o['health_monitoring']['type_thresholds'] = {
            'stowage': {
                'processing': {
                    'count': 1
                }
            }
        }

        await dataset.ch_wms_order_status_update(
            order=order_1,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
        )
        await dataset.ch_wms_order_status_update(
            order=order_2,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=61),
        )
        await dataset.ch_wms_order_status_update(
            order=different_order,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
        )
        time_mock.set(today_at_12 + datetime.timedelta(seconds=121))

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        with tap.subtest(
                8,
                'Слишком много документов в статусе processing'
        ) as taps:
            problems = await StoreProblem.list(
                by='full',
                conditions=(
                    ('store_id', store.store_id),
                    ('is_resolved', False)
                ),
            )
            taps.eq(len(problems.list), 1, '1 проблема')
            with problems.list[0] as p:
                taps.eq(len(p.details), 1, '1 детализация')
                taps.in_ok(
                    order_1.order_id,
                    p.details[0].order_ids,
                    '1-й документ попал'
                )
                taps.in_ok(
                    order_2.order_id,
                    p.details[0].order_ids,
                    '2-й документ попал'
                )
                taps.eq(p.is_active, True, 'is_active')

            store_health = await StoreHealth.load(
                ['store', store.store_id],
                by='conflict'
            )
            taps.ok(store_health, 'Инфа по здоровью есть')
            taps.eq(store_health.has_problem, True, 'Лавка не здорова')
            taps.eq(store_health.reason, 'document', 'Из-за документов')

        await dataset.ch_wms_order_status_update(
            order=order_1,
            status='complete',
            timestamp=today_at_12 + datetime.timedelta(seconds=90),
            items_count=1,
            items_uniq=1,
            suggests_count=1,
        )

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        with tap.subtest(
                8,
                'Документ закрыт, новых проблем нет, старая осталась'
        ) as taps:
            problems = await StoreProblem.list(
                by='full',
                conditions=(
                    ('store_id', store.store_id),
                    ('is_resolved', False)
                ),
            )
            taps.eq(len(problems.list), 1, '1 проблема')
            with problems.list[0] as p:
                taps.eq(len(p.details), 1, '1 детализация')
                taps.in_ok(
                    order_1.order_id,
                    p.details[0].order_ids,
                    '1-й документ попал'
                )
                taps.in_ok(
                    order_2.order_id,
                    p.details[0].order_ids,
                    '2-й документ попал'
                )
                taps.eq(p.is_active, False, 'is_active')

            store_health = await StoreHealth.load(
                ['store', store.store_id],
                by='conflict'
            )
            taps.ok(store_health, 'Инфа по здоровью есть')
            taps.eq(store_health.has_problem, False, 'Лавка здорова')
            taps.eq(store_health.reason, None, 'Причина пустая')

        await dataset.ch_wms_order_status_update(
            order=order_3,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=91),
        )

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        with tap.subtest(
                9,
                'Открыли новый документ. Добавили в проблему второй документ'
        ) as taps:
            problems = await StoreProblem.list(
                by='full',
                conditions=(
                    ('store_id', store.store_id),
                    ('is_resolved', False)
                ),
            )
            taps.eq(len(problems.list), 1, '1 проблема')
            with problems.list[0] as p:
                taps.eq(len(p.details), 1, '1 детализация')
                taps.in_ok(
                    order_1.order_id,
                    p.details[0].order_ids,
                    '1-й документ попал'
                )
                taps.in_ok(
                    order_2.order_id,
                    p.details[0].order_ids,
                    '2-й документ попал'
                )
                taps.in_ok(
                    order_3.order_id,
                    p.details[0].order_ids,
                    'Новый документ попал'
                )
                taps.eq(p.is_active, True, 'is_active')

            store_health = await StoreHealth.load(
                ['store', store.store_id],
                by='conflict'
            )
            taps.ok(store_health, 'Инфа по здоровью есть')
            taps.eq(store_health.has_problem, True, 'Лавка не здорова')
            taps.eq(store_health.reason, 'document', 'Из-за документов')


async def test_today_and_tomorrow(
        tap, now, time_mock, cfg, tzone, dataset, clickhouse_client,
):
    # pylint: disable=unused-argument, protected-access, too-many-arguments
    # pylint: disable=too-many-locals
    with tap.plan(14, 'Группируем проблемы по дате проверки.'):
        store = await dataset.store(tz='Asia/Omsk')
        order = await dataset.order(store=store, type='stowage')
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        cfg._db.o['health_monitoring']['type_thresholds'] = {
            'stowage': {
                'processing': {
                    'duration_total': 60
                }
            }
        }
        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
            items_count=1,
            items_uniq=1,
            suggests_count=1,
        )
        time_mock.set(today_at_12 + datetime.timedelta(seconds=121))

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        problems = await StoreProblem.list(
            by='walk',
            conditions=(
                ('store_id', store.store_id),
                ('is_resolved', False)
            ),
            sort=(
                ('timestamp_group', 'ASC'),
            )
        )
        tap.eq(len(problems.list), 1, '1 проблема')
        with problems.list[0] as p:
            tap.in_ok(
                today.isoformat(),
                p.timestamp_group.astimezone(tz=tzone(store.tz)).isoformat(),
                'Группируем по дате'
            )
            tap.eq(len(p.details), 1, 'Проблема в одном документе')
            tap.eq(p.details[0].order_id, order.order_id, 'order_id')
            tap.eq(p.is_active, True, 'is_active')

        tap.note('Запустим проверку завтра')
        tomorrow = today + datetime.timedelta(days=1)
        tomorrow_at_12 = today_at_12 + datetime.timedelta(hours=24)
        time_mock.set(tomorrow_at_12)

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        problems = await StoreProblem.list(
            by='walk',
            conditions=(
                ('store_id', store.store_id),
                ('is_resolved', False)
            ),
            sort=(
                ('timestamp_group', 'DESC'),
                ('lsn', 'DESC'),
            )
        )
        tap.eq(len(problems.list), 2, '2 проблемы')

        with problems.list[0] as p:
            tap.in_ok(
                tomorrow.isoformat(),
                p.timestamp_group.astimezone(tz=tzone(store.tz)).isoformat(),
                'Группируем по дате'
            )
            tap.eq(len(p.details), 1, 'Проблема в одном документе')
            tap.eq(p.details[0].order_id, order.order_id, 'order_id')
            tap.eq(p.is_active, True, 'is_active')

        with problems.list[1] as p:
            tap.in_ok(
                today.isoformat(),
                p.timestamp_group.astimezone(tz=tzone(store.tz)).isoformat(),
                'Группируем по дате'
            )
            tap.eq(len(p.details), 1, 'Проблема в одном документе')
            tap.eq(p.details[0].order_id, order.order_id, 'order_id')
            tap.eq(p.is_active, False, 'is_active')


async def test_events(
        tap, now, time_mock, cfg, tzone, dataset, clickhouse_client, lp,
        push_events_cache,
):
    # pylint: disable=unused-argument, protected-access, too-many-arguments
    # pylint: disable=too-many-locals, too-many-statements

    with tap.plan(6, 'Отправим ивент, что нашли проблему'):
        store = await dataset.store(tz='UTC')
        supervisor = await dataset.user(store=store, role='supervisor')
        empty_supervisor_id = f'EMPTY:{store.company_id}:{store.cluster_id}'
        order = await dataset.order(store=store, type='stowage')
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        cfg._db.o['health_monitoring']['type_thresholds'] = {
            'stowage': {
                'processing': {
                    'duration_total': 60
                }
            }
        }
        await dataset.ch_wms_order_status_update(
            order=order,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=60),
            items_count=1,
            items_uniq=1,
            suggests_count=1,
        )
        time_mock.set(today_at_12 + datetime.timedelta(seconds=121))
        lp.clean_cache()

        args = lambda: None
        args.store_id = store.store_id
        await main(args)

        with tap.subtest(4, 'Ивенты по проблемам') as taps:
            store_problems = await StoreProblem.list(
                by='full',
                conditions=(
                    ('store_id', store.store_id),
                ),
                limit=1,
            )

            await push_events_cache(
                store_problems.list, event_type='lp', database='analytics'
            )
            taps.ok(len(lp.pytest_cache), 'Ивенты отправлены')
            keys = [event.key for event in lp.pytest_cache]
            lp.clean_cache()

            taps.in_ok(
                ['store_problems', 'store', store.store_id],
                keys,
                'Отправили проблему по стору'
            )
            taps.in_ok(
                ['store_problems', 'supervisor', empty_supervisor_id],
                keys,
                'Отправили проблему по супервайзеру'
            )
            taps.in_ok(
                ['store_problems', 'cluster', store.cluster_id],
                keys,
                'Отправили проблему по кластеру'
            )

        with tap.subtest(6, 'Ивенты по здоровью') as taps:
            store_health_cursor = await StoreHealth.list(
                by='full',
                conditions=(
                    (
                        ('company_id', store.company_id),
                        ('entity_id', 'total'),
                    ),
                )
            )
            await push_events_cache(
                store_health_cursor.list, event_type='lp', database='analytics'
            )
            taps.ok(len(lp.pytest_cache), 'Ивенты отправлены')
            keys = [event.key for event in lp.pytest_cache]
            lp.clean_cache()

            taps.in_ok(
                ['store_health', 'store', store.store_id],
                keys,
                'Отправили здоровье по стору'
            )
            taps.in_ok(
                ['store_health', 'supervisor', empty_supervisor_id],
                keys,
                'Отправили здоровье по супервайзеру'
            )
            taps.in_ok(
                ['store_health', 'cluster', store.cluster_id],
                keys,
                'Отправили здоровье по кластеру'
            )
            taps.in_ok(
                ['store_health', 'company', store.company_id],
                keys,
                'Отправили здоровье по компании'
            )
            taps.in_ok(
                ['store_health', 'total', 'total'],
                keys,
                'Отправили здоровье по всему'
            )

        with tap.subtest(6, 'Ивенты по метрикам') as taps:
            tablo_metric_cursor = await TabloMetric.list(
                by='full',
                conditions=('company_id', store.company_id),
            )
            await push_events_cache(
                tablo_metric_cursor.list, event_type='lp', database='analytics'
            )
            tablo_metric_cursor = await TabloMetric.list(
                by='full',
                conditions=('entity_id', 'total'),
            )
            await push_events_cache(
                tablo_metric_cursor.list, event_type='lp', database='analytics'
            )
            taps.ok(len(lp.pytest_cache), 'Ивенты отправлены')
            keys = [event.key for event in lp.pytest_cache]
            lp.clean_cache()

            taps.in_ok(
                ['tablo_metrics', 'store', store.store_id],
                keys,
                'Отправили метрики по лавке'
            )
            taps.in_ok(
                ['tablo_metrics', 'supervisor', empty_supervisor_id],
                keys,
                'Отправили метрики по супервайзеру'
            )
            taps.in_ok(
                ['tablo_metrics', 'cluster', store.cluster_id],
                keys,
                'Отправили метрики по кластеру'
            )
            taps.in_ok(
                ['tablo_metrics', 'company', store.company_id],
                keys,
                'Отправили метрики по компании'
            )
            taps.in_ok(
                ['tablo_metrics', 'total', 'total'],
                keys,
                'Отправили метрики по всему'
            )


        tap.note('Обновим супервайзера')
        await dataset.ch_wms_order_status_update(
            order=order,
            supervisor_id=supervisor.user_id,
            status='processing',
            timestamp=today_at_12 + datetime.timedelta(seconds=70),
            items_count=1,
            items_uniq=1,
            suggests_count=1,
        )

        await main(args)

        with tap.subtest(4, 'Ивенты по проблемам') as taps:
            store_problems = await StoreProblem.list(
                by='full',
                conditions=(
                    ('store_id', store.store_id),
                ),
                limit=1,
            )

            await push_events_cache(
                store_problems.list, event_type='lp', database='analytics'
            )
            taps.ok(len(lp.pytest_cache), 'Ивенты отправлены')
            keys = [event.key for event in lp.pytest_cache]
            lp.clean_cache()

            taps.in_ok(
                ['store_problems', 'store', store.store_id],
                keys,
                'Отправили проблему по стору'
            )
            taps.in_ok(
                ['store_problems', 'supervisor', supervisor.user_id],
                keys,
                'Отправили проблему по супервайзеру'
            )
            taps.in_ok(
                ['store_problems', 'cluster', store.cluster_id],
                keys,
                'Отправили проблему по кластеру'
            )

        with tap.subtest(6, 'Ивенты по здоровью') as taps:
            store_health_cursor = await StoreHealth.list(
                by='full',
                conditions=(
                    (
                        ('company_id', store.company_id),
                        ('entity_id', 'total'),
                    ),
                )
            )
            await push_events_cache(
                store_health_cursor.list, event_type='lp', database='analytics'
            )
            taps.ok(len(lp.pytest_cache), 'Ивенты отправлены')
            keys = [event.key for event in lp.pytest_cache]
            lp.clean_cache()

            taps.in_ok(
                ['store_health', 'store', store.store_id],
                keys,
                'Отправили здоровье по стору'
            )
            taps.in_ok(
                ['store_health', 'supervisor', supervisor.user_id],
                keys,
                'Отправили здоровье по супервайзеру'
            )
            taps.in_ok(
                ['store_health', 'cluster', store.cluster_id],
                keys,
                'Отправили здоровье по кластеру'
            )
            taps.in_ok(
                ['store_health', 'company', store.company_id],
                keys,
                'Отправили здоровье по компании'
            )
            taps.in_ok(
                ['store_health', 'total', 'total'],
                keys,
                'Отправили здоровье по всему'
            )

        with tap.subtest(6, 'Ивенты по метрикам') as taps:
            tablo_metric_cursor = await TabloMetric.list(
                by='full',
                conditions=('company_id', store.company_id),
            )
            await push_events_cache(
                tablo_metric_cursor.list, event_type='lp', database='analytics'
            )
            tablo_metric_cursor = await TabloMetric.list(
                by='full',
                conditions=('entity_id', 'total'),
            )
            await push_events_cache(
                tablo_metric_cursor.list, event_type='lp', database='analytics'
            )
            taps.ok(len(lp.pytest_cache), 'Ивенты отправлены')
            keys = [event.key for event in lp.pytest_cache]
            lp.clean_cache()

            taps.in_ok(
                ['tablo_metrics', 'store', store.store_id],
                keys,
                'Отправили метрики по лавке'
            )
            taps.in_ok(
                ['tablo_metrics', 'supervisor', supervisor.user_id],
                keys,
                'Отправили метрики по супервайзеру'
            )
            taps.in_ok(
                ['tablo_metrics', 'cluster', store.cluster_id],
                keys,
                'Отправили метрики по кластеру'
            )
            taps.in_ok(
                ['tablo_metrics', 'company', store.company_id],
                keys,
                'Отправили метрики по компании'
            )
            taps.in_ok(
                ['tablo_metrics', 'total', 'total'],
                keys,
                'Отправили метрики по всему'
            )
