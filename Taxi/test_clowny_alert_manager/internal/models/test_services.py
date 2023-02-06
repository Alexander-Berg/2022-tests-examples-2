import pytest

from clowny_alert_manager.internal.models import service


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.features_on('enable_clownductor_cache'),
]


@pytest.mark.parametrize(
    'yaml_data, parsed',
    [
        pytest.param(
            {'host': 'taxi_clownductor_stable', 'type': 'rtc'},
            {
                'project_name': 'taxi-infra',
                'service_name': 'clownductor',
                'type': 'rtc',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': None,
                    'file_path': None,
                },
                'clown_service_id': 1,
                'clown_project_id': 150,
            },
            id='searchable service in clownductor base',
        ),
        pytest.param(
            {'host': 'taxi_routestats_stable', 'type': 'rtc'},
            {
                'project_name': 'taxi',
                'service_name': 'routestats',
                'type': 'rtc',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': None,
                    'file_path': None,
                },
                'clown_service_id': None,
                'clown_project_id': None,
            },
            id='service with removable part in the middle of name',
        ),
        pytest.param(
            {'host': 'taxi_scripts'},
            {
                'project_name': 'taxi',
                'service_name': 'scripts',
                'type': 'cgroup',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': None,
                    'file_path': None,
                },
                'clown_service_id': None,
                'clown_project_id': None,
            },
            id='unknown service for clownductor',
        ),
    ],
)
async def test_parse_yaml(web_context, yaml_data, parsed):
    await web_context.clownductor_cache.refresh_cache()
    bare_services = service.BareServices()
    srv = bare_services.find_or_create(
        yaml_data, 'taxi', web_context.clownductor_cache,
    )
    assert srv.to_query_json() == parsed
