import datetime
import tests.dataset as dt

async def test_graph_invalid(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')
    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            },
            'detalization': 'day',
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'detalization': 'day',
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')
    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            },
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')

async def test_graph_invalid_period(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2010, 5, 1),
            },
            'detalization': 'day',
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'ER_BAD_REQUEST')

async def test_graph_access(api, tap, dataset: dt):
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
        'detalization': 'day',
    }
    with tap.subtest(3, 'Ручка недоступна без пермита') as taps:
        t.tap = taps
        await t.post_ok(
            'api_report_data_courier_metrics_graph',
            json=request_body
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

    with user.role as role:
        role.add_permit('courier_analytics', True)

        with tap.subtest(3, 'Пермит есть - ручка доступна') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_courier_metrics_graph',
                json=request_body
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with tap.subtest(3, 'Ручка недоступна для другой лавки') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_courier_metrics_graph',
                json={
                    'store_id': other_store.store_id,
                    'period': {
                        'begin': datetime.date(2020, 5, 5),
                        'end': datetime.date(2020, 5, 5),
                    },
                    'detalization': 'day',
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

async def test_graph_empty(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            },
            'detalization': 'day',
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    t.json_is('graphs.cte', [])
    t.json_is('graphs.oph', [])
    t.json_is('graphs.logistics_cancellation', [])
    t.json_is('graphs.fallback', [])


async def test_graph_two_days(api, dataset: dt):
    store = await dataset.store()
    m1 = dataset.CourierMetric(
        date=datetime.date(2020, 5, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        grand_total_cnt=78,
        success_delivered_cnt=77,
        success_delivered_cnt_25=33,
        success_delivered_cnt_40=69,
        fallback_cnt=11,
        cpo_orders=77,
        fact_shift_dur_sec=18005,
        cte_dur_sec=8055,
        cur_dur_sec_not_start=3600,
        cur_dur_sec_plan=18000,
        early_leaving_dur_sec=600,
        lateness_dur_sec=300,
        shift_dur_sec_work_capability=25200,
        shift_dur_sec_work_promise=18000,
        cancel_client=1,
        cancel_courier=2,
        cancel_store=3,
        cancel_other=4,
    )
    m2 = dataset.CourierMetric(
        date=datetime.date(2020, 5, 2),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        grand_total_cnt=67,
        success_delivered_cnt=66,
        success_delivered_cnt_25=22,
        success_delivered_cnt_40=58,
        fallback_cnt=9,
        cpo_orders=66,
        fact_shift_dur_sec=20400,
        cte_dur_sec=9111,
        cur_dur_sec_not_start=0,
        cur_dur_sec_plan=21600,
        early_leaving_dur_sec=360,
        lateness_dur_sec=1200,
        shift_dur_sec_work_capability=28800,
        shift_dur_sec_work_promise=21600,
        cancel_client=5,
        cancel_courier=6,
        cancel_store=7,
        cancel_other=8,
    )
    await m1.save()
    await m2.save()

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 5, 2),
            },
            'detalization': 'day',
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    # cte_dur_sec / success_delivered_cnt / 60
    t.json_is('graphs.cte.0.value', round(8055 / 77 / 60))
    t.json_is('graphs.cte.1.value', round(9111 / 66 / 60))
    t.json_is('graphs.cte.0.threshold', 0)
    t.json_is('graphs.cte.0.date', '2020-05-01')

    # 60 * 60 * success_delivered_cnt / fact_shift_dur_sec
    t.json_is('graphs.oph.0.value', round(60 * 60 * (77 - 11) / 18005, 1))
    t.json_is('graphs.oph.1.value', round(60 * 60 * (66 - 9) / 20400, 1))
    t.json_is('graphs.oph.0.threshold', 0)
    t.json_is('graphs.oph.0.date', '2020-05-01')

    # 100 * cancel_courier
    # / (grand_total_cnt)
    t.json_is(
        'graphs.logistics_cancellation.0.value',
        round(100 * 2 / 78, 1)
    )
    t.json_is(
        'graphs.logistics_cancellation.1.value',
        round(100 * 6 / 67, 1)
    )
    t.json_is('graphs.logistics_cancellation.0.threshold', 0)
    t.json_is('graphs.logistics_cancellation.0.date', '2020-05-01')

    # 100 * fallback_cnt / grand_total_cnt
    t.json_is('graphs.fallback.0.value', round(100 * 11 / 78, 2))
    t.json_is('graphs.fallback.1.value', round(100 * 9 / 67, 2))
    t.json_is('graphs.fallback.0.threshold', 0)
    t.json_is('graphs.fallback.0.date', '2020-05-01')

    t.json_has('aggregations')
    # 100 * shift_dur_sec_work_promise / shift_dur_sec_work_capability
    t.json_is(
        'aggregations.shift_utilisation.value',
        round(100 * (18000 + 21600) / (25200 + 28800))
    )
    t.json_has('aggregations.shift_utilisation.threshold')
    # 100 * cur_dur_sec_not_start / cur_dur_sec_plan
    t.json_is(
        'aggregations.shift_not_start.value',
        round(100 * (3600 + 0) / (18000 + 21600))
    )
    t.json_has('aggregations.shift_not_start.threshold')
    # 100 * (early_leaving_dur_sec + lateness_dur_sec) / cur_dur_sec_plan
    t.json_is(
        'aggregations.early_leaving_lateness.value',
        round(100 * (600 + 360 + 300 + 1200) / (18000 + 21600))
    )
    t.json_has('aggregations.early_leaving_lateness.threshold')
    # 100 * success_delivered_cnt_25 / success_delivered_cnt
    t.json_is(
        'aggregations.lateness.value',
        round(100 * (33 + 22) / (77 + 66))
    )
    t.json_has('aggregations.lateness.threshold')
    t.json_is(
        'aggregations.lateness_25.value',
        round(100 * (33 + 22) / (77 + 66))
    )
    t.json_has('aggregations.lateness_25.threshold')
    t.json_is(
        'aggregations.lateness_40.value',
        round(100 * (69 + 58) / (77 + 66))
    )
    t.json_has('aggregations.lateness_40.threshold')
    # fact_shift_dur_sec // 60 // 60
    t.json_is('aggregations.sh.value', (18005 + 20400) // 60 // 60)
    t.json_hasnt('aggregations.sh.threshold')
    # success_delivered_cnt
    t.json_is('aggregations.orders_success.value', 77 + 66)
    t.json_hasnt('aggregations.orders_success.threshold')
    # Нет данных
    t.json_is('aggregations.orders_not_taken.value', 0)
    t.json_is('aggregations.orders_not_taken.threshold', None)

async def test_graph_zero_data(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 1),
        datetime.date(2020, 5, 1)
    )
    store = await dataset.store()
    metrics = await dataset.courier_metric_daily(_store=store, period=period,
                                                 courier_cnt=0)
    tap.eq_ok(len(metrics), 1, 'Метрики сгенерированы на 1 день')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
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
    t.json_has('graphs')
    t.json_is('graphs.cte.0.date', '2020-05-01')
    t.json_is('graphs.cte.0.value', None)
    t.json_is('graphs.cte.0.threshold', 0)

    t.json_is('graphs.oph.0.date', '2020-05-01')
    t.json_is('graphs.oph.0.value', None)
    t.json_is('graphs.oph.0.threshold', 0)

    t.json_is('graphs.logistics_cancellation.0.date', '2020-05-01')
    t.json_is('graphs.logistics_cancellation.0.value', None)
    t.json_is('graphs.logistics_cancellation.0.threshold', 0)

    t.json_is('graphs.fallback.0.date', '2020-05-01')
    t.json_is('graphs.fallback.0.value', None)
    t.json_is('graphs.fallback.0.threshold', 0)

    t.json_is('aggregations.shift_utilisation.value', 0)
    t.json_is('aggregations.shift_not_start.value', 0)
    t.json_is('aggregations.early_leaving_lateness.value', 0)
    t.json_is('aggregations.lateness.value', 0)
    t.json_is('aggregations.lateness_25.value', 0)
    t.json_is('aggregations.lateness_40.value', 0)
    t.json_is('aggregations.sh.value', 0)
    t.json_is('aggregations.orders_success.value', 0)
    t.json_is('aggregations.orders_not_taken.value', 0)


async def test_graph_week(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 4), # Понедельник
        datetime.date(2020, 5, 18)
    )
    store = await dataset.store()
    metrics = await dataset.courier_metric_daily(_store=store, period=period)
    tap.eq_ok(len(metrics), 30, 'Метрики сгенерированы на 2 недели')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 4),
                'end': datetime.date(2020, 5, 10),
            },
            'detalization': 'week'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['cte']), 1,
              'График cte за 1 неделю')
    t.json_is('graphs.cte.0.date', '2020-05-04')
    tap.eq_ok(len(t.res['json']['graphs']['oph']), 1,
              'График oph за 1 неделю')
    t.json_is('graphs.oph.0.date', '2020-05-04')
    tap.eq_ok(len(t.res['json']['graphs']['logistics_cancellation']), 1,
              'График logistics_cancellation за 1 неделю')
    t.json_is('graphs.logistics_cancellation.0.date', '2020-05-04')
    tap.eq_ok(len(t.res['json']['graphs']['fallback']), 1,
              'График fallback за 1 неделю')
    t.json_is('graphs.fallback.0.date', '2020-05-04')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 5),
                'end': datetime.date(2020, 5, 13),
            },
            'detalization': 'week'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['cte']), 2,
              'График cte за 2 недели')
    t.json_is('graphs.cte.0.date', '2020-05-05')
    t.json_is('graphs.cte.1.date', '2020-05-11')
    tap.eq_ok(len(t.res['json']['graphs']['oph']), 2,
              'График oph за 2 недели')
    t.json_is('graphs.oph.0.date', '2020-05-05')
    t.json_is('graphs.oph.1.date', '2020-05-11')
    tap.eq_ok(len(t.res['json']['graphs']['logistics_cancellation']), 2,
              'Графика logistics_cancellation за 2 недели')
    t.json_is('graphs.logistics_cancellation.0.date', '2020-05-05')
    t.json_is('graphs.logistics_cancellation.1.date', '2020-05-11')
    tap.eq_ok(len(t.res['json']['graphs']['fallback']), 2,
              'График fallback за 2 недели')
    t.json_is('graphs.fallback.0.date', '2020-05-05')
    t.json_is('graphs.fallback.1.date', '2020-05-11')

async def test_graph_month(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 4), # Понедельник
        datetime.date(2020, 6, 18)
    )
    store = await dataset.store()
    metrics = await dataset.courier_metric_daily(_store=store, period=period)
    tap.eq_ok(len(metrics), 92, 'Метрики сгенерированы на 2 месяца')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 4),
                'end': datetime.date(2020, 5, 18),
            },
            'detalization': 'month'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['cte']), 1,
              'График cte за 1 месяц')
    t.json_is('graphs.cte.0.date', '2020-05-04')
    tap.eq_ok(len(t.res['json']['graphs']['oph']), 1,
              'График oph за 1 месяц')
    t.json_is('graphs.oph.0.date', '2020-05-04')
    tap.eq_ok(len(t.res['json']['graphs']['logistics_cancellation']), 1,
              'Графика logistics_cancellation за 1 месяц')
    t.json_is('graphs.logistics_cancellation.0.date', '2020-05-04')
    tap.eq_ok(len(t.res['json']['graphs']['fallback']), 1,
              'График fallback за 1 месяц')
    t.json_is('graphs.fallback.0.date', '2020-05-04')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 6, 20),
            },
            'detalization': 'month'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['cte']), 2,
              'График cte за 2 недели')
    t.json_is('graphs.cte.0.date', '2020-05-01')
    t.json_is('graphs.cte.1.date', '2020-06-01')
    tap.eq_ok(len(t.res['json']['graphs']['oph']), 2,
              'График oph за 2 недели')
    t.json_is('graphs.oph.0.date', '2020-05-01')
    t.json_is('graphs.oph.1.date', '2020-06-01')
    tap.eq_ok(len(t.res['json']['graphs']['logistics_cancellation']), 2,
              'График logistics_cancellation за 2 недели')
    t.json_is('graphs.logistics_cancellation.0.date', '2020-05-01')
    t.json_is('graphs.logistics_cancellation.1.date', '2020-06-01')
    tap.eq_ok(len(t.res['json']['graphs']['fallback']), 2,
              'График fallback за 2 недели')
    t.json_is('graphs.fallback.0.date', '2020-05-01')
    t.json_is('graphs.fallback.1.date', '2020-06-01')

async def test_graph_month_by_days(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 1),
        datetime.date(2020, 5, 31)
    )
    store = await dataset.store()
    metrics = await dataset.courier_metric_daily(_store=store, period=period)
    tap.eq_ok(len(metrics), 62, 'Метрики сгенерированы на 2 месяца')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 5, 31),
            },
            'detalization': 'day'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['cte']), 31,
              'График cte за 1 месяц')
    t.json_is('graphs.cte.0.date', '2020-05-01')
    t.json_is('graphs.cte.30.date', '2020-05-31')
    tap.eq_ok(len(t.res['json']['graphs']['oph']), 31,
              'График oph за 1 месяц')
    t.json_is('graphs.oph.0.date', '2020-05-01')
    t.json_is('graphs.oph.30.date', '2020-05-31')
    tap.eq_ok(len(t.res['json']['graphs']['logistics_cancellation']), 31,
              'График logistics_cancellation за 1 месяц')
    t.json_is('graphs.logistics_cancellation.0.date', '2020-05-01')
    t.json_is('graphs.logistics_cancellation.30.date', '2020-05-31')
    tap.eq_ok(len(t.res['json']['graphs']['fallback']), 31,
              'График fallback за 1 месяц')
    t.json_is('graphs.fallback.0.date', '2020-05-01')
    t.json_is('graphs.fallback.30.date', '2020-05-31')
