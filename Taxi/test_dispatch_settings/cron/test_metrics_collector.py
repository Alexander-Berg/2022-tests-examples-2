import dataclasses
import datetime

import pytest

from taxi.maintenance import run
from taxi.util import dates

from dispatch_settings.crontasks import metrics_collector


TIMESTAMP_NOW = 1619827200
NOW = datetime.datetime.utcfromtimestamp(TIMESTAMP_NOW)


@dataclasses.dataclass()
class MetricsEtalon:
    settings_count: int = 0
    invalid_zones_count: int = 0
    categories_count: int = 0
    not_filled_categories_count: int = 0
    resetted_categories_count: int = 0
    invalid_group_tariffs_count: int = 0


def check_metrics(cron_context, get_stats, etalon: MetricsEtalon):
    assert (
        get_stats(
            cron_context,
            [
                {'sensor': 'settings.all.count'},
                {'sensor': 'zones.invalid.count'},
                {'sensor': 'categories.all.count'},
                {'sensor': 'categories.not_filled.count'},
                {'sensor': 'categories.resetted.count'},
                {'sensor': 'default_zone.invalid_group_tariffs.count'},
            ],
        )
        == [
            [
                {
                    'kind': 'IGAUGE',
                    'labels': {'sensor': 'settings.all.count'},
                    'timestamp': None,
                    'value': etalon.settings_count,
                },
            ],
            [
                {
                    'kind': 'IGAUGE',
                    'labels': {'sensor': 'zones.invalid.count'},
                    'timestamp': None,
                    'value': etalon.invalid_zones_count,
                },
            ],
            [
                {
                    'kind': 'IGAUGE',
                    'labels': {'sensor': 'categories.all.count'},
                    'timestamp': None,
                    'value': etalon.categories_count,
                },
            ],
            [
                {
                    'kind': 'IGAUGE',
                    'labels': {'sensor': 'categories.not_filled.count'},
                    'timestamp': None,
                    'value': etalon.not_filled_categories_count,
                },
            ],
            [
                {
                    'kind': 'IGAUGE',
                    'labels': {'sensor': 'categories.resetted.count'},
                    'timestamp': None,
                    'value': etalon.resetted_categories_count,
                },
            ],
            [
                {
                    'kind': 'IGAUGE',
                    'labels': {
                        'sensor': 'default_zone.invalid_group_tariffs.count',
                    },
                    'timestamp': None,
                    'value': etalon.invalid_group_tariffs_count,
                },
            ],
        ]
    )


@pytest.mark.now(NOW.isoformat())
async def test_metrics_collector_empty(
        cron_context, get_stats_by_list_label_values,
):
    check_metrics(
        cron_context, get_stats_by_list_label_values, etalon=MetricsEtalon(),
    )


@pytest.mark.config(DISPATCH_SETTINGS_REQUIRED_SETTINGS_IN_CATEGORY_COUNT=2)
@pytest.mark.now(NOW.isoformat())
async def test_metrics_collector(
        cron_context, loop, get_stats_by_list_label_values, tariffs,
):
    tariffs.set_zones(['test_zone_1', 'test_zone_2', 'some_new_zone'])

    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    await metrics_collector.do_stuff(stuff_context, loop)
    check_metrics(
        cron_context,
        get_stats_by_list_label_values,
        etalon=MetricsEtalon(
            settings_count=11,
            invalid_zones_count=3,
            categories_count=5,
            not_filled_categories_count=3,
            resetted_categories_count=2,
            invalid_group_tariffs_count=1,
        ),
    )
