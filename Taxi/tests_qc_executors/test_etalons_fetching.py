import pytest

from tests_qc_executors import utils

BIOMETRY_ETALONS = {
    'entity_id1': {
        'profiles': [
            {
                'version': 1,
                'profile_media': {
                    'photo': [
                        {
                            'media_id': 'media_id_1',
                            'storage_bucket': 'bucket_id1',
                            'storage_id': 'storage_id1',
                            'storage_type': 'media-storage',
                            'temporary_url': 'http://url1.com',
                            'face_features': {'cbir': [0.1, 0.2, 0.3, 0.4]},
                            'meta': {'from': 'dkvu', 'created': '2022-14-02'},
                        },
                        {
                            'media_id': 'media_id_2',
                            'storage_bucket': 'driver_photo',
                            'storage_id': 'storage_id_2',
                            'storage_type': 'media-storage',
                            'face_features': {'cbir': [0.1, 0.2, 0.3, 0.4]},
                        },
                        {
                            'media_id': 'media_id_3',
                            'storage_bucket': 'driver_photo',
                            'storage_id': 'storage_id_3',
                            'storage_type': 'media-storage',
                            'temporary_url': 'http://url3.com',
                        },
                    ],
                },
                'profile': {'id': 'yyy_yyy', 'type': 'park_driver_profile_id'},
                'provider': 'signalq',
            },
        ],
    },
    'entity_id2': {
        'profiles': [
            {
                'version': 2,
                'profile_media': {
                    'photo': [
                        {
                            'media_id': 'media_id_1',
                            'storage_bucket': 'bucket_id1',
                            'storage_id': 'storage_id1',
                            'storage_type': 'media-storage',
                            'temporary_url': 'http://url11.com',
                            'face_features': {'cbir': [0.1, 0.2, 0.3, 0.4]},
                        },
                        {
                            'media_id': 'media_id_2',
                            'storage_bucket': 'bucket_id2',
                            'storage_id': 'storage_id2',
                            'storage_type': 'media-storage',
                            'temporary_url': 'http://url2.com',
                            'face_features': {'cbir': [0.5, 0.6, 0.7, 0.8]},
                        },
                    ],
                },
                'profile': {'id': 'yyy_yyy', 'type': 'park_driver_profile_id'},
                'provider': 'signalq',
            },
        ],
    },
    'entity_id3': {
        'profiles': [
            {
                'profile_media': {'photo': []},
                'profile': {'id': 'yyy_yyy', 'type': 'park_driver_profile_id'},
                'provider': 'signalq',
            },
        ],
    },
}

RIGHT_MEDIA = {
    'id1': {
        'version': '1',
        'resolution': 'PART_DATA',
        'media': [
            {
                'code': 'selfie.0',
                'url': 'http://url1.com',
                'id': 'storage_id1',
                'bucket': 'bucket_id1',
            },
            {
                'code': 'selfie.2',
                'url': 'http://url3.com',
                'id': 'storage_id_3',
                'bucket': 'driver_photo',
            },
        ],
        'face_features': {
            'selfie.0.cbir_face_features': [
                '0.100000',
                '0.200000',
                '0.300000',
                '0.400000',
            ],
        },
        'meta': {
            'selfie.0.meta.from': 'dkvu',
            'selfie.0.meta.created': '2022-14-02',
        },
    },
    'id2': {
        'version': '2',
        'resolution': 'SUCCESS',
        'media': [
            {
                'code': 'selfie.0',
                'url': 'http://url11.com',
                'id': 'storage_id1',
                'bucket': 'bucket_id1',
            },
            {
                'code': 'selfie.1',
                'url': 'http://url2.com',
                'id': 'storage_id2',
                'bucket': 'bucket_id2',
            },
        ],
        'face_features': {
            'selfie.0.cbir_face_features': [
                '0.100000',
                '0.200000',
                '0.300000',
                '0.400000',
            ],
            'selfie.1.cbir_face_features': [
                '0.500000',
                '0.600000',
                '0.700000',
                '0.800000',
            ],
        },
    },
    'id3': {'resolution': 'NO_DATA'},
}


@pytest.mark.config(
    QC_EXECUTORS_FETCH_BIOMETRY_ETALONS_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
        'concurrent_biometry_etalons_requests_count': 10,
    },
)
@pytest.mark.parametrize(
    'passes_,exams_without_etalons_',
    [
        (
            [
                utils.make_pass('id1', 'dkvu', status='new'),
                utils.make_pass('id2', 'dkk', status='new'),
                utils.make_pass('id3', 'sts', entity_type='car'),
            ],
            ['entity_id3'],
        ),
    ],
)
async def test_simple_scenario_etalons_fetcher(
        taxi_qc_executors,
        testpoint,
        mockserver,
        passes_,
        exams_without_etalons_,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': passes_, 'cursor': 'next'}, status=200,
        )

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profiles/retrieve',
    )
    def _biometry_etalons_services_v1_retrive(request):
        assert request.method == 'POST'
        assert request.json['profile_ids'][0] not in exams_without_etalons_
        return mockserver.make_response(
            json=BIOMETRY_ETALONS[request.json['profile_ids'][0]], status=200,
        )

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        for val in request.json['items']:
            if val['entity_id'] not in exams_without_etalons_:
                assert val['data']
            if val['entity_id'] in exams_without_etalons_:
                assert (
                    len(val['data']) == 1
                    and val['data'][0]['field'] == 'resolution'
                    and val['data'][0]['value'] == 'NO_DATA'
                )
                continue

            if val['entity_id'] in exams_without_etalons_:
                assert 'media' not in val
            else:
                assert sorted(val['media'], key=lambda x: x['code']) == sorted(
                    RIGHT_MEDIA[val['id']]['media'], key=lambda x: x['code'],
                )
            num_matched = 0
            for dat in val['data']:
                if dat['field'] == 'version':
                    num_matched += 1
                    assert dat['value'] == RIGHT_MEDIA[val['id']]['version']
                if dat['field'] == 'resolution':
                    num_matched += 1
                    assert dat['value'] == RIGHT_MEDIA[val['id']]['resolution']
                if 'cbir_face_features' in dat['field']:
                    num_matched += 1
                    assert (
                        dat['value']
                        == RIGHT_MEDIA[val['id']]['face_features'][
                            dat['field']
                        ]
                    )
                if 'meta' in dat['field']:
                    num_matched += 1
                    assert (
                        dat['value']
                        == RIGHT_MEDIA[val['id']]['meta'][dat['field']]
                    )
            assert num_matched == len(val['data'])

        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('fetch-biometry-etalons'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
    assert _biometry_etalons_services_v1_retrive.times_called == 2
    assert _internal_qc_pools_v1_pool_push.times_called == 1


@pytest.mark.config(
    QC_EXECUTORS_FETCH_BIOMETRY_ETALONS_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
        'concurrent_biometry_etalons_requests_count': 10,
    },
)
@pytest.mark.parametrize(
    'passes_',
    [
        (
            [
                utils.make_pass('id1', 'dkvu', status='new'),
                utils.make_pass('id2', 'dkk', status='new'),
                utils.make_pass('id3', 'sts', entity_type='car'),
            ]
        ),
    ],
)
async def test_error_scenario_etalons_fetcher(
        taxi_qc_executors, testpoint, mockserver, passes_,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': passes_, 'cursor': 'next'}, status=200,
        )

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profiles/retrieve',
    )
    def _biometry_etalons_services_v1_retrive(request):
        assert request.method == 'POST'
        if request.json['profile_ids'] == ['entity_id2']:
            return mockserver.make_response(status=500, json={})

        return mockserver.make_response(
            json=BIOMETRY_ETALONS[request.json['profile_ids'][0]], status=200,
        )

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        assert len(request.json['items']) == 2
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('fetch-biometry-etalons'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
    assert _biometry_etalons_services_v1_retrive.times_called == 4
    assert _internal_qc_pools_v1_pool_push.times_called == 1
