import datetime
import pytest
from libstall.util import time2time


# pylint: disable=pointless-string-statement
'''
TEST PLAN:
- [x] Открыли-закрыли смену
- [x] Активная смена: открыта и ещё не закрыта
- [x] В рабочем времени не считаем паузу
- [x] Пауз может быть больше одной
- [x] Закрыли смену не закрыв паузу
- [x] Активная смена с активной паузой
- [x] Активная смена после паузы
- [x] Открыли смену вчера. Учитываем только часть за сегодня
- [x] Вчера открыли смену и начали паузу, сегодня сняли паузу и закрыли смену
- [x] Открыли смену сегодня и закрыли завтра. Учитываем только часть за сегодня
- [x] Сегодня открыли смену и начали паузу, завтра сняли паузу и закрыли смену
- [x] Событие о закрытии паузы приходит после закрытия смены
- [x] Заменить везде now на today
- [x] В ручке заменить now на end_timestamp
- [x] Timestamp None у unpause.
- [x] Timestamp None у unpause и до сейчас больше 20 минут.
- [x] Timestamp None у unpause и до конца смены меньше 20 минут
'''


@pytest.mark.parametrize(
    'note, shift_updates, expected',
    [
        (
            'Простой кейс: открыли-закрыли смену',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['close', datetime.timedelta(minutes=60)],
                ['now', datetime.timedelta(minutes=90)],
            ],
            # 60 минут смена
            60 * 60, # 60 минут
        ),
        (
            'Активная смена: открыта и ещё не закрыта',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['now', datetime.timedelta(minutes=30)],
            ],
            # 30 минут смена
            30 * 60, # 30 минут
        ),
        (
            'В рабочем времени не считаем паузу',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['pause', datetime.timedelta(minutes=20)],
                ['unpause', datetime.timedelta(minutes=30)],
                ['close', datetime.timedelta(minutes=60)],
                ['now', datetime.timedelta(minutes=90)],
            ],
            # 20 минут смена | 10 минут пауза | 30 минут смена
            50 * 60, # 50 минут
        ),
        (
            'Пауз может быть больше одной',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['pause', datetime.timedelta(minutes=20)],
                ['unpause', datetime.timedelta(minutes=30)],
                ['pause', datetime.timedelta(minutes=40)],
                ['unpause', datetime.timedelta(minutes=50)],
                ['close', datetime.timedelta(minutes=60)],
                ['now', datetime.timedelta(minutes=90)],
            ],
            # 20 минут смена | 10 минут пауза | 10 минут смена
            # | 10 минут пауза | 10 минут смена
            40 * 60, # 40 минут
        ),
        (
            'Закрыли смену не закрыв паузу',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['pause', datetime.timedelta(minutes=55)],
                ['close', datetime.timedelta(minutes=60)],
                ['now', datetime.timedelta(minutes=90)],
            ],
            # 55 минут смена | 5 минут пауза
            55 * 60, # 55 минут
        ),
        (
            'Активаня смена с активной паузой',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['pause', datetime.timedelta(minutes=25)],
                ['now', datetime.timedelta(minutes=30)],
            ],
             # 25 минут смена | 5 минут пауза
            25 * 60, # 25 минут
        ),
        (
            'Пауза длится больше 20 минут и не завершилась. '
            'Считаем её как 20 минут',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['pause', datetime.timedelta(minutes=25)],
                ['now', datetime.timedelta(minutes=60)],
            ],
            # 25 минут смена | 20 минут дефолтная пауза | 15 минут смена
            40 * 60, # 40 минут
        ),
        (
            'Пауза длится больше 20 минут и завершилась. '
            'Считаем её по ивенту завершения',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['pause', datetime.timedelta(minutes=25)],
                ['unpause', datetime.timedelta(minutes=55)],
                ['now', datetime.timedelta(minutes=60)],
            ],
             # 25 минут смена | 30 минут пауза | 5 минут смена
            30 * 60, # 30 минут
        ),
        (
            'Событие о закрытии паузы приходит после закрытия смены',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['pause', datetime.timedelta(minutes=50)],
                ['close', datetime.timedelta(minutes=60)],
                ['unpause', datetime.timedelta(minutes=61)],
                ['now', datetime.timedelta(minutes=90)],
            ],
             # 50 минут смена | 10 минут пауза
            50 * 60, # 50 минут
        ),
    ]
)
async def test_shift_time(
        api, tap, now, dataset, time_mock, tzone,
        clickhouse_client, note, shift_updates, expected
):
    # pylint: disable=unused-argument, too-many-locals, too-many-arguments
    with tap.plan(4, note):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        shift = await dataset.courier_shift(courier=courier, store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        for status, delta in shift_updates:
            if status == 'now':
                time_mock.set(today_at_12 + delta)
                continue

            await dataset.ch_grocery_shift_update(
                timestamp=today_at_12 + delta,
                courier=courier,
                store=store,
                shift_id=shift.courier_shift_id,
                status=status
            )

        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.shift_time', expected)


@pytest.mark.parametrize(
    'note, shift_updates, expected',
    [
        (
            'Дефолтная пауза 20 минут',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['pause', datetime.timedelta(minutes=20)],
                ['unpause',  datetime.timedelta(minutes=21)],
                ['close', datetime.timedelta(minutes=60)],
                ['now', datetime.timedelta(minutes=90)],
            ],
             # 20 минут смена | 20 минут пауза | 20 минут смена = 40 минут
            40 * 60,
        ),
        (
            'Пауза до конца смены меньше 20 минут',
            [
                ['open', datetime.timedelta(minutes=0)],
                ['pause', datetime.timedelta(minutes=20)],
                ['unpause',  datetime.timedelta(minutes=21)],
                ['close', datetime.timedelta(minutes=30)],
                ['now', datetime.timedelta(minutes=90)],
            ],
             # 20 минут смена | 10 минут пауза = 20 минут
            20 * 60,
        ),
    ]
)
async def test_unpause_without_timestamp(
        api, tap, now, dataset, time_mock, tzone,
        clickhouse_client, note, shift_updates, expected
):
    # pylint: disable=unused-argument, too-many-locals, too-many-arguments
    with tap.plan(4, 'У unpause не указан timestamp.\n' + note):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        shift = await dataset.courier_shift(courier=courier, store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        for status, delta in shift_updates:
            if status == 'now':
                time_mock.set(today_at_12 + delta)
                continue
            if status == 'unpause':
                await dataset.ch_grocery_shift_update(
                    timestamp=None,
                    _timestamp=today_at_12 + delta,
                    courier=courier,
                    store=store,
                    shift_id=shift.courier_shift_id,
                    status=status
                )
                continue
            await dataset.ch_grocery_shift_update(
                timestamp=today_at_12 + delta,
                courier=courier,
                store=store,
                shift_id=shift.courier_shift_id,
                status=status
            )

        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.shift_time', expected)


@pytest.mark.parametrize(
    'note, shift_updates, expected',
    [
        (
            'Открыли смену вчера. Учитываем только часть за сегодня',
            [
                ['open', datetime.timedelta(minutes=-30)],
                ['close', datetime.timedelta(minutes=60)],
                ['now', datetime.timedelta(minutes=90)],
            ],
             # 30 минут смена вчера | 60 смена сегодня
            60 * 60, # 60 минут
        ),
        (
            'Вчера открыли смену и начали паузу, '
            'сегодня сняли паузу и закрыли смену',
            [
                ['open', datetime.timedelta(minutes=-30)],
                ['pause', datetime.timedelta(minutes=-10)],
                ['unpause', datetime.timedelta(minutes=10)],
                ['close', datetime.timedelta(minutes=60)],
                ['now', datetime.timedelta(minutes=90)],
            ],
             # 20 минут смена вчера | 10 пауза вчера
             # | 10 мнут пауза сегодня | 50 минут смена сегодня
            50 * 60, # 60 минут
        ),
        (
            'Открыли смену сегодня и закрыли завтра. '
            'Учитываем только часть за сегодня',
            [
                ['open', datetime.timedelta(hours=22)],
                ['close', datetime.timedelta(hours=27)],
                ['now', datetime.timedelta(hours=28)],
            ],
             # 2 часа смена сегодня | 3 часа смена завтра
            2 * 60 * 60, # 2 часа
        ),
        (
            'Сегодня открыли смену и начали паузу, '
            'завтра сняли паузу и закрыли смену',
            [
                ['open', datetime.timedelta(hours=22)],
                ['pause', datetime.timedelta(hours=23)],
                ['unpause', datetime.timedelta(hours=25)],
                ['close', datetime.timedelta(hours=27)],
                ['now', datetime.timedelta(hours=28)],
            ],
             # 1 часа смена сегодня | 1 час паузы сегодня
             # | 1 час паузы завтар | 2 часа смена завтра
            1 * 60 * 60, # 1 час
        ),
    ]
)
async def test_day_range(
        api, tap, now, dataset, time_mock, tzone,
        clickhouse_client, note, shift_updates, expected
):
    # pylint: disable=unused-argument, too-many-locals, too-many-arguments
    with tap.plan(4, 'У unpause не указан timestamp.\n' + note):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        shift = await dataset.courier_shift(courier=courier, store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_0 = time2time(today.isoformat())

        for status, delta in shift_updates:
            if status == 'now':
                time_mock.set(today_at_0 + delta)
                continue
            await dataset.ch_grocery_shift_update(
                timestamp=today_at_0 + delta,
                courier=courier,
                store=store,
                shift_id=shift.courier_shift_id,
                status=status
            )

        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
                'date': today.isoformat()
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.shift_time', expected)


async def test_oph(api, tap, now, dataset, tzone, time_mock,
                   clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            4,
            'Время от окончания сборки заказа до того, как его забрал курьер'
    ):

        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        shift = await dataset.courier_shift(courier=courier, store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        time_mock.set(today_at_12 + datetime.timedelta(minutes=60))

        await dataset.ch_grocery_shift_update(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            courier=courier,
            store=store,
            shift_id=shift.courier_shift_id,
            status='open'
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            delivery_type='dispatch'
        )

        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            courier=courier,
            delivery_type='courier'
        )

        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(minutes=17),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_shift_update(
            timestamp=today_at_12 + datetime.timedelta(minutes=30),
            courier=courier,
            store=store,
            shift_id=shift.courier_shift_id,
            status='close'
        )

        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        # Курьер забрал 1 заказ за 30 минут => OPH = 2
        t.json_is('metrics.oph', 2)
