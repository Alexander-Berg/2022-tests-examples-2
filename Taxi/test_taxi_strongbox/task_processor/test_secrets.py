import pytest

from taxi_strongbox.components import group_processor as gp


@pytest.mark.parametrize(
    [
        'service',
        'new_project_name',
        'old_project_name',
        'expected',
        'expected_names',
        'calls',
    ],
    [
        (
            'service',
            'eda',
            'taxi',
            [
                {
                    'env': 'testing',
                    'key': 'MONGODB_TAXI_STRONGBOX',
                    'project_name': 'eda',
                    'service_name': 'service',
                },
                {
                    'env': 'unstable',
                    'key': 'SEARCHABLE_SECRET',
                    'project_name': 'eda',
                    'service_name': 'service',
                },
            ],
            [
                'eda:service:testing',
                'eda:service:unstable',
                'taxi-infra:service:testing',
            ],
            6,
        ),
        (
            'service2',
            'taxi-infra',
            'eda',
            [
                {
                    'env': 'testing',
                    'key': 'TEST_2',
                    'project_name': 'taxi-infra',
                    'service_name': 'service2',
                },
            ],
            ['taxi-infra:service2:testing'],
            3,
        ),
        (
            'service',
            'taxi-ml',
            'taxi-infra',
            [
                {
                    'env': 'testing',
                    'key': 'MONGODB_TAXI-INFRA_STRONGBOX',
                    'project_name': 'taxi-ml',
                    'service_name': 'service',
                },
            ],
            [
                'taxi-ml:service:testing',
                'taxi:service:testing',
                'taxi:service:unstable',
            ],
            3,
        ),
        ('service1', 'eda', 'taxi-infra', [], [], 0),
    ],
)
@pytest.mark.pgsql('strongbox', files=['init_secrets.sql'])
async def test_cube_change_project(
        call_cube,
        web_context,
        service,
        expected,
        new_project_name,
        old_project_name,
        expected_names,
        patch_clownductor_session,
        calls,
):
    group_processor = gp.GroupProcessor(web_context, None)

    clown_patch = patch_clownductor_session(
        [{'id': 1, 'name': 'unstable'}, {'id': 1, 'name': 'testing'}],
    )
    data = await call_cube(
        'ChangeSecretsProjectForService',
        {
            'service_name': service,
            'new_project_name': new_project_name,
            'old_project_name': old_project_name,
        },
    )
    assert data == {'status': 'success'}

    result = await web_context.pg.master_pool.fetch(
        """
        select key, env, project_name, service_name
        from secrets.secrets
        where service_name = $1 and project_name = $2
        order by key
        """,
        service,
        new_project_name,
    )
    assert [dict(row) for row in result] == expected

    groups = await group_processor.get_groups_by_service_name(
        service_name=service,
    )
    assert sorted([group.name for group in groups]) == expected_names
    assert len(clown_patch.calls) == calls
