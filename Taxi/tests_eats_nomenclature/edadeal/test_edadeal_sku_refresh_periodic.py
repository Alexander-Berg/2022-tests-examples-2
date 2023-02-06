import json

import pytest

SKU_YT_PATH = '//edadeal_yt/skus'
QUEUE_NAME = 'eats_nomenclature_edadeal_yt_skus_processing'
EDADEAL_REACTOR_HANDLER = '/nirvana-reactor-production/api/v1/a/i/get/last'
PERIODIC_NAME = 'edadeal-yt-skus-sync-periodic'


@pytest.fixture(name='reactor_edadeal_mock')
def _reactor_edadeal_mock(mockserver, testsuite_build_dir, load_yaml):
    @mockserver.json_handler(EDADEAL_REACTOR_HANDLER)
    def _mock(request):
        config_path = testsuite_build_dir.joinpath('configs/service.yaml')
        config = load_yaml(config_path)
        config_vars = load_yaml(config['config_vars'])
        artifact_id_var_name = config['components_manager']['components'][
            'nmn-service-settings'
        ]['reactor_edadeal_skus_artifact_id']
        artifact_id = config_vars[artifact_id_var_name[1:]]

        data = request.json
        assert data['artifactIdentifier']['artifactId'] == artifact_id

        return mockserver.make_response(
            json.dumps(
                {
                    'result': {
                        'id': 'dummy_id',
                        'artifactId': f'{artifact_id}',
                        'creatorLogin': 'dummy_login',
                        'metadata': {
                            '@type': (
                                '/yandex.reactor.artifact.'
                                + 'YtPathArtifactValueProto'
                            ),
                            'path': SKU_YT_PATH,
                        },
                        'creationTimestamp': 'dummy_stamp',
                        'status': 'ACTIVE',
                        'source': 'API',
                    },
                },
            ),
            200,
        )


@pytest.mark.suspend_periodic_tasks('PERIODIC_NAME')
async def test_no_previous_path(
        stq, reactor_edadeal_mock, taxi_eats_nomenclature,
):
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    stq_next_call = getattr(stq, QUEUE_NAME).next_call()
    assert 'skus_yt_path' in stq_next_call['kwargs']
    assert stq_next_call['kwargs']['skus_yt_path'] == SKU_YT_PATH


@pytest.mark.suspend_periodic_tasks('PERIODIC_NAME')
async def test_has_same_path(
        stq, reactor_edadeal_mock, taxi_eats_nomenclature, pgsql,
):
    sql_add_sku_path(pgsql, SKU_YT_PATH)

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    assert getattr(stq, QUEUE_NAME).has_calls is False


@pytest.mark.suspend_periodic_tasks('PERIODIC_NAME')
async def test_has_different_path(
        stq, reactor_edadeal_mock, taxi_eats_nomenclature, pgsql,
):
    sql_add_sku_path(pgsql, f'{SKU_YT_PATH}_different')

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    stq_next_call = getattr(stq, QUEUE_NAME).next_call()
    assert 'skus_yt_path' in stq_next_call['kwargs']
    assert stq_next_call['kwargs']['skus_yt_path'] == SKU_YT_PATH


async def test_periodic_metrics(reactor_edadeal_mock, verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def sql_add_sku_path(pgsql, path):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.sku_yt_update_statuses
        (last_sku_path, update_started_at, is_in_progress)
        values ('{path}', now(), false)
        """,
    )
