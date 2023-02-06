import pytest


NOW = '2022-01-26T12:00:00+0300'


@pytest.mark.config(
    SCOOTERS_OPS_RELOCATION_WORKERS_V2={
        'iteration-worker': {'enabled': True, 'period_seconds': 60},
    },
    SCOOTERS_REGIONS=[
        {'id': 'moscow', 'name': 'Москва'},
        {'id': 'spb', 'name': 'Питер'},
    ],
    SCOOTERS_OPS_RELOCATION_ITERATION_STQ_DELAY=100,
)
@pytest.mark.experiments3(filename='exp3_polygons.json')
@pytest.mark.experiments3(filename='exp3_settings.json')
@pytest.mark.now(NOW)
async def test(taxi_scooters_ops_relocation, pgsql, testpoint, stq):
    polygons = []

    @testpoint('iteration.relevant_polygons')
    def _relevant_polygons(request):
        polygons.extend(request['polygons'])

    await taxi_scooters_ops_relocation.run_task('testsuite-iteration-worker')

    assert _relevant_polygons.times_called == 1

    assert sorted(polygons) == sorted(['msk1', 'msk2', 'msk3', 'msk4', 'spb1'])

    assert stq.scooters_ops_relocation_iteration.times_called == 2
