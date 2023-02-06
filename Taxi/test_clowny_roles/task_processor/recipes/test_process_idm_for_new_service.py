import pytest


@pytest.mark.roles_features_on(
    'idm_add_nodes_for_new_service', 'idm_request_roles_for_new_service',
)
async def test_recipe(
        mockserver,
        load_yaml,
        task_processor,
        add_subsystem,
        add_role,
        web_context,
        mock_idm_batch,
        run_job_common,
):
    internal_subsystem_id = await add_subsystem('internal')
    await add_role(
        'nanny_admin_testing', 'srv-1-slug', 'service', internal_subsystem_id,
    )
    await add_role(
        'strongbox_secrets_creation',
        'srv-1-slug',
        'service',
        internal_subsystem_id,
    )
    await add_role(
        'mdb_cluster_ro_access',
        'srv-1-slug',
        'service',
        internal_subsystem_id,
    )
    await add_role(
        'deploy_approve_programmer',
        'srv-1-slug',
        'service',
        internal_subsystem_id,
    )

    _batch_handler = mock_idm_batch()

    @mockserver.json_handler('/client-staff/v3/persons')
    def _persons_handler(request):
        if request.query.get('_one') == '1':
            return {
                'department_group': {'department': {'url': 'department_url'}},
            }
        return {
            'result': [
                {
                    'chief': {'login': 'chief-1'},
                    'login': request.query['login'],
                },
            ],
        }

    @mockserver.json_handler('/client-staff/v3/groups')
    def _groups_handler(_):
        return {'result': [{'id': 1}]}

    recipe = task_processor.load_recipe(
        load_yaml('ProcessIdmForNewService.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={'service_id': 1}, initiator='testsuite',
    )
    await run_job_common(job)

    batch_requests = []
    while _batch_handler.has_calls:
        batch_requests.append(_batch_handler.next_call())
    assert len(batch_requests) == 2
