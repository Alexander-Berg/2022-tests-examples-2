import pytest

from test_clowny_alert_manager.helpers import builders


@pytest.mark.parametrize(
    'data, diff',
    [
        pytest.param(
            builders.service(
                builders.branch(
                    builders.Config(for_upsert=True)
                    .with_events(builders.Event(1, 'some', for_upsert=True))
                    .with_templates(
                        builders.LinkedTemplate(
                            builders.template(
                                'tmpl',
                                builders.Event(2, 'another', for_upsert=True),
                                for_upsert=True,
                            ),
                            ignore_nodata=True,
                        ),
                    )
                    .with_notifications(
                        builders.notification(
                            ['d1mbas'], 'default', 1, for_upsert=True,
                        ),
                    ),
                    for_upsert=True,
                ),
                for_upsert=True,
            ),
            {
                'new': builders.service(
                    builders.branch(
                        builders.Config(for_upsert=True)
                        .with_events(
                            builders.Event(1, 'some', for_upsert=True),
                        )
                        .with_templates(
                            builders.LinkedTemplate(
                                builders.template(
                                    'tmpl',
                                    builders.Event(
                                        2, 'another', for_upsert=True,
                                    ),
                                    for_upsert=True,
                                ),
                                ignore_nodata=True,
                            ),
                        )
                        .with_notifications(
                            builders.notification(
                                ['d1mbas'], 'default', 1, for_upsert=True,
                            ),
                        ),
                        for_upsert=True,
                    ),
                    for_upsert=True,
                ),
            },
            id='create new',
        ),
        pytest.param(
            builders.service(
                builders.branch(
                    builders.Config(for_upsert=True)
                    .with_events(builders.Event(1, 'some', for_upsert=True))
                    .with_templates(
                        builders.LinkedTemplate(
                            builders.template(
                                'tmpl',
                                builders.Event(2, 'another', for_upsert=True),
                                for_upsert=True,
                            ),
                            ignore_nodata=True,
                        ),
                    )
                    .with_notifications(
                        builders.notification(
                            ['d1mbas'], 'default', 1, for_upsert=True,
                        ),
                    ),
                    names=['taxi_clownductor_stable'],
                    for_upsert=True,
                ),
                project_name='taxi-infra',
                service_name='clownductor',
                type_='rtc',
                for_upsert=True,
            ),
            {
                'new': builders.service(
                    builders.branch(
                        builders.Config(for_upsert=True)
                        .with_events(
                            builders.Event(1, 'some', for_upsert=True),
                        )
                        .with_templates(
                            builders.LinkedTemplate(
                                builders.template(
                                    'tmpl',
                                    builders.Event(
                                        2, 'another', for_upsert=True,
                                    ),
                                    for_upsert=True,
                                ),
                                ignore_nodata=True,
                            ),
                        )
                        .with_notifications(
                            builders.notification(
                                ['d1mbas'], 'default', 1, for_upsert=True,
                            ),
                        ),
                        names=['taxi_clownductor_stable'],
                        clown_branch_ids=[1],
                        for_upsert=True,
                    ),
                    project_name='taxi-infra',
                    service_name='clownductor',
                    type_='rtc',
                    for_upsert=True,
                ),
                'current': builders.service(
                    builders.branch(
                        names=['taxi_clownductor_stable'], for_upsert=True,
                    ),
                    project_name='taxi-infra',
                    service_name='clownductor',
                    type_='rtc',
                    repo_meta_=builders.repo_meta(
                        file_name='b1.yaml', file_path='b1.yaml',
                    ),
                    for_upsert=True,
                ),
            },
            id='update existing',
        ),
    ],
)
async def test_draft_diff(upsert_service, data, diff):
    response = await upsert_service(data, draft_api_type='check')
    assert response['diff'] == diff
