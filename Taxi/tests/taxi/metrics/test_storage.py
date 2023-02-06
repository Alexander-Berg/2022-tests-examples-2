import pytest

from taxi import metrics as metrics_mod


class DummySolomon:
    pass


@pytest.mark.now('2019-01-30T14:00:00.000Z')
@pytest.mark.mongodb_collections('transactions_stat')
async def test_history(db):
    metrics = metrics_mod.Metrics(
        collection_name='transactions_stat',
        time_resolution=15,
        application_name='testsuite',
        commit_time=15,
        upload_time=15,
        db=db,
        client_solomon=DummySolomon(),
        series=(),
    )
    await metrics.sync()

    assert metrics.calc_rps_for('foo', 60) == pytest.approx(4 / 60.0, 1e-6)
    metrics.event('foo')
    assert metrics.calc_rps_for('foo', 60) == pytest.approx(5 / 60.0, 1e-6)
