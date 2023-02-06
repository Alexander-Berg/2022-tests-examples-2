# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import typing as tp
import uuid

from cargo_dispatch_plugins import *  # noqa: F403 F401
import pytest


PROFILE_REQUEST = {
    'user': {'personal_phone_id': 'personal_phone_id_1'},
    'name': 'Насруло',
    'sourceid': 'cargo',
}


@pytest.fixture(name='get_default_profile_response')
def get_default_profile_resp():
    return {
        'dont_ask_name': False,
        'experiments': [],
        'name': 'Насруло',
        'personal_phone_id': 'personal_phone_id_1',
        'user_id': 'taxi_user_id_1',
    }


@pytest.fixture(autouse=True)
def mock_profile(mockserver, get_default_profile_response):
    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _profile(request):
        assert request.json == PROFILE_REQUEST
        return get_default_profile_response


@pytest.fixture(name='changedestinations_response')
def default_changedest_resp():
    return {
        'change_id': '3a78e3efbffb4700b8649c109e62b451',
        'name': 'comment ',
        'status': 'success',
        'value': [
            {
                'type': 'address',
                'country': 'Россия',
                'fullname': 'Россия, Москва, 8 Марта, 4',
                'geopoint': [33.1, 52.1],
                'locality': 'Москва',
                'porchnumber': '',
                'premisenumber': '4',
                'thoroughfare': '8 Марта',
            },
        ],
    }


@pytest.fixture(autouse=True)
def mock_nearest_zone(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/nearestzone')
    def _nearestzone(request):
        return {'nearest_zone': 'moscow'}

    return _nearestzone


@pytest.fixture(autouse=True)
def mock_changedestination(mockserver, changedestinations_response):
    @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    def _changedestinations(request):
        return changedestinations_response

    return _changedestinations


@pytest.fixture(name='mock_corp_api', autouse=True)
def _mock_corp_api(mockserver):
    @mockserver.json_handler(
        '/taxi-corp-integration/v1/client_tariff_plan/current',
    )
    def _corp_api(request):
        return {
            'tariff_plan_series_id': 'tariff_plan_id_123',
            'client_id': 'corp_client_id_12312312312312312',
            'date_from': '2020-01-22T15:30:00+00:00',
            'date_to': '2021-01-22T15:30:00+00:00',
        }


@pytest.fixture(name='mock_tariffs', autouse=True)
def _mock_tariffs(mockserver, load_json):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff/corp/current')
    def _tariffs(request):
        return {
            'id': 'tariff_id',
            'categories': load_json('categories.json'),
            'disable_paid_supply_price': False,
        }


@pytest.fixture(name='mock_order_change_destination')
def _mock_order_change_destination(mockserver):
    @mockserver.json_handler('/cargo-orders/v1/order/change-destination')
    def change_destination(request):
        return {}

    return change_destination


@pytest.fixture(name='mock_cargo_orders_performer_info', autouse=True)
def _mock_cargo_orders_performer_info(mockserver):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def handler(request):
        performers = list()
        if not context.no_performers:
            assert request.json['orders_ids']
            for order_id in request.json['orders_ids']:
                try:
                    uuid.UUID(order_id)
                except ValueError:
                    pytest.fail(
                        'order_id in request is cargo_order_id. Must be uuid',
                    )

                performers.append(
                    {
                        'order_id': order_id,
                        'order_alias_id': '1234',
                        'phone_pd_id': '+70000000000_id',
                        'name': 'Kostya',
                        'driver_id': 'driver_id_1',
                        'park_id': 'park_id_1',
                        'park_name': 'some_park_name',
                        'park_org_name': 'some_park_org_name',
                        'car_id': '123',
                        'car_number': 'А001АА77',
                        'car_model': 'KAMAZ',
                        'lookup_version': 1,
                        'tariff_class': 'cargo',
                        'revision': 1,
                        'transport_type': context.transport_type,
                    },
                )
        return {'performers': performers}

    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info-cached')
    async def cached_handler(request):
        performers = list()
        if not context.no_performers:
            assert request.json['orders_ids']
            for order_id in request.json['orders_ids']:
                try:
                    uuid.UUID(order_id)
                except ValueError:
                    pytest.fail(
                        'order_id in request is cargo_order_id. Must be uuid',
                    )

                performers.append(
                    {
                        'order_id': order_id,
                        'order_alias_id': '1234',
                        'phone_pd_id': '+70000000000_id',
                        'name': 'Kostya',
                        'driver_id': 'driver_id_1',
                        'park_id': 'park_id_1',
                        'park_name': 'some_park_name',
                        'park_org_name': 'some_park_org_name',
                        'car_id': '123',
                        'car_number': 'А001АА77',
                        'car_model': 'KAMAZ',
                        'lookup_version': 1,
                        'tariff_class': 'cargo',
                        'revision': 1,
                        'transport_type': context.transport_type,
                    },
                )
        return {'performers': performers}

    class Context:
        def __init__(self):
            self.handlers = [handler, cached_handler]
            self.no_performers = False
            self.transport_type = 'car'

    context = Context()

    return context


@pytest.fixture(name='mock_cargo_orders_bulk_info')
def _mock_cargo_orders_bulk_info(mockserver):
    def _wrapper(
            tariff_class: str = 'cargo',
            autocancel_reason: str = None,
            transport_type: str = None,
            admin_cancel_reason: str = None,
            order_error: dict = None,
            order_cancel_performer_reason: list = None,
    ):
        @mockserver.json_handler('/cargo-orders/v1/orders/bulk-info')
        def _handler(request):
            orders = []
            assert request.json['cargo_orders_ids']
            for order_id in request.json['cargo_orders_ids']:
                try:
                    uuid.UUID(order_id)
                except ValueError:
                    pytest.fail(
                        'order_id in request is cargo_order_id. Must be uuid',
                    )

                orders.append(
                    {
                        'order': {
                            'order_id': order_id,
                            'provider_order_id': 'taxi-id',
                            'presetcar_calc_id': 'cargo-pricing/v1/bbb',
                            'final_calc_id': 'cargo-pricing/v1/aaa',
                            'use_cargo_pricing': True,
                            'nondecoupling_client_final_calc_id': (
                                'cargo-pricing/v1/ccc'
                            ),
                        },
                        'performer_info': {
                            'order_id': order_id,
                            'order_alias_id': '1234',
                            'phone_pd_id': '+70000000000_id',
                            'name': 'Kostya',
                            'park_clid': 'park_clid1',
                            'driver_id': 'driver_id_1',
                            'park_id': 'park_id_1',
                            'park_name': 'some_park_name',
                            'park_org_name': 'some_park_org_name',
                            'car_id': '123',
                            'car_number': 'А001АА77',
                            'car_model': 'KAMAZ',
                            'lookup_version': 1,
                            'tariff_class': tariff_class,
                            'revision': 1,
                        },
                    },
                )
                if autocancel_reason is not None:
                    orders[-1]['order'][
                        'autocancel_reason'
                    ] = autocancel_reason

                if transport_type is not None:
                    orders[-1]['performer_info'][
                        'transport_type'
                    ] = transport_type

                if admin_cancel_reason is not None:
                    orders[-1]['order'][
                        'admin_cancel_reason'
                    ] = admin_cancel_reason

                if order_error is not None:
                    orders[-1]['order']['order_error'] = order_error

                if order_cancel_performer_reason is not None:
                    orders[-1]['order'][
                        'order_cancel_performer_reason_list'
                    ] = order_cancel_performer_reason
            return {'orders': orders}

        return _handler

    return _wrapper


@pytest.fixture(name='draft_400_handler')
def _draft_400_handler(mockserver):
    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def handler(request):
        return mockserver.make_response(status=400)

    return handler


@pytest.fixture(name='commit_5xx_handler')
def _commit_5xx_handler(mockserver):
    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def handler(request):
        return mockserver.make_response(status=500)

    return handler


@pytest.fixture(name='commit_400_handler')
def _commit_400_handler(cargo_orders_commit_handler, mockserver):
    @mockserver.json_handler('/cargo-orders/v1/order/commit')
    def handler(request):
        return mockserver.make_response(status=400, json={})

    return handler


@pytest.fixture(name='state_fallback_chosen')
async def _state_fallback_chosen(
        happy_path_state_fallback_waybills_proposed, run_choose_waybills,
):
    result = await run_choose_waybills()
    assert result['stats']['accepted-waybills'] == 1
    return result


@pytest.fixture(name='state_fallback_chosen_with_taxi_requirements')
async def _state_fallback_chosen_with_taxi_requirements(
        happy_path_state_fallback_proposed_args, run_choose_waybills,
):
    async def _wrapper(taxi_requirements):
        await happy_path_state_fallback_proposed_args(taxi_requirements)
        result = await run_choose_waybills()
        assert result['stats']['accepted-waybills'] == 1
        return result

    return _wrapper


@pytest.fixture(name='draft_5xx_handler')
def _draft_5xx_handler(cargo_orders_draft_handler, mockserver):
    @mockserver.json_handler('/cargo-orders/v1/order/draft')
    def handler(request):
        return mockserver.make_response(status=500)

    return handler


@pytest.fixture(autouse=True)
def _mock_orders_bulk_info_autouse(mock_cargo_orders_bulk_info):
    _wrapper = mock_cargo_orders_bulk_info()
    return _wrapper


@pytest.fixture(name='mock_claim_bulk_update_state')
def _mock_claim_bulk_update_state(mockserver):
    @mockserver.json_handler(
        '/cargo-claims/v1/segments/dispatch/bulk-update-state',
    )
    def handler(request):
        context.last_request = request.json
        if context.expected_request is not None:
            assert context.expected_request == request.json
        return mockserver.make_response(
            status=context.status_code,
            json={
                'processed_segment_ids': [
                    seg['id'] for seg in request.json['segments']
                ],
            },
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.handler = handler
            self.expected_request = None
            self.last_request = None

    context = Context()

    return context


@pytest.fixture(name='mock_claims_full', autouse=True)
def _mock_claims_full(mockserver, load_json):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def mock(request):
        return load_json('claims/default.json')

    return mock


@pytest.fixture(name='mock_order_cancel')
def _mock_order_cancel(mockserver):
    @mockserver.json_handler('/cargo-orders/v1/order/cancel')
    def mock(request):
        if context.expected_request is not None:
            assert request.json == context.expected_request
        if context.status_code == 200:
            return {'cancel_state': request.json['cancel_state']}
        return mockserver.make_response(
            json={
                'code': context.error_code,
                'message': f'failed with code {context.status_code}',
            },
            status=context.status_code,
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.error_code = 'order_not_found'
            self.expected_request = None
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='cursors_storage')
def _cursors_storage(pgsql):
    def _wrapper(name):
        cursor = pgsql['cargo_dispatch'].cursor()

        cursor.execute(
            """
            SELECT cursor
            FROM cargo_dispatch.cursors_storage
            WHERE name = %s
        """,
            (name,),
        )
        return cursor.fetchone()[0]

    return _wrapper


@pytest.fixture(name='points_eta')
def _points_eta(pgsql):
    def _wrapper(point_id, waybill_external_ref):
        cursor = pgsql['cargo_dispatch'].cursor()

        cursor.execute(
            """
            SELECT
                estimated_time_of_arrival,
                estimated_distance_of_arrival,
                is_approximate
            FROM cargo_dispatch.waybill_points
            WHERE point_id = %s AND waybill_external_ref = %s
        """,
            (point_id, waybill_external_ref),
        )
        return cursor.fetchall()

    return _wrapper


@pytest.fixture(name='mock_claims_bulk_info')
def _mock_claims_bulk_info(happy_path_claims_segment_db, mockserver):
    def _wrapper(segments_to_ignore: tp.List[str]):
        @mockserver.json_handler('/cargo-claims/v1/segments/bulk-info')
        def _handler(request):
            response = {'segments': []}
            for obj in request.json['segment_ids']:
                segment_id = obj['segment_id']
                if segments_to_ignore and segment_id in segments_to_ignore:
                    continue

                segment = happy_path_claims_segment_db.get_segment(segment_id)
                if segment is not None:
                    response['segments'].append(segment.json)
            return response

        return _handler

    return _wrapper


@pytest.fixture(name='mock_segments_bulk_info_cut')
def _mock_segments_bulk_info_cut(happy_path_claims_segment_db, mockserver):
    @mockserver.json_handler('/cargo-claims/v1/segments/bulk-info/cut')
    def _handler(request):
        response = {'segments': []}
        for obj in request.json['segment_ids']:
            segment_id = obj['segment_id']
            segment = happy_path_claims_segment_db.get_segment(segment_id)
            if segment is not None:
                response['segments'].append(segment.json)
        return response

    return _handler


@pytest.fixture(name='request_waybill_update_proposition')
def _request_waybill_update_proposition(taxi_cargo_dispatch):
    async def _wrapper(
            proposition: dict, updated_waybill_ref: str, extra_time_min=None,
    ):
        request = {
            'proposition': proposition,
            'updated_waybill_ref': updated_waybill_ref,
        }
        if extra_time_min is not None:
            request['extra_time_min'] = extra_time_min
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/update-proposition', json=request,
        )
        return response

    return _wrapper


@pytest.fixture(name='mock_claims_arrive_at_point')
def _mock_claims_arrive_at_point(mockserver):
    def _wrapper(expected_request: dict = None, response: dict = None):
        @mockserver.json_handler('/cargo-claims/v1/segments/arrive_at_point')
        def _arrive_at_point(request):
            if expected_request:
                assert request.json == expected_request
            return (
                {
                    'new_status': 'pickup_confirmation',
                    'new_claim_status': 'ready_for_pickup_confirmation',
                    'new_route': [],
                }
                if response is None
                else response
            )

        return _arrive_at_point

    return _wrapper


@pytest.fixture(name='default_order_fail_request')
def _default_order_fail_request():
    def _wrapper(waybill_id, fail_reason='performer_cancel'):
        return {
            'order_id': 'b66b2650-31b5-46d2-95dc-5ff80f865c6f',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': fail_reason,
            'lookup_version': 0,
        }

    return _wrapper


@pytest.fixture(name='state_cancelled_resolved')
async def _state_cancelled_resolved(
        happy_path_state_orders_created,
        happy_path_claims_segment_db,
        mock_order_cancel,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        run_claims_segment_replication,
        run_notify_orders,
):
    happy_path_claims_segment_db.cancel_segment_by_user('seg3')
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    result = await run_notify_orders()
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-handle-processing',
    )
    assert result['stats']['waybills-for-handling'] == 1
    assert stats['stats']['resolved'] == 1
    return await run_notify_orders()


@pytest.fixture(autouse=True, name='mock_phoenix_traits')
def _mock_phoenix_traits(mockserver):
    @mockserver.json_handler('/cargo-orders/v1/phoenix/traits')
    def handler(request):
        if context.expected_request is not None:
            assert context.expected_request == request.json
        response_json = {
            'cargo_ref_id': request.json['cargo_ref_id'],
            'is_phoenix_flow': context.use_phoenix_flow,
            'is_cargo_finance_billing_event': False,
            'is_cargo_finance_using_cargo_pipelines': False,
            'is_cargo_finance_dry_run_for_cargo_pipelines': False,
            'is_phoenix_corp': context.use_phoenix_flow,
            'is_agent_scheme': context.use_phoenix_flow,
        }
        if context.use_phoenix_flow:
            response_json['claim_id'] = 'claim_id'

        return mockserver.make_response(
            status=context.status_code, json=response_json,
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.handler = handler
            self.expected_request = None
            self.last_request = None
            self.use_phoenix_flow = False

    context = Context()
    return context


@pytest.fixture(name='get_experiment')
def _get_experiment(experiments3):
    def inner(consumer_name, experiment_name):
        exps = experiments3.get_configs(consumer_name, -1)
        for exp in exps:
            if exp['name'] == experiment_name:
                return exp
        return None

    return inner


@pytest.fixture(name='trigger_need_to_notify_orders')
async def _trigger_need_to_notify_orders(pgsql):
    async def _wrapper(waybill_ref: str):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            'UPDATE cargo_dispatch.waybills '
            'SET claims_changes_version = claims_changes_version + 1 '
            'WHERE external_ref=%s',
            (waybill_ref,),
        )

    return _wrapper


@pytest.fixture(name='mock_order_error_info')
def _mock_order_error_info(mockserver):
    def _wrapper(expected_request: dict = None, response: dict = None):
        @mockserver.json_handler('/cargo-orders/v1/order/error-info')
        def _error_info(request):
            if expected_request:
                assert request.json == expected_request
            return (
                mockserver.make_response(status=404, json={})
                if response is None
                else mockserver.make_response(status=200, json=response)
            )

        return _error_info

    return _wrapper


@pytest.fixture(name='set_waybill_cargo_order_id')
async def _set_waybill_cargo_order_id(pgsql):
    async def _wrapper(waybill_ref: str, cargo_order_id: str):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            'UPDATE cargo_dispatch.waybills '
            'SET order_id = %s '
            'WHERE external_ref=%s',
            (cargo_order_id, waybill_ref),
        )

    return _wrapper
