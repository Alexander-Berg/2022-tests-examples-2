import pytest


@pytest.mark.parametrize('simulate_fail', [True, False])
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_config_reload(
        testpoint, taxi_processing, simulate_fail, use_ydb, use_fast_flow,
):
    @testpoint('ProcessingNgStorage::LoadQueuesAndPipelinesFromFs')
    def load_from_fs_tp(data):
        return {'simuate-fail': simulate_fail}

    response = await taxi_processing.post(
        '/internal/deploy/v1/reload-from-fs', json={},
    )
    assert response.status_code == {True: 400, False: 200}[simulate_fail]
    assert load_from_fs_tp.times_called == 1
