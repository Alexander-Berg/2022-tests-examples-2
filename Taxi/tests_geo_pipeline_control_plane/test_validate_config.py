# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest
import json


async def test_validate_bad_pipelines(
        taxi_geo_pipeline_control_plane, load_json, fts_current_version,
):
    for pipeline_config in load_json('bad_configs.json'):
        response = await taxi_geo_pipeline_control_plane.post(
            'v1/config/validate',
            json={'version': fts_current_version, 'config': pipeline_config},
        )
        assert response.status_code == 200
        assert not response.json()['is_valid']


async def test_validate_good_pipelines(
        taxi_geo_pipeline_control_plane, load_json, fts_current_version,
):
    ## We use this file in many other tests, so let's check it
    pipeline_config = load_json('config1.json')['test']
    response = await taxi_geo_pipeline_control_plane.post(
        'v1/config/validate',
        json={'version': fts_current_version, 'config': pipeline_config},
    )
    assert response.status_code == 200
    assert response.json()['is_valid']

    ## You can add other files here
