from stall.model.analytics.store_health import StoreHealth


async def test_rehash(tap, dataset):
    with tap.plan(18, 'Сохранение по конфликтному ключу'):
        store = await dataset.store()
        init_health = StoreHealth(
            entity='store',
            entity_id=store.store_id,
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            store_id=store.store_id,
            has_problem=False,
            problems_count=None,
            stores_total=0,
            stores_with_problems=0,
            children_total=None,
            children_with_problems=None,
            reason=None,
        )
        init_health.rehashed(supervisor_id=True)
        await init_health.save()

        with await StoreHealth.load(
            ('store', store.store_id),
            by='conflict',
        ) as health:
            tap.eq(health.entity, 'store', 'entity')
            tap.eq(health.entity_id, store.store_id, 'entity_id')
            tap.eq(health.has_problem, False, 'has_problem')
            tap.eq(health.problems_count, None, 'problems_count')
            tap.eq(health.stores_total, 0, 'stores_total')
            tap.eq(health.stores_with_problems, 0, 'stores_with_problems')
            tap.eq(health.children_total, None, 'children_total')
            tap.eq(
                health.children_with_problems, None, 'children_with_problems'
            )
            tap.eq(health.reason, None, 'reason')

        tap.note('Пересохраним по конфликтному ключу')
        update_health = StoreHealth(
            entity='store',
            entity_id=store.store_id,
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            store_id=store.store_id,
            has_problem=True,
            problems_count=1,
            stores_total=1,
            stores_with_problems=1,
            children_total=1,
            children_with_problems=1,
            reason='document',
        )
        update_health.rehashed(supervisor_id=True)
        await update_health.save()

        with await StoreHealth.load(
            ('store', store.store_id),
            by='conflict',
        ) as health:
            tap.eq(health.entity, 'store', 'entity')
            tap.eq(health.entity_id, store.store_id, 'entity_id')
            tap.eq(health.has_problem, True, 'has_problem')
            tap.eq(health.problems_count, 1, 'problems_count')
            tap.eq(health.stores_total, 1, 'stores_total')
            tap.eq(health.stores_with_problems, 1, 'stores_with_problems')
            tap.eq(health.children_total, 1, 'children_total')
            tap.eq(
                health.children_with_problems, 1, 'children_with_problems'
            )
            tap.eq(health.reason, 'document', 'reason')
