import datetime

import pytest

from taxi.util import dates

import quality_control.extensions as ext
from quality_control.generated.cron import run_cron


@pytest.mark.now('2020-09-09T18:00:00.000Z')
@pytest.mark.config(
    QC_VALIDATE_STATES=dict(enabled='on', lower='2d', upper='1h'),
)
async def test_validate_states(patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.validate_states', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls

    graphite_calls = sorted(graphite_calls, key=lambda x: x['metric'])
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    timestamp = dates.timestamp_us(now)
    assert len(graphite_calls) == 8
    assert graphite_calls[2:] == [
        dict(
            metric='qc.validate_states.driver.dkk.state_block_mismatch',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.validate_states.driver.dkvu.state_block_mismatch',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.validate_states.driver.state_block_mismatch',
            timestamp=timestamp,
            value=2,
        ),
        dict(
            metric='qc.validate_states.total.dkk.state_block_mismatch',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.validate_states.total.dkvu.state_block_mismatch',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.validate_states.total.state_block_mismatch',
            timestamp=timestamp,
            value=2,
        ),
    ]

    entities = db.qc_entities.find({}, projection=['block.items'])
    async for x in entities:
        if x['_id'] == 'missing_block':
            assert ext.state.block(x, 'dkk')['sanctions'] == ['orders_off']
        elif x['_id'] == 'extra_block':
            assert not ext.state.block(x, 'dkvu').get('sanctions')


@pytest.mark.now('2020-09-09T18:00:00.000Z')
@pytest.mark.config(
    QC_VALIDATE_STATES=dict(enabled='on', lower='2d', upper='1h'),
)
@pytest.mark.filldb(qc_entities='missing_pass_id')
async def test_missing_pass(simple_secdist, patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.validate_states', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls

    graphite_calls = sorted(graphite_calls, key=lambda x: x['metric'])
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    timestamp = dates.timestamp_us(now)
    assert len(graphite_calls) == 6
    assert graphite_calls[2:] == [
        dict(
            metric='qc.validate_states.driver.dkvu.pass_not_found',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.validate_states.driver.pass_not_found',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.validate_states.total.dkvu.pass_not_found',
            timestamp=timestamp,
            value=1,
        ),
        dict(
            metric='qc.validate_states.total.pass_not_found',
            timestamp=timestamp,
            value=1,
        ),
    ]


@pytest.mark.now('2020-09-09T12:15:00.000Z')
@pytest.mark.config(
    QC_VALIDATE_STATES=dict(enabled='on', lower='2d', upper='1h'),
)
async def test_too_early_to_validate(simple_secdist, patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.validate_states', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls
    assert len(graphite_calls) == 2


@pytest.mark.now('2020-09-09T18:00:00.000Z')
@pytest.mark.config(
    QC_VALIDATE_STATES=dict(enabled='on', lower='4h', upper='1h'),
)
async def test_too_late_to_validate(simple_secdist, patch, db):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    await run_cron.main(
        ['quality_control.crontasks.validate_states', '-t', '0'],
    )

    graphite_calls = graphite_mock.calls
    assert len(graphite_calls) == 2
