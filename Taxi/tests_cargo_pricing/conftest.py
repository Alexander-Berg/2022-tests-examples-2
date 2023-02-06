# pylint: disable=wildcard-import, unused-wildcard-import, import-error

# pylint: disable=no-name-in-module
from fbs.internal.v2.route import CachedRoutes
from fbs.internal.v2.route import PathInfo
import pytest

from cargo_pricing_plugins import *  # noqa: F403 F401

from tests_cargo_pricing import utils


@pytest.fixture(name='user_options')
def _user_options():
    return {
        'composite_pricing__destination_point_completed': 1.0,
        'composite_pricing__destination_point_visited': 1.0,
        'composite_pricing__return_point_completed': 1.0,
        'composite_pricing__return_point_visited': 1.0,
        'composite_pricing__source_point_completed': 1.0,
        'composite_pricing__source_point_visited': 1.0,
        'fake_middle_point_cargocorp_van.no_loaders_point': 2,
    }


@pytest.fixture(name='mock_pricing_prepare')
def _mock_pricing_prepare(mockserver, load_json):
    class PrepareContext:
        request = None
        categories = load_json('v2_prepare.json')
        mock = None
        error_response = None

    ctx = PrepareContext()

    @mockserver.json_handler('/cargo-pricing-data-preparer/v2/prepare')
    def _mock(request, *args, **kwargs):
        ctx.request = request.json
        assert len(ctx.request['waypoints']) >= 2
        assert ctx.request.get('modifications_scope') == 'cargo'
        assert ctx.request.get('zone')
        if ctx.error_response is None:
            return {'categories': ctx.categories}
        return ctx.error_response

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='mock_pricing_paid_supply')
def _mock_pricing_paid_supply(mockserver, load_json):
    class Context:
        request = None
        mock = None
        paid_supply_price = {
            'modifications': {'for_fixed': [1294], 'for_taximeter': [1294]},
            'price': {'total': 999},
            'meta': {'paid_supply_paid_cancel_in_driving_price': 888.0},
        }

    ctx = Context()

    @mockserver.json_handler(
        '/cargo-pricing-data-preparer/v2/calc_paid_supply',
    )
    def _mock(request, *args, **kwargs):
        ctx.request = request.json
        assert ctx.request.get('modifications_scope') == 'cargo'
        assert ctx.request.get('zone')
        categories = ctx.request['categories']
        response = {}
        for class_name, category in categories.items():
            response[class_name] = category['prepared']
            response[class_name]['driver']['additional_prices'][
                'paid_supply'
            ] = ctx.paid_supply_price
            response[class_name]['user']['additional_prices'][
                'paid_supply'
            ] = ctx.paid_supply_price

        return {'categories': response}

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='mock_route')
def _mock_route(mockserver, load_binary):
    class RouterContext:
        request = None
        empty_route = False
        mock = None
        two_routes = False

    ctx = RouterContext()

    @mockserver.handler('/maps-router/v2/route')
    def _mock(request, *args, **kwargs):
        ctx.request = dict(request.query)
        if not ctx.empty_route:
            if not ctx.two_routes:
                response = load_binary('maps.protobuf')
            else:
                response = load_binary('maps2.protobuf')
        else:
            response = load_binary('empty_route.protobuf')
        return mockserver.make_response(
            response=response,
            status=200,
            content_type='application/x-protobuf',
        )

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='mock_pricing_recalc')
def _mock_pricing_recalc(mockserver, load_json):
    class RecalcContext:
        request = None
        requests = []
        response = load_json('pricing_recalc_response.json')
        mock = None

    ctx = RecalcContext()

    @mockserver.json_handler('/cargo-pricing-data-preparer/v2/recalc')
    def _mock(request, *args, **kwargs):
        ctx.request = request.json
        ctx.requests.append(request.json)
        return ctx.response

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='v1_add_processing_event')
async def _v1_add_processing_event(taxi_cargo_pricing):
    async def call(claim_id, events):
        request = {'entity_id': claim_id, 'events': events}
        response = await taxi_cargo_pricing.post(
            '/v1/taxi/add-processing-event', json=request,
        )
        return response

    return call


@pytest.fixture(name='v1_calc_creator')
async def _v1_calc_creator(
        taxi_cargo_pricing,
        mock_pricing_prepare,
        mock_put_processing_event,
        mock_pricing_recalc,
        mock_route,
):
    class CalcRequestCreator:
        url = '/v1/taxi/calc'
        payload = utils.get_default_calc_request()
        mock_prepare = mock_pricing_prepare
        mock_recalc = mock_pricing_recalc
        mock_router = mock_route

        async def execute(self):
            return await taxi_cargo_pricing.post(self.url, json=self.payload)

    return CalcRequestCreator()


@pytest.fixture(name='v2_calc_creator')
async def _v2_calc_creator(
        taxi_cargo_pricing,
        mock_pricing_prepare,
        mock_put_processing_event,
        mock_pricing_recalc,
        mock_route,
):
    class CalcRequestCreator:
        url = '/v2/taxi/calc'
        payload = {'calc_requests': [utils.get_default_calc_request()]}
        mock_prepare = mock_pricing_prepare
        mock_recalc = mock_pricing_recalc
        mock_router = mock_route

        async def execute(self):
            return await taxi_cargo_pricing.post(self.url, json=self.payload)

    return CalcRequestCreator()


@pytest.fixture(name='v2_add_paid_supply')
async def _v2_add_paid_supply(
        taxi_cargo_pricing,
        mock_pricing_paid_supply,
        mock_pricing_recalc,
        mock_route,
):
    class RequestPerformer:
        url = '/v2/taxi/add-paid-supply'
        payload = {'calculations': []}
        mock_paid_supply = mock_pricing_paid_supply
        mock_recalc = mock_pricing_recalc
        mock_router = mock_route

        def add_calc(self, calc_id, eta_seconds=0, eta_meters=0):
            self.payload['calculations'].append(
                {
                    'calc_id': calc_id,
                    'expectations': {
                        'seconds_to_arrive': eta_seconds,
                        'meters_to_arrive': eta_meters,
                    },
                },
            )

        async def execute(self):
            return await taxi_cargo_pricing.post(self.url, json=self.payload)

    return RequestPerformer()


@pytest.fixture(name='confirm_usage')
async def _confirm_usage(taxi_cargo_pricing):
    async def _req(calc_id, external_ref=None):
        resp = await taxi_cargo_pricing.post(
            '/v1/taxi/calc/confirm-usage',
            json={'calc_id': calc_id, 'external_ref': external_ref},
        )
        assert resp.status_code == 200

    return _req


@pytest.fixture(name='setup_fallback_router')
def _setup_fallback_router(experiments3):
    experiments3.add_config(
        consumers=['cargo-pricing/v1/taxi/calc'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'clause',
                'predicate': {
                    'init': {
                        'predicate': {
                            'init': {
                                'arg_name': 'max_distance_between_waypoints',
                                'arg_type': 'int',
                                'value': 37540,
                            },
                            'type': 'eq',
                        },
                    },
                    'type': 'not',
                },
                'value': {'type': 'car'},
            },
        ],
        name='cargo_pricing_detect_router',
        default_value={'type': 'fallback', 'tolls': 'no_tolls'},
    )


@pytest.fixture(name='setup_two_routes_exp')
def _setup_two_routes_exp(experiments3):
    experiments3.add_config(
        consumers=['cargo-pricing/v1/taxi/calc'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='cargo_pricing_detect_router',
        default_value={'type': 'car', 'routes_count': 2},
    )


@pytest.fixture(name='lazy_setup_batched_distance_correction_exp')
def _lazy_setup_batched_distance_correction_exp(
        experiments3, taxi_cargo_pricing,
):
    async def _setup(default_value):
        experiments3.add_config(
            consumers=['cargo-pricing/v1/taxi/calc'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[],
            name='cargo_pricing_batched_order_route_price_correction',
            default_value=default_value,
        )
        await taxi_cargo_pricing.invalidate_caches()

    return _setup


@pytest.fixture(name='setup_batched_distance_correction_exp')
async def _setup_batched_distance_correction_exp(
        lazy_setup_batched_distance_correction_exp,
):
    await lazy_setup_batched_distance_correction_exp(
        {
            'requirement_names': {
                'limited_requirement_names': [
                    {
                        'requirement_names': {
                            'per_km_requirement_name': 'per_km_corr_0',
                            'constant_requirement_name': 'const_corr_0',
                        },
                        'saved_distance_limit': 3.0,
                    },
                    {
                        'requirement_names': {
                            'per_km_requirement_name': 'per_km_corr_1',
                            'constant_requirement_name': 'const_corr_1',
                        },
                        'saved_distance_limit': 4.0,
                    },
                    {
                        'requirement_names': {
                            'per_km_requirement_name': 'per_km_corr_2',
                            'constant_requirement_name': 'const_corr_2',
                        },
                        'saved_distance_limit': 5.0,
                    },
                ],
                'default_requirement_names': {
                    'per_km_requirement_name': 'per_km_corr_def',
                    'constant_requirement_name': 'const_corr_def',
                },
            },
        },
    )


@pytest.fixture(name='overload_tariff_class')
async def _overload_tariff_class(experiments3, taxi_cargo_pricing):
    class OverloadTariffClass:
        def __init__(self):
            self.predicate = {'type': 'true'}

        async def execute(self, new_class):
            experiments3.add_config(
                match={'predicate': self.predicate, 'enabled': True},
                name='cargo_pricing_class_substitution',
                consumers=['cargo-pricing/v1/taxi/calc'],
                clauses=[],
                default_value={'new_class': new_class},
            )
            await taxi_cargo_pricing.invalidate_caches()

    return OverloadTariffClass()


@pytest.fixture(name='limit_paid_waiting')
def _limit_paid_waiting(experiments3):
    utils.set_limit_paid_waiting(
        experiments3, value={'max_source_point_paid_waiting': 10},
    )


@pytest.fixture(name='setup_cancel_control')
def _setup_cancel_control(experiments3):
    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_pricing_paid_cancel_control',
        consumers=['cargo-pricing/v1/taxi/calc'],
        clauses=[],
        default_value={
            'paid_cancel_interval_start': 5 * 60,
            'paid_cancel_interval_finish': 25 * 60,
            'disable_driver_paid_cancel': True,
        },
    )


@pytest.fixture(name='validate_request')
def _validate_request(experiments3):
    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_pricing_request_additional_validation',
        consumers=['cargo-pricing/v1/taxi/calc'],
        clauses=[
            {
                'title': 'clause',
                'predicate': {'type': 'false'},
                'value': {'enabled': False},
            },
        ],
        default_value={'enabled': True},
    )


@pytest.fixture(name='setup_fake_middle_points', autouse=True)
async def _setup_fake_middle_points(taxi_cargo_pricing, taxi_config):
    taxi_config.set_values(
        dict(
            CARGO_MATCHER_MIDDLE_POINT_FIELDS={
                'requirement_postfix': {
                    'cargo_type': {
                        'lcv_m': {'value': '_lcv_m', 'tariffs': ['cargocorp']},
                        'lcv_l': {'value': '_lcv_l', 'tariffs': ['cargocorp']},
                        'van': {'value': '_van', 'tariffs': ['cargocorp']},
                    },
                },
                'cargocorp': 'fake_middle_point_cargocorp',
                'courier': 'fake_middle_point_express',
                'express': 'fake_middle_point_express',
            },
        ),
    )


@pytest.fixture(name='run_calculations_cleanup')
async def _run_calculations_cleanup(taxi_cargo_pricing, taxi_config):
    class State:
        def __init__(self):
            self.sleep_time_ms = 50
            self.rules = []

        def add_rule(self, **overrides):
            conf = {
                'chunk_size': 1000,
                'delete_not_confirmed_calculations_after_min': 0,
                'delete_confirmed_calculations_after_min': 0,
                'pg_timeout': 1000,
            }
            self.rules.append({**conf, **overrides})

        async def __call__(self):
            conf = {'sleep_time_ms': self.sleep_time_ms, 'rules': self.rules}

            taxi_config.set_values(
                dict(CARGO_PRICING_CLEANUP_WORKMODE_RULES=conf),
            )
            await taxi_cargo_pricing.invalidate_caches()
            return await taxi_cargo_pricing.run_distlock_task(
                'cargo-pricing-db-cleanup',
            )

    return State()


@pytest.fixture(name='get_cached_edges')
async def get_cached_edges(pgsql):
    async def get_edges():
        psql_cursor = pgsql['cargo_pricing'].cursor()
        psql_cursor.execute(
            'SELECT cached_edges_flatterbuffers'
            ' FROM cargo_pricing.calculations',
        )

        parsed = CachedRoutes.CachedRoutes.GetRootAsCachedRoutes(
            list(psql_cursor)[0][0], 0,
        )

        path = []
        for route_idx in range(0, parsed.RoutesLength()):
            route = parsed.Routes(route_idx)
            for point_idx in range(0, route.PathLength()):
                point = route.Path(point_idx)

                path_info = point.FromStart(PathInfo.PathInfo())
                path.append(
                    {
                        'point': [point.Longitude(), point.Latitude()],
                        'from_start': {
                            'time': path_info.Time(),
                            'distance': path_info.Distance(),
                        },
                    },
                )

        return {'path': path}

    return get_edges


@pytest.fixture(name='setup_merge_waypoints_config')
def _setup_merge_waypoints_config(experiments3):
    experiments3.add_config(
        consumers=['cargo-pricing/v1/taxi/calc'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[],
        name='cargo_pricing_merge_waypoints',
        default_value={
            'merged_points_types': ['source', 'destination'],
            'meters_between_points': 10,
        },
    )


@pytest.fixture(name='setup_composite_pricing_point_limits_config')
def _setup_composite_pricing_point_limits_config(experiments3):
    experiments3.add_config(
        consumers=['cargo-pricing/v1/taxi/calc'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[],
        name='cargo_pricing_composite_pricing_point_limits_setup',
        default_value={
            'batched': {
                'composite_pricing__source_point_visited': {'max': 1},
                'composite_pricing__destination_point_visited': {'max': 2},
            },
            'not_batched': {
                'composite_pricing__source_point_visited': {'max': 1},
            },
        },
    )


@pytest.fixture(name='setup_linear_overweight_config')
def _setup_linear_overweight_config(experiments3):
    experiments3.add_config(
        consumers=['cargo-pricing/v1/taxi/calc'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[],
        name='cargo_pricing_overweight_params',
        default_value={
            'type': 'linear',
            'overweight_threshold': 20,
            'minimum_overweight': 4,
        },
    )


@pytest.fixture(name='setup_discrete_overweight_config')
def _setup_discrete_overweight_config(experiments3):
    experiments3.add_config(
        consumers=['cargo-pricing/v1/taxi/calc'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[],
        name='cargo_pricing_overweight_params',
        default_value={
            'type': 'discrete',
            'overweight_threshold': 20,
            'top_thresholds': {'small': 2, 'medium': 4, 'large': 6},
        },
    )


@pytest.fixture(name='setup_disabled_overweight_config')
def _setup_disabled_overweight_config(experiments3):
    experiments3.add_config(
        consumers=['cargo-pricing/v1/taxi/calc'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[],
        name='cargo_pricing_overweight_params',
        default_value={'type': 'disabled'},
    )


@pytest.fixture(name='setup_pricing_class_substitution')
def _setup_pricing_class_substitution(experiments3):
    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_pricing_class_substitution',
        consumers=['cargo-pricing/v1/taxi/calc'],
        clauses=[],
        default_value={},
    )


@pytest.fixture(name='conf_exp3_yt_calcs_logging_enabled')
def _conf_exp3_yt_calcs_logging_enabled(experiments3, taxi_cargo_pricing):
    async def configurate(enabled):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_pricing_yt_calcs_logging',
            consumers=['cargo-pricing/yt_calcs_logging'],
            clauses=[],
            default_value={'enabled': enabled},
        )
        await taxi_cargo_pricing.invalidate_caches()

    return configurate


@pytest.fixture(name='yt_calcs_logger_testpoint')
async def _yt_calcs_logger_testpoint(testpoint, taxi_cargo_pricing):
    @testpoint('yt_calcs_logger')
    def _testpoint(message):
        context.messages.append(message)

    await taxi_cargo_pricing.enable_testpoints()

    class Context:
        def __init__(self):
            self.messages = []

    context = Context()
    return context


@pytest.fixture(name='lazy_config_shared_calc_parts')
def _lazy_config_shared_calc_parts(taxi_cargo_pricing, taxi_config):
    async def _call(shared_fields):
        taxi_config.set_values(
            dict(
                CARGO_PRICING_SHARED_CALC_PARTS={
                    'shared_fields': shared_fields,
                },
            ),
        )
        await taxi_cargo_pricing.invalidate_caches()

    return _call


@pytest.fixture(name='config_shared_calc_parts')
async def _config_shared_calc_parts(lazy_config_shared_calc_parts):
    await lazy_config_shared_calc_parts(
        shared_fields=[
            {
                'field': 'prepared_category',
                'sub_fields': [
                    'driver.modifications',
                    'user.data.tariff.requirement_prices',
                    'driver.NOT_EXISTS_FIELD.NOT_EXISTS',
                ],
            },
            {
                'field': 'prepared_category',
                'sub_fields': ['user.modifications'],
            },
            {
                'field': 'prepared_category',
                'sub_fields': [
                    'driver.NOT_EXISTS_FIELD',
                    'driver.NOT_EXISTS_FIELD.NOT_EXISTS',
                    'NOT_EXISTS_FIELD',
                    'user.additional_prices.NOT_EXISTS',
                    'driver.data.tariff.requirement_prices.NOT_EXISTS',
                ],
            },
        ],
    )


@pytest.fixture(name='v1_retrieve_calc')
def _v1_retrieve_calc(taxi_cargo_pricing):
    async def call(calc_id):
        response = await taxi_cargo_pricing.post(
            '/v1/taxi/calc/retrieve', json={'calc_id': calc_id},
        )
        return response

    return call


@pytest.fixture(name='v2_retrieve_calc')
def _v2_retrieve_calc(taxi_cargo_pricing):
    async def call(calc_ids, response_controller=None):
        request = {'calc_ids': calc_ids}
        if response_controller:
            request['response_controller'] = response_controller
        response = await taxi_cargo_pricing.post(
            '/v2/taxi/calc/retrieve', json=request,
        )
        return response

    return call


@pytest.fixture(name='mock_get_processing_events')
def _mock_get_processing_events(mockserver):
    class GetProcessingEventsContext:
        requests = []
        mock = None
        response = {'events': []}

    ctx = GetProcessingEventsContext()

    @mockserver.json_handler('/processing/v1/cargo/pricing/events')
    def _mock(request):
        ctx.requests.append(request)
        response = mockserver.make_response(json=ctx.response, status=200)
        return response

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='mock_put_processing_event')
def _mock_put_processing_event(mockserver):
    class PutProcessingEventContext:
        requests = []
        mock = None
        status_code = 200
        response = None

    ctx = PutProcessingEventContext()

    @mockserver.json_handler('/processing/v1/cargo/pricing/create-event')
    def _mock(request):
        ctx.requests.append(request)
        if ctx.status_code == 200:
            ctx.response = {'event_id': f'some_event_id_{len(ctx.requests)}'}
        response = mockserver.make_response(
            json=ctx.response, status=ctx.status_code,
        )
        return response

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='conf_exp3_processing_events_saving_enabled')
async def _conf_exp3_processing_events_saving_enabled(
        experiments3, taxi_cargo_pricing,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_pricing_processing_events_saving',
        consumers=['cargo-pricing/processing_events_saving'],
        clauses=[],
        default_value={'enabled': True},
    )
    await taxi_cargo_pricing.invalidate_caches()


@pytest.fixture(name='conf_exp3_events_saving_by_calc_kind_default')
async def _conf_exp3_events_saving_by_calc_kind_default(
        experiments3, taxi_cargo_pricing,
):
    await utils.set_events_saving_by_calc_kind(
        experiments3,
        taxi_cargo_pricing,
        value={'final': True, 'offer': True, 'analytical': True},
    )


@pytest.fixture(name='conf_exp3_get_calc_id_from_processing')
def _conf_exp3_get_calc_id_from_processing(experiments3, taxi_cargo_pricing):
    async def configurate(enabled):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_pricing_get_calc_id_from_processing',
            consumers=['cargo-pricing/v1/taxi/calc'],
            clauses=[],
            default_value={'enabled': enabled},
        )
        await taxi_cargo_pricing.invalidate_caches()

    return configurate


@pytest.fixture(name='v1_drivers_match_profile')
async def _v1_drivers_match_profile(
        mockserver, taxi_cargo_pricing, taxi_config,
):
    class DriverMatchProfileContext:
        driver_tags = {
            ('dbid0', 'uuid0'): ['driver_fix_bad_guy'],
            ('dbid1', 'uuid1'): ['driver_honor_good_guy'],
        }
        mock = None

    ctx = DriverMatchProfileContext()

    taxi_config.set_values(
        dict(
            CARGO_PRICING_DRIVER_TAGS_USEFULL_TOPICS={
                'topics': ['cargo-pricing', 'usefull-topic-2'],
            },
        ),
    )
    await taxi_cargo_pricing.invalidate_caches()

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _mock(request):
        assert request.json['topics'] == ['cargo-pricing', 'usefull-topic-2']
        dbid = request.json['dbid']
        uuid = request.json['uuid']
        return {'tags': ctx.driver_tags.get((dbid, uuid), list())}

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='setup_v2_recalc_route_parts_request_enabled')
def _setup_v2_recalc_route_parts_request_enabled(experiments3):
    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_pricing_v2_recalc_route_parts_request_enabled',
        consumers=['cargo-pricing/v1/taxi/calc'],
        clauses=[],
        default_value={'enabled': True},
    )
