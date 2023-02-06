import datetime

import pytest


def _make_metric_json(tariff_name, zone_group, code, value):
    return {
        '$meta': {'solomon_children_labels': 'tariff'},
        tariff_name: {
            '$meta': {'solomon_children_labels': 'zone_group'},
            zone_group: {
                '$meta': {'solomon_children_labels': 'code'},
                code: {'tariff_unavailable_count': value},
            },
        },
    }


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(names=['top_level:common_statistics'])
async def test_plugin_common_statistics(
        load_json,
        mockserver,
        taxi_routestats,
        taxi_routestats_monitor,
        mocked_time,
        taxi_config,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(_):
        return load_json('protocol_response.json')

    now = datetime.datetime.utcnow()
    mocked_time.set(now)
    await taxi_routestats.tests_control(reset_metrics=True)
    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'),
    )
    assert response.status_code == 200
    mocked_time.set(now + datetime.timedelta(seconds=30))
    await taxi_routestats.tests_control(invalidate_caches=False)

    metrics = await taxi_routestats_monitor.get_metric(
        'routestats_common_metrics',
    )
    assert metrics == _make_metric_json(
        'uberblack', 'rest_zones', 'no_free_cars_nearby', 1,
    )

    taxi_config.set_values(
        {'ROUTESTATS_ZONE_TO_ZONE_GROUP_MAPPING': {'Msk': ['moscow']}},
    )
    await taxi_routestats.tests_control(
        invalidate_caches=True, reset_metrics=True,
    )

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'),
    )
    assert response.status_code == 200
    mocked_time.set(now + datetime.timedelta(seconds=50))

    await taxi_routestats.tests_control(invalidate_caches=False)

    metrics = await taxi_routestats_monitor.get_metric(
        'routestats_common_metrics',
    )
    assert metrics == _make_metric_json(
        'uberblack', 'Msk', 'no_free_cars_nearby', 1,
    )
