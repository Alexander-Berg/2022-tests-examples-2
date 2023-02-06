import datetime

import pytest

from taxi.util import dates

from quality_control.generated.cron import run_cron


@pytest.mark.now('2021-04-08T18:00:00.000Z')
@pytest.mark.config(
    QC_CLEANUP_CANCELLED_PASSES=dict(enabled='on', lower='2d', upper='1d'),
)
async def test_cleanup_cancelled(patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.cleanup_cancelled_passes', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls

    graphite_calls = sorted(graphite_calls, key=lambda x: x['metric'])
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    timestamp = dates.timestamp_us(now)
    assert len(graphite_calls) == 3
    assert graphite_calls[2:] == [
        dict(
            metric='qc.cleanup_passes.cancelled', timestamp=timestamp, value=1,
        ),
    ]

    assert await db.qc_passes.count() == 4


@pytest.mark.now('2021-04-08T18:00:00.000Z')
@pytest.mark.config(
    QC_CLEANUP_CANCELLED_PASSES=dict(
        enabled='dry-run', lower='2d', upper='1d',
    ),
)
async def test_cleanup_cancelled_dry_run(patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.cleanup_cancelled_passes', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls

    graphite_calls = sorted(graphite_calls, key=lambda x: x['metric'])
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    timestamp = dates.timestamp_us(now)
    assert len(graphite_calls) == 3
    assert graphite_calls[2:] == [
        dict(
            metric='qc.cleanup_passes.cancelled', timestamp=timestamp, value=1,
        ),
    ]

    assert await db.qc_passes.count() == 5


@pytest.mark.now('2021-04-08T18:00:00.000Z')
@pytest.mark.config(
    QC_CLEANUP_CANCELLED_PASSES=dict(enabled='off', lower='2d', upper='1d'),
)
async def test_cleanup_cancelled_off(patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.cleanup_cancelled_passes', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls
    assert len(graphite_calls) == 2

    assert await db.qc_passes.count() == 5
