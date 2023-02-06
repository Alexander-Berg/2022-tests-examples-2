import pytest

from tests_qc_executors import utils
RECOGNITION_PATH = 'verify_response.prediction.branding_recognition'


@pytest.mark.config(
    QC_EXECUTORS_SEND_RQC_TO_ML_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
        'concurrent_ml_requests_count': 10,
    },
)
@pytest.mark.parametrize(
    'passes_,expected_verify_requests_,expected_push_requests_',
    [
        (
            [
                utils.make_pass(
                    'id1',
                    'rqc',
                    entity_type='car',
                    media=[
                        {
                            'code': 'front',
                            'url': 'front_url',
                            'bucket': 'some_bucket',
                            'id': 'front_id',
                        },
                        {
                            'code': 'back',
                            'url': 'back_url',
                            'bucket': 'some_bucket',
                            'id': 'back_id',
                        },
                        {
                            'code': 'trunk',
                            'url': 'trunk_url',
                            'bucket': 'some_bucket',
                            'id': 'trunk_id',
                        },
                        {
                            'code': 'other',
                            'url': 'other_url',
                            'bucket': 'some_bucket',
                            'id': 'other_id',
                        },
                    ],
                    data=[
                        {'field': 'city', 'value': 'Msk'},
                        {'field': 'country', 'value': 'Rus'},
                        {'field': 'year', 'value': 2016},
                        {'field': 'brand', 'value': 'Brand'},
                        {'field': 'number_normalized', 'value': 'K519YP777'},
                    ],
                ),
            ],
            [
                {
                    'exam_info': {
                        'use_ml': True,
                        'pass_id': 'id1',
                        'exam_country': 'Rus',
                        'exam_city': 'Msk',
                        'car_brand': 'Brand',
                        'car_year': '2016',
                        'car_license_plate_number': 'K519YP777',
                        'check_history': [],
                    },
                    'media': [
                        {'code': 'front', 'url': 'front_url'},
                        {'code': 'back', 'url': 'back_url'},
                        {'code': 'trunk', 'url': 'trunk_url'},
                    ],
                },
            ],
            [
                {
                    'items': [
                        {
                            'id': 'id1',
                            'entity_id': 'entity_id1',
                            'entity_type': 'car',
                            'exam': 'rqc',
                            'data': [
                                {'field': 'resolution', 'value': 'block'},
                                {'field': 'actual_result', 'value': 'block'},
                                {
                                    'field': 'correct',
                                    'value': ['NO_MODEL', 'NO_NUMBER_VIEW'],
                                },
                                {
                                    'field': 'incorrect',
                                    'value': ['NO_QUALITY', 'DUPLICATE'],
                                },
                                {
                                    'field': 'unknown',
                                    'value': ['NO_HARD_DEFECT', 'NO_COLOR'],
                                },
                                {
                                    'field': 'message_keys',
                                    'value': ['dkk_block_reason_fake_pass'],
                                },
                                {
                                    'field': RECOGNITION_PATH + '.score',
                                    'value': '0.039029',
                                },
                                {
                                    'field': RECOGNITION_PATH + '.brand',
                                    'value': 'N/A',
                                },
                                {
                                    'field': RECOGNITION_PATH + '.decision',
                                    'value': 'without_branding',
                                },
                            ],
                        },
                    ],
                },
            ],
        ),
    ],
)
async def test_simple_scenario(
        taxi_qc_executors,
        testpoint,
        mockserver,
        load_json,
        passes_,
        expected_verify_requests_,
        expected_push_requests_,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': passes_, 'cursor': 'next'}, status=200,
        )

    @mockserver.json_handler('/plotva-ml/remote_quality_control/v2')
    def _plotva_ml_remote_quality_control_v2(request):
        assert request.method == 'POST'
        return mockserver.make_response(json=load_json('rqc_response.json'))

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('send-rqc-to-ml'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    def _get_requests(mocked_func):
        return [
            mocked_func.next_call()['request'].json
            for _ in range(mocked_func.times_called)
        ]

    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
    assert (
        _get_requests(_plotva_ml_remote_quality_control_v2)
        == expected_verify_requests_
    )
    assert (
        _get_requests(_internal_qc_pools_v1_pool_push)
        == expected_push_requests_
    )
