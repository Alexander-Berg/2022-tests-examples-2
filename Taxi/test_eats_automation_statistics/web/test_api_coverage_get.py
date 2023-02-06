import pytest


@pytest.mark.parametrize(
    'service_name,coverage_ratio,commit_id,repository',
    [
        ('some-service-1', 0.73, '05ad4efa', 'uservices'),
        ('some-service-2', 1.0, '05ad4efa', 'backend-py3'),
    ],
)
async def test_get_one_service(
        taxi_eats_automation_statistics_web,
        service_name,
        coverage_ratio,
        commit_id,
        repository,
):
    response = await taxi_eats_automation_statistics_web.get(
        path='/api/v1/coverage', params={'service_name': service_name},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'services': [
            {
                'service_name': service_name,
                'coverage_ratio': coverage_ratio,
                'commit_id': commit_id,
                'repository': repository,
            },
        ],
    }


async def test_get_all_services(taxi_eats_automation_statistics_web):
    response = await taxi_eats_automation_statistics_web.get(
        path='/api/v1/coverage',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'services': [
            {
                'service_name': 'some-service-1',
                'coverage_ratio': 0.73,
                'commit_id': '05ad4efa',
                'repository': 'uservices',
            },
            {
                'service_name': 'some-service-2',
                'coverage_ratio': 1.0,
                'commit_id': '05ad4efa',
                'repository': 'backend-py3',
            },
        ],
    }


async def test_get_not_found(taxi_eats_automation_statistics_web):
    response = await taxi_eats_automation_statistics_web.get(
        path='/api/v1/coverage',
        params={'service_name': 'not-existing-service'},
    )
    assert response.status == 404
    response_json = await response.json()
    assert response_json == {
        'message': 'Нет данных API Coverage по сервису или хранилище пусто',
    }
