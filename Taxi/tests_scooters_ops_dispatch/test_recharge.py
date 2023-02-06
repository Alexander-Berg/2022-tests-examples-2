import datetime

import pytest


@pytest.mark.experiments3(filename='scooters_ops_jobs_times.json')
@pytest.mark.experiments3(filename='scooters_ops_candidates_filter.json')
@pytest.mark.experiments3(filename='recharge_scooters_min_load.json')
@pytest.mark.experiments3(
    filename='recharge_scooters_request_additional_drafts.json',
)
@pytest.mark.config(TAGS_INDEX={'enabled': True})
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'candidate_0', 'scooters_batteries_capacity_2'),
        ('dbid_uuid', 'candidate_1', 'scooters_batteries_capacity_6'),
        ('dbid_uuid', 'candidate_2', 'scooters_batteries_capacity_10'),
    ],
    topic_relations=[
        ('scooters_ops', 'scooters_batteries_capacity_2'),
        ('scooters_ops', 'scooters_batteries_capacity_6'),
        ('scooters_ops', 'scooters_batteries_capacity_10'),
    ],
)
@pytest.mark.config(SCOOTERS_OPS_DISPATCH_PERIOD=1)
@pytest.mark.config(SCOOTERS_OPS_DISPATCH_POINT_RADIUS=1)
@pytest.mark.now('2022-02-16T12:00:00+03:00')
@pytest.mark.config(
    SCOOTERS_OPS_DISPATCH_ROUTER_CACHE_SETTINGS={
        'limit_rps': 5000,
        'mget_chunk_size': 5000,
        'leaky_bucket_wait_time': 1,
        'expire_times': {'__default__': 86400},
        'command_control': {
            'max_retries': 1,
            'timeout_all': 1000,
            'timeout_single': 200,
        },
    },
)
@pytest.mark.config(
    SCOOTERS_OPS_DISPATCH_ROUTER_SETTINGS={
        'leaky_bucket_wait_time': 1,
        'router_params': {
            '__default__': {'enabled': False, 'limit_rps': 1},
            'scooter': {'enabled': True, 'limit_rps': 100},
        },
    },
)
@pytest.mark.config(
    ROUTER_MATRIX_MAPS_ENABLED=True,
    ROUTER_SELECT=[
        {'routers': ['yamaps-matrix', 'yamaps', 'linear-fallback']},
    ],
)
@pytest.mark.router_request_info(file='routing.json')
@pytest.mark.parametrize(
    'dispatch_job_enabled, create_missions_enabled',
    [
        pytest.param(False, False, id='job_disabled_by_config'),
        pytest.param(True, False, id='create_missions_disabled'),
        pytest.param(True, True, id='simple'),
    ],
)
@pytest.mark.redis_store(file='redis')
async def test_recharge(
        taxi_scooters_ops_dispatch,
        taxi_scooters_ops_dispatch_monitor,
        mockserver,
        taxi_config,
        load_json,
        mocked_time,
        redis_store,
        testpoint,
        dispatch_job_enabled,
        create_missions_enabled,
        mock_router_matrix,
):
    taxi_config.set_values(
        {
            'SCOOTERS_OPS_DISPATCH_ENABLED': dispatch_job_enabled,
            'SCOOTERS_OPS_DISPATCH_CREATE_MISSIONS_ENABLED': (
                create_missions_enabled
            ),
        },
    )

    @mockserver.json_handler('/scooters-misc/admin/v1/depots/list')
    def mock_depots_list(request):
        assert request.json['limit'] == 10000
        return mockserver.make_response(
            status=200, json=load_json('depots_list.json'),
        )

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    def mock_areas(request):
        assert sorted(request.json['tags']) == [
            'depot_recharge_on_car_zone',
            'depot_recharge_zone',
            'depot_relocation_on_car_zone',
        ]
        return mockserver.make_response(
            status=200, json=load_json('areas.json'),
        )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_scooters_positions(request):
        return mockserver.make_response(
            status=200, json=load_json('scooters_positions.json'),
        )

    @mockserver.json_handler('/scooters-ops/scooters-ops/v1/drafts/actual')
    def mock_actual_drafts(request):
        return mockserver.make_response(
            status=200, json=load_json('actual_drafts.json'),
        )

    @mockserver.json_handler('/scooters-ops/scooters-ops/v1/missions/list')
    def mock_missions_list(request):
        return mockserver.make_response(
            status=200, json=load_json('missions_list_response.json'),
        )

    @mockserver.json_handler(
        '/scooters-ops/scooters-ops/v1/drafts/create-for-target',
    )
    def mock_drafts_create_for_target(request):
        for target in request.json['targets']:
            target['id'] = 'uuid'
        assert request.json == load_json(
            'drafts_create_for_target_request.json',
        )
        return mockserver.make_response(
            status=200,
            json=load_json('drafts_create_for_target_response.json'),
        )

    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(request):
        if (
                request.json['order']['request']['scooters']['operators_type']
                == 'energizers'
        ):
            json = load_json('candidates.json')
            point = request.json['point']
            response_for_point = json[str(point[0]) + ',' + str(point[1])]
            return mockserver.make_response(
                status=200, json=response_for_point,
            )
        return mockserver.make_response(status=200, json='{}')

    @mockserver.json_handler('/scooters-ops/scooters-ops/v1/missions/create')
    def mock_missions_create(request):
        expected_requests_json = load_json('missions_create_requests.json')
        performer_id = request.json['performer_id']
        expected_request = expected_requests_json[performer_id]

        assert request.json == expected_request

        return mockserver.make_response(
            status=200, json=load_json('missions_create_response.json'),
        )

    @testpoint('dispatch-job::compare_depots_list_size')
    def _depots_list_testpoint(result):
        assert result == 2

    @testpoint('dispatch-job::compare_areas_size')
    def _areas_testpoint(result):
        assert result == 2

    @testpoint('dispatch-job::compare_scooters_positions_cache_size')
    def _depots_scooters_positions_testpoint(result):
        assert result == 9

    @testpoint('dispatch-job::compare_actual_drafts_size')
    def _actual_drafts_testpoint(result):
        assert result == 6

    @testpoint('dispatch-job::compare_time_until_closing')
    def _time_until_closing_testpoint(result):
        assert result == 18 * 60 * 60

    @testpoint('dispatch-job::compare_busy_candidates_size')
    def _busy_candidates_size_testpoint(result):
        assert result == 1

    @testpoint('dispatch-job::filter_candidate')
    def _filter_candidate_testpoint(result):
        pass

    await taxi_scooters_ops_dispatch.run_distlock_task('dispatch-job')

    assert mock_depots_list.has_calls == dispatch_job_enabled
    assert _depots_list_testpoint.times_called == dispatch_job_enabled

    assert mock_areas.has_calls == dispatch_job_enabled
    assert _areas_testpoint.times_called == dispatch_job_enabled

    assert mock_missions_list.has_calls == dispatch_job_enabled
    assert _busy_candidates_size_testpoint.times_called == dispatch_job_enabled

    assert _filter_candidate_testpoint.times_called == 1 * dispatch_job_enabled

    assert mock_order_search.has_calls == dispatch_job_enabled
    assert mock_order_search.times_called == 2 * 2 * dispatch_job_enabled

    assert mock_scooters_positions.has_calls
    assert (
        _depots_scooters_positions_testpoint.times_called
        == dispatch_job_enabled
    )

    assert mock_actual_drafts.has_calls == dispatch_job_enabled
    assert _actual_drafts_testpoint.times_called == dispatch_job_enabled

    assert mock_drafts_create_for_target.has_calls == dispatch_job_enabled

    assert (
        _time_until_closing_testpoint.times_called == 2 * dispatch_job_enabled
    )

    #  2 for contractors, 5 for depots & scooters
    assert mock_router_matrix.times_called() == (2 + 5) * dispatch_job_enabled

    assert (
        mock_missions_create.times_called
        == 2 * dispatch_job_enabled * create_missions_enabled
    )

    # check that we have 4 known routes in cache
    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=15))
    await taxi_scooters_ops_dispatch.tests_control(invalidate_caches=False)
    metrics = await taxi_scooters_ops_dispatch_monitor.get_metric(
        'scooters_ops_dispatch_metrics',
    )
    if metrics:
        assert metrics['route_info_from_cache']['scooter']['true'] == 4
