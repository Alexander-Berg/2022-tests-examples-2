import pytest


async def test_simple_scenario(
        taxi_qc_executors, testpoint, mockserver, load_json,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': load_json('passes.json'), 'cursor': 'next'},
            status=200,
        )

    @mockserver.json_handler('/plotva-ml/quality_control/router/v1')
    def _plotva_ml_thermobag_v1(request):
        assert request.method == 'POST'
        return mockserver.make_response(json=load_json('ml_response.json'))

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        assert request.json == load_json('push_request.json')
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('send-to-ml'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    def _get_requests(mocked_func):
        return [
            mocked_func.next_call()['request'].json
            for _ in range(mocked_func.times_called)
        ]

    assert _plotva_ml_thermobag_v1.times_called == 2
    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1


@pytest.mark.config(
    QC_EXECUTORS_SEND_RQC_TO_ML_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
        'concurrent_ml_requests_count': 10,
    },
    QC_EXECUTORS_ML_THRESHOLDS={
        'thermobag_ml': {
            'path': 'thermobag_check',
            'projection': [],
            'thermobag_presented_confidence': {
                'correct_gt': 0.9,
                'incorrect_lte': 0.5,
                'model': 'thermobag_presented',
            },
            'recognized_string': {
                'correct_gt': 0.9,
                'incorrect_lte': 0.5,
                'model': 'string',
            },
            'thermobag_not_presented_confidence': {
                'correct_gt': 0.9,
                'incorrect_lte': 0.5,
            },
        },
    },
)
async def test_bounds_scenario(
        taxi_qc_executors, testpoint, mockserver, load_json,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': load_json('passes.json'), 'cursor': 'next'},
            status=200,
        )

    @mockserver.json_handler('/plotva-ml/quality_control/router/v1')
    def _plotva_ml_thermobag_v1(request):
        assert request.method == 'POST'
        return mockserver.make_response(json=load_json('ml_response.json'))

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        assert request.json == load_json('push_request_models.json')
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('send-to-ml'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    def _get_requests(mocked_func):
        return [
            mocked_func.next_call()['request'].json
            for _ in range(mocked_func.times_called)
        ]

    assert _plotva_ml_thermobag_v1.times_called == 2
    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
