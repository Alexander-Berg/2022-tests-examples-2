import pytest


@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.parametrize(
    'cube_name',
    [
        'PerforatorCreateService',
        'PerforatorCreateEnvironment',
        'PerforatorEnsureDefaultTvmRules',
        'PerforatorCheckExistingTvm',
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'perforator_enable_cubes': True,
        'check_existing_tvm': True,
    },
)
async def test_perforator_cubes(
        web_app_client, cube_name, load_json, mockserver,
):
    @mockserver.json_handler('/clowny-perforator/v1.0/services/create')
    # pylint: disable=unused-variable
    def create_handler(*args):
        return {
            'id': 1,
            'tvm_name': 'service-tvm-name',
            'environments': [],
            'clown_service': {'project_id': 1, 'clown_id': 1},
            'is_internal': True,
        }

    @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
    # pylint: disable=unused-variable
    def retrieve_handler(request):
        services = []
        tvm_name = request.json.get('tvm_names')[0]
        if tvm_name == 'existing-tvm':
            services.append(
                {
                    'id': 1,
                    'is_internal': True,
                    'tvm_name': tvm_name,
                    'environments': [
                        {'id': 1, 'env_type': 'production', 'tvm_id': 1234},
                    ],
                },
            )
        return {'services': services}

    @mockserver.json_handler(
        '/clowny-perforator/v1.0/services/environments/create',
    )
    # pylint: disable=unused-variable
    def create_env_handler(*args):
        return {'id': 1, 'env_type': 'production', 'tvm_id': 1001}

    @mockserver.json_handler('/clowny-perforator/v1.0/services')
    # pylint: disable=unused-variable
    def get_handler(*args):
        return {
            'id': 1,
            'tvm_name': 'service-tvm-name',
            'environments': [],
            'clown_service': {'project_id': 1, 'clown_id': 1},
            'is_internal': True,
        }

    @mockserver.json_handler(
        '/clowny-perforator/v1.0/services/environments/rules/create',
    )
    # pylint: disable=unused-variable
    def handler(*args):
        return {
            'status': 'succeeded',
            'created_rules': [
                {
                    'rule_id': 1,
                    'source': {
                        'id': 1,
                        'environment_id': 1,
                        'tvm_name': 'new-service',
                        'tvm_id': 1001,
                    },
                    'destination': {
                        'id': 2,
                        'environment_id': 2,
                        'tvm_name': 'statistics',
                        'tvm_id': 1002,
                    },
                    'env_type': 'production',
                },
            ],
        }

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']
