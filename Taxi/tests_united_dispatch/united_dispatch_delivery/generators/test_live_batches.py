import pytest


def _get_waybill_segment_ids(waybill):
    return {
        segment['segment']['segment']['id'] for segment in waybill['segments']
    }


@pytest.mark.parametrize(
    ','.join(
        [
            'first_segment_kwargs',
            'second_segment_kwargs',
            'should_batch',
            'can_change_next_point_in_path',
        ],
    ),
    [
        pytest.param(
            dict(
                pickup_coordinates=[37.0, 55.01],
                dropoff_coordinates=[37.0, 55.01],
            ),
            dict(
                pickup_coordinates=[37.0, 55.01],
                dropoff_coordinates=[37.0, 55.01],
            ),
            True,
            False,
        ),
        pytest.param(
            dict(
                pickup_coordinates=[37.0, 55.01],
                dropoff_coordinates=[37.0, 55.01],
            ),
            dict(
                pickup_coordinates=[37.0, 55.0],
                dropoff_coordinates=[37.0, 55.0],
            ),
            True,
            True,
        ),
        pytest.param(
            dict(
                pickup_coordinates=[37.0, 55.01],
                dropoff_coordinates=[37.0, 55.01],
            ),
            dict(
                pickup_coordinates=[38.0, 55.0],
                dropoff_coordinates=[38.0, 55.0],
            ),
            False,
            False,
        ),
        pytest.param(
            dict(
                pickup_coordinates=[37.0, 55.01],
                dropoff_coordinates=[37.0, 55.01],
            ),
            dict(
                pickup_coordinates=[38.0, 55.0],
                dropoff_coordinates=[38.0, 55.0],
            ),
            False,
            True,
        ),
        pytest.param(
            dict(
                pickup_coordinates=[37.73310468874161, 55.70329157000376],
                dropoff_coordinates=[37.738243, 55.673692],
            ),
            dict(
                pickup_coordinates=[37.73632964061161, 55.686121950176314],
                dropoff_coordinates=[37.739052, 55.654635],
            ),
            True,
            False,
        ),
        pytest.param(
            dict(
                pickup_coordinates=[37.73310468874161, 55.70329157000376],
                dropoff_coordinates=[37.739052, 55.654635],
            ),
            dict(
                pickup_coordinates=[37.73632964061161, 55.686121950176314],
                dropoff_coordinates=[37.738243, 55.673692],
            ),
            True,
            False,
        ),
    ],
)
async def test_live_batching(
        exp_delivery_configs,
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        first_segment_kwargs,
        second_segment_kwargs,
        should_batch,
        can_change_next_point_in_path,
):
    candidates_json = load_json('candidates.json')
    assert len(candidates_json['candidates']) == 1, 'test misconfiguration'

    candidate_coordinates = candidates_json['candidates'][0]['position']
    assert candidate_coordinates == [
        37.733474,
        55.702543,
    ], 'test misconfiguration'

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

    generators = ['single-segment', 'live-batch']
    await exp_delivery_gamble_settings(generators=generators)
    await exp_delivery_generators_settings(
        can_change_next_point_in_path=can_change_next_point_in_path,
    )
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )

    segment1 = create_segment(**first_segment_kwargs)
    await state_waybill_proposed()
    await state_taxi_order_performer_found(performer_tariff='courier')

    # no more candidates for the second segment
    return_candidates = False

    segment2 = create_segment(**second_segment_kwargs)
    await state_waybill_proposed()

    segment1_info = get_segment(segment1.id)
    segment2_info = get_segment(segment2.id)

    waybill1 = get_waybill(segment1_info['waybill_ref'])['waybill']

    assert _get_waybill_segment_ids(waybill1) == {segment1.id}
    if should_batch:
        waybill2 = get_waybill(segment2_info['waybill_ref'])['waybill']
        assert _get_waybill_segment_ids(waybill2) == {segment1.id, segment2.id}
    else:
        assert get_waybill(segment2_info['waybill_ref']) is None
