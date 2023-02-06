import itertools
import typing

import pytest

from eats_performer_hiring_metrics.generated.cron import (
    cron_context as context_module,
)
from eats_performer_hiring_metrics.generated.cron import run_cron


@pytest.mark.parametrize(
    ('webim_service_level',),
    [
        pytest.param(
            None,
            marks=pytest.mark.pgsql(
                'eats_performer_hiring_metrics', files=['too_old.sql'],
            ),
        ),
        pytest.param(
            60,
            marks=pytest.mark.pgsql(
                'eats_performer_hiring_metrics',
                files=['service_level_60.sql'],
            ),
        ),
    ],
)
@pytest.mark.config(
    EATS_PERFORMER_HIRING_METRICS_WEBIM_SERVICE_LEVEL=dict(
        service_level_delta=3600, good_response_delta=900,
    ),
)
@pytest.mark.now('2022-02-01T12:00:00Z')
async def test_webim_metrics(
        cron_context: context_module.Context,
        get_single_stat_by_label_values,
        webim_service_level: typing.Optional[float],
        mock_stats,
):
    await run_cron.main(
        ['eats_performer_hiring_metrics.crontasks.webim_metrics', '-t', '0'],
    )

    flat_stats = list(itertools.chain.from_iterable(mock_stats))
    if webim_service_level is None:
        assert not flat_stats, 'We expected for stat to not update'
    else:
        assert (
            len(flat_stats) == 1
        ), 'We expected for stat to update exactly once'
        (raw_sensor,) = flat_stats
        assert raw_sensor.labels['sensor'] == 'webim_service_level'
        assert raw_sensor.value == pytest.approx(webim_service_level)
