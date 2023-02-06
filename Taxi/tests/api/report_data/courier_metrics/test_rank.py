import datetime
import tests.dataset as dt

async def test_rank_invalid(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')
    await t.post_ok(
        'api_report_data_courier_metrics_rank',
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
        'api_report_data_courier_metrics_rank',
        json={
            'store_id': store.store_id,
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')

async def test_rank_invalid_period(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_rank',
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

async def test_rank_access(api, tap, dataset: dt):
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
            'api_report_data_courier_metrics_rank',
            json=request_body
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

    with user.role as role:
        role.add_permit('courier_analytics', True)

        with tap.subtest(3, 'Пермит есть - ручка доступна') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_courier_metrics_rank',
                json=request_body
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with tap.subtest(3, 'Ручка недоступна для другой лавки') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_courier_metrics_rank',
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

async def test_rank_empty(api, dataset: dt):
    store = await dataset.store()

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_rank',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2002, 5, 5),
                'end': datetime.date(2002, 5, 10),
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_is('rank.cte', None)
    t.json_is('rank.oph', None)
    t.json_is('rank.logistics_cancellation', None)
    t.json_is('rank.fallback', None)


async def test_rank(api, dataset: dt):
    store1 = await dataset.store(external_id='8404657')
    store2 = await dataset.store(external_id='8404658')
    not_similar_store = await dataset.store(external_id='8404659')
    some_date = datetime.date(2001, 5, 6)

    await dataset.CourierMetric(
        date=some_date,
        time=datetime.datetime(*some_date.timetuple()[:-2]),
        store_id=store1.store_id,
        store_cluster=2,
        store_factor=3,

        success_delivered_cnt=100,
        cte_dur_sec=9000,
        cpo_orders=100,
        fact_shift_dur_sec=10000,
        cancel_courier=1,
        cancel_other=9,
        fallback_cnt=10,
    ).save()

    await dataset.CourierMetric(
        date=some_date,
        time=datetime.datetime(*some_date.timetuple()[:-2]),
        store_id=store2.store_id,
        store_cluster=2,
        store_factor=3,

        success_delivered_cnt=100,
        cte_dur_sec=11000,
        cpo_orders=10,
        fact_shift_dur_sec=10000,
        cancel_courier=7,
        cancel_other=3,
        fallback_cnt=20,
    ).save()

    await dataset.CourierMetric(
        date=some_date,
        time=datetime.datetime(*some_date.timetuple()[:-2]),
        store_id=not_similar_store.store_id,
        store_cluster=5,
        store_factor=7,

        success_delivered_cnt=100,
        cte_dur_sec=7000,
    ).save()

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_rank',
        json={
            'store_id': store1.store_id,
            'period': {
                'begin': some_date,
                'end': some_date,
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    # cte_dur_sec / success_delivered_cnt / 60
    # Меньше - лучше
    # 9000 / 100 = 90 # 1 место
    t.json_is('rank.cte', 1)
    # 60 * 60 * (success_delivered_cnt - fallback_cnt) / fact_shift_dur_sec
    # Больше - лучше
    # (100 - 10) / 10000 = 0.01 # 1 место
    t.json_is('rank.oph', 1)
    # 100 * cancel_courier
    # / (cancel_client + cancel_courier + cancel_store + cancel_other)
    # Меньше лучше
    # 1 / (1 + 9) = 0.1 - # 1 место
    t.json_is('rank.logistics_cancellation', 1)
    # 100 * fallback_cnt / success_delivered_cnt
    # Больше - лучше
    # 10 / 100 = 0.1 # 2 место
    t.json_is('rank.fallback', 2)

    await t.post_ok(
        'api_report_data_courier_metrics_rank',
        json={
            'store_id': store2.store_id,
            'period': {
                'begin': some_date,
                'end': some_date,
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    # cte_dur_sec / success_delivered_cnt / 60
    # Меньше - лучше
    # 11000 / 100 = 110 # 2 место
    t.json_is('rank.cte', 2)
    # 60 * 60 * (success_delivered_cnt - fallback_cnt) / fact_shift_dur_sec
    # Больше - лучше
    # (100 - 20) / 10000 = 0.01 # 2 место
    t.json_is('rank.oph', 2)
    # 100 * cancel_courier
    # / (cancel_client + cancel_courier + cancel_store + cancel_other)
    # Меньше лучше
    # 7 / (3 + 7) = 0.7 # 2 место
    t.json_is('rank.logistics_cancellation', 2)
    # 100 * fallback_cnt / success_delivered_cnt
    # Больше - лучше
    # 20 / 100 = 0.2 # 1 место
    t.json_is('rank.fallback', 1)

    await t.post_ok(
        'api_report_data_courier_metrics_rank',
        json={
            'store_id': not_similar_store.store_id,
            'period': {
                'begin': some_date,
                'end': some_date,
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    # Меньше - лучше
    # cte_dur_sec / success_delivered_cnt / 60
    t.json_is('rank.cte', 1)

async def test_get_actual_metric(tap, dataset: dt):
    begin_date = datetime.date(2002, 5, 6)
    empty_date = datetime.date(2002, 5, 7)
    end_date = datetime.date(2002, 5, 8)
    store = await dataset.store()
    begin_metric, *_ = await dataset.courier_metric_daily(
        _store=store,
        courier_cnt=0,
        period=(begin_date, begin_date),
    )
    tap.ok(begin_metric, 'Метрика создана на 6 число')
    begin_metric.store_cluster = 3
    begin_metric.store_factor = 5
    await begin_metric.save()

    end_metric, *_ = await dataset.courier_metric_daily(
        _store=store,
        courier_cnt=0,
        period=(end_date, end_date),
    )
    tap.ok(end_metric, 'Метрика создана на 8 число')
    end_metric.store_cluster = 7
    end_metric.store_factor = 9
    await end_metric.save()

    with tap.subtest(4, 'Данные о лавке из первой метрки') as taps:
        cursor = await dataset.CourierMetric.list(
            by='last_cluster_and_factor',
            full=True,
            db={'mode': 'slave'},
            conditions=(
                ('date', '<=', begin_date),
            ),
        )
        metric = next(iter(
            it for it in cursor.list
            if it.store_id == store.store_id
        ), None)
        taps.ok(metric, 'Актуальная метрика получена')
        taps.eq_ok(metric.store_id, store.store_id,
                   'Актуальная метрика принадлежит правильной лавке')
        taps.eq_ok(metric.store_cluster, begin_metric.store_cluster,
                   'Кластер от begin_date')
        taps.eq_ok(metric.store_factor, begin_metric.store_factor,
                   'Фактор от begin_date')

    with tap.subtest(4, 'Данные о лавке изменились') as taps:
        cursor = await dataset.CourierMetric.list(
            by='last_cluster_and_factor',
            full=True,
            db={'mode': 'slave'},
            conditions=(
                ('date', '<=', end_date),
            ),
        )
        metric = next(iter(
            it for it in cursor.list
            if it.store_id == store.store_id
        ), None)
        taps.ok(metric, 'Актуальная метрика получена')
        taps.eq_ok(metric.store_id, store.store_id,
                   'Актуальная метрика принадлежит правильной лавке')
        taps.eq_ok(metric.store_cluster, end_metric.store_cluster,
                   'Кластер от end_date')
        taps.eq_ok(metric.store_factor, end_metric.store_factor,
                   'Фактор от end_date')

    with tap.subtest(
            4, 'На искомую дату данных о лавке нет, они были вчера'
    ) as taps:
        cursor = await dataset.CourierMetric.list(
            by='last_cluster_and_factor',
            full=True,
            db={'mode': 'slave'},
            conditions=(
                ('date', '<=', empty_date),
            ),
        )
        metric = next(iter(
            it for it in cursor.list
            if it.store_id == store.store_id
        ), None)
        taps.ok(metric, 'Актуальная метрика получена')
        taps.eq_ok(metric.store_id, store.store_id,
                   'Актуальная метрика принадлежит правильной лавке')
        taps.eq_ok(metric.store_cluster, begin_metric.store_cluster,
                   'Кластер от begin_date')
        taps.eq_ok(metric.store_factor, begin_metric.store_factor,
                   'Фактор от begin_date')
