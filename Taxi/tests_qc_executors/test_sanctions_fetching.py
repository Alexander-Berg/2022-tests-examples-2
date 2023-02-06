import pytest

from tests_qc_executors import utils


@pytest.mark.config(
    QC_EXECUTORS_FETCH_SANCTIONS_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
    },
)
@pytest.mark.parametrize(
    'passes_,ids_,exams_with_sanctions_',
    [
        (
            [
                utils.make_pass('id1', 'dkvu', status='new'),
                utils.make_pass('id2', 'dkk', status='pending'),
                utils.make_pass('id3', 'sts', entity_type='car'),
            ],
            ['entity_id1', 'entity_id2', 'entity_id3'],
            ['dkk', 'dkvu'],
        ),
    ],
)
async def test_simple_scenario(
        taxi_qc_executors,
        testpoint,
        mockserver,
        passes_,
        ids_,
        exams_with_sanctions_,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': passes_, 'cursor': 'next'}, status=200,
        )

    @mockserver.json_handler('/quality-control-cpp/v1/blocks')
    def _quality_contol_cpp_v1_blocks(request):
        assert request.method == 'POST'
        assert set(request.json['entity_id_in_set']) == set(ids_)
        return mockserver.make_response(
            json={
                'entities_by_id': [utils.make_blocks_item(id) for id in ids_],
            },
            status=200,
        )

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        got_fields = set()
        print(request.json)
        for val in request.json['items']:
            for dat in val['data']:
                got_fields.add(dat['field'])
            assert 'sanctions' in got_fields
            got_fields = set()
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('fetch-sanctions'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
    assert _quality_contol_cpp_v1_blocks.times_called == 1
    assert _internal_qc_pools_v1_pool_push.times_called == 1
