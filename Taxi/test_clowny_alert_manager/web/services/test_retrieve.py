import pytest

from test_clowny_alert_manager.helpers import builders
from test_clowny_alert_manager.helpers import extractors


@pytest.mark.parametrize(
    'service_id, clown_id, status, data',
    [
        (
            1,
            None,
            200,
            builders.service(
                builders.branch(
                    builders.Config()
                    .with_events(
                        builders.Event(
                            id_=1, name='oom', config_id=1,
                        ).with_notifications(
                            builders.notification(
                                ['d1mbas'], 'telegram_option1', 1,
                            ),
                        ),
                        builders.Event(id_=2, name='vhost500', config_id=1),
                    )
                    .with_templates(
                        builders.LinkedTemplate(
                            builders.template(
                                'pkgver',
                                builders.Event(
                                    id_=4, name='pkgver', template_id=1,
                                ),
                            ),
                            ignore_nodata=True,
                        ).with_notifications(
                            builders.notification(
                                ['mvpetrov'], 'telegram_option2', 2,
                            ),
                        ),
                    )
                    .with_notifications(
                        builders.notification(
                            ['d1mbas'], 'telegram_option1', 1,
                        ),
                    ),
                ),
            ),
        ),
        (
            None,
            1,
            200,
            builders.service(
                builders.branch(
                    builders.Config(
                        id_=2,
                        branch_id=2,
                        repo_meta_=builders.repo_meta(
                            file_name='b2.yaml', file_path='b2.yaml',
                        ),
                    ).with_events(
                        builders.Event(id_=3, name='oom', config_id=2),
                    ),
                    id_=2,
                    service_id=2,
                    clown_branch_ids=[1, 2],
                    repo_meta_=builders.repo_meta(
                        file_name='b2.yaml', file_path='b2.yaml',
                    ),
                    names=['branch1', 'branch2'],
                ),
                id_=2,
                service_name='clownductor',
                project_name='taxi-infra',
                type_='rtc',
                clown_project_id=1,
                clown_service_id=1,
            ),
        ),
        (
            3,
            None,
            404,
            {'code': 'NOT_FOUND', 'message': 'service for id 3 not found'},
        ),
    ],
)
async def test_get(
        taxi_clowny_alert_manager_web, service_id, clown_id, status, data,
):
    params = {}
    if service_id:
        params['id'] = service_id
    if clown_id:
        params['clown_id'] = clown_id
    response = await taxi_clowny_alert_manager_web.get(
        '/v1/services/get/', params=params,
    )
    assert response.status == status, await response.text()
    assert (await response.json()) == data


@pytest.mark.parametrize(
    (
        'filters, max_id, '
        'services_count, total_branches_count, total_events_count'
    ),
    [
        pytest.param({}, 2, 2, 2, 3, id='no filters'),
        pytest.param({'limit': 1}, 1, 1, 1, 2, id='limit by 1'),
        pytest.param(
            {'cursor': {'newer_than': 1}}, 2, 1, 1, 1, id='skip 1 via cursor',
        ),
    ],
)
async def test_list(
        taxi_clowny_alert_manager_web,
        filters,
        max_id,
        services_count,
        total_branches_count,
        total_events_count,
):
    response = await taxi_clowny_alert_manager_web.post(
        '/v1/services/list/', json=filters,
    )
    assert response.status == 200, await response.text()
    data = await response.json()
    assert data['cursor']['newer_than'] == max_id
    services = extractors.Services(data['services'])
    assert len(services.services) == services_count
    assert len(list(services.branches)) == total_branches_count
    assert len(list(services.configs)) == total_branches_count
    assert len(list(services.events)) == total_events_count
