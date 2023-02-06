from collections import OrderedDict
from stall.model.analytics.store_health import StoreHealth, Threshold


async def test_load_thresholds(tap, cfg):
    with tap.plan(1, 'Все конфиги должны загружаться'):
        thresholds = await Threshold.load(cfg('health_monitoring'))
        tap.ok(thresholds, 'Все конфиги загрузились')


async def test_load_custom_threshold(tap, cfg, uuid):
    # pylint: disable=protected-access
    with tap.plan(5, 'Загрузка конфигов'):
        config_name = uuid()
        cfg._lazy_load()
        cfg._db.o[config_name] = {
            'entity_thresholds': {
                'cluster': {
                    'count': 2,
                    'percent': 10,
                    'lifetime': 500,
                }
            }
        }

        thresholds = await Threshold.load(cfg(config_name))

        tap.eq(len(thresholds), 1, '1 конфиг')
        tap.eq(thresholds[0].type, 'cluster', 'type')
        tap.eq(thresholds[0].count, 2, 'count')
        tap.eq(thresholds[0].percent, 10, 'percent')
        tap.eq(thresholds[0].lifetime, 500, 'lifetime')


async def test_recalculate(tap, dataset):
    with tap.plan(24, 'Ищем проблемы в кластере'):
        company = await dataset.company()
        cluster = await dataset.cluster()
        store_1 = await dataset.store(company=company, cluster=cluster)
        store_2 = await dataset.store(company=company, cluster=cluster)
        supervisor_1 = await dataset.user(
            store=store_1, role='supervisor', stores_allow=[store_1.store_id]
        )
        supervisor_2 = await dataset.user(
            store=store_2, role='supervisor', stores_allow=[store_2.store_id]
        )
        await dataset.store_health(
            store=store_1,
            supervisor_id=supervisor_1.user_id,
            problems_count=2,
        )

        await dataset.store_health(
            store=store_2,
            supervisor_id=supervisor_2.user_id,
            problems_count=3,
        )

        await StoreHealth.recalculate(
            [company.company_id], [cluster.cluster_id]
        )

        supervisor_health = await StoreHealth.load(
            ['supervisor', supervisor_1.user_id],
            by='conflict'
        )
        tap.eq(supervisor_health.has_problem, True, 'У супервайзера проблемы')
        tap.eq(supervisor_health.problems_count, 2, 'problems_count')
        tap.eq(supervisor_health.children_total, 1, 'children_total')
        tap.eq(
            supervisor_health.children_with_problems,
            1,
            'children_with_problems',
        )
        tap.eq(supervisor_health.stores_total, 1, 'stores_total')
        tap.eq(
            supervisor_health.stores_with_problems, 1, 'stores_with_problems'
        )

        supervisor_health = await StoreHealth.load(
            ['supervisor', supervisor_2.user_id],
            by='conflict'
        )
        tap.eq(supervisor_health.has_problem, True, 'У супервайзера проблемы')
        tap.eq(supervisor_health.problems_count, 3, 'problems_count')
        tap.eq(supervisor_health.children_total, 1, 'children_total')
        tap.eq(
            supervisor_health.children_with_problems,
            1,
            'children_with_problems',
        )
        tap.eq(supervisor_health.stores_total, 1, 'stores_total')
        tap.eq(
            supervisor_health.stores_with_problems, 1, 'stores_with_problems'
        )

        cluster_health = await StoreHealth.load(
            ['cluster', cluster.cluster_id],
            by='conflict'
        )
        tap.eq(cluster_health.has_problem, True, 'В кластере проблемы')
        tap.eq(cluster_health.problems_count, 5, 'problems_count')
        tap.eq(cluster_health.children_total, 2, 'children_total')
        tap.eq(
            cluster_health.children_with_problems, 2, 'children_with_problems',
        )
        tap.eq(cluster_health.stores_total, 2, 'stores_total')
        tap.eq(
            cluster_health.stores_with_problems, 2, 'stores_with_problems'
        )

        company_health = await StoreHealth.load(
            ['company', company.company_id],
            by='conflict'
        )
        tap.eq(company_health.has_problem, True, 'В компании проблемы')
        tap.eq(company_health.problems_count, 5, 'problems_count')
        tap.eq(company_health.children_total, 1, 'children_total')
        tap.eq(
            company_health.children_with_problems, 1, 'children_with_problems',
        )
        tap.eq(company_health.stores_total, 2, 'stores_total')
        tap.eq(
            company_health.stores_with_problems, 2, 'stores_with_problems'
        )


async def test_empty_supervisor(tap, dataset):
    with tap.plan(18, 'Ищем проблемы супервайзера'):
        store = await dataset.store()
        supervisor = await dataset.user(
            store=store, role='supervisor', stores_allow=[store.store_id]
        )
        await dataset.store_health(
            store=store,
            supervisor_id=None,
        )

        await StoreHealth.recalculate([store.company_id], [store.cluster_id])

        empty_supervisor = await StoreHealth.load(
            ['supervisor', f'EMPTY:{store.company_id}:{store.cluster_id}'],
            by='conflict'
        )
        tap.eq(
            empty_supervisor.has_problem,
            True,
            'У пустого супервайзера проблемы'
        )
        tap.eq(empty_supervisor.problems_count, 1, 'problems_count')
        tap.eq(empty_supervisor.children_total, 1, 'children_total')
        tap.eq(
            empty_supervisor.children_with_problems,
            1,
            'children_with_problems',
        )
        tap.eq(empty_supervisor.stores_total, 1, 'stores_total')
        tap.eq(
            empty_supervisor.stores_with_problems, 1, 'stores_with_problems'
        )

        tap.note('Проставили лавке супервайзера')
        await dataset.store_health(
            store=store,
            supervisor_id=supervisor.user_id,
        )

        await StoreHealth.recalculate([store.company_id], [store.cluster_id])

        await empty_supervisor.reload()
        tap.eq(
            empty_supervisor.has_problem,
            False,
            'У пустого супервайзера всё хорошо'
        )
        tap.eq(empty_supervisor.problems_count, 0, 'problems_count')
        tap.eq(empty_supervisor.children_total, 0, 'children_total')
        tap.eq(
            empty_supervisor.children_with_problems,
            0,
            'children_with_problems',
        )
        tap.eq(empty_supervisor.stores_total, 0, 'stores_total')
        tap.eq(
            empty_supervisor.stores_with_problems, 0, 'stores_with_problems'
        )

        supervisor_health = await StoreHealth.load(
            ['supervisor', supervisor.user_id],
            by='conflict'
        )
        tap.eq(
            supervisor_health.has_problem, True, 'У супервайзера проблемы'
        )
        tap.eq(supervisor_health.problems_count, 1, 'problems_count')
        tap.eq(supervisor_health.children_total, 1, 'children_total')
        tap.eq(
            supervisor_health.children_with_problems,
            1,
            'children_with_problems',
        )
        tap.eq(supervisor_health.stores_total, 1, 'stores_total')
        tap.eq(
            supervisor_health.stores_with_problems, 1, 'stores_with_problems'
        )



async def test_toggle_problems(tap, cfg, dataset):
    # pylint: disable=protected-access, too-many-statements
    with tap.plan(4, 'Смотрим как стейты здоровья прорастают'):
        cfg._lazy_load()
        cfg._db.o['health_monitoring'] = {
            'entity_thresholds': {
                'supervisor': {
                    'percent': 50,
                },
                'cluster': {
                    'percent': 50,
                },
                'company': {
                    'count': 1,
                },
                'total': {
                    'count': 1,
                },
            }
        }
        company = await dataset.company()
        cluster_1 = await dataset.cluster()
        cluster_2 = await dataset.cluster()
        stores = OrderedDict()
        stores[0] = await dataset.store(company=company, cluster=cluster_1)
        stores[1] = await dataset.store(company=company, cluster=cluster_1)
        stores[2] = await dataset.store(company=company, cluster=cluster_1)
        stores[3] = await dataset.store(company=company, cluster=cluster_2)
        for store in stores.values():
            await dataset.store_health(
                store=store,
                problems_count=0,
            )

        with tap.subtest(6, 'Всё спокойно') as taps:
            await StoreHealth.recalculate(
                company.company_id, [cluster_1.cluster_id, cluster_2.cluster_id]
            )

            cluster_health = await StoreHealth.load(
                ['cluster', cluster_1.cluster_id],
                by='conflict'
            )
            taps.eq(
                cluster_health.has_problem, False, 'В кластере 1 нет проблем'
            )
            taps.eq(cluster_health.reason, None, 'Пустая причина')

            cluster_health = await StoreHealth.load(
                ['cluster', cluster_2.cluster_id],
                by='conflict'
            )
            taps.eq(
                cluster_health.has_problem, False, 'В кластере 2 нет проблем'
            )
            taps.eq(cluster_health.reason, None, 'Пустая причина')

            company_health = await StoreHealth.load(
                ['company', company.company_id],
                by='conflict'
            )
            taps.eq(company_health.has_problem, False, 'В компании проблемы')
            taps.eq(company_health.reason, None, 'Пустая причина')


        with tap.subtest(6, 'Загорелась 1 лавка из 3-х. Порог 50%') as taps:
            await dataset.store_health(
                store=stores[0],
                problems_count=1,
            )
            await StoreHealth.recalculate(
                company.company_id, [cluster_1.cluster_id, cluster_2.cluster_id]
            )

            cluster_health = await StoreHealth.load(
                ['cluster', cluster_1.cluster_id],
                by='conflict'
            )
            taps.eq(
                cluster_health.has_problem, False, 'В кластере 1 нет проблем'
            )
            taps.eq(cluster_health.reason, None, 'Пустая причина')

            cluster_health = await StoreHealth.load(
                ['cluster', cluster_2.cluster_id],
                by='conflict'
            )
            taps.eq(
                cluster_health.has_problem, False, 'В кластере 2 нет проблем'
            )
            taps.eq(cluster_health.reason, None, 'Пустая причина')

            company_health = await StoreHealth.load(
                ['company', company.company_id],
                by='conflict'
            )
            taps.eq(
                company_health.has_problem, False, 'В компании нет проблем'
            )
            taps.eq(company_health.reason, None, 'Пустая причина')

        with tap.subtest(6, 'Загорелась 2-ая лавка из 3-х. Порог 50%') as taps:
            await dataset.store_health(
                store=stores[1],
                problems_count=1,
            )
            await StoreHealth.recalculate(
                company.company_id, [cluster_1.cluster_id, cluster_2.cluster_id]
            )

            cluster_health = await StoreHealth.load(
                ['cluster', cluster_1.cluster_id],
                by='conflict'
            )
            taps.eq(
                cluster_health.has_problem, True, 'В кластере 1 ЕСТЬ проблемы'
            )
            taps.eq(
                cluster_health.reason, 'document', 'Лавки перегружены'
            )

            cluster_health = await StoreHealth.load(
                ['cluster', cluster_2.cluster_id],
                by='conflict'
            )
            taps.eq(
                cluster_health.has_problem, False, 'В кластере 2 нет проблем'
            )
            taps.eq(cluster_health.reason, None, 'Пустая причина')

            company_health = await StoreHealth.load(
                ['company', company.company_id],
                by='conflict'
            )
            taps.eq(
                company_health.has_problem, True, 'В компании ЕСТЬ проблемы'
            )
            taps.eq(
                company_health.reason, 'document', 'Кластер перегружен'
            )

        with tap.subtest(
                6, 'Потухла 1 лавка. 1 из 3-х горят. Порог 50%'
        ) as taps:
            await dataset.store_health(
                store=stores[0],
                problems_count=0,
            )
            await StoreHealth.recalculate(
                company.company_id, [cluster_1.cluster_id, cluster_2.cluster_id]
            )

            cluster_health = await StoreHealth.load(
                ['cluster', cluster_1.cluster_id],
                by='conflict'
            )
            taps.eq(
                cluster_health.has_problem, False, 'В кластере 1 нет проблем'
            )
            taps.eq(cluster_health.reason, None, 'Пустая причина')

            cluster_health = await StoreHealth.load(
                ['cluster', cluster_2.cluster_id],
                by='conflict'
            )
            taps.eq(
                cluster_health.has_problem, False, 'В кластере 2 нет проблем'
            )
            taps.eq(cluster_health.reason, None, 'Пустая причина')

            company_health = await StoreHealth.load(
                ['company', company.company_id],
                by='conflict'
            )
            taps.eq(company_health.has_problem, False, 'В компании проблемы')
            taps.eq(company_health.reason, None, 'Пустая причина')
