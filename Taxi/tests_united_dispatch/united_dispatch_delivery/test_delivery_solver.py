import pytest


async def test_multi_solver(
        testpoint,
        experiments3,
        create_segment,
        mockserver,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        state_waybill_proposed,
):
    await exp_delivery_gamble_settings(use_taxi_dispatch=False)

    configs = experiments3.get_configs('united-dispatch/planner-run', 0)[-1][
        'default_value'
    ]['solvers']

    await exp_delivery_configs(delivery_gamble_settings=False)

    create_segment()
    create_segment()
    create_segment(
        pickup_coordinates=[37.4005, 55.7002],
        dropoff_coordinates=[37.4003, 55.7004],
    )

    settings_tags = [config['tag'] for config in configs]
    settings_tags.sort()

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _score_bulk(request):
        result = {'responses': []}
        for req in request.json['requests']:
            candidate_response = {'candidates': []}
            for candidate in req['candidates']:
                candidate_response['candidates'].append(
                    {'id': candidate['id'], 'score': -10},
                )
            result['responses'].append(candidate_response)
        return result

    @testpoint('delivery_planner::best_solver')
    def check_best_solver(data):
        assert data['best_solver'] == 'greedy-solver'
        assert data['num_total_conflicts'] == 0

    @testpoint('delivery_planner::created_solvers')
    def check_created_solvers(data):
        tags = [element['solver_tag'] for element in data]
        tags.sort()
        assert tags == settings_tags

    await state_waybill_proposed()
    assert check_created_solvers.times_called
    assert check_best_solver.times_called


async def test_retention_score(
        testpoint,
        mockserver,
        create_segment,
        exp_delivery_configs,
        state_waybill_proposed,
        exp_delivery_gamble_settings,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _score_bulk(request):
        result = {'responses': []}
        for req in request.json['requests']:
            candidate_response = {'candidates': []}
            for candidate in req['candidates']:
                candidate_response['candidates'].append(
                    {'id': candidate['id'], 'score': -15},
                )
            candidate_response['search'] = {'retention_score': 23}
            result['responses'].append(candidate_response)
        return result

    create_segment()

    @testpoint('delivery_planner::best_solver')
    def check_result(data):
        assert data['score'] == 8

    await exp_delivery_configs()
    await exp_delivery_gamble_settings(
        shift_scores_to_nonnegative=True, min_edge_score=0,
    )
    await state_waybill_proposed()
    assert check_result.times_called


@pytest.mark.parametrize(
    'live_batch_score,p2p_score,live_batch_assigned',
    [(1, 10, False), (100, 10, True)],
)
async def test_live_batching_solving(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        testpoint,
        live_batch_score,
        p2p_score,
        live_batch_assigned,
):
    candidate_coordinates = [37.0, 55.0]

    candidates_json = load_json('candidates.json')
    candidates_json['candidates'] = [candidates_json['candidates'][0]]
    candidates_json['position'] = candidate_coordinates

    return_candidates = True

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(_):
        if return_candidates:
            return candidates_json
        return []

    @mockserver.json_handler('/driver-trackstory/positions')
    def _driver_position(request):
        result = []
        for driver_id in request.json['driver_ids']:
            result.append(
                {
                    'position': {
                        'lon': candidate_coordinates[0],
                        'lat': candidate_coordinates[1],
                        'timestamp': 10,
                    },
                    'type': 'adjusted',
                    'driver_id': driver_id,
                },
            )

        return {'results': result}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _score_bulk(request):
        result = {'responses': []}
        for req in request.json['requests']:
            num_segments = req['search']['order']['request'][
                'batch_properties'
            ]['batch_aggregates']['num_segments']
            score = -p2p_score
            if num_segments > 1:
                score = -live_batch_score

            candidate_response = {'candidates': []}
            for candidate in req['candidates']:
                resp = {'id': candidate['id'], 'score': score}
                candidate_response['candidates'].append(resp)

            result['responses'].append(candidate_response)
        return result

    @testpoint('delivery_planner::best_solver')
    def check_result(data):
        if return_candidates:
            return
        if live_batch_assigned:
            assert data['score'] == live_batch_score - p2p_score
        else:
            assert data['score'] == p2p_score - live_batch_score

    generators = ['single-segment', 'live-batch']

    await exp_delivery_gamble_settings(
        generators=generators,
        shift_scores_to_nonnegative=True,
        min_edge_score=0,
    )
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )

    first_segment_kwargs = dict(
        pickup_coordinates=[37.0, 55.01],
        dropoff_coordinates=[37.0, 55.01],
        corp_client_id='client1',
    )
    second_segment_kwargs = dict(
        pickup_coordinates=[37.0, 55.01],
        dropoff_coordinates=[37.0, 55.01],
        corp_client_id='client1',
    )

    create_segment(**first_segment_kwargs)
    await state_taxi_order_performer_found(performer_tariff='courier')

    # no more candidates for the second segment
    return_candidates = False

    create_segment(**second_segment_kwargs)
    await state_waybill_proposed()
    assert check_result.times_called
