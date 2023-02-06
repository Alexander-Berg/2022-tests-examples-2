import pytest


async def test_basic(
        mockserver,
        stq_runner,
        happy_path_state_waybills_chosen,
        cargo_orders_db,
        run_create_orders,
        cargo_orders_draft_handler,
        cargo_orders_commit_handler,
):
    await run_create_orders(expect_fail=False)

    assert cargo_orders_draft_handler.times_called == 2
    assert cargo_orders_commit_handler.times_called == 2


async def test_nothing_changed_on_draft_errors(
        stq_runner,
        state_fallback_chosen,
        draft_5xx_handler,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        run_create_orders,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    await run_create_orders(expect_fail=True)

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['created-drafts'] == 0
    assert stats['stats']['inserted-drafts'] == 0
    assert stats['stats']['marked-as-resolved'] == 0
    assert stats['stats']['waybills-for-draft'] == 1


async def test_create_draft_failure(
        stq_runner,
        state_fallback_chosen,
        draft_400_handler,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        read_waybill_info,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test', kwargs={'waybill_ref': 'waybill_fb_3'},
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['created-drafts'] == 0
    assert stats['stats']['inserted-drafts'] == 0
    assert stats['stats']['marked-as-resolved'] == 1

    # check status
    for waybill in ['waybill_fb_3']:
        info = await read_waybill_info(waybill)
        assert info['dispatch']['status'] == 'resolved'
        assert info['dispatch']['resolution'] == 'technical_fail'


def test_do_nothing_if_commit_failed(
        state_successfully_drafted_but_commit_failed,
):

    result = state_successfully_drafted_but_commit_failed
    assert result['stats']['waybills-for-commit'] == 1
    assert result['stats']['committed-orders'] == 0
    assert result['stats']['lost-drafts'] == 0
    assert result['stats']['marked-as-committed'] == 0
    assert result['stats']['unset-drafts'] == 0


async def test_drafts_always_committed(
        state_fallback_chosen,
        stq_runner,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        mockserver,
        commit_5xx_handler,
        cargo_orders_db,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=True,
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-commit'] == 1
    assert stats['stats']['marked-as-committed'] == 0

    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def _commit_handler_ok(request):
        order_id = request.json['order_id']
        if order_id in cargo_orders_db.uuids2refs:
            cargo_orders_db.commit(order_id)
            return cargo_orders_db.build_commit_response_body(order_id)
        return mockserver.make_response(status=410, json={})

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test', kwargs={'waybill_ref': 'waybill_fb_3'},
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-commit'] == 1
    assert stats['stats']['marked-as-committed'] == 1


async def test_stq_success_after_status_accepted(
        state_fallback_chosen,
        stq_runner,
        pgsql,
        taxi_cargo_dispatch,
        mockserver,
        cargo_orders_draft_handler,
        cargo_orders_commit_handler,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""
    UPDATE cargo_dispatch.waybills
        SET status = 'processing';
    """,
    )

    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test', kwargs={'waybill_ref': 'waybill_fb_3'},
    )
    assert cargo_orders_draft_handler.times_called == 0
    assert cargo_orders_commit_handler.times_called == 0


@pytest.mark.config(
    CARGO_DISPATCH_INT_AUTHPROXY_429_ERROR_PROCESSING={
        'enabled': True,
        'reschedule_delay_ms': 200,
    },
)
async def test_429_on_draft_commit(
        state_fallback_chosen,
        stq_runner,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        cargo_orders_db,
        mockserver,
):
    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def _draft_handler(request):
        return mockserver.make_response(status=429, json={})

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=False,
    )

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-draft'] == 1

    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def _handler(request):
        order_id = cargo_orders_db.new_order(request.json['waybill_ref'])
        return {'order_id': order_id}

    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def _commit_handler(request):
        return mockserver.make_response(status=429, json={})

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=False,
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-commit'] == 1
    assert stats['stats']['marked-as-committed'] == 0


async def test_425_on_draft_commit(
        state_fallback_chosen,
        stq_runner,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        mockserver,
):
    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def _draft_handler(request):
        return mockserver.make_response(
            status=425, json={'code': 'too_early', 'message': 'please retry'},
        )

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=False,
    )

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-draft'] == 1


async def test_new_drafts_on_same_waybill_after_cleanup(
        state_removed_drafts_cleaned_up,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        stq_runner,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=True,
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-draft'] == 1
    assert stats['stats']['waybills-for-commit'] == 1
    assert stats['stats']['lost-drafts'] == 1
    assert stats['stats']['unset-drafts'] == 1


@pytest.fixture(name='state_successfully_drafted_but_commit_failed')
async def _state_successfully_drafted_but_commit_failed(
        state_fallback_chosen,
        commit_5xx_handler,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        stq_runner,
        run_create_orders,
):
    await run_create_orders(expect_fail=True)
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['inserted-drafts'] == 1
    return stats


def test_cleanup_removed_drafts(state_removed_drafts_cleaned_up):
    result = state_removed_drafts_cleaned_up
    assert result['stats']['waybills-for-processing'] == 0
    assert result['stats']['waybills-for-commit'] == 1
    assert result['stats']['lost-drafts'] == 1
    assert result['stats']['marked-as-committed'] == 0
    assert result['stats']['unset-drafts'] == 1


@pytest.fixture(name='state_removed_drafts_cleaned_up')
async def _state_removed_drafts_cleaned_up(
        state_successfully_drafted_but_commit_failed,
        mockserver,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        stq_runner,
):
    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def _handler(request):
        return mockserver.make_response(status=410, json={})

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=True,
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    return stats


async def test_order_do_not_process_twice(
        mockserver,
        state_fallback_chosen,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        stq_runner,
        run_create_orders,
        cargo_orders_db,
):
    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def _draft_handler_500(request):
        return mockserver.make_response(status=500)

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await run_create_orders(expect_fail=True)
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['committed-orders'] == 0
    assert stats['stats']['marked-as-committed'] == 0
    assert stats['stats']['waybills-for-draft'] == 1

    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def _draft(request):
        order_id = cargo_orders_db.new_order(request.json['waybill_ref'])
        return {'order_id': order_id}

    result = await run_create_orders()
    assert result['stats']['stq-success'] == 0
    assert result['stats']['stq-fail'] == 0


async def test_with_draft_4xx_error(
        mockserver,
        state_fallback_chosen,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        run_create_orders,
        draft_400_handler,
        cargo_orders_commit_handler,
        read_waybill_info,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await run_create_orders(expect_fail=False)

    assert cargo_orders_commit_handler.times_called == 0
    # check status
    info = await read_waybill_info('waybill_fb_3')
    assert info['dispatch']['status'] == 'resolved'
    assert info['dispatch']['resolution'] == 'technical_fail'


@pytest.mark.parametrize('code', [400, 403, 406])
async def test_with_commit_4xx_error(
        mockserver,
        state_fallback_chosen,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        stq_runner,
        cargo_orders_draft_handler,
        cargo_orders_db,
        read_waybill_info,
        code: str,
):
    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def commit(request):
        return mockserver.make_response(status=code)

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=False,
    )
    assert commit.times_called == 1

    # check status
    info = await read_waybill_info('waybill_fb_3')
    assert info['dispatch']['status'] == 'resolved'
    assert info['dispatch']['resolution'] == 'technical_fail'


async def test_mark_accepted_as_resolved(
        mock_claims_bulk_info,
        state_fallback_chosen,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        stq_runner,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        run_create_orders,
        read_waybill_info,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    happy_path_claims_segment_db.cancel_segment_by_user('seg3')
    await run_claims_segment_replication()
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    # check status
    info = await read_waybill_info('waybill_fb_3')
    assert info['dispatch']['status'] == 'accepted'

    result = await run_create_orders(expect_fail=False)
    assert result['stats']['stq-success'] == 1

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-processing'] == 1
    assert stats['stats']['marked-as-resolved'] == 1
    assert stats['stats']['already-resolved'] == 1
    assert stats['stats']['created-drafts'] == 0

    # check status and resolution
    info = await read_waybill_info('waybill_fb_3')
    assert info['dispatch']['status'] == 'resolved'
    assert info['dispatch']['resolution'] == 'cancelled'


async def test_mark_accepted_as_failed(
        mock_claims_bulk_info,
        state_fallback_chosen,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        stq_runner,
        run_create_orders,
        read_waybill_info,
        mockserver,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    mock_claims_bulk_info(segments_to_ignore=['seg3'])
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    result = await run_create_orders(expect_fail=False)
    assert result['stats']['stq-success'] == 1

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-processing'] == 1
    assert stats['stats']['marked-as-resolved'] == 1
    assert stats['stats']['already-resolved'] == 1
    assert stats['stats']['created-drafts'] == 0

    mock_claims_bulk_info(segments_to_ignore=[])

    # check status and resolution
    info = await read_waybill_info('waybill_fb_3')
    assert info['dispatch']['status'] == 'resolved'
    assert info['dispatch']['resolution'] == 'technical_fail'


async def test_stq_resolved_order(
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        state_cancelled_resolved,
        stq_runner,
        cargo_orders_db,
        mockserver,
        run_create_orders,
):

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test', kwargs={'waybill_ref': 'waybill_fb_3'},
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['created-drafts'] == 0
    assert stats['stats']['committed-orders'] == 0
    assert stats['stats']['already-resolved'] == 1
    assert stats['stats']['marked-as-resolved'] == 0

    result = await run_create_orders()
    assert result['stats']['stq-success'] == 0
    assert result['stats']['stq-fail'] == 0


async def test_retry_410(
        mockserver,
        state_fallback_chosen,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        stq_runner,
        cargo_orders_db,
        cargo_orders_draft_handler,
        cargo_orders_commit_handler,
        read_waybill_info,
):
    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def commit_1(request):
        return mockserver.make_response(status=410, json={})

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=True,
    )

    assert cargo_orders_draft_handler.times_called == 1
    assert commit_1.times_called == 1
    cargo_orders_draft_handler.flush()
    commit_1.flush()

    # check status
    info = await read_waybill_info('waybill_fb_3')
    assert info['dispatch']['status'] == 'accepted'
    assert 'resolution' not in info['dispatch']

    # Commit 200
    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def commit_2(request):
        order_id = request.json['order_id']
        if order_id in cargo_orders_db.uuids2refs:
            cargo_orders_db.commit(order_id)
            return cargo_orders_db.build_commit_response_body(order_id)
        return mockserver.make_response(status=410, json={})

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=False,
    )

    assert cargo_orders_draft_handler.times_called == 1
    assert commit_2.times_called == 1

    # check status
    info = await read_waybill_info('waybill_fb_3')
    assert info['dispatch']['status'] == 'processing'
    assert 'resolution' not in info['dispatch']


async def test_change_revision_after_write_draft_in_db(
        mockserver,
        stq_runner,
        happy_path_state_waybills_chosen,
        cargo_orders_db,
        pgsql,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        testpoint,
        waybill_id='waybill_fb_3',
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    @testpoint('change-revision-after-write-draft-in-db')
    def testpoint_callback(data):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            f"""
            UPDATE cargo_dispatch.waybills
            SET updated_ts = now(),
                revision = revision + 1
            WHERE external_ref = \'{waybill_id}\'
            RETURNING revision;
        """,
        )

    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def commit(request):
        order_id = request.json['order_id']
        if order_id in cargo_orders_db.uuids2refs:
            cargo_orders_db.commit(order_id)
            return cargo_orders_db.build_commit_response_body(order_id)
        return mockserver.make_response(status=410, json={})

    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def draft(request):
        order_id = cargo_orders_db.new_order(request.json['waybill_ref'])
        return {'order_id': order_id}

    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test', kwargs={'waybill_ref': waybill_id}, expect_fail=False,
    )
    assert testpoint_callback.times_called == 1
    assert draft.times_called == 1
    assert commit.times_called == 1
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['created-drafts'] == 1
    assert stats['stats']['committed-orders'] == 1
    assert stats['stats']['already-resolved'] == 0
    assert stats['stats']['marked-as-resolved'] == 0


async def test_change_revision_with_commit_4xx_error(
        mockserver,
        state_fallback_chosen,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        stq_runner,
        cargo_orders_db,
        read_waybill_info,
        testpoint,
        pgsql,
        code=400,
):
    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def _draft(request):
        order_id = cargo_orders_db.new_order(request.json['waybill_ref'])
        return {'order_id': order_id}

    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def commit(request):
        return mockserver.make_response(status=code)

    @testpoint('change-revision-before-commit')
    def testpoint_callback(data):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            f"""
            UPDATE cargo_dispatch.waybills
            SET updated_ts = now(),
                revision = revision + 1
            WHERE external_ref = \'{'waybill_fb_3'}\'
            RETURNING revision;
        """,
        )

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=True,
    )
    assert testpoint_callback.times_called == 1
    assert commit.times_called == 1

    @testpoint('change-revision-before-commit')
    def _testpoint_callback_2(data):
        pass

    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=False,
    )
    # check status
    info = await read_waybill_info('waybill_fb_3')
    assert info['dispatch']['status'] == 'resolved'
    assert info['dispatch']['resolution'] == 'technical_fail'


async def test_change_revision_with_draft_4xx_error(
        mockserver,
        state_fallback_chosen,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        stq_runner,
        cargo_orders_db,
        read_waybill_info,
        draft_400_handler,
        cargo_orders_commit_handler,
        pgsql,
        testpoint,
):
    @testpoint('change-revision-before-draft')
    def testpoint_callback(data):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            f"""
            UPDATE cargo_dispatch.waybills
            SET updated_ts = now(),
                revision = revision + 1
            WHERE external_ref = \'{'waybill_fb_3'}\'
            RETURNING revision;
        """,
        )

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=True,
    )

    assert testpoint_callback.times_called == 1
    assert cargo_orders_commit_handler.times_called == 0

    @testpoint('change-revision-before-draft')
    def _testpoint_callback(data):
        pass

    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=False,
    )

    # check status
    info = await read_waybill_info('waybill_fb_3')
    assert info['dispatch']['status'] == 'resolved'
    assert info['dispatch']['resolution'] == 'technical_fail'


async def test_change_revision_before_draft(
        mockserver,
        stq_runner,
        happy_path_state_waybills_chosen,
        cargo_orders_db,
        pgsql,
        cargo_orders_commit_handler,
        cargo_orders_draft_handler,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        testpoint,
        waybill_id='waybill_fb_3',
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    @testpoint('change-revision-before-draft')
    def testpoint_callback(data):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            f"""
            UPDATE cargo_dispatch.waybills
            SET updated_ts = now(),
                revision = revision + 1
            WHERE external_ref = \'{waybill_id}\'
            RETURNING revision;
        """,
        )

    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test', kwargs={'waybill_ref': waybill_id}, expect_fail=True,
    )
    assert testpoint_callback.times_called == 1
    assert cargo_orders_draft_handler.times_called == 1

    @testpoint('change-revision-before-draft')
    def _testpoint_callback(data):
        pass

    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test', kwargs={'waybill_ref': waybill_id}, expect_fail=False,
    )


@pytest.mark.config(
    CARGO_DISPATCH_CREATE_ORDERS_SETTINGS={
        'enabled': True,
        'waybills_for_draft_limit': 100,
        'waybills_for_commit_limit': 100,
        'rate_limit': {'limit': 10, 'interval': 1, 'burst': 20},
    },
)
@pytest.mark.parametrize(
    'quota, expected_waybills_drafts', [(10, 2), (2, 2), (1, 1), (3, 2)],
)
async def test_rate_limit(
        happy_path_state_waybills_chosen,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        run_create_orders,
        rps_limiter,
        pgsql,
        quota,
        expected_waybills_drafts,
):
    rps_limiter.set_budget('cargo-dispatch-create-orders', quota)
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await run_create_orders(
        should_set_stq=True, limit=expected_waybills_drafts,
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['created-drafts'] == expected_waybills_drafts

    statistics = await taxi_cargo_dispatch_monitor.get_metric('rps-limiter')
    limiter = statistics['cargo-dispatch-distlocks-limiter']
    assert limiter['quota-requests-failed'] == 0

    resource = limiter['resource_stat']['cargo-dispatch-create-orders']
    assert resource['quota-assigned'] == quota
    assert resource['limit'] == 10


async def test_schedule_stq(
        happy_path_state_waybills_chosen, run_create_orders, stq,
):
    result = await run_create_orders()
    assert result['stats']['stq-fail'] == 0
    assert result['stats']['stq-success'] == 2
    assert stq.cargo_dispatch_create_orders.times_called == 2
    call = stq.cargo_dispatch_create_orders.next_call()
    assert call['queue'] == 'cargo_dispatch_create_orders'


async def test_check_stq_on_unreplying(
        state_fallback_chosen, run_create_orders,
):
    result = await run_create_orders()
    assert result['stats']['stq-success'] == 1
    assert result['stats']['stq-fail'] == 0

    result = await run_create_orders()
    assert result['stats']['stq-success'] == 0
    assert result['stats']['stq-fail'] == 0


async def test_check_stq_on_replying(
        state_fallback_chosen, run_create_orders, mockserver,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)/bulk', regex=True,
    )
    async def _mock_error(request, queue_name):
        data = request.json
        response = {'tasks': []}
        for task in data['tasks']:
            response['tasks'].append(
                {
                    'task_id': task['task_id'],
                    'add_result': {'code': 500, 'description': 'task failed'},
                },
            )
        return response

    result = await run_create_orders(should_set_stq=False)
    assert result['stats']['stq-success'] == 0
    assert result['stats']['stq-fail'] == 1

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)/bulk', regex=True,
    )
    async def _mock_success(request, queue_name):
        data = request.json
        response = {'tasks': []}
        for task in data['tasks']:
            response['tasks'].append(
                {'task_id': task['task_id'], 'add_result': {'code': 200}},
            )
        assert len(response['tasks']) == 1
        assert response['tasks'][0]['task_id'] == 'waybill_fb_3'
        return response

    result = await run_create_orders(should_set_stq=False)
    assert result['stats']['stq-success'] == 1
    assert result['stats']['stq-fail'] == 0


async def test_taxi_requirements_order_draft(
        state_fallback_chosen_with_taxi_requirements,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        run_create_orders,
        mockserver,
        cargo_orders_db,
):
    await state_fallback_chosen_with_taxi_requirements(
        taxi_requirements={'kirslayk_property': 'property'},
    )
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def _draft(request):
        order_id = cargo_orders_db.new_order(request.json['waybill_ref'])
        assert request.json['requirements'] == {
            'door_to_door': True,
            'kirslayk_property': 'property',
            'taxi_classes': ['express', 'courier'],
        }
        return {'order_id': order_id}

    await run_create_orders()
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-draft'] == 1
    assert stats['stats']['created-drafts'] == 1
    assert stats['stats']['waybills-for-commit'] == 1
    assert stats['stats']['committed-orders'] == 1
    assert stats['stats']['failed-on-commit'] == 0


@pytest.mark.parametrize(
    'due, draft_times_called',
    [('2020-01-27T19:55:00+00:00', 1), ('broken_time', 0)],
)
async def test_lookup_requirements_due(
        state_fallback_chosen_with_taxi_requirements,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        run_create_orders,
        mockserver,
        cargo_orders_db,
        due,
        draft_times_called,
        propose_from_segments,
        run_choose_waybills,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    await propose_from_segments(
        'fallback_router', 'waybill_fb_3', 'seg3', lookup_extra={'due': due},
    )
    await run_choose_waybills()

    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def _draft(request):
        order_id = cargo_orders_db.new_order(request.json['waybill_ref'])
        assert request.json['requirements']['lookup_extra']['due'] == due
        return {'order_id': order_id}

    await run_create_orders(should_set_stq=True)

    assert _draft.times_called == draft_times_called
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['waybills-for-draft'] == 1
    assert stats['stats']['created-drafts'] == draft_times_called
    assert stats['stats']['marked-as-resolved'] == 1 - draft_times_called


@pytest.mark.now('2020-04-01T10:35:02+0000')
async def test_oldest_waybill_lag(
        state_fallback_chosen,
        stq_runner,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        mockserver,
        commit_5xx_handler,
        pgsql,
        cargo_orders_draft_handler,
        waybill_ref='waybill_fb_3',
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
    UPDATE cargo_dispatch.waybills
    SET updated_ts='2020-04-01T10:35:01+0000'
        """,
    )

    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test', kwargs={'waybill_ref': waybill_ref}, expect_fail=True,
    )

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['draft-oldest-waybill-lag-ms'] == 1000
    assert stats['stats']['commit-oldest-waybill-lag-ms'] == 1000

    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
    UPDATE cargo_dispatch.waybills
    SET updated_ts='2020-04-01T10:35:00+0000'
        """,
    )

    # check that draft lag don't calculated

    await stq_runner.cargo_dispatch_create_orders.call(
        task_id='test', kwargs={'waybill_ref': waybill_ref}, expect_fail=True,
    )

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    assert stats['stats']['draft-oldest-waybill-lag-ms'] == 1000
    assert stats['stats']['commit-oldest-waybill-lag-ms'] == 2000
