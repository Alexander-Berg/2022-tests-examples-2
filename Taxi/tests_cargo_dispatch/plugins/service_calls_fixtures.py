"""Calls to cargo-dispatch API and jobs.

To request a handler and work with response object use `request_*()` fixtures.

To just get 200-OK response body use `get_*()` or `read_*()` fixtures.

To start a job use `run_<task name>()` fixtures.
"""
import uuid

import pytest

CLAIM_SEGMENTS_REPLICATION = 'cargo-dispatch-claim-segments-replication'
CHOOSE_ROUTERS = 'cargo-dispatch-choose-routers'
CHOOSE_WAYBILLS = 'cargo-dispatch-choose-waybills'
CREATE_ORDERS = 'cargo-dispatch-create-orders'
FALLBACK_ROUTER = 'fallback-router'
NOTIFY_ORDERS = 'cargo-dispatch-notify-orders'
NOTIFY_CLAIMS = 'cargo-dispatch-notify-claims'
EXPIRED_ORDERS = 'cargo-dispatch-expired-orders'
SEGMENTS_JOURNAL_MOVER = 'cargo-dispatch-segments-journal-mover'
WAYBILLS_JOURNAL_MOVER = 'cargo-dispatch-waybills-journal-mover'
WORKER_STATS_MONITOR = 'cargo-dispatch-worker-stats-monitor'
REPLACE_CHOSEN_ROUTERS = 'cargo-dispatch-replace-chosen-routers'

CLAIMS_POINT_BASE: dict = {'type': 'source', 'label': 'label', 'phones': []}

CLAIMS_ROUTE_POINT: dict = {
    'address': {'fullname': 'SEND IT TO ORDERS', 'coordinates': [1.0, 2.0]},
    **CLAIMS_POINT_BASE,
}

CLAIMS_NEW_ROUTE: list = [{'id': 1, **CLAIMS_ROUTE_POINT}]

CLAIMS_NEW_POINT: dict = {
    **CLAIMS_POINT_BASE,
    'need_confirmation': True,
    'visit_order': 1,
    'actions': [],
}


@pytest.fixture(name='request_segment_journal')
def _request_segment_journal(taxi_cargo_dispatch):
    async def _wrapper(router_id, cursor=None, without_duplicates=None):
        body = {'router_id': router_id}
        if cursor is not None:
            body['cursor'] = cursor
        if without_duplicates is not None:
            body['without_duplicates'] = without_duplicates
        response = await taxi_cargo_dispatch.post(
            '/v1/segment/dispatch-journal', json=body,
        )
        return response

    return _wrapper


@pytest.fixture(name='read_segment_journal')
def _read_segment_journal(request_segment_journal):
    async def _wrapper(*args, **kwargs):
        response = await request_segment_journal(*args, **kwargs)
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='request_segment_info')
def _request_segment_info(taxi_cargo_dispatch):
    async def _wrapper(segment_id, min_revision: int = None):
        params = {'segment_id': segment_id}
        if min_revision:
            params['min_revision'] = min_revision

        response = await taxi_cargo_dispatch.post(
            '/v1/segment/info', params=params,
        )
        return response

    return _wrapper


@pytest.fixture(name='get_segment_info')
def _get_segment_info(request_segment_info):
    async def _wrapper(segment_id, min_revision: int = None):
        response = await request_segment_info(segment_id, min_revision)
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='get_admin_segment_info')
def _get_admin_segment_info(taxi_cargo_dispatch):
    async def _wrapper(segment_id):
        response = await taxi_cargo_dispatch.post(
            '/v1/admin/segment/info', params={'segment_id': segment_id},
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='waybill_mark_order_fail')
def _waybill_mark_order_fail(
        taxi_cargo_dispatch,
        default_order_fail_request,
        set_up_cargo_dispatch_reorder_exp,
):
    async def _wrapper(
            waybill_id: str,
            fail_reason: str,
            ticket: str = None,
            admin_cancel_reason: str = None,
            is_reorder_required: bool = False,
    ):
        await set_up_cargo_dispatch_reorder_exp(
            fail_reason=fail_reason,
            admin_cancel_reason_null=(admin_cancel_reason is None),
            is_reorder_required=is_reorder_required,
        )
        request = default_order_fail_request(
            waybill_id, fail_reason=fail_reason,
        )
        request.update(
            {'ticket': ticket, 'admin_cancel_reason': admin_cancel_reason},
        )

        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/mark/order-fail', request,
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='request_waybill_propose')
def _request_waybill_propose(taxi_cargo_dispatch):
    async def _wrapper(req_body):
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/propose', json=req_body,
        )
        return response

    return _wrapper


@pytest.fixture(name='get_waybill_info')
def _get_waybill_info(taxi_cargo_dispatch):
    async def _wrapper(waybill_external_ref: str, actual_waybill: bool = None):
        params: dict = {'waybill_external_ref': waybill_external_ref}
        if actual_waybill is not None:
            params['actual_waybill'] = actual_waybill
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/info', params=params,
        )
        assert response.status_code == 200

        return response

    return _wrapper


@pytest.fixture(name='read_waybill_info')
def _read_waybill_info(get_waybill_info):
    async def _wrapper(waybill_external_ref: str, actual_waybill: bool = None):
        response = await get_waybill_info(waybill_external_ref, actual_waybill)
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='request_waybill_ref_by_taxi_order_id')
def _request_waybill_ref_by_taxi_order_id(taxi_cargo_dispatch):
    async def _wrapper(taxi_order_id):
        data = {'taxi_order_id': taxi_order_id}
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/find-ref', json=data,
        )
        return response

    return _wrapper


@pytest.fixture(name='get_waybill_ref_by_taxi_order_id')
def _get_waybill_ref_by_taxi_order_id(request_waybill_ref_by_taxi_order_id):
    async def _wrapper(taxi_order_id):
        response = await request_waybill_ref_by_taxi_order_id(taxi_order_id)
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='get_waybill_path_info')
def _get_waybill_path_info(taxi_cargo_dispatch):
    async def _wrapper(waybill_external_ref: str):
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/path/info',
            params={'waybill_external_ref': waybill_external_ref},
        )
        return response

    return _wrapper


@pytest.fixture(name='run_claims_segment_replication')
def _run_claims_segment_replication(run_task_once):
    async def _wrapper():
        return await run_task_once(CLAIM_SEGMENTS_REPLICATION)

    return _wrapper


@pytest.fixture(name='run_choose_routers')
def _run_choose_routers(run_task_once):
    async def _wrapper():
        return await run_task_once(CHOOSE_ROUTERS)

    return _wrapper


@pytest.fixture(name='run_fallback_router')
def _run_fallback_router(run_task_once):
    async def _wrapper():
        return await run_task_once(FALLBACK_ROUTER)

    return _wrapper


@pytest.fixture(name='run_choose_waybills')
def _run_choose_waybills(run_task_once):
    async def _wrapper():
        return await run_task_once(CHOOSE_WAYBILLS)

    return _wrapper


@pytest.fixture(name='run_create_orders')
def _run_create_orders(run_task_once, taxi_cargo_dispatch, pgsql, stq_runner):
    async def _wrapper(should_set_stq=True, expect_fail=False, limit=100):
        await taxi_cargo_dispatch.tests_control(reset_metrics=True)
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            f"""
            SELECT
                external_ref
            FROM cargo_dispatch.waybills
            WHERE (status = 'accepted' AND order_id IS NULL)
                AND stq_create_orders_was_set IS NOT TRUE
            ORDER BY updated_ts
            LIMIT {limit}
        """,
        )
        result = await run_task_once(CREATE_ORDERS)
        if should_set_stq:
            for external_ref in cursor.fetchall():
                await stq_runner.cargo_dispatch_create_orders.call(
                    task_id='test',
                    kwargs={'waybill_ref': external_ref[0]},
                    expect_fail=expect_fail,
                )
        return result

    return _wrapper


@pytest.fixture(name='run_notify_orders')
def _run_notify_orders(run_task_once, taxi_cargo_dispatch, stq_runner, pgsql):
    async def _wrapper(should_set_stq=True, expect_fail=False):
        await taxi_cargo_dispatch.tests_control(reset_metrics=True)
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            """
            SELECT external_ref
            FROM cargo_dispatch.waybills
            WHERE NOT need_commit AND
            claims_changes_version != orders_notify_claims_changes_version
            ORDER BY updated_ts ASC;
        """,
        )
        result = await run_task_once(NOTIFY_ORDERS)
        if should_set_stq:
            for waybill in cursor.fetchall():
                await stq_runner.cargo_dispatch_notify_orders.call(
                    task_id=waybill[0],
                    kwargs={'waybill_ref': waybill[0]},
                    expect_fail=expect_fail,
                )

        return result

    return _wrapper


@pytest.fixture(name='run_expired_orders')
def _run_expired_orders(run_task_once):
    async def _wrapper():
        return await run_task_once(EXPIRED_ORDERS)

    return _wrapper


@pytest.fixture(name='run_worker_stats_monitor')
def _run_worker_stats_monitor(run_task_once):
    async def _wrapper():
        return await run_task_once(WORKER_STATS_MONITOR)

    return _wrapper


@pytest.fixture(name='run_replace_chosen_routers')
def _run_replace_chosen_routers(run_task_once):
    async def _wrapper():
        return await run_task_once(REPLACE_CHOSEN_ROUTERS)

    return _wrapper


@pytest.fixture(name='run_task_once')
def _run_task_once(taxi_cargo_dispatch, testpoint):
    async def _wrapper(task_name):
        @testpoint('%s::result' % task_name)
        def task_result(result):
            pass

        await taxi_cargo_dispatch.run_task(task_name)
        args = await task_result.wait_call()
        assert not task_result.has_calls

        return args['result']

    return _wrapper


@pytest.fixture(name='request_waybill_journal')
def _request_waybill_journal(taxi_cargo_dispatch):
    async def _wrapper(router_id, cursor=None, without_duplicates=None):
        body = {'router_id': router_id}
        if cursor is not None:
            body['cursor'] = cursor
        if without_duplicates is not None:
            body['without_duplicates'] = without_duplicates
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/dispatch-journal', json=body,
        )
        return response

    return _wrapper


@pytest.fixture(name='read_waybill_journal')
def _read_waybill_journal(request_waybill_journal):
    async def _wrapper(router_id, cursor=None):
        response = await request_waybill_journal(router_id, cursor)
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='run_notify_claims')
def _run_notify_claims(run_task_once, pgsql, stq_runner, taxi_cargo_dispatch):
    async def _wrapper(should_set_stq=True, expect_fail=False):
        await taxi_cargo_dispatch.tests_control(reset_metrics=True)
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            """
            SELECT segment_id FROM cargo_dispatch.segments
            WHERE orders_changes_version !=
                claims_notified_on_orders_changes_version
        """,
        )
        result = await run_task_once(NOTIFY_CLAIMS)
        if should_set_stq:
            for segment in cursor.fetchall():
                await stq_runner.cargo_dispatch_notify_claims.call(
                    task_id='test',
                    kwargs={'segment_id': segment[0]},
                    expect_fail=expect_fail,
                )
        return result

    return _wrapper


@pytest.fixture(name='run_segments_journal_mover')
def _run_segments_journal_mover(run_task_once):
    async def _wrapper():
        return await run_task_once(SEGMENTS_JOURNAL_MOVER)

    return _wrapper


@pytest.fixture(name='run_waybills_journal_mover')
def _run_waybills_journal_mover(run_task_once):
    async def _wrapper():
        return await run_task_once(WAYBILLS_JOURNAL_MOVER)

    return _wrapper


@pytest.fixture(name='mock_check_taxi_requirements', autouse=True)
def _mock_check_taxi_requirements(mockserver):
    @mockserver.json_handler('/cargo-orders/v1/check-taxi-requirements')
    def _mock(request):
        return {}


@pytest.fixture(autouse=True)
def mock_personal_data(mockserver):
    def _store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    def _retrieve(request):
        return {'id': request.json['id'], 'value': request.json['id'][:-3]}

    def _bulk_retrieve(request):
        result = {'items': []}
        for i in request.json['items']:
            result['items'].append({'id': i['id'], 'value': i['id'][:-3]})
        return result

    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        return _store(request)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        return _bulk_retrieve(request)


@pytest.fixture(name='mock_employee_timer')
async def _mock_employee_timer(mockserver):
    @mockserver.json_handler('/logistic-dispatcher/employee/timer')
    def handler(request):
        context.last_request = request.json
        if context.expected_request is not None:
            assert request.json == context.expected_request
        response = {
            'estimation_time_of_arrival': (
                '2020-07-20T11:08:00+00:00'
                if context.eta is None
                else context.eta
            ),
            'estimation_distance': 8.88,
        }
        if context.is_approximate is not None:
            response['is_approximate'] = context.is_approximate
        return response.copy()

    class Context:
        def __init__(self):
            self.expected_request = {
                'point_from': [37.5, 55.7],
                'point_to': [37.5, 55.7],
                'employer': 'eda',
                'park_driver_profile_id': 'park_id_1_driver_id_1',
            }
            self.handler = handler
            self.last_request = None
            self.is_approximate = None
            self.eta = None

    context = Context()
    return context


@pytest.fixture(name='mock_assign_external_driver')
async def _mock_assign_external_driver(mockserver):
    @mockserver.json_handler('/logistic-dispatcher/assign-external-driver')
    def handler(request):
        context.last_request = request.json
        return mockserver.make_response(
            status=context.status_code, json=context.response,
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.response = {'code': 'ERROR', 'message': 'some text'}
            self.handler = handler
            self.last_request = None

    context = Context()
    return context


@pytest.fixture(name='mock_driver_trackstory')
async def _mock_driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def handler(request):
        context.last_request = request.json
        if context.status_code == 200:
            return {
                'position': {
                    'direction': 0,
                    'lat': 55.7350642,
                    'lon': 37.57839202,
                    'speed': 0,
                    'timestamp': 1595243280,
                },
                'type': 'raw',
            }
        return mockserver.make_response(
            json={'message': f'failed with code {context.status_code}'},
            status=context.status_code,
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.handler = handler
            self.last_request = None

    context = Context()
    return context


@pytest.fixture(name='mock_claims_exchange_confirm')
def _mock_claims_exchange_confirm(mockserver):
    def _wrapper(expected_request: dict = None, response: dict = None):
        @mockserver.json_handler('/cargo-claims/v1/segments/exchange/confirm')
        def _exchange_confirm(request):
            if expected_request:
                assert request.json == expected_request
            return (
                {
                    'result': 'confirmed',
                    'new_status': 'delivering',
                    'new_claim_status': 'pickuped',
                    'new_route': CLAIMS_NEW_ROUTE,
                }
                if response is None
                else response
            )

        return _exchange_confirm

    _wrapper()
    return _wrapper


@pytest.fixture(name='mock_claims_return')
def _mock_claims_return(mockserver):
    def _wrapper(expected_request: dict = None, response: dict = None):
        @mockserver.json_handler('/cargo-claims/v1/segments/return')
        def return_handle(request):
            if expected_request:
                assert request.json == expected_request
            return (
                {
                    'result': 'confirmed',
                    'new_status': 'returning',
                    'new_claim_status': 'returning',
                    'new_route': CLAIMS_NEW_ROUTE,
                }
                if response is None
                else response
            )

        return return_handle

    _wrapper()
    return _wrapper


@pytest.fixture(name='mock_order_set_eta')
async def _mock_order_set_eta(mockserver):
    @mockserver.json_handler('/cargo-orders/v1/order/set-eta')
    def handler(request):
        context.last_request = request.json
        if context.status_code == 200:
            return {}
        return mockserver.make_response(
            json={'message': f'failed with code {context.status_code}'},
            status=context.status_code,
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.handler = handler
            self.last_request = None

    context = Context()
    return context


@pytest.fixture(name='mock_payment_set_performer', autouse=True)
def _mock_payment_set_performer(mockserver):
    @mockserver.json_handler('/cargo-payments/v1/payment/set-performer')
    def mock(request):
        context.requests.append(request.json)
        if context.status_code == 200:
            return {}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_payment_cancel', autouse=True)
def _mock_payment_cancel(mockserver):
    @mockserver.json_handler('/cargo-payments/v1/payment/cancel')
    def mock(request):
        context.requests.append(request)
        if context.status_code == 200:
            return {'payment_id': str(uuid.uuid4()), 'revision': 1}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='update_proposition_alive_batch_stq')
def _update_proposition_alive_batch_stq(
        taxi_cargo_dispatch, testpoint, stq, stq_runner,
):
    async def _wrapper(
            waybill_ref: str,
            wait_testpoint=False,
            revision=1,
            call=True,
            times_called=None,
            exec_tries=0,
    ):
        @testpoint('try-accept-proposition-retry')
        def testpoint_retry(result):
            assert result['waybill_ref'] == waybill_ref

        task_id = waybill_ref + '_' + str(revision)
        kwargs = {
            'new_waybill_ref': waybill_ref,
            'waybill_revision': revision,
            'is_offer_accepted': True,
        }

        if times_called is not None:
            assert (
                stq.cargo_alive_batch_confirmation.times_called == times_called
            )
        if stq.cargo_alive_batch_confirmation.times_called > 0:
            call = True
            stq_call = await stq.cargo_alive_batch_confirmation.wait_call()
            assert stq_call['id'] == task_id
            kwargs = stq_call['kwargs']
            assert kwargs['new_waybill_ref'] == waybill_ref
            assert kwargs['waybill_revision'] == revision
            assert kwargs['is_offer_accepted']

        if call:
            await stq_runner.cargo_alive_batch_confirmation.call(
                task_id=task_id,
                kwargs=kwargs,
                expect_fail=wait_testpoint,
                exec_tries=exec_tries,
            )

        if wait_testpoint:
            await testpoint_retry.wait_call()
        else:
            await taxi_cargo_dispatch.enable_testpoints()
            assert testpoint_retry.times_called == 0

    return _wrapper
