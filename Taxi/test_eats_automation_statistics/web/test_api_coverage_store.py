async def test_success_store_and_get(taxi_eats_automation_statistics_web):
    response = await taxi_eats_automation_statistics_web.post(
        path='/api/v1/coverage',
        json={
            'services': [
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
        },
    )
    assert response.status == 201
    response_json = await response.json()
    assert response_json == {'stored_records': 2}

    response = await taxi_eats_automation_statistics_web.get(
        path='/api/v1/coverage', params={'service_name': 'some-service-1'},
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json == {
        'services': [
            {
                'service_name': 'some-service-1',
                'coverage_ratio': 0.73,
                'repository': 'uservices',
                'commit_id': '4fabcd53',
            },
        ],
    }


async def test_store_error(taxi_eats_automation_statistics_web):
    response = await taxi_eats_automation_statistics_web.post(
        path='/api/v1/coverage', json={},
    )
    assert response.status == 400
    response_json = await response.json()
    assert response_json == {
        'message': 'Список переданных сервисов для сохранения пуст',
    }


async def test_get_last_results(taxi_eats_automation_statistics_web):
    response = await taxi_eats_automation_statistics_web.post(
        path='/api/v1/coverage',
        json={
            'services': [
                {
                    'service_name': 'test-service',
                    'coverage_ratio': 0.666,
                    'repository': 'uservices',
                    'commit_id': '4fabcd53',
                },
            ],
        },
    )
    assert response.status == 201

    response = await taxi_eats_automation_statistics_web.post(
        path='/api/v1/coverage',
        json={
            'services': [
                {
                    'service_name': 'test-service',
                    'coverage_ratio': 0.777,
                    'repository': 'uservices',
                    'commit_id': 'fff45ab9',
                },
            ],
        },
    )
    assert response.status == 201

    response = await taxi_eats_automation_statistics_web.get(
        path='/api/v1/coverage', params={'service_name': 'test-service'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'services': [
            {
                'service_name': 'test-service',
                'coverage_ratio': 0.777,
                'repository': 'uservices',
                'commit_id': 'fff45ab9',
            },
        ],
    }


async def test_coverage_ratio_precision(taxi_eats_automation_statistics_web):
    expected_coverage_ratio = 0.15037593984962405
    response = await taxi_eats_automation_statistics_web.post(
        path='/api/v1/coverage',
        json={
            'services': [
                {
                    'service_name': 'test-precision-service',
                    'coverage_ratio': expected_coverage_ratio,
                    'commit_id': 'test_commit_id',
                    'repository': 'backend-py3',
                },
            ],
        },
    )
    assert response.status == 201

    response = await taxi_eats_automation_statistics_web.get(
        path='/api/v1/coverage',
        params={'service_name': 'test-precision-service'},
    )
    assert response.status == 200
    response_json = await response.json()
    actual_coverage_ratio = response_json['services'][0]['coverage_ratio']
    assert actual_coverage_ratio == expected_coverage_ratio
