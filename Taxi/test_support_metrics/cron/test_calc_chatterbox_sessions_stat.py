# pylint: disable=redefined-outer-name
import datetime
import json

import freezegun
import pytest
import pytz

from support_metrics.generated.cron import run_cron
from . import expected_calc_aggregate_stat as expected


NOW = datetime.datetime(2019, 7, 2, 12, 2, 23)


async def _check_result(db, expected_result, expected_updated_time=None):
    result = await db.primary_fetch(
        'SELECT * FROM events.aggregated_stat ORDER BY id ASC',
    )
    expected_stat = sorted(expected_result, key=lambda x: x['id'])
    assert len(expected_result) == len(result)
    for i, record in enumerate(result):
        assert record['id'] == expected_stat[i]['id'], dict(record)
        assert record['source'] == expected_stat[i]['source']
        assert record['created_ts'] == expected_stat[i]['created_ts']
        if expected_updated_time:
            assert record['updated_ts'] == expected_updated_time.replace(
                tzinfo=pytz.utc,
            )
        assert record['sent'] == expected_stat[i]['sent']
        assert json.loads(record['stat']) == expected_stat[i]['stat']


@pytest.mark.config(
    SUPPORT_METRICS_SIMULTANEOUS_CALCULATION=False,
    SUPPORT_METRICS_SESSION_DURATION_THRESHOLDS_IN_MINUTES=[1, 2],
)
@pytest.mark.parametrize(
    'expected_result',
    [
        [
            expected.CHATTERBOX_SESSIONS_AT_12_00
            + expected.CHATTERBOX_SESSIONS_AT_12_05_UPDATED_AT_12_0_23,
            expected.CHATTERBOX_SESSIONS_AT_12_00
            + expected.CHATTERBOX_SESSIONS_AT_12_05_UPDATED_AT_12_2_23,
        ],
    ],
)
async def test_calc_stat(cron_context, expected_result):
    with freezegun.freeze_time(NOW - datetime.timedelta(minutes=2)):
        await run_cron.main(
            [
                'support_metrics.crontasks.calculate_chatterbox_sessions_stat',
                '-t',
                '0',
            ],
        )
    db = cron_context.postgresql.support_metrics[0]
    await _check_result(
        db,
        expected_result[0],
        expected_updated_time=NOW - datetime.timedelta(minutes=2),
    )

    with freezegun.freeze_time(NOW):
        await run_cron.main(
            [
                'support_metrics.crontasks.calculate_chatterbox_sessions_stat',
                '-t',
                '0',
            ],
        )
    await _check_result(db, expected_result[1])
