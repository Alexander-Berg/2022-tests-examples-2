import pytest


@pytest.mark.experiments3(filename='scooters_ops_jobs_times.json')
@pytest.mark.config(TAGS_INDEX={'enabled': True})
@pytest.mark.tags_v2_index(
    tags_list=[('dbid_uuid', 'candidate_2', 'scooters_relocation_capacity_2')],
    topic_relations=[('scooters_ops', 'scooters_relocation_capacity_2')],
)
@pytest.mark.config(SCOOTERS_OPS_DISPATCH_PERIOD=1)
@pytest.mark.config(SCOOTERS_OPS_DISPATCH_POINT_RADIUS=1)
@pytest.mark.config(SCOOTERS_OPS_DISPATCH_ENABLED=True)
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
    'relocation_enabled, create_missions_enabled',
    [
        pytest.param(False, False, id='relocation_disabled'),
        pytest.param(True, False, id='create_missions_disabled'),
        pytest.param(True, True, id='simple'),
    ],
)
@pytest.mark.redis_store(file='redis')
async def test_relocation(
        taxi_scooters_ops_dispatch,
        mockserver,
        taxi_config,
        load_json,
        mocked_time,
        testpoint,
        relocation_enabled,
        create_missions_enabled,
        experiments3,
):
    relocation_exp = load_json('relocation_scooters_enabled.json')['configs'][
        0
    ]
    relocation_exp['default_value']['run_algorithm'] = relocation_enabled
    relocation_exp['default_value'][
        'create_missions'
    ] = create_missions_enabled
    experiments3.add_config(**relocation_exp)

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

    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(request):
        if (
                request.json['order']['request']['scooters']['operators_type']
                == 'relocators'
        ):
            return mockserver.make_response(
                status=200, json=load_json('candidates.json'),
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
        assert result == 1

    @testpoint('dispatch-job::compare_areas_size')
    def _areas_testpoint(result):
        assert result == 1

    @testpoint('dispatch-job::compare_actual_drafts_size')
    def _actual_drafts_testpoint(result):
        assert result == 8

    @testpoint('dispatch-job::compare_time_until_closing')
    def _time_until_closing_testpoint(result):
        assert result == 18 * 60 * 60

    await taxi_scooters_ops_dispatch.run_distlock_task('dispatch-job')

    assert mock_depots_list.has_calls
    assert mock_areas.has_calls
    assert mock_scooters_positions.has_calls
    assert mock_actual_drafts.has_calls
    assert mock_order_search.has_calls

    assert _depots_list_testpoint.times_called == 1
    assert _areas_testpoint.has_calls
    assert _actual_drafts_testpoint.has_calls
    assert _time_until_closing_testpoint.has_calls

    assert mock_missions_create.times_called == (
        relocation_enabled and create_missions_enabled
    )
