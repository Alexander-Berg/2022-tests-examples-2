import datetime
import json

import pytest

from testsuite.utils import matching


@pytest.fixture(name='get_candidate')
def _get_candidate(get_segment, get_waybill):
    def _wrapper(segment):
        segment_info = get_segment(segment.id)
        waybill = get_waybill(segment_info['waybill_ref'])
        if not waybill:
            return None

        candidate_doc = waybill['candidate']
        assigned_at = candidate_doc['assigned_at'] if candidate_doc else None

        assert bool(candidate_doc) == bool(assigned_at)

        return candidate_doc['info']['id'] if candidate_doc else None

    return _wrapper


def _remove_extra_keys(actual, expected):
    """
    Removes extra keys in 'actual' response object, that are missing
    in 'expected', including nested keys.

    :param actual: Actual candidates response
    :param expected: Expected candidates response

    :returns: actual response without extra keys
    """
    type_actual = type(actual)
    type_expected = type(expected)

    if type_actual is list and type_expected is list:
        for actual_item, expected_item in zip(actual, expected):
            _remove_extra_keys(actual_item, expected_item)

    if type_actual is not dict or type_expected is not dict:
        return actual

    for key in list(actual):
        if key == 'driver_ids':
            actual[key].sort()
        if key not in expected:
            del actual[key]
        else:
            _remove_extra_keys(actual[key], expected[key])

    return actual


def _compare_requests(actual, expected):
    actual = _remove_extra_keys(actual, expected)
    assert actual == expected


def _make_performer_request(*, taxi_order_id, generation=1, version=1, wave=1):
    return {
        'order_id': taxi_order_id,
        'allowed_classes': ['cargo'],
        'lookup': {'generation': generation, 'version': version, 'wave': wave},
        'order': {'created': 1584378627.69, 'nearest_zone': 'moscow'},
    }


# Test basic scenario where for each segment a list of candidates should be
# found and best one proposed.
# Performs GetCandidates() call with two segments, a call should perform
# two requests to /order-search to find candidates and one bulk request to
# /v2/score-candidates-bulk to score them
async def test_greedy_assignment(
        create_candidates_segment,
        state_segments_replicated,
        run_single_planner,
        get_candidate,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request, body_json):
        _compare_requests(body_json, load_json('order_search_request.json'))
        return load_json('order_search_response.json')

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request, body_json):
        _compare_requests(body_json, load_json('scoring_request.json'))
        return load_json('scoring_response.json')

    segment1 = create_candidates_segment('greedy')
    segment2 = create_candidates_segment('greedy')

    await state_segments_replicated()
    await run_single_planner()

    assert _order_search.times_called == 2
    assert _scoring.times_called == 1

    assert {get_candidate(segment1), get_candidate(segment2)} == {
        'dbid1_uuid1',
        'dbid1_uuid2',
    }


# Test basic scenario where for each segment a list of candidates should be
# found and best one proposed, but with error from scoring and thus
# fallback scoring performed.
# Performs GetCandidates() call with one segment, a call should perform
# one request to /order-search to find candidates and one bulk request to
# /v2/score-candidates-bulk to score them. Call should fail and fallback should
# sort candidates by best time in route info.
async def test_scoring_fallback(
        create_candidates_segment,
        state_segments_replicated,
        run_single_planner,
        get_candidate,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return load_json('order_search_response.json')

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        return mockserver.make_response(
            status=429, json={'status': 'error', 'code': 'too many requests'},
        )

    segment1 = create_candidates_segment('greedy')

    await state_segments_replicated()
    await run_single_planner()

    assert _order_search.times_called == 1
    assert _scoring.times_called == 1

    assert get_candidate(segment1) == 'dbid1_uuid2'


# Test basic scenario where for each segment a list of candidates should be
# found and best one proposed, but with error from /order-search for one of
# the segments.
# Performs GetCandidates() call with two segments, a call should perform
# two requests to /order-search to find candidates and one bulk request to
# /v2/score-candidates-bulk to score them. One of the searches should fail but
# it should not affect second one
async def test_order_search_error(
        create_candidates_segment,
        state_segments_replicated,
        run_single_planner,
        get_candidate,
        load_json,
        mockserver,
):
    order_search_responses = [load_json('order_search_response.json')]

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        if not order_search_responses:
            return mockserver.make_response(
                status=429,
                json={'status': 'error', 'code': 'too many requests'},
            )
        return order_search_responses.pop(0)

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request, body_json):
        _compare_requests(body_json, load_json('scoring_request.json'))
        return load_json('scoring_response.json')

    segment1 = create_candidates_segment('greedy')
    segment2 = create_candidates_segment('greedy')

    await state_segments_replicated()
    await run_single_planner()

    assert _order_search.times_called == 2
    assert _scoring.times_called == 1

    assert {get_candidate(segment1), get_candidate(segment2)} == {
        'dbid1_uuid2',
        None,
    }


# Test batching scenario where for each segment a list of candidates should be
# found then some of them combined into a batch, scored again with new
# parameters and best proposed.
# Performs GetCandidates() call with two segments, a call should perform
# two requests to /order-search to find candidates and one bulk request to
# /v2/score-candidates-bulk to score them. Then performs ScoreCandidates() call
# for two batches, a call should perform two requests to /order-satisfy to
# satisfy candidates for a batch and one request to /v2/score-candidates-bulk
# to score them.
async def test_batch_assignment(
        create_candidates_segment,
        state_segments_replicated,
        run_single_planner,
        get_candidate,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return load_json('order_search_response.json')

    scoring_request = load_json('scoring_request.json')
    scoring_response = load_json('scoring_response2.json')

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request, body_json):
        _compare_requests(body_json, scoring_request)
        return scoring_response

    segment1 = create_candidates_segment('batch')
    segment2 = create_candidates_segment('batch')

    satisfy_responses = {
        'ud/' + segment1.id: load_json('order_satisfy_response1.json'),
        'ud/' + segment2.id: load_json('order_satisfy_response2.json'),
    }

    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request, body_json):
        response = satisfy_responses[body_json['order_id']]
        _compare_requests(body_json, load_json('order_satisfy_request.json'))
        return response

    await state_segments_replicated()
    await run_single_planner()

    assert _order_search.times_called == 2
    assert _scoring.times_called == 1
    assert _order_satisfy.times_called == 2

    assert {get_candidate(segment1), get_candidate(segment2)} == {
        'dbid1_uuid1',
        'dbid1_uuid2',
    }


# Test live batching scenario where for each segment a list of on order
# candidates should be found then best proposed.
# For initialization performs basic greedy scenario for two segments to have
# two waybills with candidates in waybill geoindex for final scenario.
# Performs GetCandidatesOnOrder() call with one segment, a call should perform
# one search in waybill geoindex which should find two candidates from init
# step, then a call to /order-satisfy to check found candidates for order,
# then a call to scoring to score satisfied candidates.
async def test_live_batch_assignment(
        create_candidates_segment,
        state_waybill_created,
        state_taxi_order_performer_found,
        run_single_planner,
        get_candidate,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return load_json('order_search_response.json')

    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request, body_json):
        _compare_requests(body_json, load_json('order_satisfy_request.json'))
        return load_json('order_satisfy_response.json')

    expected_scoring_request = None
    scoring_response = load_json('scoring_response1.json')

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request, body_json):
        if expected_scoring_request:
            _compare_requests(body_json, expected_scoring_request)
        return scoring_response

    @mockserver.json_handler('/driver-trackstory/positions')
    def _positions(request, body_json):
        _compare_requests(body_json, load_json('positions_request.json'))
        return load_json('positions_response.json')

    # propose two segments with two different candidates

    segment1 = create_candidates_segment('greedy')
    segment2 = create_candidates_segment('greedy')
    await state_taxi_order_performer_found()

    assert {get_candidate(segment1), get_candidate(segment2)} == {
        'dbid1_uuid1',
        'dbid1_uuid2',
    }

    # candidates positions are added to waybill geoindex
    #   pickup and dropoff points for segment1 and segment2
    #   dbid1_uuid2's position
    #   total: 5
    stats = await run_single_planner()
    assert _positions.times_called == 1
    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'waybill-geoindex-size'},
        ).value
        == 5
    )

    # Now try to assign one of busy candidates to segment3
    expected_scoring_request = load_json('scoring_request.json')
    scoring_response = load_json('scoring_response2.json')

    segment3 = create_candidates_segment('live_batch')

    await state_waybill_created()

    assert get_candidate(segment3) == 'dbid1_uuid2'


async def test_cargo_ref_ids_passed(
        create_candidates_segment,
        state_segments_replicated,
        run_single_planner,
        mockserver,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(*, body_json):
        assert body_json['order']['cargo_ref_ids'] == [segment.id]
        return {'candidates': []}

    segment = create_candidates_segment('greedy')

    await state_segments_replicated()
    await run_single_planner()

    assert _order_search.times_called > 0


async def test_frozen_candidates(
        create_candidates_segment,
        run_single_planner,
        exp_frozen_candidates_settings,
        get_frozen_candidates,
        state_taxi_order_created,
        state_taxi_order_performer_found,
        mockserver,
        load_json,
        mocked_time,
):
    await exp_frozen_candidates_settings()

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return load_json('order_search_response.json')

    now = datetime.datetime(2022, 5, 1)
    mocked_time.set(now)

    create_candidates_segment('greedy')
    await state_taxi_order_created()
    await run_single_planner()

    assert get_frozen_candidates() == [
        {
            'candidate_id': 'dbid1_uuid1',
            'waybill_id': matching.any_string,
            'expiration_ts': now.replace(
                tzinfo=datetime.timezone.utc,
            ) + datetime.timedelta(seconds=10),
        },
    ]

    await state_taxi_order_performer_found()
    assert not get_frozen_candidates()


async def test_defreeze_candidate(
        create_candidates_segment,
        run_single_planner,
        exp_frozen_candidates_settings,
        get_frozen_candidates,
        state_taxi_order_created,
        mockserver,
        load_json,
        performer_for_order,
):
    await exp_frozen_candidates_settings()

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return load_json('order_search_response.json')

    create_candidates_segment('greedy')
    await state_taxi_order_created()
    await run_single_planner()

    assert get_frozen_candidates()

    await performer_for_order(version=1)
    await performer_for_order(version=2)
    assert not get_frozen_candidates()


@pytest.mark.config(
    UNITED_DISPATCH_REJECTED_CANDIDATES_SETTINGS={'enabled': True},
)
async def test_repeat_waybill_search(
        create_candidates_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        set_waybill_lookup_flow,
        get_single_waybill,
        run_single_planner,
        mockserver,
        load_json,
        exp_performer_repeat_search,
        exp_rejected_candidates_load_settings,
        state_segments_replicated,
):

    await exp_performer_repeat_search()
    await exp_rejected_candidates_load_settings()

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request, body_json):
        return load_json('order_search_response.json')

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

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
        ),
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == 'dbid1_uuid2'

    @mockserver.json_handler('/candidates/order-search')
    def _order_search_(request, body_json):
        _compare_requests(body_json, load_json('order_search_request.json'))
        return load_json('order_search_response.json')

    # Increase lookup version, this should trigger waybill update and mark
    # waybill for new search

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], version=2,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'updated'}

    # Start planner which should find new candidate for waybill

    _order_search_.flush()

    await run_single_planner()

    assert _order_search_.times_called == 1

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], version=2,
        ),
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == 'dbid1_uuid1'


async def test_all_candidates_rejected(
        state_waybill_proposed,
        taxi_united_dispatch,
        taxi_united_dispatch_monitor,
        add_rejected_candidate,
        create_candidates_segment,
        propositions_manager,
        exp_rejected_candidates_load_settings,
        mockserver,
        load_json,
):
    """
        Check all rejected candidates filtered from
        GetCandidates result.
    """
    await exp_rejected_candidates_load_settings()
    await taxi_united_dispatch.tests_control(reset_metrics=True)
    seg = create_candidates_segment('greedy')

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        body = json.loads(request.get_data())
        assert len(body['excluded_contractor_ids']) == 2
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    add_rejected_candidate(segment=seg, candidate_id='dbid1_uuid1')
    add_rejected_candidate(segment=seg, candidate_id='dbid1_uuid2')

    await state_waybill_proposed()

    assert not propositions_manager.propositions


async def test_rejected_candidate(
        state_waybill_proposed,
        taxi_united_dispatch,
        taxi_united_dispatch_monitor,
        add_rejected_candidate,
        create_candidates_segment,
        propositions_manager,
        exp_rejected_candidates_load_settings,
        mockserver,
        load_json,
):
    """
        Check one rejected candidate filtered from GetCandidates result,
        second candidate returned.
    """
    await exp_rejected_candidates_load_settings()
    await taxi_united_dispatch.tests_control(reset_metrics=True)
    seg = create_candidates_segment('greedy')

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        body = json.loads(request.get_data())
        assert len(body['excluded_contractor_ids']) == 1
        response = load_json('order_search_response.json')
        del response['candidates'][0]
        return response

    add_rejected_candidate(segment=seg, candidate_id='dbid1_uuid1')

    await state_waybill_proposed()

    assert propositions_manager.propositions
