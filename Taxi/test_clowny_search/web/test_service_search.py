import pytest


@pytest.mark.pgsql('clowny_search', files=['add_test_data.sql'])
@pytest.mark.parametrize(
    'name, login, expected',
    [
        pytest.param(
            '',
            'elrusso',
            [
                {
                    'project_id': 2,
                    'project_name': 'eda',
                    'services': [
                        {
                            'id': 5,
                            'name': 'eda_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 2,
                            'abc_service': 'eda1',
                        },
                    ],
                },
                {
                    'project_id': 1,
                    'project_name': 'taxi',
                    'services': [
                        {
                            'id': 1,
                            'name': 'taxi_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi1',
                        },
                        {
                            'id': 2,
                            'name': 'taxi_service_2_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi2',
                        },
                        {
                            'id': 3,
                            'name': 'taxi_service_3_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi3',
                        },
                    ],
                },
            ],
        ),
        pytest.param(
            'taxi_service',
            'elrusso',
            [
                {
                    'project_id': 1,
                    'project_name': 'taxi',
                    'services': [
                        {
                            'id': 1,
                            'name': 'taxi_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi1',
                        },
                        {
                            'id': 2,
                            'name': 'taxi_service_2_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi2',
                        },
                        {
                            'id': 3,
                            'name': 'taxi_service_3_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi3',
                        },
                    ],
                },
            ],
        ),
        pytest.param(
            '',
            None,
            [
                {
                    'project_id': 2,
                    'project_name': 'eda',
                    'services': [
                        {
                            'id': 5,
                            'name': 'eda_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 2,
                            'abc_service': 'eda1',
                        },
                        {
                            'id': 6,
                            'name': 'eda_service_3_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 2,
                            'abc_service': 'eda2',
                        },
                        {
                            'id': 7,
                            'name': 'eda_service_5_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 2,
                            'abc_service': 'eda3',
                        },
                    ],
                },
                {
                    'project_id': 1,
                    'project_name': 'taxi',
                    'services': [
                        {
                            'id': 1,
                            'name': 'taxi_service_1_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi1',
                        },
                        {
                            'id': 2,
                            'name': 'taxi_service_2_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi2',
                        },
                        {
                            'id': 3,
                            'name': 'taxi_service_3_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi3',
                        },
                        {
                            'id': 4,
                            'name': 'taxi_service_4_smth',
                            'artifact_name': 'ubuntu',
                            'cluster_type': 'nanny',
                            'st_task': 'TAXIADMIN-100500',
                            'production_ready': False,
                            'requester': 'unit_test',
                            'project_id': 1,
                            'abc_service': 'taxi4',
                        },
                    ],
                },
            ],
        ),
    ],
)
async def test_clowny_service_search(
        mockserver,
        taxi_clowny_search_web,
        mock_clown,
        import_clown,
        name,
        login,
        expected,
):
    params = {'name': name}
    if login:
        params['login'] = login
    response = await taxi_clowny_search_web.get(
        '/v1/services/search', params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content['projects'] == expected
