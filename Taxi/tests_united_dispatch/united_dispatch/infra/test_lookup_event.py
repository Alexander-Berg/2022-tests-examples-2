import pytest


def _get_callback(mockserver, taxi_order_id, generation=1, version=1, wave=1):
    return {
        'url': (
            mockserver.url('/lookup/v2/event')
            + '?order_id='
            + taxi_order_id
            + '&generation='
            + str(generation)
            + '&wave='
            + str(wave)
            + '&version='
            + str(version)
        ),
        'timeout_ms': 400,
        'attempts': 2,
    }


@pytest.mark.config(
    UNITED_DISPATCH_REJECTED_CANDIDATES_SETTINGS={'enabled': True},
)
async def test_callback_happy_path(
        create_candidates_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        set_waybill_lookup_flow,
        get_single_waybill,
        run_single_planner,
        mockserver,
        testpoint,
        load_json,
        exp_performer_repeat_search,
        exp_rejected_candidates_load_settings,
        performer_for_order,
):

    await exp_performer_repeat_search()
    await exp_rejected_candidates_load_settings()

    @testpoint('lookup-event')
    def _callback(param):
        return {}

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request, body_json):
        return load_json('order_search_response.json')

    @mockserver.json_handler('/lookup/v2/event')
    def _lookup_event(request, body_json):
        assert body_json['candidate']['id'] == 'dbid1_uuid1'
        return {}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        return {
            'responses': [
                {
                    'candidates': [{'id': 'dbid1_uuid1', 'score': 1}],
                    'search': {'retention_score': 1},
                },
            ],
        }

    create_candidates_segment('greedy')

    await state_taxi_order_created()

    waybill = get_single_waybill()
    set_waybill_candidate(
        waybill_ref=waybill['id'], performer_id='dbid1_uuid2',
    )
    set_waybill_lookup_flow(
        waybill_ref=waybill['id'], lookup_flow='united-dispatch',
    )

    taxi_order_id = waybill['waybill']['taxi_order_id']
    response = await performer_for_order(
        taxi_order_id=taxi_order_id,
        callback=_get_callback(mockserver, taxi_order_id),
    )
    assert response['candidate']['id'] == 'dbid1_uuid2'

    # Increase lookup version, this should trigger waybill update and mark
    # waybill for new search

    response = await performer_for_order(
        taxi_order_id=taxi_order_id,
        version=2,
        callback=_get_callback(mockserver, taxi_order_id, version=2),
    )
    assert response == {'message': 'updated'}

    # Start planner which should find new candidate for waybill

    await run_single_planner()
    await _callback.wait_call()

    response = await performer_for_order(
        taxi_order_id=taxi_order_id,
        version=2,
        callback=_get_callback(mockserver, taxi_order_id, version=2),
    )
    assert response['candidate']['id'] == 'dbid1_uuid1'

    assert _lookup_event.has_calls


@pytest.mark.config(
    UNITED_DISPATCH_REJECTED_CANDIDATES_SETTINGS={'enabled': True},
)
async def test_new_callback(
        create_candidates_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        set_waybill_lookup_flow,
        get_single_waybill,
        run_single_planner,
        mockserver,
        testpoint,
        load_json,
        exp_performer_repeat_search,
        exp_rejected_candidates_load_settings,
        performer_for_order,
):

    await exp_performer_repeat_search()
    await exp_rejected_candidates_load_settings()

    @testpoint('lookup-event')
    def _callback(param):
        return {}

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request, body_json):
        return load_json('order_search_response.json')

    @mockserver.json_handler('/lookup/v2/event')
    def _lookup_event(request, body_json):
        assert body_json['candidate']['id'] == 'dbid1_uuid1'
        return {
            'success': False,
            'callback': {
                'url': (
                    mockserver.url('/lookup/v2/event')
                    + '?order_id=XXX&generation=1&wave=1&version=5'
                ),
                'timeout_ms': 300,
                'attempts': 1,
            },
        }

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        return {
            'responses': [
                {
                    'candidates': [{'id': 'dbid1_uuid1', 'score': 1}],
                    'search': {'retention_score': 1},
                },
            ],
        }

    create_candidates_segment('greedy')

    await state_taxi_order_created()

    waybill = get_single_waybill()
    set_waybill_candidate(
        waybill_ref=waybill['id'], performer_id='dbid1_uuid2',
    )
    set_waybill_lookup_flow(
        waybill_ref=waybill['id'], lookup_flow='united-dispatch',
    )

    taxi_order_id = waybill['waybill']['taxi_order_id']
    response = await performer_for_order(
        taxi_order_id=taxi_order_id,
        callback=_get_callback(mockserver, taxi_order_id),
    )
    assert response['candidate']['id'] == 'dbid1_uuid2'

    # Increase lookup version, this should trigger waybill update and mark
    # waybill for new search

    response = await performer_for_order(
        taxi_order_id=taxi_order_id,
        version=2,
        callback=_get_callback(mockserver, taxi_order_id, version=2),
    )
    assert response == {'message': 'updated'}

    # Start planner which should find new candidate for waybill

    await run_single_planner()
    await _callback.wait_call()

    response = await performer_for_order(
        taxi_order_id=taxi_order_id,
        version=5,
        callback=_get_callback(mockserver, taxi_order_id, version=5),
    )
    assert response == {'message': 'not_found'}

    assert _lookup_event.has_calls
