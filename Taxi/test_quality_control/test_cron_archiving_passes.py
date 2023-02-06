import datetime
import typing

import pytest

from taxi.util import dates

from quality_control.generated.cron import run_cron


async def _get_pass_ids(db):
    cursor = db.qc_passes.find({}, projection=['_id'])
    passes: typing.List[str] = list()
    async for item in cursor:
        passes.append(item['_id'])

    return sorted(passes)


@pytest.mark.now('2021-04-08T18:00:00.000Z')
@pytest.mark.config(
    QC_ARCHIVING_RULES=dict(
        car=dict(dkk=dict(enabled='on', lag='1d', chunk=5, sleep_ms=0)),
    ),
)
async def test_archiving_passes(patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.archiving_passes', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls

    graphite_calls = sorted(graphite_calls, key=lambda x: x['metric'])
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    timestamp = dates.timestamp_us(now)
    assert len(graphite_calls) == 10
    assert graphite_calls[2:] == [
        dict(
            metric='qc.archiving_passes.car.dkk.deleted',
            timestamp=timestamp,
            value=5,
        ),
        dict(
            metric='qc.archiving_passes.car.dkk.skipped',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.archiving_passes.car.dkk.to_delete',
            timestamp=timestamp,
            value=5,
        ),
        dict(
            metric='qc.archiving_passes.car.dkk.total',
            timestamp=timestamp,
            value=6,
        ),
        dict(
            metric='qc.archiving_passes.total.deleted',
            timestamp=timestamp,
            value=5,
        ),
        dict(
            metric='qc.archiving_passes.total.skipped',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.archiving_passes.total.to_delete',
            timestamp=timestamp,
            value=5,
        ),
        dict(
            metric='qc.archiving_passes.total.total',
            timestamp=timestamp,
            value=6,
        ),
    ]

    passes = await _get_pass_ids(db)
    assert passes == ['too_new_pass', 'used_pass_id']


@pytest.mark.now('2021-04-08T18:00:00.000Z')
@pytest.mark.config(
    QC_ARCHIVING_RULES=dict(
        car=dict(
            dkk=dict(
                enabled='on',
                lag='1d',
                chunk=5,
                sleep_ms=0,
                skip_entity_check=True,
            ),
        ),
    ),
)
async def test_skip_entity_check(patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.archiving_passes', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls

    graphite_calls = sorted(graphite_calls, key=lambda x: x['metric'])
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    timestamp = dates.timestamp_us(now)
    assert len(graphite_calls) == 8
    assert graphite_calls[2:] == [
        dict(
            metric='qc.archiving_passes.car.dkk.deleted',
            timestamp=timestamp,
            value=6,
        ),
        dict(
            metric='qc.archiving_passes.car.dkk.to_delete',
            timestamp=timestamp,
            value=6,
        ),
        dict(
            metric='qc.archiving_passes.car.dkk.total',
            timestamp=timestamp,
            value=6,
        ),
        dict(
            metric='qc.archiving_passes.total.deleted',
            timestamp=timestamp,
            value=6,
        ),
        dict(
            metric='qc.archiving_passes.total.to_delete',
            timestamp=timestamp,
            value=6,
        ),
        dict(
            metric='qc.archiving_passes.total.total',
            timestamp=timestamp,
            value=6,
        ),
    ]

    passes = await _get_pass_ids(db)
    assert passes == ['too_new_pass']


@pytest.mark.now('2021-04-08T18:00:00.000Z')
@pytest.mark.config(
    QC_ARCHIVING_RULES=dict(
        car=dict(dkk=dict(enabled='dry-run', lag='1d', chunk=5, sleep_ms=0)),
    ),
)
async def test_dry_run_mode(patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.archiving_passes', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls

    graphite_calls = sorted(graphite_calls, key=lambda x: x['metric'])
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    timestamp = dates.timestamp_us(now)
    assert len(graphite_calls) == 8
    assert graphite_calls[2:] == [
        dict(
            metric='qc.archiving_passes.car.dkk.skipped',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.archiving_passes.car.dkk.to_delete',
            timestamp=timestamp,
            value=5,
        ),
        dict(
            metric='qc.archiving_passes.car.dkk.total',
            timestamp=timestamp,
            value=6,
        ),
        dict(
            metric='qc.archiving_passes.total.skipped',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.archiving_passes.total.to_delete',
            timestamp=timestamp,
            value=5,
        ),
        dict(
            metric='qc.archiving_passes.total.total',
            timestamp=timestamp,
            value=6,
        ),
    ]

    passes = await _get_pass_ids(db)
    assert len(passes) == 7
