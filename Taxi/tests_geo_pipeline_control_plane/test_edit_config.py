# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest
import json


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_edit_pipeline(
        taxi_geo_pipeline_control_plane,
        load_json,
        fts_db_configs_by_version,
        fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    pipelines_configs = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', fts_current_version,
    )

    expected_answer = pipelines_configs.copy()

    response = await taxi_geo_pipeline_control_plane.post(
        f'/internal/config/get-all', json={'version': fts_current_version},
    )
    assert response.status_code == 200
    assert response.json() == expected_answer

    new_pipeline_value = next(iter(load_json('config1.json').values()))
    print(new_pipeline_value)

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/edit?pipeline=test',
        json={
            'old': {
                'version': fts_current_version,
                'config': pipelines_configs['test'],
            },
            'new': {
                'version': fts_current_version,
                'config': new_pipeline_value,
            },
        },
    )
    assert response.status_code == 200
    expected_answer['test'] = new_pipeline_value
    print(expected_answer['test'])

    await taxi_geo_pipeline_control_plane.invalidate_caches()

    response = await taxi_geo_pipeline_control_plane.post(
        f'/internal/config/get-all', json={'version': fts_current_version},
    )
    assert response.status_code == 200
    assert response.json() == expected_answer


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_edit_pipeline_same_value(
        taxi_geo_pipeline_control_plane,
        load_json,
        fts_db_configs_by_version,
        fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    pipelines_configs = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', 4,
    )

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/edit?pipeline=test',
        json={
            'old': {
                'version': fts_current_version,
                'config': pipelines_configs['test'],
            },
            'new': {
                'version': fts_current_version,
                'config': pipelines_configs['test'],
            },
        },
    )
    assert response.status_code == 200

    await taxi_geo_pipeline_control_plane.invalidate_caches()

    response = await taxi_geo_pipeline_control_plane.post(
        f'/internal/config/get-all', json={'version': fts_current_version},
    )
    assert response.status_code == 200
    assert response.json() == pipelines_configs


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_edit_pipeline_concurrently(
        taxi_geo_pipeline_control_plane,
        load_json,
        fts_db_configs_by_version,
        fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    pipelines_configs = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', 4,
    )
    new_value = next(iter(load_json('config1.json').values()))

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/edit?pipeline=test',
        json={
            'old': {
                'version': fts_current_version,
                'config': pipelines_configs['test'],
            },
            'new': {'version': fts_current_version, 'config': new_value},
        },
    )
    assert response.status_code == 200

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/edit?pipeline=test',
        json={
            'old': {
                'version': fts_current_version,
                'config': pipelines_configs['test'],
            },
            'new': {'version': fts_current_version, 'config': new_value},
        },
    )
    assert response.status_code == 400


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_edit_missing_pipeline(
        taxi_geo_pipeline_control_plane, load_json, fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    new_pipeline_value = load_json('config1.json')

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/edit?pipeline=test4',
        json={
            'old': {
                'version': fts_current_version,
                'config': new_pipeline_value,
            },
            'new': {
                'version': fts_current_version,
                'config': new_pipeline_value,
            },
        },
    )
    assert response.status_code == 400


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_edit_pipeline_bad_old_value(
        taxi_geo_pipeline_control_plane, load_json, fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    new_pipeline_value = load_json('config1.json')

    response = await taxi_geo_pipeline_control_plane.post(
        f'/v1/config/edit?pipeline=test',
        json={
            'old': {
                'version': fts_current_version,
                'config': new_pipeline_value,
            },
            'new': {
                'version': fts_current_version,
                'config': new_pipeline_value,
            },
        },
    )
    assert response.status_code == 400


@pytest.mark.filldb(geo_pipeline_configs='test')
async def test_edit_bad_pipeline(
        taxi_geo_pipeline_control_plane,
        load_json,
        fts_db_configs_by_version,
        fts_current_version,
):
    await taxi_geo_pipeline_control_plane.invalidate_caches()
    pipelines_configs = fts_db_configs_by_version(
        'db_geo_pipeline_configs_test.json', fts_current_version,
    )

    for pipeline_config in load_json('bad_configs.json'):

        response = await taxi_geo_pipeline_control_plane.post(
            f'/v1/config/edit?pipeline=test',
            json={
                'old': {
                    'version': fts_current_version,
                    'config': pipelines_configs['test'],
                },
                'new': {
                    'version': fts_current_version,
                    'config': pipeline_config,
                },
            },
        )
        assert response.status_code == 400
