import pytest


async def test_ok(taxi_bank_applications):
    response = await taxi_bank_applications.post(
        '/applications-test/v1/get_application_track_id',
        json={'application_id': '7948e3a9-623c-4524-a390-9e4264d27a01'},
    )

    assert response.status_code == 200
    assert response.json()['track_id'] == 'track_id'


async def test_no_track_id(taxi_bank_applications):
    response = await taxi_bank_applications.post(
        '/applications-test/v1/get_application_track_id',
        json={'application_id': '7948e3a9-623c-4524-a390-9e4264d27a02'},
    )

    assert response.status_code == 200
    assert response.json().get('track_id') is None


async def test_no_application(taxi_bank_applications):
    response = await taxi_bank_applications.post(
        '/applications-test/v1/get_application_track_id',
        json={'application_id': '7948e3a9-623c-4524-a390-9e4264d27a03'},
    )

    assert response.status_code == 404


async def test_invalid_application_id(taxi_bank_applications):
    response = await taxi_bank_applications.post(
        '/applications-test/v1/get_application_track_id',
        json={'application_id': '1-2-3-4-5'},
    )

    assert response.status_code == 400


def production_patch_config(config, config_vars):
    config_vars['non_production'] = False


@pytest.mark.uservice_oneshot(config_hooks=[production_patch_config])
async def test_production_env(taxi_bank_applications):
    response = await taxi_bank_applications.post(
        '/applications-test/v1/get_application_track_id',
        json={'application_id': '7948e3a9-623c-4524-a390-9e4264d27a01'},
    )

    assert response.status_code == 404
