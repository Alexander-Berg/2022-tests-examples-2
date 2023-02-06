import pytest


@pytest.mark.parametrize(
    """need_to_make_invalid_path""", [pytest.param(True), pytest.param(False)],
)
async def test_paths_valid(
        exp_delivery_configs,
        exp_delivery_gamble_settings,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        testpoint,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        need_to_make_invalid_path,
):
    candidates_json = load_json('candidates.json')
    assert len(candidates_json['candidates']) == 1, 'test misconfiguration'

    candidate_coordinates = candidates_json['candidates'][0]['position']
    assert candidate_coordinates == [37.0, 55.0], 'test misconfiguration'

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(_):
        return candidates_json

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

    @testpoint('route_finder::make_path_invalid')
    def _make_path_invalid(data):
        return {'need_to_make_invalid_path': need_to_make_invalid_path}

    generators = ['two-circles-batch']
    await exp_delivery_gamble_settings(generators=generators)
    await exp_delivery_configs(delivery_gamble_settings=False)

    segments = []
    for i in range(5):
        segments.append(
            create_segment(
                pickup_coordinates=[37.0, 55.0],
                dropoff_coordinates=[37.01, 55.01],
                segment_id=str(i),
            ),
        )
    await state_waybill_proposed()
    await state_taxi_order_performer_found(performer_tariff='courier')

    segment_infos = []
    for segment in segments:
        segment_infos.append(get_segment(segment.id))

    waybills = []
    for segment in segments:
        segment_info = get_segment(segment.id)
        if segment_info['waybill_ref']:
            waybills.append(
                get_waybill(segment_info['waybill_ref'])['waybill'],
            )

    if not need_to_make_invalid_path:
        assert waybills
    else:
        assert not waybills
