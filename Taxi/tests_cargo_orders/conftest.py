# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
import copy
import dataclasses
import datetime
import typing

import bson
import psycopg2.tz  # noqa: F403 F401
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from cargo_orders_plugins import *  # noqa: F403 F401
from testsuite.mockserver import classes


DISPATCH_POINT_BASE: dict = {'type': 'source', 'label': 'label', 'phones': []}

DISPATCH_ROUTE_POINT: dict = {
    'address': {'fullname': 'SEND IT TO ORDERS', 'coordinates': [1.0, 2.0]},
    **DISPATCH_POINT_BASE,
}

DISPATCH_NEW_ROUTE: list = [{'id': 1, **DISPATCH_ROUTE_POINT}]

DISPATCH_NEW_POINT: dict = {
    **DISPATCH_POINT_BASE,
    'need_confirmation': True,
    'visit_order': 1,
    'actions': [],
}

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


TAXIMETER_DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@dataclasses.dataclass
class CargoOrder:
    order_id: str
    waybill_ref: str
    provider_order_id: typing.Optional[str]
    commit_state: str
    revision: int
    presetcar_calc_id: typing.Optional[str]
    final_calc_id: typing.Optional[str]
    taximeter_price: typing.Optional[float]
    cargo_pricing_price: typing.Optional[float]
    use_cargo_pricing: bool
    final_calc_fallback_was_used: typing.Optional[bool]
    last_calculated_for_driver_with_id: typing.Optional[str]
    complete_time: datetime.datetime
    cancel_request_token: typing.Optional[str]
    nondecoupling_client_offer_calc_id: typing.Optional[str]
    nondecoupling_client_final_calc_id: typing.Optional[str]
    created: int


@pytest.fixture
def fetch_order(pgsql):
    def fetch(order_id):
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
            SELECT
             order_id,
             waybill_ref,
             provider_order_id,
             commit_state,
             revision,
             presetcar_calc_id,
             final_calc_id,
             taximeter_price,
             cargo_pricing_price,
             use_cargo_pricing,
             final_calc_fallback_was_used,
             last_calculated_for_driver_with_id,
             complete_time,
             cancel_request_token,
             nondecoupling_client_offer_calc_id,
             nondecoupling_client_final_calc_id,
             created
            FROM cargo_orders.orders WHERE order_id = %s
            """,
            (order_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f'No order {order_id} found')
        return CargoOrder(
            order_id=row[0],
            waybill_ref=row[1],
            provider_order_id=row[2],
            commit_state=row[3],
            revision=row[4],
            presetcar_calc_id=row[5],
            final_calc_id=row[6],
            taximeter_price=row[7],
            cargo_pricing_price=row[8],
            use_cargo_pricing=row[9],
            final_calc_fallback_was_used=row[10],
            last_calculated_for_driver_with_id=row[11],
            complete_time=row[12],
            cancel_request_token=row[13],
            nondecoupling_client_offer_calc_id=row[14],
            nondecoupling_client_final_calc_id=row[15],
            created=row[16],
        )

    return fetch


@dataclasses.dataclass
class CargoOrderPerformer:
    order_id: str
    dist_from_point_a: int
    eta_to_point_a: datetime.datetime


@pytest.fixture
def fetch_performer(pgsql):
    def fetch(order_id):
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
            SELECT
             order_id,
             dist_from_point_a,
             eta_to_point_a
            FROM cargo_orders.orders_performers WHERE order_id = %s
            """,
            (order_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f'No performer for order {order_id} found')
        return CargoOrderPerformer(
            order_id=row[0], dist_from_point_a=row[1], eta_to_point_a=row[2],
        )

    return fetch


@dataclasses.dataclass
class OrderClientRobocall:
    order_id: str
    point_id: str
    claim_id: str
    reason: str
    provider: str
    status: str
    resolution: typing.Optional[str]
    created_ts: datetime.datetime
    updated_ts: datetime.datetime


@pytest.fixture(name='prepare_order_client_robocall')
def _prepare_order_client_robocall(pgsql):
    def prepare(
            order_id,
            point_id,
            claim_id='test_claim_id_1',
            reason='client_not_responding',
            provider='eats_core',
            status='calling',
            resolution=None,
            created_ts='2021-10-10T10:00:00+03:00',
            updated_ts='2021-10-10T10:00:00+03:00',
    ):
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
INSERT INTO cargo_orders.orders_client_robocalls (
    order_id,
    point_id,
    claim_id,
    reason,
    provider,
    status,
    resolution,
    created_ts,
    updated_ts
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                order_id,
                point_id,
                claim_id,
                reason,
                provider,
                status,
                resolution,
                created_ts,
                updated_ts,
            ),
        )

    return prepare


@pytest.fixture(name='fetch_order_client_robocall')
def _fetch_order_client_robocall(pgsql):
    def fetch(order_id, point_id):
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
            SELECT
             order_id,
             point_id,
             claim_id,
             reason,
             provider,
             status,
             resolution,
             created_ts,
             updated_ts
            FROM cargo_orders.orders_client_robocalls
            WHERE order_id = %s AND point_id = %s
            """,
            (order_id, point_id),
        )
        rows = cursor.fetchall()
        if rows is None:
            raise RuntimeError(
                'order_client_robocall is not found'
                + f'order_id: {order_id}, point_id: {point_id}',
            )
        assert len(rows) == 1
        row = rows[0]
        return OrderClientRobocall(
            order_id=row[0],
            point_id=row[1],
            claim_id=row[2],
            reason=row[3],
            provider=row[4],
            status=row[5],
            resolution=row[6],
            created_ts=row[7],
            updated_ts=row[8],
        )

    return fetch


@dataclasses.dataclass
class OrderClientRobocallAttempt:
    order_id: str
    point_id: str
    attempt_id: int
    eats_core_robocall_data: typing.Optional[dict]
    resolution: typing.Optional[str]
    created_ts: datetime.datetime
    updated_ts: datetime.datetime


@pytest.fixture(name='prepare_robocall_attempt')
def _prepare_robocall_attempt(pgsql):
    def prepare(
            order_id,
            point_id,
            attempt_id,
            eats_core_robocall_data=None,
            resolution=None,
            created_ts='2021-10-10T10:00:00+03:00',
            updated_ts='2021-10-10T10:00:00+03:00',
    ):
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
INSERT INTO cargo_orders.orders_client_robocall_attempts (
    order_id,
    point_id,
    attempt_id,
    eats_core_robocall_data,
    resolution,
    created_ts,
    updated_ts
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                order_id,
                point_id,
                attempt_id,
                eats_core_robocall_data,
                resolution,
                created_ts,
                updated_ts,
            ),
        )

    return prepare


@pytest.fixture(name='fetch_robocall_attempt')
def _fetch_robocall_attempt(pgsql):
    def fetch(order_id, point_id, attempt_id):
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
            SELECT
             order_id,
             point_id,
             attempt_id,
             eats_core_robocall_data,
             resolution,
             created_ts,
             updated_ts
            FROM cargo_orders.orders_client_robocall_attempts
            WHERE order_id = %s AND point_id = %s AND attempt_id = %s
            """,
            (order_id, point_id, attempt_id),
        )
        rows = cursor.fetchall()
        if rows is None:
            raise RuntimeError(
                'order_client_robocall_attempt is not found'
                + f'order_id: {order_id}, point_id: {point_id}, '
                + f'attempt_id: {attempt_id}',
            )
        assert len(rows) == 1
        row = rows[0]
        return OrderClientRobocallAttempt(
            order_id=row[0],
            point_id=row[1],
            attempt_id=row[2],
            eats_core_robocall_data=row[3],
            resolution=row[4],
            created_ts=row[5],
            updated_ts=row[6],
        )

    return fetch


@pytest.fixture(name='default_order_id')
def _default_order_id():
    return '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'


@pytest.fixture(name='default_courier_demand_multiplier')
def _default_courier_demand_multiplier():
    return 1.0


@pytest.fixture(name='order_id_without_performer')
def _order_id_without_performer():
    return '7771622e-4091-582d-b6fc-4cb2ffdc12c0'


@pytest.fixture(name='order_id_no_pricing')
def _order_id_no_pricing():
    return '51c4386a-4edc-40bc-a64e-b45a14d711f0'


def substitute_template(value, **kwargs):
    if isinstance(value, str):
        return value.format(**kwargs)

    if isinstance(value, dict):
        for dict_key, dict_value in value.items():
            value[dict_key] = substitute_template(dict_value, **kwargs)
    elif isinstance(value, list):
        for idx, list_value in enumerate(value):
            value[idx] = substitute_template(list_value, **kwargs)
    return value


@pytest.fixture(name='mock_cargo_dispatch_find_ref', autouse=True)
def _mock_cargo_dispatch_find_ref(mockserver):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/find-ref')
    def mock(request):
        return {'waybill_external_ref': 'waybill-ref'}

    return mock


@pytest.fixture(name='default_calc_request')
def _default_calc_request():
    return {
        'user_id': 'mock-user',
        'order_id': 'taxi-order',
        'cargo_ref_id': 'mock-claim',
        'tariff_class': 'mock-tariff',
        'status': 'finished',
        'taxi_status': 'failed',
        'driver_id': 'driver_id1',
        'park_db_id': 'park_db_id1',
        'transport_type': 'electric_bicycle',
        'source_type': 'presetcar',
    }


@pytest.fixture(name='mock_cargo_pricing_calc')
def _mock_cargo_pricing_calc(mockserver, load_json):
    class Context:
        request = None
        mock = None
        response = load_json('cargo-pricing/v1_taxi_calc.json')
        substituted_client_price = None
        substituted_driver_price = None
        substituted_client_calc_id = None
        substituted_driver_calc_id = None

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc')
    def mock(request):
        ctx.request = request.json
        response = copy.copy(ctx.response)
        print(
            request.json['price_for'],
            ctx.substituted_client_price,
            ctx.substituted_client_calc_id,
            ctx.substituted_driver_price,
            ctx.substituted_driver_calc_id,
        )
        if request.json['price_for'] == 'client':
            if ctx.substituted_client_price:
                response['price'] = ctx.substituted_client_price
            if ctx.substituted_client_calc_id:
                response['calc_id'] = ctx.substituted_client_calc_id
        else:
            if ctx.substituted_driver_price:
                response['price'] = ctx.substituted_driver_price
            if ctx.substituted_driver_calc_id:
                response['calc_id'] = ctx.substituted_driver_calc_id
        return response

    ctx.mock = mock
    return ctx


@pytest.fixture(name='mock_cargo_pricing_calc_retrieve')
def _mock_cargo_pricing_calc_retrieve(mockserver, load_json):
    class Context:
        request = None
        mock = None
        response = load_json('cargo-pricing/v1_taxi_calc_retrieve.json')
        substituted_price = {}

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/retrieve')
    def mock(request):
        ctx.request = request.json
        response = copy.copy(ctx.response)
        calc_id = request.json['calc_id']
        response['calc_id'] = calc_id
        price = ctx.substituted_price.get(calc_id, None)
        if price:
            response['price'] = price
        return response

    ctx.mock = mock
    return ctx


@pytest.fixture(name='mock_cargo_pricing_v2_calc_retrieve')
def _mock_cargo_pricing_v2_calc_retrieve(mockserver, load_json):
    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
    def mock(request):
        return load_json('cargo-pricing/v2_taxi_calc_retrieve.json')

    return mock


@pytest.fixture(name='base_fines_queue')
def _base_fines_queue(load_json):
    def _wrapper(events_path, cancelled_events_path):
        class BaseFinesQueue:
            def __init__(self):
                self.events = load_json(events_path)

            def drop_unresolved_request(self):
                return self.events.pop()

            def drop_all_events(self):
                orig_events = self.events.copy()
                self.events = []
                return orig_events

            def restore_all_events(self):
                self.events = load_json(events_path)

            def restore_events_rejected_fine(self):
                self.events = load_json(cancelled_events_path)

            @property
            def update_fine_request_event(self):
                return self.events[1]

            @property
            def unresolved_request_event(self):
                return self.events[-1]

        return BaseFinesQueue()

    return _wrapper


@pytest.fixture(name='fines_queue')
def _fines_queue(base_fines_queue):
    return base_fines_queue(
        events_path='processing_events.json',
        cancelled_events_path='cancelled_fine_events.json',
    )


@pytest.fixture(name='calc_price')
async def _calc_price(
        taxi_cargo_orders, default_calc_request, mock_cargo_pricing_calc,
):
    async def call(source_type='presetcar', request_override=None):
        default_calc_request['source_type'] = source_type
        default_calc_request.update(request_override or {})
        response = await taxi_cargo_orders.post(
            '/v1/calc-price', json=default_calc_request,
        )
        assert response.status_code == 200
        return response

    return call


@pytest.fixture(name='calc_price_via_taximeter')
async def _calc_price_via_taximeter(
        taxi_cargo_orders, default_order_id, mock_cargo_pricing_calc,
):
    async def call(
            stage='performer_assignment',
            status='new',
            order_id=default_order_id,
    ):
        response = await taxi_cargo_orders.post(
            'driver/v1/cargo-claims/v1/cargo/calc-price',
            headers=TAXIMETER_DEFAULT_HEADERS,
            json={
                'cargo_ref_id': f'order/{order_id}',
                'calculation_stage': stage,
                'status': status,
            },
        )
        assert response.status_code == 200
        return response

    return call


@pytest.fixture(name='calc_cash_via_taximeter')
async def _calc_cash_via_taximeter(
        taxi_cargo_orders, default_order_id, mock_cargo_pricing_calc,
):
    async def call(order_id=default_order_id):
        response = await taxi_cargo_orders.post(
            'driver/v1/cargo-claims/v1/cargo/calc-cash',
            headers=TAXIMETER_DEFAULT_HEADERS,
            json={'cargo_ref_id': f'order/{order_id}'},
        )
        assert response.status_code == 200
        return response

    return call


@pytest.fixture(name='mock_waybill_path_info', autouse=True)
def _mock_waybill_path_info(mockserver):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/path/info')
    def mock(request):
        return {
            'waybill_ref': request.query.get(
                'waybill_external_ref', 'DEAFAULT',
            ),
            'segments': [
                {'segment_id': 'some_segment_id', 'claim_id': 'some_claim_id'},
            ],
            'path': [
                {
                    'segment_id': 'some_segment_id',
                    'waybill_point_id': 'point_id',
                    'visit_order': 1,
                },
            ],
        }

    return mock


@pytest.fixture(name='mock_waybill_path_info_batch')
def _mock_waybill_path_info_batch(mockserver):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/path/info')
    def mock(request):
        return {
            'waybill_ref': request.query['waybill_external_ref'],
            'segments': [
                {'segment_id': 'seg1', 'claim_id': 'seg1_claim'},
                {'segment_id': 'seg2', 'claim_id': 'seg2_claim'},
            ],
            'path': [
                {
                    'segment_id': 'seg1',
                    'waybill_point_id': 'point_id1',
                    'visit_order': 1,
                },
                {
                    'segment_id': 'seg2',
                    'waybill_point_id': 'point_id2',
                    'visit_order': 2,
                },
            ],
        }

    return mock


@pytest.fixture(name='mock_segments_bulk_info', autouse=True)
def _mock_segments_bulk_info(mockserver, load_json):
    class Context:
        pickup_code_received_at = None
        soft_requirements = None
        taxi_classes = None
        custom_context = None

        @mockserver.json_handler('/cargo-claims/v1/segments/bulk-info')
        @staticmethod
        def handle(request):
            response = {'segments': []}
            for obj in request.json['segment_ids']:
                one_segment = load_json(
                    'cargo-claims/v1_segments_bulk_info_tpl.json',
                )
                substitute_template(one_segment, segment_id=obj['segment_id'])

                if Context.pickup_code_received_at is not None:
                    for point in one_segment['points']:
                        point[
                            'pickup_code_received_at'
                        ] = Context.pickup_code_received_at

                if Context.soft_requirements is not None:
                    one_segment['performer_requirements'][
                        'dispatch_requirements'
                    ] = {'soft_requirements': Context.soft_requirements}
                if Context.taxi_classes is not None:
                    one_segment['performer_requirements'][
                        'taxi_classes'
                    ] = Context.taxi_classes
                if Context.custom_context is not None:
                    one_segment['custom_context'] = Context.custom_context

                response['segments'].append(one_segment)
            return response

        @staticmethod
        def set_pickup_code_received_at(value):
            Context.pickup_code_received_at = value

        @staticmethod
        def set_soft_requirements(value):
            Context.soft_requirements = value

        @staticmethod
        def set_taxi_classes(value):
            Context.taxi_classes = value

        @staticmethod
        def set_custom_context(value):
            Context.custom_context = value

    return Context()


# TODO: remove in <Задача на исправление тестов>
def set_segments_status(waybill_info: dict, segment_status: str):
    for segment in waybill_info['execution']['segments']:
        segment['status'] = segment_status


@pytest.fixture(name='mock_dispatch_return')
def _mock_dispatch_return(mockserver, my_waybill_info):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/return')
    def mock(request):
        if (
                'need_create_ticket' in request.json
                and request.json['need_create_ticket']
        ):
            return mockserver.make_response(
                status=403,
                json={
                    'code': 'block_restriction',
                    'message': 'There is blocked restricton',
                },
            )
        set_segments_status(my_waybill_info, segment_status='returning')

        if context.expected_request is not None:
            assert request.json == context.expected_request
        return {
            'result': 'confirmed',
            'new_status': 'returning',
            'new_route': DISPATCH_NEW_ROUTE,
            'waybill_info': my_waybill_info,
        }

    class Context:
        def __init__(self):
            self.expected_request = None
            self.response = None
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_dispatch_exchange_confirm')
def _mock_dispatch_exchange_confirm(mockserver, load_json, my_waybill_info):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/exchange/confirm')
    def mock(request):
        if context.expected_request is not None:
            assert request.json == context.expected_request
        if context.response is not None:
            return context.response
        response = load_json('cargo-dispatch/v1_waybill_exchange_confirm.json')
        response['waybill_info'] = my_waybill_info
        return response

    class Context:
        def __init__(self):
            self.expected_request = None
            self.response = None
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(autouse=True, name='mocker_archive_get_order_proc')
def _mocker_archive_get_order_proc(order_archive_mock):
    def wrapper(json):
        if json is not None:
            order_archive_mock.set_order_proc(json)

        return order_archive_mock.order_proc_retrieve

    wrapper(None)
    return wrapper


@pytest.fixture(name='load_json_var')
def _load_json_var(load_json):
    def load_json_var(path, **variables):
        def var_hook(obj):
            varname = obj['$var']
            return variables[varname]

        return load_json(path, object_hook={'$var': var_hook})

    return load_json_var


@pytest.fixture(name='waybill_state')
def _waybill_state(load_json_var, default_order_id):
    class WaybillState:
        def __init__(self):
            self.waybills = {}

        def load_waybill(self, path, *, waybill_id='waybill-ref'):
            response = load_json_var(path, order_id=default_order_id)
            self.waybills[waybill_id] = response
            self.waybills[default_order_id] = response
            return response

        def set_segment_status(self, segment_status: str):
            for waybill in self.waybills.values():
                for segment in waybill['execution']['segments']:
                    segment['status'] = segment_status

        def set_post_payment(
                self, payment_ref_id: str = '123', method: str = 'card',
        ):
            for waybill in self.waybills.values():
                points = waybill['execution']['points']
                for point in points:
                    point['post_payment'] = {
                        'id': payment_ref_id,
                        'method': method,
                    }

        def set_cargo_c2c_order_id(self, cargo_c2c_order_id):
            for waybill in self.waybills.values():
                segments = waybill['execution']['segments']
                for segment in segments:
                    segment['cargo_c2c_order_id'] = cargo_c2c_order_id

        def set_payment_type(self, payment_type):
            for waybill in self.waybills.values():
                waybill['execution']['segments'][0]['client_info'][
                    'payment_info'
                ]['type'] = payment_type

        def set_point_resolved(self, index=0, waybill_id='waybill-ref'):
            point = self.waybills[waybill_id]['execution']['points'][index]
            last_timestamp = datetime.datetime.fromisoformat(
                point['changelog'][-1]['timestamp'],
            )
            point['is_resolved'] = True
            point['changelog'] += [
                {
                    'status': 'arrived',
                    'timestamp': (
                        last_timestamp + datetime.timedelta(minutes=5)
                    ).isoformat(),
                },
            ]

    return WaybillState()


@pytest.fixture(name='my_waybill_info', autouse=True)
def _my_waybill_info(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_tpl.json',
    )


@pytest.fixture(name='my_multipoints_waybill_info')
def _my_multipoints_waybill_info(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_multipoints_waybill_info_tpl.json',
    )


@pytest.fixture(name='waybill_info_with_same_source_point')
def _waybill_info_with_same_source_point(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_same_A_point_tpl.json',
    )


@pytest.fixture(name='my_batch_waybill_info')
def _my_batch_waybill_info(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_batch_tpl.json',
    )


@pytest.fixture(name='my_triple_batch_waybill_info')
def _my_triple_batch_waybill_info(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_triple_batch_tpl.json',
    )


@pytest.fixture(name='my_batch_with_multipoints_waybill_info')
def _my_batch_with_multipoints_waybill_info(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_batch_multipoints_tpl.json',
    )


@pytest.fixture(name='waybill_info_pull_dispatch')
def _waybill_info_pull_dispatch(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_grocery_pull_dispatch.json',
    )


@pytest.fixture(name='waybill_info_pull_dispatch_extra_fields')
def _waybill_info_pull_dispatch_extra(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/'
        'v1_waybill_info_grocery_pull_dispatch_extra_fields.json',
    )


@pytest.fixture(name='waybill_info_glue_route_points')
def _waybill_info_glue_route_points(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_glue_route_points.json',
    )


@pytest.fixture(name='waybill_info_c2c')
def _waybill_info_c2c(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_c2c.json',
    )


@pytest.fixture(name='waybill_info_pull_dispatch_nobatch')
def _waybill_info_pull_dispatch_nobatch(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_grocery_pull_dispatch_nobatch.json',
    )


@pytest.fixture(name='mock_waybill_info')
def _mock_waybill_info(mockserver, default_order_id, load_json, waybill_state):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def mock(request):
        waybill_ref = request.args.get('waybill_external_ref')
        if waybill_ref:
            if waybill_ref not in waybill_state.waybills:
                return mockserver.make_response(
                    status=404,
                    json={
                        'code': 'not_found',
                        'message': 'waybill_ref is not found',
                    },
                )
            return mockserver.make_response(
                status=200, json=waybill_state.waybills[waybill_ref],
            )

        cargo_order_id = request.args['cargo_order_id']
        if cargo_order_id not in waybill_state.waybills:
            return mockserver.make_response(
                status=404,
                json={
                    'code': 'not_found',
                    'message': 'cargo_order_id is not found',
                },
            )
        return mockserver.make_response(
            status=200, json=waybill_state.waybills[cargo_order_id],
        )

    return mock


@pytest.fixture(name='mock_waybill_info_404')
def _mock_waybill_info_404(mockserver):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def mock(request):
        return mockserver.make_response(
            status=404, json={'code': 'not_found', 'message': 'not found'},
        )

    return mock


@pytest.fixture(autouse=True)
def personal_data_request(mockserver):
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


@pytest.fixture
async def set_order_properties(pgsql):
    def wrapper(
            order_id: str,
            *,
            commit_state: str = None,
            use_cargo_pricing: bool = None,
            created: str = None,
            cancel_request_token: str = None,
    ):

        cursor = pgsql['cargo_orders'].conn.cursor()
        cursor.execute(
            """
UPDATE cargo_orders.orders
SET
    use_cargo_pricing = COALESCE(%(use_cargo_pricing)s, use_cargo_pricing),
    commit_state = COALESCE(%(commit_state)s, commit_state),
    created = COALESCE(%(created)s, created),
    cancel_request_token = COALESCE(%(cancel_request_token)s,
                                    cancel_request_token)
WHERE order_id = %(order_id)s
        """,
            dict(
                order_id=order_id,
                commit_state=commit_state,
                use_cargo_pricing=use_cargo_pricing,
                created=created,
                cancel_request_token=cancel_request_token,
            ),
        )

    return wrapper


@pytest.fixture
def mock_dispatch_mark_fail(mockserver, default_order_id):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/mark/order-fail')
    def mock_cargo_dispatch(request):
        assert request.json['order_id'] == context.order_id
        if context.expecting_reason is not None:
            assert request.json['reason'] == context.expecting_reason
        if context.expecting_cancel_request_token is not None:
            assert (
                request.json['cancel_request_token']
                == context.expecting_cancel_request_token
            )

        if context.status_code == 200:
            return {'id': 'waybill-ref', 'status': 'processing'}
        return mockserver.make_response(
            status=context.status_code,
            json={'message': 'something', 'code': 'bad'},
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.handler = mock_cargo_dispatch
            self.order_id = default_order_id
            self.expecting_reason = None
            self.expecting_cancel_request_token = None

    context = Context()

    return context


@pytest.fixture
async def fetch_taxi_order_error(pgsql):
    def wrapper():
        cursor = pgsql['cargo_orders'].dict_cursor()
        cursor.execute(
            """
            SELECT
             waybill_ref,
             cargo_order_id,
             reason,
             message
            FROM cargo_orders.orders_errors
            """,
        )
        rows = cursor.fetchall()
        assert len(rows) == 1
        return dict(rows[0])

    return wrapper


@pytest.fixture(name='mock_archive_api')
def _mock_archive_api(mockserver):
    class Context:
        def __init__(self):
            self.request = None
            self.mock = None

    context = Context()

    @mockserver.json_handler('/archive-api/archive/order')
    def mock(request):
        context.request = request.json
        response = {
            'doc': {
                'payment_tech': {
                    'driver_without_vat_to_pay': {'ride': 7990000},
                },
                'performer': {
                    'db_id': 'mock_performer_clid',
                    'taxi_alias': {'id': 'mock_performer_taxi_alias_id'},
                    'uuid': '3b21002ec1564d87ac05174bf261379f',
                },
            },
        }
        return mockserver.make_response(bson.BSON.encode(response), status=200)

    context.mock = mock

    return context


@pytest.fixture(name='mock_driver_orders_app_api_order_update_fields')
def _mock_driver_orders_app_api_order_update_fields(mockserver):
    class Context:
        def __init__(self):
            self.request = None
            self.mock = None

    context = Context()

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order-db-api/update-fields',
    )
    def mock(request, *args, **kwargs):
        context.request = request.json

        return mockserver.make_response(
            json={'message': 'something', 'code': 'bad'}, status=200,
        )

    context.mock = mock

    return context


def _check_current_point(response):
    current_point_id = response['current_point']['id']
    route_points = {point['id'] for point in response['current_route']}
    assert (
        current_point_id in route_points
    ), 'current_point is not found in current_route'


@pytest.fixture(name='get_driver_cargo_state')
def _get_driver_cargo_state(taxi_cargo_orders):
    async def cargo_state(order_id):
        response = await taxi_cargo_orders.post(
            '/driver/v1/cargo-claims/v1/cargo/state',
            headers=DEFAULT_HEADERS,
            json={'cargo_ref_id': 'order/' + order_id},
        )
        assert response.status_code == 200
        _check_current_point(response.json())
        return response

    return cargo_state


@pytest.fixture(name='get_driver_cargo_items')
def _get_driver_cargo_items(taxi_cargo_orders):
    async def cargo_items(cargo_ref_id, point_id):
        response = await taxi_cargo_orders.get(
            'driver/v1/cargo-claims/v1/cargo/items'
            f'?cargo_ref_id={cargo_ref_id}&point_id={point_id}',
            headers=DEFAULT_HEADERS,
        )
        assert response.status_code == 200
        return response

    return cargo_items


@pytest.fixture(name='set_order_calculations_ids')
async def _set_order_calculations_ids(pgsql):
    def wrapper(
            presetcar_calc_id=None,
            final_calc_id=None,
            client_offer_calc_id=None,
    ):
        cursor = pgsql['cargo_orders'].conn.cursor()
        cursor.execute(
            """
        UPDATE cargo_orders.orders
        SET
            presetcar_calc_id = %(presetcar_calc_id)s,
            final_calc_id = %(final_calc_id)s,
            nondecoupling_client_offer_calc_id =
                %(client_offer_calc_id)s
        """,
            dict(
                presetcar_calc_id=presetcar_calc_id,
                final_calc_id=final_calc_id,
                client_offer_calc_id=client_offer_calc_id,
            ),
        )

    return wrapper


@pytest.fixture
def set_point_visited():
    def set_(v1_waybill_info_response, index=0):
        point = v1_waybill_info_response['execution']['points'][index]
        last_timestamp = datetime.datetime.fromisoformat(
            point['changelog'][-1]['timestamp'],
        )
        point['changelog'] += [
            {
                'status': 'arrived',
                'timestamp': (
                    last_timestamp + datetime.timedelta(minutes=5)
                ).isoformat(),
            },
        ]

    return set_


@pytest.fixture
def resolve_waybill():
    def resolve(v1_waybill_info_response):
        v1_waybill_info_response['dispatch']['status'] = 'resolved'
        v1_waybill_info_response['dispatch']['resolution'] = 'complete'
        v1_waybill_info_response['dispatch'][
            'resolved_at'
        ] = '2020-06-01T12:00:00+0300'
        for driver in ['driver_id1', 'driver_id2']:
            for point in v1_waybill_info_response['execution']['points']:
                last_timestamp = datetime.datetime.fromisoformat(
                    point['changelog'][-1]['timestamp'],
                )
                if point['type'] != 'return':
                    point['changelog'] += [
                        {
                            'driver_id': driver,
                            'status': 'arrived',
                            'timestamp': (
                                last_timestamp + datetime.timedelta(minutes=5)
                            ).isoformat(),
                        },
                        {
                            'driver_id': driver,
                            'status': 'visited',
                            'timestamp': (
                                last_timestamp + datetime.timedelta(minutes=10)
                            ).isoformat(),
                        },
                    ]
                else:
                    point['changelog'] += [
                        {
                            'driver_id': driver,
                            'status': 'skipped',
                            'timestamp': (
                                last_timestamp + datetime.timedelta(minutes=5)
                            ).isoformat(),
                        },
                    ]

    return resolve


@pytest.fixture(name='mock_admin_claims_phoenix_traits')
def _mock_admin_claims_phoenix_traits(mockserver, default_order_id):
    @mockserver.json_handler('/cargo-claims/v2/admin/phoenix/bulk-traits')
    def mock_cargo_claims(request):
        cargo_order_ids = request.json['cargo_order_ids']
        if cargo_order_ids[0] == default_order_id:
            context.is_phoenix = False
        order = {
            'cargo_order_id': cargo_order_ids[0],
            'claim_id': 'some_id',
            'is_phoenix_flow': context.is_phoenix,
            'is_cargo_finance_billing_event': False,
            'is_agent_scheme': context.is_phoenix,
            'is_phoenix_corp': context.is_phoenix,
        }
        return mockserver.make_response(status=200, json={'orders': [order]})

    class Context:
        def __init__(self):
            self.is_phoenix = True
            self.handler = mock_cargo_claims

    context = Context()

    return context


@pytest.fixture(name='mock_claims_phoenix_traits')
def _mock_claims_phoenix_traits(mockserver):
    @mockserver.json_handler('/cargo-claims/v2/claims/phoenix/bulk-traits')
    def mock_cargo_claims(request):
        response_json = {'orders': []}
        if context.claims_response_status == 'success':
            response_json['orders'] = [
                {
                    'cargo_order_id': request.json['cargo_order_ids'][0],
                    'claim_id': 'claim_uuid_1',
                    'is_phoenix_flow': True,
                    'is_cargo_finance_billing_event': False,
                    'is_agent_scheme': context.is_agent_scheme,
                    'is_phoenix_corp': True,
                },
            ]
        elif context.claims_response_status == 'failed':
            response_json = {'code': '500', 'message': 'Internal Server Error'}
        return mockserver.make_response(
            status=500 if context.claims_response_status == 'failed' else 200,
            json=response_json,
        )

    class Context:
        def __init__(self):
            self.claims_response_status = 'success'
            self.is_agent_scheme = True
            self.handler = mock_cargo_claims

    context = Context()

    return context


# pylint: disable=invalid-name
@dataclasses.dataclass(frozen=True)
class PerformerOrderCancel:
    id: int
    cargo_order_id: str
    taxi_order_id: str
    park_id: str
    driver_id: str
    cargo_cancel_reason: str
    taxi_cancel_reason: str
    completed: bool
    guilty: bool
    need_reorder: bool
    payload: dict
    free_cancellations_limit_exceeded: bool


@pytest.fixture(name='query_performer_order_cancel')
def _query_performer_order_cancel(pgsql):
    def _wrapper(id_: int):
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
            SELECT id, cargo_order_id, taxi_order_id, park_id, driver_id,
            cargo_cancel_reason, taxi_cancel_reason,
            completed, guilty, need_reorder, payload,
            free_cancellations_limit_exceeded
            FROM cargo_orders.performer_order_cancel
            WHERE id =  %s
            """,
            (id_,),
        )
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(
                PerformerOrderCancel(
                    id=row[0],
                    cargo_order_id=row[1],
                    taxi_order_id=row[2],
                    park_id=row[3],
                    driver_id=row[4],
                    cargo_cancel_reason=row[5],
                    taxi_cancel_reason=row[6],
                    completed=row[7],
                    guilty=row[8],
                    need_reorder=row[9],
                    payload=row[10],
                    free_cancellations_limit_exceeded=row[11],
                ),
            )
        return result

    return _wrapper


@pytest.fixture(name='mock_dispatch_arrive_at_point')
async def _mock_dispatch_arrive_at_point(mockserver, waybill_state):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/arrive-at-point')
    def mock(request):
        context.last_request = request.json
        if context.status_code == 200:
            return {
                'new_status': 'new',
                'waybill_info': waybill_state.waybills[
                    request.args['waybill_external_ref']
                ],
            }
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.last_request = None
            self.status_code = 200
            self.error_code = 'not_found'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_driver_tags_v1_match_profile')
def _mock_driver_tags_v1_match_profile(mockserver):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def mock(request):
        return mockserver.make_response(
            status=200, json={'tags': ['eats_courier_from_region_1']},
        )

    return mock


# pylint: disable=invalid-name
@dataclasses.dataclass(frozen=True)
class PerformerOrderCancelStatistics:
    dbid_uuid: str
    completed_orders: int
    cancellation_count: int


@pytest.fixture(name='query_performer_order_cancel_statistics')
def _query_performer_order_cancel_statistics(pgsql):
    def _wrapper(dbid_uuid_: str):
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
SELECT dbid_uuid,
completed_orders_count_after_last_cancellation,
cancellation_count_after_last_reset
FROM cargo_orders.performer_order_cancel_statistics
WHERE dbid_uuid =  %s
            """,
            (dbid_uuid_,),
        )
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(
                PerformerOrderCancelStatistics(
                    dbid_uuid=row[0],
                    completed_orders=row[1],
                    cancellation_count=row[2],
                ),
            )
        return result

    return _wrapper


@pytest.fixture(name='insert_performer_order_cancel_statistics')
def _insert_performer_order_cancel_statistics(pgsql):
    def _wrapper(dbid_uuid_: str, cancel_count=1):
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
INSERT INTO cargo_orders.performer_order_cancel_statistics (
    dbid_uuid,
    cancellation_count_after_last_reset
)
VALUES (%s, %s)
            """,
            (dbid_uuid_, cancel_count),
        )

    return _wrapper


@pytest.fixture(name='mock_cargo_resolve_segment')
def _mock_cargo_resolve_segment(mockserver, load_json):
    class Context:
        def __init__(self):
            self.request = None
            self.mock = None
            calc_for_client = load_json(
                'cargo-pricing/v2_taxi_resolve_segment.json',
            )
            self.response = {
                'calc_for_client': calc_for_client,
                'calc_for_performer': copy.deepcopy(calc_for_client),
            }
            self.response['calc_for_performer']['price_for'] = 'performer'

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v2/taxi/resolve-segment')
    def mock(request):
        ctx.request = request.json
        response = copy.copy(ctx.response)
        return response

    ctx.mock = mock
    return ctx


@dataclasses.dataclass
class MockserverData:
    request: typing.Optional[classes.MockserverRequest]
    response_data: typing.Any
    response_code: int
    mock: typing.Optional[classes.GenericRequestHandler]


@pytest.fixture(name='mock_with_context')
def _mock_with_context(mockserver):
    def _callable(
            decorator: classes.GenericRequestDecorator,
            response_data,
            response_code=200,
    ) -> MockserverData:
        data = MockserverData(
            request=None,
            response_data=response_data,
            response_code=response_code,
            mock=None,
        )

        @decorator
        def handler(request):
            data.request = request
            return mockserver.make_response(
                json=data.response_data, status=data.response_code,
            )

        data.mock = handler
        return data

    return _callable


@pytest.fixture(name='performers_loyalties')
def _performers_loyalties(pgsql):
    def _wrapper():
        cursor = pgsql['cargo_orders'].cursor()
        cursor.execute(
            """
            SELECT loyalty_rewards
            FROM cargo_orders.orders_performers
            """,
        )
        return cursor.fetchall()

    return _wrapper


@pytest.fixture(name='mock_cargo_estimate_waybill')
def _mock_cargo_estimate_waybill(mockserver, load_json):
    class Context:
        def __init__(self):
            self.request = None
            self.mock = None
            self.response = load_json(
                'cargo-pricing/v2_taxi_estimate_waybill.json',
            )

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v2/taxi/estimate-waybill')
    def mock(request):
        ctx.request = request.json
        response = copy.copy(ctx.response)
        return response

    ctx.mock = mock
    return ctx


@pytest.fixture(name='mock_cargo_resolve_waybill')
def _mock_cargo_resolve_waybill(mockserver, load_json):
    class Context:
        def __init__(self):
            self.request = None
            self.mock = None
            self.response = load_json(
                'cargo-pricing/v2_taxi_resolve_waybill.json',
            )

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v2/taxi/resolve-waybill')
    def mock(request):
        ctx.request = request.json
        response = copy.copy(ctx.response)
        return response

    ctx.mock = mock
    return ctx


@pytest.fixture(name='mock_cargo_retrieve_waybill_pricing')
def _mock_cargo_retrieve_waybill_pricing(mockserver, load_json):
    class Context:
        def __init__(self):
            self.request = None
            self.mock = None
            self.response = load_json(
                'cargo-pricing/v2_taxi_resolve_waybill.json',
            )
            for segment in self.response['segments']:
                del segment['calc_for_client']

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v2/taxi/retrieve-waybill-pricing')
    def mock(request):
        ctx.request = request.json
        response = copy.copy(ctx.response)
        return response

    ctx.mock = mock
    return ctx


@pytest.fixture(name='find_action')
def _find_action():
    def _wrapper(json, action_type):
        for action in json['current_point']['actions']:
            if action['type'] == action_type:
                return action
        return None

    return _wrapper


@pytest.fixture(name='set_segments_place_id')
def _set_segments_place_id():
    def _wrapper(waybill: dict, segment_ids: list, place_id: int):
        for i in segment_ids:
            waybill['execution']['segments'][i]['custom_context'] = {
                'place_id': place_id,
            }

    return _wrapper


@pytest.fixture(name='set_segment_status')
def _set_segment_status():
    def _wrapper(waybill: dict, segment_index: int, status: str):
        waybill['execution']['segments'][segment_index]['status'] = status

    return _wrapper


@pytest.fixture(name='set_current_point')
def _set_current_point():
    def _wrapper(waybill: dict, idx: int):
        for i, point in enumerate(waybill['execution']['points']):
            if i < idx:
                point['visit_status'] = 'visited'
                point['is_resolved'] = True
            else:
                point['visit_status'] = 'pending'
                point['is_resolved'] = False

    return _wrapper


@pytest.fixture(name='set_points_resolved')
def _set_points_resolved():
    def _wrapper(waybill: dict, point_indexes: list):
        for i in point_indexes:
            point = waybill['execution']['points'][i]
            point['visit_status'] = 'visited'
            point['is_resolved'] = True

    return _wrapper


@pytest.fixture(name='set_segments_points_skipped')
def _set_segments_points_skipped():
    def _wrapper(waybill: dict, segment_ids: list):
        for point in waybill['execution']['points']:
            if point['segment_id'] in segment_ids:
                point['is_segment_skipped'] = True
                point['is_resolved'] = True
                point['visit_status'] = 'skipped'

    return _wrapper
