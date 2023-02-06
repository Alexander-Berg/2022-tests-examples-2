import pytest


@pytest.mark.parametrize('claim_id', ['claim_seg5', None])
async def test_batch_happy_path(
        run_task_once, mockserver, load_json, claim_id,
):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    def _dispatch_journal(request):
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'},
            json=load_json('dispatch_journal_batch.json'),
        )

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    def _dispatch_journal_info(request):
        ret = load_json('segment_{}.json'.format(request.query['segment_id']))
        ret['segment']['custom_context']['delivery_flags'] = {
            'forced_claim_id': claim_id,
        }
        return mockserver.make_response(json=ret)

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _waybill_info(request):
        resp = load_json('waybill_info_response.json')
        for point in resp['execution']['points']:
            point['is_resolved'] = False
        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('claim_full_response.json')

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/update-proposition')
    def _dispatch_wayill_propose(request):
        assert request.json['proposition']['taxi_lookup_extra'] == {
            'claim_id': 'claim_seg5',
            'intent': 'grocery-manual',
        }
        assert (
            'lookup_extra'
            not in request.json['proposition']['taxi_order_requirements']
        )
        return mockserver.make_response(json={})

    result = await run_task_once('segments-processor')
    assert result['stats'] == {
        'new-segment-events-count': 1,
        'waybills-proposed-count': 1 if claim_id is not None else 0,
    }


async def test_batch_point_order(run_task_once, mockserver, load_json):
    claim_id = 'claim_seg5'

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    def _dispatch_journal(request):
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'},
            json=load_json('dispatch_journal_batch.json'),
        )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _waybill_info(request):
        resp = load_json('waybill_info_response.json')
        for point in resp['execution']['points']:
            point['is_resolved'] = False
        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    def _dispatch_journal_info(request):
        ret = load_json('segment_{}.json'.format(request.query['segment_id']))
        ret['segment']['custom_context']['delivery_flags'] = {
            'forced_claim_id': claim_id,
        }
        return mockserver.make_response(json=ret)

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('claim_full_response.json')

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/update-proposition')
    def _dispatch_wayill_propose(request):
        assert request.json['proposition']['points'] == [
            {'point_id': 'seg5_A1_p1', 'segment_id': 'seg5', 'visit_order': 1},
            {'point_id': 'seg4_A1_p1', 'segment_id': 'seg4', 'visit_order': 2},
            {'point_id': 'seg4_B1_p2', 'segment_id': 'seg4', 'visit_order': 3},
            {'point_id': 'seg5_B1_p2', 'segment_id': 'seg5', 'visit_order': 4},
            {'point_id': 'seg5_A1_p3', 'segment_id': 'seg5', 'visit_order': 5},
            {'point_id': 'seg4_A1_p3', 'segment_id': 'seg4', 'visit_order': 6},
        ]
        return mockserver.make_response(json={})

    result = await run_task_once('segments-processor')
    assert result['stats'] == {
        'new-segment-events-count': 1,
        'waybills-proposed-count': 1,
    }


async def test_big_batch_point_order(run_task_once, mockserver, load_json):
    claim_id = 'claim_seg5'

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    def _dispatch_journal(request):
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'},
            json=load_json('dispatch_journal_batch.json'),
        )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _waybill_info(request):
        resp = load_json('waybill_info_response_batch.json')
        for point in resp['execution']['points']:
            point['is_resolved'] = False
        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    def _dispatch_journal_info(request):
        ret = load_json('segment_{}.json'.format(request.query['segment_id']))
        ret['segment']['custom_context']['delivery_flags'] = {
            'forced_claim_id': claim_id,
        }
        return mockserver.make_response(json=ret)

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('claim_full_response.json')

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/update-proposition')
    def _dispatch_wayill_propose(request):
        assert request.json['proposition']['points'] == [
            {'point_id': 'seg1_A1_p1', 'segment_id': 'seg1', 'visit_order': 1},
            {'point_id': 'seg5_A1_p1', 'segment_id': 'seg5', 'visit_order': 2},
            {'point_id': 'seg4_A1_p1', 'segment_id': 'seg4', 'visit_order': 3},
            {'point_id': 'seg4_B1_p2', 'segment_id': 'seg4', 'visit_order': 4},
            {'point_id': 'seg1_A2_p2', 'segment_id': 'seg1', 'visit_order': 5},
            {'point_id': 'seg5_B1_p2', 'segment_id': 'seg5', 'visit_order': 6},
            {'point_id': 'seg1_B1_p3', 'segment_id': 'seg1', 'visit_order': 7},
            {'point_id': 'seg5_A1_p3', 'segment_id': 'seg5', 'visit_order': 8},
            {'point_id': 'seg4_A1_p3', 'segment_id': 'seg4', 'visit_order': 9},
        ]
        return mockserver.make_response(json={})

    result = await run_task_once('segments-processor')
    assert result['stats'] == {
        'new-segment-events-count': 1,
        'waybills-proposed-count': 1,
    }
