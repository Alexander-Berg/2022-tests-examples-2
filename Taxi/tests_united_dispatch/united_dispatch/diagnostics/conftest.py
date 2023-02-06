import pytest

from tests_united_dispatch.plugins import cargo_dispatch_manager

PERFORMER = 'dbid_uuid'


@pytest.fixture(name='segment_diagnostics')
async def _segment_diagnostics(taxi_united_dispatch):
    async def wrapper(*, segment_id, expected_status=200):
        response = await taxi_united_dispatch.post(
            '/admin/v1/diagnostics/segment',
            json={'segment_id': segment_id, 'performer_id': PERFORMER},
        )
        assert response.status_code == expected_status
        return response.json()

    return wrapper


@pytest.fixture(name='planner_diagnostics')
async def _planner_diagnostics(
        taxi_united_dispatch,
        segment_builder,
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
):
    async def wrapper(
            *,
            segment_id,
            planner_type,
            planner_shard='default',
            performer_id=None,
            expected_status=200,
    ):
        response = await taxi_united_dispatch.post(
            '/diagnostics/planner',
            json={
                'segment_doc': segment_builder(
                    cargo_dispatch.get_segment(segment_id),
                ),
                'performer_id': performer_id,
                'planner_type': planner_type,
                'planner_shard': planner_shard,
            },
        )
        assert response.status_code == expected_status
        return response.json()

    return wrapper


@pytest.fixture(name='mock_dispatch_admin_segment_info')
def _mock_dispatch_admin_segment_info(
        mockserver,
        segment_builder,
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
):
    @mockserver.json_handler('/cargo-dispatch/v1/admin/segment/info')
    def mock_segment_info(request):
        segment_id = request.args['segment_id']
        segment = cargo_dispatch.get_segment(segment_id)
        if segment is None:
            return mockserver.make_response(
                status=404,
                json={'code': 'not found', 'message': 'segment not found'},
            )
        return segment_builder(segment)

    return mock_segment_info


@pytest.fixture(name='mock_units_diagnostics_responses')
def _mock_units_diagnostics_responses(mockserver):
    @mockserver.json_handler('/united-dispatch/diagnostics/planner')
    def _mock_ud(request):
        assert request.json['planner_type'] == 'crutches'

        return {
            'planner': {
                'planner_id': 'crutches',
                'recorded_requests': [],
                'result': {'kind': 'add_proposition'},
            },
            'candidate': {
                'candidate_id': PERFORMER,
                'planner_satisfy': {
                    'planner_id': 'crutches',
                    'response': {'foo': 'bar'},
                },
            },
        }

    @mockserver.json_handler('/united-dispatch-testsuite/diagnostics/planner')
    def _mock_ud_candidates(request):
        assert request.json['planner_type'] == 'testsuite-candidates'
        return {
            'planner': {
                'planner_id': 'testsuite-candidates',
                'recorded_requests': [],
                'result': {'kind': 'add_proposition'},
            },
        }
