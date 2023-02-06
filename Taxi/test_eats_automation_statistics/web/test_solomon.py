import pytest


@pytest.mark.parametrize(
    'services,expected_stats',
    [
        pytest.param(
            [
                {
                    'service_name': 'some-service-1',
                    'coverage_ratio': 0.73,
                    'repository': 'uservices',
                    'commit_id': '4fabcd53',
                },
                {
                    'service_name': 'some-service-2',
                    'coverage_ratio': 1.0,
                    'repository': 'uservices',
                    'commit_id': '4fabcd53',
                },
            ],
            [
                {
                    'kind': 'IGAUGE',
                    'labels': {
                        'repository': 'uservices',
                        'sensor': 'services_enabled',
                    },
                    'timestamp': None,
                    'value': 2,
                },
                {
                    'kind': 'IGAUGE',
                    'labels': {
                        'repository': 'backend-py3',
                        'sensor': 'services_enabled',
                    },
                    'timestamp': None,
                    'value': 0,
                },
            ],
        ),
        pytest.param(
            [
                {
                    'service_name': 'some-service-1',
                    'coverage_ratio': 0.73,
                    'repository': 'backend-py3',
                    'commit_id': '4fabcd53',
                },
                {
                    'service_name': 'some-service-2',
                    'coverage_ratio': 1.0,
                    'repository': 'uservices',
                    'commit_id': '4fabcd53',
                },
            ],
            [
                {
                    'kind': 'IGAUGE',
                    'labels': {
                        'repository': 'uservices',
                        'sensor': 'services_enabled',
                    },
                    'timestamp': None,
                    'value': 1,
                },
                {
                    'kind': 'IGAUGE',
                    'labels': {
                        'repository': 'backend-py3',
                        'sensor': 'services_enabled',
                    },
                    'timestamp': None,
                    'value': 1,
                },
            ],
        ),
        pytest.param(
            [
                {
                    'service_name': 'some-service-1',
                    'coverage_ratio': 0.666,
                    'repository': 'backend-py3',
                    'commit_id': '4fabcd53',
                },
                {
                    'service_name': 'some-service-2',
                    'coverage_ratio': 0.666,
                    'repository': 'backend-py3',
                    'commit_id': '4fabcd53',
                },
            ],
            [
                {
                    'kind': 'IGAUGE',
                    'labels': {
                        'repository': 'uservices',
                        'sensor': 'services_enabled',
                    },
                    'timestamp': None,
                    'value': 0,
                },
                {
                    'kind': 'IGAUGE',
                    'labels': {
                        'repository': 'backend-py3',
                        'sensor': 'services_enabled',
                    },
                    'timestamp': None,
                    'value': 2,
                },
            ],
        ),
    ],
)
async def test_api_coverage_enabled_metrics(
        get_stats_by_label_values,
        web_app_client,
        web_app,
        services,
        expected_stats,
):
    response = await web_app_client.post(
        path='/api/v1/coverage', json={'services': services},
    )
    assert response.status == 201

    actual_stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'services_enabled'},
    )
    assert actual_stats == expected_stats
