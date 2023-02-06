import pytest


@pytest.fixture(name='cargo_dispatch')
def mock_cargo_dispatch(mockserver):
    @mockserver.json_handler('/cargo-dispatch/v1/admin/segment/autoreorder')
    def _mock_segment_autoreorder(request):
        claim_id = request.query['claim_id']
        performer_info = request.json['performer_info']
        claim_info = context.claim_infos[claim_id]
        status_code = context.autoreorder_status.get(claim_id, 200)
        disable_batching = context.disable_batching[claim_id]
        if disable_batching:
            assert disable_batching == request.json['disable_batching']
        else:
            assert 'disable_batching' not in request.json

        if status_code != 200:
            return mockserver.make_response(
                status=status_code,
                json={'code': 'some code', 'message': 'some_message'},
            )

        if (
                performer_info is None
                or performer_info['driver_id'] != claim_info['driver_id']
                or performer_info['park_id'] != claim_info['park_id']
        ):
            # Driver already changed.
            return mockserver.make_response(
                status=409,
                json={'code': 'some code', 'message': 'some_message'},
            )

        return mockserver.make_response(json={'result': 'ok'})

    class Context:
        def __init__(self):
            self.claim_infos = {}
            self.autoreorder_status = {}
            self.disable_batching = {}

        def add_claim(
                self,
                *,
                claim_id,
                driver_id,
                park_id,
                autoreorder_status=200,
                disable_batching=None,
        ):
            claim_info = {'driver_id': driver_id, 'park_id': park_id}

            self.claim_infos[claim_id] = claim_info
            self.autoreorder_status[claim_id] = autoreorder_status
            self.disable_batching[claim_id] = disable_batching

    context = Context()
    return context
