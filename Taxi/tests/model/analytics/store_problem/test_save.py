from mouse.exception import ErCoerce

from stall.model.analytics.store_problem import StoreProblem


async def test_simple(tap, uuid, dataset):
    with tap.plan(10, 'Тестим сохранение'):
        store = await dataset.store()
        head_supervisor_id = uuid()
        supervisor_id = uuid()
        order_type = uuid()
        order_status = uuid()
        reason = 'count'
        is_resolved = False
        details = []

        store_problem = StoreProblem(
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            head_supervisor_id=head_supervisor_id,
            supervisor_id=supervisor_id,
            store_id=store.store_id,
            timestamp_group=StoreProblem.calculate_timestamp_group(store),
            order_type=order_type,
            order_status=order_status,
            reason=reason,
            is_resolved=is_resolved,
            details=details
        )

        tap.eq(store_problem.company_id, store.company_id, 'company_id')
        tap.eq(store_problem.cluster_id, store.cluster_id, 'cluster_id')
        tap.eq(
            store_problem.head_supervisor_id,
            head_supervisor_id,
            'head_supervisor_id'
        )
        tap.eq(store_problem.supervisor_id, supervisor_id, 'supervisor_id')
        tap.eq(store_problem.store_id, store.store_id, 'store_id')
        tap.eq(store_problem.order_type, order_type, 'order_type')
        tap.eq(store_problem.order_status, order_status, 'order_status')
        tap.eq(store_problem.reason, reason, 'reason')
        tap.eq(store_problem.is_resolved, is_resolved, 'is_resolved')
        tap.eq(store_problem.details, details, 'details')


async def test_dataset(tap, dataset):
    with tap.plan(5, 'Тестим через dataset'):
        store = await dataset.store()
        reason = 'count'
        store_problem = await dataset.store_problem(
            store=store,
            reason=reason,
        )

        tap.eq(store_problem.company_id, store.company_id, 'company_id')
        tap.eq(store_problem.cluster_id, store.cluster_id, 'cluster_id')
        tap.eq(store_problem.store_id, store.store_id, 'store_id')
        tap.eq(store_problem.reason, reason, 'reason')
        tap.eq(store_problem.details, [], 'details')


async def test_details_count(tap, dataset):
    with tap.plan(4, 'Тестим details'):
        details = [{
            'reason': 'count',
            'order_ids': [1, 2],
            'count': 10,
            'count_threshold': 5,
        }]

        store_problem = await dataset.store_problem(
            reason='count',
            details=details,
        )

        saved_vars = store_problem.details[0]
        tap.eq(saved_vars.reason, details[0]['reason'], 'details.reason')
        tap.eq(
            saved_vars.order_ids, details[0]['order_ids'], 'details.order_ids'
        )
        tap.eq(saved_vars.count, details[0]['count'], 'details.count')
        tap.eq(
            saved_vars.count_threshold,
            details[0]['count_threshold'],
            'details.count_threshold'
        )


async def test_details_duration(tap, uuid, dataset):
    with tap.plan(4, 'Тестим details'):
        details = [{
            'reason': 'duration_total',
            'order_id': uuid(),
            'duration': 10,
            'duration_threshold': 5,
        }]
        store_problem = await dataset.store_problem(
            reason='duration_total',
            details=details,
        )

        saved_vars = store_problem.details[0]
        tap.eq(saved_vars.reason, details[0]['reason'], 'details.reason')
        tap.eq(saved_vars.order_id, details[0]['order_id'], 'details.order_id')
        tap.eq(saved_vars.duration, details[0]['duration'], 'details.duration')
        tap.eq(
            saved_vars.duration_threshold,
            details[0]['duration_threshold'],
            'details.duration_threshold'
        )


async def test_details_failed(tap, uuid, dataset):
    with tap.plan(1, 'Тестим ошибку сохранения details'):
        details = [{
            'reason': uuid(),
            'order_id': uuid(),
            'duration': 10,
            'duration_threshold': 5,
        }]

        with tap.raises(ErCoerce):
            await dataset.store_problem(
                details=details,
            )
