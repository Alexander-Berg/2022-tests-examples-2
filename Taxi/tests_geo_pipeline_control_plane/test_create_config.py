# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest
import json


@pytest.mark.filldb(geo_pipeline_configs='empty')
async def test_create_pipeline(
        taxi_geo_pipeline_control_plane,
        load_json,
        fts_db_configs_by_version,
        fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    pipelines_configs = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', fts_current_version,
    )
    assert pipelines_configs

    expected_answer = {}

    response = await taxi_geo_pipeline_control_plane.post(
        f'/internal/config/get-all', json={'version': fts_current_version},
    )
    assert response.status_code == 200
    assert response.json() == expected_answer

    for pipeline, config in pipelines_configs.items():
        response = await taxi_geo_pipeline_control_plane.post(
            f'/v1/config/validate',
            json={'version': fts_current_version, 'config': config},
        )
        assert response.status_code == 200
        assert response.json()['is_valid']

        response = await taxi_geo_pipeline_control_plane.post(
            f'/v1/config/create?pipeline={pipeline}',
            json={'version': fts_current_version, 'config': config},
        )
        expected_answer[pipeline] = config

        await taxi_geo_pipeline_control_plane.invalidate_caches()

        response = await taxi_geo_pipeline_control_plane.post(
            f'/internal/config/get-all', json={'version': fts_current_version},
        )
        assert response.status_code == 200
        assert response.json() == expected_answer


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_create_existing_pipeline(
        taxi_geo_pipeline_control_plane, fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/create?pipeline=test',
        json={'version': fts_current_version, 'config': {'channels-list': {}}},
    )
    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/create?pipeline=test',
        json={'version': fts_current_version, 'config': {'channels-list': {}}},
    )

    assert response.status_code == 400


@pytest.mark.filldb(geo_pipeline_configs='empty')
async def test_create_bad_pipeline(
        taxi_geo_pipeline_control_plane, load_json, fts_current_version,
):
    for pipeline_config in load_json('bad_configs.json'):
        response = await taxi_geo_pipeline_control_plane.post(
            f'/v1/config/create?pipeline=test',
            json={'version': fts_current_version, 'config': pipeline_config},
        )
        assert response.status_code == 400


@pytest.mark.filldb(geo_pipeline_configs='empty')
async def test_create_bad_pipeline_special(
        taxi_geo_pipeline_control_plane, load_json, fts_current_version,
):
    for pipeline_config in load_json('bad_configs_create.json'):
        response = await taxi_geo_pipeline_control_plane.post(
            f'/v1/config/create?piepline=test',
            json={'version': fts_current_version, 'config': pipeline_config},
        )
        assert response.status_code == 400
