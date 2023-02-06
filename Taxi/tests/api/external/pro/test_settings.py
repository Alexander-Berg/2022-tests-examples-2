# pylint: disable=unused-argument

from datetime import time, timedelta

import pytest


async def test_settings(tap, api, dataset, now, tzone, time2iso_utc):
    with tap.plan(22, 'Получение настроек'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 16,
                'max_week_hours': 80,
                'recommended_week_hours': 40,
                'duration_between_stores': 45 * 60,
                'shift_close_time': time(11, 30, 55),
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        day = now(tz=tzone(cluster.tz)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Текущая смена
        await dataset.courier_shift(
            cluster=cluster,
            store=store,
            courier=courier,
            status='processing',
            schedule=[{'tags': [], 'time': now()}],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13, minute=30),
            shift_events=[
                {
                    'type': 'started',
                    'created': day.replace(hour=12),
                },
            ],
        )

        # Завершенна смена по фактическому времени
        await dataset.courier_shift(
            cluster=cluster,
            store=store,
            courier=courier,
            status='leave',
            schedule=[{'tags': [], 'time': now()}],
            started_at=day.replace(hour=9),
            closes_at=day.replace(hour=11),
            shift_events=[
                {
                    'type': 'started',
                    'created': day.replace(hour=9, minute=5),
                },
                {
                    'type': 'stopped',
                    'created': day.replace(hour=9, minute=35),
                },
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.id', courier.courier_id)
        t.json_is('data.type', 'settings')
        t.json_is('data.attributes.workStatus', 'active')
        t.json_is('data.attributes.showFreeSlotButton', False)
        t.json_is('data.attributes.shiftPullToRefreshCacheTime', 5000)
        t.json_is('data.attributes.shiftsMinInterval', 45)
        t.json_is(
            'data.attributes.shiftRefuseMaxTime',
            time2iso_utc(
                now(tz=tzone(cluster.tz)).replace(hour=11, minute=30, second=55)
            ),
        )
        t.json_is(
            'data.attributes.weeklyRecommendedShiftHours',
            cluster.courier_shift_setup.recommended_week_hours
        )

        # Лимиты текущей недели
        t.json_is(
            'data.attributes.workTimeLimit.currentWeek.maxShiftHours',
            cluster.courier_shift_setup.max_week_hours
        )
        t.json_is(
            'data.attributes.workTimeLimit.currentWeek.recommendedShiftHours',
            cluster.courier_shift_setup.recommended_week_hours
        )
        t.json_is(
            'data.attributes.workTimeLimit.currentWeek.chosenShiftHours',
            1.5 + 0.5,  # одна смена уже идет + одна завершена
        )

        # Лимиты следующей недели
        t.json_is(
            'data.attributes.workTimeLimit.nextWeek.maxShiftHours',
            cluster.courier_shift_setup.max_week_hours
        )
        t.json_is(
            'data.attributes.workTimeLimit.nextWeek.recommendedShiftHours',
            cluster.courier_shift_setup.recommended_week_hours
        )
        t.json_is(
            'data.attributes.workTimeLimit.nextWeek.chosenShiftHours',
            0,  # смен еще не было
        )

        # Список лимитов
        t.json_is(
            'data.attributes.dailyWorkTimeLimits.0.date',
            time2iso_utc(day.date()),
        )
        t.json_is(
            'data.attributes.dailyWorkTimeLimits.0.maxShiftHours',
            cluster.courier_shift_setup.max_day_hours,
        )
        t.json_is(
            'data.attributes.dailyWorkTimeLimits.0.chosenShiftHours',
            1.5 + 0.5,  # одна смена уже идет + одна завершена
        )
        t.json_is(
            'data.attributes.savingShiftFilterPeriod.from',
            time2iso_utc(day),
        )
        t.json_is(
            'data.attributes.savingShiftFilterPeriod.to',
            time2iso_utc(day + timedelta(days=14 - day.weekday())),
        )


async def test_week_stat(tap, api, dataset, now, tzone):
    with tap.plan(11, 'Правильность подсчета статистики за неделю'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 16,
                'max_week_hours': 80,
                'recommended_week_hours': 40,
                'duration_between_stores': 45 * 60,
                'shift_close_time': time(11, 30, 55),
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Начало недели
        _now = now(tz=tzone(cluster.tz)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        _start = _now - timedelta(days=_now.weekday())

        # Проверять будем с запасом в пару дней спереди и сзади, чтобы проверить
        # правильность интервала
        _start = _start - timedelta(days=2)

        for i in range(14 + 2 + 2):
            _current = _start + timedelta(days=i)

            await dataset.courier_shift(
                cluster=cluster,
                store=store,
                courier=courier,
                status='waiting',
                started_at=_current.replace(hour=12),
                closes_at=_current.replace(hour=13, minute=30),
            )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.id', courier.courier_id)
        t.json_is('data.type', 'settings')

        # Лимиты текущей недели
        t.json_is(
            'data.attributes.workTimeLimit.currentWeek.maxShiftHours',
            cluster.courier_shift_setup.max_week_hours
        )
        t.json_is(
            'data.attributes.workTimeLimit.currentWeek.recommendedShiftHours',
            cluster.courier_shift_setup.recommended_week_hours
        )
        t.json_is(
            'data.attributes.workTimeLimit.currentWeek.chosenShiftHours',
            1.5 * 7,  # в день по смене
        )

        # Лимиты следующей недели
        t.json_is(
            'data.attributes.workTimeLimit.nextWeek.maxShiftHours',
            cluster.courier_shift_setup.max_week_hours
        )
        t.json_is(
            'data.attributes.workTimeLimit.nextWeek.recommendedShiftHours',
            cluster.courier_shift_setup.recommended_week_hours
        )
        t.json_is(
            'data.attributes.workTimeLimit.nextWeek.chosenShiftHours',
            1.5 * 7,  # в день по смене
        )


async def test_auth_headers(tap, api):
    with tap.plan(9, 'Проверка заголовков авторизации'):
        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
        )

        t.status_is(401, diag=True)
        t.json_has('errors')

        t.json_is('errors.0.id', 'authorization')
        t.json_is('errors.0.type', 'error')
        t.json_is('errors.0.attributes.code', 'unauthorized')
        t.json_is('errors.0.attributes.title', 'Require auth parameters')
        t.json_is('errors.0.attributes.source', None)
        t.json_has('meta')


async def test_auth_not_found(tap, api, uuid):
    with tap.plan(9, 'Проверка нахождения курьера'):
        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': uuid(),
                'X-YaTaxi-Driver-Profile-Id': uuid(),
            }
        )

        t.status_is(401, diag=True)
        t.json_has('errors')

        t.json_is('errors.0.id', 'authorization')
        t.json_is('errors.0.type', 'error')
        t.json_is('errors.0.attributes.code', 'unauthorized')
        t.json_is('errors.0.attributes.title', 'Courier not found')
        t.json_is('errors.0.attributes.source', None)
        t.json_has('meta')


async def test_auth_no_active(tap, api, dataset):
    with tap.plan(9, 'Проверка включения кластера'):
        courier = await dataset.courier(status='disabled')

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )

        t.status_is(401, diag=True)
        t.json_has('errors')

        t.json_is('errors.0.id', 'authorization')
        t.json_is('errors.0.type', 'error')
        t.json_is('errors.0.attributes.code', 'unauthorized')
        t.json_is('errors.0.attributes.title', 'Courier disabled')
        t.json_is('errors.0.attributes.source', None)
        t.json_has('meta')


async def test_auth_no_delivery_type(tap, api, dataset):
    with tap.plan(9, 'Проверка наличия типа доставки'):
        courier = await dataset.courier(delivery_type=None)

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )

        t.status_is(401, diag=True)
        t.json_has('errors')

        t.json_is('errors.0.id', 'authorization')
        t.json_is('errors.0.type', 'error')
        t.json_is('errors.0.attributes.code', 'unauthorized')
        t.json_is('errors.0.attributes.title', 'Delivery type not defined')
        t.json_is('errors.0.attributes.source', None)
        t.json_has('meta')


@pytest.mark.parametrize('vars_', (
    {
    }, {
        'external_ids': {},
    }, {
        'external_ids': {
            'eats': '1234567',
        },
    }, {
        'external_ids': {
            'eats': '1234567',
        },
    },
))
async def test_get_current(tap, api, dataset, vars_):
    with tap.plan(4, 'Получение текущих настроек после ошибки'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(
            cluster=cluster,
            vars=vars_,
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_has('data')

        await courier.reload()
        tap.eq(courier.cluster_id, cluster.cluster_id, 'Остался старый кластер')


async def test_recently_updated(tap, api, dataset, now):
    with tap.plan(4, 'Получение текущих настроек т.к. обновились недавно'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': '1234567',
                },
                'cluster_updated': now() - timedelta(hours=1),
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_has('data')

        await courier.reload()
        tap.eq(courier.cluster_id, cluster.cluster_id, 'Остался старый кластер')


async def test_get_empty_request(tap, api, dataset, mock_client_response):
    with tap.plan(4, 'Получение настроек с ответом без региона'):
        # Отрицательный результат не влияет на обработку запроса
        mock_client_response(status=500)

        cluster = await dataset.cluster()
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': '1234567',
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_has('data')

        await courier.reload()
        tap.eq(courier.cluster_id, cluster.cluster_id, 'Остался старый кластер')


async def test_without_cluster(tap, api, dataset):
    with tap.plan(3, 'Получение настроек без кластера и без Едового id'):
        courier = await dataset.courier(cluster_id=None)

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )

        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'common.courier_not_found'
        )


async def test_with_unknown_cluster(tap, api, dataset, uuid):
    with tap.plan(3, 'Получение кластера, который потерялся'):
        courier = await dataset.courier(cluster_id=uuid())

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )

        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'common.courier_not_found'
        )


async def test_external_ids(tap, api, dataset, uuid):
    with tap.plan(5, 'Не менять Едовый id, если уже есть'):
        eda_id_old = uuid()

        cluster = await dataset.cluster()
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': eda_id_old,
                },
            },
        )

        tap.eq(
            (courier.vars.get('external_ids') or {}).get('eats', None),
            eda_id_old,
            'Едовый id есть',
        )

        eda_id_new = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-YaEda-CourierId': eda_id_new,
            }
        )

        t.status_is(200, diag=True)
        t.json_has('data')

        await courier.reload()

        tap.eq(
            (courier.vars.get('external_ids') or {}).get('eats', None),
            eda_id_old,
            'Едовый id остался старым'
        )


async def test_set_external_ids(tap, api, dataset, uuid):
    with tap.plan(5, 'Сохранение Едового id при запросе'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster)

        tap.eq((courier.vars.get('external_ids') or {}), {}, 'Едовый id пуст')

        eda_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_settings',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-YaEda-CourierId': eda_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_has('data')

        await courier.reload()

        tap.eq(
            (courier.vars.get('external_ids') or {}).get('eats', None),
            eda_id,
            'Едовый id обновился'
        )
