# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest
import json


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_check_statistics(
        taxi_geo_pipeline_control_plane,
        taxi_geo_pipeline_control_plane_monitor,
        load_json,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    stats = await taxi_geo_pipeline_control_plane_monitor.get_metric(
        'geo-pipeline-control-plane-statistics',
    )
    assert stats == {
        '$meta': {
            '$meta': {'solomon_children_labels': 'pipeline'},
            'solomon_children_labels': 'version',
        },
        '4': {
            '$meta': {'solomon_children_labels': 'pipeline'},
            'test': {'enabled': 1},
            'test2': {'enabled': 1},
        },
        ## old versions of config
        '3': {
            '$meta': {'solomon_children_labels': 'pipeline'},
            'test': {'enabled': 1},
            'test2': {'enabled': 1},
        },
        'all': {
            '$meta': {'solomon_children_labels': 'pipeline'},
            'test': {'enabled': 1},
            'test2': {'enabled': 1},
        },
    }
