import datetime

import pytest


async def get_metrics(
        url: str,
        taxi_userver_sample,
        taxi_userver_sample_monitor,
        mocked_time,
):
    now = datetime.datetime.utcnow()
    mocked_time.set(now)
    await taxi_userver_sample.tests_control(invalidate_caches=False)

    response = await taxi_userver_sample.post(url)
    assert response.status_code == 200

    mocked_time.sleep(6)
    await taxi_userver_sample.tests_control(invalidate_caches=False)

    return await taxi_userver_sample_monitor.get_metric(
        'userver_sample_metrics',
    )


async def test_metrix_base(
        taxi_userver_sample, taxi_userver_sample_monitor, mocked_time,
):
    metrics = await get_metrics(
        'metrix/base',
        taxi_userver_sample,
        taxi_userver_sample_monitor,
        mocked_time,
    )

    assert metrics['metric_1']['econom']['moscow'] == 5

    assert metrics['metric_2']['econom']['spb'] == 7

    assert metrics['metric_3']['moscow']['p0'] == 1
    assert metrics['metric_3']['moscow']['p50'] == 5.0
    assert metrics['metric_3']['moscow']['p95'] == 7.0

    assert metrics['metric_4']['business']['moscow']['p0'] == 1000
    assert metrics['metric_4']['business']['moscow']['p50'] == 5000
    assert metrics['metric_4']['business']['moscow']['p75'] == 7000

    assert metrics['metric_6']['spb'] == 15

    assert metrics['metric_7']['comfort']['moscow'] == 15

    assert metrics['metric_8']['econom']['moscow'] > 0

    assert metrics['metric_9']['econom']['moscow']['p100'] > 0

    assert metrics['metric_0']['econom']['spb'] == 13

    mocked_time.sleep(6)
    await taxi_userver_sample.tests_control(invalidate_caches=False)

    metrics = await taxi_userver_sample_monitor.get_metric(
        'userver_sample_metrics',
    )

    assert metrics['metric_5']['business']['moscow']['p0'] == 1
    assert metrics['metric_5']['business']['moscow']['p50'] == 5
    assert metrics['metric_5']['business']['moscow']['p75'] == 7


@pytest.mark.config(
    METRIX_AGGREGATION=[
        {
            'rule': {
                'and': [
                    {'all_of': ['metric_name:metric_1']},
                    {'any_of': ['zone:moscow', 'tariff:business']},
                ],
            },
            'value': [],
        },
    ],
)
async def test_metrix_aggregation_empty_value(
        taxi_userver_sample, taxi_userver_sample_monitor, mocked_time,
):
    metrics = await get_metrics(
        'metrix/aggregation',
        taxi_userver_sample,
        taxi_userver_sample_monitor,
        mocked_time,
    )

    assert metrics['metric_1']['econom']['moscow'] == 2
    assert metrics['metric_1']['business']['ekb'] == 4
    assert metrics['metric_1']['courier']['moscow'] == 6
    assert metrics['metric_1']['econom'].get('spb') is not None
    assert metrics['metric_1'].get('cargo') is not None
    assert metrics.get('metric_2') is not None


@pytest.mark.config(
    METRIX_AGGREGATION=[
        {
            'rule': {
                'and': [
                    {'all_of': ['metric_name:metric_1']},
                    {
                        'any_of': [
                            'zone:moscow',
                            'zone:spb',
                            'zone:ekb',
                            'tariff:business',
                        ],
                    },
                ],
            },
            'value': [
                {
                    'rule_type': 'whitelist',
                    'label_name': 'zone',
                    'values': ['moscow', 'ekb'],
                    'use_others': True,
                },
                {
                    'rule_type': 'grouping',
                    'label_name': 'tariff',
                    'groups': [
                        {
                            'group_name': 'taxi',
                            'values': ['econom', 'business'],
                        },
                        {
                            'group_name': 'cargo_express',
                            'values': ['cargo', 'courier'],
                        },
                    ],
                    'use_others': False,
                },
            ],
        },
    ],
)
async def test_metrix_aggregation_agg_value(
        taxi_userver_sample, taxi_userver_sample_monitor, mocked_time,
):
    metrics = await get_metrics(
        'metrix/aggregation',
        taxi_userver_sample,
        taxi_userver_sample_monitor,
        mocked_time,
    )

    assert metrics['metric_1']['taxi']['moscow'] == 2
    assert metrics['metric_1']['taxi']['ekb'] == 4
    assert metrics['metric_1']['taxi']['others'] == 3
    assert metrics['metric_1']['cargo_express']['ekb'] == 5
    assert metrics['metric_1']['cargo_express']['moscow'] == 6

    assert metrics['metric_1']['taxi'].get('spb') is None
    assert metrics['metric_1'].get('others') is None
    assert metrics.get('metric_2') is not None
