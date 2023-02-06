import pytest


@pytest.mark.parametrize('performer_id', [None, 'dbid_uuid'])
async def test_happy_path(run_task_once, mockserver, load_json, performer_id):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    def _dispatch_journal(request):
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'},
            json=load_json('dispatch_journal.json'),
        )

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    def _dispatch_journal_info(request):
        ret = load_json('segment_{}.json'.format(request.query['segment_id']))
        ret['segment']['custom_context']['delivery_flags'] = {
            'forced_performer': performer_id,
        }
        return mockserver.make_response(json=ret)

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _dispatch_wayill_propose(request):
        return mockserver.make_response(json={})

    result = await run_task_once('segments-processor')
    assert result['stats'] == {
        'new-segment-events-count': 6,
        'waybills-proposed-count': 3 if performer_id is not None else 0,
    }
