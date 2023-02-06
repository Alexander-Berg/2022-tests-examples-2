import pytest

from tests_qc_executors import utils


@pytest.mark.config(
    QC_EXECUTORS_SEND_BIOMETRY_TO_ML_SETTINGS={
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
                    'biometry',
                    status='new',
                    media=[
                        {
                            'code': 'biometry_etalons.selfie.something',
                            'url': 'some_url',
                            'bucket': 'some_bucket',
                            'id': 'some_id',
                        },
                        {
                            'code': (
                                'biometry_etalons.something_else.something'
                            ),
                            'url': 'some_another_url',
                            'bucket': 'some_another_bucket',
                            'id': 'some_another_id',
                        },
                        {
                            'code': 'selfie',
                            'url': 'some_other_url',
                            'bucket': 'some_other_bucket',
                            'id': 'some_other_id',
                        },
                        {
                            'code': 'something_else',
                            'url': 'some_another_url',
                            'bucket': 'some_another_bucket',
                            'id': 'some_another_id',
                        },
                    ],
                ),
            ],
            [
                {
                    'reference_media': [
                        {
                            'code': 'selfie',
                            'items': [
                                {
                                    'id': 'some_bucket_some_id',
                                    'referenced_at': (
                                        '1970-01-01T00:00:00+00:00'
                                    ),
                                    'url': 'some_url',
                                },
                            ],
                            'type': 'image',
                        },
                    ],
                    'target_media': [
                        {
                            'code': 'selfie',
                            'items': [
                                {
                                    'id': 'some_other_bucket_some_other_id',
                                    'url': 'some_other_url',
                                },
                            ],
                            'type': 'image',
                        },
                    ],
                },
            ],
            [
                {
                    'items': [
                        {
                            'data': [
                                {'field': 'resolution', 'value': 'success'},
                                {
                                    'field': 'good_biometry_etalons_ids',
                                    'value': ['some_etalon_id'],
                                },
                            ],
                            'entity_id': 'entity_id1',
                            'entity_type': 'driver',
                            'exam': 'biometry',
                            'id': 'id1',
                        },
                    ],
                },
            ],
        ),
        (
            [
                utils.make_pass(
                    'id1',
                    'biometry',
                    status='new',
                    media=[
                        {
                            'code': (
                                'biometry_etalons.something_else.something'
                            ),
                            'url': 'some_url',
                            'bucket': 'some_bucket',
                            'id': 'some_id',
                        },
                        {
                            'code': (
                                'biometry_etalons.something_else.something'
                            ),
                            'url': 'some_another_url',
                            'bucket': 'some_another_bucket',
                            'id': 'some_another_id',
                        },
                        {
                            'code': 'selfie',
                            'url': 'some_other_url',
                            'bucket': 'some_other_bucket',
                            'id': 'some_other_id',
                        },
                        {
                            'code': 'something_else',
                            'url': 'some_another_url',
                            'bucket': 'some_another_bucket',
                            'id': 'some_another_id',
                        },
                    ],
                ),
            ],
            [],
            [
                {
                    'items': [
                        {
                            'data': [
                                {'field': 'resolution', 'value': 'NO_DATA'},
                            ],
                            'entity_id': 'entity_id1',
                            'entity_type': 'driver',
                            'exam': 'biometry',
                            'id': 'id1',
                        },
                    ],
                },
            ],
        ),
        (
            [
                utils.make_pass('id1', 'biometry', status='new', media=[]),
                utils.make_pass(
                    'id2',
                    'biometry',
                    status='new',
                    media=[
                        {
                            'code': 'biometry_etalons.selfie.1',
                            'url': 'some_url',
                            'bucket': 'some_bucket',
                            'id': 'some_id',
                        },
                        {
                            'code': 'selfie',
                            'url': 'some_other_url',
                            'bucket': 'some_other_bucket',
                            'id': 'some_other_id',
                        },
                    ],
                ),
            ],
            [
                {
                    'reference_media': [
                        {
                            'code': 'selfie',
                            'items': [
                                {
                                    'id': 'some_bucket_some_id',
                                    'referenced_at': (
                                        '1970-01-01T00:00:00+00:00'
                                    ),
                                    'url': 'some_url',
                                },
                            ],
                            'type': 'image',
                        },
                    ],
                    'target_media': [
                        {
                            'code': 'selfie',
                            'items': [
                                {
                                    'id': 'some_other_bucket_some_other_id',
                                    'url': 'some_other_url',
                                },
                            ],
                            'type': 'image',
                        },
                    ],
                },
            ],
            [
                {
                    'items': [
                        {
                            'data': [
                                {'field': 'resolution', 'value': 'NO_DATA'},
                            ],
                            'entity_id': 'entity_id1',
                            'entity_type': 'driver',
                            'exam': 'biometry',
                            'id': 'id1',
                        },
                        {
                            'data': [
                                {'field': 'resolution', 'value': 'success'},
                                {
                                    'field': 'good_biometry_etalons_ids',
                                    'value': ['some_etalon_id'],
                                },
                            ],
                            'entity_id': 'entity_id2',
                            'entity_type': 'driver',
                            'exam': 'biometry',
                            'id': 'id2',
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

    @mockserver.json_handler('/plotva-ml/biometrics/verify/v1')
    def _plotva_ml_biometrics_verify_v1(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={
                'resolution': {'status': 'success'},
                'reference_media': [
                    {
                        'code': 'selfie',
                        'type': 'image',
                        'items': [{'id': 'some_etalon_id'}],
                    },
                ],
            },
            status=200,
        )

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('send-biometry-to-ml'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    def _get_requests(mocked_func):
        return [
            mocked_func.next_call()['request'].json
            for _ in range(mocked_func.times_called)
        ]

    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
    assert (
        _get_requests(_plotva_ml_biometrics_verify_v1)
        == expected_verify_requests_
    )
    assert (
        _get_requests(_internal_qc_pools_v1_pool_push)
        == expected_push_requests_
    )
