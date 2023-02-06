import pytest

from tests_qc_executors import utils


@pytest.mark.config(
    QC_EXECUTORS_SAVE_BIOMETRY_ETALONS_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
        'concurrent_biometry_etalons_requests_count': 10,
    },
)
@pytest.mark.parametrize(
    'ids_, multiple_pools_response',
    [
        pytest.param(
            [
                '7ad36bc7560449998acbe2c57a75c293_b3aae4c3400b6baef08fbb4484dd5a69',  # noqa: E501
            ]
            * 4,
            (('1', 'bucket'), ('2', 'bucket')),
            marks=pytest.mark.config(
                QC_EXECUTORS_ETALONS_POOLS_PRIORITY=[
                    'from_toloka',
                    'plotva_ml_pool',
                ],
            ),
        ),
        pytest.param(
            [
                '7ad36bc7560449998acbe2c57a75c293_b3aae4c3400b6baef08fbb4484dd5a69',  # noqa: E501
            ]
            * 4,
            (('1', 'bucket'), ('3', 'bucket')),
            marks=pytest.mark.config(
                QC_EXECUTORS_ETALONS_POOLS_PRIORITY=[
                    'plotva_ml_pool',
                    'from_toloka',
                ],
            ),
        ),
    ],
)
async def test_simple_scenario(
        taxi_qc_executors,
        testpoint,
        mockserver,
        load_json,
        biometry_etalons,
        ids_,
        multiple_pools_response,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': load_json('passes.json'), 'cursor': 'next'},
            status=200,
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
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    park_id = '7ad36bc7560449998acbe2c57a75c293'
    biometry_etalons.set_expected_etalons(
        park_id, 'b3aae4c3400b6baef08fbb4484dd5a69', multiple_pools_response,
    )
    biometry_etalons.set_expected_etalons(
        park_id, 'b3aae4c3400b6baef08fbb4484dd5a68', (('4', 'bucket'),),
    )
    biometry_etalons.set_expected_etalons(
        park_id, 'b3aae4c3400b6baef08fbb4484dd5a67', (('5', 'bucket'),),
    )

    async with taxi_qc_executors.spawn_task('save-biometry-etalons'):
        await handle_finished.wait_call()
