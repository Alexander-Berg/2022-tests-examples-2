# pylint: disable=invalid-name
import pytest


@pytest.fixture(name='exp_segment_executors_selector')
async def _exp_segment_executors_selectors(experiments3, united_dispatch_unit):
    async def wrapper(*, executors=None):
        if executors is None:
            executors = [
                {'planner_type': 'testsuite-candidates', 'is_active': True},
                {'planner_type': 'crutches', 'is_active': True},
                {'planner_type': 'grocery', 'is_active': True},
                {'planner_type': 'eats', 'is_active': True},
                {'planner_type': 'delivery', 'is_active': True},
                {'planner_type': 'fallback', 'is_active': True},
            ]

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_segment_executors_selector',
            consumers=['united-dispatch/segment-doc'],
            clauses=[],
            default_value={'executors': executors},
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_planner_shard')
async def _exp_planner_shard(experiments3, united_dispatch_unit):
    async def wrapper(*, shard='default'):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_planner_shard',
            consumers=['united-dispatch/make-segment-executor'],
            clauses=[],
            default_value={'shard': shard},
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_proposition_fail')
async def _exp_proposition_fail(experiments3, united_dispatch_unit):
    async def wrapper(*, clean_waybill_on_decline=True):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_proposition_fail',
            consumers=['united-dispatch/proposition-fail'],
            clauses=[],
            default_value={
                'clean_waybill_on_decline': clean_waybill_on_decline,
            },
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_planner_settings')
async def _exp_planner_settings(experiments3, united_dispatch_unit):
    async def wrapper(
            *,
            enabled=True,
            waybill_geoindex_enabled=True,
            wait_until_due_seconds=1800,
            idle_waybills_limit=10,
            waybills_limit=10,
            enable_store_segment_gambles=False,
            check_throttled_segment_on_apply=False,
            throttle_segment_schedule=None,
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_planner_settings',
            consumers=['united-dispatch/planner-run'],
            clauses=[],
            default_value={
                'enabled': enabled,
                'unprocessed_limit': 100,
                'waybill_geoindex_enabled': waybill_geoindex_enabled,
                'idle_waybills_limit': idle_waybills_limit,
                'waybills_limit': waybills_limit,
                'wait_until_due_seconds': wait_until_due_seconds,
                'enable_store_segment_gambles': enable_store_segment_gambles,
                'check_throttled_segment_on_apply': (
                    check_throttled_segment_on_apply
                ),
                'throttle_segment_schedule': throttle_segment_schedule,
            },
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_delivery_gamble_settings')
async def _exp_delivery_gamble_settings(experiments3, united_dispatch_unit):
    async def wrapper(
            *,
            use_taxi_dispatch=False,
            generators=['single-segment', 'two-circles-batch'],
            lookup_flow='taxi-dispatch',
            exclude_rejected_candidates=True,
            candidate_rejection_limit=0,
            disable_maps_router=True,
            validate_all_transport_types=False,
            transport_types_for_validation=['pedestrian'],
            forcedly_batched_origins=[],
            return_time_left=None,
            shift_scores_to_nonnegative=False,
            min_edge_score=1,
            solvers=None,
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name=(
                'united_dispatch_delivery_proposition_builder_gamble_settings'
            ),
            consumers=['united-dispatch/planner-run'],
            clauses=[],
            default_value={
                'allow_batching_classes': ['courier'],
                'use_taxi_dispatch': use_taxi_dispatch,
                'generators': generators,
                'shift_scores_to_nonnegative': shift_scores_to_nonnegative,
                'min_edge_score': min_edge_score,
                'batch_restrictions': {
                    'max_number_of_destination_points': 1,
                    'required_taxi_classes': ['courier'],
                    'disabled_for_employers': [
                        'eats',
                        'grocery',
                        'food_retail',
                    ],
                    'return_time_left': return_time_left,
                },
                'logging': {'log_generated_routes_info': True},
                'solvers': solvers or [
                    {'type': 'greedy', 'tag': 'greedy-solver'},
                    {
                        'type': 'greedy',
                        'tag': 'greedy-solver-min1000',
                        'min_nontrivial_route_score': 1000,
                    },
                    {'type': 'exclusive', 'tag': 'exclusive-solver'},
                    {
                        'type': 'hungarian_sandwich',
                        'tag': 'hungarian-sandwich-solver',
                        'batches_ratio': 0.1,
                    },
                ],
                'premium_clients': ['moscow.*'],
                'disable_maps_router': disable_maps_router,
                'max_simultaneous_router_requests': 50,
                'lookup_flow': lookup_flow,
                'exclude_rejected_candidates': exclude_rejected_candidates,
                'candidate_rejection_limit': candidate_rejection_limit,
                'enable_batch_lateness_validator': True,
                'enable_batch_earliness_validator': True,
                'validate_all_transport_types': validate_all_transport_types,
                'transport_types_for_validation': (
                    transport_types_for_validation
                ),
                'cargo_pipeline_forcedly_batched_origins': (
                    forcedly_batched_origins
                ),
            },
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_performer_repeat_search')
async def _exp_performer_repeat_search(experiments3, united_dispatch_unit):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_performer_for_order_repeat_search',
            consumers=['united-dispatch/performer-for-order'],
            clauses=[],
            default_value={'enabled': True},
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_rejected_candidates_load_settings')
async def _exp_rejected_candidates_load_settings(
        experiments3, united_dispatch_unit,
):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_rejected_candidates_load_settings',
            consumers=['united-dispatch/planner-run'],
            clauses=[],
            default_value={
                'enabled': True,
                'bulk_limit': 10,
                'load_limit': 500,
                'simultaneous_requests_limit': 2,
            },
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_frozen_candidates_settings')
async def _exp_frozen_candidates_settings(experiments3, united_dispatch_unit):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_frozen_candidates_settings',
            consumers=['united-dispatch/frozen-candidates'],
            clauses=[],
            default_value={
                'enabled': True,
                'expiration_time': 10,
                'freeze_bulk_limit': 100,
                'simultaneous_freeze_requests_limit': 100,
            },
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_delivery_generators_settings')
async def _exp_delivery_generators_settings(
        experiments3, united_dispatch_unit,
):
    async def wrapper(
            batch_size2_goodness_diff=-5000,
            batch_size2_goodness_ratio=0,
            max_segment_duration_increase=4,
            batch_size2_goodness_diff_pre_filtration=-5000,
            batch_size2_goodness_ratio_pre_filtration=0,
            max_segment_duration_increase_pre_filtration=10,
            distance_of_arrival=10,
            max_batches_per_segment=10,
            max_mean_batches_per_segment=10,
            lookup_segments_num=1000,
            pickup_radius_mult=1.5,
            dropoff_radius_mult=50,
            pickup_radius_bias=0.5,
            dropoff_radius_bias=0,
            min_batch_size=2,
            max_batch_size=6,
            min_performer_eta=1,
            max_performer_eta=200,
            pickup_time=5,
            dropoff_time=5,
            same_corp_validation_for_clients=None,
            extra_segments_handling_num=1,
            num_best_routes_route_finder=5,
            max_lookup_radius=0.1,
            can_change_next_point_in_path=False,
            forbidden_second_in_batch_sla=0,
            strict_from_interval_diff=0,
            strict_to_interval_diff=0,
    ):
        same_corp_validation_config = {'__default__': False}
        if same_corp_validation_for_clients:
            for client in same_corp_validation_for_clients:
                same_corp_validation_config[f'*.{client}'] = True

        MAX_MERGE_SEGMENT_PACKS = (
            'max_packs_per_segment_threshold_for_merge_segment_packs'
        )
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_delivery_generators_settings',
            consumers=['united-dispatch/planner-run'],
            clauses=[],
            default_value={
                'common': {
                    'batch_size2_goodness_diff_threshold': {
                        '__default__': batch_size2_goodness_diff,
                        'test_zone_id.*': 3,
                        '*.test_corp_id': 4,
                        'test_zone_id.test_corp_id': 1,
                        '__pre_filtration__': (
                            batch_size2_goodness_diff_pre_filtration
                        ),
                    },
                    'batch_size2_goodness_ratio_threshold': {
                        '__default__': batch_size2_goodness_ratio,
                        'test_zone_id.test_corp_id': 1.9,
                        '__pre_filtration__': (
                            batch_size2_goodness_ratio_pre_filtration
                        ),
                    },
                    'max_segment_duration_increase': {
                        '__default__': max_segment_duration_increase,
                        'test_zone_id.*': 2.1,
                        '__pre_filtration__': (
                            max_segment_duration_increase_pre_filtration
                        ),
                    },
                    'distance_of_arrival': {
                        '__default__': distance_of_arrival,
                    },
                    'max_batches_per_segment': {
                        '__default__': max_batches_per_segment,
                    },
                    'max_mean_batches_per_segment': {
                        '__default__': max_mean_batches_per_segment,
                    },
                    'add_same_corp_validation': same_corp_validation_config,
                    'buffer_settings': {
                        '__default__': {
                            'p2p_after_created': None,
                            'p2p_before_due': None,
                        },
                    },
                    'min_batch_size': {'__default__': min_batch_size},
                    'max_batch_size': {'__default__': max_batch_size},
                    'min_performer_eta': {'__default__': min_performer_eta},
                    'max_performer_eta': {'__default__': max_performer_eta},
                    'pickup_time': {'__default__': pickup_time},
                    'dropoff_time': {'__default__': dropoff_time},
                    'forbidden_second_in_batch_sla': {
                        '__default__': forbidden_second_in_batch_sla,
                    },
                    'strict_from_interval_diff': {
                        '__default__': strict_from_interval_diff,
                    },
                    'strict_to_interval_diff': {
                        '__default__': strict_to_interval_diff,
                    },
                    MAX_MERGE_SEGMENT_PACKS: 1000,
                    'intersected_threshold_for_merge_segment_packs': 1,
                },
                'route_finder': {
                    'num_best_routes': num_best_routes_route_finder,
                    'init_annealing_probability': 0.7,
                    'edges_swap_annealing_it_num': 10,
                    'extra_segments_handling_num': extra_segments_handling_num,
                    'segments_swap_annealing_it_mult': 5,
                    'max_num_of_swap_edges_attempts': 5,
                },
                'two_circles_batch': {
                    'lookup_segments_num': {
                        '__default__': lookup_segments_num,
                    },
                    'pickup_radius_mult': {'__default__': pickup_radius_mult},
                    'dropoff_radius_mult': {
                        '__default__': dropoff_radius_mult,
                    },
                    'pickup_radius_bias': {'__default__': pickup_radius_bias},
                    'dropoff_radius_bias': {
                        '__default__': dropoff_radius_bias,
                    },
                },
                'two_circles_premium_batch': {
                    'lookup_segments_num': {
                        '__default__': lookup_segments_num,
                    },
                    'pickup_radius_mult': {'__default__': pickup_radius_mult},
                    'dropoff_radius_mult': {
                        '__default__': dropoff_radius_mult,
                    },
                    'pickup_radius_bias': {'__default__': pickup_radius_bias},
                    'dropoff_radius_bias': {
                        '__default__': dropoff_radius_bias,
                    },
                },
                'angle_distance_generator': {
                    'lookup_segments_num': {
                        '__default__': lookup_segments_num,
                    },
                    'angle_mult': {'__default__': 0.08},
                    'max_lookup_radius': {'__default__': max_lookup_radius},
                },
                'live_batch': {
                    'candidates_limit': 20,
                    'candidates_max_search_radius': 10000,
                    'can_change_next_point_in_path': (
                        can_change_next_point_in_path
                    ),
                },
            },
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_sla_groups_settings')
async def _exp_sla_groups_settings(experiments3, united_dispatch_unit):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_sla_groups_settings',
            consumers=['united-dispatch/planner-run'],
            clauses=[],
            default_value={
                '__default__': {
                    'max_segment_duration_absolute_increase': 12000,
                },
                'no_corp_group': {
                    'max_segment_duration_absolute_increase': 24000,
                },
                'batching_without_delay': {
                    'max_segment_duration_absolute_increase': 0,
                },
                'batching_max_10min': {
                    'max_segment_duration_absolute_increase': 600,
                },
            },
        )
        await united_dispatch_unit.invalidate_caches()

    return wrapper


@pytest.fixture(name='exp_clients_to_sla_groups_mapping')
async def _exp_clients_to_sla_groups_mapping(
        experiments3, united_dispatch_unit,
):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_clients_to_sla_groups_mapping',
            consumers=['united-dispatch/planner-run'],
            clauses=[],
            default_value={
                '__default__': '__default__',
                '*.__no_corp_client_id__': 'no_corp_group',
                '*.test_corp_id_0m': 'batching_without_delay',
                '*.test_corp_id_10m': 'batching_max_10min',
            },
        )
        await united_dispatch_unit.invalidate_caches()

    return wrapper


@pytest.fixture(name='exp_eats_dispatch_settings')
async def _exp_eats_dispatch_settings(experiments3, united_dispatch_unit):
    async def wrapper(
            *,
            intent='united-dispatch-eats',
            log_candidates=True,
            log_live_batch_candidates=True,
            algorithm='hungarian',
            pass_score=1e6,
            separate_batches_solving=False,
            lookup_flow='taxi-dispatch',
            manually_filter_candidates=False,
            enable_live_batches=True,
            enable_segments_filtration=False,
            allow_distinct_places=True,
            max_linear_distance=20000,
            max_real_distance=10000,
            due_threshold=10 * 60,
            max_late_dropoff=5 * 60,
            live_batch_max_candidates=10,
            live_batch_max_distance=10000,
            linear_sideways_allowance=10000,
            linear_backwards_allowance=10000,
            route_sideways_allowance=10000,
            route_backwards_allowance=10000,
            exclude_rejected_candidates=False,
            candidate_rejection_limit=0,
            exclude_return_points=False,
            request_cpo_for_driver_scoring=False,
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_eats_dispatch',
            consumers=['united-dispatch/planner-run'],
            clauses=[],
            default_value={
                'intent': intent,
                'log_candidates': log_candidates,
                'algorithm': algorithm,
                'pass_score': pass_score,
                'separate_batches_solving': separate_batches_solving,
                'lookup_flow': lookup_flow,
                'exclude_rejected_candidates': exclude_rejected_candidates,
                'candidate_rejection_limit': candidate_rejection_limit,
                'exclude_return_points': exclude_return_points,
                'manually_filter_candidates': manually_filter_candidates,
                'request_cpo_for_driver_scoring': (
                    request_cpo_for_driver_scoring
                ),
                'live_batching': {
                    'limit': live_batch_max_candidates,
                    'max_distance': live_batch_max_distance,
                    'batch_linear_sideways_allowance_abs': (
                        linear_sideways_allowance
                    ),
                    'batch_linear_backwards_allowance_abs': (
                        linear_backwards_allowance
                    ),
                    'batch_route_sideways_allowance_abs': (
                        route_sideways_allowance
                    ),
                    'batch_route_backwards_allowance_abs': (
                        route_backwards_allowance
                    ),
                    'enable_batching': enable_live_batches,
                    'enable_segments_filtration': enable_segments_filtration,
                    'allow_distinct_places': allow_distinct_places,
                    'distinct_places_settings': {
                        'allow': allow_distinct_places,
                        'max_linear_distance': max_linear_distance,
                        'max_real_distance': max_real_distance,
                    },
                    'log_candidates': log_live_batch_candidates,
                    'max_late_dropoff': max_late_dropoff,
                    'due_threshold': due_threshold,
                },
            },
        )
        await united_dispatch_unit.invalidate_caches(
            clean_update=False, cache_names=['experiments3-cache'],
        )

    return wrapper


@pytest.fixture(name='exp_eats_scoring_coefficients')
async def _exp_eats_scoring_coefficients(experiments3, united_dispatch_unit):
    async def wrapper(
            *,
            pickup_cost=10,
            dropoff_cost=15,
            long_arrival_cost=20,
            long_arrival_distance_km=1,
            arrival_kilometer_payment=10,
            delivery_kilometer_payment=12,
            additional_cost=100,
    ):
        default_value = {
            'pickup_cost': pickup_cost,
            'dropoff_cost': dropoff_cost,
            'long_arrival_cost': 0,
            'arrival_kilometer_payment': arrival_kilometer_payment,
            'delivery_kilometer_payment': delivery_kilometer_payment,
            'additional_cost': additional_cost,
        }
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_eats_scoring_coefficients',
            consumers=['united-dispatch/eats-scoring-coefficients'],
            clauses=[
                {
                    'predicate': {
                        'init': {
                            'arg_name': 'arrival_distance_km',
                            'arg_type': 'double',
                            'value': long_arrival_distance_km,
                        },
                        'type': 'gte',
                    },
                    'value': dict(
                        default_value, long_arrival_cost=long_arrival_cost,
                    ),
                },
            ],
            default_value=default_value,
        )
        await united_dispatch_unit.invalidate_caches()

    return wrapper


# pylint: disable=invalid-name
@pytest.fixture(name='exp_eats_segment_scoring_method')
async def _exp_eats_segment_scoring_method(experiments3, united_dispatch_unit):
    async def wrapper(
            *,
            use_driver_scoring_score_for_segments=True,
            use_driver_scoring_score_for_batches=True,
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='united_dispatch_eats_segment_scoring_method',
            consumers=['united-dispatch/eats-segment-scoring-method'],
            clauses=[],
            default_value={
                'use_driver_scoring_score_for_segments': (
                    use_driver_scoring_score_for_segments
                ),
                'use_driver_scoring_score_for_batches': (
                    use_driver_scoring_score_for_batches
                ),
            },
        )
        await united_dispatch_unit.invalidate_caches()

    return wrapper
