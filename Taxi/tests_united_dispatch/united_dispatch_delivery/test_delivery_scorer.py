import collections

import pytest


async def test_driver_scoring(
        testpoint,
        mockserver,
        exp_delivery_configs,
        create_segment,
        state_waybill_proposed,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _score_bulk(request):
        result = {'responses': []}
        for req in request.json['requests']:
            candidate_response = {'candidates': []}
            for candidate in req['candidates']:
                candidate_response['candidates'].append(
                    {'id': candidate['id'], 'score': -42},
                )
            result['responses'].append(candidate_response)
        return result

    @testpoint('delivery_planner::batch_scores')
    def check_batch_scores(data):
        assert data['routes']
        for route in data['routes']:
            for candidate in route['candidates']:
                assert candidate['score'] == -42
                assert candidate['scoring_score'] == -42

    await exp_delivery_configs()

    create_segment()
    await state_waybill_proposed()
    assert check_batch_scores.times_called


async def test_multiple_drivers(
        testpoint,
        mockserver,
        exp_delivery_configs,
        create_segment,
        state_waybill_proposed,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _score_bulk(request):
        result = {'responses': []}
        first = True
        for req in request.json['requests']:
            candidate_response = {'candidates': []}
            for candidate in req['candidates']:
                if first:
                    candidate_response['candidates'].append(
                        {'id': candidate['id'], 'score': -420},
                    )
                    first = False
                else:
                    candidate_response['candidates'].append(
                        {'id': candidate['id'], 'score': -42},
                    )
            result['responses'].append(candidate_response)
        return result

    expected_scores = {-420: 1, -42: 7}

    @testpoint('delivery_planner::batch_scores')
    def check_batch_scores(data):
        scores = collections.defaultdict(int)
        for route in data['routes']:
            for candidate in route['candidates']:
                scores[candidate['score']] += 1
        for key in expected_scores:
            assert key in scores
            assert scores[key] == expected_scores[key]

    await exp_delivery_configs()

    create_segment()
    create_segment()

    await state_waybill_proposed()
    assert check_batch_scores.times_called


@pytest.mark.parametrize(
    'live_candidates_filtered', [False, True, False, True],
)
async def test_live_batching_scoring(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        testpoint,
        live_candidates_filtered,
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
        return {'candidates': []}

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
            candidate_response = {'candidates': []}
            for candidate in req['candidates']:
                resp = {'id': candidate['id'], 'score': 100}
                if return_candidates or not live_candidates_filtered:
                    candidate_response['candidates'].append(resp)
            result['responses'].append(candidate_response)
        return result

    @testpoint('delivery_planner::live_batch_scores')
    def check_batch_scores(data):
        if live_candidates_filtered:
            assert not data['routes']
        elif not return_candidates:
            assert data['routes']

        for route in data['routes']:
            candidate = route['performer']
            expected_score = 100
            assert candidate['scoring_score'] == expected_score

    generators = ['single-segment', 'live-batch']

    await exp_delivery_gamble_settings(generators=generators)
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

    assert check_batch_scores.times_called >= 2
