async def test_get_cubes(get_all_cubes):
    response = await get_all_cubes()
    assert response == {
        'cubes': [
            {
                'name': 'ChangeOwnersCompletely',
                'needed_parameters': ['secret_uuid'],
                'optional_parameters': [
                    'new_owners',
                    'new_abc_groups',
                    'new_staff_ids',
                ],
                'output_parameters': [],
            },
            {
                'name': 'ChangeSecretsProjectForService',
                'needed_parameters': [
                    'service_name',
                    'old_project_name',
                    'new_project_name',
                ],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'GetArcadiaPrUrl',
                'needed_parameters': ['job_id'],
                'optional_parameters': [],
                'output_parameters': ['pull_request_url'],
            },
            {
                'name': 'SaveLastChangeUrl',
                'needed_parameters': ['service_name', 'type_name'],
                'optional_parameters': ['merge_sha', 'pull_request_url'],
                'output_parameters': [],
            },
        ],
    }
