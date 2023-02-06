import pytest


@pytest.mark.parametrize(
    'data, expected',
    [
        (
            {
                'project_name': 'test_project',
                'service_name': 'test-service',
                'env': 'testing',
            },
            {
                'configs': [
                    {
                        'id': 1,
                        'branch_id': 2,
                        'name': 'EXIST_CONFIG',
                        'libraries': ['lib'],
                        'plugins': ['plugin'],
                        'is_service_yaml': True,
                        'description': 'config description 2',
                        'group': 'clownductor',
                        'is_fallback': False,
                        'maintainers': ['elrusso'],
                        'tags': ['notfallback'],
                        'ticket_required': False,
                        'has_overrides': False,
                    },
                    {
                        'id': 2,
                        'branch_id': 2,
                        'name': 'EXIST_CONFIGS',
                        'libraries': ['lib'],
                        'plugins': ['plugin'],
                        'is_service_yaml': True,
                        'description': 'config description 3',
                        'group': 'clownductor',
                        'is_fallback': True,
                        'maintainers': [],
                        'tags': ['notfallback'],
                        'ticket_required': False,
                        'has_overrides': False,
                    },
                ],
            },
        ),
        (
            {
                'project_name': 'test_project',
                'service_name': 'test-service',
                'env': 'stable',
                'is_service_yaml': True,
                'libraries': ['lib_1'],
                'plugins': ['plugin_1'],
            },
            {
                'configs': [
                    {
                        'id': 5,
                        'branch_id': 1,
                        'name': 'CONFIG_3',
                        'libraries': ['lib_1', 'lib_2'],
                        'plugins': ['plugin_1'],
                        'description': 'config description 1',
                        'is_service_yaml': True,
                        'group': 'clownductor',
                        'is_fallback': False,
                        'maintainers': [],
                        'tags': ['notfallback'],
                        'ticket_required': False,
                        'has_overrides': False,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_configs(
        web_app_client,
        data,
        expected,
        login_mockserver,
        mock_configs_admin,
        patch,
):
    @mock_configs_admin('/v1/configs/search/')
    async def handler(request):
        exact_names = request.json['exact_names']
        assert exact_names
        configs = {
            'CONFIG_3': {
                'description': 'config description 1',
                'group': 'clownductor',
                'is_fallback': False,
                'maintainers': [],
                'name': 'CONFIG_3',
                'tags': ['notfallback'],
                'ticket_required': False,
                'has_overrides': False,
                'default': 123,
            },
            'EXIST_CONFIG': {
                'description': 'config description 2',
                'group': 'clownductor',
                'is_fallback': False,
                'maintainers': ['elrusso'],
                'name': 'EXIST_CONFIG',
                'tags': ['notfallback'],
                'ticket_required': False,
                'has_overrides': False,
                'default': 123,
            },
            'EXIST_CONFIGS': {
                'description': 'config description 3',
                'group': 'clownductor',
                'is_fallback': True,
                'maintainers': [],
                'name': 'EXIST_CONFIGS',
                'tags': ['notfallback'],
                'ticket_required': False,
                'has_overrides': False,
                'default': 123,
            },
        }
        result = {'items': []}
        for name in exact_names:
            if configs.get(name):
                result['items'].append(configs.get(name))
        return result

    login_mockserver()

    response = await web_app_client.post('v1/configs/retrieve/', json=data)
    assert response.status == 200
    data = await response.json()
    for config in data['configs']:
        config.pop('updated_at')
    assert data == expected
    assert handler.times_called == 1
