import datetime

import pytest

from stall.model.analytics.courier_metric import CourierMetric
from stall.model.analytics.courier_scoring import CourierScoring
import tests.dataset as dt


async def test_list_invalid(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')
    await t.post_ok(
        'api_report_data_courier_metrics_list',
        json={
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            },
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')

    await t.post_ok(
        'api_report_data_courier_metrics_list',
        json={
            'store_id': store.store_id,
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')

async def test_list_invalid_period(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_list',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2010, 5, 1),
            },
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'ER_BAD_REQUEST')

async def test_list_access(api, tap, dataset: dt):
    store = await dataset.store()
    other_store = await dataset.store()
    user = await dataset.user(store=store, role='executer')

    t = await api(user=user)
    request_body = {
        'store_id': store.store_id,
        'period': {
            'begin': datetime.date(2020, 5, 5),
            'end': datetime.date(2020, 5, 5),
        },
    }
    with tap.subtest(3, 'Ручка недоступна без пермита') as taps:
        t.tap = taps
        await t.post_ok(
            'api_report_data_courier_metrics_list',
            json=request_body
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

    with user.role as role:
        role.add_permit('courier_analytics', True)

        with tap.subtest(3, 'Пермит есть - ручка доступна') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_courier_metrics_list',
                json=request_body
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with tap.subtest(3, 'Ручка недоступна для другой лавки') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_courier_metrics_list',
                json={
                    'store_id': other_store.store_id,
                    'period': {
                        'begin': datetime.date(2020, 5, 5),
                        'end': datetime.date(2020, 5, 5),
                    },
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

async def test_list_empty(api, dataset: dt):
    # with tap.plan(4):
    store = await dataset.store()

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_list',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_is('couriers', [])


async def test_list_nonempty(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 1),
        datetime.date(2020, 5, 10)
    )
    store = await dataset.store()
    metrics = await dataset.courier_metric_daily(_store=store, period=period,
                                                 courier_cnt=2)
    tap.eq_ok(len(metrics), 30, 'Метрики сгенерированы на 10 дней')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_list',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('couriers')
    tap.eq_ok(len(t.res['json']['couriers']), 2,
              'Получены метрики по 2 курьерам')

async def test_list_two_days(api, dataset: dt, tap):
    store = await dataset.store()
    courier = await dataset.courier(store=store)

    await CourierMetric(
        store_id=store.store_id,
        courier_id=courier.courier_id,
        courier_name=courier.first_name,
        external_courier_id=courier.external_id,
        date=datetime.date(2020, 5, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        batch_cnt=2,
        check_valid_writeoffs_cost_lcy=0.0,
        complaints_10_cnt=3,
        complaints_all_cnt=3,
        cpo_cost=3273.7531617820923,
        cpo_orders=35,
        cte_dur_sec=8437,
        cur_dur_sec_not_start=0,
        cur_dur_sec_plan=21600,
        damage_writeoffs_cost_lcy=0.0,
        early_leaving_dur_sec=0,
        fact_shift_dur_sec=21605,
        fallback_cnt=2,
        grand_total_cnt=40,
        lateness_dur_sec=300,
        recount_writeoffs_cost_lcy=0.0,
        refund_writeoffs_cost_lcy=0.0,
        shift_dur_sec_work_capability=21600,
        shift_dur_sec_work_promise=21600,
        success_delivered_cnt=35,
        success_delivered_cnt_10=1,
        success_delivered_cnt_25=6,
        success_delivered_cnt_40=5,
        surge_cnt=0,
    ).save()

    await CourierMetric(
        store_id=store.store_id,
        courier_id=courier.courier_id,
        courier_name=courier.first_name,
        external_courier_id=courier.external_id,
        date=datetime.date(2020, 5, 2),
        time=datetime.datetime(2020, 5, 2, 0, 0, 0, 0),
        batch_cnt=3,
        check_valid_writeoffs_cost_lcy=0.0,
        complaints_10_cnt=1,
        complaints_all_cnt=2,
        cpo_cost=883.9784596798391,
        cpo_orders=36,
        cte_dur_sec=13967,
        cur_dur_sec_not_start=14400,
        cur_dur_sec_plan=25200,
        damage_writeoffs_cost_lcy=0.0,
        early_leaving_dur_sec=2400,
        fact_shift_dur_sec=25210,
        fallback_cnt=2,
        grand_total_cnt=39,
        lateness_dur_sec=1800,
        recount_writeoffs_cost_lcy=0.0,
        refund_writeoffs_cost_lcy=0.0,
        shift_dur_sec_work_capability=25200,
        shift_dur_sec_work_promise=25200,
        success_delivered_cnt=36,
        success_delivered_cnt_10=6,
        success_delivered_cnt_25=3,
        success_delivered_cnt_40=0,
        surge_cnt=1,
    ).save()

    await CourierScoring(
        statistics_week=datetime.date(2020, 4, 27),
        external_courier_id=courier.external_id,
        shift_delivery_type='foot',
        rating_position=15,
        orders=5,
        is_top=True,
        region_name='ru'
    ).save()

    await CourierScoring(
        statistics_week=datetime.date(2020, 4, 27),
        external_courier_id=courier.external_id,
        shift_delivery_type='car',
        rating_position=7,
        orders=27,
        is_top=True,
        region_name='ru'
    ).save()

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_list',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 5, 2),
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('couriers')
    t.json_is('couriers.*.external_courier_id', courier.external_id)
    t.json_is('couriers.*.courier_name', courier.first_name)
    tap.eq_ok(len(t.res['json']['couriers']), 1,
              'Получены метрики по 1 курьеру')
    t.json_is('couriers.0.rating_position.value', 7)
    t.json_is('couriers.0.rating_position.is_top', True)
    # cte_dur_sec / success_delivered_cnt / 60
    t.json_is(
        'couriers.0.cte.value',
        round((8437 + 13967) / (35 + 36) / 60)
    )
    # success_delivered_cnt
    t.json_is(
        'couriers.0.orders_success.value',
        35 + 36
    )
    # fact_shift_dur_sec // 60 // 60
    t.json_is(
        'couriers.0.sh.value',
        (21605 + 25210) // 60 // 60
    )
    t.json_is(
        'couriers.0.sh_sec.value',
        21605 + 25210
    )
    # 100 * success_delivered_cnt_25 / success_delivered_cnt
    t.json_is(
        'couriers.0.lateness.value',
        round(100 * (6 + 3) / (35 + 36))
    )
    # 100 * success_delivered_cnt_25 / success_delivered_cnt
    t.json_is(
        'couriers.0.lateness_25.value',
        round(100 * (6 + 3) / (35 + 36))
    )
    # 100 * success_delivered_cnt_40 / success_delivered_cnt
    t.json_is(
        'couriers.0.lateness_40.value',
        round(100 * (5 + 0) / (35 + 36))
    )
    # 100 * cur_dur_sec_not_start / cur_dur_sec_plan
    t.json_is(
        'couriers.0.shift_not_start.value',
        round(100 * (0 + 14400) / (21600 + 25200))
    )
    # 100 * (early_leaving_dur_sec + lateness_dur_sec) / cur_dur_sec_plan
    t.json_is(
        'couriers.0.early_leaving_lateness.value',
        round(100 * (0 + 2400 + 300 + 1800) / (21600 + 25200))
    )
    # Нет данных
    t.json_is(
        'couriers.0.orders_not_taken.value',
        0
    )
    # 60 * 60 * success_delivered_cnt / fact_shift_dur_sec
    t.json_is(
        'couriers.0.oph.value',
        round(60 * 60 * (35 + 36) / (21605 + 25210), 1)
    )
    # 100 * complaints_10_cnt / success_delivered_cnt
    t.json_is(
        'couriers.0.compensation.value',
        round(100 * (3 + 1) / (35 + 36))
    )


async def test_list_zero_data(api, dataset: dt):
    store = await dataset.store()
    courier = await dataset.courier(store=store)
    courier_metric = CourierMetric(
        date=datetime.date(2020, 5, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        courier_id=courier.courier_id,
        courier_name='Courier1',
        external_courier_id=courier.external_id
    )
    await courier_metric.save()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_list',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 5, 1),
            },
            'detalization': 'day',
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('couriers')
    t.json_is('couriers.0.courier_name', 'Courier1')
    t.json_is('couriers.0.courier_id', courier.courier_id)
    t.json_is('couriers.0.external_courier_id', courier.external_id)
    t.json_is('couriers.0.rating_position.value', None)
    t.json_is('couriers.0.rating_position.is_top', False)
    t.json_is('couriers.0.cte.value', 0)
    t.json_is('couriers.0.orders_success.value', 0)
    t.json_is('couriers.0.sh.value', 0)
    t.json_is('couriers.0.lateness.value', 0)
    t.json_is('couriers.0.lateness_25.value', 0)
    t.json_is('couriers.0.lateness_40.value', 0)
    t.json_is('couriers.0.shift_not_start.value', 0)
    t.json_is('couriers.0.early_leaving_lateness.value', 0)
    t.json_is('couriers.0.orders_not_taken.value', 0)
    t.json_is('couriers.0.oph.value', 0.0)
    t.json_is('couriers.0.compensation.value', 0)


@pytest.mark.parametrize(
    'is_top, expected',
    [
        (True, True),
        (False, False),
        (None, False),
    ]
)
async def test_is_top(api, tap, dataset, is_top, expected):
    with tap.plan(4, 'Корректные значения is_top'):
        store = await dataset.store()
        courier = await dataset.courier(store=store)
        courier_metric = CourierMetric(
            date=datetime.date(2020, 5, 1),
            time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
            store_id=store.store_id,
            courier_id=courier.courier_id,
            courier_name='Courier1',
            external_courier_id=courier.external_id
        )

        await CourierScoring(
            statistics_week=datetime.date(2020, 4, 27),
            external_courier_id=courier.external_id,
            shift_delivery_type='foot',
            rating_position=15,
            orders=5,
            is_top=is_top,
            region_name='ru'
        ).save()

        await courier_metric.save()

        t = await api(role='admin')

        await t.post_ok(
            'api_report_data_courier_metrics_list',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': datetime.date(2020, 5, 1),
                    'end': datetime.date(2020, 5, 1),
                },
                'detalization': 'day',
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('couriers.0.rating_position.is_top', expected)
