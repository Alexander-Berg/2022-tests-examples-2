from aiohttp import web
import pytest


@pytest.fixture(name='cube_job_get_information_update')
def _cube_job_get_information_update(patch_method):
    @patch_method(
        'clownductor.internal.tasks.cubes.cubes_internal.'
        'InternalJobGetInformation._update',
    )
    async def _update(self, input_data):
        self._data['payload'] = {  # pylint: disable=protected-access
            'service_id': 1,
            'project_id': 1,
            'branch_id': 2,
            'service_name': 'some_service',
            'project_name': 'taxi',
        }
        return self.succeed()


@pytest.fixture(name='strongbox_get_groups')
def _strongbox_get_groups(mock_strongbox):
    @mock_strongbox('/v1/groups/')
    async def _handler(_):
        data = {
            'yav_secret_uuid': 'sec-XXX',
            'yav_version_uuid': 'ver-YYY',
            'service_name': 'test_service',
            'env': 'production',
        }
        return web.json_response(data, status=200)

    return _handler


@pytest.fixture(name='strongbox_get_secrets')
def _strongbox_get_secrets(mock_strongbox):
    @mock_strongbox('/v1/secrets/')
    async def _secrets_handler(_):
        return web.json_response(
            {
                'yav_secret_uuid': 'sec-XXX',
                'yav_version_uuid': 'ver-YYY',
                'name': 'SOME_NAME',
            },
            status=200,
        )


@pytest.fixture(name='random_region')
async def _random_region(patch):
    @patch('clownductor.internal.presets.presets.random_region')
    def _random_region(context, count=1, project=None):
        return ['vla', 'man', 'sas'][0:count]


@pytest.fixture(name='create_branch_fixture')
async def _create_service(
        nanny_mockserver,
        staff_mockserver,
        solomon_mockserver,
        cookie_monster_mockserver,
        abc_mockserver,
        nanny_yp_mockserver,
):
    staff_mockserver()
    solomon_mockserver()
    cookie_monster_mockserver()
    abc_mockserver()
    nanny_yp_mockserver()


@pytest.fixture(name='assert_mock_calls')
def _assert_mock_calls(load_json):
    def _wrapper(mock, file_name):
        expected = load_json(file_name)
        assert mock.times_called == len(expected)
        result = []
        while mock.has_calls:
            call = mock.next_call()['request']
            result_item = {'method': call.method, 'path': call.path}
            if call.query:
                result_item['query'] = dict(call.query)
            if call.method != 'GET':
                result_item['json'] = call.json
            result.append(result_item)
        assert result == expected

    return _wrapper


@pytest.fixture(name='assert_job_variables')
def _assert_job_variables(load_json):
    def _wrapper(job_vars, job_name, job_id, file_name):
        loaded = load_json(file_name)
        expected_vars = None
        for job in loaded:
            if job['name'] == job_name and job['id'] == job_id:
                expected_vars = job['vars']

        msg = f'{job_name} with job_id {job_id} has never been executed'
        assert expected_vars is not None, msg
        assert job_vars == expected_vars

    return _wrapper


@pytest.fixture(name='add_external_cubes')
def _add_external_cubes(task_processor):
    def _wrapper():
        slb_provider = task_processor.provider('clowny-balancer')
        task_processor.add_cube(
            'InternalGetNamespaces',
            needed_parameters=['service_id'],
            optional_parameters=['branch_ids'],
            output_parameters=['namespace_ids'],
            check_input_mappings=True,
            check_output_mappings=True,
            provider=slb_provider,
        )
        task_processor.add_cube(
            'AwacsWaitSyncBackends',
            needed_parameters=['namespace_ids'],
            optional_parameters=[
                'pod_ids_by_region',
                'vla_pod_ids',
                'sas_pod_ids',
                'man_pod_ids',
            ],
            output_parameters=['success_after_sleep'],
            check_input_mappings=True,
            check_output_mappings=True,
            provider=slb_provider,
        )
        task_processor.add_cube(
            'AwacsAddDcToSlowBackends',
            needed_parameters=['namespace_ids'],
            optional_parameters=[
                'pod_ids_by_region',
                'vla_pod_ids',
                'sas_pod_ids',
                'man_pod_ids',
                'environment',
            ],
            output_parameters=[],
            check_input_mappings=True,
            check_output_mappings=True,
            provider=slb_provider,
        )

        task_processor.add_cube(
            name='ChangeOwnersCompletely',
            needed_parameters=['secret_uuid'],
            optional_parameters=[
                'new_owners',
                'new_abc_groups',
                'new_staff_ids',
            ],
            output_parameters=[],
            check_input_mappings=False,
            check_output_mappings=False,
            provider=task_processor.provider('taxi-strongbox'),
        )

        task_processor.add_cube(
            'FindServiceForClown',
            needed_parameters=['clowny_service_id'],
            optional_parameters=[],
            output_parameters=['service_id'],
            check_input_mappings=True,
            check_output_mappings=True,
            provider=task_processor.provider('clowny-perforator'),
        )

    return _wrapper


@pytest.fixture(name='external_call_cube')
def _external_call_cube(mockserver):
    async def do_it(stage, cube, request_data):

        assert cube.name in [
            'InternalGetNamespaces',
            'AwacsWaitSyncBackends',
            'AwacsAddDcToSlowBackends',
            'ChangeOwnersCompletely',
            'FindServiceForClown',
        ]
        response_data = {'status': 'success'}
        if cube.name == 'InternalGetNamespaces':
            response_data['payload'] = {'namespace_ids': ['namespace_id_1']}
        elif cube.name == 'AwacsWaitSyncBackends':
            response_data['payload'] = {'success_after_sleep': False}
        elif cube.name == 'AwacsAddDcToSlowBackends':
            response_data['payload'] = {}
        elif cube.name == 'FindServiceForClown':
            response_data['payload'] = {'service_id': 1}

        return mockserver.make_response(json=response_data)

    return do_it
