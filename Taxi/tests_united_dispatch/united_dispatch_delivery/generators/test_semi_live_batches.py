import pytest


def _get_waybill_segment_ids(waybill):
    return {
        segment['segment']['segment']['id'] for segment in waybill['segments']
    }


async def _run_test(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        live_batches_enabled,
        first_segment_kwargs,
        second_segment_kwargs,
        should_batch,
        performer_tariff,
        same_corp_validation_for_clients,
):
    if not live_batches_enabled:
        assert not should_batch, 'test misconfiguration'

    candidates_json = load_json('candidates.json')
    assert len(candidates_json['candidates']) == 1, 'test misconfiguration'

    candidate_coordinates = candidates_json['candidates'][0]['position']
    assert candidate_coordinates == [37.0, 55.0], 'test misconfiguration'

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

    generators = ['single-segment']
    if live_batches_enabled:
        generators.append('live-batch')
    await exp_delivery_gamble_settings(generators=generators)
    await exp_delivery_generators_settings(
        same_corp_validation_for_clients=same_corp_validation_for_clients,
        batch_size2_goodness_ratio=1,
    )
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )

    segment1 = create_segment(**first_segment_kwargs)
    await state_taxi_order_performer_found(performer_tariff=performer_tariff)

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


async def test_live_batching_unique_candidates(
        exp_delivery_configs,
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        testpoint,
):
    candidates_json = load_json('candidates.json')
    assert len(candidates_json['candidates']) == 1, 'test misconfiguration'

    candidate_coordinates = [37.0, 55.0]

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

    @testpoint('delivery_planner::unique_performers')
    def check_performers(data):
        all_performers = set()
        for performer in data:
            assert performer not in all_performers
            all_performers.add(performer)

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

    assert check_performers.times_called == 2


async def test_turn_off_live_batch(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
):
    await _run_test(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        False,
        dict(
            pickup_coordinates=[37.0, 55.0],
            dropoff_coordinates=[37.0, 55.0],
            corp_client_id='client1',
        ),
        dict(
            pickup_coordinates=[37.0, 55.0],
            dropoff_coordinates=[37.0, 55.0],
            corp_client_id='client1',
        ),
        False,
        'courier',
        [],
    )


@pytest.mark.parametrize(
    """client""", [pytest.param('client1'), pytest.param('client2')],
)
async def test_same_corp_validation(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        client,
):
    await _run_test(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        True,
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client1',
        ),
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client2',
        ),
        False,
        'courier',
        [client],
    )


async def test_batch_disallow(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
):
    await _run_test(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        True,
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client1',
        ),
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client1',
            allow_alive_batch_v1=False,
            allow_alive_batch_v2=False,
        ),
        False,
        'courier',
        [],
    )


async def test_express_disallow(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
):
    await _run_test(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        True,
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client1',
        ),
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client1',
        ),
        False,
        'express',
        [],
    )


async def test_forbidden_batch(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
):
    await _run_test(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        True,
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client1',
            allow_alive_batch_v1=False,
            allow_alive_batch_v2=False,
        ),
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client1',
        ),
        False,
        'courier',
        [],
    )


async def test_should_batch(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
):
    await _run_test(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        True,
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.001, 55.01],
            corp_client_id='client1',
        ),
        dict(
            pickup_coordinates=[37.001, 55.01],
            dropoff_coordinates=[37.001, 55.01],
            corp_client_id='client1',
        ),
        True,
        'courier',
        [],
    )


async def test_no_same_clients_batch(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
):
    await _run_test(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        create_segment,
        get_segment,
        get_waybill,
        True,
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client1',
        ),
        dict(
            pickup_coordinates=[37.0, 55.01],
            dropoff_coordinates=[37.0, 55.01],
            corp_client_id='client2',
        ),
        True,
        'courier',
        [],
    )
