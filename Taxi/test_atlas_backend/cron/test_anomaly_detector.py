# pylint: disable=unused-variable
import datetime
import math
import random
from typing import List

import pytest

from taxi.util import dates

from atlas_backend.domain import anomaly as anomaly_module
from atlas_backend.generated.cron import run_cron
from atlas_backend.internal.anomalies import create_models
from atlas_backend.internal.anomalies import hierarchy
from atlas_backend.internal.anomalies import time_series_fetcher
from atlas_backend.internal.anomalies import window_pattern
import atlas_backend.internal.anomalies.storage as _anomaly_storage

ANOMALY_START = 130
ANOMALY_END = 421
NOW = datetime.datetime(2020, 11, 14, 10, 3, 10)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_SERVICE_CRON_CONTROL={
        'atlas_backend': {'anomalies.detector': {'run_permission': True}},
    },
)
async def test_detector_empty_config(db):
    await run_cron.main(
        ['atlas_backend.crontasks.anomalies.detector', '-t', '0'],
    )

    day = await db.atlas_anomaly_proc_ctl.find_one(
        {'_id': 'last_predicted_day'},
    )
    last_processed_day = day['last_predicted_day']
    assert last_processed_day == datetime.datetime(2020, 11, 13)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_SERVICE_CRON_CONTROL={
        'atlas_backend': {'anomalies.detector': {'run_permission': True}},
    },
    ATLAS_BACKEND_ANOMALY_DETECTOR={
        'all': {
            'detector_type': 'MultiLineDetector',
            'model': {
                'name': 'all',
                'line_metas': [
                    {
                        'metric_id': 'anomaly_trips_taxi_all',
                        'hist_data_start': '2020-09-01',
                        'confidence_sigma_multiplier': 3,
                    },
                ],
                'anomaly_threshold': 3,
            },
        },
    },
)
async def test_detector(db, detector_models, anomaly_fetcher):
    # pylint: disable=redefined-outer-name
    storage = _anomaly_storage.AnomalyStorage(
        db.atlas_anomalies, hierarchy.SourceHierarchy({}),
    )
    anomalies_before = await storage.get_list(
        from_ts=dates.timestamp(datetime.date(2020, 11, 9), timezone='UTC'),
        to_ts=dates.timestamp(datetime.date(2020, 11, 15), timezone='UTC'),
        statuses=[anomaly_module.AnomalyStatus.CREATED],
        severity_levels=None,
        order_source=anomaly_module.TaxiDowntimeOrderSource.ALL,
        limit=10,
        offset=0,
        with_source_hierarchy=True,
    )
    assert not anomalies_before

    await run_cron.main(
        ['atlas_backend.crontasks.anomalies.detector', '-t', '0'],
    )

    day = await db.atlas_anomaly_proc_ctl.find_one(
        {'_id': 'last_predicted_day'},
    )
    last_processed_day = day['last_predicted_day']
    assert last_processed_day == datetime.datetime(2020, 11, 13)

    anomalies_after = await storage.get_list(
        from_ts=dates.timestamp(datetime.date(2020, 11, 9), timezone='UTC'),
        to_ts=dates.timestamp(datetime.date(2020, 11, 15), timezone='UTC'),
        statuses=[anomaly_module.AnomalyStatus.CREATED],
        severity_levels=None,
        order_source=anomaly_module.TaxiDowntimeOrderSource.ALL,
        limit=10,
        offset=0,
        with_source_hierarchy=True,
    )
    assert len(anomalies_after) == 1
    anomaly = anomalies_after[0]
    start_minute = _minute_of_day(anomaly.start_ts)
    end_minute = _minute_of_day(anomaly.end_ts)
    assert abs(start_minute - ANOMALY_START) <= 60
    assert abs(end_minute - ANOMALY_END) <= 60
    assert anomaly.author == 'robot-taxi-tst-31246'


def _minute_of_day(timestamp: int) -> int:
    dttm = dates.get_local_datetime(timestamp, 'UTC')
    return dttm.hour * 60 + dttm.minute


def _gen_data(iteration: int) -> List[float]:
    random.seed(iteration)
    base_data = [
        1000
        + 200 * math.sin(12 * math.pi * minute / window_pattern.MINUTES_IN_DAY)
        for minute in range(window_pattern.MINUTES_IN_DAY)
    ]
    return [val + random.gauss(0, 5) for val in base_data]


@pytest.fixture
async def detector_models(cron_context, patch):
    @patch('atlas_backend.internal.anomalies.create_models.fetch_hist_data')
    async def mock_fetch_hist_data(start, metric_id, fetcher):
        assert metric_id == 'anomaly_trips_taxi_all'
        result = [_gen_data(i) for i in range(35)]
        return result

    await create_models.create_models(cron_context)


@pytest.fixture
def anomaly_fetcher(patch):
    class Fetcher(time_series_fetcher.AtlasMetricFetcher):
        def _gen_value(self, start, end):
            def _gen(minute):
                return 50

            return _gen

        async def get_day_series(
                self, metric_id: str, day: datetime.datetime,
        ) -> window_pattern.DaySeries:
            base_data = _gen_data(day.day)
            if day == datetime.datetime(2020, 11, 13):
                value_generator = self._gen_value(ANOMALY_START, ANOMALY_END)
                anomaly_data = [
                    value_generator(minute)
                    for minute in range(ANOMALY_START, ANOMALY_END)
                ]
                base_data[ANOMALY_START:ANOMALY_END] = anomaly_data
            assert len(base_data) == window_pattern.MINUTES_IN_DAY
            return base_data

    @patch(
        'atlas_backend.internal.anomalies.time_series_fetcher.AtlasMetricFetcher',  # noqa: E501
    )
    def fetcher(*args, **kwargs):
        return Fetcher(*args, **kwargs)
