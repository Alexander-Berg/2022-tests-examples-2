# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest
import json


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_get_pipelines_names_list(
        taxi_geo_pipeline_control_plane,
        load_json,
        fts_db_configs_by_version,
        fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()

    expected_response = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', fts_current_version,
    )
    response = await taxi_geo_pipeline_control_plane.post(
        '/v1/config/list', json={'version': fts_current_version},
    )
    assert response.status_code == 200
    assert sorted(response.json()) == sorted(expected_response)


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_get_all_configs_v4(
        taxi_geo_pipeline_control_plane,
        fts_db_configs_by_version,
        fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()

    expected_response = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', fts_current_version,
    )
    response = await taxi_geo_pipeline_control_plane.post(
        '/internal/config/get-all', json={'version': fts_current_version},
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_get_all_configs_v3(
        taxi_geo_pipeline_control_plane,
        load_json,
        fts_db_configs_by_version,
        fts_current_version,
):
    """This test checks that previous versions of config are still accessible"""
    await taxi_geo_pipeline_control_plane.invalidate_caches()

    expected_response = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', 3,
    )
    response = await taxi_geo_pipeline_control_plane.post(
        '/internal/config/get-all', json={'version': 3},
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_get_exact_configs(
        taxi_geo_pipeline_control_plane,
        load_json,
        fts_db_configs_by_version,
        fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()

    pipelines_configs = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', fts_current_version,
    )

    for pipeline in pipelines_configs.keys():
        response = await taxi_geo_pipeline_control_plane.post(
            f'/v1/config/get?pipeline={pipeline}',
            json={'version': fts_current_version},
        )
        assert response.status_code == 200
        assert response.json()['config'] == pipelines_configs[pipeline]


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_get_missing_configs(
        taxi_geo_pipeline_control_plane, fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/get?pipeline=test4',
        json={'version': fts_current_version},
    )
    assert response.status_code == 404
