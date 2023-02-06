import pytest


def secdist_patch_config(config, config_vars):
    config['components_manager']['components']['secdist'][
        'config'
    ] = '/dev/non-existing'


# Pilorama must start w/o secdist.json
@pytest.mark.servicetest
@pytest.mark.uservice_oneshot(config_hooks=[secdist_patch_config])
async def test_start_without_secdist(taxi_pilorama):
    response = await taxi_pilorama.get('ping')
    assert response.status_code == 200
