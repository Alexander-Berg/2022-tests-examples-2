import os

import pytest


async def test_get_metrics(taxi_statistics_agent, statistics):
    metrics = [{'name': 'test1', 'value': 1}, {'name': 'test2', 'value': 2}]

    async with statistics.capture(taxi_statistics_agent, 'test-service'):
        statistics.update_statistics('test-service', metrics)
        await taxi_statistics_agent.invalidate_caches()

        response = await taxi_statistics_agent.post(
            'v1/metrics/list', json={'metrics': ['test1', 'test2']},
        )
        assert response.status_code == 200
        assert response.json() == {'metrics': metrics}


def secdist_patch_config(config, config_vars):
    secdist_path = (
        os.path.dirname(os.path.abspath(__file__))
        + '/static/test_handlers/secdist.json'
    )
    config['components_manager']['components']['secdist'][
        'config'
    ] = secdist_path


@pytest.mark.uservice_oneshot(config_hooks=[secdist_patch_config])
async def test_send_metrics_from_statistics_service_name(
        taxi_statistics_agent, statistics,
):
    metrics = [{'name': 'test1', 'value': 1}, {'name': 'test2', 'value': 2}]

    async with statistics.capture(
            taxi_statistics_agent, 'transactions',
    ) as capture:
        response = await taxi_statistics_agent.post(
            'v1/metrics/store', json={'metrics': metrics},
        )
        assert response.status_code == 200

    assert capture.statistics == {'test1': 1, 'test2': 2}


async def test_send_metrics(taxi_statistics_agent, statistics):
    metrics = [{'name': 'test1', 'value': 1}, {'name': 'test2', 'value': 2}]

    async with statistics.capture(
            taxi_statistics_agent, 'test-service',
    ) as capture:
        response = await taxi_statistics_agent.post(
            'v1/metrics/store', json={'metrics': metrics},
        )
        assert response.status_code == 200

    assert capture.statistics == {'test1': 1, 'test2': 2}


async def test_get_fallbacks(taxi_statistics_agent, statistics):
    statistics.fallbacks = ['foo.fallback1', 'bar.fallback2']

    response = await taxi_statistics_agent.post(
        'v1/fallbacks/state',
        json={'fallbacks': ['foo.fallback1', 'bar.fallback2', 'not.exist']},
    )
    assert response.status_code == 200
    assert response.json() == {
        'fallbacks': [
            {'name': 'foo.fallback1', 'value': True},
            {'name': 'bar.fallback2', 'value': True},
            {'name': 'not.exist', 'value': False},
        ],
    }


def patch_config_user_yaml(config, config_vars):
    config['components_manager']['components']['settings-storage'][
        'statistics-services'
    ] = ['service1', 'service2']


@pytest.mark.parametrize('service_name', [None, 'not-existing-service'])
@pytest.mark.uservice_oneshot(config_hooks=[patch_config_user_yaml])
async def test_requests_with_service_name_errors(
        taxi_statistics_agent, service_name,
):
    # can't use api without service-name if there are multiple
    # services in config
    body = {'metrics': ['test']}
    if service_name:
        body['service_name'] = service_name
    response = await taxi_statistics_agent.post('v1/metrics/list', json=body)
    assert response.status_code == 400

    metrics = [{'name': 'test1', 'value': 1}, {'name': 'test2', 'value': 2}]
    body = {'metrics': metrics}
    if service_name:
        body['service_name'] = service_name
    response = await taxi_statistics_agent.post('v1/metrics/store', json=body)
    assert response.status_code == 400

    body = {'fallbacks': ['not-exist']}
    if service_name:
        body['service_name'] = service_name
    response = await taxi_statistics_agent.post(
        'v1/fallbacks/state', json=body,
    )
    assert response.status_code == 400


@pytest.mark.uservice_oneshot(config_hooks=[patch_config_user_yaml])
async def test_several_services_in_config(taxi_statistics_agent, statistics):
    services = 'service1', 'service2'
    metrics = [{'name': 'test1', 'value': 1}, {'name': 'test2', 'value': 2}]

    for service in services:
        async with statistics.capture(
                taxi_statistics_agent, service,
        ) as capture:
            response = await taxi_statistics_agent.post(
                'v1/metrics/store',
                json={'metrics': metrics, 'service_name': service},
            )
            assert response.status_code == 200

        assert capture.statistics == {'test1': 1, 'test2': 2}

    for service in services:
        async with statistics.capture(taxi_statistics_agent, service):
            statistics.update_statistics(service, metrics)
            await taxi_statistics_agent.invalidate_caches()

            response = await taxi_statistics_agent.post(
                'v1/metrics/list',
                json={'metrics': ['test1', 'test2'], 'service_name': service},
            )
            assert response.status_code == 200
            assert response.json() == {
                'metrics': metrics,
                'service_name': service,
            }

    statistics.fallbacks = ['foo.fallback1', 'bar.fallback2']

    for service in services:
        await taxi_statistics_agent.invalidate_caches()
        response = await taxi_statistics_agent.post(
            'v1/fallbacks/state',
            json={
                'fallbacks': ['foo.fallback1', 'bar.fallback2', 'not.exist'],
                'service_name': service,
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            'fallbacks': [
                {'name': 'foo.fallback1', 'value': True},
                {'name': 'bar.fallback2', 'value': True},
                {'name': 'not.exist', 'value': False},
            ],
            'service_name': service,
        }
