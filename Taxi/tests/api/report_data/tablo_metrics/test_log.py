import datetime
from libstall.timetable import TimeTable, TimeTableItem
from libstall.util import time2time


async def test_load(tap, api, dataset, tzone, now):
    with tap.plan(3, 'Ручка лога метрик'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')

        today = now(tz=tzone(store.tz)).date()
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            recalculate=True,
        )
        with user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=user)

            with tap.subtest(6, 'Метрик за вчера нет') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today - datetime.timedelta(days=1),
                        'slice': '1h',
                        'entity': 'cluster',
                        'entity_id': store.cluster_id,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_is('timezone', store.tz)
                t.json_has('metrics')
                t.json_hasnt('metrics.0')

            with tap.subtest(8, 'Метрик за сегодня') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'cluster',
                        'entity_id': store.cluster_id,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_is('timezone', store.tz)
                t.json_has('metrics')
                t.json_has('metrics.0')
                t.json_hasnt('metrics.1')
                t.json_is('metrics.0.cluster_id', store.cluster_id)

            with tap.subtest(6, 'Метрик за завтра нет') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today + datetime.timedelta(days=1),
                        'slice': '1h',
                        'entity': 'cluster',
                        'entity_id': store.cluster_id,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_is('timezone', store.tz)
                t.json_has('metrics')
                t.json_hasnt('metrics.0')


async def test_timezone_and_timetable(tap, api, dataset, tzone, now):
    with tap.plan(14, 'Отдаём график по таймзоне и графику работы'):
        store = await dataset.store(
            tz='UTC',
            timetable=TimeTable([
                TimeTableItem(type='everyday', begin='03:00', end='04:00'),
                TimeTableItem(type='everyday', begin='07:00', end='03:00'),
            ]),
        )
        user = await dataset.user(store=store, role='executer')

        today = now(tz=tzone(store.tz)).date()
        today_at_0 = time2time(today.isoformat())
        today_at_0 = today_at_0 - tzone(store.tz).utcoffset(today_at_0)
        tap.note('Лавка работает до 3-х ночи. Получаем время как +3')
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(minutes=-5),
            recalculate=True,
            metrics=dict(orders_count=1),
        )
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(minutes=0),
            recalculate=True,
            metrics=dict(orders_count=2),
        )
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=2, minutes=55),
            recalculate=True,
            metrics=dict(orders_count=3),
        )
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=3),
            recalculate=True,
            metrics=dict(orders_count=4),
        )
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=23, minutes=55),
            recalculate=True,
            metrics=dict(orders_count=5),
        )
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=24),
            recalculate=True,
            metrics=dict(orders_count=6),
        )
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=26, minutes=55),
            recalculate=True,
            metrics=dict(orders_count=7),
        )
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=27),
            recalculate=True,
            metrics=dict(orders_count=8),
        )
        with user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=user)
            await t.post_ok(
                'api_report_data_tablo_metrics_log',
                json={
                    'date': today,
                    'slice': '1h',
                    'entity': 'store',
                    'entity_id': store.store_id,
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('timezone', store.tz)
            t.json_has('metrics')
            t.json_has('metrics.0')
            t.json_is('metrics.0.metrics.orders_count', 4)
            t.json_has('metrics.1')
            t.json_is('metrics.1.metrics.orders_count', 5)
            t.json_has('metrics.2')
            t.json_is('metrics.2.metrics.orders_count', 6)
            t.json_has('metrics.3')
            t.json_is('metrics.3.metrics.orders_count', 7)
            t.json_hasnt('metrics.4')


async def test_timezone(tap, api, dataset, tzone, now):
    # pylint: disable = too-many-locals, too-many-statements
    with tap.plan(4, 'Отдаём график по таймзоне своей лавки'):
        company = await dataset.company()
        cluster = await dataset.cluster(tz='Asia/Omsk')
        store = await dataset.store(
            company=company, cluster=cluster, tz='Asia/Omsk'
        )
        moscow_store = await dataset.store(
            company=company, cluster=cluster, tz='Europe/Moscow'
        )
        user = await dataset.user(store=store, role='executer')
        moscow_user = await dataset.user(store=moscow_store, role='executer')

        today = now(tz=tzone(store.tz)).date()
        today_at_0 = time2time(today.isoformat())
        today_at_0 = today_at_0 - tzone(store.tz).utcoffset(today_at_0)
        # Вчера для обоих юзеров
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(minutes=-5),
            recalculate=True,
            metrics=dict(orders_count=1),
        )
        # Юзер из Омска видит
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(minutes=0),
            recalculate=True,
            metrics=dict(orders_count=2),
        )
        # Юзер из Омска видит
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=2, minutes=55),
            recalculate=True,
            metrics=dict(orders_count=3),
        )
        # Оба юзера видят
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=3),
            recalculate=True,
            metrics=dict(orders_count=4),
        )
        # Оба юзера видят
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=23, minutes=55),
            recalculate=True,
            metrics=dict(orders_count=5),
        )
        # Только юзер из Москвы
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=24),
            recalculate=True,
            metrics=dict(orders_count=6),
        )
        # Только юзер из Москвы
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=26, minutes=55),
            recalculate=True,
            metrics=dict(orders_count=7),
        )
        # Никто не видит
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=27),
            recalculate=True,
            metrics=dict(orders_count=8),
        )
        with user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=user)
            with tap.subtest(
                    14, 'По компании день зависит от своей лавки'
            ) as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'company',
                        'entity_id': store.company_id,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_is('timezone', store.tz)
                t.json_has('metrics')
                t.json_has('metrics.0')
                t.json_is('metrics.0.metrics.orders_count', 2)
                t.json_has('metrics.1')
                t.json_is('metrics.1.metrics.orders_count', 3)
                t.json_has('metrics.2')
                t.json_is('metrics.2.metrics.orders_count', 4)
                t.json_has('metrics.3')
                t.json_is('metrics.3.metrics.orders_count', 5)
                t.json_hasnt('metrics.4')

        with moscow_user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=moscow_user)
            with tap.subtest(
                    14, 'По компании второй пользователь видит своё'
            ) as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'company',
                        'entity_id': store.company_id,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_is('timezone', moscow_store.tz)
                t.json_has('metrics')
                t.json_has('metrics.0')
                t.json_is('metrics.0.metrics.orders_count', 4)
                t.json_has('metrics.1')
                t.json_is('metrics.1.metrics.orders_count', 5)
                t.json_has('metrics.2')
                t.json_is('metrics.2.metrics.orders_count', 6)
                t.json_has('metrics.3')
                t.json_is('metrics.3.metrics.orders_count', 7)
                t.json_hasnt('metrics.4')

        with moscow_user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=moscow_user)
            with tap.subtest(
                    14,
                    'Второй юзер по кластеру видит в таймзоне кластера'
                    'отличной от своей'
            ) as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'cluster',
                        'entity_id': moscow_store.cluster_id,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_is('timezone', cluster.tz)
                t.json_has('metrics')
                t.json_has('metrics.0')
                t.json_is('metrics.0.metrics.orders_count', 2)
                t.json_has('metrics.1')
                t.json_is('metrics.1.metrics.orders_count', 3)
                t.json_has('metrics.2')
                t.json_is('metrics.2.metrics.orders_count', 4)
                t.json_has('metrics.3')
                t.json_is('metrics.3.metrics.orders_count', 5)
                t.json_hasnt('metrics.4')

        with moscow_user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=moscow_user)
            with tap.subtest(
                    14,
                    'По супервайзерам берем таймзону кластера'
            ) as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'supervisor',
                        'entity_id': f'EMPTY:{moscow_store.company_id}'
                                     f':{moscow_store.cluster_id}',
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_is('timezone', cluster.tz)
                t.json_has('metrics')
                t.json_has('metrics.0')
                t.json_is('metrics.0.metrics.orders_count', 2)
                t.json_has('metrics.1')
                t.json_is('metrics.1.metrics.orders_count', 3)
                t.json_has('metrics.2')
                t.json_is('metrics.2.metrics.orders_count', 4)
                t.json_has('metrics.3')
                t.json_is('metrics.3.metrics.orders_count', 5)
                t.json_hasnt('metrics.4')


async def test_not_found(tap, api, dataset, tzone, now, uuid):
    # pylint: disable = too-many-locals, too-many-statements
    with tap.plan(3, 'По сущности логов нет'):
        company = await dataset.company()
        cluster = await dataset.cluster()
        store = await dataset.store(
            company=company, cluster=cluster, tz='Asia/Omsk'
        )
        user = await dataset.user(store=store, role='executer')

        today = now(tz=tzone(store.tz)).date()

        with user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=user)
            with tap.subtest(3, 'Несуществующая лавка') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'store',
                        'entity_id': uuid(),
                    }
                )

                t.status_is(404, diag=True)
                t.json_is('code', 'ER_NOT_FOUND')

            with tap.subtest(3, 'Несуществующий кластер') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'cluster',
                        'entity_id': uuid(),
                    }
                )

                t.status_is(404, diag=True)
                t.json_is('code', 'ER_NOT_FOUND')

            with tap.subtest(3, 'Несуществующий супервайзер') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'supervisor',
                        'entity_id': uuid(),
                    }
                )

                t.status_is(404, diag=True)
                t.json_is('code', 'ER_NOT_FOUND')


async def test_cursor(tap, api, dataset, tzone, now):
    # pylint: disable = too-many-locals, too-many-statements
    with tap.plan(4, 'Отдаём график по таймзоне своей лавки'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(store=store, role='executer')

        today = now(tz=tzone(store.tz)).date()
        today_at_0 = time2time(today.isoformat())
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=1),
            recalculate=True,
            metrics=dict(orders_count=1),
        )
        await dataset.tablo_metric(
            slice='1h',
            store=store,
            calculated=today_at_0 + datetime.timedelta(hours=2),
            recalculate=True,
            metrics=dict(orders_count=2),
        )

        cursor = None
        with user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=user)

            with tap.subtest(9, 'Потестим курсор') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'store',
                        'entity_id': store.store_id,
                        "cursor": cursor,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('metrics')
                t.json_has('metrics.0')
                t.json_is('metrics.0.metrics.orders_count', 1)
                t.json_has('metrics.1')
                t.json_is('metrics.1.metrics.orders_count', 2)
                t.json_hasnt('metrics.2')
                cursor = t.res['json']['cursor']

            await dataset.tablo_metric(
                slice='1h',
                store=store,
                calculated=today_at_0 + datetime.timedelta(hours=3),
                recalculate=True,
                metrics=dict(orders_count=3),
            )

            with tap.subtest(
                7, 'Продолжим получать данные по курсору'
            ) as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'store',
                        'entity_id': store.store_id,
                        'cursor':  cursor,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('metrics')
                t.json_has('metrics.0')
                t.json_is('metrics.0.metrics.orders_count', 3)
                t.json_hasnt('metrics.1')
                cursor = t.res['json']['cursor']

            await dataset.tablo_metric(
                slice='1h',
                store=store,
                calculated=today_at_0 + datetime.timedelta(hours=24),
                recalculate=True,
                metrics=dict(orders_count=24),
            )

            with tap.subtest(5, 'Вышли за границу суток') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'slice': '1h',
                        'entity': 'store',
                        'entity_id': store.store_id,
                        'cursor':  cursor,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('metrics')
                t.json_hasnt('metrics.0')
                cursor = t.res['json']['cursor']

            with tap.subtest(7, 'unbound позволит получать дальше') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_report_data_tablo_metrics_log',
                    json={
                        'date': today,
                        'unbound': True,
                        'slice': '1h',
                        'entity': 'store',
                        'entity_id': store.store_id,
                        'cursor':  cursor,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('metrics')
                t.json_has('metrics.0')
                t.json_is('metrics.0.metrics.orders_count', 24)
                t.json_hasnt('metrics.1')
                cursor = t.res['json']['cursor']
