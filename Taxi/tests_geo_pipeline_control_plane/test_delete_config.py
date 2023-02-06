# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest
import json


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_delete_pipeline(
        taxi_geo_pipeline_control_plane,
        load_json,
        fts_db_configs_by_version,
        fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    pipelines_configs = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', 4,
    )
    pipeline_names = pipelines_configs.keys()
    expected_answer = pipelines_configs.copy()

    response = await taxi_geo_pipeline_control_plane.post(
        f'/internal/config/get-all', json={'version': fts_current_version},
    )
    assert response.status_code == 200
    assert response.json() == expected_answer

    for pipeline in pipeline_names:
        response = await taxi_geo_pipeline_control_plane.post(
            f'/v1/config/get?pipeline={pipeline}',
            json={'version': fts_current_version},
        )
        assert response.status_code == 200
        response = await taxi_geo_pipeline_control_plane.post(
            f'/v1/config/delete?pipeline={pipeline}',
            json={'version': fts_current_version},
        )
        assert response.status_code == 200
        del expected_answer[pipeline]

        await taxi_geo_pipeline_control_plane.invalidate_caches()

        response = await taxi_geo_pipeline_control_plane.post(
            f'/internal/config/get-all', json={'version': fts_current_version},
        )
        assert response.status_code == 200
        assert response.json() == expected_answer


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_delete_pipeline_twice(
        taxi_geo_pipeline_control_plane, fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/get?pipeline=test', json={'version': fts_current_version},
    )
    assert response.status_code == 200

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/delete?pipeline=test',
        json={'version': fts_current_version},
    )
    assert response.status_code == 200

    await taxi_geo_pipeline_control_plane.invalidate_caches()

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/delete?pipeline=test',
        json={'version': fts_current_version},
    )
    assert response.status_code == 404


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_delete_missing_pipeline(
        taxi_geo_pipeline_control_plane, fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/delete?pipeline=test4',
        json={'version': fts_current_version},
    )
    assert response.status_code == 404
